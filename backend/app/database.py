# Database instance - 3D Print Management System
"""
Centralized database instance to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()