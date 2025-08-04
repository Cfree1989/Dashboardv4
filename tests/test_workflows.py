# Workflow Integration Tests for 3D Print Management System
"""
Test suite for complete workflow scenarios from submission to completion.
Tests file operations, status transitions, email notifications, and data integrity.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app import create_app
from app.models import Job, Event, Payment, Staff, db
from app.services.file_service import move_job_file_safely
from app.services.email_service import send_approval_email, send_completion_email
from app.utils.cost_calculator import calculate_print_cost


@pytest.fixture
def app():
    """Create test Flask application with temporary file storage."""
    app = create_app(config_name='testing')
    
    # Create temporary directory for test file operations
    temp_dir = tempfile.mkdtemp()
    app.config['STORAGE_BASE_PATH'] = temp_dir
    
    with app.app_context():
        db.create_all()
        
        # Create test storage directories
        for status_dir in ['Uploaded', 'Pending', 'ReadyToPrint', 'Printing', 'Completed', 'PaidPickedUp', 'Archived']:
            os.makedirs(os.path.join(temp_dir, status_dir), exist_ok=True)
        
        yield app
        
        # Cleanup
        db.drop_all()
        shutil.rmtree(temp_dir)


@pytest.fixture
def sample_staff():
    """Create sample staff member."""
    staff = Staff(name='Test Staff Member', is_active=True)
    db.session.add(staff)
    db.session.commit()
    return staff


class TestCompleteJobWorkflow:
    """Test end-to-end job workflow scenarios."""
    
    def create_test_file(self, storage_path, filename):
        """Helper to create test files."""
        file_path = os.path.join(storage_path, filename)
        with open(file_path, 'w') as f:
            f.write('test file content')
        return file_path
    
    def test_complete_successful_workflow(self, app, sample_staff):
        """Test complete workflow from submission to pickup."""
        with app.app_context():
            storage_base = app.config['STORAGE_BASE_PATH']
            
            # 1. Create initial job (simulates student submission)
            job = Job(
                id='workflow-test-123',
                student_name='Alice Johnson',
                student_email='alice@university.edu',
                discipline='Architecture',
                class_number='ARCH 4000',
                original_filename='building_model.stl',
                display_name='AliceJohnson_Filament_Red_123.stl',
                file_path=os.path.join(storage_base, 'Uploaded', 'AliceJohnson_Filament_Red_123.stl'),
                metadata_path=os.path.join(storage_base, 'Uploaded', 'AliceJohnson_Filament_Red_123.json'),
                status='UPLOADED',
                printer='Prusa MK4S',
                color='Red',
                material='filament',
                acknowledged_minimum_charge=True
            )
            db.session.add(job)
            db.session.commit()
            
            # Create test files
            self.create_test_file(storage_base, f'Uploaded/{job.display_name}')
            self.create_test_file(storage_base, f'Uploaded/{job.display_name.replace(".stl", ".json")}')
            
            # 2. Staff approval workflow
            job.weight_g = 35.2
            job.time_hours = 4.5
            job.cost_usd = calculate_print_cost(35.2, 'filament')
            job.status = 'PENDING'
            job.last_updated_by = sample_staff.name
            job.generate_confirmation_token()
            
            # Log approval event
            approval_event = Event(
                job_id=job.id,
                event_type='StaffApproved',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation',
                details={
                    'weight_g': 35.2,
                    'time_hours': 4.5,
                    'cost_usd': float(job.cost_usd)
                }
            )
            db.session.add(approval_event)
            db.session.commit()
            
            # Move files to Pending
            move_job_file_safely(job, 'PENDING', job.display_name)
            
            # Verify files moved correctly
            assert os.path.exists(os.path.join(storage_base, 'Pending', job.display_name))
            assert not os.path.exists(os.path.join(storage_base, 'Uploaded', job.display_name))
            
            # 3. Student confirmation
            job.student_confirmed = True
            job.student_confirmed_at = datetime.utcnow()
            job.status = 'READYTOPRINT'
            
            confirmation_event = Event(
                job_id=job.id,
                event_type='StudentConfirmed',
                triggered_by='student',
                details={'confirmation_method': 'email_link'}
            )
            db.session.add(confirmation_event)
            db.session.commit()
            
            # Move files to ReadyToPrint
            move_job_file_safely(job, 'READYTOPRINT', job.display_name)
            
            # 4. Start printing
            job.status = 'PRINTING'
            
            printing_event = Event(
                job_id=job.id,
                event_type='PrintingStarted',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation'
            )
            db.session.add(printing_event)
            db.session.commit()
            
            move_job_file_safely(job, 'PRINTING', job.display_name)
            
            # 5. Complete printing
            job.status = 'COMPLETED'
            
            completion_event = Event(
                job_id=job.id,
                event_type='PrintingCompleted',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation'
            )
            db.session.add(completion_event)
            db.session.commit()
            
            move_job_file_safely(job, 'COMPLETED', job.display_name)
            
            # 6. Payment and pickup
            actual_weight = 34.8  # Slightly different from estimate
            final_cost = calculate_print_cost(actual_weight, 'filament')
            
            payment = Payment(
                job_id=job.id,
                grams=actual_weight,
                price_cents=int(final_cost * 100),
                txn_no='TC123456789',
                picked_up_by='Alice Johnson',
                paid_by_staff=sample_staff.name
            )
            db.session.add(payment)
            
            job.status = 'PAIDPICKEDUP'
            
            pickup_event = Event(
                job_id=job.id,
                event_type='JobPickedUp',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation',
                details={'payment_amount': final_cost, 'txn_no': 'TC123456789'}
            )
            db.session.add(pickup_event)
            db.session.commit()
            
            move_job_file_safely(job, 'PAIDPICKEDUP', job.display_name)
            
            # Verify final state
            assert job.status == 'PAIDPICKEDUP'
            assert job.payment.txn_no == 'TC123456789'
            assert len(job.events) == 6  # All workflow events logged
            assert os.path.exists(os.path.join(storage_base, 'PaidPickedUp', job.display_name))
    
    def test_job_rejection_workflow(self, app, sample_staff):
        """Test job rejection workflow."""
        with app.app_context():
            storage_base = app.config['STORAGE_BASE_PATH']
            
            # Create job for rejection
            job = Job(
                id='reject-test-123',
                student_name='Bob Wilson',
                student_email='bob@university.edu',
                status='UPLOADED',
                original_filename='bad_model.stl',
                display_name='BobWilson_Filament_Blue_123.stl',
                file_path=os.path.join(storage_base, 'Uploaded', 'BobWilson_Filament_Blue_123.stl'),
                material='filament'
            )
            db.session.add(job)
            db.session.commit()
            
            self.create_test_file(storage_base, f'Uploaded/{job.display_name}')
            
            # Staff rejects job
            job.status = 'REJECTED'
            job.reject_reasons = ['too_large', 'poor_quality']
            job.last_updated_by = sample_staff.name
            
            rejection_event = Event(
                job_id=job.id,
                event_type='StaffRejected',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation',
                details={
                    'reasons': ['too_large', 'poor_quality'],
                    'custom_reason': 'Model exceeds printer dimensions'
                }
            )
            db.session.add(rejection_event)
            db.session.commit()
            
            # File should remain in Uploaded directory for rejected jobs
            assert os.path.exists(os.path.join(storage_base, 'Uploaded', job.display_name))
            assert job.status == 'REJECTED'
            assert 'too_large' in job.reject_reasons
    
    def test_print_failure_recovery(self, app, sample_staff):
        """Test handling of print failures."""
        with app.app_context():
            storage_base = app.config['STORAGE_BASE_PATH']
            
            # Create job in PRINTING status
            job = Job(
                id='failure-test-123',
                student_name='Carol Davis',
                student_email='carol@university.edu',
                status='PRINTING',
                original_filename='test_model.stl',
                display_name='CarolDavis_Resin_Clear_123.stl',
                file_path=os.path.join(storage_base, 'Printing', 'CarolDavis_Resin_Clear_123.stl'),
                material='resin',
                weight_g=15.3,
                time_hours=2.5,
                cost_usd=3.06,
                student_confirmed=True
            )
            db.session.add(job)
            db.session.commit()
            
            self.create_test_file(storage_base, f'Printing/{job.display_name}')
            
            # Simulate print failure (lab error - return to queue)
            job.status = 'READYTOPRINT'
            
            failure_event = Event(
                job_id=job.id,
                event_type='PrintFailed',
                triggered_by=sample_staff.name,
                workstation_id='test-workstation',
                details={'reason': 'Filament jam detected', 'failure_type': 'lab_error'}
            )
            db.session.add(failure_event)
            db.session.commit()
            
            # Move file back to ReadyToPrint
            move_job_file_safely(job, 'READYTOPRINT', job.display_name)
            
            # Verify job is back in queue without requiring re-confirmation
            assert job.status == 'READYTOPRINT'
            assert job.student_confirmed == True  # Still confirmed
            assert os.path.exists(os.path.join(storage_base, 'ReadyToPrint', job.display_name))


class TestFileOperations:
    """Test file management and integrity."""
    
    def test_file_move_safety(self, app):
        """Test copy-update-delete file operation pattern."""
        with app.app_context():
            storage_base = app.config['STORAGE_BASE_PATH']
            
            # Create test job and file
            job = Job(
                id='file-test-123',
                status='UPLOADED',
                display_name='TestFile.stl',
                file_path=os.path.join(storage_base, 'Uploaded', 'TestFile.stl')
            )
            
            original_path = job.file_path
            with open(original_path, 'w') as f:
                f.write('original file content')
            
            # Test safe file move
            move_job_file_safely(job, 'PENDING', 'TestFile.stl')
            
            # Verify file moved and original is gone
            new_path = os.path.join(storage_base, 'Pending', 'TestFile.stl')
            assert os.path.exists(new_path)
            assert not os.path.exists(original_path)
            assert job.file_path == new_path
            
            # Verify content preserved
            with open(new_path, 'r') as f:
                assert f.read() == 'original file content'
    
    @patch('app.services.file_service.shutil.copy2')
    def test_file_operation_failure_handling(self, mock_copy, app):
        """Test handling of file operation failures."""
        with app.app_context():
            storage_base = app.config['STORAGE_BASE_PATH'] 
            
            job = Job(
                id='fail-test-123',
                status='UPLOADED',
                display_name='FailTest.stl',
                file_path=os.path.join(storage_base, 'Uploaded', 'FailTest.stl')
            )
            
            # Create original file
            with open(job.file_path, 'w') as f:
                f.write('test content')
            
            original_status = job.status
            original_path = job.file_path
            
            # Mock file copy failure
            mock_copy.side_effect = OSError("Permission denied")
            
            # Attempt file move should fail gracefully
            with pytest.raises(OSError):
                move_job_file_safely(job, 'PENDING', 'FailTest.stl')
            
            # Verify job state unchanged after failure
            assert job.status == original_status
            assert job.file_path == original_path
            assert os.path.exists(original_path)


class TestEmailNotifications:
    """Test email notification workflows."""
    
    @patch('app.services.email_service.send_email')
    def test_approval_email_queued(self, mock_send_email, app, sample_staff):
        """Test that approval emails are properly queued."""
        with app.app_context():
            job = Job(
                id='email-test-123',
                student_name='Diana Prince',
                student_email='diana@university.edu',
                status='PENDING', 
                cost_usd=3.52,
                confirm_token='test-token-123'
            )
            db.session.add(job)
            db.session.commit()
            
            # Queue approval email
            send_approval_email(job.id, job.confirm_token)
            
            # Verify email was queued (in real implementation, this would be async)
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['to'] == 'diana@university.edu'
            assert 'approve' in call_args['subject'].lower()
    
    @patch('app.services.email_service.send_email')
    def test_completion_email_queued(self, mock_send_email, app):
        """Test that completion emails are properly queued."""
        with app.app_context():
            job = Job(
                id='complete-email-test',
                student_name='Edward Norton',
                student_email='edward@university.edu',
                status='COMPLETED',
                cost_usd=4.80
            )
            db.session.add(job)
            db.session.commit()
            
            # Queue completion email
            send_completion_email(job.id)
            
            # Verify email was queued
            mock_send_email.assert_called_once()
            call_args = mock_send_email.call_args[1]
            assert call_args['to'] == 'edward@university.edu'
            assert 'complete' in call_args['subject'].lower()


class TestDataIntegrity:
    """Test data consistency and audit trails."""
    
    def test_event_logging_completeness(self, app, sample_staff):
        """Test that all major actions create event logs."""
        with app.app_context():
            job = Job(
                id='event-test-123',
                student_name='Frank Castle',
                student_email='frank@university.edu',
                status='UPLOADED'
            )
            db.session.add(job)
            db.session.commit()
            
            # Perform various actions and verify event creation
            actions = [
                ('StaffApproved', {'weight_g': 20.0}),
                ('StudentConfirmed', {'confirmation_method': 'email'}),
                ('PrintingStarted', {}),
                ('PrintingCompleted', {}),
                ('JobPickedUp', {'payment_amount': 3.00})
            ]
            
            for event_type, details in actions:
                event = Event(
                    job_id=job.id,
                    event_type=event_type,
                    triggered_by=sample_staff.name,
                    workstation_id='test-workstation',
                    details=details
                )
                db.session.add(event)
            
            db.session.commit()
            
            # Verify all events were logged
            events = Event.query.filter_by(job_id=job.id).all()
            assert len(events) == 5
            
            event_types = [e.event_type for e in events]
            for action_type, _ in actions:
                assert action_type in event_types
    
    def test_staff_attribution_integrity(self, app):
        """Test that staff attribution is preserved correctly."""
        with app.app_context():
            # Create multiple staff members
            staff1 = Staff(name='Alice Admin', is_active=True)
            staff2 = Staff(name='Bob Staff', is_active=True)
            db.session.add_all([staff1, staff2])
            db.session.commit()
            
            job = Job(id='attribution-test', status='UPLOADED')
            db.session.add(job)
            db.session.commit()
            
            # Create events attributed to different staff
            event1 = Event(
                job_id=job.id,
                event_type='StaffApproved',
                triggered_by=staff1.name,
                workstation_id='workstation-1'
            )
            
            event2 = Event(
                job_id=job.id,
                event_type='PrintingCompleted',
                triggered_by=staff2.name,
                workstation_id='workstation-2'
            )
            
            db.session.add_all([event1, event2])
            db.session.commit()
            
            # Verify attribution is correctly stored
            events = Event.query.filter_by(job_id=job.id).order_by(Event.timestamp).all()
            assert events[0].triggered_by == 'Alice Admin'
            assert events[0].workstation_id == 'workstation-1'
            assert events[1].triggered_by == 'Bob Staff'
            assert events[1].workstation_id == 'workstation-2'


if __name__ == '__main__':
    pytest.main([__file__])