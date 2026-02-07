"""Session management for MoltBattle MCP Server"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
from config import SESSION_STORAGE_PATH


class SessionManager:
    """Manages user sessions, tokens, and combat keys"""
    
    def __init__(self, storage_path: str = SESSION_STORAGE_PATH):
        self.storage_path = Path(storage_path)
        self.session_data: Dict[str, Any] = self._load_session()
    
    def _load_session(self) -> Dict[str, Any]:
        """Load session data from disk"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "user_token": None,
            "username": None,
            "user_id": None,
            "combat_keys": {},  # code -> api_key mapping
            "active_tokens": {}  # token_id -> token mapping (for API tokens)
        }
    
    def _save_session(self):
        """Save session data to disk"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.session_data, f, indent=2)
    
    def set_user_token(self, token: str, username: str, user_id: int):
        """Set the current user's authentication token"""
        self.session_data["user_token"] = token
        self.session_data["username"] = username
        self.session_data["user_id"] = user_id
        self._save_session()
    
    def get_user_token(self) -> Optional[str]:
        """Get the current user's authentication token"""
        return self.session_data.get("user_token")
    
    def get_username(self) -> Optional[str]:
        """Get the current user's username"""
        return self.session_data.get("username")
    
    def clear_user_session(self):
        """Clear all user session data"""
        self.session_data = {
            "user_token": None,
            "username": None,
            "user_id": None,
            "combat_keys": {},
            "active_tokens": {}
        }
        self._save_session()
    
    def store_combat_key(self, combat_code: str, api_key: str):
        """Store a combat API key"""
        self.session_data["combat_keys"][combat_code] = api_key
        self._save_session()
    
    def get_combat_key(self, combat_code: str) -> Optional[str]:
        """Get a combat API key"""
        return self.session_data["combat_keys"].get(combat_code)
    
    def store_api_token(self, token_id: str, token: str, name: str):
        """Store an API token"""
        self.session_data["active_tokens"][token_id] = {
            "token": token,
            "name": name
        }
        self._save_session()
    
    def get_api_token(self, token_id: str) -> Optional[str]:
        """Get an API token"""
        token_data = self.session_data["active_tokens"].get(token_id)
        return token_data["token"] if token_data else None
    
    def list_api_tokens(self) -> Dict[str, Dict[str, str]]:
        """List all stored API tokens"""
        return self.session_data.get("active_tokens", {})
    
    def remove_api_token(self, token_id: str):
        """Remove an API token"""
        if token_id in self.session_data["active_tokens"]:
            del self.session_data["active_tokens"][token_id]
            self._save_session()
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.get_user_token() is not None


# Global session manager instance
session_manager = SessionManager()
