# Email Routes for 3D Print Management System
"""
API endpoints for email-related operations including job confirmation,
resending confirmations, and email template testing.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
from app import limiter
from app.database import db
from app.models.job import Job
from app.models.event import Event
from app.services.email_service import email_service
from app.utils.tokens import token_manager
from app.utils.auth import require_workstation_auth, require_staff_attribution


bp = Blueprint('email', __name__)


@bp.route('/confirm/<token>', methods=['POST'])
@limiter.limit("5 per minute")
def confirm_job(token):
    """
    Confirm job via email token.
    
    This endpoint is accessed by students clicking email confirmation links.
    No authentication required as the token provides security.
    """
    try:
        # Verify token
        payload = token_manager.verify_token(token, expected_action='confirm')
        if not payload:
            return jsonify({
                'error': 'Invalid or expired confirmation link',
                'code': 'INVALID_TOKEN'
            }), 400
        
        job_id = payload.get('job_id')
        if not job_id:
            return jsonify({
                'error': 'Invalid token format',
                'code': 'MALFORMED_TOKEN'
            }), 400
        
        # Get job
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'Job not found',
                'code': 'JOB_NOT_FOUND'
            }), 404
        
        # Check if job is in correct status for confirmation
        if job.status != 'PENDING':
            if job.status == 'READYTOPRINT':
                return jsonify({
                    'message': 'Job already confirmed',
                    'job': {
                        'id': job.id,
                        'status': job.status,
                        'student_name': job.student_name,
                        'original_filename': job.original_filename
                    }
                }), 200
            else:
                return jsonify({
                    'error': f'Job cannot be confirmed in current status: {job.status}',
                    'code': 'INVALID_STATUS'
                }), 400
        
        # Update job status
        job.status = 'READYTOPRINT'
        job.confirmed_at = datetime.utcnow()
        
        # Create event
        event = Event(
            job_id=job.id,
            event_type='JOB_CONFIRMED',
            description=f'Job confirmed by student via email token',
            staff_name='STUDENT',
            workstation='EMAIL_CONFIRMATION'
        )
        db.session.add(event)
        
        # Move file to ReadyToPrint directory
        from app.services.file_service import file_service
        if job.current_file_path:
            try:
                new_path = file_service.move_file_to_status(job.current_file_path, 'READYTOPRINT', job)
                if new_path:
                    job.current_file_path = new_path
            except Exception as e:
                current_app.logger.error(f"Failed to move file for job {job.id}: {str(e)}")
                # Don't fail the confirmation if file move fails
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job.id} confirmed by student via email token")
        
        return jsonify({
            'message': 'Job confirmed successfully',
            'job': {
                'id': job.id,
                'status': job.status,
                'student_name': job.student_name,
                'original_filename': job.original_filename,
                'final_cost': job.final_cost,
                'confirmed_at': job.confirmed_at.isoformat() if job.confirmed_at else None
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error confirming job with token: {str(e)}")
        return jsonify({
            'error': 'Failed to confirm job',
            'code': 'CONFIRMATION_FAILED'
        }), 500


@bp.route('/resend-confirmation', methods=['POST'])
@limiter.limit("3 per hour")
def resend_confirmation():
    """
    Resend confirmation email for a job.
    
    Rate limited to prevent abuse. Students can request new confirmation emails
    if their original token expired or they lost the email.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Validate required fields
        student_email = data.get('student_email', '').strip()
        job_id = data.get('job_id', '').strip()
        
        if not student_email or not job_id:
            return jsonify({
                'error': 'student_email and job_id are required',
                'code': 'MISSING_FIELDS'
            }), 400
        
        # Get job
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'Job not found',
                'code': 'JOB_NOT_FOUND'
            }), 404
        
        # Verify email matches job
        if job.student_email.lower() != student_email.lower():
            return jsonify({
                'error': 'Email does not match job record',
                'code': 'EMAIL_MISMATCH'
            }), 400
        
        # Check if job can receive confirmation
        if job.status not in ['UPLOADED', 'PENDING']:
            return jsonify({
                'error': f'Job in status {job.status} cannot be confirmed',
                'code': 'INVALID_STATUS'
            }), 400
        
        # Check for recent resend attempts (additional rate limiting)
        recent_events = Event.query.filter(
            Event.job_id == job.id,
            Event.event_type == 'EMAIL_CONFIRMATION_RESENT',
            Event.created_at >= datetime.utcnow() - timedelta(minutes=15)
        ).count()
        
        if recent_events > 0:
            return jsonify({
                'error': 'Confirmation email was recently sent. Please wait 15 minutes before requesting another.',
                'code': 'TOO_RECENT'
            }), 429
        
        # Send confirmation email
        success = email_service.send_submission_confirmation(job)
        if not success:
            return jsonify({
                'error': 'Failed to send confirmation email',
                'code': 'EMAIL_FAILED'
            }), 500
        
        # Log resend event
        event = Event(
            job_id=job.id,
            event_type='EMAIL_CONFIRMATION_RESENT',
            description=f'Confirmation email resent to {student_email}',
            staff_name='STUDENT',
            workstation='EMAIL_RESEND'
        )
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Confirmation email sent successfully',
            'job_id': job.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resending confirmation: {str(e)}")
        return jsonify({
            'error': 'Failed to resend confirmation',
            'code': 'RESEND_FAILED'
        }), 500


