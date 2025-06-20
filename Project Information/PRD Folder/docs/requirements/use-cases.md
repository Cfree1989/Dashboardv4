# Use Cases

This document outlines the primary workflows and use cases for the 3D Print System, organized by job status progression.

## UC-1: Student Submission (UPLOADED)

**Actor:** Student  
**Precondition:** Student has a 3D model file ready for printing  
**Postcondition:** Job is created in UPLOADED status

1. Student navigates to the submission form (`/submit`)
2. Student fills out the required information:
   - Name and email address
   - Discipline and class number
   - Print method (Filament or Resin)
   - Color preference (based on selected print method)
   - Printer selection
   - Minimum charge consent
3. Student uploads their 3D model file (.stl, .obj, or .3mf)
4. System validates the form input and file:
   - Checks file type and size
   - Validates email format
   - Ensures all required fields are filled
5. System processes the submission:
   - File is renamed using standard naming convention (`FirstAndLastName_PrintMethod_Color_SimpleJobID.extension`)
   - File is stored in `storage/Uploaded/` directory
   - `metadata.json` is created alongside the file
   - Thumbnail is generated asynchronously
   - Job record is created in database with UPLOADED status
6. Student is shown a success page with their job ID and next steps

## UC-2: Staff Job Approval (PENDING)

**Actor:** Staff Member  
**Precondition:** Job exists in UPLOADED status  
**Postcondition:** Job is moved to PENDING status, student receives approval email

1. Staff member logs into the dashboard using workstation credentials
2. Staff views new jobs in the UPLOADED tab
3. Staff selects a job to review
4. Staff opens the file in local slicer software using the 3dprint:// protocol handler
5. Staff prepares the model for printing (slicing, adjusting settings)
6. Staff saves the sliced file in the job's directory
7. Staff initiates the approval process:
   - Staff selects the authoritative file for printing from available files
   - Staff enters weight (grams) and time (hours) estimates
   - System calculates the cost based on material and weight
   - Staff selects their name from the attribution dropdown
8. System processes the approval:
   - Files are moved from `storage/Uploaded/` to `storage/Pending/`
   - Job status is updated to PENDING
   - A secure confirmation token is generated
   - An approval email with confirmation link is sent to the student
   - Event is logged with staff attribution and workstation ID

## UC-3: Staff Job Rejection

**Actor:** Staff Member  
**Precondition:** Job exists in UPLOADED status  
**Postcondition:** Job is marked as REJECTED, student receives rejection email

1. Staff member reviews job and determines it cannot be printed
2. Staff initiates rejection process:
   - Staff selects standardized rejection reasons from checklist
   - Staff optionally adds custom rejection notes
   - Staff selects their name from attribution dropdown
3. System processes the rejection:
   - Job status is updated to REJECTED
   - Rejection email is sent to student with selected reasons
   - Event is logged with staff attribution and workstation ID
4. Job will eventually be moved to ARCHIVED status through the standard archival process

## UC-4: Student Confirmation (READYTOPRINT)

**Actor:** Student  
**Precondition:** Job exists in PENDING status with valid confirmation token  
**Postcondition:** Job is moved to READYTOPRINT status

1. Student receives approval email with confirmation link
2. Student clicks the link, which opens the confirmation page (`/confirm/<token>`)
3. System validates the token:
   - Checks that token exists and is associated with the correct job
   - Verifies that token has not expired
4. System processes the confirmation:
   - Files are moved from `storage/Pending/` to `storage/ReadyToPrint/`
   - Job status is updated to READYTOPRINT
   - Job's `student_confirmed` field is set to true
   - Event is logged with timestamp

## UC-5: Staff Marks Job as Printing

**Actor:** Staff Member  
**Precondition:** Job exists in READYTOPRINT status  
**Postcondition:** Job is moved to PRINTING status

