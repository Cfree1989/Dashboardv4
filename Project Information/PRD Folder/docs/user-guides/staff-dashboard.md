# Staff Dashboard Guide

This guide provides instructions for using the 3D Print System's staff dashboard, covering all major features and workflows.

## Dashboard Overview

The staff dashboard is the central interface for managing 3D print jobs. It provides a comprehensive view of all jobs in the system, with powerful filtering, sorting, and management capabilities.

### Key Dashboard Features

- **Auto-updating**: Dashboard refreshes automatically every 45 seconds
- **Sound notifications**: Audio alerts for new job uploads
- **Visual alerts**: Pulsing "NEW" badges for unreviewed jobs
- **Job age tracking**: Human-readable time display with color-coded aging
- **Staff acknowledgment**: "Mark as Reviewed" functionality to clear alerts
- **Debug panel**: Shows system health and sound settings
- **Last updated indicator**: Timestamp showing when data was last refreshed

## Getting Started

### Accessing the Dashboard

1. Open your web browser and navigate to `http://<server-ip>` (or the configured URL)
2. You will be redirected to the login page if not already authenticated
3. Enter your workstation credentials (shared password)
4. After successful login, you'll be taken to the dashboard

### Dashboard Layout

The dashboard is organized into several key sections:

- **Top Bar**: Shows workstation name, sound toggle, and last updated time
- **Status Tabs**: Filter jobs by status (Uploaded, Pending, etc.)
- **Job List**: Displays jobs matching the selected status and filters
- **Debug Panel**: Optional panel showing system health (visible in development)

## Job Management

### Viewing Jobs

1. Select the appropriate status tab to filter jobs
2. Jobs are displayed as cards with key information:
   - Thumbnail (if available)
   - Student name and email
   - File name
   - Submission date/time
   - Job age indicator (color-coded)
   - Printer and material details
   - Cost (if calculated)
   - Action buttons appropriate to the job's status

### Job Cards

Each job card shows essential information and provides status-specific action buttons:

- **Uploaded Jobs**: Open File, Approve, Reject
- **Pending Jobs**: Open File, Resend Email
- **Ready to Print Jobs**: Open File, Mark Printing
- **Printing Jobs**: Mark Complete, Mark Failed
- **Completed Jobs**: Mark Picked Up
- **Paid & Picked Up Jobs**: No actions (archived state)

### Managing Job State

#### Approving a Job

1. Click "Approve" on a job card in the UPLOADED tab
2. The Approval Modal will open
3. Select the authoritative file from the dropdown
   - The system will recommend the most recently modified file
   - The original uploaded file is always available
4. Enter the weight (grams) and print time (hours)
   - Cost is automatically calculated based on material and weight
   - Minimum charge of $3.00 is enforced
5. Select your name from the staff attribution dropdown
6. Click "Approve" to confirm
7. The system will:
   - Move files to the Pending directory
   - Update job status to PENDING
   - Send an approval email with confirmation link to the student
   - Log the approval event with your attribution

#### Rejecting a Job

1. Click "Reject" on a job card in the UPLOADED tab
2. The Rejection Modal will open
3. Select the applicable rejection reasons:
   - Model is broken or has errors
   - Model is too large for printers
   - Unsupported geometry
   - Needs scaling
   - Other (with custom explanation)
4. Add additional notes in the custom reason field if needed
5. Select your name from the staff attribution dropdown
6. Click "Reject" to confirm
7. The system will:
   - Update job status to REJECTED
   - Send a rejection email to the student with the selected reasons
   - Log the rejection event with your attribution

#### Mark as Printing

1. Click "Mark Printing" on a job card in the READYTOPRINT tab
2. Confirm your staff attribution
3. The system will:
   - Move files to the Printing directory
   - Update job status to PRINTING
   - Log the status change event with your attribution

#### Mark as Complete

1. Click "Mark Complete" on a job card in the PRINTING tab
2. Confirm your staff attribution
3. The system will:
   - Move files to the Completed directory
   - Update job status to COMPLETED
   - Send a completion email to the student
   - Log the completion event with your attribution

#### Mark as Picked Up

1. Click "Mark Picked Up" on a job card in the COMPLETED tab
2. Confirm your staff attribution
3. The system will:
   - Move files to the PaidPickedUp directory
   - Update job status to PAIDPICKEDUP
   - Log the pickup event with your attribution

### Working with Files

#### Opening Files in Slicer Software

1. Click "Open File" on any job card
2. The system will generate a `3dprint://` protocol URL
3. Your browser will prompt to open the URL with the SlicerOpener application
4. SlicerOpener will validate the file path and open it in the appropriate slicer software
5. If multiple slicers are compatible with the file type, you may be prompted to choose one