@bp.route('/templates', methods=['GET'])
@require_workstation_auth
def get_email_templates():
    """
    Get email template preview for testing and development.
    
    Staff can view email templates to verify formatting and content.
    """
    try:
        template_type = request.args.get('type', 'all')
        
        # Sample job data for template preview
        sample_job_data = {
            'student_name': 'John Doe',
            'job_id': 'job_123456789',
            'filename': 'sample_model.stl',
            'material': 'PLA',
            'color': 'Blue',
            'estimated_cost': '$5.50',
            'estimated_weight': '55g',
            'final_cost': '$6.25',
            'final_weight': '62g',
            'confirmation_url': 'http://localhost:3000/confirm/sample-token',
            'submission_date': 'March 15, 2024 at 2:30 PM',
            'staff_name': 'Jane Smith',
            'approval_date': 'March 15, 2024 at 3:45 PM',
            'estimated_completion': 'March 17, 2024',
            'rejection_reason': 'File contains unsupported geometry that cannot be printed safely.',
            'rejection_date': 'March 15, 2024 at 3:45 PM',
            'completion_date': 'March 17, 2024 at 10:15 AM',
            'pickup_hours': 'Monday-Friday 9AM-5PM, Saturday 10AM-3PM',
            'pickup_location': '3D Printing Lab - Room 234, Engineering Building',
            'pickup_instructions': 'Please bring your student ID and be prepared to pay the final cost.',
            'payment_info': 'Tiger-Cash terminal available at pickup location.',
            'days_since': '3',
            'action_required': 'Please confirm your job to proceed with printing.',
            'resubmit_url': 'http://localhost:3000/submit',
            'contact_email': 'support@3dprinting.edu'
        }
        
        templates = {}
        
        if template_type in ['all', 'submission']:
            templates['submission_confirmation'] = email_service._templates['submission_confirmation'].format(**sample_job_data)
        
        if template_type in ['all', 'approval']:
            templates['approval_notification'] = email_service._templates['approval_notification'].format(**sample_job_data)
        
        if template_type in ['all', 'rejection']:
            templates['rejection_notification'] = email_service._templates['rejection_notification'].format(**sample_job_data)
        
        if template_type in ['all', 'completion']:
            templates['completion_notification'] = email_service._templates['completion_notification'].format(**sample_job_data)
        
        if template_type in ['all', 'reminder']:
            templates['reminder_notification'] = email_service._templates['reminder_notification'].format(**sample_job_data)
        
        return jsonify({
            'templates': templates,
            'sample_data': sample_job_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting email templates: {str(e)}")
        return jsonify({
            'error': 'Failed to get email templates',
            'code': 'TEMPLATE_ERROR'
        }), 500


@bp.route('/test', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def send_test_email():
    """
    Send test email for development and testing.
    
    Allows staff to test email functionality with sample data.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        staff_name = data.get('staff_name', '').strip()
        if not staff_name:
            return jsonify({'error': 'staff_name is required'}), 400
        
        test_email = data.get('test_email', '').strip()
        template_type = data.get('template_type', 'submission').strip()
        
        if not test_email:
            return jsonify({'error': 'test_email is required'}), 400
        
        # Create sample job for testing
        from app.models.job import Job
        sample_job = Job(
            id='test_job_' + str(int(datetime.utcnow().timestamp())),
            student_name='Test Student',
            student_email=test_email,
            original_filename='test_model.stl',
            material_type='PLA',
            color='Blue',
            estimated_weight_grams=55,
            estimated_cost=5.50,
            final_weight_grams=62,
            final_cost=6.25,
            status='PENDING'
        )
        
        # Send appropriate test email
        success = False
        if template_type == 'submission':
            success = email_service.send_submission_confirmation(sample_job)
        elif template_type == 'approval':
            success = email_service.send_approval_notification(sample_job, staff_name)
        elif template_type == 'rejection':
            success = email_service.send_rejection_notification(sample_job, staff_name, 'This is a test rejection for email testing purposes.')
        elif template_type == 'completion':
            success = email_service.send_completion_notification(sample_job, staff_name)
        elif template_type == 'reminder':
            success = email_service.send_reminder_notification(sample_job, 'confirmation')
        else:
            return jsonify({
                'error': 'Invalid template_type. Must be one of: submission, approval, rejection, completion, reminder',
                'code': 'INVALID_TEMPLATE_TYPE'
            }), 400
        
        if not success:
            return jsonify({
                'error': 'Failed to send test email',
                'code': 'EMAIL_FAILED'
            }), 500
        
        return jsonify({
            'message': f'Test {template_type} email sent successfully to {test_email}',
            'template_type': template_type,
            'recipient': test_email
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error sending test email: {str(e)}")
        return jsonify({
            'error': 'Failed to send test email',
            'code': 'TEST_EMAIL_FAILED'
        }), 500