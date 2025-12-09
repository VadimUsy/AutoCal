from authlib.integrations.flask_client import OAuth

oauth = OAuth()

def init_oauth(app):
    """Initialize OAuth with the Flask app"""
    oauth.init_app(app)
    
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        client_kwargs={'scope': ' '.join(app.config['GOOGLE_OAUTH_SCOPES'])},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        claims_options={
            'iss': {'values': ['https://accounts.google.com', 'accounts.google.com']}
        }
    )
    
    return google