from celery import current_task
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.transcription import TranscriptionJob, JobStatus
from app.services.assemblyai_service import assemblyai_service
from datetime import datetime
import logging
import time

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def process_transcription_job(self, job_id: int):
    """
    Celery task to process audio transcription
    """
    db = SessionLocal()
    start_time = time.time()
    
    try:
        # Get job from database
        job = db.query(TranscriptionJob).filter(TranscriptionJob.id == job_id).first()
        if not job:
            raise Exception(f"Job with id {job_id} not found")
        
        logger.info(f"Starting transcription job {job_id} for file: {job.filename}")
        
        # Update job status to processing
        job.status = JobStatus.PROCESSING.value
        job.started_at = datetime.utcnow()
        job.celery_task_id = self.request.id
        db.commit()
        
        # Update task progress
        self.update_state(
            state="PROCESSING",
            meta={"job_id": job_id, "message": "Starting transcription..."}
        )
        
        # Call AssemblyAI service
        result = assemblyai_service.transcribe_audio(
            audio_url=job.s3_url,
            enable_speaker_diarization=job.enable_speaker_diarization,
            enable_sentiment_analysis=job.enable_sentiment_analysis
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Update job with results
        job.status = JobStatus.COMPLETED.value
        job.transcript_text = result["transcript_text"]
        job.confidence_score = result.get("confidence")
        job.processing_time = processing_time
        job.speaker_diarization_results = result.get("speaker_diarization_results")
        job.sentiment_analysis_results = result.get("sentiment_analysis_results")
        
        # Generate summary from chapters if available
        if result.get("chapters"):
            summary_parts = [chapter.get("summary", "") for chapter in result["chapters"]]
            job.summary = " ".join(filter(None, summary_parts))
        
        job.completed_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Transcription job {job_id} completed successfully in {processing_time:.2f}s")
        
        return {
            "job_id": job_id,
            "status": "completed",
            "processing_time": processing_time
        }
        
    except Exception as exc:
        logger.error(f"Transcription job {job_id} failed: {str(exc)}")
        
        # Update job status to failed
        if 'job' in locals():
            job.status = JobStatus.FAILED.value
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()
            db.commit()
        
        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying job {job_id}, attempt {self.request.retries + 1}")
            raise self.retry(countdown=60 * (self.request.retries + 1), exc=exc)
        
        raise exc
        
    finally:
        db.close()
