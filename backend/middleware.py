from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import ApiKey, Combat, User
from auth import hash_token
from datetime import datetime
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

def get_current_user_from_token(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> dict:
    """Get current user and combat from API key"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    token_hash_value = hash_token(token)
    
    # Find API key
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
