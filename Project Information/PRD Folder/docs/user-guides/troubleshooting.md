# Troubleshooting Guide

This document provides solutions for common issues that may arise when using the 3D Print Dashboard system.

## Table of Contents
1. [Dashboard Access Issues](#dashboard-access-issues)
2. [File Upload Problems](#file-upload-problems)
3. [Dashboard Functionality Issues](#dashboard-functionality-issues)
4. [SlicerOpener Protocol Handler Issues](#sliceropener-protocol-handler-issues)
5. [Email Notification Problems](#email-notification-problems)
6. [Job Status Issues](#job-status-issues)
7. [Storage and File Management](#storage-and-file-management)
8. [Performance Issues](#performance-issues)
9. [Administrative Tasks](#administrative-tasks)

## Dashboard Access Issues

### Unable to Access Dashboard

**Symptoms**:
- Browser shows "Connection refused" or "Cannot connect to server"
- Dashboard URL doesn't load at all

**Possible Causes and Solutions**:

1. **Server is down**
   - Check if all Docker containers are running: `docker-compose ps`
   - Restart the containers if needed: `docker-compose down && docker-compose up -d`

2. **Network connectivity issues**
   - Verify you can ping the server IP address
   - Check if any firewalls might be blocking port 80/443

3. **Incorrect URL/IP address**
   - Confirm you're using the correct URL or IP address
   - Try accessing via IP address directly if DNS resolution might be failing

4. **Frontend container not running**
   - Check specific frontend logs: `docker-compose logs frontend`
   - Look for errors and restart if necessary: `docker-compose restart frontend`

### Login Authentication Issues

**Symptoms**:
- "Invalid credentials" error when attempting to log in
- Login form accepts submission but returns to login page

**Possible Causes and Solutions**:

1. **Incorrect workstation credentials**
   - Verify the workstation ID and password are correct
   - Ask administrator to verify/reset workstation password if necessary

2. **Backend authentication service issues**
   - Check backend logs: `docker-compose logs backend`
   - Verify the JWT configuration in the `.env` file is correct

3. **JWT token expired/invalid**
   - Clear browser cookies and cache
   - Try logging in with a different browser

## File Upload Problems

### File Upload Fails

**Symptoms**:
- Upload progress reaches 100% but then shows an error
- Form submission fails with file validation error
- Server returns 413 error (Payload Too Large)

**Possible Causes and Solutions**:

1. **File too large**
   - Ensure file is under the size limit (50MB)
   - Try reducing the model complexity or file size

2. **Incorrect file format**
   - Verify the file is in an allowed format (.stl, .obj, or .3mf)
   - Try re-exporting the file from the modeling software

3. **Server-side upload limit issues**
   - Check for nginx/web server upload limits in configuration
   - Check backend logs for specific error messages
   - Adjust server configuration if needed (see administrator guide)

4. **File corruption**
   - Verify the file can be opened in a local slicer software
   - Try re-exporting a fresh copy of the file

### File Validation Problems

**Symptoms**:
- Upload is rejected with message about invalid model
- Error mentioning non-manifold geometry or mesh issues

**Possible Causes and Solutions**:

1. **3D model has geometry issues**
   - Fix non-manifold edges, holes, or other mesh issues in modeling software
   - Use mesh repair software (like MeshMixer or Netfabb) to fix the model

2. **File is not actually a 3D model**
   - Ensure the file actually contains 3D geometry
   - Convert from proprietary formats to standard formats (.stl) using appropriate software

## Dashboard Functionality Issues

### Dashboard Not Updating

**Symptoms**:
- New submissions don't appear in dashboard
- Status changes aren't reflected when actions are taken
- Last updated timestamp doesn't change

**Possible Causes and Solutions**:

1. **Auto-refresh not working**
   - Check if JavaScript is enabled in your browser
   - Try manually refreshing the page first
   - Check browser console for JavaScript errors

2. **Backend API communication failure**
   - Check network tab in browser developer tools for failed API requests
   - Verify the backend service is running: `docker-compose ps`
   - Check backend logs: `docker-compose logs backend`

3. **Database connectivity issues**
   - Check database logs: `docker-compose logs db`
   - Verify database is running and accepting connections

### Sound Notifications Not Working

**Symptoms**:
- No sound plays when new jobs are uploaded
- Sound toggle button doesn't seem to have any effect

**Possible Causes and Solutions**:

1. **Browser sound permissions**
   - Make sure the browser has permission to play audio
   - Check if the site is muted in your browser settings

2. **Sound toggle is off**
   - Click the sound toggle button to enable sound notifications
   - Verify the sound icon shows as enabled (not crossed out)

3. **Computer audio issues**
   - Verify computer speakers are working with other applications
   - Check volume controls and ensure audio is not muted system-wide

## SlicerOpener Protocol Handler Issues

### Protocol Handler Not Opening Files

**Symptoms**:
- Clicking "Open in Slicer" does nothing
- Browser shows an error about unknown protocol
- SlicerOpener error dialog appears

**Possible Causes and Solutions**:

1. **Protocol handler not properly registered**
   - Re-run the `register.bat` script as administrator
   - Verify the Windows registry entries for `3dprint://` protocol
   - Check for permission issues during installation

2. **Path configuration mismatch**
   - Ensure the `AUTHORITATIVE_STORAGE_BASE_PATH` in `config.ini` exactly matches the network share path
   - Verify the network share is mounted and accessible

3. **Slicer software configuration**
   - Check that the paths to slicer executables in `config.ini` are correct
   - Verify the slicer extensions list includes the file type you're trying to open
   - Ensure the slicer software is actually installed and working

4. **Network storage access issues**
   - Verify you can manually navigate to the file in Windows Explorer
   - Check if you have sufficient permissions to read files from the network storage

### Multiple Slicers Confusion

**Symptoms**:
- File opens in wrong slicer application
- No slicer selection dialog appears when expected

**Possible Causes and Solutions**:

1. **Configuration file issues**
   - Check the `config.ini` file to ensure all slicers are correctly defined
   - Verify file extensions are correctly associated with each slicer

2. **Dialog not appearing**
   - Check for error messages in the SlicerOpener log file
   - Verify the SlicerOpener application hasn't crashed (check Task Manager)

### Security Validation Errors

**Symptoms**:
- SlicerOpener shows a "Security validation failed" error dialog
- Log file shows security validation errors

**Possible Causes and Solutions**:

1. **Path traversal attempts**
   - Ensure the URL doesn't contain any suspicious path traversal elements (../, etc.)
   - Check if the file path is actually within the authorized storage path

2. **Permission issues**
   - Verify your user account has permission to read from the network storage

## Email Notification Problems

### Students Not Receiving Emails

**Symptoms**:
- Students report not getting approval/rejection emails
- Jobs stuck in PENDING status waiting for confirmation

**Possible Causes and Solutions**:

1. **Email configuration issues**
   - Verify email settings in the `.env` file
   - Check backend logs for email sending errors
   - Test email functionality with the command: `docker-compose exec backend flask test-mail`

2. **Emails going to spam/junk folders**
   - Ask students to check their spam/junk email folders
   - Consider adding sender domain to trusted senders list

3. **Worker process issues**
   - Check if the worker container is running: `docker-compose ps`
   - Look for errors in the worker logs: `docker-compose logs worker`
   - Verify Redis is running properly

### Expired Confirmation Links

**Symptoms**:
- Students report confirmation links not working
- Jobs show an "Expired confirmation" status

**Possible Causes and Solutions**:

1. **Token expiration**
   - Confirmation links expire after 72 hours
   - Staff can resend emails through the dashboard
   - Use the admin override to force-confirm if needed

2. **Token generation issues**
   - Check backend logs for errors during token generation
   - Verify the SECRET_KEY in environment variables is stable

## Job Status Issues

### Jobs Stuck in Status

**Symptoms**:
- Jobs remain in one status despite actions being taken
- Status changes but files don't move correctly
- Database and file system become unsynchronized

**Possible Causes and Solutions**:

1. **Process interruption**
   - Check event logs for the job to see if an operation was partially completed
   - Use the admin override to force the correct status if necessary

2. **File system permissions**
   - Ensure the backend container has write permissions to all storage directories
   - Check if the storage mount is working properly

3. **Database transaction issues**
   - Run the system health check to identify inconsistencies
   - Check the database logs for transaction errors

### Cannot Make Status Changes

**Symptoms**:
- Clicking status change buttons does nothing
- Status change attempts result in errors

**Possible Causes and Solutions**:

1. **Job locking issues**
   - Check if the job is locked by another user/session
   - If needed, an administrator can force-unlock via admin overrides
   - Wait for the lock to expire (5 minutes)

2. **Missing staff attribution**
   - Ensure you've selected your name from the staff dropdown in the modal
   - Verify your staff name is in the active staff list

3. **API communication errors**
   - Check network tab in browser developer tools
   - Look for specific error messages in the response

## Storage and File Management

### Missing Files

**Symptoms**:
- Jobs show "File not found" warnings
- SlicerOpener fails to find files that should exist

**Possible Causes and Solutions**:

1. **File system corruption**
   - Run system health check to identify inconsistencies
   - Use admin tools to identify and fix orphaned files and broken links

2. **Network storage disconnection**
   - Check if the network storage is properly mounted
   - Verify connectivity to the storage server

3. **Path mismatches**
   - Ensure the path in the database matches the actual file location
   - Check if files were manually moved outside the system

### Storage Space Issues

**Symptoms**:
- New uploads fail with storage errors
- System alerts showing low disk space

**Possible Causes and Solutions**:

1. **Running out of storage**
   - Archive older completed jobs (use administrator tools)
   - Add more storage space to the network volume

2. **Quotas or limits reached**
   - Check if any system quotas are in effect
   - Verify disk usage with command: `df -h`

3. **Temporary files accumulation**
   - Check for large temporary files that should be cleaned up
   - Run cleanup scripts if available

## Performance Issues

### Slow Dashboard Response

**Symptoms**:
- Dashboard takes a long time to load
- Operations like approving or rejecting jobs are sluggish

**Possible Causes and Solutions**:

1. **Database performance**
   - Check if the database has grown too large
   - Run database maintenance operations (see admin guide)

2. **Large number of jobs**
   - Consider archiving older jobs
   - Use filters to limit the number of jobs displayed

3. **Network latency**
   - Check network connectivity between user computer and server
   - Verify there are no bandwidth limitations in effect

### File Preview Generation Issues

**Symptoms**:
- Thumbnails don't appear for some jobs
- Placeholder images shown instead of actual previews

**Possible Causes and Solutions**:

1. **Thumbnail generation failures**
   - Check worker logs for errors during thumbnail processing
   - Verify the model file is valid and can be properly rendered

2. **Worker queue backlog**
   - Check the status of the worker queue
   - Consider restarting the worker container if it seems stuck

## Administrative Tasks

### System Health Check Issues

**Symptoms**:
- System health check reports inconsistencies
- Jobs showing in incorrect directories

**Possible Causes and Solutions**:

1. **Manual file operations**
   - Avoid manually moving files outside the application
   - Use the provided admin tools for file management

2. **Interrupted processes**
   - Review event logs to identify when synchronization was lost
   - Use admin tools to resolve inconsistencies

### Staff Management Problems

**Symptoms**:
- Cannot add new staff members
- Staff names not appearing in attribution dropdown

**Possible Causes and Solutions**:

1. **Database access issues**
   - Check backend logs for errors during staff list operations
   - Verify database permissions

2. **Frontend cache**
   - Try refreshing the page to fetch latest staff list
   - Clear browser cache if needed

3. **API errors**
   - Check network requests in browser developer tools
   - Look for specific error messages in responses

## Database Maintenance

**When to Perform Maintenance**:
- System performance has degraded over time
- After several months of continuous operation
- When disk space usage has grown significantly

**Maintenance Tasks**:
1. Create a backup before any maintenance: `docker-compose exec db pg_dump -U user 3dprint_dashboard > backup.sql`
2. Run VACUUM ANALYZE: `docker-compose exec db psql -U user -d 3dprint_dashboard -c "VACUUM ANALYZE;"`
3. Check for database bloat: `docker-compose exec db psql -U user -d 3dprint_dashboard -c "SELECT pg_size_pretty(pg_database_size('3dprint_dashboard'));"`

## Getting Help

If issues persist after trying the solutions in this guide:

1. **Gather Information**:
   - Take screenshots of any error messages
   - Export relevant logs: `docker-compose logs > system_logs.txt`
   - Document the exact steps that lead to the issue

2. **Contact Support**:
   - Email: [support email]
   - Include all gathered information
   - Specify the urgency of the issue

3. **Emergency Procedures**:
   - For critical issues affecting lab operations, call: [emergency contact]
   - For immediate system recovery, follow the backup restoration procedure in the administrator guide 