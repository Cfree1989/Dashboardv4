# User Stories - 3D Print Management System

## Student User Stories

### Submission Process
**As a student**, I want to submit a 3D model for printing so that I can get a physical version of my design.

**Acceptance Criteria:**
- I can upload .stl, .obj, or .3mf files up to 50MB
- I must provide my name, email, discipline, and class information
- I must select print method (Filament/Resin) and color preference
- I must acknowledge the $3.00 minimum charge
- I receive immediate feedback if my submission is invalid
- I get a confirmation page with job ID after successful submission

### Confirmation Process  
**As a student**, I want to confirm my print job after staff approval so that I can authorize the final cost and printing.

**Acceptance Criteria:**
- I receive an email with job details and confirmation link
- The confirmation link is valid for 72 hours
- I can see the calculated cost before confirming
- I can request a new confirmation email if my link expires
- I receive notification when my print is completed

### Tracking Process
**As a student**, I want to track my print job status so that I know when to pick it up and pay.

**Acceptance Criteria:**
- I can reference my job by the provided Job ID
- I understand what each status means (Pending, Ready to Print, etc.)
- I know when to come pay and pick up my completed print

## Staff User Stories

### Daily Operations
**As a staff member**, I want to review submitted print jobs so that I can approve appropriate requests and reject problematic ones.

**Acceptance Criteria:**
- I can see all new submissions in the dashboard
- I can view job details including uploaded files
- I can open files directly in slicer software with one click
- I can approve jobs by setting weight, time, and selecting authoritative file
- I can reject jobs with clear reasons that are communicated to students
- All my actions are attributed to me personally for accountability

### Workflow Management
**As a staff member**, I want to manage jobs through their lifecycle so that the printing process stays organized.

**Acceptance Criteria:**
- I can mark jobs as "Printing" when I start them
- I can mark jobs as "Complete" when printing finishes  
- I can handle payment and mark jobs as "Picked Up"
- I can revert recent status changes if I make mistakes
- I can add internal notes to jobs for other staff

### File Management
**As a staff member**, I want to work with job files efficiently so that I can prepare models for printing.

**Acceptance Criteria:**
- I can open any job file directly in appropriate slicer software
- I can save modified versions that become the authoritative file
- The system tracks both original student files and my sliced versions
- File operations are logged for troubleshooting

### Alert System
**As a staff member**, I want to be notified of new submissions so that I can respond promptly.

**Acceptance Criteria:**
- The dashboard shows visual "NEW" indicators for unreviewed jobs
- I hear audio notifications when new jobs arrive (toggleable)
- I can mark jobs as "reviewed" to clear visual alerts
- Jobs are color-coded by age to prioritize older submissions

## Administrative User Stories

### System Management
**As an administrator**, I want to manage staff access so that I can control who can perform actions.

**Acceptance Criteria:**
- I can add new staff members to the attribution list
- I can deactivate staff who no longer work here
- Inactive staff don't appear in action dropdowns but remain in audit logs
- Each workstation has its own shared password

### Data Management  
**As an administrator**, I want to manage system data so that storage doesn't grow indefinitely.

**Acceptance Criteria:**
- I can archive old completed jobs to free up active storage
- I can run integrity checks to find orphaned files or broken links
- I can export financial reports for accounting purposes
- I have clear audit trails for all system actions

### Emergency Operations
**As an administrator**, I want to handle exceptional situations so that operations can continue smoothly.

**Acceptance Criteria:**
- I can manually confirm jobs if email confirmation fails
- I can unlock jobs that are stuck in locked state
- I can force status changes for debugging workflow issues
- I can mark failed prints to return them to the queue
- All override actions are fully logged with my attribution

## Authentication Stories

### Workstation Access
**As a staff member**, I want to log into any workstation so that I can work from different computers.

**Acceptance Criteria:**
- Each workstation has its own shared password
- Sessions last for a full work day without re-authentication
- The UI clearly shows which workstation I'm logged into
- I must select my name for every action I perform

### Action Attribution
**As a staff member**, I want my actions to be properly attributed so that there's accountability.

**Acceptance Criteria:**
- Every state-changing action requires me to select my name
- My name appears in all event logs for actions I perform  
- The system records both my name and which workstation I used
- I cannot perform actions anonymously