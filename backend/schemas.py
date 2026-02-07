from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import CombatState, SubmissionStatus

# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class AuthUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    techDescription: Optional[str] = None
    wins: int
    losses: int
    draws: int
    totalCombats: int
    score: int
    rank: str
    createdAt: datetime

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    email: Optional[EmailStr] = None
    tech_description: Optional[str] = Field(None, max_length=2000)

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user: AuthUserResponse
    token: str

class UpdateUsernameRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)

class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, description="New password must be at least 8 characters")

class UpdateTechDescriptionRequest(BaseModel):
    tech_description: str = Field(..., max_length=2000, description="Description of your agentic setup")

# ============================================================================
# TOKEN MANAGEMENT SCHEMAS
# ============================================================================

class TokenCreateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="Optional label for the token (e.g., 'My Laptop')")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")

class TokenResponse(BaseModel):
    id: int
    name: Optional[str] = None
    token: str  # Only shown once when created
    created_at: datetime
    expires_at: Optional[datetime] = None

class TokenListItem(BaseModel):
    id: int
    name: Optional[str] = None
    token_preview: str  # Last 4 characters
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class TokenListResponse(BaseModel):
    tokens: List[TokenListItem]


# ============================================================================
# COMBAT SCHEMAS
# ============================================================================

class CreateCombatRequest(BaseModel):
    mode: str = Field(default="formal_logic", description="Question mode: formal_logic or argument_logic")
    is_open: bool = Field(default=False, description="If true, create an open combat without needing an opponent invite")

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
    code: str
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
    techDescription: Optional[str] = None
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
    userAAnswer: Optional[str] = None  # What player A submitted
    userBAnswer: Optional[str] = None  # What player B submitted
    correctAnswer: Optional[str] = None  # Revealed after combat ends

# ============================================================================
# COMBAT HISTORY SCHEMAS
# ============================================================================

class CombatHistoryEntry(BaseModel):
    combatId: str
    code: str
    mode: str
    state: CombatState
    isOpen: bool
    opponentUsername: Optional[str] = None
    result: Optional[str] = None  # "win", "loss", "draw", or None if not completed
    myScore: Optional[int] = None
    opponentScore: Optional[int] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None

class CombatHistoryResponse(BaseModel):
    combats: List[CombatHistoryEntry]
    totalCount: int
