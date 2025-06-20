# API Specification

This document details the RESTful API endpoints for the 3D Print System. All endpoints are prefixed with `/api/v1` and return responses in JSON format. Timestamps are in UTC ISO 8601 format.

## General Information

- **Base URL**: `/api/v1`
- **Authentication**: JWT-based authentication for protected endpoints
- **Response Format**: All responses are in JSON format
- **Timestamp Format**: UTC ISO 8601 (e.g., `"2023-06-01T12:00:00Z"`)

## Authentication

### Login

**Endpoint**: `POST /auth/login`

**Description**: Authenticates a workstation.

**Request Body**:
```json
{
  "workstation_id": "front-desk",
  "password": "shared-password"
}
```

**Success Response (200)**:
```json
{
  "token": "workstation-jwt",
  "expires_at": "2023-06-01T18:00:00Z",
  "workstation_id": "front-desk"
}
```

**Error Response (401)**:
```json
{
  "message": "Invalid workstation ID or password"
}
```

### Authentication Headers

For protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <workstation-jwt>
```

**Error Response (401)**:
```json
{
  "message": "Invalid or expired token"
}
```

**Error Response (403)**:
```json
{
  "message": "Insufficient permissions"
}
```

## Public System Health

### Health Check

**Endpoint**: `GET /health`

**Description**: Provides a simple health check of the backend services. Does not require authentication. Intended for use by automated monitoring tools.

**Success Response (200)**:
```json
{
  "status": "ok",
  "timestamp": "2023-06-01T12:00:00Z",
  "components": {
    "database": "ok",
    "workers": "ok"
  }
}
```

**Error Response (503)**:
```json
{
  "status": "error",
  "timestamp": "2023-06-01T12:00:00Z",
  "components": {
    "database": "ok",
    "workers": "error",
    "details": "Could not connect to message broker."
  }
}
```

## Student Submission

### Submit Job

**Endpoint**: `POST /submit`

**Description**: Creates a new print job from student submission.

**Request Body**: `multipart/form-data` with fields for `student_name`, `student_email`, `discipline`, `class_number`, `print_method`, `color`, `printer`, `acknowledged_minimum_charge`, and `file`.

**Success Response (201)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "JaneDoe_Filament_Blue_123.stl",
  "status": "UPLOADED",
  "created_at": "2023-06-01T12:00:00Z"
}
```

**Error Response (400)**:
```json
{
  "errors": {
    "student_email": "Invalid email format",
    "file": "File must be .stl, .obj, or .3mf format"
  }
}
```

**Error Response (409)**:
```json
{
  "message": "An identical active job has already been submitted.",
  "existing_job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (429)**:
```json
{
  "message": "Submission limit exceeded. Please try again later."
}
```

### Confirm Job

**Endpoint**: `POST /confirm/<token>`

**Description**: Confirms a job using the token from the email link.

**Request Body**: (Empty)

**Success Response (200)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "JaneDoe_Filament_Blue_123.stl",
  "status": "READYTOPRINT",
  "student_confirmed_at": "2023-06-01T14:30:00Z"
}
```

**Error Response (404)**:
```json
{
  "message": "Invalid confirmation token"
}
```

**Error Response (410)**:
```json
{
  "message": "Confirmation link expired",
  "reason": "expired",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Get Expired Confirmation Details

**Endpoint**: `GET /confirm/expired`

**Description**: Returns information about an expired confirmation link.

**Query Parameters**:
- `job_id`: Required. The ID of the job.

**Success Response (200)**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "display_name": "JaneDoe_Filament_Blue_123.stl",
  "status": "PENDING",
  "token_expired_at": "2023-06-01T14:30:00Z",
  "can_request_new_email": true,
  "wait_time_minutes": 0
}
```

### Resend Confirmation Email

**Endpoint**: `POST /submit/resend-confirmation`

**Description**: Allows a student to request a new confirmation email for an unconfirmed job. This is a public but rate-limited endpoint.

