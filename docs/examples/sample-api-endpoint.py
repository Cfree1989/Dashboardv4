# Sample Flask API Endpoint - Job Approval Workflow
"""
This example demonstrates the standard pattern for API endpoints in the 3D Print Management System.
Key patterns: Authentication, staff attribution, event logging, file operations, error handling.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import Job, Event, db
from app.services.file_service import move_job_file_safely
from app.services.email_service import send_approval_email
from app.utils.decorators import require_staff_attribution
from app.utils.validators import validate_approval_params
import logging

# Create Blueprint for job-related endpoints
bp = Blueprint('jobs', __name__, url_prefix='/api/v1/jobs')
logger = logging.getLogger(__name__)


@bp.route('/<job_id>/approve', methods=['POST'])
@jwt_required()  # Require workstation JWT token
@require_staff_attribution  # Ensure staff_name in request body
def approve_job(job_id):
    """
    Approve a submitted job and transition to PENDING status.
    
    Required request body:
    {
        "weight_g": 25.5,
        "time_hours": 3.0,
        "authoritative_file": "filename.stl",
        "staff_name": "Jane Doe"
    }
    
    Returns:
        200: Updated job object
        400: Validation errors
        404: Job not found
        409: Job in wrong status or locked by another user
    """
    try:
        # Get workstation info from JWT
        workstation_id = get_jwt_identity()
        
        # Parse and validate request data
        data = request.get_json() or {}
        validation_result = validate_approval_params(data)
        if not validation_result.valid:
            return jsonify({
                "error": "validation_failed",
                "message": "Invalid approval parameters",
                "details": validation_result.errors
            }), 400
        
        # Find the job and verify it exists
        job = Job.query.get(job_id)
        if not job:
            logger.warning(f"Approval attempted for non-existent job: {job_id}")
            return jsonify({
                "error": "job_not_found",
                "message": "Job not found"
            }), 404
        
        # Verify job is in correct status for approval
        if job.status != 'UPLOADED':
            return jsonify({
                "error": "invalid_status",
                "message": f"Job must be in UPLOADED status, currently {job.status}"
            }), 409
        
        # Check if job is locked by another user
        if job.is_locked() and not job.is_locked_by_current_user():
            return jsonify({
                "error": "job_locked",
                "message": "Job is currently being edited by another user",
                "locked_by": job.locked_by_user
            }), 409
        
        # Extract validated parameters
        weight_g = validation_result.data['weight_g']
        time_hours = validation_result.data['time_hours']
        authoritative_file = validation_result.data['authoritative_file']
        staff_name = validation_result.data['staff_name']
        
        # Calculate cost based on material and weight
        cost_usd = calculate_print_cost(weight_g, job.material)
        
        # Perform approval workflow within database transaction
        with db.session.begin():
            # Update job with approval parameters
            job.weight_g = weight_g
            job.time_hours = time_hours
            job.cost_usd = cost_usd
            job.status = 'PENDING'
            job.last_updated_by = staff_name
            
            # Create event log entry for approval
            approval_event = Event(
                job_id=job.id,
                event_type='StaffApproved',
                triggered_by=staff_name,
                workstation_id=workstation_id,
                details={
                    'weight_g': weight_g,
                    'time_hours': time_hours,
                    'cost_usd': float(cost_usd),
                    'authoritative_file': authoritative_file
                }
            )
            db.session.add(approval_event)
            
            # Generate confirmation token for student email
            job.generate_confirmation_token()
        
        # Move job file to Pending directory (outside transaction)
        try:
            move_job_file_safely(job, 'PENDING', authoritative_file)
        except Exception as e:
            logger.error(f"File operation failed for job {job_id}: {str(e)}")
            # Rollback job status if file operation fails
            job.status = 'UPLOADED'
            db.session.commit()
            return jsonify({
                "error": "file_operation_failed",
                "message": "Could not move job file, approval cancelled"
            }), 500
        
        # Release job lock if held
        if job.is_locked():
            job.release_lock()
        
        # Queue approval email to student (async)
        send_approval_email.delay(job.id, job.confirm_token)
        
        logger.info(f"Job {job_id} approved by {staff_name} from {workstation_id}")
        
        # Return updated job object
        return jsonify({
            "success": True,
            "data": {
                "job": job.to_dict(),
                "message": "Job approved successfully"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Unexpected error approving job {job_id}: {str(e)}")
        return jsonify({
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }), 500


def calculate_print_cost(weight_g: float, material: str) -> float:
    """
    Calculate print cost based on weight and material type.
    
    Args:
        weight_g: Weight in grams
        material: 'filament' or 'resin'
        
    Returns:
        Cost in USD with $3.00 minimum
    """
    if material == 'filament':
        cost = weight_g * 0.10  # $0.10 per gram
    elif material == 'resin':
        cost = weight_g * 0.20  # $0.20 per gram
    else:
        raise ValueError(f"Unknown material type: {material}")
    
    # Apply minimum charge
    return max(cost, 3.00)


# Additional helper endpoints following same patterns

@bp.route('/<job_id>/reject', methods=['POST'])
@jwt_required()
@require_staff_attribution
def reject_job(job_id):
    """Reject a job with reasons - follows same authentication/logging pattern."""
    # Implementation follows similar structure to approve_job
    pass


@bp.route('/<job_id>/mark-printing', methods=['POST'])
@jwt_required()
@require_staff_attribution  
def mark_job_printing(job_id):
    """Mark job as printing - simpler status transition."""
    # Implementation follows similar structure with status validation
    pass