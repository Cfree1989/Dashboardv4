# API Endpoints - 3D Print Management System

Base URL: `/api/v1`

All endpoints return JSON responses with UTC timestamps. Protected endpoints require `Authorization: Bearer <workstation_jwt>` header.

## Authentication

### Login
- **POST** `/auth/login`
- **Body**: `{ "workstation_id": "front-desk", "password": "shared-password" }`
- **Success (200)**: `{ "token": "workstation-jwt", "workstation_id": "front-desk" }`
- **Error (401)**: `{ "error": "invalid_credentials", "message": "Invalid workstation ID or password" }`

## System Health

### Health Check
- **GET** `/health`
- **Public endpoint** (no authentication required)
- **Success (200)**: `{ "status": "ok", "components": { "database": "ok", "workers": "ok" } }`
- **Error (503)**: `{ "status": "error", "components": { "database": "error", "workers": "ok" } }`

## Student Submission

### Submit Job
- **POST** `/submit`
- **Content-Type**: `multipart/form-data`
- **Body**: Form data with fields:
  - `student_name` (string, required)
  - `student_email` (email, required)
  - `discipline` (string, required)
  - `class_number` (string, required)
  - `print_method` (enum: "filament" | "resin", required)
  - `color` (string, required)
  - `printer` (string, required)
  - `minimum_charge_consent` (boolean, required)
  - `file` (file upload, .stl/.obj/.3mf, max 50MB, required)
- **Success (201)**: Returns job object with ID
- **Error (400)**: Validation errors
- **Error (409)**: Duplicate submission detected
- **Error (429)**: Rate limit exceeded

### Confirm Job
- **POST** `/confirm/<token>`
- **Success (200)**: `{ "job": { job_object }, "message": "Job confirmed successfully" }`
- **Error (404)**: Token not found
- **Error (410)**: `{ "error": "token_expired", "job_id": "abc123" }`

### Resend Confirmation
- **POST** `/submit/resend-confirmation`
- **Body**: `{ "job_id": "abc123" }`
- **Success (200)**: `{ "message": "New confirmation email sent" }`
- **Error (429)**: Rate limited

## Staff Dashboard

### List Jobs
- **GET** `/jobs`
- **Auth**: Required
- **Query Params**: 
  - `status` (string, optional): Filter by job status
  - `search` (string, optional): Search student name/email
  - `printer` (string, optional): Filter by printer
  - `discipline` (string, optional): Filter by discipline
  - `confirmation_expired` (boolean, optional): Show only expired confirmations
- **Success (200)**: `{ "jobs": [job_objects], "total": 50, "filtered": 25 }`

### Get Job Details
- **GET** `/jobs/<job_id>`
- **Auth**: Required
- **Success (200)**: Full job object with event history
- **Error (404)**: Job not found

### Get Candidate Files
- **GET** `/jobs/<job_id>/candidate-files`
- **Auth**: Required
- **Success (200)**: `{ "files": ["original.stl", "sliced.3mf"] }`

## Job Actions

### Lock Job
- **POST** `/jobs/<job_id>/lock`
- **Auth**: Required
- **Success (200)**: `{ "message": "Job locked", "locked_until": "timestamp" }`
- **Error (409)**: `{ "error": "job_locked", "locked_by": "Jane Doe" }`

### Unlock Job
- **POST** `/jobs/<job_id>/unlock`
- **Auth**: Required
- **Success (200)**: `{ "message": "Job unlocked" }`

### Extend Lock
- **POST** `/jobs/<job_id>/lock/extend`
- **Auth**: Required
- **Success (200)**: `{ "message": "Lock extended", "locked_until": "timestamp" }`

### Approve Job
- **POST** `/jobs/<job_id>/approve`
- **Auth**: Required
- **Body**: 
  ```json
  {
    "weight_g": 25.5,
    "time_hours": 3.0,
    "authoritative_file": "filename.stl",
    "staff_name": "Jane Doe"
  }
  ```
- **Success (200)**: Updated job object
- **Error (400)**: Validation errors
- **Error (409)**: Wrong status or job locked

### Reject Job
- **POST** `/jobs/<job_id>/reject`
- **Auth**: Required
- **Body**: 
  ```json
  {
    "reasons": ["too_large", "poor_quality"],
    "custom_reason": "Model needs supports",
    "staff_name": "Jane Doe"
  }
  ```
- **Success (200)**: Updated job object

### Mark Job as Printing
- **POST** `/jobs/<job_id>/mark-printing`
- **Auth**: Required
- **Body**: `{ "staff_name": "Jane Doe" }`
- **Success (200)**: Updated job object

### Mark Job as Complete
- **POST** `/jobs/<job_id>/mark-complete`
- **Auth**: Required
- **Body**: `{ "staff_name": "Jane Doe" }`
- **Success (200)**: Updated job object

### Process Payment
- **POST** `/jobs/<job_id>/payment`
- **Auth**: Required
- **Body**: 
  ```json
  {
    "grams": 25.3,
    "txn_no": "TC123456",
    "picked_up_by": "John Smith",
    "staff_name": "Jane Doe"
  }
  ```
