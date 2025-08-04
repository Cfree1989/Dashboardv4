# Job Management Routes - 3D Print Management System
"""
Job management API endpoints for staff dashboard operations.
Handles job listing, approval, rejection, status changes, and job locking.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, g
from sqlalchemy import or_, and_
from app.database import db
from app.models.job import Job
from app.models.event import Event
from app.models.staff import Staff
from app.utils.auth import require_workstation_auth, require_staff_attribution

bp = Blueprint('jobs', __name__)


@bp.route('', methods=['GET'])
@require_workstation_auth
def list_jobs():
    """
    List jobs with filtering and pagination.
    
    Query parameters:
    - status: Filter by job status (e.g., 'UPLOADED', 'PENDING')
    - search: Search in student name, email, display name
    - printer: Filter by printer name
    - discipline: Filter by student discipline  
    - confirmation_expired: Filter jobs with expired confirmation (true/false)
    - page: Page number (default: 1)
    - limit: Jobs per page (default: 50, max: 100)
    """
    try:
        # Parse query parameters
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        printer = request.args.get('printer')
        discipline = request.args.get('discipline')
        confirmation_expired = request.args.get('confirmation_expired', '').lower() == 'true'
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 50)), 100)
        
        # Build query
        query = Job.query
        
        # Status filter
        if status and status in Job.VALID_STATUSES:
            query = query.filter(Job.status == status)
        
        # Search filter (student name, email, display name)
        if search:
            search_term = f'%{search}%'
            query = query.filter(or_(
                Job.student_name.ilike(search_term),
                Job.student_email.ilike(search_term),
                Job.display_name.ilike(search_term)
            ))
        
        # Printer filter
        if printer:
            query = query.filter(Job.printer == printer)
        
        # Discipline filter
        if discipline:
            query = query.filter(Job.discipline == discipline)
        
        # Confirmation expired filter
        if confirmation_expired:
            query = query.filter(and_(
                Job.status == Job.STATUS_PENDING,
                Job.student_confirmed == False,
                Job.confirm_token_expires < db.func.now()
            ))
        
        # Order by creation date (newest first)
        query = query.order_by(Job.created_at.desc())
        
        # Pagination
        offset = (page - 1) * limit
        total = query.count()
        jobs = query.offset(offset).limit(limit).all()
        
        # Convert to dictionaries
        jobs_data = []
        for job in jobs:
            job_dict = job.to_dict()
            # Add computed fields for dashboard
            job_dict['needs_review'] = (job.status == Job.STATUS_UPLOADED and 
                                       job.staff_viewed_at is None)
            job_dict['age_hours'] = (datetime.utcnow() - job.created_at).total_seconds() / 3600
            jobs_data.append(job_dict)
        
        return jsonify({
            'jobs': jobs_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit,
                'has_next': offset + limit < total,
                'has_prev': page > 1
            },
            'filters_applied': {
                'status': status,
                'search': search if search else None,
                'printer': printer,
                'discipline': discipline,
                'confirmation_expired': confirmation_expired
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'error': 'invalid_parameters',
            'message': f'Invalid query parameters: {str(e)}'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error listing jobs: {str(e)}")
    return jsonify({
            'error': 'list_jobs_failed',
            'message': 'Failed to retrieve jobs'
        }), 500


@bp.route('/<job_id>', methods=['GET'])
@require_workstation_auth
def get_job(job_id):
    """Get specific job details with full event history."""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Return full job details including events
        job_data = job.to_dict(include_events=True)
        
        return jsonify(job_data), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting job {job_id}: {str(e)}")
        return jsonify({
            'error': 'get_job_failed',
            'message': 'Failed to retrieve job details'
        }), 500


@bp.route('/<job_id>/lock', methods=['POST'])
@require_workstation_auth
def lock_job(job_id):
    """
    Acquire exclusive lock on a job to prevent concurrent edits.
    
    Body (optional):
    - duration_minutes: Lock duration in minutes (default: 5, max: 30)
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Parse request data
        data = request.get_json() or {}
        duration_minutes = min(int(data.get('duration_minutes', 5)), 30)
        
        # Try to acquire lock
        if job.lock('system', g.workstation_id, duration_minutes):
            db.session.commit()
            
            current_app.logger.info(f"Job {job_id} locked by workstation {g.workstation_id}")
            
            return jsonify({
                'message': 'Job locked successfully',
                'locked_until': job.locked_until.isoformat(),
                'locked_by_workstation': g.workstation_id
            }), 200
        else:
            return jsonify({
                'error': 'job_already_locked',
                'message': 'Job is currently locked by another user',
                'locked_by_workstation': job.locked_workstation,
                'locked_until': job.locked_until.isoformat() if job.locked_until else None
            }), 409
            
    except ValueError as e:
        return jsonify({
            'error': 'invalid_parameters',
            'message': str(e)
        }), 400
    except Exception as e:
        current_app.logger.error(f"Error locking job {job_id}: {str(e)}")
        return jsonify({
            'error': 'lock_job_failed',
            'message': 'Failed to lock job'
        }), 500