1. Staff member selects job from READYTOPRINT tab
2. Staff retrieves the authoritative file and begins the print
3. Staff clicks "Mark Printing" button:
   - Staff selects their name from attribution dropdown
4. System processes the status change:
   - Files are moved from `storage/ReadyToPrint/` to `storage/Printing/`
   - Job status is updated to PRINTING
   - Event is logged with staff attribution and workstation ID

## UC-6: Staff Marks Job as Complete

**Actor:** Staff Member  
**Precondition:** Job exists in PRINTING status  
**Postcondition:** Job is moved to COMPLETED status, student receives completion email

1. Staff member removes completed print from printer
2. Staff clicks "Mark Complete" button:
   - Staff selects their name from attribution dropdown
3. System processes the status change:
   - Files are moved from `storage/Printing/` to `storage/Completed/`
   - Job status is updated to COMPLETED
   - Completion email is sent to student
   - Event is logged with staff attribution and workstation ID

## UC-7: Staff Marks Job as Picked Up

**Actor:** Staff Member  
**Precondition:** Job exists in COMPLETED status, student has paid and collected print  
**Postcondition:** Job is moved to PAIDPICKEDUP status

1. Student arrives to pick up and pay for print
2. Staff locates the completed print
3. Staff collects payment from student
4. Staff clicks "Mark Picked Up" button:
   - Staff selects their name from attribution dropdown
5. System processes the status change:
   - Files are moved from `storage/Completed/` to `storage/PaidPickedUp/`
   - Job status is updated to PAIDPICKEDUP
   - Event is logged with staff attribution and workstation ID

## UC-8: Administrator Archives Old Jobs

**Actor:** Administrator  
**Precondition:** Jobs exist in final states (PAIDPICKEDUP or REJECTED) older than retention period  
**Postcondition:** Old jobs are moved to ARCHIVED status

1. Administrator navigates to system management section
2. Administrator reviews jobs eligible for archival
3. Administrator triggers archival process:
   - Administrator confirms action
   - Administrator selects retention period (default 90 days)
4. System processes the archival:
   - Identifies eligible jobs in final states older than retention period
   - For each job, moves files to `storage/Archived/`
   - Updates job status to ARCHIVED
   - Logs event with admin attribution

## UC-9: Handling Expired Confirmation Links

**Actor:** Student, Staff Member  
**Precondition:** Job exists in PENDING status with expired confirmation token  
**Postcondition:** Job has new valid token, student receives new email

### Student Path
1. Student clicks expired confirmation link
2. System shows expired link page with job details
3. Student clicks "Request New Confirmation Email"
4. System validates the request (e.g., one request per hour per job)
5. System generates new token and sends new email
6. Student is shown confirmation message

### Staff Path
1. Staff notices job with expired confirmation on dashboard
2. Staff uses admin override to resend confirmation:
   - Staff selects "Resend Email" from actions menu
   - Staff selects email type "approval"
3. System generates new token and sends new email
4. Event is logged with staff attribution

## UC-10: Administrator Print Failure Handling

**Actor:** Staff Member  
**Precondition:** Job exists in PRINTING status, print has failed due to lab error  
**Postcondition:** Job is returned to READYTOPRINT status

1. Staff notices print failure not attributable to the student's file
2. Staff clicks "Mark Failed" button:
   - Staff enters failure reason (e.g., "Filament tangle detected")
   - Staff selects their name from attribution dropdown
3. System processes the status change:
   - Files are moved from `storage/Printing/` to `storage/ReadyToPrint/`
   - Job status is updated to READYTOPRINT
   - Events are logged with failure reason and staff attribution

## UC-11: Staff Notes Management

**Actor:** Staff Member  
**Precondition:** Job exists in any status  
**Postcondition:** Job has updated notes

1. Staff selects a job to view details
2. Staff clicks in notes field
3. Staff enters or edits notes about the job
4. System saves notes automatically
5. System logs notes update event with staff attribution 