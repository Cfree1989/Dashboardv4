# Authentication Utilities - 3D Print Management System
"""
JWT utilities and authentication middleware for workstation-based authentication.
Handles workstation token generation, validation, and staff attribution.
"""

import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app, g
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, 
    verify_jwt_in_request, get_jwt
)
from app.models.staff import Staff


# Workstation Configuration
def load_workstation_config():
    """
    Load workstation credentials from environment variables.
    Expected format: WORKSTATION_CREDENTIALS='{"front-desk": "password1", "lab-computer": "password2"}'
    """
    config_str = os.environ.get('WORKSTATION_CREDENTIALS')
    if not config_str:
        # Default development workstations
        return {
            'front-desk': 'dev-front-desk-pass',
            'lab-computer': 'dev-lab-computer-pass'
        }
    
    try:
        return json.loads(config_str)
    except json.JSONDecodeError:
        current_app.logger.error("Invalid WORKSTATION_CREDENTIALS format. Using defaults.")
        return {
            'front-desk': 'dev-front-desk-pass',
            'lab-computer': 'dev-lab-computer-pass'
        }


def validate_workstation_credentials(workstation_id, password):
    """
    Validate workstation ID and password against configured credentials.
    
    Args:
        workstation_id (str): Workstation identifier
        password (str): Workstation password
        
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    workstations = load_workstation_config()
    return workstations.get(workstation_id) == password


def create_workstation_token(workstation_id):
    """
    Create JWT token for workstation authentication.
    
    Args:
        workstation_id (str): Workstation identifier
        
    Returns:
        str: JWT token string
    """
    # Create token with workstation ID as identity
    additional_claims = {
        'workstation_id': workstation_id,
        'token_type': 'workstation',
        'created_at': datetime.utcnow().isoformat()
    }
    
    token = create_access_token(
        identity=workstation_id,
        additional_claims=additional_claims
    )
    
    return token


def validate_staff_name(staff_name):
    """
    Validate that staff name belongs to an active staff member.
    
    Args:
        staff_name (str): Staff member name to validate
        
    Returns:
        bool: True if staff name is valid and active, False otherwise
    """
    if not staff_name:
        return False
    
    return Staff.is_valid_staff_name(staff_name)


def require_workstation_auth(f):
    """
    Decorator to require workstation authentication for API endpoints.
    Sets g.workstation_id for use in the decorated function.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Verify JWT token
            verify_jwt_in_request()
            
            # Get workstation ID from token
            workstation_id = get_jwt_identity()
            claims = get_jwt()
            
            # Validate token type
            if claims.get('token_type') != 'workstation':
                return jsonify({
                    'error': 'invalid_token_type',
                    'message': 'Invalid token type. Workstation token required.'
                }), 401
            
            # Set workstation ID in Flask g object for use in handlers
            g.workstation_id = workstation_id
            
            return f(*args, **kwargs)
            
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'error': 'authentication_failed',
                'message': 'Authentication required'
            }), 401
    
    return decorated_function


def require_staff_attribution(f):
    """
    Decorator to require staff attribution for state-changing actions.
    Validates that 'staff_name' is provided in request JSON and is a valid active staff member.
    Sets g.staff_name for use in the decorated function.
    
    Must be used in combination with @require_workstation_auth.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Ensure workstation auth was already verified
        if not hasattr(g, 'workstation_id'):
            return jsonify({
                'error': 'authentication_required',
                'message': 'Workstation authentication required'
            }), 401
        
        # Get request JSON
        if not request.is_json:
            return jsonify({
                'error': 'invalid_content_type',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        staff_name = data.get('staff_name') if data else None
        
        # Validate staff name is provided
        if not staff_name:
            return jsonify({
                'error': 'staff_attribution_required',
                'message': 'staff_name is required for this action'
            }), 400
        
        # Validate staff name is active
        if not validate_staff_name(staff_name):
            return jsonify({
                'error': 'invalid_staff_name',
                'message': f'Staff member "{staff_name}" not found or inactive'
            }), 400
        
        # Set staff name in Flask g object
        g.staff_name = staff_name
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_token_info():
    """
    Get information about the current JWT token.
    
    Returns:
        dict: Token information including workstation_id, created_at, expires_at
    """
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        workstation_id = get_jwt_identity()
        
        return {
            'workstation_id': workstation_id,
            'token_type': claims.get('token_type'),
            'created_at': claims.get('created_at'),
            'expires_at': datetime.fromtimestamp(claims.get('exp')).isoformat() if claims.get('exp') else None
        }
    except Exception:
        return None


def extend_token(workstation_id):
    """
    Create a new token with extended expiration (token refresh).
    
    Args:
        workstation_id (str): Workstation identifier
        
    Returns:
        str: New JWT token string
    """
    return create_workstation_token(workstation_id)


# Utility function for creating audit trail events
def create_auth_event_data(action, details=None):
    """
    Create standardized event data for authentication-related actions.
    
    Args:
        action (str): Action type (e.g., 'WorkstationLogin', 'TokenRefresh')
        details (dict): Additional event details
        
    Returns:
        dict: Event data ready for Event model creation
    """
    event_data = {
        'event_type': action,
        'workstation_id': getattr(g, 'workstation_id', None),
        'triggered_by': getattr(g, 'staff_name', None),  # May be None for login events
        'details': details or {}
    }
    
    # Add timestamp to details
    event_data['details']['timestamp'] = datetime.utcnow().isoformat()
    
    if hasattr(g, 'workstation_id'):
        event_data['details']['workstation_id'] = g.workstation_id
    
    return event_data