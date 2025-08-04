# Job Model - 3D Print Management System
"""
Job model representing a 3D print request from submission to completion.
Central entity with comprehensive workflow state management and file tracking.
"""

import uuid
import secrets
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func
from app import db


class Job(db.Model):
    """
    Job model representing a complete 3D print request.
    
    Tracks the entire lifecycle from student submission through staff approval,
    printing, payment, and pickup. Includes comprehensive file management and
    audit trail support.
    """
    
    __tablename__ = 'job'
    
    # Primary identifier (UUID as string for simplicity)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Student Information
    student_name = db.Column(db.String(100), nullable=False)
    student_email = db.Column(db.String(100), nullable=False)
    discipline = db.Column(db.String(50), nullable=False)
    class_number = db.Column(db.String(50), nullable=False)
    
    # File Management
    original_filename = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(256), nullable=False)  # Standardized name for dashboard
    file_path = db.Column(db.String(512), nullable=False)     # Path to authoritative file
    metadata_path = db.Column(db.String(512), nullable=False) # Path to metadata.json
    file_hash = db.Column(db.String(64), nullable=True)       # SHA-256 for duplicate detection
    
    # Job Configuration
    status = db.Column(db.String(20), nullable=False, default='UPLOADED')
    printer = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(32), nullable=False)
    material = db.Column(db.String(32), nullable=False)  # 'filament' or 'resin'
    weight_g = db.Column(db.Float, nullable=True)
    time_hours = db.Column(db.Float, nullable=True)
    cost_usd = db.Column(db.Numeric(6, 2), nullable=True)
    
    # Student Confirmation System
    acknowledged_minimum_charge = db.Column(db.Boolean, default=False, nullable=False)
    student_confirmed = db.Column(db.Boolean, default=False, nullable=False)
    student_confirmed_at = db.Column(db.DateTime, nullable=True)
    confirm_token = db.Column(db.String(128), nullable=True, unique=True)
    confirm_token_expires = db.Column(db.DateTime, nullable=True)
    is_confirmation_expired = db.Column(db.Boolean, default=False, nullable=False)
    confirmation_last_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Staff Management & Notes
    reject_reasons = db.Column(db.JSON, nullable=True)
    staff_viewed_at = db.Column(db.DateTime, nullable=True)    # For visual alerts
    last_updated_by = db.Column(db.String(100), nullable=True) # Staff member name
    notes = db.Column(db.Text, nullable=True)                  # Internal staff notes
    
    # Job Locking for Concurrent Access Control
    locked_by_user = db.Column(db.String(100), nullable=True)
    locked_until = db.Column(db.DateTime, nullable=True)
    locked_workstation = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='job', lazy='dynamic', cascade='all, delete-orphan')
    payment = db.relationship('Payment', backref='job', uselist=False, cascade='all, delete-orphan')
    
    # Indexes for common queries
    __table_args__ = (
        db.Index('idx_job_status', 'status'),
        db.Index('idx_job_created_at', 'created_at'),
        db.Index('idx_job_student_email', 'student_email'),
        db.Index('idx_job_confirm_token', 'confirm_token'),
    )
    
    def __repr__(self):
        return f'<Job {self.id}: {self.display_name} ({self.status})>'
    
    # Status Constants
    STATUS_UPLOADED = 'UPLOADED'
    STATUS_PENDING = 'PENDING'
    STATUS_READYTOPRINT = 'READYTOPRINT'
    STATUS_PRINTING = 'PRINTING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_PAIDPICKEDUP = 'PAIDPICKEDUP'
    STATUS_REJECTED = 'REJECTED'
    STATUS_ARCHIVED = 'ARCHIVED'
    
    VALID_STATUSES = [
        STATUS_UPLOADED, STATUS_PENDING, STATUS_READYTOPRINT, STATUS_PRINTING,
        STATUS_COMPLETED, STATUS_PAIDPICKEDUP, STATUS_REJECTED, STATUS_ARCHIVED
    ]
    
    # Status Transition Rules
    VALID_TRANSITIONS = {
        STATUS_UPLOADED: [STATUS_PENDING, STATUS_REJECTED, STATUS_ARCHIVED],
        STATUS_PENDING: [STATUS_READYTOPRINT, STATUS_UPLOADED],  # Can revert to uploaded
        STATUS_READYTOPRINT: [STATUS_PRINTING],
        STATUS_PRINTING: [STATUS_COMPLETED, STATUS_READYTOPRINT],  # Can fail back to ready
        STATUS_COMPLETED: [STATUS_PAIDPICKEDUP, STATUS_PRINTING],  # Can revert
        STATUS_PAIDPICKEDUP: [STATUS_ARCHIVED, STATUS_COMPLETED],  # Can revert
        STATUS_REJECTED: [STATUS_ARCHIVED],
        STATUS_ARCHIVED: []  # No transitions from archived
    }
    
    def can_transition_to(self, new_status):
        """Check if transition to new status is valid."""
        return new_status in self.VALID_TRANSITIONS.get(self.status, [])
    
    def generate_confirmation_token(self, expires_hours=72):
        """Generate secure confirmation token for student email."""
        self.confirm_token = secrets.token_urlsafe(32)
        self.confirm_token_expires = datetime.utcnow() + timedelta(hours=expires_hours)
        self.is_confirmation_expired = False
        return self.confirm_token
    
    def is_token_valid(self):
        """Check if confirmation token is valid and not expired."""
        if not self.confirm_token or not self.confirm_token_expires:
            return False
        return datetime.utcnow() < self.confirm_token_expires
    
    def expire_token(self):
        """Mark confirmation token as expired."""
        self.is_confirmation_expired = True
    
    # Job Locking Methods
    def is_locked(self):
        """Check if job is currently locked."""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until
    
    def lock(self, user_name, workstation_id, duration_minutes=5):
        """Lock job for exclusive editing."""
        if self.is_locked():
            return False  # Already locked
        
        self.locked_by_user = user_name
        self.locked_workstation = workstation_id
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
        return True
    
    def unlock(self):
        """Remove lock from job."""
        self.locked_by_user = None
        self.locked_workstation = None
        self.locked_until = None
    
    def extend_lock(self, duration_minutes=5):
        """Extend existing lock duration."""
        if self.is_locked():
            self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
            return True
        return False
    
    def is_locked_by_current_user(self, user_name=None, workstation_id=None):
        """Check if job is locked by the current user/workstation."""
        if not self.is_locked():
            return False
        
        if user_name and self.locked_by_user == user_name:
            return True
        if workstation_id and self.locked_workstation == workstation_id:
            return True
        
        return False
    
    # Status Helper Methods
    def is_active(self):
        """Check if job is in an active (non-final) status."""
        return self.status in [
            self.STATUS_UPLOADED, self.STATUS_PENDING, 
            self.STATUS_READYTOPRINT, self.STATUS_PRINTING, 
            self.STATUS_COMPLETED
        ]
    
    def is_deletable(self):
        """Check if job can be permanently deleted."""
        return self.status in [self.STATUS_UPLOADED, self.STATUS_PENDING]
    
    def needs_student_confirmation(self):
        """Check if job is waiting for student confirmation."""
        return (self.status == self.STATUS_PENDING and 
                not self.student_confirmed and 
                self.is_token_valid())
    
    def is_confirmation_overdue(self):
        """Check if student confirmation is overdue."""
        return (self.status == self.STATUS_PENDING and 
                not self.student_confirmed and 
                not self.is_token_valid())
    
    # Cost Calculation
    def calculate_cost(self):
        """Calculate print cost based on material and weight."""
        if not self.weight_g:
            return None
        
        if self.material == 'filament':
            base_cost = float(self.weight_g) * 0.10
        elif self.material == 'resin':
            base_cost = float(self.weight_g) * 0.20
        else:
            return None
        
        # Apply minimum charge
        return max(base_cost, 3.00)
    
    def update_cost(self):
        """Update cost_usd field based on current weight and material."""
        calculated_cost = self.calculate_cost()
        if calculated_cost:
            self.cost_usd = Decimal(str(calculated_cost))
    
    # Serialization
    def to_dict(self, include_events=False):
        """Convert job to dictionary for API responses."""
        data = {
            'id': self.id,
            'student_name': self.student_name,
            'student_email': self.student_email,
            'discipline': self.discipline,
            'class_number': self.class_number,
            'original_filename': self.original_filename,
            'display_name': self.display_name,
            'file_path': self.file_path,
            'status': self.status,
            'printer': self.printer,
            'color': self.color,
            'material': self.material,
            'weight_g': self.weight_g,
            'time_hours': self.time_hours,
            'cost_usd': float(self.cost_usd) if self.cost_usd else None,
            'student_confirmed': self.student_confirmed,
            'student_confirmed_at': self.student_confirmed_at.isoformat() if self.student_confirmed_at else None,
            'is_confirmation_expired': self.is_confirmation_expired,
            'needs_confirmation': self.needs_student_confirmation(),
            'is_overdue': self.is_confirmation_overdue(),
            'staff_viewed_at': self.staff_viewed_at.isoformat() if self.staff_viewed_at else None,
            'last_updated_by': self.last_updated_by,
            'notes': self.notes,
            'is_locked': self.is_locked(),
            'locked_by_user': self.locked_by_user if self.is_locked() else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_events:
            data['events'] = [event.to_dict() for event in self.events.order_by(Event.timestamp.desc())]
        
        if self.payment:
            data['payment'] = self.payment.to_dict()
        
        return data
    
    @classmethod
    def find_by_token(cls, token):
        """Find job by confirmation token."""
        return cls.query.filter_by(confirm_token=token).first()
    
    @classmethod
    def find_active_duplicates(cls, file_hash, student_email):
        """Find active jobs with same file hash and student email."""
        return cls.query.filter(
            cls.file_hash == file_hash,
            cls.student_email == student_email,
            cls.status.in_([
                cls.STATUS_UPLOADED, cls.STATUS_PENDING, cls.STATUS_READYTOPRINT
            ])
        ).all()