from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionJobCreate(BaseModel):
    filename: str
    enable_speaker_diarization: bool = True
    enable_sentiment_analysis: bool = True
    enable_summarization: bool = True

class TranscriptionJobResponse(BaseModel):
    id: int
    filename: str
    status: JobStatus
    created_at: datetime
    updated_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    # Results (only present when completed)
    transcript_text: Optional[str]
    confidence_score: Optional[float]
    processing_time: Optional[float]
    speaker_diarization_results: Optional[Dict[str, Any]]
    sentiment_analysis_results: Optional[Dict[str, Any]]
    summary: Optional[str]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

class JobSubmissionResponse(BaseModel):
    job_id: int
    message: str
    status: JobStatus
