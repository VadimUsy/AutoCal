import datetime
import pytz
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import List
from app.models.event import Event
from app.config import config

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for Google Calendar operations"""
    
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    
    def __init__(self, token: dict):
        """Initialize calendar service with OAuth token"""
        self.token = token
        self.credentials = self._build_credentials()
        self.service = None
    
    def _build_credentials(self) -> Credentials:
        """Build Google credentials from token"""
        creds = Credentials(
            token=self.token['access_token'],
            refresh_token=self.token.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=config.GOOGLE_CLIENT_ID,
            client_secret=config.GOOGLE_CLIENT_SECRET,
            scopes=self.SCOPES
        )
        
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        return creds
    
    def _get_service(self):
        """Get or create calendar service"""
        if not self.service:
            self.service = build('calendar', 'v3', credentials=self.credentials)
        return self.service
    
    def create_event(self, event: Event) -> dict:
        """Create a single calendar event"""
        local_tz = pytz.timezone(config.LOCAL_TIMEZONE)
        
        # Convert 12-hour time to 24-hour time
        hour_24 = event.hour
        if event.ampm == 'PM' and event.hour != 12:
            hour_24 += 12
        elif event.ampm == 'AM' and event.hour == 12:
            hour_24 = 0
        
        start_datetime = datetime.datetime(
            event.year,
            event.month,
            event.day,
            hour_24,
            event.minute
        )
        
        # Localize to timezone
        start_datetime = local_tz.localize(start_datetime)
        end_datetime = start_datetime + datetime.timedelta(
            hours=config.DEFAULT_EVENT_DURATION_HOURS
        )
        
        event_body = {
            'summary': event.title,
            'description': event.description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': str(local_tz)
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': str(local_tz)
            },
        }
        
        service = self._get_service()
        result = service.events().insert(
            calendarId='primary',
            body=event_body
        ).execute()
        
        logger.info(f"Created event: {event.title} at {start_datetime}")
        return result
    
    def create_events_batch(self, events: List[Event]) -> List[dict]:
        """Create multiple calendar events"""
        results = []
        for event in events:
            try:
                result = self.create_event(event)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to create event {event.title}: {str(e)}")
                raise
        return results
