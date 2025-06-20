# File Management Architecture

This document details the file management architecture for the 3D Print System, including storage structure, file handling procedures, and the SlicerOpener protocol handler.

## 1. Storage Structure

The 3D Print System uses a network-mounted storage location accessible from all staff computers. This shared storage follows a standardized directory structure based on job status.

### 1.1 Directory Structure

```
storage/
├─ Uploaded/         # New submissions
├─ Pending/          # Awaiting student confirmation
├─ ReadyToPrint/     # Approved, ready for printing
├─ Printing/         # Currently being printed
├─ Completed/        # Finished prints
├─ PaidPickedUp/     # Final state for completed jobs
└─ Archived/         # Archived jobs (older completed or rejected)
```

### 1.2 File Naming Convention

All files follow a standardized naming convention:

```
FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension
```

Example: `JaneDoe_Filament_Blue_123.stl`

This naming convention provides essential context about the job at the filesystem level, even if database access is temporarily unavailable.

## 2. File Resilience Strategy

The system employs multiple strategies to ensure file integrity and resilience:

### 2.1 metadata.json Companion Files

Each job file is accompanied by a `metadata.json` file containing essential job details:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_name": "Jane Doe",
  "student_email": "jane.doe@example.edu",
  "discipline": "Architecture",
  "class_number": "ARCH 4000",
  "print_method": "Filament",
  "color": "Blue",
  "printer": "Prusa MK4S",
  "original_filename": "model_v3.stl",
  "status": "PENDING",
  "created_at": "2023-06-01T12:00:00Z",
  "status_updated_at": "2023-06-01T14:30:00Z"
}
```

This companion file serves as a redundancy mechanism, allowing the system to rebuild or verify database records if needed.

### 2.2 Authoritative File Tracking

The system tracks both the original student upload and any staff-modified files:

1. **Original File Preservation**: Student uploads are preserved throughout the entire lifecycle
2. **Explicit Authoritative File Selection**: During approval, staff explicitly select which file should be considered the authoritative version for printing
3. **Database Path Tracking**: The `file_path` field in the database always points to the current authoritative file

### 2.3 Resilient File Operations

File operations follow a "copy, update, then delete" pattern to prevent data loss:

1. **Copy**: First copy the file to the destination directory
2. **Update Database**: Update the database record within a transaction
3. **Delete Original**: Only after successful database update, delete the original

This approach ensures that if a crash occurs between steps, the system can recover without data loss.

## 3. File Lifecycle Management

### 3.1 Submission Phase

1. Student uploads file through Next.js form
2. Backend validates file type (.stl, .obj, .3mf) and size (max 50MB)
3. File is renamed according to the standard convention
4. File is stored in `storage/Uploaded/` directory
5. `metadata.json` is generated with job details
6. Thumbnail is asynchronously generated

### 3.2 Approval Phase

1. Staff opens file in local slicer software, prepares for printing
2. Staff may create new "sliced" versions of the file
3. When approving, staff explicitly selects the authoritative file
4. System moves the selected file to `storage/Pending/`
5. Original file is also preserved (if different from selected file)
6. All file paths are updated in the database

### 3.3 Status Progression

As a job moves through its lifecycle, files move between directories according to the status:

1. `storage/Uploaded/` → `storage/Pending/` (on staff approval)
2. `storage/Pending/` → `storage/ReadyToPrint/` (on student confirmation)
3. `storage/ReadyToPrint/` → `storage/Printing/` (when printing starts)
4. `storage/Printing/` → `storage/Completed/` (when print is complete)
5. `storage/Completed/` → `storage/PaidPickedUp/` (when student pays and picks up)
6. `storage/PaidPickedUp/` → `storage/Archived/` (during archival process)

For rejected jobs:
1. `storage/Uploaded/` → `storage/Archived/` (during archival process)

### 3.4 Error Recovery

The system includes several mechanisms to recover from file system errors:

1. **System Health Audit**: Admin-triggered tool to identify and resolve discrepancies
2. **Orphaned Files Detection**: Identifies files without database entries
3. **Broken Links Detection**: Finds database entries pointing to missing files
4. **Stale Files Detection**: Locates files in incorrect directories based on job status

## 4. Direct File Access: SlicerOpener Protocol Handler

### 4.1 Purpose and Overview

The SlicerOpener protocol handler enables staff to open 3D model files directly from the web dashboard in their local slicer software.

### 4.2 Components

```
SlicerOpener/
├── SlicerOpener.py      # Protocol handler script
├── config.ini           # Configuration file
├── register.bat         # Windows registry setup
└── SlicerOpener.exe     # Compiled executable (PyInstaller)
```

### 4.3 Protocol Registration

On Windows, the protocol is registered via the registry:

```
Windows Registry:
HKEY_CLASSES_ROOT\3dprint\shell\open\command
(Default) = "C:\Path\To\SlicerOpener.exe" "%1"
```

A `register.bat` script automates this setup on staff computers.

### 4.4 Configuration

The `config.ini` file defines essential settings:

```ini
[main]
AUTHORITATIVE_STORAGE_BASE_PATH=Z:\storage
LOG_FILE_PATH=C:\Users\Staff\AppData\Local\SlicerOpener\logs.txt

