# Flask App Factory for 3D Print Management System
"""
Flask application factory following the pattern described in the masterplan.
Creates the Flask app with all necessary extensions and blueprints.
"""

import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

# Import database instance
from app.database import db

# Initialize other extensions
migrate = Migrate()
jwt = JWTManager()
mail = Mail()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)


def create_app(config_name=None):
    """
    Flask application factory.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(f'app.config.{config_name.title()}Config')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    
    # Configure CORS for frontend communication
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['http://localhost:3000']))
    
    # Import models (ensures they're registered with SQLAlchemy)
    from app.models import job, event, staff, payment
    
    # Register API blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.jobs import bp as jobs_bp
    from app.routes.submit import bp as submit_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.analytics import bp as analytics_bp
    from app.routes.email import bp as email_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(jobs_bp, url_prefix='/api/v1/jobs')
    app.register_blueprint(submit_bp, url_prefix='/api/v1')
    app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
    app.register_blueprint(analytics_bp, url_prefix='/api/v1')
    app.register_blueprint(email_bp, url_prefix='/api/v1')
    
    # Health check endpoint (no authentication required)
    @app.route('/api/v1/health')
    def health_check():
        """System health check endpoint for monitoring."""
        try:
            # Test database connection
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'ok'
        except Exception:
            db_status = 'error'
        
        # TODO: Test Redis connection when RQ is implemented
        worker_status = 'ok'  # Placeholder
        
        status = 'ok' if db_status == 'ok' and worker_status == 'ok' else 'error'
        
        response_data = {
            'status': status,
            'components': {
                'database': db_status,
                'workers': worker_status
            },
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return response_data, 200 if status == 'ok' else 503
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'not_found',
            'message': 'The requested resource was not found'
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {
            'error': 'internal_server_error',
            'message': 'An internal server error occurred'
        }, 500
    
    # Request/response middleware
    @app.after_request
    def after_request(response):
        """Add common headers to all responses."""
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('X-Frame-Options', 'DENY')
        response.headers.add('X-XSS-Protection', '1; mode=block')
        return response
    
    return app