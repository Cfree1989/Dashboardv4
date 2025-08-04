# Email Service for 3D Print Management System
"""
Email service handling all notification emails for the 3D print workflow.
Includes template management, token generation, and background task integration.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from flask import current_app, render_template_string
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from app import mail
from app.models.job import Job
from app.models.event import Event
from app.database import db


class EmailService:
    """Service for handling all email notifications in the 3D print system."""
    
    def __init__(self):
        self.serializer = None
        self._templates = {}
        self._load_templates()
    
    def _get_serializer(self):
        """Get URLSafeTimedSerializer for token generation."""
        if not self.serializer:
            self.serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return self.serializer
    
    def _load_templates(self):
        """Load email templates."""
        self._templates = {
            'submission_confirmation': self._get_submission_template(),
            'approval_notification': self._get_approval_template(),
            'rejection_notification': self._get_rejection_template(),
            'completion_notification': self._get_completion_template(),
            'reminder_notification': self._get_reminder_template()
        }
    
    def generate_confirmation_token(self, job_id: str, expires_hours: int = 168) -> str:
        """
        Generate secure confirmation token for job confirmation.
        
        Args:
            job_id: Job ID to encode in token
            expires_hours: Token expiration in hours (default 7 days)
            
        Returns:
            Secure token string
        """
        serializer = self._get_serializer()
        return serializer.dumps({'job_id': job_id, 'action': 'confirm'})
    
    def verify_confirmation_token(self, token: str, max_age: int = 604800) -> Optional[str]:
        """
        Verify confirmation token and extract job ID.
        
        Args:
            token: Token to verify
            max_age: Maximum age in seconds (default 7 days)
            
        Returns:
            Job ID if valid, None if invalid/expired
        """
        try:
            serializer = self._get_serializer()
            data = serializer.loads(token, max_age=max_age)
            if data.get('action') == 'confirm':
                return data.get('job_id')
        except (SignatureExpired, BadSignature):
            pass
        return None
    
    def send_submission_confirmation(self, job: Job) -> bool:
        """
        Send confirmation email after job submission.
        
        Args:
            job: Job instance
            
        Returns:
            True if email sent successfully
        """
        try:
            token = self.generate_confirmation_token(job.id)
            confirmation_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/confirm/{token}"
            
            template_data = {
                'student_name': job.student_name,
                'job_id': job.id,
                'filename': job.original_filename,
                'material': job.material_type,
                'color': job.color,
                'estimated_cost': f"${job.estimated_cost:.2f}",
                'estimated_weight': f"{job.estimated_weight_grams}g",
                'confirmation_url': confirmation_url,
                'submission_date': job.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'contact_email': current_app.config.get('CONTACT_EMAIL', 'support@3dprinting.edu')
            }
            
            subject = f"3D Print Submission Confirmation - {job.original_filename}"
            html_body = self._templates['submission_confirmation'].format(**template_data)
            
            return self._send_email(
                to=job.student_email,
                subject=subject,
                html_body=html_body,
                job_id=job.id,
                event_type='EMAIL_CONFIRMATION_SENT'
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send submission confirmation for job {job.id}: {str(e)}")
            return False
    
    def send_approval_notification(self, job: Job, staff_name: str) -> bool:
        """
        Send approval notification to student.
        
        Args:
            job: Job instance
            staff_name: Name of approving staff member
            
        Returns:
            True if email sent successfully
        """
        try:
            template_data = {
                'student_name': job.student_name,
                'job_id': job.id,
                'filename': job.original_filename,
                'material': job.material_type,
                'color': job.color,
                'final_cost': f"${job.final_cost:.2f}" if job.final_cost else f"${job.estimated_cost:.2f}",
                'final_weight': f"{job.final_weight_grams}g" if job.final_weight_grams else f"{job.estimated_weight_grams}g",
                'staff_name': staff_name,
                'approval_date': datetime.utcnow().strftime('%B %d, %Y at %I:%M %p'),
                'estimated_completion': (datetime.utcnow() + timedelta(days=2)).strftime('%B %d, %Y'),
                'pickup_instructions': "Please bring your student ID and be prepared to pay the final cost.",
                'contact_email': current_app.config.get('CONTACT_EMAIL', 'support@3dprinting.edu')
            }
            
            subject = f"3D Print Approved - {job.original_filename}"
            html_body = self._templates['approval_notification'].format(**template_data)
            
            return self._send_email(
                to=job.student_email,
                subject=subject,
                html_body=html_body,
                job_id=job.id,
                event_type='EMAIL_APPROVAL_SENT'
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send approval notification for job {job.id}: {str(e)}")
            return False
    
    def send_rejection_notification(self, job: Job, staff_name: str, reason: str) -> bool:
        """
        Send rejection notification to student.
        
        Args:
            job: Job instance
            staff_name: Name of rejecting staff member
            reason: Rejection reason
            
        Returns:
            True if email sent successfully
        """
        try:
            template_data = {
                'student_name': job.student_name,
                'job_id': job.id,
                'filename': job.original_filename,
                'staff_name': staff_name,
                'rejection_reason': reason,
                'rejection_date': datetime.utcnow().strftime('%B %d, %Y at %I:%M %p'),
                'resubmit_url': f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/submit",
                'contact_email': current_app.config.get('CONTACT_EMAIL', 'support@3dprinting.edu')
            }
            
            subject = f"3D Print Submission Update - {job.original_filename}"
            html_body = self._templates['rejection_notification'].format(**template_data)
            
            return self._send_email(
                to=job.student_email,
                subject=subject,
                html_body=html_body,
                job_id=job.id,
                event_type='EMAIL_REJECTION_SENT'
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send rejection notification for job {job.id}: {str(e)}")
            return False
    
    def send_completion_notification(self, job: Job, staff_name: str) -> bool:
        """
        Send completion notification to student.
        
        Args:
            job: Job instance
            staff_name: Name of staff member marking complete
            
        Returns:
            True if email sent successfully
        """
        try:
            payment_info = "Tiger-Cash terminal available at pickup location."
            if job.final_cost and job.final_cost < 3.00:
                payment_info = f"Final cost: ${job.final_cost:.2f} (minimum charge ${3.00:.2f})"
            
            template_data = {
                'student_name': job.student_name,
                'job_id': job.id,
                'filename': job.original_filename,
                'material': job.material_type,
                'color': job.color,
                'final_cost': f"${job.final_cost:.2f}" if job.final_cost else f"${job.estimated_cost:.2f}",
                'final_weight': f"{job.final_weight_grams}g" if job.final_weight_grams else "Weight not recorded",
                'staff_name': staff_name,
                'completion_date': datetime.utcnow().strftime('%B %d, %Y at %I:%M %p'),
                'pickup_hours': "Monday-Friday 9AM-5PM, Saturday 10AM-3PM",
                'pickup_location': "3D Printing Lab - Room 234, Engineering Building",
                'payment_info': payment_info,
                'contact_email': current_app.config.get('CONTACT_EMAIL', 'support@3dprinting.edu')
            }
            
            subject = f"3D Print Ready for Pickup - {job.original_filename}"
            html_body = self._templates['completion_notification'].format(**template_data)
            
            return self._send_email(
                to=job.student_email,
                subject=subject,
                html_body=html_body,
                job_id=job.id,
                event_type='EMAIL_COMPLETION_SENT'
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send completion notification for job {job.id}: {str(e)}")
            return False
    
    def send_reminder_notification(self, job: Job, reminder_type: str) -> bool:
        """
        Send reminder notification to student.
        
        Args:
            job: Job instance
            reminder_type: Type of reminder ('confirmation', 'pickup')
            
        Returns:
            True if email sent successfully
        """
        try:
            if reminder_type == 'confirmation':
                days_since = (datetime.utcnow() - job.created_at).days
                token = self.generate_confirmation_token(job.id)
                confirmation_url = f"{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/confirm/{token}"
                action_required = f'Please <a href="{confirmation_url}">confirm your job</a> to proceed with printing.'
                subject = f"Reminder: Confirm Your 3D Print - {job.original_filename}"
            else:  # pickup reminder
                days_since = (datetime.utcnow() - job.completed_at).days if job.completed_at else 0
                action_required = "Please pick up your completed 3D print during lab hours."
                subject = f"Reminder: Pick Up Your 3D Print - {job.original_filename}"
            
            template_data = {
                'student_name': job.student_name,
                'job_id': job.id,
                'filename': job.original_filename,
                'days_since': days_since,
                'action_required': action_required,
                'pickup_hours': "Monday-Friday 9AM-5PM, Saturday 10AM-3PM",
                'pickup_location': "3D Printing Lab - Room 234, Engineering Building",
                'contact_email': current_app.config.get('CONTACT_EMAIL', 'support@3dprinting.edu')
            }
            
            html_body = self._templates['reminder_notification'].format(**template_data)
            
            return self._send_email(
                to=job.student_email,
                subject=subject,
                html_body=html_body,
                job_id=job.id,
                event_type='EMAIL_REMINDER_SENT'
            )
        except Exception as e:
            current_app.logger.error(f"Failed to send reminder notification for job {job.id}: {str(e)}")
            return False
    
    def _send_email(self, to: str, subject: str, html_body: str, job_id: str = None, event_type: str = 'EMAIL_SENT') -> bool:
        """
        Send email and log the event.
        
        Args:
            to: Recipient email
            subject: Email subject
            html_body: HTML email body
            job_id: Optional job ID for event logging
            event_type: Event type for logging
            
        Returns:
            True if email sent successfully
        """
        try:
            # Create message
            msg = Message(
                subject=subject,
                recipients=[to],
                html=html_body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            # Send email
            mail.send(msg)
            
            # Log event
            if job_id:
                event = Event(
                    job_id=job_id,
                    event_type=event_type,
                    description=f"Email sent to {to}: {subject}",
                    staff_name="SYSTEM",
                    workstation="EMAIL_SERVICE"
                )
                db.session.add(event)
                db.session.commit()
            
            current_app.logger.info(f"Email sent successfully to {to}: {subject}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Failed to send email to {to}: {str(e)}")
            if job_id:
                try:
                    event = Event(
                        job_id=job_id,
                        event_type='EMAIL_FAILED',
                        description=f"Failed to send email to {to}: {str(e)}",
                        staff_name="SYSTEM",
                        workstation="EMAIL_SERVICE"
                    )
                    db.session.add(event)
                    db.session.commit()
                except Exception:
                    pass  # Don't fail if we can't log the failure
            return False
    
    def _get_submission_template(self) -> str:
        """Get submission confirmation email template."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Print Submission Confirmation</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2563eb; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .job-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb; }}
        .confirmation-button {{ display: inline-block; background-color: #16a34a; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
        .warning {{ background-color: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>3D Print Submission Received</h1>
    </div>
    <div class="content">
        <p>Hello {student_name},</p>
        
        <p>Thank you for submitting your 3D print job! We've received your file and it's now in our review queue.</p>
        
        <div class="job-details">
            <h3>Job Details</h3>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Job ID:</strong> {job_id}</p>
            <p><strong>Material:</strong> {material}</p>
            <p><strong>Color:</strong> {color}</p>
            <p><strong>Estimated Weight:</strong> {estimated_weight}</p>
            <p><strong>Estimated Cost:</strong> {estimated_cost}</p>
            <p><strong>Submitted:</strong> {submission_date}</p>
        </div>
        
        <div class="warning">
            <h4>⚠️ Confirmation Required</h4>
            <p>Your job is pending review by our staff. Once approved, you'll receive an email with the final cost and a confirmation link. <strong>You must confirm your job within 7 days</strong> or it will be automatically cancelled.</p>
        </div>
        
        <h3>Next Steps</h3>
        <ol>
            <li>Our staff will review your file for printability and safety</li>
            <li>If approved, you'll receive an email with final cost and confirmation link</li>
            <li>Click the confirmation link to authorize the final cost</li>
            <li>Your job will be queued for printing</li>
            <li>You'll be notified when your print is ready for pickup</li>
        </ol>
        
        <p>Questions? Contact us at <a href="mailto:{contact_email}">{contact_email}</a></p>
        
        <div class="footer">
            <p>3D Printing Lab - Engineering Department<br>
            This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_approval_template(self) -> str:
        """Get approval notification email template."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Print Approved</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #16a34a; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .job-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #16a34a; }}
        .success {{ background-color: #dcfce7; padding: 15px; border-radius: 6px; border-left: 4px solid #16a34a; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>✅ Your 3D Print Has Been Approved!</h1>
    </div>
    <div class="content">
        <p>Hello {student_name},</p>
        
        <p>Great news! Your 3D print job has been reviewed and approved by our staff.</p>
        
        <div class="job-details">
            <h3>Approved Job Details</h3>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Job ID:</strong> {job_id}</p>
            <p><strong>Material:</strong> {material}</p>
            <p><strong>Color:</strong> {color}</p>
            <p><strong>Final Weight:</strong> {final_weight}</p>
            <p><strong>Final Cost:</strong> {final_cost}</p>
            <p><strong>Approved by:</strong> {staff_name}</p>
            <p><strong>Approval Date:</strong> {approval_date}</p>
        </div>
        
        <div class="success">
            <h4>🎉 Your job is now queued for printing!</h4>
            <p>Estimated completion: <strong>{estimated_completion}</strong></p>
            <p>You'll receive another email when your print is ready for pickup.</p>
        </div>
        
        <h3>What's Next?</h3>
        <ol>
            <li>Your job is now in the print queue</li>
            <li>We'll email you when printing is complete</li>
            <li>Bring your student ID and payment for pickup</li>
        </ol>
        
        <p><strong>Pickup Instructions:</strong> {pickup_instructions}</p>
        
        <p>Questions? Contact us at <a href="mailto:{contact_email}">{contact_email}</a></p>
        
        <div class="footer">
            <p>3D Printing Lab - Engineering Department<br>
            This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_rejection_template(self) -> str:
        """Get rejection notification email template."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Print Submission Update</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #dc2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .job-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626; }}
        .rejection-reason {{ background-color: #fee2e2; padding: 15px; border-radius: 6px; border-left: 4px solid #dc2626; margin: 20px 0; }}
        .resubmit-button {{ display: inline-block; background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>3D Print Submission Update</h1>
    </div>
    <div class="content">
        <p>Hello {student_name},</p>
        
        <p>Thank you for your 3D print submission. After review, we're unable to proceed with your current job.</p>
        
        <div class="job-details">
            <h3>Submission Details</h3>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Job ID:</strong> {job_id}</p>
            <p><strong>Reviewed by:</strong> {staff_name}</p>
            <p><strong>Review Date:</strong> {rejection_date}</p>
        </div>
        
        <div class="rejection-reason">
            <h4>Reason for Rejection</h4>
            <p>{rejection_reason}</p>
        </div>
        
        <h3>What You Can Do</h3>
        <ol>
            <li>Review the rejection feedback above</li>
            <li>Make necessary modifications to your file</li>
            <li>Submit a new job with the corrected file</li>
            <li>Contact us if you need clarification</li>
        </ol>
        
        <div style="text-align: center;">
            <a href="{resubmit_url}" class="resubmit-button">Submit New Job</a>
        </div>
        
        <p>Need help? Contact us at <a href="mailto:{contact_email}">{contact_email}</a> and reference job ID {job_id}.</p>
        
        <div class="footer">
            <p>3D Printing Lab - Engineering Department<br>
            This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_completion_template(self) -> str:
        """Get completion notification email template."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Print Ready for Pickup</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #7c3aed; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .job-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #7c3aed; }}
        .pickup-info {{ background-color: #ede9fe; padding: 15px; border-radius: 6px; border-left: 4px solid #7c3aed; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Your 3D Print is Ready!</h1>
    </div>
    <div class="content">
        <p>Hello {student_name},</p>
        
        <p>Excellent news! Your 3D print has been completed and is ready for pickup.</p>
        
        <div class="job-details">
            <h3>Completed Job Details</h3>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Job ID:</strong> {job_id}</p>
            <p><strong>Material:</strong> {material}</p>
            <p><strong>Color:</strong> {color}</p>
            <p><strong>Final Weight:</strong> {final_weight}</p>
            <p><strong>Final Cost:</strong> {final_cost}</p>
            <p><strong>Completed by:</strong> {staff_name}</p>
            <p><strong>Completion Date:</strong> {completion_date}</p>
        </div>
        
        <div class="pickup-info">
            <h4>📍 Pickup Information</h4>
            <p><strong>Location:</strong> {pickup_location}</p>
            <p><strong>Hours:</strong> {pickup_hours}</p>
            <p><strong>Payment:</strong> {payment_info}</p>
            <p><strong>Bring:</strong> Student ID for verification</p>
        </div>
        
        <h3>Important Notes</h3>
        <ul>
            <li>Please pick up your print within <strong>30 days</strong></li>
            <li>Unclaimed prints after 30 days may be disposed of</li>
            <li>Payment is required at pickup</li>
            <li>Handle your print carefully - some materials may be fragile</li>
        </ul>
        
        <p>Questions? Contact us at <a href="mailto:{contact_email}">{contact_email}</a> and reference job ID {job_id}.</p>
        
        <div class="footer">
            <p>3D Printing Lab - Engineering Department<br>
            This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_reminder_template(self) -> str:
        """Get reminder notification email template."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Print Reminder</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #f59e0b; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
        .job-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
        .reminder {{ background-color: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 20px 0; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 14px; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>⏰ 3D Print Reminder</h1>
    </div>
    <div class="content">
        <p>Hello {student_name},</p>
        
        <p>This is a friendly reminder about your 3D print job submitted {days_since} days ago.</p>
        
        <div class="job-details">
            <h3>Job Details</h3>
            <p><strong>File:</strong> {filename}</p>
            <p><strong>Job ID:</strong> {job_id}</p>
        </div>
        
        <div class="reminder">
            <h4>⚠️ Action Required</h4>
            <p>{action_required}</p>
        </div>
        
        <p><strong>Pickup Location:</strong> {pickup_location}<br>
        <strong>Hours:</strong> {pickup_hours}</p>
        
        <p>Questions? Contact us at <a href="mailto:{contact_email}">{contact_email}</a> and reference job ID {job_id}.</p>
        
        <div class="footer">
            <p>3D Printing Lab - Engineering Department<br>
            This is an automated message. Please do not reply to this email.</p>
        </div>
    </div>
</body>
</html>
        """


# Singleton instance
email_service = EmailService()