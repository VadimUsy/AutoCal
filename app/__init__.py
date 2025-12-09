import os
import logging
from flask import Flask
from flask_session import Session
from app.config import config
from app.auth.oauth import init_oauth

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_app():
    """Application factory pattern"""
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend',
        static_url_path='/static'
    )
    
    # Load configuration
    app.config.from_object(config)
    
    # Ensure session directory exists
    os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize extensions
    Session(app)
    init_oauth(app)
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.api.routes import api_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    return app

# Create app instance
app = create_app()