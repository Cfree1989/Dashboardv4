# Email Background Tasks for 3D Print Management System
"""
Background task functions for sending emails asynchronously using RQ.
These tasks are queued when email notifications need to be sent.
"""

import logging
from datetime import datetime
from flask import current_app
from rq import get_current_job
from app import create_app
from app.database import db
from app.models.job import Job
from app.models.event import Event
from app.services.email_service import email_service


def send_submission_confirmation_task(job_id: str):
    """
    Background task to send submission confirmation email.
    
    Args:
        job_id: ID of the job to send confirmation for
        
    Returns:
        dict: Task result with success status and details
    """
    # Create app context for background task
    app = create_app()
    
    with app.app_context():
        try:
            # Get current RQ job for logging
            rq_job = get_current_job()
            job_uuid = rq_job.id if rq_job else 'unknown'
            
            # Get job from database
            job = Job.query.get(job_id)
            if not job:
                error_msg = f"Job {job_id} not found for submission confirmation"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            # Send email
            success = email_service.send_submission_confirmation(job)
            
            if success:
                # Log success event
                event = Event(
                    job_id=job.id,
                    event_type='EMAIL_CONFIRMATION_QUEUED',
                    description=f'Submission confirmation email queued successfully (RQ Job: {job_uuid})',
                    staff_name='SYSTEM',
                    workstation='EMAIL_WORKER'
                )
                db.session.add(event)
                db.session.commit()
                
                result = {'success': True, 'job_id': job_id, 'email': job.student_email}
                current_app.logger.info(f"Submission confirmation sent for job {job_id}")
                return result
            else:
                error_msg = f"Failed to send submission confirmation for job {job_id}"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error in submission confirmation task for job {job_id}: {str(e)}"
            current_app.logger.error(error_msg)
            
            # Try to log error event
            try:
                if 'job' in locals() and job:
                    event = Event(
                        job_id=job.id,
                        event_type='EMAIL_TASK_FAILED',
                        description=f'Submission confirmation task failed: {str(e)}',
                        staff_name='SYSTEM',
                        workstation='EMAIL_WORKER'
                    )
                    db.session.add(event)
                    db.session.commit()
            except Exception:
                pass  # Don't fail if we can't log the error
            
            return {'success': False, 'error': error_msg}


def send_approval_notification_task(job_id: str, staff_name: str):
    """
    Background task to send approval notification email.
    
    Args:
        job_id: ID of the approved job
        staff_name: Name of approving staff member
        
    Returns:
        dict: Task result with success status and details
    """
    app = create_app()
    
    with app.app_context():
        try:
            rq_job = get_current_job()
            job_uuid = rq_job.id if rq_job else 'unknown'
            
            job = Job.query.get(job_id)
            if not job:
                error_msg = f"Job {job_id} not found for approval notification"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            success = email_service.send_approval_notification(job, staff_name)
            
            if success:
                event = Event(
                    job_id=job.id,
                    event_type='EMAIL_APPROVAL_QUEUED',
                    description=f'Approval notification email queued successfully (RQ Job: {job_uuid})',
                    staff_name=staff_name,
                    workstation='EMAIL_WORKER'
                )
                db.session.add(event)
                db.session.commit()
                
                result = {'success': True, 'job_id': job_id, 'email': job.student_email, 'staff_name': staff_name}
                current_app.logger.info(f"Approval notification sent for job {job_id}")
                return result
            else:
                error_msg = f"Failed to send approval notification for job {job_id}"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error in approval notification task for job {job_id}: {str(e)}"
            current_app.logger.error(error_msg)
            
            try:
                if 'job' in locals() and job:
                    event = Event(
                        job_id=job.id,
                        event_type='EMAIL_TASK_FAILED',
                        description=f'Approval notification task failed: {str(e)}',
                        staff_name=staff_name,
                        workstation='EMAIL_WORKER'
                    )
                    db.session.add(event)
                    db.session.commit()
            except Exception:
                pass
            
            return {'success': False, 'error': error_msg}


