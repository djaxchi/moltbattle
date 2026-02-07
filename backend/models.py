from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import enum

Base = declarative_base()

class CombatState(str, enum.Enum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    KEYS_ISSUED = "KEYS_ISSUED"  # Keys issued, waiting for both to be ready
    RUNNING = "RUNNING"
    OPEN = "OPEN"  # User A finished, waiting for opponent to complete
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    TIMEOUT = "timeout"
    INVALID = "invalid"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=True)  # Deprecated - kept for migration
    email = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)  # Bcrypt hash
    tech_description = Column(Text, nullable=True)  # Description of agentic setup
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Scoring fields
    wins = Column(Integer, default=0, nullable=False)
    losses = Column(Integer, default=0, nullable=False)
    draws = Column(Integer, default=0, nullable=False)
    total_combats = Column(Integer, default=0, nullable=False)
    
    combats_as_a = relationship("Combat", foreign_keys="Combat.user_a_id", back_populates="user_a")
    combats_as_b = relationship("Combat", foreign_keys="Combat.user_b_id", back_populates="user_b")
    api_keys = relationship("ApiKey", back_populates="user")
    user_api_tokens = relationship("UserApiToken", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    
    @property
    def score(self):
        """Calculate score: 3 points for win, 1 for draw, 0 for loss"""
        return (self.wins * 3) + self.draws
    
    @property
    def rank(self):
        """Get rank tier based on wins"""
        if self.wins >= 100:
            return "Professional"
        elif self.wins >= 50:
            return "Diamond"
        elif self.wins >= 25:
            return "Gold"
        elif self.wins >= 10:
            return "Silver"
        else:
            return "Bronze"

class Combat(Base):
    __tablename__ = "combats"
    
    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_draw = Column(Integer, default=0, nullable=False)  # 1 if draw, 0 otherwise
    state = Column(Enum(CombatState), default=CombatState.CREATED, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)  # Legacy
    question_mode = Column(String, default="formal_logic", nullable=False)  # formal_logic or argument_logic
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Individual timers for async online combat
    user_a_started_at = Column(DateTime, nullable=True)
    user_a_expires_at = Column(DateTime, nullable=True)
    user_b_started_at = Column(DateTime, nullable=True)
    user_b_expires_at = Column(DateTime, nullable=True)
    
    # Ready flags - both must be True before timer starts
    user_a_ready = Column(Integer, default=0, nullable=False)  # 1 if ready, 0 otherwise
    user_b_ready = Column(Integer, default=0, nullable=False)  # 1 if ready, 0 otherwise
    
    # Open combat fields - for async matchmaking
    is_open = Column(Integer, default=0, nullable=False)  # 1 if open combat, 0 if invite-based
    user_a_score = Column(Integer, nullable=True)  # Score for user A in open combats
    user_b_score = Column(Integer, nullable=True)  # Score for user B in open combats
    
    user_a = relationship("User", foreign_keys=[user_a_id], back_populates="combats_as_a")
    user_b = relationship("User", foreign_keys=[user_b_id], back_populates="combats_as_b")
    winner = relationship("User", foreign_keys=[winner_id])
    question = relationship("Question", back_populates="combats")
    api_keys = relationship("ApiKey", back_populates="combat")
    submissions = relationship("Submission", back_populates="combat")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    combat = relationship("Combat", back_populates="api_keys")
    user = relationship("User", back_populates="api_keys")


class UserApiToken(Base):
    """
    Persistent API tokens for user authentication.
    These are long-lived tokens that users can use to authenticate API requests.
    """
    __tablename__ = "user_api_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)  # Optional label like "My Laptop" or "Production Agent"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    
    user = relationship("User", back_populates="user_api_tokens")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    golden_label = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    combats = relationship("Combat", back_populates="question")

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.SUBMITTED, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    combat = relationship("Combat", back_populates="submissions")
    user = relationship("User", back_populates="submissions")


class CombatQuestion(Base):
    """
    Stores metadata about the question used in a combat.
    The actual question data is fetched from HuggingFace, but we store
    the reference and answer hash for verification.
    """
    __tablename__ = "combat_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), unique=True, nullable=False)
    
    # Dataset reference
    dataset = Column(String, nullable=False)  # e.g., "tasksource/proofwriter"
    config = Column(String, nullable=False)   # e.g., "default"
    split = Column(String, nullable=False)    # e.g., "validation"
    row_offset = Column(Integer, nullable=False)  # Row index in the dataset
    
    # Question display data (what was shown to players)
    prompt = Column(Text, nullable=False)
    choices_json = Column(Text, nullable=False)  # JSON array of choices
    
    # Secure answer verification
    answer_key_hash = Column(String, nullable=False)  # SHA256 of correct answer + salt
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    combat = relationship("Combat", backref="combat_question")


class TempApiKey(Base):
    """
    Temporary storage for plaintext API keys so both users can retrieve them.
    Keys are deleted after both users retrieve them or after combat starts.
    """
    __tablename__ = "temp_api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), unique=True, nullable=False)
    key_a = Column(String, nullable=False)  # Plaintext key for user A
    key_b = Column(String, nullable=False)  # Plaintext key for user B
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    expires_at = Column(DateTime, nullable=False)  # Auto-expire after 5 minutes