@bp.route('/<job_id>/unlock', methods=['POST'])
@require_workstation_auth  
def unlock_job(job_id):
    """Release exclusive lock on a job."""
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Check if job is locked by this workstation
        if job.is_locked() and job.locked_workstation != g.workstation_id:
            return jsonify({
                'error': 'not_lock_owner',
                'message': 'You cannot unlock a job locked by another workstation',
                'locked_by_workstation': job.locked_workstation
            }), 403
        
        # Release lock
        job.unlock()
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} unlocked by workstation {g.workstation_id}")
        
        return jsonify({
            'message': 'Job unlocked successfully'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error unlocking job {job_id}: {str(e)}")
    return jsonify({
            'error': 'unlock_job_failed',
            'message': 'Failed to unlock job'
        }), 500


@bp.route('/<job_id>/approve', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def approve_job(job_id):
    """
    Approve a job for printing.
    
    Requires staff attribution and job lock.
    Body must include: weight_g, time_hours, and authoritative_file.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Validate job status
        if not job.can_transition_to(Job.STATUS_PENDING):
            return jsonify({
                'error': 'invalid_status_transition',
                'message': f'Cannot approve job in {job.status} status'
            }), 400
        
        # Check job lock
        if not job.is_locked() or job.locked_workstation != g.workstation_id:
            return jsonify({
                'error': 'job_not_locked',
                'message': 'Job must be locked before approval'
            }), 400
        
        # Parse request data
        data = request.get_json()
        required_fields = ['weight_g', 'time_hours', 'authoritative_file']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'missing_required_field',
                    'message': f'Field {field} is required'
                }), 400
        
        # Validate numeric fields
        try:
            weight_g = float(data['weight_g'])
            time_hours = float(data['time_hours'])
            if weight_g <= 0 or time_hours <= 0:
                raise ValueError("Weight and time must be positive")
        except (ValueError, TypeError):
            return jsonify({
                'error': 'invalid_numeric_values',
                'message': 'weight_g and time_hours must be positive numbers'
            }), 400
        
        # Update job with approval data
        job.weight_g = weight_g
        job.time_hours = time_hours
        job.update_cost()  # Calculate cost based on weight and material
        job.status = Job.STATUS_PENDING
        job.last_updated_by = g.staff_name
        job.staff_viewed_at = datetime.utcnow()
        
        # Generate confirmation token for student
        job.generate_confirmation_token()
        
        # Move files to Pending directory
        from app.services.file_service import file_service, FileOperationError
        try:
            new_file_path, new_metadata_path = file_service.move_job_files(
                old_status=Job.STATUS_UPLOADED,
                new_status=Job.STATUS_PENDING,
                job_data=job.to_dict()
            )
            job.file_path = new_file_path
            job.metadata_path = new_metadata_path
        except FileOperationError as e:
            db.session.rollback()
            current_app.logger.error(f"Error moving files for job {job_id}: {str(e)}")
            return jsonify({
                'error': 'file_move_failed',
                'message': 'Failed to move job files during approval'
            }), 500
        
        # Release lock
        job.unlock()
        
        # Create approval event
        approval_event = Event(
            job_id=job.id,
            event_type='JobApproved',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'weight_g': weight_g,
                'time_hours': time_hours,
                'cost_usd': float(job.cost_usd),
                'authoritative_file': data['authoritative_file'],
                'confirmation_token_generated': True
            }
        )
        db.session.add(approval_event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} approved by {g.staff_name} on {g.workstation_id}")
        
        return jsonify({
            'message': 'Job approved successfully',
            'job': job.to_dict(),
            'confirmation_token': job.confirm_token  # For email sending
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving job {job_id}: {str(e)}")
    return jsonify({
            'error': 'approve_job_failed',
            'message': 'Failed to approve job'
        }), 500


@bp.route('/<job_id>/reject', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def reject_job(job_id):
    """
    Reject a job submission.
    
    Requires staff attribution and job lock.
    Body must include rejection reasons.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Validate job status
        if not job.can_transition_to(Job.STATUS_REJECTED):
            return jsonify({
                'error': 'invalid_status_transition',
                'message': f'Cannot reject job in {job.status} status'
            }), 400
        
        # Check job lock
        if not job.is_locked() or job.locked_workstation != g.workstation_id:
            return jsonify({
                'error': 'job_not_locked',
                'message': 'Job must be locked before rejection'
            }), 400
        
        # Parse request data
        data = request.get_json()
        reasons = data.get('reasons', [])
        custom_reason = data.get('custom_reason', '').strip()
        
        if not reasons and not custom_reason:
            return jsonify({
                'error': 'rejection_reason_required',
                'message': 'At least one rejection reason is required'
            }), 400
        
        # Update job with rejection data
        job.status = Job.STATUS_REJECTED
        job.reject_reasons = {
            'reasons': reasons,
            'custom_reason': custom_reason,
            'rejected_by': g.staff_name,
            'rejected_at': datetime.utcnow().isoformat()
        }
        job.last_updated_by = g.staff_name
        job.staff_viewed_at = datetime.utcnow()
        
        # Release lock
        job.unlock()
        
        # Create rejection event
        rejection_event = Event(
            job_id=job.id,
            event_type='JobRejected',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'reasons': reasons,
                'custom_reason': custom_reason
            }
        )
        db.session.add(rejection_event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} rejected by {g.staff_name} on {g.workstation_id}")
        
        return jsonify({
            'message': 'Job rejected successfully',
            'job': job.to_dict(),
            'rejection_reasons': job.reject_reasons
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting job {job_id}: {str(e)}")
        return jsonify({
            'error': 'reject_job_failed',
            'message': 'Failed to reject job'
        }), 500


@bp.route('/<job_id>/mark-printing', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def mark_printing(job_id):
    """
    Mark a job as currently printing.
    
    Requires staff attribution.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Validate job status transition
        if not job.can_transition_to(Job.STATUS_PRINTING):
            return jsonify({
                'error': 'invalid_status_transition',
                'message': f'Cannot mark job as printing from {job.status} status'
            }), 400
        
        # Update job status
        old_status = job.status
        job.status = Job.STATUS_PRINTING
        job.last_updated_by = g.staff_name
        
        # Move files to Printing directory
        from app.services.file_service import file_service, FileOperationError
        try:
            new_file_path, new_metadata_path = file_service.move_job_files(
                old_status=old_status,
                new_status=Job.STATUS_PRINTING,
                job_data=job.to_dict()
            )
            job.file_path = new_file_path
            job.metadata_path = new_metadata_path
        except FileOperationError as e:
            db.session.rollback()
            current_app.logger.error(f"Error moving files for job {job_id}: {str(e)}")
            return jsonify({
                'error': 'file_move_failed',
                'message': 'Failed to move job files'
            }), 500
        
        # Create status change event
        event = Event(
            job_id=job.id,
            event_type='StatusChanged',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'old_status': Job.STATUS_READYTOPRINT,
                'new_status': Job.STATUS_PRINTING,
                'action': 'mark_printing'
            }
        )
        db.session.add(event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} marked as printing by {g.staff_name}")
        
        return jsonify({
            'message': 'Job marked as printing successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking job {job_id} as printing: {str(e)}")
        return jsonify({
            'error': 'mark_printing_failed',
            'message': 'Failed to mark job as printing'
        }), 500


@bp.route('/<job_id>/mark-complete', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def mark_complete(job_id):
    """
    Mark a job as completed.
    
    Requires staff attribution.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Validate job status transition
        if not job.can_transition_to(Job.STATUS_COMPLETED):
            return jsonify({
                'error': 'invalid_status_transition',
                'message': f'Cannot mark job as complete from {job.status} status'
            }), 400
        
        # Update job status
        old_status = job.status
        job.status = Job.STATUS_COMPLETED
        job.last_updated_by = g.staff_name
        
        # Move files to Completed directory
        from app.services.file_service import file_service, FileOperationError
        try:
            new_file_path, new_metadata_path = file_service.move_job_files(
                old_status=old_status,
                new_status=Job.STATUS_COMPLETED,
                job_data=job.to_dict()
            )
            job.file_path = new_file_path
            job.metadata_path = new_metadata_path
        except FileOperationError as e:
            db.session.rollback()
            current_app.logger.error(f"Error moving files for job {job_id}: {str(e)}")
            return jsonify({
                'error': 'file_move_failed',
                'message': 'Failed to move job files'
            }), 500
        
        # Create status change event
        event = Event(
            job_id=job.id,
            event_type='StatusChanged',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'old_status': Job.STATUS_PRINTING,
                'new_status': Job.STATUS_COMPLETED,
                'action': 'mark_complete'
            }
        )
        db.session.add(event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} marked as complete by {g.staff_name}")
        
        return jsonify({
            'message': 'Job marked as complete successfully',
            'job': job.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking job {job_id} as complete: {str(e)}")
        return jsonify({
            'error': 'mark_complete_failed',
            'message': 'Failed to mark job as complete'
        }), 500


@bp.route('/<job_id>/mark-picked-up', methods=['POST'])
@require_workstation_auth
@require_staff_attribution
def mark_picked_up(job_id):
    """
    Mark a job as picked up (after payment).
    
    Requires staff attribution and payment information.
    Body should include: grams, txn_no, picked_up_by
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Validate job status transition
        if not job.can_transition_to(Job.STATUS_PAIDPICKEDUP):
            return jsonify({
                'error': 'invalid_status_transition',
                'message': f'Cannot mark job as picked up from {job.status} status'
            }), 400
        
        # Parse request data for payment information
        data = request.get_json()
        required_fields = ['grams', 'txn_no', 'picked_up_by']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': 'missing_required_field',
                    'message': f'Field {field} is required for pickup'
                }), 400
        
        try:
            grams = float(data['grams'])
            if grams <= 0:
                raise ValueError("Weight must be positive")
        except (ValueError, TypeError):
            return jsonify({
                'error': 'invalid_weight',
                'message': 'grams must be a positive number'
            }), 400
        
        # Calculate final price based on actual weight
        if job.material == 'filament':
            price_cents = max(int(grams * 10), 300)  # $0.10/gram, $3.00 minimum
        elif job.material == 'resin':
            price_cents = max(int(grams * 20), 300)  # $0.20/gram, $3.00 minimum
        else:
            return jsonify({
                'error': 'invalid_material',
                'message': 'Job material must be filament or resin'
            }), 400
        
        # Update job status
        old_status = job.status
        job.status = Job.STATUS_PAIDPICKEDUP
        job.last_updated_by = g.staff_name
        
        # Move files to PaidPickedUp directory
        from app.services.file_service import file_service, FileOperationError
        try:
            new_file_path, new_metadata_path = file_service.move_job_files(
                old_status=old_status,
                new_status=Job.STATUS_PAIDPICKEDUP,
                job_data=job.to_dict()
            )
            job.file_path = new_file_path
            job.metadata_path = new_metadata_path
        except FileOperationError as e:
            db.session.rollback()
            current_app.logger.error(f"Error moving files for job {job_id}: {str(e)}")
            return jsonify({
                'error': 'file_move_failed',
                'message': 'Failed to move job files'
            }), 500
        
        # Create payment record
        from app.models.payment import Payment
        payment = Payment(
            job_id=job.id,
            grams=grams,
            price_cents=price_cents,
            txn_no=data['txn_no'],
            picked_up_by=data['picked_up_by'],
            paid_by_staff=g.staff_name
        )
        db.session.add(payment)
        
        # Create pickup event
        event = Event(
            job_id=job.id,
            event_type='JobPickedUp',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'actual_weight_g': grams,
                'final_price_cents': price_cents,
                'txn_no': data['txn_no'],
                'picked_up_by': data['picked_up_by']
            }
        )
        db.session.add(event)
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} marked as picked up by {g.staff_name}")
        
        return jsonify({
            'message': 'Job marked as picked up successfully',
            'job': job.to_dict(),
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking job {job_id} as picked up: {str(e)}")
        return jsonify({
            'error': 'mark_picked_up_failed',
            'message': 'Failed to mark job as picked up'
        }), 500


@bp.route('/<job_id>/review', methods=['POST'])
@require_workstation_auth
def mark_reviewed(job_id):
    """
    Mark a job as reviewed (clears visual alerts).
    
    Does not require staff attribution since it's just clearing alerts.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Update staff viewed timestamp
        job.staff_viewed_at = datetime.utcnow()
        
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} marked as reviewed on {g.workstation_id}")
        
        return jsonify({
            'message': 'Job marked as reviewed successfully',
            'staff_viewed_at': job.staff_viewed_at.isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking job {job_id} as reviewed: {str(e)}")
        return jsonify({
            'error': 'mark_reviewed_failed',
            'message': 'Failed to mark job as reviewed'
        }), 500


@bp.route('/<job_id>/notes', methods=['PATCH'])
@require_workstation_auth
@require_staff_attribution
def update_notes(job_id):
    """
    Update staff notes for a job.
    
    Requires staff attribution.
    Body should include: notes
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Parse request data
        data = request.get_json()
        if 'notes' not in data:
            return jsonify({
                'error': 'missing_notes_field',
                'message': 'notes field is required'
            }), 400
        
        old_notes = job.notes
        job.notes = data['notes']
        job.last_updated_by = g.staff_name
        
        # Create notes update event
        event = Event(
            job_id=job.id,
            event_type='NotesUpdated',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'old_notes': old_notes,
                'new_notes': job.notes
            }
        )
        db.session.add(event)
        
        db.session.commit()
        
        current_app.logger.info(f"Notes updated for job {job_id} by {g.staff_name}")
        
        return jsonify({
            'message': 'Notes updated successfully',
            'notes': job.notes
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating notes for job {job_id}: {str(e)}")
        return jsonify({
            'error': 'update_notes_failed',
            'message': 'Failed to update notes'
        }), 500


@bp.route('/<job_id>/candidate-files', methods=['GET'])
@require_workstation_auth
def get_candidate_files(job_id):
    """
    Get list of potential authoritative files for job approval.
    
    Scans job directory for original file and any slicer-generated files.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Get candidate files from file service
        from app.services.file_service import file_service
        candidates = file_service.find_candidate_files(job.to_dict())
        
        return jsonify({
            'job_id': job_id,
            'candidates': candidates,
            'total': len(candidates)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting candidate files for job {job_id}: {str(e)}")
        return jsonify({
            'error': 'get_candidates_failed',
            'message': 'Failed to retrieve candidate files'
        }), 500


@bp.route('/<job_id>', methods=['DELETE'])
@require_workstation_auth
@require_staff_attribution
def delete_job(job_id):
    """
    Permanently delete a job and its associated files.
    
    Only allowed for jobs in UPLOADED or PENDING status.
    Requires staff attribution and creates audit trail.
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            return jsonify({
                'error': 'job_not_found',
                'message': f'Job {job_id} not found'
            }), 404
        
        # Check if job can be deleted
        if job.status not in [Job.STATUS_UPLOADED, Job.STATUS_PENDING]:
            return jsonify({
                'error': 'invalid_status_for_deletion',
                'message': f'Cannot delete job in {job.status} status'
            }), 400
        
        # Store job info for logging before deletion
        job_info = {
            'id': job.id,
            'student_name': job.student_name,
            'student_email': job.student_email,
            'display_name': job.display_name,
            'status': job.status,
            'file_path': job.file_path,
            'metadata_path': job.metadata_path
        }
        
        # Delete job files
        from app.services.file_service import file_service
        files_deleted = file_service.delete_job_files(job.to_dict())
        
        if not files_deleted:
            current_app.logger.warning(f"Failed to delete files for job {job_id}, proceeding with database deletion")
        
        # Create deletion event before deleting job
        deletion_event = Event(
            job_id=job.id,
            event_type='JobDeleted',
            triggered_by=g.staff_name,
            workstation_id=g.workstation_id,
            details={
                'job_info': job_info,
                'files_deleted': files_deleted,
                'deletion_reason': 'staff_initiated'
            }
        )
        db.session.add(deletion_event)
        
        # Delete job and all related records (events will be cascade deleted)
        db.session.delete(job)
        db.session.commit()
        
        current_app.logger.info(f"Job {job_id} deleted by {g.staff_name}")
        
        return jsonify({
            'message': 'Job deleted successfully',
            'job_id': job_id,
            'files_deleted': files_deleted
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting job {job_id}: {str(e)}")
        return jsonify({
            'error': 'delete_job_failed',
            'message': 'Failed to delete job'
        }), 500


@bp.route('/storage-info', methods=['GET'])
@require_workstation_auth
def get_storage_info():
    """
    Get storage usage information for system monitoring.
    
    Returns file counts and sizes for each status directory.
    """
    try:
        from app.services.file_service import file_service
        storage_info = file_service.get_storage_info()
        
        return jsonify(storage_info), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting storage info: {str(e)}")
    return jsonify({
            'error': 'storage_info_failed',
            'message': 'Failed to retrieve storage information'
        }), 500


