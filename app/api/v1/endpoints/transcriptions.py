from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.transcription import TranscriptionJob, JobStatus
from app.schemas.transcription import (
    TranscriptionJobResponse,
    JobSubmissionResponse,
    TranscriptionJobCreate
)
from app.services.s3_service import s3_service
from app.workers.transcription_worker import process_transcription_job
import uuid
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=JobSubmissionResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    enable_speaker_diarization: bool = True,
    enable_sentiment_analysis: bool = True,
    enable_summarization: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio file and create transcription job
    """
    try:
        # Validate file type
        allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp3', 'audio/m4a', 'audio/ogg']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_types)}"
            )
        
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        file_size = 0
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to beginning
        
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail="File size too large. Maximum allowed size is 100MB"
            )
        
        # Generate unique S3 object name
        file_extension = os.path.splitext(file.filename)[1]
        object_name = f"audio/{current_user.id}/{uuid.uuid4()}{file_extension}"
        
        # Upload to S3
        s3_url = await s3_service.upload_file(file, object_name)

        # Generate presigned URL for the uploaded file
        presigned_url = s3_service.generate_presigned_url(object_name)
        
        # Create job record
        job = TranscriptionJob(
            user_id=current_user.id,
            filename=file.filename,
            s3_url=presigned_url,
            status=JobStatus.PENDING.value,
            enable_speaker_diarization=enable_speaker_diarization,
            enable_sentiment_analysis=enable_sentiment_analysis,
            enable_summarization=enable_summarization
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Queue Celery task
        task = process_transcription_job.delay(job.id)
        
        # Update job with Celery task ID
        job.celery_task_id = task.id
        db.commit()
        
        logger.info(f"Created transcription job {job.id} for user {current_user.id}")
        
        return JobSubmissionResponse(
            job_id=job.id,
            message="File uploaded successfully. Transcription job started.",
            status=JobStatus.PENDING
        )

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions
        raise http_exc    
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{job_id}", response_model=TranscriptionJobResponse)
def get_transcription_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get transcription job status and results
    """
    job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user owns this job or is superuser
    if job.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return job

@router.get("/", response_model=List[TranscriptionJobResponse])
def get_user_transcription_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's transcription jobs
    """
    query = db.query(TranscriptionJob)
    
    # Non-superusers can only see their own jobs
    if not current_user.is_superuser:
        query = query.filter(TranscriptionJob.user_id == current_user.id)
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs

@router.delete("/{job_id}")
def delete_transcription_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete transcription job
    """
    job = db.query(TranscriptionJob).filter(
        TranscriptionJob.id == job_id
    ).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Check if user owns this job or is superuser
    if job.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Access denied")
    
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}
