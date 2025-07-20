# Alembic migration file for initial database schema
# Save this as: alembic/versions/001_initial_migration.py

"""Initial migration

Revision ID: 001_initial_migration
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_migration'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create transcription_jobs table
    op.create_table('transcription_jobs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=255), nullable=False),
    sa.Column('s3_url', sa.Text(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('celery_task_id', sa.String(length=255), nullable=True),
    sa.Column('enable_speaker_diarization', sa.Boolean(), nullable=True),
    sa.Column('enable_sentiment_analysis', sa.Boolean(), nullable=True),
    sa.Column('enable_summarization', sa.Boolean(), nullable=True),
    sa.Column('transcript_text', sa.Text(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('processing_time', sa.Float(), nullable=True),
    sa.Column('speaker_diarization_results', sa.JSON(), nullable=True),
    sa.Column('sentiment_analysis_results', sa.JSON(), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transcription_jobs_id'), 'transcription_jobs', ['id'], unique=False)
    op.create_index(op.f('ix_transcription_jobs_celery_task_id'), 'transcription_jobs', ['celery_task_id'], unique=True)


def downgrade() -> None:
    # Drop transcription_jobs table
    op.drop_index(op.f('ix_transcription_jobs_celery_task_id'), table_name='transcription_jobs')
    op.drop_index(op.f('ix_transcription_jobs_id'), table_name='transcription_jobs')
    op.drop_table('transcription_jobs')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')