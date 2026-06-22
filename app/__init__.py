"""Flask Application Factory"""
from flask import Flask
from flask_cors import CORS
from config import config_by_name
from app.extensions import db, migrate, login_manager
from app.utils.helpers import register_blueprints


def create_app(config_name='dev'):
    """
    Application Factory Pattern
    Args:
        config_name: Configuration name ('dev', 'prod', 'test')
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
