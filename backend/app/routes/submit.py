# Student Submission Routes - 3D Print Management System
"""
Student job submission and confirmation endpoints.
Handles file uploads, job creation, and student confirmation workflow.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.database import db
from app.models.job import Job
from app.models.event import Event
from app.services.file_service import file_service, FileValidationError, FileOperationError
from app.services.queue_service import queue_service
import uuid
from datetime import datetime

bp = Blueprint('submit', __name__)

# Rate limiting for submission endpoints
limiter = Limiter(key_func=get_remote_address)


@bp.route('/submit', methods=['POST'])
@limiter.limit("3 per hour")  # Prevent abuse
def submit_job():
    """
    Student job submission endpoint.
    
    Handles file upload, validation, and job creation.
    Accepts multipart/form-data with file and job details.
    """
    try:
        # Validate content type
        if not request.files:
            return jsonify({
                'error': 'no_file_uploaded',
                'message': 'No file was uploaded'
            }), 400
        
        # Get uploaded file
        uploaded_file = request.files.get('file')
        if not uploaded_file:
            return jsonify({
                'error': 'missing_file',
                'message': 'File field is required'
            }), 400
        
        # Get form data
        form_data = request.form
        required_fields = [
            'student_name', 'student_email', 'discipline', 'class_number',
            'printer', 'color', 'material', 'acknowledged_minimum_charge'
        ]
        
        # Validate required fields
        for field in required_fields:
            if field not in form_data or not form_data[field].strip():
                return jsonify({
                    'error': 'missing_required_field',
                    'message': f'Field {field} is required'
                }), 400
        
        # Validate email format
        student_email = form_data['student_email'].strip().lower()
        if '@' not in student_email or '.' not in student_email:
            return jsonify({
                'error': 'invalid_email',
                'message': 'Please provide a valid email address'
            }), 400
        
        # Validate minimum charge acknowledgment
        if form_data['acknowledged_minimum_charge'].lower() not in ['true', 'yes', '1']:
            return jsonify({
                'error': 'minimum_charge_not_acknowledged',
                'message': 'You must acknowledge the minimum charge requirement'
            }), 400
        
        # Validate file
        try:
            file_info = file_service.validate_file(uploaded_file)
        except FileValidationError as e:
            return jsonify({
                'error': 'file_validation_failed',
                'message': str(e)
            }), 400
        
        # Calculate file hash for duplicate detection
        file_hash = file_service.calculate_file_hash(uploaded_file)
        
        # Check for duplicate submissions
        existing_duplicates = Job.find_active_duplicates(file_hash, student_email)
        if existing_duplicates:
            return jsonify({
                'error': 'duplicate_submission',
                'message': 'An identical active job has already been submitted.',
                'existing_job_id': existing_duplicates[0].id
            }), 409
        
        # Create new job record
        job_id = str(uuid.uuid4())
        
        # Generate display name
        display_name = file_service.generate_display_name(
            student_name=form_data['student_name'],
            print_method=form_data['material'],
            color=form_data['color'],
            job_id=job_id,
            original_filename=file_info['original_filename']
        )
        
        # Create job object
        job = Job(
            id=job_id,
            student_name=form_data['student_name'].strip(),
            student_email=student_email,
            discipline=form_data['discipline'],
            class_number=form_data['class_number'].strip(),
            original_filename=file_info['original_filename'],
            display_name=display_name,
            file_path='',  # Will be set after file save
            metadata_path='',  # Will be set after file save
            file_hash=file_hash,
            status=Job.STATUS_UPLOADED,
            printer=form_data['printer'],
            color=form_data['color'],
            material=form_data['material'],
            acknowledged_minimum_charge=True
        )
        
        # Save to database first to get timestamps
        db.session.add(job)
        db.session.flush()  # Get job with timestamps but don't commit yet
        
        # Save uploaded file and create metadata
        try:
            file_path, metadata_path = file_service.save_uploaded_file(uploaded_file, job.to_dict())
            job.file_path = file_path
            job.metadata_path = metadata_path
        except FileOperationError as e:
            db.session.rollback()
            return jsonify({
                'error': 'file_save_failed',
                'message': f'Failed to save uploaded file: {str(e)}'
            }), 500
        
        # Create submission event
        submission_event = Event(
            job_id=job.id,
            event_type=Event.EVENT_JOB_CREATED,
            triggered_by='student',  # Student submission
            workstation_id='student_portal',
            details={
                'file_info': file_info,
                'file_hash': file_hash,
                'submission_ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
        )
        db.session.add(submission_event)
        
        # Commit transaction
        db.session.commit()
        
        # Queue submission confirmation email
        try:
            rq_job_id = queue_service.queue_submission_confirmation(job.id)
            if rq_job_id:
                current_app.logger.info(f"Queued submission confirmation for job {job.id} - RQ Job: {rq_job_id}")
            else:
                current_app.logger.warning(f"Failed to queue submission confirmation for job {job.id}")
        except Exception as e:
            current_app.logger.error(f"Error queuing submission confirmation for job {job.id}: {str(e)}")
            # Don't fail the submission if email queueing fails
        
        current_app.logger.info(f"Job submitted successfully: {job.id} by {student_email}")
        
        # Return success response
        return jsonify({
            'message': 'Job submitted successfully',
            'job': {
                'id': job.id,
                'display_name': job.display_name,
                'status': job.status,
                'created_at': job.created_at.isoformat(),
                'estimated_cost': f"${job.calculate_cost():.2f}" if job.calculate_cost() else "TBD"
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in job submission: {str(e)}")
        return jsonify({
            'error': 'submission_failed',
            'message': 'Job submission failed due to server error'
        }), 500


@bp.route('/confirm/<token>', methods=['POST'])
def confirm_job(token):
    """
    Student job confirmation endpoint.
    
    Confirms a job using the secure token sent via email.
    Transitions job from PENDING to READYTOPRINT status.
    """
    try:
        # Find job by confirmation token
        job = Job.find_by_token(token)
        if not job:
            return jsonify({
                'error': 'invalid_token',
                'message': 'Invalid or expired confirmation token'
            }), 404
        
        # Check if token is still valid
        if not job.is_token_valid():
            return jsonify({
                'error': 'token_expired',
                'message': 'Confirmation link has expired',
                'job_id': job.id
            }), 410
        
        # Check if job is in correct status for confirmation
        if job.status != Job.STATUS_PENDING:
            return jsonify({
                'error': 'invalid_job_status',
                'message': f'Job cannot be confirmed in {job.status} status'
            }), 400
        
        # Check if already confirmed
        if job.student_confirmed:
            return jsonify({
                'error': 'already_confirmed',
                'message': 'Job has already been confirmed',
                'job': job.to_dict()
            }), 409
        
        # Confirm the job
        job.student_confirmed = True
        job.student_confirmed_at = datetime.utcnow()
        job.status = Job.STATUS_READYTOPRINT
        
        # Move files to ReadyToPrint directory
        try:
            new_file_path, new_metadata_path = file_service.move_job_files(
                old_status=Job.STATUS_PENDING,
                new_status=Job.STATUS_READYTOPRINT,
                job_data=job.to_dict()
            )
            job.file_path = new_file_path
            job.metadata_path = new_metadata_path
        except FileOperationError as e:
            db.session.rollback()
            current_app.logger.error(f"Error moving files for job {job.id}: {str(e)}")
            return jsonify({
                'error': 'file_move_failed',
                'message': 'Failed to update job files'
            }), 500
        
        # Create confirmation event
        confirmation_event = Event(
            job_id=job.id,
            event_type='JobConfirmed',
            triggered_by=None,  # Student confirmation
            workstation_id='student_portal',
            details={
                'confirmed_via': 'email_token',
                'confirmation_token': token,
                'confirmation_ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
        )
        db.session.add(confirmation_event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job confirmed successfully: {job.id}")
        
        return jsonify({
            'message': 'Job confirmed successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in job confirmation: {str(e)}")
        return jsonify({
            'error': 'confirmation_failed',
            'message': 'Job confirmation failed due to server error'
        }), 500


@bp.route('/resend-confirmation', methods=['POST'])
@limiter.limit("1 per hour")  # Rate limit resend requests
def resend_confirmation():
    """
    Resend confirmation email for a job.
    
    Public endpoint for students to request new confirmation email
    if their original link expired.
    """
    try:
        data = request.get_json()
        if not data or 'job_id' not in data:
            return jsonify({
                'error': 'missing_job_id',
                'message': 'job_id is required'
            }), 400
        
        job = Job.query.get(data['job_id'])
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': 'Job not found'
            }), 404
        
        # Validate job can receive new confirmation
        if job.status != Job.STATUS_PENDING:
            return jsonify({
                'error': 'invalid_job_status',
                'message': 'Job is not awaiting confirmation'
            }), 400
        
        if job.student_confirmed:
            return jsonify({
                'error': 'already_confirmed',
                'message': 'Job has already been confirmed'
            }), 409
        
        # Generate new confirmation token
        new_token = job.generate_confirmation_token()
        job.confirmation_last_sent_at = datetime.utcnow()
        
        # Create resend event
        resend_event = Event(
            job_id=job.id,
            event_type='ConfirmationResent',
            triggered_by=None,  # Student request
            workstation_id='student_portal',
            details={
                'new_token_generated': True,
                'request_ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown')
            }
        )
        db.session.add(resend_event)
        
        db.session.commit()
        
        current_app.logger.info(f"Confirmation email resent for job: {job.id}")
        
        # TODO: Queue email sending task here when email service is implemented
        
        return jsonify({
            'message': 'New confirmation email has been sent',
            'job_id': job.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error resending confirmation: {str(e)}")
        return jsonify({
            'error': 'resend_failed',
            'message': 'Failed to resend confirmation email'
        }), 500