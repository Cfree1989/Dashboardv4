#!/usr/bin/env python3
# Initialize Staff Members - 3D Print Management System
"""
Script to create initial staff members for testing and development.
Run this after database migration to populate the Staff table.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.database import db
from app.models.staff import Staff


def create_initial_staff():
    """Create initial staff members for development/testing."""
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Creating initial staff members...")
        
        # Define initial staff members
        initial_staff = [
            {
                'name': 'Jane Doe',
                'notes': 'Initial staff member - Lab Manager'
            },
            {
                'name': 'John Smith', 
                'notes': 'Initial staff member - Lab Assistant'
            },
            {
                'name': 'Admin User',
                'notes': 'System Administrator'
            },
            {
                'name': 'Sarah Wilson',
                'notes': 'Part-time Lab Assistant'
            }
        ]
        
        created_count = 0
        
        for staff_data in initial_staff:
            # Check if staff member already exists
            existing_staff = Staff.find_by_name(staff_data['name'])
            
            if existing_staff:
                print(f"  Staff member '{staff_data['name']}' already exists - skipping")
                continue
            
            # Create new staff member
            try:
                staff = Staff.create_staff_member(
                    name=staff_data['name'],
                    notes=staff_data['notes']
                )
                
                db.session.commit()
                created_count += 1
                print(f"  ✓ Created staff member: {staff_data['name']}")
                
            except Exception as e:
                db.session.rollback()
                print(f"  ✗ Failed to create staff member '{staff_data['name']}': {str(e)}")
        
        print(f"\nInitialization complete!")
        print(f"Created {created_count} new staff members")
        
        # Show all active staff
        all_staff = Staff.get_active_staff()
        print(f"Total active staff members: {len(all_staff)}")
        for staff in all_staff:
            print(f"  - {staff.name}")


if __name__ == '__main__':
    create_initial_staff()