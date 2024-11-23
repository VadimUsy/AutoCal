import logging
from flask import Blueprint, redirect, url_for, session, request, render_template
from googleapiclient.discovery import build
from app import oauth
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import datetime
import os
import pytz

# Set up logging
logging.basicConfig(level=logging.DEBUG)

SCOPES = ["https://www.googleapis.com/auth/calendar"]

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))

@main_bp.route('/login')
def login():
    redirect_uri = url_for('main.authorized', _external=True)
    google = oauth.create_client('google')  # Get the Google client dynamically
    return google.authorize_redirect(redirect_uri, prompt='consent')

@main_bp.route('/login/google/authorized')
def authorized():
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
        return redirect(url_for('main.login'))

    session['token'] = token
    session['user'] = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
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

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.route('/remove_events', methods=['POST'])
def remove_events():
    remove_indices = request.form.getlist('remove_events')
    if 'events' in session:
        events = session['events']
        for index in sorted(map(int, remove_indices), reverse=True):
            if 0 <= index < len(events):
                events.pop(index)
        session['events'] = events
    return redirect(url_for('main.events'))

@main_bp.route('/complete')
def complete():
    if 'events' not in session:
        return redirect(url_for('main.events'))

    token = session.get('token')
    if not token:
        return redirect(url_for('main.login'))

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

    session.pop('events', None)
    return redirect(url_for('main.events'))