[slicer_prusaslicer]
name=PrusaSlicer
path=C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe
extensions=.stl,.obj,.3mf

[slicer_formlabs]
name=PreForm
path=C:\Program Files\Formlabs\PreForm\PreForm.exe
extensions=.stl,.obj,.3mf,.form
```

### 4.5 Security Validation

The protocol handler implements strict security measures:

1. **Path Validation**: Ensures the requested file is within the authorized storage path
2. **Path Traversal Prevention**: Guards against directory traversal attacks
3. **Error Handling**: Provides clear feedback for any validation failures
4. **Audit Logging**: Records all access attempts with timestamps and results

### 4.6 Operation Workflow

1. Dashboard generates a link like `3dprint://open?path=Z:\storage\Uploaded\JaneDoe_Filament_Blue_123.stl`
2. User clicks the "Open in Slicer" button, triggering the protocol
3. Browser passes the URL to the registered SlicerOpener application
4. SlicerOpener parses and validates the URL
5. SlicerOpener checks which slicers can handle the file type
6. If multiple slicers are compatible, SlicerOpener shows a selection dialog
7. SlicerOpener launches the appropriate slicer with the file path
8. GUI feedback is shown for success or failure

### 4.7 SlicerOpener Implementation Details

Key features of the SlicerOpener implementation:

1. **External Configuration**: All paths and slicer definitions are in `config.ini`, not hardcoded
2. **GUI Feedback**: Uses tkinter or similar for user-friendly dialogs
3. **Slicer Selection Dialog**: Allows user to choose which application to open the file with
4. **Logging**: Records all actions and errors for troubleshooting
5. **Error Handling**: Clear error messages for file not found, security violations, etc.

## 5. Backup and Disaster Recovery

### 5.1 Automated Backup Strategy

1. **Daily Database Backup**: Complete SQL dump of PostgreSQL database
2. **Daily File System Backup**: Incremental backup of the entire `storage/` directory
3. **Off-Site Storage**: Backups pushed to secure, remote location
4. **Retention Policy**: Daily backups for 14 days, weekly for 2 months, monthly for 1 year

### 5.2 Recovery Procedure

1. **Halt System**: Stop all application services
2. **Restore File System**: Copy backup files to host's storage directory
3. **Restore Database**: Load SQL dump into PostgreSQL
4. **Verify Integrity**: Run system health audit to identify any inconsistencies
5. **Restart System**: Bring application services back online

## 6. Data Retention and Archival

### 6.1 Archival Policy

1. **Retention Period**: Jobs in a final state (`PaidPickedUp` or `Rejected`) are retained for 90 days
2. **Archival Process**: Admin-triggered process moves eligible jobs to `ARCHIVED` status and files to `storage/Archived/`
3. **Long-term Storage**: Archived jobs and files are retained for 1 year before permanent deletion

### 6.2 Permanent Deletion

1. **Eligibility**: Only jobs in the `ARCHIVED` state older than 1 year
2. **Process**: Admin-triggered process permanently deletes both database records and files
3. **Logging**: All deletion actions are fully logged with admin attribution 