"""
Firebase Authentication module for Agent Fight Club.

Setup:
1. Go to Firebase Console (https://console.firebase.google.com)
2. Create a new project or use existing
3. Go to Project Settings > Service Accounts
4. Generate new private key and save as 'firebase-service-account.json' in backend folder
5. Enable Email/Password authentication in Firebase Console > Authentication > Sign-in method
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Header, Depends
from functools import lru_cache

# Initialize Firebase Admin SDK
_firebase_app = None

def get_firebase_app():
    """Get or initialize Firebase Admin app."""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    # Check for service account file
    service_account_path = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", 
        os.path.join(os.path.dirname(__file__), "firebase-service-account.json")
    )
    
    if os.path.exists(service_account_path):
        cred = credentials.Certificate(service_account_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        print(f"✅ Firebase initialized with service account")
    else:
        # Try to use default credentials (for cloud deployments)
        try:
            _firebase_app = firebase_admin.initialize_app()
            print("✅ Firebase initialized with default credentials")
        except Exception as e:
            print(f"⚠️ Firebase not initialized: {e}")
            print("   Place firebase-service-account.json in backend folder")
            return None
    
    return _firebase_app


def verify_firebase_token(id_token: str) -> dict:
    """
    Verify a Firebase ID token and return the decoded token.
    
    Args:
        id_token: The Firebase ID token from the client
        
    Returns:
        Decoded token containing uid, email, etc.
        
    Raises:
        HTTPException: If token is invalid
    """
    app = get_firebase_app()
    
    if app is None:
        raise HTTPException(
            status_code=503, 
            detail="Firebase authentication not configured"
        )
    
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=401, detail="Token has been revoked")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def get_current_firebase_user(authorization: str = Header(None)) -> dict:
    """
    FastAPI dependency to get current authenticated Firebase user.
    
    Usage:
        @app.get("/protected")
        def protected_route(user: dict = Depends(get_current_firebase_user)):
            return {"uid": user["uid"], "email": user.get("email")}
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format. Use: Bearer <token>")
    
    token = authorization.replace("Bearer ", "")
    return verify_firebase_token(token)


async def get_optional_firebase_user(authorization: str = Header(None)) -> dict | None:
    """
    FastAPI dependency to optionally get current Firebase user.
    Returns None if no valid token is provided (for public routes that can be enhanced with auth).
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.replace("Bearer ", "")
        return verify_firebase_token(token)
    except HTTPException:
        return None


def get_firebase_user_record(uid: str) -> dict:
    """
    Get full Firebase user record including displayName, email, etc.
    
    Args:
        uid: The Firebase user ID
        
    Returns:
        dict with user data including displayName
    """
    app = get_firebase_app()
    if app is None:
        raise HTTPException(
            status_code=503,
            detail="Firebase authentication not configured"
        )
    
    try:
        user_record = auth.get_user(uid)
        return {
            "uid": user_record.uid,
            "email": user_record.email,
            "displayName": user_record.display_name,
            "photoURL": user_record.photo_url,
            "emailVerified": user_record.email_verified,
        }
    except auth.UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")


# Initialize on module load
get_firebase_app()
