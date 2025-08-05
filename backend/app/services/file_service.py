# File Service - 3D Print Management System
"""
Comprehensive file management service for 3D print job files.
Handles uploads, moves, metadata creation, and file integrity operations.
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import current_app


class FileServiceError(Exception):
    """Base exception for file service operations."""
    pass


class FileValidationError(FileServiceError):
    """Exception for file validation failures."""
    pass


class FileOperationError(FileServiceError):
    """Exception for file operation failures."""
    pass


class FileService:
    """
    Comprehensive file management service for 3D print jobs.
    
    Provides file validation, upload processing, metadata management,
    and status-based file movement operations.
    """
    
    # Allowed file extensions for uploads
    ALLOWED_EXTENSIONS = {'.stl', '.obj', '.3mf'}
    
    # Slicer file extensions for authoritative file detection
    SLICER_EXTENSIONS = {'.3mf', '.form', '.gcode', '.idea'}
    
    # Maximum file size (50MB)
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def __init__(self, storage_base_path: str = None):
        """
        Initialize file service.
        
        Args:
            storage_base_path: Base path for file storage (defaults to config)
        """
        self._storage_base_path = storage_base_path  # Store for later resolution
        self._storage_path = None
        self._initialized = False
    
    def _initialize_storage(self):
        """Initialize storage paths and directories (lazy initialization)."""
        if not self._initialized:
            from flask import current_app
            self.storage_base_path = self._storage_base_path or current_app.config.get('STORAGE_BASE_PATH', './storage')
            self.storage_path = Path(self.storage_base_path)
            self._ensure_storage_directories()
            self._initialized = True
    
    def _ensure_storage_directories(self):
        """Create storage directories if they don't exist."""
        directories = [
            'Uploaded', 'Pending', 'ReadyToPrint', 'Printing',
            'Completed', 'PaidPickedUp', 'Archived'
        ]
        
        for directory in directories:
            dir_path = self.storage_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file: FileStorage) -> Dict[str, Any]:
        """
        Validate uploaded file for security and format compliance.
        
        Args:
            file: Werkzeug FileStorage object
            
        Returns:
            Dict with validation results
            
        Raises:
            FileValidationError: If validation fails
        """
        self._initialize_storage()
        
        if not file or not file.filename:
            raise FileValidationError("No file provided")
        
        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = Path(filename).suffix.lower()
        
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise FileValidationError(
                f"File type '{file_ext}' not allowed. "
                f"Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File size ({file_size} bytes) exceeds maximum allowed "
                f"({self.MAX_FILE_SIZE} bytes)"
            )
        
        if file_size == 0:
            raise FileValidationError("File is empty")
        
        return {
            'original_filename': file.filename,
            'secure_filename': filename,
            'file_extension': file_ext,
            'file_size': file_size,
            'is_valid': True
        }
    
    def calculate_file_hash(self, file: FileStorage) -> str:
        """
        Calculate SHA-256 hash of file content for duplicate detection.
        
        Args:
            file: Werkzeug FileStorage object
            
        Returns:
            Hex string of SHA-256 hash
        """
        hasher = hashlib.sha256()
        file.seek(0)
        
        # Read file in chunks to handle large files
        while chunk := file.read(8192):
            hasher.update(chunk)
        
        file.seek(0)  # Reset file pointer
        return hasher.hexdigest()
    
    def generate_display_name(self, student_name: str, print_method: str, 
                            color: str, job_id: str, original_filename: str) -> str:
        """
        Generate standardized display name for job files.
        
        Format: FirstAndLastName_PrintMethod_Color_SimpleJobID.original_extension
        
        Args:
            student_name: Student's full name
            print_method: 'filament' or 'resin'
            color: Selected color
            job_id: Job UUID
            original_filename: Original uploaded filename
            
        Returns:
            Standardized display name
        """
        # Clean and format student name (remove spaces, special chars)
        clean_name = ''.join(c for c in student_name if c.isalnum())
        
        # Get file extension
        extension = Path(original_filename).suffix
        
        # Generate simple job ID (first 6 chars of UUID)
        simple_id = job_id[:6]
        
        # Capitalize print method and color
        method = print_method.capitalize()
        color_clean = color.replace(' ', '')
        
        return f"{clean_name}_{method}_{color_clean}_{simple_id}{extension}"
    
    def create_metadata_json(self, job_data: Dict[str, Any], file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create metadata.json content for job file.
        
        Args:
            job_data: Job information from database
            file_info: File validation information
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            'job_id': job_data['id'],
            'student_info': {
                'name': job_data['student_name'],
                'email': job_data['student_email'],
                'discipline': job_data['discipline'],
                'class_number': job_data['class_number']
            },
            'file_info': {
                'original_filename': file_info['original_filename'],
                'display_name': job_data['display_name'],
                'file_size': file_info['file_size'],
                'file_hash': job_data.get('file_hash'),
                'file_extension': file_info['file_extension']
            },
            'job_config': {
                'status': job_data['status'],
                'printer': job_data['printer'],
                'color': job_data['color'],
                'material': job_data['material'],
                'weight_g': job_data.get('weight_g'),
                'time_hours': job_data.get('time_hours'),
                'cost_usd': float(job_data['cost_usd']) if job_data.get('cost_usd') else None
            },
            'timestamps': {
                'created_at': job_data['created_at'].isoformat() if hasattr(job_data['created_at'], 'isoformat') else job_data['created_at'],
                'updated_at': job_data['updated_at'].isoformat() if hasattr(job_data['updated_at'], 'isoformat') else job_data['updated_at'],
                'metadata_created_at': datetime.utcnow().isoformat()
            }
        }
        
        return metadata
    
    def save_uploaded_file(self, file: FileStorage, job_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Save uploaded file to Uploaded directory with metadata.
        
        Args:
            file: Werkzeug FileStorage object
            job_data: Job information from database
            
        Returns:
            Tuple of (file_path, metadata_path)
            
        Raises:
            FileOperationError: If save operation fails
        """
        self._initialize_storage()
        
        try:
            # Validate file first
            file_info = self.validate_file(file)
            
            # Create file paths
            display_name = job_data['display_name']
            uploaded_dir = self.storage_path / 'Uploaded'
            file_path = uploaded_dir / display_name
            metadata_path = uploaded_dir / f"{display_name}.metadata.json"
            
            # Ensure directory exists
            uploaded_dir.mkdir(parents=True, exist_ok=True)
            
            # Save the file
            file.save(str(file_path))
            current_app.logger.info(f"Saved file to: {file_path}")
            
            # Create and save metadata
            metadata = self.create_metadata_json(job_data, file_info)
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            current_app.logger.info(f"Created metadata: {metadata_path}")
            
            return str(file_path), str(metadata_path)
            
        except Exception as e:
            current_app.logger.error(f"Error saving uploaded file: {str(e)}")
            raise FileOperationError(f"Failed to save uploaded file: {str(e)}")
    
    def move_job_files(self, old_status: str, new_status: str, job_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Move job files between status directories using copy-update-delete pattern.
        
        Args:
            old_status: Current job status (directory name)
            new_status: New job status (directory name)
            job_data: Job information with current file paths
            
        Returns:
            Tuple of (new_file_path, new_metadata_path)
            
        Raises:
            FileOperationError: If move operation fails
        """
        try:
            # Convert status to directory names (UPPERCASE -> PascalCase)
            old_dir = self._status_to_directory(old_status)
            new_dir = self._status_to_directory(new_status)
            
            # Get current file paths
            current_file_path = Path(job_data['file_path'])
            current_metadata_path = Path(job_data['metadata_path'])
            
            # Create new file paths
            display_name = job_data['display_name']
            new_file_path = self.storage_path / new_dir / display_name
            new_metadata_path = self.storage_path / new_dir / f"{display_name}.metadata.json"
            
            # Ensure destination directory exists
            (self.storage_path / new_dir).mkdir(parents=True, exist_ok=True)
            
            # Copy files to new location
            if current_file_path.exists():
                shutil.copy2(current_file_path, new_file_path)
                current_app.logger.info(f"Copied file: {current_file_path} -> {new_file_path}")
            else:
                current_app.logger.warning(f"Source file not found: {current_file_path}")
            
            if current_metadata_path.exists():
                # Update metadata with new status
                metadata = self._load_metadata(current_metadata_path)
                metadata['job_config']['status'] = new_status
                metadata['timestamps']['last_moved_at'] = datetime.utcnow().isoformat()
                metadata['file_info']['moved_from'] = str(current_file_path)
                
                # Save updated metadata
                with open(new_metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                current_app.logger.info(f"Updated metadata: {new_metadata_path}")
            
            # Delete original files (completing copy-update-delete pattern)
            try:
                if current_file_path.exists():
                    current_file_path.unlink()
                    current_app.logger.info(f"Deleted original file: {current_file_path}")
                
                if current_metadata_path.exists():
                    current_metadata_path.unlink()
                    current_app.logger.info(f"Deleted original metadata: {current_metadata_path}")
            except Exception as e:
                current_app.logger.warning(f"Error deleting original files: {str(e)}")
                # Don't raise error here - move was successful, cleanup failed
            
            return str(new_file_path), str(new_metadata_path)
            
        except Exception as e:
            current_app.logger.error(f"Error moving job files: {str(e)}")
            raise FileOperationError(f"Failed to move job files: {str(e)}")
    
    def find_candidate_files(self, job_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find all potential authoritative files for a job in its current directory.
        
        Args:
            job_data: Job information with current file path
            
        Returns:
            List of file information dictionaries
        """
        try:
            current_file_path = Path(job_data['file_path'])
            job_directory = current_file_path.parent
            job_id = job_data['id']
            
            candidates = []
            
            # Look for files that might belong to this job
            if job_directory.exists():
                for file_path in job_directory.iterdir():
                    if file_path.is_file() and not file_path.name.endswith('.metadata.json'):
                        # Check if file is related to this job (contains job ID or similar name pattern)
                        if (job_id[:6] in file_path.name or 
                            file_path.name.startswith(job_data['display_name'].split('_')[0])):
                            
                            stat = file_path.stat()
                            candidates.append({
                                'filename': file_path.name,
                                'full_path': str(file_path),
                                'size': stat.st_size,
                                'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                'is_original': file_path.name == job_data['display_name'],
                                'is_slicer_file': file_path.suffix.lower() in self.SLICER_EXTENSIONS,
                                'extension': file_path.suffix.lower()
                            })
            
            # Sort by modification time (newest first) and prioritize slicer files
            candidates.sort(key=lambda x: (not x['is_slicer_file'], x['modified_at']), reverse=True)
            
            return candidates
            
        except Exception as e:
            current_app.logger.error(f"Error finding candidate files: {str(e)}")
            return []
    
    def delete_job_files(self, job_data: Dict[str, Any]) -> bool:
        """
        Permanently delete job files and metadata.
        
        Args:
            job_data: Job information with file paths
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = Path(job_data['file_path'])
            metadata_path = Path(job_data['metadata_path'])
            
            deleted_files = []
            
            # Delete main file
            if file_path.exists():
                file_path.unlink()
                deleted_files.append(str(file_path))
            
            # Delete metadata
            if metadata_path.exists():
                metadata_path.unlink()
                deleted_files.append(str(metadata_path))
            
            current_app.logger.info(f"Deleted job files: {deleted_files}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error deleting job files: {str(e)}")
            return False
    
    def _status_to_directory(self, status: str) -> str:
        """Convert job status to directory name."""
        status_mapping = {
            'UPLOADED': 'Uploaded',
            'PENDING': 'Pending',
            'READYTOPRINT': 'ReadyToPrint',
            'PRINTING': 'Printing',
            'COMPLETED': 'Completed',
            'PAIDPICKEDUP': 'PaidPickedUp',
            'REJECTED': 'Rejected',
            'ARCHIVED': 'Archived'
        }
        return status_mapping.get(status, status)
    
    def _load_metadata(self, metadata_path: Path) -> Dict[str, Any]:
        """Load metadata from JSON file."""
        try:
            with open(metadata_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.warning(f"Error loading metadata from {metadata_path}: {str(e)}")
            return {}
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage usage information.
        
        Returns:
            Dictionary with storage statistics
        """
        self._initialize_storage()
        
        try:
            storage_info = {
                'base_path': str(self.storage_path),
                'directories': {},
                'total_files': 0,
                'total_size': 0
            }
            
            for status_dir in ['Uploaded', 'Pending', 'ReadyToPrint', 'Printing', 
                              'Completed', 'PaidPickedUp', 'Archived']:
                dir_path = self.storage_path / status_dir
                if dir_path.exists():
                    files = list(dir_path.glob('*'))
                    model_files = [f for f in files if not f.name.endswith('.metadata.json')]
                    
                    dir_size = sum(f.stat().st_size for f in files if f.is_file())
                    
                    storage_info['directories'][status_dir] = {
                        'file_count': len(model_files),
                        'total_files': len(files),
                        'size_bytes': dir_size
                    }
                    
                    storage_info['total_files'] += len(model_files)
                    storage_info['total_size'] += dir_size
            
            return storage_info
            
        except Exception as e:
            current_app.logger.error(f"Error getting storage info: {str(e)}")
            return {'error': str(e)}


# Global file service instance
file_service = FileService()