from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "transcription_worker",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.transcription_worker"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_annotations={
        "*": {"rate_limit": "10/s"}
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)
