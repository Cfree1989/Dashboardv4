# SlicerOpener Protocol Handler Guide

This guide explains how to install, configure, and use the SlicerOpener protocol handler to open 3D model files directly from the dashboard.

## What is the SlicerOpener Protocol Handler?

The SlicerOpener is a custom protocol handler that enables staff to open 3D model files directly from the web dashboard in their preferred slicer software with a single click. When you click "Open in Slicer" on a job card, the SlicerOpener handles the `3dprint://` protocol URL and opens the correct file in the appropriate application.

## Installation Instructions

### Prerequisites

- Windows 7, 8, 10, or 11
- Administrative privileges on your computer
- Slicer software installed (PrusaSlicer, Cura, etc.)
- Access to the shared network drive where job files are stored

### Installation Steps

1. **Download the SlicerOpener Package**
   - Obtain the SlicerOpener package from your system administrator
   - The package should contain:
     - `SlicerOpener.exe` (the compiled protocol handler)
     - `SlicerOpener.py` (source code, for reference)
     - `config.ini.example` (template configuration file)
     - `register.bat` (Windows registry script)

2. **Place Files in a Permanent Location**
   - Create a folder for the application (e.g., `C:\Program Files\SlicerOpener\`)
   - Copy `SlicerOpener.exe` and `SlicerOpener.py` to this folder

3. **Create Configuration File**
   - Copy `config.ini.example` to `config.ini` in the same folder
   - Edit `config.ini` to specify:
     - The base path to the shared storage (`AUTHORITATIVE_STORAGE_BASE_PATH`)
     - The installed slicer software on your computer

4. **Register the Protocol Handler**
   - Right-click `register.bat` and select "Run as administrator"
   - This script will register the `3dprint://` protocol with your Windows registry
   - You should see a confirmation message when complete

### Configuration File Setup

The `config.ini` file must be correctly configured for your specific workstation. Here's a sample configuration:

```ini
[main]
AUTHORITATIVE_STORAGE_BASE_PATH=Z:\storage
LOG_PATH=C:\Program Files\SlicerOpener\slicer_opener.log

[slicer_prusaslicer]
name=PrusaSlicer
path=C:\Program Files\Prusa3D\PrusaSlicer\prusa-slicer.exe
extensions=.stl,.obj,.3mf,.amf

[slicer_cura]
name=Ultimaker Cura
path=C:\Program Files\Ultimaker Cura\Cura.exe
extensions=.stl,.obj,.3mf,.x3d,.gcode
```

**Configuration Sections:**

1. **main** section:
   - `AUTHORITATIVE_STORAGE_BASE_PATH`: Must match the exact path where the shared storage is mounted on your computer
   - `LOG_PATH`: Path where the log file will be created

2. **slicer_** sections (one for each installed slicer):
   - `name`: Display name of the slicer software
   - `path`: Full path to the slicer executable
   - `extensions`: Comma-separated list of file extensions this slicer can open

**Important**: The storage path must be identical across all workstations. For example, if the storage is mounted at `Z:\storage\` on one computer, it must be mounted at the exact same path on all others.

## How to Use

Once installed, using the SlicerOpener is simple:

1. Browse to the dashboard in your web browser
2. Find a job card with a 3D model file
3. Click the "Open in Slicer" button
4. If this is your first time using the protocol:
   - Your browser may ask permission to use the external protocol
   - Select "Remember my choice" and "Allow"
5. SlicerOpener will:
   - Validate the file path for security
   - Find compatible slicers based on the file extension
   - Open the file in the appropriate slicer application
   - Show confirmation or error messages as needed

### Multiple Slicer Support

If you have multiple compatible slicers installed for a specific file type:

1. When clicking "Open in Slicer" for a compatible file
2. SlicerOpener will display a selection dialog
3. Choose which slicer you want to use for this file
4. The file will open in your chosen slicer

## Troubleshooting

### Common Issues and Solutions

#### "Protocol Handler Not Found" Error

**Symptom**: Clicking "Open in Slicer" does nothing or shows "Protocol Not Registered" in the browser.

**Solutions**:
- Verify the protocol handler is correctly registered:
  - Re-run `register.bat` as administrator
  - Check for 3dprint:// protocol in Windows registry

#### "File Not Found" Error

**Symptom**: SlicerOpener shows an error dialog saying the file could not be found.

**Solutions**:
- Check the network storage is properly mounted at the configured path
- Verify the `AUTHORITATIVE_STORAGE_BASE_PATH` in `config.ini` matches the actual mount point
- Ensure network connectivity to the shared storage

#### "No Compatible Slicer Found" Error

**Symptom**: SlicerOpener shows an error dialog saying no compatible slicer was found.

**Solutions**:
- Verify the slicer path in `config.ini` is correct
- Check that the file extension is in the slicer's supported extensions list
- Ensure the slicer software is actually installed at the specified path

#### "Security Validation Failed" Error

**Symptom**: SlicerOpener shows an error dialog about security validation.

**Solutions**:
- This indicates a potential security issue - the file path is not within the authorized storage location
- Verify the `AUTHORITATIVE_STORAGE_BASE_PATH` setting is correct
- Contact your system administrator if the problem persists

### Advanced Troubleshooting

For persistent issues:

1. Check the SlicerOpener log file (location defined in `config.ini`)
2. Look for specific error messages or exceptions
3. Verify file permissions - ensure your user account has read access to the shared storage
4. Try reinstalling the protocol handler
5. Contact your system administrator with the log file for assistance

## Updating SlicerOpener

When a new version of SlicerOpener is released:

1. Close any open slicer software
2. Replace the existing `SlicerOpener.exe` and `SlicerOpener.py` files with the new versions
3. Re-run the `register.bat` script as administrator
4. Your configuration file (`config.ini`) should be preserved

## Security Considerations

SlicerOpener includes several security features:

- **Path Validation**: Only allows opening files within the authorized storage directory
- **Protocol Security**: URLs must follow the correct format (`3dprint://open?path=...`)
- **Error Handling**: Displays clear error messages for any issues
- **Logging**: All actions and security validations are logged for troubleshooting

Report any security concerns to your system administrator immediately. 