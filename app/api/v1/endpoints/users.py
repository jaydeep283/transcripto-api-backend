from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_active_user, get_current_user
from app.models.user import User
from app.schemas.auth import User as UserSchema, UserCreate
from app.schemas.user import UserUpdate, UserResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    """
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile
    """
    # Update user fields
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered by another user"
            )
        current_user.email = user_update.email
    
    if user_update.username is not None:
        # Check if username is already taken by another user
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken by another user"
            )
        current_user.username = user_update.username
    
    if user_update.password is not None:
        current_user.hashed_password = User.hash_password(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"User {current_user.id} updated their profile")
    return current_user

@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve users (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID (superuser only or own profile)
    """
    # Users can access their own profile, superusers can access any
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a user (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Update user fields
    if user_update.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered by another user"
            )
        user.email = user_update.email
    
    if user_update.username is not None:
        # Check if username is already taken by another user
        existing_user = db.query(User).filter(
            User.username == user_update.username,
            User.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken by another user"
            )
        user.username = user_update.username
    
    if user_update.password is not None:
        user.hashed_password = User.hash_password(user_update.password)
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    if user_update.is_superuser is not None:
        user.is_superuser = user_update.is_superuser
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Superuser {current_user.id} updated user {user_id}")
    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    logger.info(f"Superuser {current_user.id} deleted user {user_id}")
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Activate a user (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user.is_active = True
    db.commit()
    
    logger.info(f"Superuser {current_user.id} activated user {user_id}")
    return {"message": "User activated successfully"}

@router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot deactivate yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user.is_active = False
    db.commit()
    
    logger.info(f"Superuser {current_user.id} deactivated user {user_id}")
    return {"message": "User deactivated successfully"}

@router.post("/{user_id}/make-superuser")
async def make_superuser(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Grant superuser privileges (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user.is_superuser = True
    db.commit()
    
    logger.info(f"Superuser {current_user.id} granted superuser privileges to user {user_id}")
    return {"message": "User granted superuser privileges"}

@router.delete("/{user_id}/remove-superuser")
async def remove_superuser(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove superuser privileges (superuser only)
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot remove superuser privileges from yourself"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    user.is_superuser = False
    db.commit()
    
    logger.info(f"Superuser {current_user.id} removed superuser privileges from user {user_id}")
    return {"message": "Superuser privileges removed"}