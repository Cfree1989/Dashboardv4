# Staff Model - 3D Print Management System
"""
Staff model for managing lab personnel with activation/deactivation support.
Supports staff turnover while preserving historical attribution in audit logs.
"""

from datetime import datetime
from app.database import db


class Staff(db.Model):
    """
    Staff model representing lab personnel.
    
    Manages active staff members who can be attributed to actions,
    while preserving historical records of inactive staff for audit trails.
    """
    
    __tablename__ = 'staff'
    
    # Primary identifier (staff name as primary key for simplicity)
    name = db.Column(db.String(100), primary_key=True)
    
    # Status tracking
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    deactivated_at = db.Column(db.DateTime, nullable=True)
    
    # Optional metadata
    notes = db.Column(db.Text, nullable=True)  # Internal notes about staff member
    
    # Relationships (optional, for query optimization)
    # Note: We use foreign() to avoid circular import issues
    # actions = db.relationship('Event', backref='attributed_staff', lazy=True,
    #                          primaryjoin="Staff.name == foreign(Event.triggered_by)")
    
    def __repr__(self):
        status = "active" if self.is_active else "inactive"
        return f'<Staff {self.name} ({status})>'
    
    def deactivate(self, reason=None):
        """Deactivate staff member."""
        if self.is_active:
            self.is_active = False
            self.deactivated_at = datetime.utcnow()
            if reason:
                self.notes = f"{self.notes or ''}\nDeactivated: {reason}".strip()
    
    def reactivate(self):
        """Reactivate staff member."""
        if not self.is_active:
            self.is_active = True
            self.deactivated_at = None
    
    @property
    def days_since_added(self):
        """Calculate days since staff member was added."""
        return (datetime.utcnow() - self.added_at).days
    
    @property
    def days_since_deactivated(self):
        """Calculate days since staff member was deactivated."""
        if not self.deactivated_at:
            return None
        return (datetime.utcnow() - self.deactivated_at).days
    
    def to_dict(self):
        """Convert staff to dictionary for API responses."""
        return {
            'id': hash(self.name) % 1000000,  # Generate numeric ID from name hash
            'name': self.name,
            'email': f"{self.name.lower().replace(' ', '.')}@university.edu",  # Generate email
            'role': 'Staff Member',  # Default role
            'is_active': self.is_active,
            'is_recently_added': self.days_since_added <= 7,
            'added_at': self.added_at.isoformat(),
            'deactivated_at': self.deactivated_at.isoformat() if self.deactivated_at else None,
            'days_since_added': self.days_since_added,
            'days_since_deactivated': self.days_since_deactivated
        }
    
    @classmethod
    def get_active_staff(cls):
        """Get all active staff members."""
        return cls.query.filter_by(is_active=True).order_by(cls.name).all()
    
    @classmethod
    def get_all_staff(cls, include_inactive=False):
        """Get all staff members, optionally including inactive ones."""
        query = cls.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        return query.order_by(cls.name).all()
    
    @classmethod
    def create_staff_member(cls, name, notes=None):
        """Create new active staff member."""
        staff = cls(name=name, notes=notes)
        db.session.add(staff)
        return staff
    
    @classmethod
    def find_by_name(cls, name):
        """Find staff member by name."""
        return cls.query.get(name)
    
    @classmethod
    def is_valid_staff_name(cls, name):
        """Check if name belongs to an active staff member."""
        staff = cls.find_by_name(name)
        return staff is not None and staff.is_active