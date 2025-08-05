#!/usr/bin/env python3
# Development Server Entry Point for 3D Print Management System
"""
Development server entry point for Flask application.
Run this script to start the development server with hot reload.
"""

import os
from app import create_app, db

# Create Flask app instance
app = create_app()

# CLI commands for database management
@app.cli.command()
def init_db():
    """Create database tables."""
    db.create_all()
    print("Database tables created.")

@app.cli.command()
def reset_db():
    """Reset database (drop and recreate all tables)."""
    db.drop_all()
    db.create_all()
    print("Database reset complete.")

@app.cli.command()
def init_migrations():
    """Initialize database migrations."""
    import subprocess
    try:
        result = subprocess.run(['flask', 'db', 'init'], 
                              capture_output=True, text=True, check=True)
        print("Migration repository initialized successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error initializing migrations: {e}")
        print(e.stderr)

@app.cli.command()
def create_migration():
    """Create a new database migration."""
    import subprocess
    try:
        result = subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'], 
                              capture_output=True, text=True, check=True)
        print("Migration created successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error creating migration: {e}")
        print(e.stderr)

@app.cli.command()
def upgrade_db():
    """Apply database migrations."""
    import subprocess
    try:
        result = subprocess.run(['flask', 'db', 'upgrade'], 
                              capture_output=True, text=True, check=True)
        print("Database upgraded successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading database: {e}")
        print(e.stderr)

@app.cli.command()
def seed_db():
    """Seed database with sample data for development."""
    from app.models.staff import Staff
    
    # Create sample staff members
    staff_members = [
        Staff(name='Alice Johnson', is_active=True),
        Staff(name='Bob Smith', is_active=True),
        Staff(name='Carol Davis', is_active=True),
        Staff(name='Admin User', is_active=True),
    ]
    
    for staff in staff_members:
        existing = Staff.query.filter_by(name=staff.name).first()
        if not existing:
            db.session.add(staff)
    
    db.session.commit()
    print(f"Added {len(staff_members)} staff members to database.")

if __name__ == '__main__':
    # Development server configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Flask development server on {host}:{port}")
    print(f"Debug mode: {debug}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    
    app.run(host=host, port=port, debug=debug)