**Request Body**:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (200)**:
```json
{
  "message": "A new confirmation email has been sent."
}
```

**Error Response (404)**:
```json
{
  "message": "Job not found or already confirmed/rejected."
}
```

**Error Response (429)**:
```json
{
  "message": "You can request a new email in 45 minutes."
}
```

## Staff Management

### Get Staff List

**Endpoint**: `GET /staff`

**Description**: Returns a list of staff members.

**Authentication**: Required (Workstation JWT)

**Query Parameters**:
- `include_inactive`: Optional, defaults to false. Whether to include inactive staff members.

**Success Response (200)**:
```json
{
  "staff": [
    {
      "name": "Jane Doe",
      "is_active": true,
      "added_at": "2023-01-15T10:00:00Z"
    },
    {
      "name": "John Smith",
      "is_active": false,
      "added_at": "2023-01-15T10:00:00Z",
      "deactivated_at": "2023-05-15T10:00:00Z"
    }
  ]
}
```

### Add Staff

**Endpoint**: `POST /staff`

**Description**: Adds a new staff member.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "name": "New Staff Name",
  "staff_name": "Admin User"
}
```

**Success Response (201)**:
```json
{
  "name": "New Staff Name",
  "is_active": true,
  "added_at": "2023-06-01T12:00:00Z"
}
```

**Error Response (409)**:
```json
{
  "message": "Staff member with this name already exists"
}
```

### Update Staff

**Endpoint**: `PATCH /staff/:name`

**Description**: Updates a staff member's status.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "is_active": false,
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "name": "Staff Name",
  "is_active": false,
  "added_at": "2023-01-15T10:00:00Z",
  "deactivated_at": "2023-06-01T12:00:00Z"
}
```

**Error Response (404)**:
```json
{
  "message": "Staff member not found"
}
```

## Job Management

### Get Jobs

**Endpoint**: `GET /jobs`

**Description**: Returns a list of jobs, optionally filtered by various criteria.

**Authentication**: Required (Workstation JWT)

**Query Parameters**:
- `status`: Optional. Filter by job status (e.g., "UPLOADED", "PENDING").
- `search`: Optional. Search for jobs by student name or email.
- `printer`: Optional. Filter by printer type.
- `discipline`: Optional. Filter by discipline.
- `confirmation_expired`: Optional. Filter for jobs with expired confirmation tokens.
- `page`: Optional, defaults to 1. Page number for pagination.
- `limit`: Optional, defaults to 50. Number of items per page.

**Success Response (200)**:
```json
{
  "jobs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "student_name": "Jane Doe",
      "student_email": "jane.doe@example.edu",
      "display_name": "JaneDoe_Filament_Blue_123.stl",
      "status": "UPLOADED",
      "created_at": "2023-06-01T12:00:00Z",
      "updated_at": "2023-06-01T12:00:00Z",
      "staff_viewed_at": null,
      "is_new": true,
      "locked_by": null,
      "locked_until": null,
      "printer": "Prusa MK4S",
      "color": "Blue",
      "material": "Filament",
      "cost_usd": null,
      "has_notes": false
    }
  ],
  "total": 25,
  "filtered": 10,
  "page": 1,
  "pages": 1,
  "limit": 50
}
```

### Get Job Details

**Endpoint**: `GET /jobs/<job_id>`

