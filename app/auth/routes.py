import logging
from flask import Blueprint, redirect, url_for, session
from authlib.integrations.flask_client import OAuthError
from app.auth.oauth import oauth

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """Initiate Google OAuth login"""
    redirect_uri = url_for('auth.authorized', _external=True)
    google = oauth.create_client('google')
    return google.authorize_redirect(redirect_uri, prompt='consent')

@auth_bp.route('/login/google/authorized')
def authorized():
    """Handle OAuth callback from Google"""
    google = oauth.create_client('google')
    claims_options = {
        'iss': {'values': ['https://accounts.google.com', 'accounts.google.com']}
    }
    
    try:
        token = google.authorize_access_token(claims_options=claims_options)
    except OAuthError as e:
        logger.error(f"OAuthError: {e.error} - {e.description}")
        return redirect(url_for('auth.login'))
    
    # Parse ID token
    id_token = token.get('id_token')
    if id_token:
        nonce = token.get('nonce')
        claims = google.parse_id_token(token, nonce=nonce, claims_options=claims_options)
        logger.debug(f"ID Token claims: {claims}")
    
    if not token:
        return redirect(url_for('auth.login'))
    
    # Store token and user info in session
    session['token'] = token
    session['user'] = google.get('https://www.googleapis.com/oauth2/v3/userinfo').json()
    
    return redirect(url_for('api.events'))

@auth_bp.route('/logout')
def logout():
    """Clear session and logout user"""
    session.clear()
    return redirect(url_for('auth.login'))