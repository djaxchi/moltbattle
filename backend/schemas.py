from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from models import CombatState, SubmissionStatus

class CreateCombatRequest(BaseModel):
    handle: str

class AcceptCombatRequest(BaseModel):
    handle: str

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
    countdownSeconds: Optional[int] = None
    question: Optional[Dict[str, str]] = None
    submissionsStatus: Optional[Dict[str, str]] = None
    userAHandle: Optional[str] = None
    userBHandle: Optional[str] = None
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
    userAHandle: str
    userBHandle: Optional[str]
    questionId: Optional[int]
    createdAt: datetime
    startedAt: Optional[datetime]
    completedAt: Optional[datetime]
