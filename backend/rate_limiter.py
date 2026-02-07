"""
Simple in-memory rate limiter for authentication endpoints.
For production at scale, consider using Redis or a dedicated rate limiting service.
"""

from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import threading

class RateLimiter:
    """
    Thread-safe in-memory rate limiter.
    Tracks attempts by key (username or IP) and enforces rate limits.
    """
    
    def __init__(self):
        self._attempts: Dict[str, list] = defaultdict(list)
        self._lock = threading.Lock()
    
    def check_rate_limit(self, key: str, max_attempts: int, window_minutes: int) -> Tuple[bool, int]:
        """
        Check if the key has exceeded the rate limit.
        
        Args:
            key: Identifier to track (e.g., username, IP address)
            max_attempts: Maximum number of attempts allowed
            window_minutes: Time window in minutes
        
        Returns:
            Tuple of (is_allowed, remaining_attempts)
        """
        with self._lock:
            now = datetime.utcnow()
            cutoff = now - timedelta(minutes=window_minutes)
            
            # Remove old attempts outside the window
            if key in self._attempts:
                self._attempts[key] = [
                    timestamp for timestamp in self._attempts[key]
                    if timestamp > cutoff
                ]
            
            # Count current attempts
            current_attempts = len(self._attempts[key])
            
            if current_attempts >= max_attempts:
                return False, 0
            
            return True, max_attempts - current_attempts
    
    def record_attempt(self, key: str):
        """Record an attempt for the given key."""
        with self._lock:
            self._attempts[key].append(datetime.utcnow())
    
    def reset(self, key: str):
        """Reset attempts for a given key (e.g., after successful login)."""
        with self._lock:
            if key in self._attempts:
                del self._attempts[key]
    
    def cleanup_old_entries(self, max_age_hours: int = 24):
        """
        Clean up old entries to prevent memory bloat.
        Should be called periodically.
        """
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
            keys_to_delete = []
            
            for key, timestamps in self._attempts.items():
                # Filter out old timestamps
                self._attempts[key] = [
                    timestamp for timestamp in timestamps
                    if timestamp > cutoff
                ]
                # Mark empty lists for deletion
                if not self._attempts[key]:
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                del self._attempts[key]


# Global rate limiter instance
login_rate_limiter = RateLimiter()
register_rate_limiter = RateLimiter()
token_generation_rate_limiter = RateLimiter()