- **Success (200)**: Updated job with payment details

### Update Notes
- **PATCH** `/jobs/<job_id>/notes`
- **Auth**: Required
- **Body**: `{ "notes": "Print had minor warping on corners" }`
- **Success (200)**: Updated job object

### Mark as Reviewed
- **POST** `/jobs/<job_id>/review`
- **Auth**: Required
- **Body**: `{ "reviewed": true, "staff_name": "Jane Doe" }`
- **Success (200)**: Updated job object

### Delete Job
- **DELETE** `/jobs/<job_id>`
- **Auth**: Required
- **Success (204)**: No content
- **Error (403)**: Cannot delete job in this status

## Staff Management

### List Staff
- **GET** `/staff`
- **Auth**: Required
- **Query Params**: `include_inactive` (boolean, optional)
- **Success (200)**: `{ "staff": [{"name": "Jane Doe", "is_active": true}] }`

### Add Staff
- **POST** `/staff`
- **Auth**: Required
- **Body**: `{ "name": "New Staff Member", "staff_name": "Admin User" }`
- **Success (201)**: New staff object

### Update Staff Status
- **PATCH** `/staff/<name>`
- **Auth**: Required
- **Body**: `{ "is_active": false, "staff_name": "Admin User" }`
- **Success (200)**: Updated staff object

## Admin Overrides

### Force Unlock Job
- **POST** `/jobs/<job_id>/admin/force-unlock`
- **Auth**: Required
- **Body**: `{ "reason": "Browser crashed", "staff_name": "Admin User" }`
- **Success (200)**: `{ "message": "Lock released" }`

### Manual Confirmation
- **POST** `/jobs/<job_id>/admin/force-confirm`
- **Auth**: Required
- **Body**: `{ "reason": "Student confirmed verbally", "staff_name": "Admin User" }`
- **Success (200)**: Updated job object

### Change Status
- **POST** `/jobs/<job_id>/admin/change-status`
- **Auth**: Required
- **Body**: `{ "new_status": "READYTOPRINT", "reason": "Debugging", "staff_name": "Admin User" }`
- **Success (200)**: Updated job object

### Mark Print Failed
- **POST** `/jobs/<job_id>/admin/mark-failed`
- **Auth**: Required
- **Body**: `{ "reason": "Filament jam", "staff_name": "Jane Doe" }`
- **Success (200)**: Job moved back to READYTOPRINT

### Resend Email
- **POST** `/jobs/<job_id>/admin/resend-email`
- **Auth**: Required
- **Body**: `{ "email_type": "approval", "staff_name": "Jane Doe" }`
- **Success (200)**: `{ "message": "Email sent", "new_token": "xyz789" }`

## System Management

### Start Integrity Audit
- **POST** `/admin/audit/start`
- **Auth**: Required
- **Body**: `{ "staff_name": "Admin User" }`
- **Success (202)**: `{ "message": "Audit started", "task_id": "audit-123" }`

### Get Audit Report
- **GET** `/admin/audit/report`
- **Auth**: Required
- **Success (200)**: `{ "orphaned_files": [], "broken_links": [], "generated_at": "timestamp" }`

### Delete Orphaned File
- **DELETE** `/admin/audit/orphaned-file`
- **Auth**: Required
- **Body**: `{ "file_path": "path/to/orphan.stl", "staff_name": "Admin User" }`
- **Success (200)**: `{ "message": "File deleted" }`

### Archive Jobs
- **POST** `/admin/archive`
- **Auth**: Required
- **Body**: `{ "retention_days": 90, "staff_name": "Admin User" }`
- **Success (200)**: `{ "jobs_archived": 15 }`

### Prune Jobs
- **POST** `/admin/prune`
- **Auth**: Required
- **Body**: `{ "retention_days": 365, "staff_name": "Admin User" }`
- **Success (200)**: `{ "jobs_deleted": 5 }`

## Analytics

### Dashboard Stats
- **GET** `/stats`
- **Auth**: Required
- **Success (200)**: `{ "uploaded": 10, "pending": 5, "readyToPrint": 3 }`

### Export Payments
- **POST** `/export/payments`
- **Auth**: Required
- **Body**: 
  ```json
  {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "email_to": "admin@university.edu",
    "staff_name": "Admin User"
  }
  ```
- **Success (202)**: `{ "message": "Export queued", "task_id": "export-123" }`

## Standard Response Format

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Response
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": { /* additional error details */ },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Common Error Codes

- `validation_failed` - Request data validation errors
- `job_not_found` - Job ID does not exist
- `invalid_status` - Job not in correct status for action
- `job_locked` - Job is locked by another user
- `file_operation_failed` - File system operation failed
- `rate_limit_exceeded` - Too many requests
- `token_expired` - Confirmation token expired
- `insufficient_permission` - Action not allowed
- `internal_server_error` - Unexpected server error

## Rate Limits

- `/submit`: 3 requests per IP per hour
- `/auth/login`: 10 requests per IP per hour  
- `/submit/resend-confirmation`: 1 per job per hour
- `/admin/resend-email`: 3 per job per hour