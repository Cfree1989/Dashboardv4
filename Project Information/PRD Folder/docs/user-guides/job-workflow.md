# Job Workflow Guide

This guide explains the complete lifecycle of a 3D print job in the system, from initial submission to completion.

## Overview of Job Statuses

A print job progresses through several defined status stages. Each status has specific characteristics, permissions, and associated actions.

```
UPLOADED → PENDING → READYTOPRINT → PRINTING → COMPLETED → PAIDPICKEDUP → ARCHIVED
```

Alternative path for rejected jobs:
```
UPLOADED → REJECTED → ARCHIVED
```

## Detailed Job Lifecycle

### 1. UPLOADED Status

**Description**: The initial status when a student submits a new print job.

**Storage Location**: `storage/Uploaded/`

**Creation Process**:
1. Student completes the submission form with all required information
2. Student uploads a 3D model file (.stl, .obj, or .3mf)
3. System validates input and creates a new job record
4. System renames the file using the standard naming convention (`FirstAndLastName_PrintMethod_Color_SimpleJobID.extension`)
5. System creates a `metadata.json` file alongside the uploaded file
6. System asynchronously generates a thumbnail for dashboard display

**Available Actions**:
- Staff can view the job details
- Staff can open the file in their slicer software
- Staff can approve the job (which moves it to PENDING)
- Staff can reject the job (which moves it to REJECTED)
- Staff can add internal notes

**User Experience**:
- Student receives a success message with their job ID
- Staff sees the job in the UPLOADED tab of the dashboard
- New jobs display a "NEW" badge until marked as reviewed

### 2. PENDING Status

**Description**: The job has been approved by staff and is awaiting student confirmation.

**Storage Location**: `storage/Pending/`

**Transition Process**:
1. Staff reviews the uploaded file
2. Staff may prepare the model in their slicer software and save a modified version
3. Staff completes the approval form:
   - Selects the authoritative file for printing
   - Enters weight and time estimates
   - Selects their name for attribution
4. System calculates the cost based on material and weight
5. System moves the selected file and metadata to `storage/Pending/`
6. System generates a secure confirmation token
7. System sends an approval email to the student with a confirmation link
8. System logs the approval action with staff attribution

**Available Actions**:
- Staff can resend the confirmation email if needed
- Staff can force-confirm the job (administrative override)
- Staff can delete the job if necessary
- Staff can edit internal notes

**User Experience**:
- Student receives an approval email with job details and confirmation link
- Staff sees the job in the PENDING tab of the dashboard
- Jobs with expired confirmation tokens are visually highlighted

### 3. READYTOPRINT Status

**Description**: The job has been confirmed by the student and is ready to be printed.

**Storage Location**: `storage/ReadyToPrint/`

**Transition Process**:
1. Student clicks the confirmation link in the approval email
2. System validates the confirmation token
3. System moves files from `storage/Pending/` to `storage/ReadyToPrint/`
4. System updates the job status to READYTOPRINT
5. System logs the confirmation action

**Alternative Path**: Staff Force-Confirmation
1. Staff uses the administrative override to force-confirm the job
2. System records the reason for the override
3. System moves files to `storage/ReadyToPrint/`
4. System logs the force-confirmation with staff attribution

**Available Actions**:
- Staff can open the file in their slicer software
- Staff can mark the job as printing
- Staff can add internal notes

**User Experience**:
- Staff sees the job in the READYTOPRINT tab of the dashboard
- Job is prioritized based on its age (color-coded)

### 4. PRINTING Status

**Description**: The job is currently being printed on one of the lab's 3D printers.

**Storage Location**: `storage/Printing/`

**Transition Process**:
1. Staff selects a job from the READYTOPRINT tab
2. Staff clicks "Mark Printing" and confirms their attribution
3. System moves files from `storage/ReadyToPrint/` to `storage/Printing/`
4. System updates the job status to PRINTING
5. System logs the status change with staff attribution

**Available Actions**:
- Staff can mark the job as complete when printing finishes
- Staff can mark the print as failed (returns to READYTOPRINT)
- Staff can add internal notes

**User Experience**:
- Staff sees the job in the PRINTING tab of the dashboard
- Staff can easily track how long the job has been printing

### 5. COMPLETED Status

**Description**: The print is finished and ready for pickup and payment.

**Storage Location**: `storage/Completed/`

**Transition Process**:
1. Staff confirms the print is complete
2. Staff clicks "Mark Complete" and confirms their attribution
3. System moves files from `storage/Printing/` to `storage/Completed/`
4. System updates the job status to COMPLETED
5. System sends a completion notification email to the student
6. System logs the completion with staff attribution

