"""Initial migration - Create all tables

Revision ID: 001
Revises: 
Create Date: 2025-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create staff table
    op.create_table('staff',
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('added_at', sa.DateTime(), nullable=False),
        sa.Column('deactivated_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('name')
    )
    
    # Create job table
    op.create_table('job',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('student_name', sa.String(length=100), nullable=False),
        sa.Column('student_email', sa.String(length=100), nullable=False),
        sa.Column('discipline', sa.String(length=50), nullable=False),
        sa.Column('class_number', sa.String(length=50), nullable=False),
        sa.Column('original_filename', sa.String(length=256), nullable=False),
        sa.Column('display_name', sa.String(length=256), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('metadata_path', sa.String(length=512), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('printer', sa.String(length=64), nullable=False),
        sa.Column('color', sa.String(length=32), nullable=False),
        sa.Column('material', sa.String(length=32), nullable=False),
        sa.Column('weight_g', sa.Float(), nullable=True),
        sa.Column('time_hours', sa.Float(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('acknowledged_minimum_charge', sa.Boolean(), nullable=False),
        sa.Column('student_confirmed', sa.Boolean(), nullable=False),
        sa.Column('student_confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('confirm_token', sa.String(length=128), nullable=True),
        sa.Column('confirm_token_expires', sa.DateTime(), nullable=True),
        sa.Column('is_confirmation_expired', sa.Boolean(), nullable=False),
        sa.Column('confirmation_last_sent_at', sa.DateTime(), nullable=True),
        sa.Column('reject_reasons', sa.JSON(), nullable=True),
        sa.Column('staff_viewed_at', sa.DateTime(), nullable=True),
        sa.Column('last_updated_by', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('locked_by_user', sa.String(length=100), nullable=True),
        sa.Column('locked_until', sa.DateTime(), nullable=True),
        sa.Column('locked_workstation', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('confirm_token')
    )
    
    # Create indexes for job table
    op.create_index('idx_job_status', 'job', ['status'])
    op.create_index('idx_job_created_at', 'job', ['created_at'])
    op.create_index('idx_job_student_email', 'job', ['student_email'])
    op.create_index('idx_job_confirm_token', 'job', ['confirm_token'])
    
    # Create event table
    op.create_table('event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('triggered_by', sa.String(length=100), nullable=False),
        sa.Column('workstation_id', sa.String(length=100), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('user_name', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for event table
    op.create_index('idx_event_job_id', 'event', ['job_id'])
    op.create_index('idx_event_timestamp', 'event', ['timestamp'])
    op.create_index('idx_event_type', 'event', ['event_type'])
    op.create_index('idx_event_triggered_by', 'event', ['triggered_by'])
    
    # Create payment table
    op.create_table('payment',
        sa.Column('job_id', sa.String(length=36), nullable=False),
        sa.Column('grams', sa.Float(), nullable=False),
        sa.Column('price_cents', sa.Integer(), nullable=False),
        sa.Column('txn_no', sa.String(length=50), nullable=False),
        sa.Column('picked_up_by', sa.String(length=100), nullable=False),
        sa.Column('paid_ts', sa.DateTime(), nullable=False),
        sa.Column('paid_by_staff', sa.String(length=100), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['job.id'], ),
        sa.PrimaryKeyConstraint('job_id')
    )


def downgrade():
    op.drop_table('payment')
    op.drop_index('idx_event_triggered_by', table_name='event')
    op.drop_index('idx_event_type', table_name='event')
    op.drop_index('idx_event_timestamp', table_name='event')
    op.drop_index('idx_event_job_id', table_name='event')
    op.drop_table('event')
    op.drop_index('idx_job_confirm_token', table_name='job')
    op.drop_index('idx_job_student_email', table_name='job')
    op.drop_index('idx_job_created_at', table_name='job')
    op.drop_index('idx_job_status', table_name='job')
    op.drop_table('job')
    op.drop_table('staff')