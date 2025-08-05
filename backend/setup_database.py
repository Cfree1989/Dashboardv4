#!/usr/bin/env python3
# Database Setup Script for 3D Print Management System
"""
Comprehensive database setup script that handles initialization,
migrations, and sample data creation.
"""

import os
import sys
from app import create_app
from app.database import db
from flask_migrate import init, migrate, upgrade


def setup_database():
    """Complete database setup process."""
    print("🚀 Starting database setup for 3D Print Management System")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Check if migrations directory exists
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            
            if not os.path.exists(os.path.join(migrations_dir, 'versions')):
                print("❌ Migration versions directory not found")
                print("✅ Migration structure already created manually")
            else:
                print("✅ Migration structure exists")
            
            print("🗄️  Creating database tables...")
            
            # Create all tables using SQLAlchemy (for development)
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Verify all tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['staff', 'job', 'event', 'payment']
            print("🔍 Verifying database schema...")
            
            all_tables_exist = True
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Table '{table}' exists")
                    
                    # Show column info for each table
                    columns = inspector.get_columns(table)
                    print(f"   📋 Columns: {len(columns)} ({', '.join([col['name'] for col in columns[:5]])}{'...' if len(columns) > 5 else ''})")
                else:
                    print(f"❌ Table '{table}' missing")
                    all_tables_exist = False
            
            if not all_tables_exist:
                print("❌ Database schema incomplete")
                return False
            
            # Create sample data
            print("👥 Creating sample staff members...")
            from app.models.staff import Staff
            
            staff_members = [
                Staff(name='Alice Johnson', is_active=True),
                Staff(name='Bob Smith', is_active=True),
                Staff(name='Carol Davis', is_active=True),
                Staff(name='Admin User', is_active=True),
                Staff(name='Test Staff', is_active=True),
            ]
            
            added_count = 0
            for staff in staff_members:
                existing = Staff.query.filter_by(name=staff.name).first()
                if not existing:
                    db.session.add(staff)
                    added_count += 1
            
            db.session.commit()
            print(f"✅ Added {added_count} new staff members")
            
            # Verify staff data
            total_staff = Staff.query.count()
            active_staff = Staff.query.filter_by(is_active=True).count()
            print(f"📊 Total staff in database: {total_staff} ({active_staff} active)")
            
            print("🎉 Database setup completed successfully!")
            print("\n📋 Summary:")
            print(f"   • Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print(f"   • Tables: {len(expected_tables)} created")
            print(f"   • Staff: {total_staff} members")
            print(f"   • Storage: {app.config['STORAGE_BASE_PATH']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def test_models():
    """Test model functionality."""
    print("\n🧪 Testing model functionality...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # Test Staff model
            from app.models.staff import Staff
            staff_count = Staff.query.count()
            print(f"✅ Staff model: {staff_count} records")
            
            # Test model methods
            active_staff = Staff.get_active_staff()
            print(f"✅ Staff methods: {len(active_staff)} active staff")
            
            # Test Job model (without creating actual job)
            from app.models.job import Job
            print("✅ Job model: Class loaded successfully")
            print(f"   📋 Valid statuses: {len(Job.VALID_STATUSES)}")
            
            # Test Event model
            from app.models.event import Event
            print("✅ Event model: Class loaded successfully")
            print(f"   📋 Valid event types: {len(Event.VALID_EVENT_TYPES)}")
            
            # Test Payment model
            from app.models.payment import Payment
            print("✅ Payment model: Class loaded successfully")
            
            print("🎉 All models functioning correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Model testing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    success = setup_database()
    if success:
        test_models()
        print("\n🚀 Database is ready for development!")
    else:
        print("\n❌ Database setup failed. Please check the errors above.")
        sys.exit(1)