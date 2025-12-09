import logging
from flask import Blueprint, redirect, url_for, session, request, render_template, jsonify
from app.models.event import Event
from app.utils.validators import EventValidator
from app.api.services import CalendarService

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@api_bp.route('/')
def index():
    """Redirect to events page or login"""
    if 'token' in session:
        return redirect(url_for('api.events'))
    return redirect(url_for('auth.login'))

@api_bp.route('/events')
@require_auth
def events():
    """Display events page"""
    events = session.get('events', [])
    return render_template('events.html', events=events)

@api_bp.route('/events/add', methods=['POST'])
@require_auth
def add_event():
    """Add a new event to the session"""
    try:
        event = Event.from_dict(request.form)
        
        # Validate event
        is_valid, error_message = EventValidator.validate(event)
        if not is_valid:
            logger.warning(f"Invalid event data: {error_message}")
            return jsonify({'error': error_message}), 400
        
        # Add to session
        if 'events' not in session:
            session['events'] = []
        session['events'].append(event.to_dict())
        session.modified = True
        
        logger.info(f"Added event: {event.title}")
        return redirect(url_for('api.events'))
    
    except Exception as e:
        logger.error(f"Error adding event: {str(e)}")
        return jsonify({'error': 'Failed to add event'}), 500

@api_bp.route('/events/remove', methods=['POST'])
@require_auth
def remove_events():
    """Remove selected events from session"""
    remove_indices = request.form.getlist('remove_events')
    
    if 'events' in session:
        events = session['events']
        # Remove in reverse order to maintain correct indices
        for index in sorted(map(int, remove_indices), reverse=True):
            if 0 <= index < len(events):
                removed_event = events.pop(index)
                logger.info(f"Removed event: {removed_event.get('title')}")
        
        session['events'] = events
        session.modified = True
    
    return redirect(url_for('api.events'))

@api_bp.route('/events/sync', methods=['GET', 'POST'])
@require_auth
def sync_to_calendar():
    """Sync all events to Google Calendar"""
    if 'events' not in session or not session['events']:
        return redirect(url_for('api.events'))
    
    token = session.get('token')
    if not token:
        return redirect(url_for('auth.login'))
    
    try:
        # Convert session events to Event objects
        events = [Event.from_dict(e) for e in session['events']]
        
        # Create calendar service and sync events
        calendar_service = CalendarService(token)
        results = calendar_service.create_events_batch(events)
        
        logger.info(f"Successfully synced {len(results)} events to calendar")
        
        # Clear events from session
        session.pop('events', None)
        session.modified = True
        
        return redirect(url_for('api.events'))
    
    except Exception as e:
        logger.error(f"Error syncing to calendar: {str(e)}")
        return jsonify({'error': 'Failed to sync events to calendar'}), 500