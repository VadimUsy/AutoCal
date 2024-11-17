import logging
from flask import Blueprint, redirect, url_for, session, request, render_template
from googleapiclient.discovery import build
from app import oauth

# Set up logging
logging.basicConfig(level=logging.DEBUG)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.login'))

@main_bp.route('/login')
def login():
    redirect_uri = url_for('main.authorized', _external=True)
    google = oauth.create_client('google')  # Get the Google client dynamically
    return google.authorize_redirect(redirect_uri)

@main_bp.route('/login/authorized')
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

@main_bp.route('/complete')
def complete():
    if 'events' not in session:
        return redirect(url_for('main.events'))

    google = oauth.create_client('google')  # Get the Google client dynamically
    token = session.get('token')
    if not token:
        return redirect(url_for('main.login'))

    service = build('calendar', 'v3', credentials=google.authorize_access_token())
    for event in session['events']:
        event_body = {
            'summary': event['description'],
            'start': {'dateTime': event['date']},
            'end': {'dateTime': event['date']},  # Adjust as needed
        }
        service.events().insert(calendarId='primary', body=event_body).execute()

    session.pop('events', None)
    return redirect(url_for('main.events'))
