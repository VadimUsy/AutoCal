import os
import json

class Config:
    """Application configuration"""
    
    def __init__(self):
        self._load_credentials()
        
    def _load_credentials(self):
        """Load Google OAuth credentials from credentials.json"""
        credentials_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'credentials.json'
        )
        with open(credentials_path) as f:
            credentials = json.load(f)
        
        self.GOOGLE_CLIENT_ID = credentials['web']['client_id']
        self.GOOGLE_CLIENT_SECRET = credentials['web']['client_secret']
        
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google Client ID and Secret must be set in credentials.json")
    
    # Flask configuration
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), '../flask_session')
    SESSION_PERMANENT = False
    
    # OAuth configuration
    GOOGLE_OAUTH_SCOPES = [
        'openid',
        'email',
        'profile',
        'https://www.googleapis.com/auth/calendar'
    ]
    
    # Calendar configuration
    LOCAL_TIMEZONE = 'America/New_York'
    DEFAULT_EVENT_DURATION_HOURS = 1

config = Config()