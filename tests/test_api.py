# API Endpoint Tests for 3D Print Management System
"""
Test suite for Flask API endpoints following standard patterns.
Tests authentication, validation, workflow transitions, and error handling.
"""

import pytest
import json
from datetime import datetime, timedelta
from app import create_app
from app.models import Job, Event, Staff, db
from app.services.auth_service import generate_workstation_token


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(config_name='testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture  
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Generate authentication headers for testing."""
    token = generate_workstation_token('test-workstation')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_job():
    """Create sample job for testing."""
    job = Job(
        id='test-job-123',
        student_name='Jane Doe',
        student_email='jane@university.edu',
        discipline='Engineering',
        class_number='ENGR 4000',
        original_filename='test_model.stl',
        display_name='JaneDoe_Filament_Blue_123.stl',
        file_path='/storage/Uploaded/JaneDoe_Filament_Blue_123.stl',
        metadata_path='/storage/Uploaded/JaneDoe_Filament_Blue_123.json',
        status='UPLOADED',
        printer='Prusa MK4S',
        color='Blue',
        material='filament'
    )
    db.session.add(job)
    db.session.commit()
    return job


@pytest.fixture
def sample_staff():
    """Create sample staff member."""
    staff = Staff(name='Test Staff', is_active=True)
    db.session.add(staff)
    db.session.commit()
    return staff


class TestAuthenticationEndpoints:
    """Test authentication and authorization."""
    
    def test_workstation_login_success(self, client):
        """Test successful workstation login."""
        response = client.post('/api/v1/auth/login', json={
            'workstation_id': 'test-workstation',
            'password': 'test-password'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['workstation_id'] == 'test-workstation'
    
    def test_workstation_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/v1/auth/login', json={
            'workstation_id': 'invalid',
            'password': 'wrong'
        })
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'invalid_credentials'
    
    def test_protected_endpoint_without_auth(self, client):
        """Test accessing protected endpoint without authentication."""
        response = client.get('/api/v1/jobs')
        assert response.status_code == 401


class TestJobManagementEndpoints:
    """Test job-related API endpoints."""
    
    def test_list_jobs_success(self, client, auth_headers, sample_job):
        """Test retrieving job list."""
        response = client.get('/api/v1/jobs', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'jobs' in data
        assert len(data['jobs']) == 1
        assert data['jobs'][0]['id'] == 'test-job-123'
    
    def test_get_job_details(self, client, auth_headers, sample_job):
        """Test retrieving specific job details."""
        response = client.get(f'/api/v1/jobs/{sample_job.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job']['student_name'] == 'Jane Doe'
        assert data['job']['status'] == 'UPLOADED'
    
    def test_get_nonexistent_job(self, client, auth_headers):
        """Test retrieving non-existent job."""
        response = client.get('/api/v1/jobs/nonexistent', headers=auth_headers)
        assert response.status_code == 404
    
    def test_approve_job_success(self, client, auth_headers, sample_job, sample_staff):
        """Test successful job approval."""
        approval_data = {
            'weight_g': 25.5,
            'time_hours': 3.0,
            'authoritative_file': 'test_model.stl',
            'staff_name': sample_staff.name
        }
        
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/approve',
            headers=auth_headers,
            json=approval_data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job']['status'] == 'PENDING'
        assert data['job']['weight_g'] == 25.5
        
        # Verify event log creation
        events = Event.query.filter_by(job_id=sample_job.id).all()
        assert len(events) == 1
        assert events[0].event_type == 'StaffApproved'
    
    def test_approve_job_validation_errors(self, client, auth_headers, sample_job):
        """Test job approval with validation errors."""
        invalid_data = {
            'weight_g': -1,  # Invalid negative weight
            'time_hours': 0,  # Invalid zero time
            # Missing required fields
        }
        
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/approve',
            headers=auth_headers,
            json=invalid_data
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'validation_failed'
        assert 'details' in data
    
    def test_approve_job_wrong_status(self, client, auth_headers, sample_job, sample_staff):
        """Test approving job in wrong status."""
        sample_job.status = 'PENDING'
        db.session.commit()
        
        approval_data = {
            'weight_g': 25.5,
            'time_hours': 3.0,
            'authoritative_file': 'test_model.stl',
            'staff_name': sample_staff.name
        }
        
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/approve',
            headers=auth_headers,
            json=approval_data
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'invalid_status'
    
    def test_reject_job_success(self, client, auth_headers, sample_job, sample_staff):
        """Test successful job rejection."""
        rejection_data = {
            'reasons': ['too_large', 'poor_quality'],
            'custom_reason': 'Model needs support structures',
            'staff_name': sample_staff.name
        }
        
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/reject',
            headers=auth_headers,
            json=rejection_data
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job']['status'] == 'REJECTED'
        
        # Verify event log creation
        events = Event.query.filter_by(job_id=sample_job.id).all()
        assert len(events) == 1
        assert events[0].event_type == 'StaffRejected'


class TestJobLocking:
    """Test job locking mechanism."""
    
    def test_lock_job_success(self, client, auth_headers, sample_job):
        """Test successfully locking a job."""
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/lock',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'locked_until' in data
    
    def test_lock_already_locked_job(self, client, auth_headers, sample_job):
        """Test locking a job that's already locked."""
        # First lock
        client.post(f'/api/v1/jobs/{sample_job.id}/lock', headers=auth_headers)
        
        # Try to lock again
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/lock',
            headers=auth_headers
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['error'] == 'job_locked'
    
    def test_unlock_job_success(self, client, auth_headers, sample_job):
        """Test successfully unlocking a job."""
        # First lock the job
        client.post(f'/api/v1/jobs/{sample_job.id}/lock', headers=auth_headers)
        
        # Then unlock it
        response = client.post(
            f'/api/v1/jobs/{sample_job.id}/unlock',
            headers=auth_headers
        )
        
        assert response.status_code == 200


class TestStatusTransitions:
    """Test job status transitions."""
    
    def test_mark_job_printing(self, client, auth_headers, sample_staff):
        """Test marking job as printing."""
        # Create job in READYTOPRINT status
        job = Job(
            id='ready-job-123',
            status='READYTOPRINT',
            student_name='Test Student',
            student_email='test@university.edu'
        )
        db.session.add(job)
        db.session.commit()
        
        response = client.post(
            f'/api/v1/jobs/{job.id}/mark-printing',
            headers=auth_headers,
            json={'staff_name': sample_staff.name}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job']['status'] == 'PRINTING'
    
    def test_mark_job_complete(self, client, auth_headers, sample_staff):
        """Test marking job as complete."""
        # Create job in PRINTING status
        job = Job(
            id='printing-job-123',
            status='PRINTING',
            student_name='Test Student',
            student_email='test@university.edu'
        )
        db.session.add(job)
        db.session.commit()
        
        response = client.post(
            f'/api/v1/jobs/{job.id}/mark-complete',
            headers=auth_headers,
            json={'staff_name': sample_staff.name}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job']['status'] == 'COMPLETED'


class TestHealthCheck:
    """Test system health endpoint."""
    
    def test_health_check_success(self, client):
        """Test health check endpoint."""
        response = client.get('/api/v1/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'components' in data


if __name__ == '__main__':
    pytest.main([__file__])