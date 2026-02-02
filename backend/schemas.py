from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import CombatState, SubmissionStatus

# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)

class UpdateUsernameRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)

class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    wins: int
    losses: int
    draws: int
    totalCombats: int
    score: int
    rank: str
    createdAt: datetime

# ============================================================================
# COMBAT SCHEMAS
# ============================================================================

class CreateCombatRequest(BaseModel):
    mode: str = Field(default="formal_logic", description="Question mode: formal_logic or argument_logic")

class AcceptCombatRequest(BaseModel):
    pass  # No longer need handle, we get it from auth

class SubmitAnswerRequest(BaseModel):
    answer: str

class CreateCombatResponse(BaseModel):
    combatId: str
    code: str
    inviteUrl: str

class AcceptCombatResponse(BaseModel):
    combatId: str
    state: CombatState

class CombatStatusResponse(BaseModel):
    combatId: str
    code: str
    state: CombatState
    mode: str = "formal_logic"
    countdownSeconds: Optional[int] = None
    question: Optional[Dict[str, Any]] = None  # Now includes choices
    submissionsStatus: Optional[Dict[str, str]] = None
    userAUsername: Optional[str] = None
    userBUsername: Optional[str] = None
    userAReady: bool = False
    userBReady: bool = False
    createdAt: datetime
    acceptedAt: Optional[datetime] = None
    startedAt: Optional[datetime] = None
    completedAt: Optional[datetime] = None

class IssueKeysResponse(BaseModel):
    keyA: str
    keyB: str
    instructionsUrl: str

class AgentMeResponse(BaseModel):
    combatId: str
    state: CombatState
    prompt: Optional[str] = None
    choices: Optional[List[str]] = None  # Answer choices for MCQ
    deadlineTs: Optional[int] = None

class AgentSubmitResponse(BaseModel):
    ok: bool
    status: str

class AgentResultResponse(BaseModel):
    combatId: str
    state: CombatState
    myStatus: str
    opponentStatus: str
    myAnswer: Optional[str] = None
    opponentAnswer: Optional[str] = None
    completedAt: Optional[datetime] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

class QuestionResponse(BaseModel):
    id: int
    prompt: str
    goldenLabel: str
    createdAt: datetime

class AdminCombatResponse(BaseModel):
    id: str
    code: str
    state: CombatState
    userAUsername: str
    userBUsername: Optional[str]
    questionId: Optional[int]
    createdAt: datetime
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]

# ============================================================================
# LEADERBOARD & USER PROFILE SCHEMAS
# ============================================================================

class UserProfileResponse(BaseModel):
    username: str
    wins: int
    losses: int
    draws: int
    totalCombats: int
    score: int
    rank: str
    createdAt: datetime

class LeaderboardEntryResponse(BaseModel):
    position: int
    username: str
    wins: int
    losses: int
    draws: int
    totalCombats: int
    score: int
    rank: str
    winRate: float

class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntryResponse]
    totalUsers: int

class CombatResultResponse(BaseModel):
    combatId: str
    winnerId: Optional[int] = None
    winnerUsername: Optional[str] = None
    isDraw: bool
    userAUsername: str
    userBUsername: str
    userACorrect: bool
    userBCorrect: bool
    correctAnswer: Optional[str] = None  # Revealed after combat ends
