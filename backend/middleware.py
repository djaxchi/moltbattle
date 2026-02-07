from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ApiKey, Combat, User, UserApiToken
from auth import hash_token
from datetime import datetime, timezone
import os

def verify_admin_token(authorization: str = Header(None)):
    """Verify admin token"""
    admin_token = os.getenv("ADMIN_TOKEN", "admin-secret-token")
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    
    if token != admin_token:
        raise HTTPException(status_code=403, detail="Invalid admin token")
    
    return True

def get_current_user_from_api_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from persistent API token.
    Used for user-level endpoints (create combat, accept combat, profile, etc.)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    token_hash_value = hash_token(token)
    
    # Find user API token
    user_token = db.query(UserApiToken).filter(
        UserApiToken.token_hash == token_hash_value,
        UserApiToken.revoked_at.is_(None)
    ).first()
    
    if not user_token:
        raise HTTPException(status_code=401, detail="Invalid or revoked API token")
    
    # Check if token has expired
    if user_token.expires_at and datetime.now(timezone.utc) > user_token.expires_at:
        raise HTTPException(status_code=401, detail="API token has expired")
    
    user = db.query(User).filter(User.id == user_token.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update last used timestamp
    user_token.last_used_at = datetime.now(timezone.utc)
    db.commit()
    
    return user

def get_current_user_from_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """
    Get current user and combat from combat-specific API key.
    Used for agent endpoints during combat (submit answer, get question, etc.)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    token_hash_value = hash_token(token)
    
    # Find combat-specific API key
    api_key = db.query(ApiKey).filter(
        ApiKey.token_hash == token_hash_value,
        ApiKey.revoked_at.is_(None)
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid or revoked API key")
    
    combat = db.query(Combat).filter(Combat.id == api_key.combat_id).first()
    user = db.query(User).filter(User.id == api_key.user_id).first()
    
    if not combat or not user:
        raise HTTPException(status_code=404, detail="Combat or user not found")
    
    return {
        "user": user,
        "combat": combat,
        "api_key": api_key
    }
