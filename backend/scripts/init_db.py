#!/usr/bin/env python3
# Database Initialization Script for 3D Print Management System
"""
Script to initialize the database schema and create sample data.
Run this after starting the database service to set up the initial state.
"""

import os
import sys

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.database import db
from app.models.staff import Staff
from app.models.job import Job
from app.models.event import Event
from app.models.payment import Payment


def init_database():
    """Initialize database schema and sample data."""
    app = create_app('development')
    
    with app.app_context():
        print("🗄️  Initializing database schema...")
        
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")
        
        # Create sample staff members
        print("👥 Creating sample staff members...")
        staff_members = [
            Staff(name='Alice Johnson', is_active=True),
            Staff(name='Bob Smith', is_active=True), 
            Staff(name='Carol Davis', is_active=True),
            Staff(name='Admin User', is_active=True),
        ]
        
        added_count = 0
        for staff in staff_members:
            existing = Staff.query.filter_by(name=staff.name).first()
            if not existing:
                db.session.add(staff)
                added_count += 1
        
        db.session.commit()
        print(f"✅ Added {added_count} staff members to database")
        
        # Verify tables exist
        print("🔍 Verifying database schema...")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['job', 'event', 'staff', 'payment']
        for table in expected_tables:
            if table in tables:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
        
        print("🎉 Database initialization complete!")


if __name__ == '__main__':
    init_database()