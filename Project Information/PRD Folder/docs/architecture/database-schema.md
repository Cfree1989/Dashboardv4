# Database Schema

This document details the database schema for the 3D Print System, focusing on the core models and their relationships.

## Core Models

The system uses PostgreSQL with SQLAlchemy ORM for robust data management and comprehensive audit trails.

### Staff Model

Represents staff members for attribution and tracking:

```python
class Staff(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    is_active = db.Column(db.Boolean, default=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    deactivated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships - optional, for query optimization
    actions = db.relationship('Event', backref='attributed_staff', lazy=True, 
                             primaryjoin="Staff.name == foreign(Event.triggered_by)")
```

#### Fields Explanation:

- `name`: Primary key, the staff member's full name as it appears in attribution dropdowns
- `is_active`: Boolean indicating if the staff member should appear in attribution dropdowns
- `added_at`: Timestamp when the staff member was added to the system
- `deactivated_at`: Timestamp when the staff member was deactivated (if applicable)

### Job Model

The central entity representing each 3D print request:

```python
class Job(db.Model):
   id = db.Column(db.String, primary_key=True)   # uuid4 hex
   student_name = db.Column(db.String(100))
   student_email = db.Column(db.String(100))
   discipline = db.Column(db.String(50))
   class_number = db.Column(db.String(50))
   
   # File Management
   original_filename = db.Column(db.String(256))
   display_name = db.Column(db.String(256))      # Standardized name for dashboard
   file_path = db.Column(db.String(512))         # Path to authoritative file
   metadata_path = db.Column(db.String(512))     # Path to metadata.json
   
   # Job Configuration
   status = db.Column(db.String(50))             # UPLOADED, PENDING, etc.
   printer = db.Column(db.String(64))
   color = db.Column(db.String(32))
   material = db.Column(db.String(32))
   weight_g = db.Column(db.Float)
   time_hours = db.Column(db.Float)
   cost_usd = db.Column(db.Numeric(6, 2))
   
   # Student Confirmation
   acknowledged_minimum_charge = db.Column(db.Boolean, default=False)
   student_confirmed = db.Column(db.Boolean, default=False)
   student_confirmed_at = db.Column(db.DateTime, nullable=True)
   confirm_token = db.Column(db.String(128), nullable=True, unique=True)
   confirm_token_expires = db.Column(db.DateTime, nullable=True)
   is_confirmation_expired = db.Column(db.Boolean, default=False, nullable=False)
   confirmation_last_sent_at = db.Column(db.DateTime, nullable=True)
   
   # Staff Management
   reject_reasons = db.Column(db.JSON, nullable=True)
   staff_viewed_at = db.Column(db.DateTime, nullable=True)    # For visual alerts
   last_updated_by = db.Column(db.String(100), nullable=True) # Staff member name from attribution dropdown
   notes = db.Column(db.Text, nullable=True)                  # Staff notes
   
   # Locking for concurrency control
   locked_by = db.Column(db.String(100), nullable=True)       # Staff member who has locked the job
   locked_until = db.Column(db.DateTime, nullable=True)       # When the lock expires
   
   # File hash for deduplication
   file_hash = db.Column(db.String(64), nullable=True)        # SHA-256 hash of original file
   
   # Timestamps
   created_at = db.Column(db.DateTime, default=datetime.utcnow)
   updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
   
   # Relationships
   events = db.relationship('Event', backref='job', lazy=True)
```

#### Fields Explanation:

- **Identity and Submission Information**:
  - `id`: Primary key, UUID in hex format
  - `student_name`, `student_email`: Student's contact information
  - `discipline`, `class_number`: Academic context for the print

- **File Management**:
  - `original_filename`: The name of the uploaded file
  - `display_name`: Standardized name (FirstAndLastName_PrintMethod_Color_SimpleJobID)
  - `file_path`: Path to the currently authoritative file (for resilience)
  - `metadata_path`: Path to the accompanying metadata.json file (for resilience)
  - `file_hash`: SHA-256 hash of the original file for deduplication checks

- **Job Configuration**:
  - `status`: Current status of the job (UPLOADED, PENDING, etc.)
  - `printer`: Selected printer for the job
  - `color`, `material`: Selected aesthetics and materials
  - `weight_g`: Estimated weight in grams (for cost calculation)
  - `time_hours`: Estimated print time in hours
  - `cost_usd`: Calculated cost based on material and weight

