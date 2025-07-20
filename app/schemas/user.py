from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserResponse(BaseModel):
    """Schema for user response (includes additional fields like timestamps)"""
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class UserStats(BaseModel):
    """Schema for user statistics"""
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    pending_jobs: int
    processing_jobs: int
    total_processing_time: Optional[float] = None

class UserWithStats(UserResponse):
    """Schema for user with statistics"""
    stats: Optional[UserStats] = None