**Description**: Returns the full details of a job, including its event history.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "student_name": "Jane Doe",
  "student_email": "jane.doe@example.edu",
  "discipline": "Architecture",
  "class_number": "ARCH 4000",
  "original_filename": "model_v3.stl",
  "display_name": "JaneDoe_Filament_Blue_123.stl",
  "file_path": "storage/Uploaded/JaneDoe_Filament_Blue_123.stl",
  "status": "UPLOADED",
  "printer": "Prusa MK4S",
  "color": "Blue",
  "material": "Filament",
  "weight_g": null,
  "time_hours": null,
  "cost_usd": null,
  "acknowledged_minimum_charge": true,
  "student_confirmed": false,
  "student_confirmed_at": null,
  "is_confirmation_expired": false,
  "reject_reasons": null,
  "staff_viewed_at": null,
  "notes": null,
  "locked_by": null,
  "locked_until": null,
  "created_at": "2023-06-01T12:00:00Z",
  "updated_at": "2023-06-01T12:00:00Z",
  "events": [
    {
      "id": 1,
      "timestamp": "2023-06-01T12:00:00Z",
      "event_type": "JobCreated",
      "details": {
        "original_filename": "model_v3.stl"
      },
      "triggered_by": "Student",
      "workstation_id": null
    }
  ]
}
```

### Delete Job

**Endpoint**: `DELETE /jobs/<job_id>`

**Description**: Permanently deletes a job and its associated files. This action is irreversible and only permitted for jobs in 'UPLOADED' or 'PENDING' status.

**Authentication**: Required (Workstation JWT)

**Success Response (204 No Content)**:
No content returned.

**Error Response (403)**:
```json
{
  "message": "Job cannot be deleted in its current status"
}
```

**Error Response (403)**:
```json
{
  "message": "You do not hold the lock for this job"
}
```

### Get Candidate Files

**Endpoint**: `GET /jobs/<job_id>/candidate-files`

**Description**: Scans the job's current directory and returns a list of potential authoritative files for the approval modal.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "files": [
    {
      "filename": "JaneDoe_Filament_Blue_123.stl",
      "is_original": true,
      "last_modified": "2023-06-01T12:00:00Z",
      "size_bytes": 1048576
    },
    {
      "filename": "JaneDoe_Filament_Blue_123.3mf",
      "is_original": false,
      "last_modified": "2023-06-01T12:30:00Z",
      "size_bytes": 2097152
    }
  ],
  "recommended_file": "JaneDoe_Filament_Blue_123.3mf"
}
```

### Lock Job

**Endpoint**: `POST /jobs/<job_id>/lock`

**Description**: Acquires an exclusive lock on a job to prevent concurrent edits.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "message": "Job locked successfully",
  "locked_until": "2023-06-01T13:00:00Z"
}
```

**Error Response (409)**:
```json
{
  "message": "Job is currently locked by another user.",
  "locked_by": "Jane Doe",
  "locked_until": "2023-06-01T13:00:00Z"
}
```

### Unlock Job

**Endpoint**: `POST /jobs/<job_id>/unlock`

**Description**: Releases an exclusive lock on a job.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "message": "Job unlocked successfully."
}
```

### Extend Lock

**Endpoint**: `POST /jobs/<job_id>/lock/extend`

**Description**: Extends the duration of an existing lock (heartbeat).

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "message": "Lock extended successfully",
  "locked_until": "2023-06-01T13:15:00Z"
}
```

**Error Response (403)**:
```json
{
  "message": "You do not hold the lock for this job"
}
```

### Approve Job

**Endpoint**: `POST /jobs/<job_id>/approve`

**Description**: Approves a job. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "authoritative_file": "JaneDoe_Filament_Blue_123.3mf",
  "weight_g": 25.5,
  "time_hours": 3.5,
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PENDING",
  "file_path": "storage/Pending/JaneDoe_Filament_Blue_123.3mf",
  "weight_g": 25.5,
  "time_hours": 3.5,
  "cost_usd": "5.10",
  "updated_at": "2023-06-01T13:00:00Z"
}
```

### Reject Job

**Endpoint**: `POST /jobs/<job_id>/reject`

**Description**: Rejects a job. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "reasons": ["model_broken", "too_large"],
  "custom_reason": "Model has non-manifold edges",
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "REJECTED",
  "updated_at": "2023-06-01T13:00:00Z"
}
```

### Mark Job as Printing

**Endpoint**: `POST /jobs/<job_id>/mark-printing`

**Description**: Marks a job as printing. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PRINTING",
  "file_path": "storage/Printing/JaneDoe_Filament_Blue_123.3mf",
  "updated_at": "2023-06-01T15:00:00Z"
}
```

