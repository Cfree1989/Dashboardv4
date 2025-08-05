# Queue Service for 3D Print Management System
"""
Service for managing background task queues using RQ (Redis Queue).
Handles email notifications, file processing, and other async tasks.
"""

import redis
from rq import Queue
from flask import current_app
from typing import Optional, Dict, Any
from app.tasks.email_tasks import (
    send_submission_confirmation_task,
    send_approval_notification_task,
    send_rejection_notification_task,
    send_completion_notification_task,
    send_reminder_notification_task
)


class QueueService:
    """Service for managing background task queues."""
    
    def __init__(self):
        self._redis_conn = None
        self._email_queue = None
        self._default_queue = None
    
    def _get_redis_connection(self):
        """Get Redis connection instance."""
        if not self._redis_conn:
            redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self._redis_conn = redis.from_url(redis_url)
        return self._redis_conn
    
    def _get_email_queue(self):
        """Get email processing queue."""
        if not self._email_queue:
            redis_conn = self._get_redis_connection()
            self._email_queue = Queue('email', connection=redis_conn)
        return self._email_queue
    
    def _get_default_queue(self):
        """Get default processing queue."""
        if not self._default_queue:
            redis_conn = self._get_redis_connection()
            self._default_queue = Queue('default', connection=redis_conn)
        return self._default_queue
    
    def queue_submission_confirmation(self, job_id: str, delay_seconds: int = 0) -> Optional[str]:
        """
        Queue submission confirmation email.
        
        Args:
            job_id: ID of job to send confirmation for
            delay_seconds: Delay before processing (default: immediate)
            
        Returns:
            RQ job ID if queued successfully, None if failed
        """
        try:
            email_queue = self._get_email_queue()
            
            if delay_seconds > 0:
                rq_job = email_queue.enqueue_in(
                    delay_seconds,
                    send_submission_confirmation_task,
                    job_id
                )
            else:
                rq_job = email_queue.enqueue(
                    send_submission_confirmation_task,
                    job_id
                )
            
            current_app.logger.info(f"Queued submission confirmation for job {job_id} - RQ Job: {rq_job.id}")
            return rq_job.id
            
        except Exception as e:
            current_app.logger.error(f"Failed to queue submission confirmation for job {job_id}: {str(e)}")
            return None
    
    def queue_approval_notification(self, job_id: str, staff_name: str, delay_seconds: int = 0) -> Optional[str]:
        """
        Queue approval notification email.
        
        Args:
            job_id: ID of approved job
            staff_name: Name of approving staff member
            delay_seconds: Delay before processing (default: immediate)
            
        Returns:
            RQ job ID if queued successfully, None if failed
        """
        try:
            email_queue = self._get_email_queue()
            
            if delay_seconds > 0:
                rq_job = email_queue.enqueue_in(
                    delay_seconds,
                    send_approval_notification_task,
                    job_id,
                    staff_name
                )
            else:
                rq_job = email_queue.enqueue(
                    send_approval_notification_task,
                    job_id,
                    staff_name
                )
            
            current_app.logger.info(f"Queued approval notification for job {job_id} - RQ Job: {rq_job.id}")
            return rq_job.id
            
        except Exception as e:
            current_app.logger.error(f"Failed to queue approval notification for job {job_id}: {str(e)}")
            return None
    
    def queue_rejection_notification(self, job_id: str, staff_name: str, reason: str, delay_seconds: int = 0) -> Optional[str]:
        """
        Queue rejection notification email.
        
        Args:
            job_id: ID of rejected job
            staff_name: Name of rejecting staff member
            reason: Rejection reason
            delay_seconds: Delay before processing (default: immediate)
            
        Returns:
            RQ job ID if queued successfully, None if failed
        """
        try:
            email_queue = self._get_email_queue()
            
            if delay_seconds > 0:
                rq_job = email_queue.enqueue_in(
                    delay_seconds,
                    send_rejection_notification_task,
                    job_id,
                    staff_name,
                    reason
                )
            else:
                rq_job = email_queue.enqueue(
                    send_rejection_notification_task,
                    job_id,
                    staff_name,
                    reason
                )
            
            current_app.logger.info(f"Queued rejection notification for job {job_id} - RQ Job: {rq_job.id}")
            return rq_job.id
            
        except Exception as e:
            current_app.logger.error(f"Failed to queue rejection notification for job {job_id}: {str(e)}")
            return None
    
    def queue_completion_notification(self, job_id: str, staff_name: str, delay_seconds: int = 0) -> Optional[str]:
        """
        Queue completion notification email.
        
        Args:
            job_id: ID of completed job
            staff_name: Name of staff member marking complete
            delay_seconds: Delay before processing (default: immediate)
            
        Returns:
            RQ job ID if queued successfully, None if failed
        """
        try:
            email_queue = self._get_email_queue()
            
            if delay_seconds > 0:
                rq_job = email_queue.enqueue_in(
                    delay_seconds,
                    send_completion_notification_task,
                    job_id,
                    staff_name
                )
            else:
                rq_job = email_queue.enqueue(
                    send_completion_notification_task,
                    job_id,
                    staff_name
                )
            
            current_app.logger.info(f"Queued completion notification for job {job_id} - RQ Job: {rq_job.id}")
            return rq_job.id
            
        except Exception as e:
            current_app.logger.error(f"Failed to queue completion notification for job {job_id}: {str(e)}")
            return None
    
    def queue_reminder_notification(self, job_id: str, reminder_type: str, delay_seconds: int = 0) -> Optional[str]:
        """
        Queue reminder notification email.
        
        Args:
            job_id: ID of job for reminder
            reminder_type: Type of reminder ('confirmation', 'pickup')
            delay_seconds: Delay before processing (default: immediate)
            
        Returns:
            RQ job ID if queued successfully, None if failed
        """
        try:
            email_queue = self._get_email_queue()
            
            if delay_seconds > 0:
                rq_job = email_queue.enqueue_in(
                    delay_seconds,
                    send_reminder_notification_task,
                    job_id,
                    reminder_type
                )
            else:
                rq_job = email_queue.enqueue(
                    send_reminder_notification_task,
                    job_id,
                    reminder_type
                )
            
            current_app.logger.info(f"Queued {reminder_type} reminder for job {job_id} - RQ Job: {rq_job.id}")
            return rq_job.id
            
        except Exception as e:
            current_app.logger.error(f"Failed to queue {reminder_type} reminder for job {job_id}: {str(e)}")
            return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get status of all queues.
        
        Returns:
            Dictionary with queue statistics
        """
        try:
            email_queue = self._get_email_queue()
            default_queue = self._get_default_queue()
            
            return {
                'email_queue': {
                    'name': 'email',
                    'length': len(email_queue),
                    'started_jobs': email_queue.started_job_registry.count,
                    'finished_jobs': email_queue.finished_job_registry.count,
                    'failed_jobs': email_queue.failed_job_registry.count,
                    'scheduled_jobs': email_queue.scheduled_job_registry.count
                },
                'default_queue': {
                    'name': 'default',
                    'length': len(default_queue),
                    'started_jobs': default_queue.started_job_registry.count,
                    'finished_jobs': default_queue.finished_job_registry.count,
                    'failed_jobs': default_queue.failed_job_registry.count,
                    'scheduled_jobs': default_queue.scheduled_job_registry.count
                },
                'redis_connected': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Failed to get queue status: {str(e)}")
            return {
                'error': str(e),
                'redis_connected': False
            }
    
    def clear_failed_jobs(self, queue_name: str = 'email') -> int:
        """
        Clear failed jobs from specified queue.
        
        Args:
            queue_name: Name of queue to clear ('email' or 'default')
            
        Returns:
            Number of jobs cleared
        """
        try:
            if queue_name == 'email':
                queue = self._get_email_queue()
            else:
                queue = self._get_default_queue()
            
            failed_registry = queue.failed_job_registry
            failed_count = failed_registry.count
            failed_registry.requeue_job_ids(*failed_registry.get_job_ids())
            
            current_app.logger.info(f"Cleared {failed_count} failed jobs from {queue_name} queue")
            return failed_count
            
        except Exception as e:
            current_app.logger.error(f"Failed to clear failed jobs from {queue_name}: {str(e)}")
            return 0
    
    def retry_failed_jobs(self, queue_name: str = 'email') -> int:
        """
        Retry failed jobs from specified queue.
        
        Args:
            queue_name: Name of queue to retry jobs from ('email' or 'default')
            
        Returns:
            Number of jobs retried
        """
        try:
            if queue_name == 'email':
                queue = self._get_email_queue()
            else:
                queue = self._get_default_queue()
            
            failed_registry = queue.failed_job_registry
            failed_job_ids = failed_registry.get_job_ids()
            failed_count = len(failed_job_ids)
            
            # Requeue failed jobs
            for job_id in failed_job_ids:
                failed_registry.requeue(job_id)
            
            current_app.logger.info(f"Retried {failed_count} failed jobs from {queue_name} queue")
            return failed_count
            
        except Exception as e:
            current_app.logger.error(f"Failed to retry failed jobs from {queue_name}: {str(e)}")
            return 0


# Singleton instance
queue_service = QueueService()