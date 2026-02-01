import secrets
import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_combat_code(length: int = 6) -> str:
    """Generate a random combat code (uppercase alphanumeric)"""
    alphabet = "ABCDEFGHIJKLMNPQRSTUVWXYZ123456789"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_token(length: int = 32) -> str:
    """Generate a high-entropy API token"""
    return secrets.token_urlsafe(length)

def hash_token(token: str) -> str:
    """Hash a token using SHA-256"""
    return hashlib.sha256(token.encode()).hexdigest()

def verify_token(token: str, token_hash: str) -> bool:
    """Verify a token against its hash"""
    return hash_token(token) == token_hash
