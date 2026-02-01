from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import uuid
import os
import random

from database import get_db
from models import User, Combat, ApiKey, Question, Submission, CombatState, SubmissionStatus
from schemas import (
    CreateCombatRequest, CreateCombatResponse,
    AcceptCombatRequest, AcceptCombatResponse,
    CombatStatusResponse, IssueKeysResponse,
    AgentMeResponse, AgentSubmitResponse, AgentResultResponse,
    SubmitAnswerRequest, HealthResponse,
    QuestionResponse, AdminCombatResponse
)
from auth import generate_combat_code, generate_api_token, hash_token
from middleware import verify_admin_token, get_current_user_from_token

app = FastAPI(title="Agent Fight Club API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TIME_LIMIT_SECONDS = int(os.getenv("TIME_LIMIT_SECONDS", "60"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

@app.post("/api/combats", response_model=CreateCombatResponse)
def create_combat(request: CreateCombatRequest, db: Session = Depends(get_db)):
    """Create a new combat"""
    user = db.query(User).filter(User.handle == request.handle).first()
    if not user:
        user = User(handle=request.handle)
        db.add(user)
        db.flush()
    
    # Generate unique combat code
    while True:
        code = generate_combat_code()
        existing = db.query(Combat).filter(Combat.code == code).first()
        if not existing:
            break
    
    combat_id = str(uuid.uuid4())
    combat = Combat(
        id=combat_id,
        code=code,
        user_a_id=user.id,
        state=CombatState.CREATED
    )
    db.add(combat)
    db.commit()
    
    invite_url = f"{BASE_URL}/accept/{code}"
    
    return CreateCombatResponse(
        combatId=combat_id,
        code=code,
        inviteUrl=invite_url
    )

@app.post("/api/combats/{code}/accept", response_model=AcceptCombatResponse)
def accept_combat(code: str, request: AcceptCombatRequest, db: Session = Depends(get_db)):
    """Accept a combat invitation"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    if combat.state != CombatState.CREATED:
        raise HTTPException(status_code=400, detail="Combat already accepted or started")
    
    # Create or get user
    user = db.query(User).filter(User.handle == request.handle).first()
    if not user:
        user = User(handle=request.handle)
        db.add(user)
        db.flush()
    
    # Check if user is trying to accept their own combat
    if user.id == combat.user_a_id:
        raise HTTPException(status_code=400, detail="Cannot accept your own combat")
    
    combat.user_b_id = user.id
    combat.state = CombatState.ACCEPTED
    combat.accepted_at = datetime.utcnow()
    db.commit()
    
    return AcceptCombatResponse(
        combatId=combat.id,
        state=combat.state
    )

@app.get("/api/combats/{code}", response_model=CombatStatusResponse)
def get_combat_status(code: str, db: Session = Depends(get_db)):
    """Get combat status"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    user_a = db.query(User).filter(User.id == combat.user_a_id).first()
    user_b = db.query(User).filter(User.id == combat.user_b_id).first() if combat.user_b_id else None
    
    if combat.state == CombatState.RUNNING and combat.expires_at:
        if datetime.utcnow() > combat.expires_at:
            combat.state = CombatState.EXPIRED
            combat.completed_at = datetime.utcnow()
            db.commit()
    
    countdown_seconds = None
    if combat.expires_at:
        remaining = (combat.expires_at - datetime.utcnow()).total_seconds()
        countdown_seconds = max(0, int(remaining))
    
    question_data = None
    if combat.state in [CombatState.RUNNING, CombatState.COMPLETED, CombatState.EXPIRED] and combat.question:
        question_data = {"prompt": combat.question.prompt}
    
    submissions_status = None
    if combat.state in [CombatState.RUNNING, CombatState.COMPLETED, CombatState.EXPIRED]:
        submissions = db.query(Submission).filter(Submission.combat_id == combat.id).all()
        submissions_status = {}
        for sub in submissions:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                submissions_status[user.handle] = sub.status.value
        
        if combat.user_a_id and user_a.handle not in submissions_status:
            submissions_status[user_a.handle] = "timeout"
        if combat.user_b_id and user_b and user_b.handle not in submissions_status:
            submissions_status[user_b.handle] = "timeout"
    
    return CombatStatusResponse(
        combatId=combat.id,
        code=combat.code,
        state=combat.state,
        countdownSeconds=countdown_seconds,
        question=question_data,
        submissionsStatus=submissions_status,
        userAHandle=user_a.handle if user_a else None,
        userBHandle=user_b.handle if user_b else None,
        createdAt=combat.created_at,
        acceptedAt=combat.accepted_at,
        startedAt=combat.started_at,
        completedAt=combat.completed_at
    )

@app.post("/api/combats/{code}/keys", response_model=IssueKeysResponse)
def issue_api_keys(code: str, db: Session = Depends(get_db)):
    """Issue API keys for both users (starts the combat)"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    if combat.state != CombatState.ACCEPTED:
        raise HTTPException(status_code=400, detail="Combat must be accepted first")
    existing_keys = db.query(ApiKey).filter(ApiKey.combat_id == combat.id).count()
    if existing_keys:
        raise HTTPException(status_code=400, detail="API keys already issued")
    
    token_a = generate_api_token()
    token_b = generate_api_token()
    api_key_a = ApiKey(
        combat_id=combat.id,
        user_id=combat.user_a_id,
        token_hash=hash_token(token_a)
    )
    api_key_b = ApiKey(
        combat_id=combat.id,
        user_id=combat.user_b_id,
        token_hash=hash_token(token_b)
    )
    db.add(api_key_a)
    db.add(api_key_b)
    
    # Assign random question
    questions = db.query(Question).all()
    if not questions:
        raise HTTPException(status_code=500, detail="No questions available")
    question = random.choice(questions)
    
    # Start combat
    combat.state = CombatState.RUNNING
    combat.started_at = datetime.utcnow()
    combat.expires_at = datetime.utcnow() + timedelta(seconds=TIME_LIMIT_SECONDS)
    combat.question_id = question.id
    
    db.commit()
    
    return IssueKeysResponse(
        keyA=token_a,
        keyB=token_b,
        instructionsUrl=f"{BASE_URL}/instructions"
    )

@app.get("/agent/me", response_model=AgentMeResponse)
def agent_get_assignment(context: dict = Depends(get_current_user_from_token)):
    """Get current combat assignment for agent"""
    combat = context["combat"]
    
    response = AgentMeResponse(
        combatId=combat.id,
        state=combat.state
    )
    
    if combat.state == CombatState.RUNNING and combat.question:
        response.prompt = combat.question.prompt
        response.deadlineTs = int(combat.expires_at.timestamp()) if combat.expires_at else None
    
    return response

@app.post("/agent/submit", response_model=AgentSubmitResponse)
def agent_submit_answer(
    request: SubmitAnswerRequest,
    context: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Submit answer to combat"""
    user = context["user"]
    combat = context["combat"]
    
    if combat.state != CombatState.RUNNING:
        raise HTTPException(status_code=400, detail="Combat is not running")
    
    if combat.expires_at and datetime.utcnow() > combat.expires_at:
        raise HTTPException(status_code=400, detail="Combat time limit expired")
    
    existing = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Answer already submitted")
    
    submission = Submission(
        combat_id=combat.id,
        user_id=user.id,
        answer=request.answer,
        status=SubmissionStatus.SUBMITTED
    )
    db.add(submission)
    
    all_submissions = db.query(Submission).filter(Submission.combat_id == combat.id).count()
    if all_submissions + 1 >= 2:
        combat.state = CombatState.COMPLETED
        combat.completed_at = datetime.utcnow()
    
    db.commit()
    
    return AgentSubmitResponse(ok=True, status="submitted")

@app.get("/agent/result", response_model=AgentResultResponse)
def agent_get_result(
    context: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get combat result"""
    user = context["user"]
    combat = context["combat"]
    
    my_submission = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == user.id
    ).first()
    
    opponent_id = combat.user_b_id if user.id == combat.user_a_id else combat.user_a_id
    opponent_submission = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == opponent_id
    ).first()
    
    # Handle timeouts
    my_status = my_submission.status.value if my_submission else "timeout"
    opponent_status = opponent_submission.status.value if opponent_submission else "timeout"
    
    # Only show answers if combat is completed
    my_answer = None
    opponent_answer = None
    if combat.state in [CombatState.COMPLETED, CombatState.EXPIRED]:
        my_answer = my_submission.answer if my_submission else None
        opponent_answer = opponent_submission.answer if opponent_submission else None
    
    return AgentResultResponse(
        combatId=combat.id,
        state=combat.state,
        myStatus=my_status,
        opponentStatus=opponent_status,
        myAnswer=my_answer,
        opponentAnswer=opponent_answer,
        completedAt=combat.completed_at
    )

# ============================================================================
# ADMIN API
# ============================================================================

@app.post("/admin/questions/seed")
def admin_seed_questions(
    admin: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Seed questions (admin only)"""
    from seed_questions import seed_questions
    seed_questions()
    return {"message": "Questions seeded successfully"}

@app.get("/admin/questions", response_model=List[QuestionResponse])
def admin_list_questions(
    admin: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """List all questions (admin only)"""
    questions = db.query(Question).all()
    return [
        QuestionResponse(
            id=q.id,
            prompt=q.prompt,
            goldenLabel=q.golden_label,
            createdAt=q.created_at
        )
        for q in questions
    ]

@app.get("/admin/combats", response_model=List[AdminCombatResponse])
def admin_list_combats(
    admin: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """List all combats (admin only)"""
    combats = db.query(Combat).all()
    result = []
    for combat in combats:
        user_a = db.query(User).filter(User.id == combat.user_a_id).first()
        user_b = db.query(User).filter(User.id == combat.user_b_id).first() if combat.user_b_id else None
        
        result.append(AdminCombatResponse(
            id=combat.id,
            code=combat.code,
            state=combat.state,
            userAHandle=user_a.handle if user_a else "unknown",
            userBHandle=user_b.handle if user_b else None,
            questionId=combat.question_id,
            createdAt=combat.created_at,
            startedAt=combat.started_at,
            completedAt=combat.completed_at
        ))
    
    return result

@app.get("/admin/combats/{combat_id}")
def admin_get_combat(
    combat_id: str,
    admin: bool = Depends(verify_admin_token),
    db: Session = Depends(get_db)
):
    """Get combat details (admin only)"""
    combat = db.query(Combat).filter(Combat.id == combat_id).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    submissions = db.query(Submission).filter(Submission.combat_id == combat_id).all()
    
    return {
        "combat": combat,
        "submissions": submissions,
        "question": combat.question
    }

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow()
    )

# ============================================================================
# BACKGROUND TASK: Check for expired combats
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    from database import init_database
    init_database()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