- **Student Confirmation**:
  - `acknowledged_minimum_charge`: Whether student accepted minimum charge
  - `student_confirmed`: Whether student confirmed the print job
  - `confirm_token`: Secure token for email confirmation
  - `confirm_token_expires`: Expiration timestamp for the token
  - `is_confirmation_expired`: Flag to quickly check if confirmation has expired
  - `confirmation_last_sent_at`: When the last confirmation email was sent

- **Staff Management**:
  - `reject_reasons`: JSON field storing rejection reasons if rejected
  - `staff_viewed_at`: When staff acknowledged the job (to clear NEW indicators)
  - `last_updated_by`: Staff attribution for the most recent update
  - `notes`: Text field for staff notes
  - `locked_by`, `locked_until`: Concurrency control fields

### Event Model

Immutable audit trail for all system actions:

```python
class Event(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   job_id = db.Column(db.String, db.ForeignKey('job.id'), nullable=False)
   timestamp = db.Column(db.DateTime, default=datetime.utcnow)
   event_type = db.Column(db.String(50))         # 'JobCreated', 'StaffApproved', etc.
   details = db.Column(db.JSON, nullable=True)   # Contextual information
   triggered_by = db.Column(db.String(100))      # Staff member's name from attribution dropdown
   workstation_id = db.Column(db.String(100))    # Identifier for the physical computer
```

#### Fields Explanation:

- `id`: Auto-incrementing primary key
- `job_id`: Foreign key to the related Job
- `timestamp`: When the event occurred
- `event_type`: Type of event (e.g., 'JobCreated', 'StaffApproved', 'StatusChanged')
- `details`: JSON field containing contextual information specific to the event
- `triggered_by`: Name of the staff member who performed the action
- `workstation_id`: Identifier for the physical computer from which the action originated

## Relationships and Key Constraints

### Staff-Event Relationship

- Each Event's `triggered_by` field references a Staff member's `name`
- This allows for tracking which staff member performed each action
- When a staff member is deactivated, they won't appear in dropdowns but their historical actions remain attributed to them

### Job-Event Relationship

- Each Event belongs to a Job through the `job_id` foreign key
- A Job can have many Events, creating a comprehensive audit trail
- Events are immutable once created, ensuring data integrity for auditing

## Status Name Standardization

To maintain consistency across the codebase, job statuses follow these naming conventions:

1. **Internal Identifiers (API, Code, Database):** UPPERCASE
   - Example: `UPLOADED`, `PENDING`, `READYTOPRINT`, `PRINTING`, `COMPLETED`, `PAIDPICKEDUP`, `REJECTED`, `ARCHIVED`
   - Used in: API endpoints, TypeScript types, database values, conditional logic

2. **Directory Names:** PascalCase
   - Example: `Uploaded/`, `Pending/`, `ReadyToPrint/`, `Printing/`, `Completed/`, `PaidPickedUp/`, `Archived/`
   - Used in: File system organization

3. **User Interface:** Title Case with spaces
   - Example: "Uploaded", "Pending", "Ready to Print", "Printing", "Completed", "Paid & Picked Up", "Rejected"
   - Used in: Dashboard displays, modals, status indicators

## Indexes and Performance Considerations

For optimal performance, the following indexes should be created:

- `Job.status` - Frequent filtering by status in dashboard
- `Job.file_hash` - For duplicate detection
- `Job.created_at` - For sorting and timeframe queries
- `Event.job_id` - For quickly retrieving all events for a job
- `Event.timestamp` - For chronological sorting
- `Event.triggered_by` - For filtering events by staff member

## Event Types

The system uses standardized event types to track all significant actions:

- `JobCreated` - When a student submits a new job
- `StaffApproved` - When staff approves a job
- `StaffRejected` - When staff rejects a job
- `StatusChanged` - When a job's status changes
- `StudentConfirmed` - When a student confirms the job
- `ConfirmationExpired` - When a confirmation token expires
- `NotesUpdated` - When staff updates job notes
- `AdminOverride` - When an admin performs an override action
- `PrintFailed` - When a print fails and is returned to ReadyToPrint
- `EmailSent` - When an email notification is sent
- `FileDeleted` - When a file is deleted by admin
- `JobArchived` - When a job is archived

Each event type has specific details recorded in the `details` JSON field appropriate to the action. 