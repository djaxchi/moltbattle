from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

Base = declarative_base()

class CombatState(str, enum.Enum):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"

class SubmissionStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    TIMEOUT = "timeout"
    INVALID = "invalid"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    handle = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    combats_as_a = relationship("Combat", foreign_keys="Combat.user_a_id", back_populates="user_a")
    combats_as_b = relationship("Combat", foreign_keys="Combat.user_b_id", back_populates="user_b")
    api_keys = relationship("ApiKey", back_populates="user")
    submissions = relationship("Submission", back_populates="user")

class Combat(Base):
    __tablename__ = "combats"
    
    id = Column(String, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    user_a_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_b_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    state = Column(Enum(CombatState), default=CombatState.CREATED, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    user_a = relationship("User", foreign_keys=[user_a_id], back_populates="combats_as_a")
    user_b = relationship("User", foreign_keys=[user_b_id], back_populates="combats_as_b")
    question = relationship("Question", back_populates="combats")
    api_keys = relationship("ApiKey", back_populates="combat")
    submissions = relationship("Submission", back_populates="combat")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token_hash = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    combat = relationship("Combat", back_populates="api_keys")
    user = relationship("User", back_populates="api_keys")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    golden_label = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    combats = relationship("Combat", back_populates="question")

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    combat_id = Column(String, ForeignKey("combats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatus), default=SubmissionStatus.SUBMITTED, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    combat = relationship("Combat", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
