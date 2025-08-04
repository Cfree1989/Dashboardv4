# Workflow States - 3D Print Job Lifecycle

## Job Status Definitions

### UPLOADED
- **Description**: Student has submitted a 3D model file through the web form
- **Location**: `storage/Uploaded/` directory
- **Next Actions**: Staff review for approval or rejection
- **Staff Actions**: Approve, Reject, Delete (if erroneous)
- **Student Actions**: None (waiting for staff review)

### PENDING  
- **Description**: Staff approved the job, awaiting student confirmation of cost
- **Location**: `storage/Pending/` directory
- **Next Actions**: Student confirms via email link or staff manually confirms
- **Staff Actions**: Manual confirmation, resend email, revert to uploaded
- **Student Actions**: Click confirmation link in email

### READYTOPRINT
- **Description**: Student confirmed the job, ready for printing
- **Location**: `storage/ReadyToPrint/` directory  
- **Next Actions**: Staff starts printing process
- **Staff Actions**: Mark as Printing, modify if needed
- **Student Actions**: None (waiting for printing to start)

### PRINTING
- **Description**: Job is currently being printed
- **Location**: `storage/Printing/` directory
- **Next Actions**: Complete successfully or handle print failure
- **Staff Actions**: Mark Complete, Mark Failed (returns to ReadyToPrint)
- **Student Actions**: None (waiting for completion)

### COMPLETED
- **Description**: Print finished successfully, awaiting pickup and payment
- **Location**: `storage/Completed/` directory
- **Next Actions**: Student pays and picks up print
- **Staff Actions**: Process payment and mark as Picked Up, revert to Printing if needed
- **Student Actions**: Come to lab to pay and collect print

### PAIDPICKEDUP
- **Description**: Student has paid and collected their print
- **Location**: `storage/PaidPickedUp/` directory
- **Next Actions**: Eventually archived after retention period
- **Staff Actions**: Revert to Completed (if needed), archive when eligible
- **Student Actions**: None (process complete)

### REJECTED
- **Description**: Staff rejected the submission due to quality or policy issues
- **Location**: `storage/Uploaded/` directory (until archived)
- **Next Actions**: Eventually archived, student may resubmit new job
- **Staff Actions**: Archive when eligible
- **Student Actions**: Submit new job addressing rejection reasons

### ARCHIVED
- **Description**: Old job moved to long-term storage after retention period
- **Location**: `storage/Archived/` directory
- **Next Actions**: Eventually permanent deletion after extended retention
- **Staff Actions**: Permanent deletion after final retention period
- **Student Actions**: None (historical record only)

## Status Transition Rules

### Valid Transitions
```
UPLOADED → PENDING (staff approval)
UPLOADED → REJECTED (staff rejection)
UPLOADED → ARCHIVED (direct archival of old uploads)

PENDING → READYTOPRINT (student confirmation)
PENDING → UPLOADED (staff revert, rare)

READYTOPRINT → PRINTING (staff starts print)

PRINTING → COMPLETED (successful print)
PRINTING → READYTOPRINT (print failure, retry needed)

COMPLETED → PAIDPICKEDUP (payment and pickup)
COMPLETED → PRINTING (staff revert, rare)

PAIDPICKEDUP → ARCHIVED (retention policy)
PAIDPICKEDUP → COMPLETED (staff revert, very rare)

REJECTED → ARCHIVED (retention policy)
```

### File Movement Rules
- Files move between directories when status changes
- Original student file is always preserved
- Authoritative file (may be sliced version) is the active working file
- metadata.json moves with the authoritative file
- Copy-update-delete pattern ensures file operation resilience

## Business Rules

### Approval Requirements
- Staff must set weight (grams) and time (hours) for cost calculation
- Staff must explicitly select authoritative file from available options
- All approvals require staff attribution (name selection)

### Confirmation Requirements  
- Email tokens expire after 72 hours
- Students can request new confirmation emails (rate limited)
- Staff can manually confirm if email system fails

### Payment Requirements
- Minimum $3.00 charge applies to all jobs
- Final weight from scale may differ from estimated weight
- Tiger-Cash transaction number must be recorded
- Payment processing requires staff attribution

### Retention Policies
- Jobs in final states (PAIDPICKEDUP, REJECTED) eligible for archival after 90 days
- Archived jobs eligible for permanent deletion after 1 year
- Active jobs (UPLOADED through COMPLETED) never automatically archived

## Error Handling States

### Locked Jobs
- Jobs can be locked during staff editing to prevent conflicts
- Locks expire automatically after 5 minutes
- Administrators can force-unlock stuck jobs

### Failed Operations
- File operation failures leave job in previous valid state
- Database remains source of truth for current status
- System integrity audit can detect and repair inconsistencies

### Expired Confirmations
- Jobs with expired confirmation tokens flagged visually
- Staff can resend confirmations or manually confirm
- Students have self-service option to request new emails