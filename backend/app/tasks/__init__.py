# Background Tasks Package for 3D Print Management System
"""
Background task processing using RQ (Redis Queue) for:
- Email notifications
- File processing
- Thumbnail generation
- Periodic cleanup tasks
"""

from .email_tasks import *