def send_rejection_notification_task(job_id: str, staff_name: str, reason: str):
    """
    Background task to send rejection notification email.
    
    Args:
        job_id: ID of the rejected job
        staff_name: Name of rejecting staff member
        reason: Rejection reason
        
    Returns:
        dict: Task result with success status and details
    """
    app = create_app()
    
    with app.app_context():
        try:
            rq_job = get_current_job()
            job_uuid = rq_job.id if rq_job else 'unknown'
            
            job = Job.query.get(job_id)
            if not job:
                error_msg = f"Job {job_id} not found for rejection notification"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            success = email_service.send_rejection_notification(job, staff_name, reason)
            
            if success:
                event = Event(
                    job_id=job.id,
                    event_type='EMAIL_REJECTION_QUEUED',
                    description=f'Rejection notification email queued successfully (RQ Job: {job_uuid})',
                    staff_name=staff_name,
                    workstation='EMAIL_WORKER'
                )
                db.session.add(event)
                db.session.commit()
                
                result = {'success': True, 'job_id': job_id, 'email': job.student_email, 'staff_name': staff_name}
                current_app.logger.info(f"Rejection notification sent for job {job_id}")
                return result
            else:
                error_msg = f"Failed to send rejection notification for job {job_id}"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error in rejection notification task for job {job_id}: {str(e)}"
            current_app.logger.error(error_msg)
            
            try:
                if 'job' in locals() and job:
                    event = Event(
                        job_id=job.id,
                        event_type='EMAIL_TASK_FAILED',
                        description=f'Rejection notification task failed: {str(e)}',
                        staff_name=staff_name,
                        workstation='EMAIL_WORKER'
                    )
                    db.session.add(event)
                    db.session.commit()
            except Exception:
                pass
            
            return {'success': False, 'error': error_msg}


def send_completion_notification_task(job_id: str, staff_name: str):
    """
    Background task to send completion notification email.
    
    Args:
        job_id: ID of the completed job
        staff_name: Name of staff member marking complete
        
    Returns:
        dict: Task result with success status and details
    """
    app = create_app()
    
    with app.app_context():
        try:
            rq_job = get_current_job()
            job_uuid = rq_job.id if rq_job else 'unknown'
            
            job = Job.query.get(job_id)
            if not job:
                error_msg = f"Job {job_id} not found for completion notification"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            success = email_service.send_completion_notification(job, staff_name)
            
            if success:
                event = Event(
                    job_id=job.id,
                    event_type='EMAIL_COMPLETION_QUEUED',
                    description=f'Completion notification email queued successfully (RQ Job: {job_uuid})',
                    staff_name=staff_name,
                    workstation='EMAIL_WORKER'
                )
                db.session.add(event)
                db.session.commit()
                
                result = {'success': True, 'job_id': job_id, 'email': job.student_email, 'staff_name': staff_name}
                current_app.logger.info(f"Completion notification sent for job {job_id}")
                return result
            else:
                error_msg = f"Failed to send completion notification for job {job_id}"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error in completion notification task for job {job_id}: {str(e)}"
            current_app.logger.error(error_msg)
            
            try:
                if 'job' in locals() and job:
                    event = Event(
                        job_id=job.id,
                        event_type='EMAIL_TASK_FAILED',
                        description=f'Completion notification task failed: {str(e)}',
                        staff_name=staff_name,
                        workstation='EMAIL_WORKER'
                    )
                    db.session.add(event)
                    db.session.commit()
            except Exception:
                pass
            
            return {'success': False, 'error': error_msg}


def send_reminder_notification_task(job_id: str, reminder_type: str):
    """
    Background task to send reminder notification email.
    
    Args:
        job_id: ID of the job for reminder
        reminder_type: Type of reminder ('confirmation', 'pickup')
        
    Returns:
        dict: Task result with success status and details
    """
    app = create_app()
    
    with app.app_context():
        try:
            rq_job = get_current_job()
            job_uuid = rq_job.id if rq_job else 'unknown'
            
            job = Job.query.get(job_id)
            if not job:
                error_msg = f"Job {job_id} not found for reminder notification"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
            
            success = email_service.send_reminder_notification(job, reminder_type)
            
            if success:
                event = Event(
                    job_id=job.id,
                    event_type='EMAIL_REMINDER_QUEUED',
                    description=f'{reminder_type.title()} reminder email queued successfully (RQ Job: {job_uuid})',
                    staff_name='SYSTEM',
                    workstation='EMAIL_WORKER'
                )
                db.session.add(event)
                db.session.commit()
                
                result = {'success': True, 'job_id': job_id, 'email': job.student_email, 'reminder_type': reminder_type}
                current_app.logger.info(f"{reminder_type.title()} reminder sent for job {job_id}")
                return result
            else:
                error_msg = f"Failed to send {reminder_type} reminder for job {job_id}"
                current_app.logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            error_msg = f"Error in {reminder_type} reminder task for job {job_id}: {str(e)}"
            current_app.logger.error(error_msg)
            
            try:
                if 'job' in locals() and job:
                    event = Event(
                        job_id=job.id,
                        event_type='EMAIL_TASK_FAILED',
                        description=f'{reminder_type.title()} reminder task failed: {str(e)}',
                        staff_name='SYSTEM',
                        workstation='EMAIL_WORKER'
                    )
                    db.session.add(event)
                    db.session.commit()
            except Exception:
                pass
            
            return {'success': False, 'error': error_msg}