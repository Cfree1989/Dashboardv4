# Authentication Routes - 3D Print Management System
"""
Workstation authentication endpoints.
Handles workstation login, logout, and JWT token management.
"""

from flask import Blueprint, request, jsonify, current_app, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.utils.auth import (
    validate_workstation_credentials, create_workstation_token,
    require_workstation_auth, get_token_info, extend_token,
    create_auth_event_data
)
from app.models.staff import Staff

bp = Blueprint('auth', __name__)

# Rate limiting for auth endpoints
limiter = Limiter(key_func=get_remote_address)


@bp.route('/login', methods=['POST'])
@limiter.limit("10 per hour")  # Brute force protection
def login():
    """
    Workstation login endpoint.
    
    Validates workstation credentials and returns JWT token for 12-hour session.
    """
    try:
        # Validate request format
        if not request.is_json:
            return jsonify({
                'error': 'invalid_content_type',
                'message': 'Content-Type must be application/json'
            }), 400
        
        data = request.get_json()
        
        # Extract and validate required fields
        workstation_id = data.get('workstation_id')
        password = data.get('password')
        
        if not workstation_id or not password:
            return jsonify({
                'error': 'missing_credentials',
                'message': 'workstation_id and password are required'
            }), 400
        
        # Validate workstation credentials
        if not validate_workstation_credentials(workstation_id, password):
            current_app.logger.warning(f"Failed login attempt for workstation: {workstation_id}")
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid workstation ID or password'
            }), 401
        
        # Create JWT token
        token = create_workstation_token(workstation_id)
        
        # Log successful login
        current_app.logger.info(f"Successful login for workstation: {workstation_id}")
        
        return jsonify({
            'token': token,
            'workstation_id': workstation_id,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds(),
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'error': 'login_failed',
            'message': 'Login failed due to server error'
        }), 500


@bp.route('/logout', methods=['POST'])
@require_workstation_auth
def logout():
    """
    Workstation logout endpoint.
    
    Note: JWT tokens are stateless, so logout is mainly for client-side cleanup.
    In a production system, you might implement token blacklisting.
    """
    try:
        workstation_id = g.workstation_id
        
        current_app.logger.info(f"Logout for workstation: {workstation_id}")
        
        return jsonify({
            'message': 'Logout successful',
            'workstation_id': workstation_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'error': 'logout_failed',
            'message': 'Logout failed due to server error'
        }), 500


@bp.route('/refresh', methods=['POST'])
@require_workstation_auth
def refresh_token():
    """
    Refresh workstation JWT token.
    
    Creates a new token with extended expiration time.
    """
    try:
        workstation_id = g.workstation_id
        
        # Create new token
        new_token = extend_token(workstation_id)
        
        current_app.logger.info(f"Token refreshed for workstation: {workstation_id}")
        
        return jsonify({
            'token': new_token,
            'workstation_id': workstation_id,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds(),
            'message': 'Token refreshed successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token refresh error: {str(e)}")
        return jsonify({
            'error': 'refresh_failed',
            'message': 'Token refresh failed due to server error'
        }), 500


@bp.route('/verify', methods=['GET'])
@require_workstation_auth
def verify_token():
    """
    Verify current JWT token and return token information.
    
    Useful for frontend to check if token is still valid.
    """
    try:
        token_info = get_token_info()
        
        return jsonify({
            'valid': True,
            'token_info': token_info,
            'message': 'Token is valid'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'error': 'verification_failed',
            'message': 'Token verification failed'
        }), 500


@bp.route('/staff', methods=['GET'])
@require_workstation_auth
def get_staff_list():
    """
    Get list of staff members for attribution dropdowns.
    
    Query parameters:
    - include_inactive: Include inactive staff members (default: false)
    """
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        
        staff_members = Staff.get_all_staff(include_inactive=include_inactive)
        
        staff_list = []
        for staff in staff_members:
            staff_data = staff.to_dict()
            # Add visual indicator for recently added staff (within 7 days)
            staff_data['is_recently_added'] = staff.days_since_added <= 7
            staff_list.append(staff_data)
        
        return jsonify({
            'staff': staff_list,
            'total': len(staff_list),
            'active_count': len([s for s in staff_list if s['is_active']])
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Staff list error: {str(e)}")
        return jsonify({
            'error': 'staff_list_failed',
            'message': 'Failed to retrieve staff list'
        }), 500


@bp.route('/workstations', methods=['GET'])
@require_workstation_auth
def get_workstation_info():
    """
    Get information about available workstations.
    
    Returns list of configured workstation IDs (without passwords).
    """
    try:
        from app.utils.auth import load_workstation_config
        
        workstations = load_workstation_config()
        workstation_ids = list(workstations.keys())
        
        return jsonify({
            'workstations': workstation_ids,
            'current_workstation': g.workstation_id,
            'total': len(workstation_ids)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Workstation info error: {str(e)}")
        return jsonify({
            'error': 'workstation_info_failed',
            'message': 'Failed to retrieve workstation information'
        }), 500