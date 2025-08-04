# Event Model - 3D Print Management System
"""
Event model for immutable audit trail of all system actions.
Provides comprehensive logging with staff attribution and workstation tracking.
"""

from datetime import datetime
from app import db


class Event(db.Model):
    """
    Event model for immutable audit trail.
    
    Records all significant actions in the system with full context including
    staff attribution, workstation identification, and detailed action data.
    Events are append-only and never modified or deleted.
    """
    
    __tablename__ = 'event'
    
    # Primary identifier
    id = db.Column(db.Integer, primary_key=True)
    
    # Job association
    job_id = db.Column(db.String(36), db.ForeignKey('job.id'), nullable=False)
    
    # Event metadata
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    event_type = db.Column(db.String(50), nullable=False)
    
    # Attribution and context
    triggered_by = db.Column(db.String(100), nullable=False)  # Staff member name
    workstation_id = db.Column(db.String(100), nullable=True) # Physical computer ID
    
    # Event details (JSON for flexible data storage)
    details = db.Column(db.JSON, nullable=True)
    
    # Legacy field (deprecated - use triggered_by instead)
    user_name = db.Column(db.String(100), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_event_job_id', 'job_id'),
        db.Index('idx_event_timestamp', 'timestamp'),
        db.Index('idx_event_type', 'event_type'),
        db.Index('idx_event_triggered_by', 'triggered_by'),
    )
    
    def __repr__(self):
        return f'<Event {self.id}: {self.event_type} by {self.triggered_by}>'
    
    # Event Type Constants
    # Job Lifecycle Events
    EVENT_JOB_CREATED = 'JobCreated'
    EVENT_STAFF_APPROVED = 'StaffApproved'
    EVENT_STAFF_REJECTED = 'StaffRejected'
    EVENT_STUDENT_CONFIRMED = 'StudentConfirmed'
    EVENT_PRINTING_STARTED = 'PrintingStarted'
    EVENT_PRINTING_COMPLETED = 'PrintingCompleted'
    EVENT_PRINT_FAILED = 'PrintFailed'
    EVENT_JOB_PICKED_UP = 'JobPickedUp'
    EVENT_JOB_ARCHIVED = 'JobArchived'
    EVENT_JOB_DELETED = 'JobDeleted'
    
    # Status Changes
    EVENT_STATUS_CHANGED = 'StatusChanged'
    EVENT_STATUS_REVERTED = 'StatusReverted'
    
    # File Operations
    EVENT_FILE_MOVED = 'FileMoved'
    EVENT_FILE_UPDATED = 'FileUpdated'
    EVENT_FILE_DELETED = 'FileDeleted'
    
    # Communication Events
    EVENT_EMAIL_SENT = 'EmailSent'
    EVENT_EMAIL_FAILED = 'EmailFailed'
    EVENT_EMAIL_RESENT = 'EmailResent'
    
    # Staff Actions
    EVENT_JOB_REVIEWED = 'JobReviewed'
    EVENT_NOTES_UPDATED = 'NotesUpdated'
    EVENT_JOB_LOCKED = 'JobLocked'
    EVENT_JOB_UNLOCKED = 'JobUnlocked'
    
    # Admin Actions
    EVENT_ADMIN_ACTION = 'AdminAction'
    EVENT_ADMIN_OVERRIDE = 'AdminOverride'
    EVENT_SYSTEM_AUDIT = 'SystemAudit'
    
    # Payment Events
    EVENT_PAYMENT_PROCESSED = 'PaymentProcessed'
    EVENT_PAYMENT_REFUNDED = 'PaymentRefunded'
    
    VALID_EVENT_TYPES = [
        EVENT_JOB_CREATED, EVENT_STAFF_APPROVED, EVENT_STAFF_REJECTED,
        EVENT_STUDENT_CONFIRMED, EVENT_PRINTING_STARTED, EVENT_PRINTING_COMPLETED,
        EVENT_PRINT_FAILED, EVENT_JOB_PICKED_UP, EVENT_JOB_ARCHIVED, EVENT_JOB_DELETED,
        EVENT_STATUS_CHANGED, EVENT_STATUS_REVERTED, EVENT_FILE_MOVED, EVENT_FILE_UPDATED,
        EVENT_FILE_DELETED, EVENT_EMAIL_SENT, EVENT_EMAIL_FAILED, EVENT_EMAIL_RESENT,
        EVENT_JOB_REVIEWED, EVENT_NOTES_UPDATED, EVENT_JOB_LOCKED, EVENT_JOB_UNLOCKED,
        EVENT_ADMIN_ACTION, EVENT_ADMIN_OVERRIDE, EVENT_SYSTEM_AUDIT,
        EVENT_PAYMENT_PROCESSED, EVENT_PAYMENT_REFUNDED
    ]
    
    def __init__(self, job_id, event_type, triggered_by, workstation_id=None, details=None, **kwargs):
        """
        Initialize event with validation.
        
        Args:
            job_id (str): Job ID this event relates to
            event_type (str): Type of event (must be in VALID_EVENT_TYPES)
            triggered_by (str): Name of staff member who triggered the action
            workstation_id (str, optional): ID of workstation where action occurred
            details (dict, optional): Additional event-specific data
        """
        if event_type not in self.VALID_EVENT_TYPES:
            raise ValueError(f"Invalid event type: {event_type}")
        
        super().__init__(**kwargs)
        self.job_id = job_id
        self.event_type = event_type
        self.triggered_by = triggered_by
        self.workstation_id = workstation_id
        self.details = details or {}
    
    @property
    def age_hours(self):
        """Calculate age of event in hours."""
        return (datetime.utcnow() - self.timestamp).total_seconds() / 3600
    
    @property
    def age_days(self):
        """Calculate age of event in days."""
        return self.age_hours / 24
    
    def is_staff_action(self):
        """Check if event was triggered by staff (not system or student)."""
        return self.triggered_by not in ['system', 'student', 'automated']
    
    def is_system_action(self):
        """Check if event was triggered by system automation."""
        return self.triggered_by in ['system', 'automated']
    
    def is_admin_action(self):
        """Check if event is an administrative action."""
        return self.event_type in [
            self.EVENT_ADMIN_ACTION, self.EVENT_ADMIN_OVERRIDE, self.EVENT_SYSTEM_AUDIT
        ]
    
    def to_dict(self):
        """Convert event to dictionary for API responses."""
        return {
            'id': self.id,
            'job_id': self.job_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'triggered_by': self.triggered_by,
            'workstation_id': self.workstation_id,
            'details': self.details,
            'age_hours': round(self.age_hours, 2),
            'is_staff_action': self.is_staff_action(),
            'is_admin_action': self.is_admin_action()
        }
    
    @classmethod
    def create_job_event(cls, job_id, event_type, triggered_by, workstation_id=None, **details):
        """
        Convenience method to create and save an event.
        
        Args:
            job_id (str): Job ID
            event_type (str): Event type constant
            triggered_by (str): Staff member name
            workstation_id (str, optional): Workstation ID
            **details: Additional event data as keyword arguments
            
        Returns:
            Event: Created event instance
        """
        event = cls(
            job_id=job_id,
            event_type=event_type,
            triggered_by=triggered_by,
            workstation_id=workstation_id,
            details=details
        )
        db.session.add(event)
        return event
    
    @classmethod
    def log_job_created(cls, job, triggered_by='student'):
        """Log job creation event."""
        return cls.create_job_event(
            job_id=job.id,
            event_type=cls.EVENT_JOB_CREATED,
            triggered_by=triggered_by,
            student_name=job.student_name,
            student_email=job.student_email,
            material=job.material,
            printer=job.printer,
            color=job.color,
            original_filename=job.original_filename
        )
    
    @classmethod
    def log_staff_approval(cls, job, staff_name, workstation_id, weight_g, time_hours, cost_usd, authoritative_file):
        """Log staff approval event."""
        return cls.create_job_event(
            job_id=job.id,
            event_type=cls.EVENT_STAFF_APPROVED,
            triggered_by=staff_name,
            workstation_id=workstation_id,
            weight_g=weight_g,
            time_hours=time_hours,
            cost_usd=float(cost_usd),
            authoritative_file=authoritative_file,
            previous_status=job.status
        )
    
    @classmethod
    def log_staff_rejection(cls, job, staff_name, workstation_id, reasons, custom_reason=None):
        """Log staff rejection event."""
        return cls.create_job_event(
            job_id=job.id,
            event_type=cls.EVENT_STAFF_REJECTED,
            triggered_by=staff_name,
            workstation_id=workstation_id,
            reasons=reasons,
            custom_reason=custom_reason,
            previous_status=job.status
        )
    
    @classmethod
    def log_student_confirmation(cls, job, confirmation_method='email_link'):
        """Log student confirmation event."""
        return cls.create_job_event(
            job_id=job.id,
            event_type=cls.EVENT_STUDENT_CONFIRMED,
            triggered_by='student',
            confirmation_method=confirmation_method,
            confirmed_cost=float(job.cost_usd) if job.cost_usd else None
        )
    
    @classmethod
    def log_status_change(cls, job, staff_name, workstation_id, old_status, new_status, reason=None):
        """Log generic status change event."""
        return cls.create_job_event(
            job_id=job.id,
            event_type=cls.EVENT_STATUS_CHANGED,
            triggered_by=staff_name,
            workstation_id=workstation_id,
            old_status=old_status,
            new_status=new_status,
            reason=reason
        )
    
    @classmethod
    def log_admin_action(cls, job_id, staff_name, workstation_id, action, reason, **details):
        """Log administrative action event."""
        return cls.create_job_event(
            job_id=job_id,
            event_type=cls.EVENT_ADMIN_ACTION,
            triggered_by=staff_name,
            workstation_id=workstation_id,
            action=action,
            reason=reason,
            **details
        )
    
    @classmethod
    def get_recent_by_job(cls, job_id, limit=10):
        """Get recent events for a specific job."""
        return cls.query.filter_by(job_id=job_id)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_recent_by_staff(cls, staff_name, limit=50):
        """Get recent events by a specific staff member."""
        return cls.query.filter_by(triggered_by=staff_name)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()
    
    @classmethod
    def get_events_by_type(cls, event_type, limit=100):
        """Get recent events of a specific type."""
        return cls.query.filter_by(event_type=event_type)\
                       .order_by(cls.timestamp.desc())\
                       .limit(limit).all()