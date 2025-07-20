from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.models.user import Base

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    s3_url = Column(Text, nullable=False)
    status = Column(String(20), default=JobStatus.PENDING.value, nullable=False)
    celery_task_id = Column(String(255), unique=True, index=True)
    
    # AssemblyAI configuration
    enable_speaker_diarization = Column(Boolean, default=True)
    enable_sentiment_analysis = Column(Boolean, default=True)
    enable_summarization = Column(Boolean, default=True)
    
    # Results
    transcript_text = Column(Text)
    confidence_score = Column(Float)
    processing_time = Column(Float)  # in seconds
    
    # JSON fields for detailed results
    speaker_diarization_results = Column(JSON)
    sentiment_analysis_results = Column(JSON)
    summary = Column(Text)
    
    # Error handling
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="transcription_jobs")