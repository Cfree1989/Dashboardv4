# Configuration Classes for 3D Print Management System
"""
Configuration classes for different environments (development, testing, production).
Follows the pattern described in the masterplan for environment-specific settings.
"""

import os
from datetime import timedelta


class Config:
    """Base configuration class with common settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)  # Workstation sessions last 12 hours
    JWT_ALGORITHM = 'HS256'
    
    # File Storage
    STORAGE_BASE_PATH = os.environ.get('STORAGE_BASE_PATH') or './storage'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB file upload limit
    
    # Email Configuration (Office 365)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.office365.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # Redis/RQ Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # CORS Origins
    CORS_ORIGINS = [
        'http://localhost:3000',  # Next.js development server
        'http://127.0.0.1:3000'
    ]
    
    # Pricing Configuration
    FILAMENT_COST_PER_GRAM = 0.10  # $0.10 per gram
    RESIN_COST_PER_GRAM = 0.20     # $0.20 per gram
    MINIMUM_CHARGE = 3.00          # $3.00 minimum charge
    
    # File Extensions
    ALLOWED_EXTENSIONS = {'stl', 'obj', '3mf'}
    SLICER_EXTENSIONS = {'3mf', 'form', 'gcode'}
    
    # System Configuration
    CONFIRMATION_TOKEN_EXPIRES_HOURS = 72  # Student confirmation expires after 72 hours
    JOB_LOCK_DURATION_MINUTES = 5         # Job locks expire after 5 minutes
    ARCHIVE_RETENTION_DAYS = 90           # Jobs eligible for archival after 90 days
    PRUNE_RETENTION_DAYS = 365            # Archived jobs deleted after 1 year


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development database (PostgreSQL preferred, SQLite fallback)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://printuser:dev_password@localhost:5432/printdb'
    
    # Relaxed CORS for development
    CORS_ORIGINS = ['*']  # Allow all origins in development
    
    # Development-specific settings
    SQLALCHEMY_ECHO = True  # Log SQL queries in development
    

class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = True
    
    # In-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast JWT expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    
    # Temporary storage for testing
    STORAGE_BASE_PATH = './test_storage'
    
    # Disable email sending in tests
    MAIL_SUPPRESS_SEND = True
    

class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production database (must be PostgreSQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://printuser:production_password@db:5432/printdb'
    
    # Production CORS (restrict to actual frontend domain)
    CORS_ORIGINS = [
        os.environ.get('FRONTEND_URL', 'https://print.university.edu')
    ]
    
    # Production security settings
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    
    # Production file storage (network path)
    STORAGE_BASE_PATH = os.environ.get('STORAGE_BASE_PATH') or '/mnt/print_storage'
    
    # Stricter rate limits for production
    RATELIMIT_DEFAULT = "100 per day, 25 per hour"


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}