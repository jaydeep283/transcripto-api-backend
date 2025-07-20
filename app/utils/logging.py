import logging
import sys
from app.core.config import settings

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log")
        ]
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