#### Handling Slicer Files

1. When you open a file in your slicer software, make any necessary adjustments
2. Save the sliced file in the same directory, with the same base name but a different extension
   - For example, if opening `JaneDoe_Filament_Blue_123.stl`, save as `JaneDoe_Filament_Blue_123.3mf`
3. During the approval process, you'll be able to select which file to use as the authoritative version

## Advanced Features

### Job Notes

Each job can have staff notes attached for internal use:

1. Click on a job card to view detailed information
2. In the expanded view, locate the Notes section
3. Click in the notes field to edit
4. Type your note and press Enter or click outside the field to save
5. Notes are visible to all staff and are saved automatically
6. All note changes are attributed to the staff member who made them

### Handling Expired Confirmation Links

If a student's confirmation link expires:

1. The job will be flagged in the dashboard with an "Expired" indicator
2. Click "Resend Email" on the job card
3. Confirm your staff attribution
4. A new confirmation email with a fresh token will be sent to the student

### Print Failure Handling

If a print fails due to a lab error (not due to the student's file):

1. Click "Mark Failed" on a job card in the PRINTING tab
2. Enter the reason for the failure (e.g., "Filament tangle detected")
3. Confirm your staff attribution
4. The system will:
   - Move the job back to READYTOPRINT status
   - Preserve all job details including cost
   - No new student confirmation is required
   - Log the failure with the provided reason

### Reverting Recent Status Changes

For recent status changes, you can use the revert function:

1. After marking a job complete or picked up, a "Revert" button will appear temporarily
2. Click "Revert" to undo the status change
3. Confirm your staff attribution
4. The system will:
   - Move the job back to its previous status
   - Return files to the appropriate directory
   - Log the reversion with your attribution

## Dashboard Features

### Sound Notifications

Sound alerts play when new jobs are uploaded:

1. Click the sound icon in the top bar to toggle sounds on/off
2. When enabled, a notification sound will play when new jobs appear
3. Your sound preference is saved to your browser's local storage

### Visual Alert System

New jobs are highlighted visually:

1. Unreviewed jobs display a pulsing "NEW" badge
2. Click "Mark as Reviewed" to acknowledge the job
3. This updates the `staff_viewed_at` timestamp and removes the visual alert
4. The review state is shared across all workstations

### Job Age Tracking

Jobs are color-coded based on their age:

- **Green**: Less than 24 hours old
- **Yellow**: 24-48 hours old
- **Orange**: 48-72 hours old
- **Red**: More than 72 hours old

This helps prioritize older submissions that may need attention.

### Search and Filtering

1. Use the search box to find jobs by student name, email, or class number
2. Use the filter dropdown to filter by:
   - Printer type
   - Material/color
   - Discipline
   - Date range
3. Filters can be combined with status tabs for precise results
4. Clear filters using the "Clear" button

## Administrative Functions

### Managing Staff List

1. Navigate to the Staff Management section
2. To add a new staff member:
   - Click "Add Staff"
   - Enter the staff member's name
   - Click "Add"
3. To deactivate a staff member:
   - Find their name in the list
   - Click "Deactivate"
   - Confirm the action
4. Deactivated staff won't appear in attribution dropdowns but will remain in historical logs

### System Health Audit

1. Navigate to the System Health section
2. Click "Run System Audit" to check for inconsistencies
3. Review the generated report, which may identify:
   - Orphaned files (files without database entries)
   - Broken links (database entries pointing to missing files)
   - Stale files (files in incorrect directories)
4. Use the provided tools to resolve identified issues

### Data Archival

1. Navigate to the Data Management section
2. To archive old jobs:
   - Click "Archive Old Jobs"
   - Set the retention period (default 90 days)
   - Confirm the action
3. To permanently delete archived jobs:
   - Click "Prune Archives"
   - Set the retention period (default 365 days)
   - Confirm the action
   - Note: This is irreversible

## Troubleshooting

### Common Issues and Solutions

- **Job is locked by another user**: Wait for the lock to expire (5 minutes) or ask an administrator to force-unlock it
- **SlicerOpener doesn't open**: Ensure the protocol handler is correctly installed on your computer
- **Job files not showing up**: Check if the network storage is correctly mounted at the expected path
- **Dashboard not auto-updating**: Check your internet connection and try refreshing manually

### Force Unlock

If a job is stuck in a locked state:

1. Only administrators should perform this action
2. Navigate to the locked job
3. Click "Force Unlock"
4. Enter the reason for the force unlock
5. Confirm your staff attribution
6. The system will release the lock and log the override action 