from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Audio Transcription API"
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "transcription_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
    
    # Redis/RabbitMQ
    REDIS_URL: str = "redis://localhost:6379"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str
    
    # AssemblyAI
    ASSEMBLYAI_API_KEY: str
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
