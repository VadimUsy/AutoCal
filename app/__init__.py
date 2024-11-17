import os
import secrets
from flask import Flask
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = secrets.token_hex(16)

# Configure session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), '../flask_session')
app.config['SESSION_PERMANENT'] = False
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Initialize Flask-Session
Session(app)

# Set Google OAuth credentials from environment variables
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Ensure environment variables are set
if not app.config['GOOGLE_CLIENT_ID'] or not app.config['GOOGLE_CLIENT_SECRET']:
    raise ValueError("Google Client ID and Secret must be set in the .env file.")

# Initialize OAuth without registering Google yet
oauth = OAuth(app)

# Import routes and initialize `google` after app initialization
from .routes import main_bp
app.register_blueprint(main_bp)

# Register Google OAuth after app and routes are ready
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/calendar'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    claims_options={
        'iss': {'values': ['https://accounts.google.com', 'accounts.google.com']}
    }
)
