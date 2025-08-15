"""Flask application factory and initialization."""

import logging
import os
from typing import Optional

from flask import Flask, request, g
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException
import uuid

from .config import get_config

# Initialize extensions
db = SQLAlchemy()


def create_app(config_name: Optional[str] = None) -> Flask:
    """Create and configure Flask application using factory pattern."""
    
    app = Flask(__name__)
    
    # Load configuration
    config_class = get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
        }
    })
    
    # Configure logging
    configure_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register request handlers
    register_request_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def configure_logging(app: Flask) -> None:
    """Configure application logging."""
    
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Set Flask logger level
    app.logger.setLevel(log_level)
    
    # Configure file logging if specified
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s [%(filename)s:%(lineno)d]: %(message)s'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


def register_blueprints(app: Flask) -> None:
    """Register application blueprints."""
    
    # Import blueprints here to avoid circular imports
    from .api.routes import api_bp
    from .web.routes import web_bp
    
    # Register API blueprint
    app.register_blueprint(api_bp, url_prefix=f'/api/{app.config["API_VERSION"]}')
    
    # Register web blueprint
    app.register_blueprint(web_bp, url_prefix='/')


def register_error_handlers(app: Flask) -> None:
    """Register application error handlers."""
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e: HTTPException) -> tuple:
        """Handle HTTP exceptions with JSON responses."""
        
        response = {
            'error': {
                'code': e.code,
                'name': e.name,
                'description': e.description,
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        app.logger.error(f"HTTP {e.code} error: {e.description}")
        return response, e.code
    
    @app.errorhandler(500)
    def handle_internal_error(error) -> tuple:
        """Handle internal server errors."""
        
        response = {
            'error': {
                'code': 500,
                'name': 'Internal Server Error',
                'description': 'An unexpected error occurred.',
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        app.logger.error(f"Internal server error: {error}", exc_info=True)
        return response, 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error) -> tuple:
        """Handle unexpected errors."""
        
        response = {
            'error': {
                'code': 500,
                'name': 'Unexpected Error',
                'description': 'An unexpected error occurred.',
                'request_id': getattr(g, 'request_id', None)
            }
        }
        
        app.logger.error(f"Unexpected error: {error}", exc_info=True)
        return response, 500


def register_request_handlers(app: Flask) -> None:
    """Register request-level handlers for logging and tracking."""
    
    @app.before_request
    def before_request():
        """Set up request tracking and logging."""
        
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        
        # Log request details
        app.logger.debug(
            f"Request {g.request_id}: {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def after_request(response):
        """Log response details."""
        
        app.logger.debug(
            f"Response {getattr(g, 'request_id', 'unknown')}: "
            f"{response.status_code} for {request.method} {request.path}"
        )
        
        return response


# Health check route
def register_health_route(app: Flask) -> None:
    """Register health check endpoint."""
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        
        return {
            'status': 'healthy',
            'version': app.config.get('API_VERSION', 'v1'),
            'environment': app.config.get('FLASK_ENV', 'unknown')
        }


if __name__ == '__main__':
    # For development purposes
    app = create_app('development')
    register_health_route(app)
    app.run(host='0.0.0.0', port=5000, debug=True)