**Available Actions**:
- Staff can mark the job as picked up
- Staff can revert completion if done in error (returns to PRINTING)
- Staff can add internal notes

**User Experience**:
- Student receives a completion email notification
- Staff sees the job in the COMPLETED tab of the dashboard

### 6. PAIDPICKEDUP Status

**Description**: The print has been paid for and picked up by the student.

**Storage Location**: `storage/PaidPickedUp/`

**Transition Process**:
1. Student arrives to pick up and pay for the print
2. Staff collects payment and provides the print
3. Staff clicks "Mark Picked Up" and confirms their attribution
4. System moves files from `storage/Completed/` to `storage/PaidPickedUp/`
5. System updates the job status to PAIDPICKEDUP
6. System logs the pickup with staff attribution

**Available Actions**:
- Staff can revert pickup if done in error (returns to COMPLETED)
- After 90 days, jobs become eligible for archival

**User Experience**:
- Staff sees the job in the PAIDPICKEDUP tab of the dashboard

### 7. REJECTED Status

**Description**: The job was rejected by staff because it cannot be printed.

**Storage Location**: Remains in `storage/Uploaded/` until archiving

**Transition Process**:
1. Staff determines the job cannot be printed
2. Staff selects rejection reasons and provides explanation
3. Staff clicks "Reject" and confirms their attribution
4. System updates the job status to REJECTED
5. System sends a rejection email to the student with the provided reasons
6. System logs the rejection with staff attribution

**Available Actions**:
- After 90 days, rejected jobs become eligible for archival

**User Experience**:
- Student receives a rejection email with explanation
- Staff sees the job in the REJECTED tab of the dashboard

### 8. ARCHIVED Status

**Description**: The job has been archived for long-term storage.

**Storage Location**: `storage/Archived/`

**Transition Process**:
1. Administrator triggers the archival process for eligible jobs
2. System identifies jobs in final states (PAIDPICKEDUP, REJECTED) older than the retention period
3. System moves files from their current location to `storage/Archived/`
4. System updates job status to ARCHIVED
5. System logs the archival with admin attribution

**Available Actions**:
- After 1 year in archived status, jobs become eligible for permanent deletion
- Admin can trigger permanent deletion through the pruning process

**User Experience**:
- Archived jobs are not shown in the standard dashboard
- Visible only in admin-specific archive views

## Special Workflow Cases

### Print Failure Handling

If a print fails due to lab error (not due to student file issues):

1. Staff clicks "Mark Failed" on a job in PRINTING status
2. Staff enters the failure reason
3. System moves the job back to READYTOPRINT status
4. Files are moved from `storage/Printing/` to `storage/ReadyToPrint/`
5. All job details (including cost) are preserved
6. No new student confirmation is required
7. System logs the failure with the provided reason

### Expired Confirmation Tokens

If a student doesn't confirm within the token expiry period (72 hours):

1. The system flags the job as having an expired confirmation
2. The job remains in PENDING status
3. When the student clicks the expired link, they see an expired token page
4. The student can request a new confirmation email (rate-limited)
5. Alternatively, staff can resend the confirmation email
6. Staff can also use the force-confirm override if needed

### Duplicate Submission Handling

If a student submits an identical file:

1. System calculates a SHA-256 hash of the uploaded file
2. System checks for active jobs with the same file hash and student email
3. If a duplicate is found, the submission is rejected with a 409 Conflict response
4. The student is informed that an identical job already exists

### Direct Job Deletion

For erroneous or unwanted submissions:

1. Only jobs in UPLOADED or PENDING status can be directly deleted
2. Staff clicks "Delete" on the job card
3. Staff confirms the deletion action
4. System permanently deletes the job record and associated files
5. This action is irreversible and fully logged

## Job Locking Mechanism

To prevent conflicts when multiple staff try to edit the same job:

1. When staff initiates an action (approve, reject, etc.), the job is locked
2. The lock includes the staff member's name and an expiration time
3. While locked, other staff cannot perform state-changing actions
4. The lock expires automatically after 5 minutes
5. Staff can explicitly release their own locks
6. Administrators can force-unlock if necessary

## Data Retention Policy

- **Active Jobs**: Remain in their respective statuses and directories
- **Completed Jobs**: After 90 days in PAIDPICKEDUP or REJECTED status, become eligible for archival
- **Archived Jobs**: After 1 year in ARCHIVED status, become eligible for permanent deletion

## Cross-Status Event Logging

Every status change and significant action is permanently recorded in the Event log:

- Job creation
- Staff approval/rejection
- Student confirmation
- Status changes
- Administrative overrides
- Email notifications
- Note edits

Each event includes:
- Timestamp
- Event type
- Staff attribution (when applicable)
- Workstation identification
- Contextual details
- Related job ID 