### Mark Job as Complete

**Endpoint**: `POST /jobs/<job_id>/mark-complete`

**Description**: Marks a job as complete. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "file_path": "storage/Completed/JaneDoe_Filament_Blue_123.3mf",
  "updated_at": "2023-06-02T10:00:00Z"
}
```

### Mark Job as Picked Up

**Endpoint**: `POST /jobs/<job_id>/mark-picked-up`

**Description**: Marks a job as picked up. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PAIDPICKEDUP",
  "file_path": "storage/PaidPickedUp/JaneDoe_Filament_Blue_123.3mf",
  "updated_at": "2023-06-03T14:00:00Z"
}
```

### Mark Job as Reviewed

**Endpoint**: `POST /jobs/<job_id>/review`

**Description**: Marks a job as reviewed (or un-reviewed). The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "reviewed": true,
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "staff_viewed_at": "2023-06-01T13:30:00Z",
  "updated_at": "2023-06-01T13:30:00Z"
}
```

### Update Job Notes

**Endpoint**: `PATCH /jobs/<job_id>/notes`

**Description**: Updates the notes for a job. The lock is automatically released upon completion.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "notes": "Student requested light infill to save material.",
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "notes": "Student requested light infill to save material.",
  "updated_at": "2023-06-01T13:35:00Z"
}
```

### Revert Completion

**Endpoint**: `POST /jobs/<job_id>/revert-completion`

**Description**: Reverts a job from `COMPLETED` back to `PRINTING`.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "PRINTING",
  "file_path": "storage/Printing/JaneDoe_Filament_Blue_123.3mf",
  "updated_at": "2023-06-02T11:00:00Z"
}
```

### Revert Pickup

**Endpoint**: `POST /jobs/<job_id>/revert-pickup`

**Description**: Reverts a job from `PAIDPICKEDUP` back to `COMPLETED`.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "COMPLETED",
  "file_path": "storage/Completed/JaneDoe_Filament_Blue_123.3mf",
  "updated_at": "2023-06-03T15:00:00Z"
}
```

## Admin Override Endpoints

### Force Unlock

**Endpoint**: `POST /jobs/<job_id>/admin/force-unlock`

**Description**: Forcibly releases a lock on a job.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "reason": "User browser crashed, releasing stuck lock.",
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "message": "Lock has been forcibly released."
}
```

### Force Confirm

**Endpoint**: `POST /jobs/<job_id>/admin/force-confirm`

**Description**: Administratively confirms a job without requiring student action.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "reason": "Student confirmed verbally",
  "bypass_email": true,
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "READYTOPRINT",
  "student_confirmed": true,
  "student_confirmed_at": "2023-06-01T15:00:00Z",
  "updated_at": "2023-06-01T15:00:00Z"
}
```

### Change Status

**Endpoint**: `POST /jobs/<job_id>/admin/change-status`

**Description**: Administratively changes a job's status.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "new_status": "READYTOPRINT",
  "reason": "Debugging workflow issue",
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "READYTOPRINT",
  "updated_at": "2023-06-01T15:30:00Z"
}
```

### Mark Print Failed

**Endpoint**: `POST /jobs/<job_id>/admin/mark-failed`

**Description**: Marks a job in the `PRINTING` status as failed due to lab error and returns it to the `READYTOPRINT` queue.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "reason": "Filament tangle detected on printer.",
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "READYTOPRINT",
  "updated_at": "2023-06-01T16:00:00Z"
}
```

### Resend Email

**Endpoint**: `POST /jobs/<job_id>/admin/resend-email`

