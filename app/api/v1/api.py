from fastapi import APIRouter
from app.api.v1.endpoints import auth, transcriptions, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["transcriptions"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
