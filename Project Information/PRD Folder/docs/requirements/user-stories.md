# User Stories

This document outlines the key user stories for the 3D Print System project, organized by user role.

## Student Stories

### Submission Process

1. **As a student, I want to upload my 3D model file** so that the staff can print it for me.
   - Acceptance Criteria:
     - I can upload .stl, .obj, or .3mf files
     - I receive immediate feedback if my file type is invalid
     - I receive immediate feedback if my file is too large (>50MB)
     - I am shown a success message when my upload completes

2. **As a student, I want to provide details about my print request** so that staff have the necessary context.
   - Acceptance Criteria:
     - I can enter my name and email
     - I can specify my discipline (Art, Architecture, etc.)
     - I can enter my class number or specify N/A
     - I can select print method and color options

3. **As a student, I want to see material and printer options** so that I can make informed choices.
   - Acceptance Criteria:
     - Print method descriptions are clearly visible
     - Color options are contingent on the print method selected
     - Printer dimensions are clearly displayed

4. **As a student, I want to receive email notifications** so that I know the status of my print job.
   - Acceptance Criteria:
     - I receive an email when my job is approved with a confirmation link
     - I receive an email when my job is rejected with the reasons
     - I receive an email when my job is complete and ready for pickup

5. **As a student with an expired confirmation link, I want to request a new link** so that I can still confirm my print job.
   - Acceptance Criteria:
     - When I visit an expired link, I see a clear message explaining the situation
     - I can request a new confirmation email
     - The system prevents abuse by limiting how often I can request new emails

## Staff Stories

### Job Management

6. **As a staff member, I want to log into a workstation** so that I can access the print management system.
   - Acceptance Criteria:
     - I can enter a shared workstation password
     - My authentication lasts for the entire workday
     - The UI shows which workstation I'm logged into

7. **As a staff member, I want to review submitted jobs** so that I can approve or reject them.
   - Acceptance Criteria:
     - I can see all submitted jobs in the dashboard
     - New jobs are visually highlighted
     - I can see job details like file name, student name, and requested options

8. **As a staff member, I want to approve jobs** so that students can confirm and we can proceed with printing.
   - Acceptance Criteria:
     - I can open a job's file in my local slicer software
     - I can enter weight and time estimates
     - The system calculates the cost based on my inputs
     - I must select my name from a staff dropdown before approving
     - The system prevents other staff from simultaneously editing the same job

9. **As a staff member, I want to reject jobs** so that students know their submission has issues.
   - Acceptance Criteria:
     - I can select standardized rejection reasons
     - I can add custom rejection notes
     - I must select my name from a staff dropdown before rejecting
     - The system sends a rejection email to the student

10. **As a staff member, I want to update job statuses** so that I can track progress.
    - Acceptance Criteria:
      - I can mark jobs as printing, completed, and picked up
      - I must select my name from a staff dropdown for each status change
      - Each change is logged with my name and timestamp

### Dashboard Experience

11. **As a staff member, I want to receive notifications** so that I'm aware of new submissions.
    - Acceptance Criteria:
      - The dashboard auto-updates every 45 seconds
      - Sound notifications play when new jobs are uploaded
      - I can toggle sound notifications on/off
      - Unreviewed jobs display "NEW" badges with pulsing animations

12. **As a staff member, I want to filter and sort jobs** so that I can find specific jobs quickly.
    - Acceptance Criteria:
      - I can filter by status (Uploaded, Pending, etc.)
      - I can search by student name or email
      - I can filter by printer type or discipline

13. **As a staff member, I want to add notes to jobs** so that I can track important information.
    - Acceptance Criteria:
      - I can add and edit notes for any job
      - Notes are visible to all staff
      - Notes are saved automatically

14. **As a staff member, I want to see job age at a glance** so that I can prioritize older submissions.
    - Acceptance Criteria:
      - Jobs display time elapsed in human-readable format
      - Color-coding indicates job age priority
      - The "Last Updated" timestamp shows when dashboard data was refreshed

## Administrator Stories

15. **As an administrator, I want to manage staff lists** so that the attribution system stays current.
    - Acceptance Criteria:
      - I can add new staff members to the system
      - I can deactivate staff who no longer work in the lab
      - Inactive staff don't appear in attribution dropdowns
      - Historical actions remain attributed to their original staff

16. **As an administrator, I want system health monitoring** so that I can ensure reliable operations.
    - Acceptance Criteria:
      - I can view the current status of all system components
      - I can trigger file system integrity audits
      - I can view reports of orphaned files or broken database links
      - I can resolve identified issues through the UI

17. **As an administrator, I want to archive old jobs** so that the active system stays efficient.
    - Acceptance Criteria:
      - I can trigger the archival process for jobs in final states
      - I can see how many jobs were archived
      - The system preserves metadata for archived jobs in the database
      - Archived files are moved to a separate storage location

18. **As an administrator, I want to perform override actions** so that I can handle exceptional cases.
    - Acceptance Criteria:
      - I can force-unlock jobs that are stuck
      - I can manually confirm jobs when necessary
      - I can change job statuses for debugging purposes
      - All override actions are fully logged with justification 