**Description**: Allows staff to resend a notification email. This action is rate-limited.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "email_type": "approval",
  "staff_name": "Jane Doe"
}
```

**Success Response (200)**:
```json
{
  "message": "Email resent successfully",
  "new_token": "abc123"
}
```

**Error Response (429)**:
```json
{
  "message": "An email was sent recently. Please wait before resending."
}
```

## Admin System Health

### Start System Audit

**Endpoint**: `POST /admin/audit/start`

**Description**: Triggers a new system health and integrity scan. This will be an asynchronous task.

**Authentication**: Required (Workstation JWT)

**Success Response (202)**:
```json
{
  "message": "System audit started successfully.",
  "task_id": "some-async-task-id"
}
```

### Get Audit Report

**Endpoint**: `GET /admin/audit/report`

**Description**: Retrieves the report from the last completed system health scan.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "report_generated_at": "2023-06-01T12:00:00Z",
  "orphaned_files": [
    "path/to/orphan1.stl"
  ],
  "broken_links": [
    {
      "job_id": "abc",
      "missing_path": "path/to/missing.stl"
    }
  ],
  "stale_files": [
    {
      "job_id": "abc",
      "file_path": "path/to/stale.stl",
      "expected_directory": "ReadyToPrint",
      "actual_directory": "Pending"
    }
  ]
}
```

### Delete Orphaned File

**Endpoint**: `DELETE /admin/audit/orphaned-file`

**Description**: Deletes a specific orphaned file from the storage. This action is logged.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "file_path": "path/to/orphan1.stl",
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "message": "Orphaned file deleted successfully."
}
```

## Admin Data Management

### Archive Old Jobs

**Endpoint**: `POST /admin/archive`

**Description**: Triggers the archival of all jobs in a final state (`PaidPickedUp`, `Rejected`) that are older than the specified retention period.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "retention_days": 90,
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "message": "Archival process completed",
  "jobs_archived": 12
}
```

### Prune Archives

**Endpoint**: `POST /admin/prune`

**Description**: Permanently deletes all jobs in the `ARCHIVED` state that are older than the specified retention period. This is a destructive action.

**Authentication**: Required (Workstation JWT)

**Request Body**:
```json
{
  "retention_days": 365,
  "staff_name": "Admin User"
}
```

**Success Response (200)**:
```json
{
  "message": "Pruning process completed",
  "jobs_deleted": 5
}
```

## Dashboard Stats & Analytics

### Get Basic Stats

**Endpoint**: `GET /stats`

**Description**: Returns basic system stats for dashboard display.

**Authentication**: Required (Workstation JWT)

**Success Response (200)**:
```json
{
  "uploaded": 10,
  "pending": 5,
  "readyToPrint": 3,
  "printing": 2,
  "completed": 8,
  "paidPickedUp": 15,
  "rejected": 4,
  "storage_usage_mb": 1024,
  "storage_limit_mb": 10240
}
```

### Get Detailed Stats

**Endpoint**: `GET /stats/detailed`

**Description**: Returns detailed analytics for admin dashboard.

**Authentication**: Required (Workstation JWT)

**Query Parameters**:
- `days`: Optional, defaults to 30. Number of days to include in trends.
- `printer`: Optional, defaults to "all". Filter by printer type.
- `discipline`: Optional, defaults to "all". Filter by discipline.

**Success Response (200)**:
```json
{
  "submission_trends": {
    "dates": ["2023-05-01", "2023-05-02", "..."],
    "counts": [5, 7, "..."]
  },
  "printer_utilization": {
    "Prusa MK4S": 45,
    "Prusa XL": 30,
    "Form 3": 25
  },
  "rejection_reasons": {
    "model_broken": 12,
    "too_large": 8,
    "unsupported_geometry": 5
  },
  "average_processing_time": {
    "upload_to_approval": 24,
    "approval_to_printing": 36,
    "printing_to_completion": 48
  },
  "staff_activity": {
    "Jane Doe": 35,
    "John Smith": 28
  }
}
``` 