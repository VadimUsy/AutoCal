import logging
from flask import Blueprint, redirect, url_for, session, request, render_template
from googleapiclient.discovery import build
from app import oauth
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import datetime
import os
import pytz
import requests
import msal
import json
import webbrowser

# Set up logging
logging.basicConfig(level=logging.DEBUG)

SCOPES = ["https://www.googleapis.com/auth/calendar", "https://graph.microsoft.com/Calendars.ReadWrite"]
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'

main_bp = Blueprint('main', __name__)

def generate_access_token(app_id, scopes):
    # Save Session Token as a token file
    access_token_cache = msal.SerializableTokenCache()

    # read the token file
    if os.path.exists('ms_graph_api_token.json'):
        access_token_cache.deserialize(open("ms_graph_api_token.json", "r").read())
        token_detail = json.load(open('ms_graph_api_token.json',))
        token_detail_key = list(token_detail['AccessToken'].keys())[0]
        token_expiration = datetime.fromtimestamp(int(token_detail['AccessToken'][token_detail_key]['expires_on']))
        if datetime.now() > token_expiration:
            os.remove('ms_graph_api_token.json')
            access_token_cache = msal.SerializableTokenCache()

    # assign a SerializableTokenCache object to the client instance
    client = msal.PublicClientApplication(client_id=app_id, token_cache=access_token_cache)

    accounts = client.get_accounts()
    if accounts:
        # load the session
        token_response = client.acquire_token_silent(scopes, accounts[0])
    else:
        # authenticate your account as usual
        flow = client.initiate_device_flow(scopes=scopes)
        print('user_code: ' + flow['user_code'])
        webbrowser.open('https://microsoft.com/devicelogin')
        token_response = client.acquire_token_by_device_flow(flow)

    with open('ms_graph_api_token.json', 'w') as _f:
        _f.write(access_token_cache.serialize())

    return token_response

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login')
def login():
    provider = request.args.get('provider')
    if provider == 'google':
        redirect_uri = url_for('main.authorized_google', _external=True)
        google = oauth.create_client('google')  # Get the Google client dynamically
        return google.authorize_redirect(redirect_uri, prompt='consent')
    elif provider == 'microsoft':
        redirect_uri = url_for('main.authorized_microsoft', _external=True)
        microsoft = oauth.create_client('microsoft')  # Get the Microsoft client dynamically
        return microsoft.authorize_redirect(redirect_uri, prompt='consent')
    else:
        return redirect(url_for('main.index'))

@main_bp.route('/login/google/authorized')
def authorized_google():
    google = oauth.create_client('google')  # Get the Google client dynamically
    claims_options = {
        'iss': {'values': ['https://accounts.google.com', 'accounts.google.com']}
    }
    token = google.authorize_access_token(claims_options=claims_options)
    id_token = token.get('id_token')
    if id_token:
        nonce = token.get('nonce')
        claims = google.parse_id_token(token, nonce=nonce, claims_options=claims_options)
        logging.debug(f"ID Token claims: {claims}")
    if not token:
        return redirect(url_for('main.login', provider='google'))

    session['token'] = token
    session['user'] = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
    session['provider'] = 'google'
    return redirect(url_for('main.events'))

@main_bp.route('/login/microsoft/authorized')
def authorized_microsoft():
    microsoft = oauth.create_client('microsoft')  # Get the Microsoft client dynamically
    token = microsoft.authorize_access_token()
    if not token:
        return redirect(url_for('main.login', provider='microsoft'))

    session['token'] = token
    session['user'] = microsoft.get('https://graph.microsoft.com/v1.0/me').json()
    session['provider'] = 'microsoft'
    return redirect(url_for('main.events'))

@main_bp.route('/events')
def events():
    events = session.get('events', [])
    return render_template('events.html', events=events)

@main_bp.route('/add_event', methods=['POST'])
def add_event():
    data = request.form
    event = {
        'title': data.get('title'),
        'year': data.get('year'),
        'month': data.get('month'),
        'day': data.get('day'),
        'hour': data.get('hour'),
        'minute': data.get('minute'),
        'ampm': data.get('ampm'),
        'description': data.get('description', ''),  # Default to an empty string if no description is provided
    }

    if 'events' not in session:
        session['events'] = []
    session['events'].append(event)

    return redirect(url_for('main.events'))

@main_bp.route('/complete')
def complete():
    if 'events' not in session:
        return redirect(url_for('main.events'))

    token = session.get('token')
    if not token:
        return redirect(url_for('main.login'))

    provider = session.get('provider')
    if provider == 'google':
        creds = Credentials(
            token=token['access_token'],
            refresh_token=token.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=SCOPES
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build('calendar', 'v3', credentials=creds)

        # Define the local time zone
        local_tz = pytz.timezone('America/New_York')  # Replace with your local time zone

        for event in session['events']:
            start_datetime = datetime.datetime(
                int(event['year']),
                int(event['month']),
                int(event['day']),
                int(event['hour']) + (12 if event['ampm'] == 'PM' and int(event['hour']) != 12 else 0),
                int(event['minute'])
            )

            # Convert to local time zone
            start_datetime = local_tz.localize(start_datetime)

            # Calculate end time (1 hour later)
            end_datetime = start_datetime + datetime.timedelta(hours=1)

            event_body = {
                'summary': event['title'],
                'description': event['description'],
                'start': {'dateTime': start_datetime.isoformat(), 'timeZone': str(local_tz)},
                'end': {'dateTime': end_datetime.isoformat(), 'timeZone': str(local_tz)},
            }
            service.events().insert(calendarId='primary', body=event_body).execute()

    elif provider == 'microsoft':
        # Define the local time zone
        local_tz = pytz.timezone('America/New_York')  # Replace with your local time zone

        for event in session['events']:
            start_datetime = datetime.datetime(
                int(event['year']),
                int(event['month']),
                int(event['day']),
                int(event['hour']) + (12 if event['ampm'] == 'PM' and int(event['hour']) != 12 else 0),
                int(event['minute'])
            )

            # Convert to local time zone
            start_datetime = local_tz.localize(start_datetime)

            # Calculate end time (1 hour later)
            end_datetime = start_datetime + datetime.timedelta(hours=1)

            request_body = {
                "subject": event['title'],
                "body": {
                    "contentType": "HTML",
                    "content": event['description']
                },
                "start": {
                    "dateTime": start_datetime.isoformat(),
                    "timeZone": str(local_tz)
                },
                "end": {
                    "dateTime": end_datetime.isoformat(),
                    "timeZone": str(local_tz)
                },
                "location": {
                    "displayName": "Online"
                },
                "attendees": [],
                "allowNewTimeProposals": True,
                "transactionId": "7E163156-7762-4BEB-A1C6-729EA81755A7"
            }

            headers = {
                'Authorization': f'Bearer {token["access_token"]}',
                'Content-Type': 'application/json',
                'Prefer': f'outlook.timezone="{local_tz}"'
            }

            response = requests.post(f'{GRAPH_API_ENDPOINT}/me/events', headers=headers, json=request_body)
            if response.status_code == 401:
                # Handle token expiration
                return redirect(url_for('main.login', provider='microsoft'))
            elif response.status_code == 403:
                logging.error("Access denied. Ensure the required permissions are granted.")
                return "Access denied. Ensure the required permissions are granted.", 403

    session.pop('events', None)
    return redirect(url_for('main.events'))

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))