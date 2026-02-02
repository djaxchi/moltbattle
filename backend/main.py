from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
import uuid
import os
import random
import json

from database import get_db
from models import User, Combat, ApiKey, Question, Submission, CombatState, SubmissionStatus, CombatQuestion, TempApiKey
from schemas import (
    CreateCombatRequest, CreateCombatResponse,
    AcceptCombatRequest, AcceptCombatResponse,
    CombatStatusResponse, IssueKeysResponse,
    AgentMeResponse, AgentSubmitResponse, AgentResultResponse,
    SubmitAnswerRequest, HealthResponse,
    QuestionResponse, AdminCombatResponse,
    UserProfileResponse, LeaderboardEntryResponse, LeaderboardResponse,
    CombatResultResponse, RegisterRequest, AuthUserResponse, UpdateUsernameRequest
)
from auth import generate_combat_code, generate_api_token, hash_token
from middleware import verify_admin_token, get_current_user_from_token
from firebase_auth import get_current_firebase_user, get_optional_firebase_user, get_firebase_user_record
from hf_datasets import question_service, verify_answer

app = FastAPI(title="Agent Fight Club API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TIME_LIMIT_SECONDS = int(os.getenv("TIME_LIMIT_SECONDS", "180"))
BASE_URL = os.getenv("BASE_URL", "http://localhost:3000")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_or_create_user_from_firebase(firebase_user: dict, db: Session) -> User:
    """Get existing user or create new one from Firebase auth."""
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if user:
        return user
    return None  # User needs to register with a handle first

def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison (lowercase, strip whitespace)"""
    if not answer:
        return ""
    return answer.strip().lower()

def check_answer_correct(submission_answer: str, golden_label: str) -> bool:
    """Check if submission answer matches the golden label (supports JSON format)"""
    if not submission_answer or not golden_label:
        return False
    
    # Try to parse as JSON (new HF format)
    try:
        label_data = json.loads(golden_label)
        if isinstance(label_data, dict) and "correct_answer" in label_data:
            correct = label_data["correct_answer"]
            return normalize_answer(submission_answer) == normalize_answer(correct)
    except (json.JSONDecodeError, TypeError):
        pass
    
    # Fallback to direct string comparison (old format)
    return normalize_answer(submission_answer) == normalize_answer(golden_label)

def check_answer_correct_hashed(submission_answer: str, answer_hash: str, combat_id: str) -> bool:
    """Check if submission answer matches using secure hash verification"""
    if not submission_answer or not answer_hash:
        return False
    # Convert combat_id to int for hash verification
    try:
        uuid_int = int(uuid.UUID(combat_id).int)
        combat_id_int = uuid_int % (10**9)  # Use part of UUID as int
    except:
        combat_id_int = hash(combat_id) % (10**9)
    return verify_answer(submission_answer, answer_hash, combat_id_int)

def determine_winner_and_update_stats(combat: Combat, db: Session):
    """
    Determine the winner of a combat and update user stats.
    Winner is determined by:
    1. First correct answer wins
    2. If both correct, earlier submission wins
    3. If neither correct, it's a draw
    4. If only one submitted, that person wins if correct, otherwise draw
    """
    if combat.winner_id is not None or combat.is_draw:
        # Already determined
        return
    
    user_a = db.query(User).filter(User.id == combat.user_a_id).first()
    user_b = db.query(User).filter(User.id == combat.user_b_id).first()
    
    if not user_a or not user_b:
        return
    
    # Check for new HF-based combat question first
    combat_question = db.query(CombatQuestion).filter(CombatQuestion.combat_id == combat.id).first()
    
    sub_a = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == combat.user_a_id
    ).first()
    
    sub_b = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == combat.user_b_id
    ).first()
    
    if combat_question:
        # Use secure hash verification for HF questions
        a_correct = sub_a and check_answer_correct_hashed(sub_a.answer, combat_question.answer_key_hash, combat.id)
        b_correct = sub_b and check_answer_correct_hashed(sub_b.answer, combat_question.answer_key_hash, combat.id)
    else:
        # Legacy: use golden_label from old Question table
        golden_label = combat.question.golden_label if combat.question else ""
        a_correct = sub_a and check_answer_correct(sub_a.answer, golden_label)
        b_correct = sub_b and check_answer_correct(sub_b.answer, golden_label)
    
    winner = None
    is_draw = False
    
    if a_correct and b_correct:
        # Both correct - earlier submission wins
        if sub_a.submitted_at <= sub_b.submitted_at:
            winner = user_a
        else:
            winner = user_b
    elif a_correct and not b_correct:
        winner = user_a
    elif b_correct and not a_correct:
        winner = user_b
    else:
        # Neither correct - it's a draw
        is_draw = True
    
    # Update combat
    if winner:
        combat.winner_id = winner.id
        combat.is_draw = 0
    else:
        combat.is_draw = 1
    
    # Update user stats
    user_a.total_combats += 1
    user_b.total_combats += 1
    
    if is_draw:
        user_a.draws += 1
        user_b.draws += 1
    elif winner.id == user_a.id:
        user_a.wins += 1
        user_b.losses += 1
    else:
        user_b.wins += 1
        user_a.losses += 1
    
    db.commit()

# ============================================================================
# AUTH API
# ============================================================================

@app.post("/api/auth/register", response_model=AuthUserResponse)
async def register_user(
    request: RegisterRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Register/update username for authenticated Firebase user."""
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    if user:
        # User exists, update username if provided and different
        if request.username and request.username != user.username:
            # Check if new username is taken by another user
            username_taken = db.query(User).filter(
                User.username == request.username,
                User.id != user.id
            ).first()
            if username_taken:
                raise HTTPException(status_code=400, detail="Username already taken")
            user.username = request.username
            db.commit()
            db.refresh(user)
    else:
        # Check if username is taken
        username_taken = db.query(User).filter(User.username == request.username).first()
        if username_taken:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create new user
        user = User(
            firebase_uid=firebase_user["uid"],
            email=firebase_user.get("email"),
            username=request.username
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        wins=user.wins,
        losses=user.losses,
        draws=user.draws,
        totalCombats=user.total_combats,
        score=user.score,
        rank=user.rank,
        createdAt=user.created_at
    )

@app.get("/api/auth/me", response_model=AuthUserResponse)
async def get_current_user(
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user's profile. Returns 404 if user doesn't exist."""
    # First try to find by firebase_uid
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    # If not found by firebase_uid, try by email
    if not user and firebase_user.get("email"):
        user = db.query(User).filter(User.email == firebase_user["email"]).first()
        if user:
            # Update the firebase_uid for this existing user
            user.firebase_uid = firebase_user["uid"]
            db.commit()
            db.refresh(user)
    
    # If user doesn't exist, return 404 - they need to register with a username
    if not user:
        raise HTTPException(status_code=404, detail="User not found. Please register with a username.")
    
    return AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        wins=user.wins,
        losses=user.losses,
        draws=user.draws,
        totalCombats=user.total_combats,
        score=user.score,
        rank=user.rank,
        createdAt=user.created_at
    )

@app.put("/api/auth/username", response_model=AuthUserResponse)
async def update_username(
    request: UpdateUsernameRequest,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Update the current user's username."""
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if username is already taken by another user
    existing = db.query(User).filter(
        User.username == request.username,
        User.id != user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Update username
    user.username = request.username
    db.commit()
    db.refresh(user)
    
    return AuthUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        wins=user.wins,
        losses=user.losses,
        draws=user.draws,
        totalCombats=user.total_combats,
        score=user.score,
        rank=user.rank,
        createdAt=user.created_at
    )

@app.get("/api/auth/check-username/{username}")
async def check_username_available(username: str, db: Session = Depends(get_db)):
    """Check if a username is available."""
    existing = db.query(User).filter(User.username == username).first()
    return {"available": existing is None}

# ============================================================================
# COMBAT API (Authenticated)
# ============================================================================

@app.post("/api/combats", response_model=CreateCombatResponse)
async def create_combat(
    request: CreateCombatRequest = CreateCombatRequest(),
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Create a new combat (requires authentication)"""
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered. Please register first.")
    
    # Validate mode
    mode = request.mode if request.mode in ["formal_logic", "argument_logic"] else "formal_logic"
    
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
        state=CombatState.CREATED,
        question_mode=mode
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
async def accept_combat(
    code: str,
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Accept a combat invitation (requires authentication)"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    if combat.state != CombatState.CREATED:
        raise HTTPException(status_code=400, detail="Combat already accepted or started")
    
    # Get authenticated user
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not registered. Please register first.")
    
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
            # Determine winner on expiration
            db.refresh(combat)
            determine_winner_and_update_stats(combat, db)
    
    countdown_seconds = None
    if combat.expires_at:
        remaining = (combat.expires_at - datetime.utcnow()).total_seconds()
        countdown_seconds = max(0, int(remaining))
    
    question_data = None
    if combat.state in [CombatState.RUNNING, CombatState.COMPLETED, CombatState.EXPIRED]:
        # Check for new HF-based combat question first
        combat_question = db.query(CombatQuestion).filter(CombatQuestion.combat_id == combat.id).first()
        if combat_question:
            question_data = {
                "prompt": combat_question.prompt,
                "choices": json.loads(combat_question.choices_json)
            }
        elif combat.question:
            # Legacy format - parse JSON golden_label for choices
            question_data = {"prompt": combat.question.prompt}
            try:
                label_data = json.loads(combat.question.golden_label)
                if isinstance(label_data, dict) and "choices" in label_data:
                    question_data["choices"] = label_data["choices"]
            except (json.JSONDecodeError, TypeError):
                pass
    
    submissions_status = None
    if combat.state in [CombatState.RUNNING, CombatState.COMPLETED, CombatState.EXPIRED]:
        submissions = db.query(Submission).filter(Submission.combat_id == combat.id).all()
        submissions_status = {}
        for sub in submissions:
            user = db.query(User).filter(User.id == sub.user_id).first()
            if user:
                submissions_status[user.username] = sub.status.value
        
        if combat.user_a_id and user_a.username not in submissions_status:
            submissions_status[user_a.username] = "timeout"
        if combat.user_b_id and user_b and user_b.username not in submissions_status:
            submissions_status[user_b.username] = "timeout"
    
    return CombatStatusResponse(
        combatId=combat.id,
        code=combat.code,
        state=combat.state,
        mode=getattr(combat, 'question_mode', 'formal_logic') or 'formal_logic',
        countdownSeconds=countdown_seconds,
        question=question_data,
        submissionsStatus=submissions_status,
        userAUsername=user_a.username if user_a else None,
        userBUsername=user_b.username if user_b else None,
        userAReady=bool(combat.user_a_ready),
        userBReady=bool(combat.user_b_ready),
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
    
    # Fetch question from HuggingFace datasets
    try:
        # Get combat_id as int for hashing
        combat_id_int = int(uuid.UUID(combat.id).int % (10**9))
        mode = getattr(combat, 'question_mode', 'formal_logic') or 'formal_logic'
        
        normalized_question, answer_hash = question_service.create_combat_question(
            combat_id=combat_id_int,
            mode=mode
        )
        
        # Store the combat question metadata
        combat_question = CombatQuestion(
            combat_id=combat.id,
            dataset=normalized_question.dataset,
            config=normalized_question.config,
            split=normalized_question.split,
            row_offset=normalized_question.row_offset,
            prompt=normalized_question.prompt,
            choices_json=json.dumps(normalized_question.choices),
            answer_key_hash=answer_hash
        )
        db.add(combat_question)
        
    except Exception as e:
        # Fallback to legacy local questions if HF fails
        print(f"HF question fetch failed: {e}, falling back to local questions")
        questions = db.query(Question).all()
        if not questions:
            raise HTTPException(status_code=500, detail=f"No questions available: {str(e)}")
        question = random.choice(questions)
        combat.question_id = question.id
    
    # Start combat
    combat.state = CombatState.RUNNING
    combat.started_at = datetime.utcnow()
    combat.expires_at = datetime.utcnow() + timedelta(seconds=TIME_LIMIT_SECONDS)
    
    # Store temporary plaintext keys for retrieval by both users
    temp_keys = TempApiKey(
        combat_id=combat.id,
        key_a=token_a,
        key_b=token_b,
        expires_at=datetime.utcnow() + timedelta(minutes=5)  # Keys expire in 5 minutes
    )
    db.add(temp_keys)
    
    # Set state to KEYS_ISSUED - waiting for both users to be ready
    combat.state = CombatState.KEYS_ISSUED
    
    db.commit()
    
    return IssueKeysResponse(
        keyA=token_a,
        keyB=token_b,
        instructionsUrl=f"{BASE_URL}/instructions"
    )

@app.post("/api/combats/{code}/ready")
def mark_user_ready(
    code: str,
    firebase_user = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Mark user as ready to start the combat. Timer starts when both are ready."""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    if combat.state not in [CombatState.KEYS_ISSUED, CombatState.RUNNING]:
        raise HTTPException(status_code=400, detail="Combat is not in ready state")
    
    # Get the user from our database
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Mark the appropriate user as ready
    if user.id == combat.user_a_id:
        combat.user_a_ready = 1
    elif user.id == combat.user_b_id:
        combat.user_b_ready = 1
    else:
        raise HTTPException(status_code=403, detail="Not a participant in this combat")
    
    # If both are ready, start the timer
    if combat.user_a_ready and combat.user_b_ready and combat.state == CombatState.KEYS_ISSUED:
        combat.state = CombatState.RUNNING
        combat.started_at = datetime.utcnow()
        combat.expires_at = datetime.utcnow() + timedelta(seconds=TIME_LIMIT_SECONDS)
    
    db.commit()
    
    return {
        "ok": True,
        "userAReady": bool(combat.user_a_ready),
        "userBReady": bool(combat.user_b_ready),
        "state": combat.state.value
    }

@app.get("/api/combats/{code}/my-key")
def get_my_api_key(
    code: str,
    firebase_user = Depends(get_current_firebase_user),
    db: Session = Depends(get_db)
):
    """Retrieve user's API key for a combat (only works once, keys are deleted after retrieval)"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    # Get current user
    user = db.query(User).filter(User.firebase_uid == firebase_user["uid"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is part of this combat
    if user.id not in [combat.user_a_id, combat.user_b_id]:
        raise HTTPException(status_code=403, detail="Not authorized for this combat")
    
    # Get temporary keys
    temp_keys = db.query(TempApiKey).filter(TempApiKey.combat_id == combat.id).first()
    if not temp_keys:
        raise HTTPException(status_code=404, detail="API keys not available")
    
    # Check if expired
    if datetime.utcnow() > temp_keys.expires_at:
        db.delete(temp_keys)
        db.commit()
        raise HTTPException(status_code=410, detail="API keys expired")
    
    # Return only the user's key
    my_key = temp_keys.key_a if user.id == combat.user_a_id else temp_keys.key_b
    
    return {"key": my_key}

@app.get("/agent/me", response_model=AgentMeResponse)
def agent_get_assignment(
    context: dict = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    """Get current combat assignment for agent"""
    combat = context["combat"]
    
    response = AgentMeResponse(
        combatId=combat.id,
        state=combat.state
    )
    
    if combat.state == CombatState.RUNNING:
        # Check for new HF-based combat question first
        combat_question = db.query(CombatQuestion).filter(CombatQuestion.combat_id == combat.id).first()
        if combat_question:
            response.prompt = combat_question.prompt
            response.choices = json.loads(combat_question.choices_json)
        elif combat.question:
            response.prompt = combat.question.prompt
            # Parse JSON golden_label for choices
            try:
                label_data = json.loads(combat.question.golden_label)
                if isinstance(label_data, dict) and "choices" in label_data:
                    response.choices = label_data["choices"]
            except (json.JSONDecodeError, TypeError):
                pass
        
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
        # Refresh combat to get latest state
        db.refresh(combat)
        # Determine winner and update stats
        determine_winner_and_update_stats(combat, db)
    else:
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
            userAUsername=user_a.username if user_a else "unknown",
            userBUsername=user_b.username if user_b else None,
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
# PUBLIC API: LEADERBOARD & USER PROFILES
# ============================================================================

@app.get("/api/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    limit: int = 50,
    rank: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get the leaderboard with rankings.
    Optional filter by rank tier: Bronze, Silver, Gold, Diamond, Professional
    """
    # Query all users with at least 1 combat
    query = db.query(User).filter(User.total_combats > 0)
    
    # Get all users for ranking calculation
    users = query.all()
    
    # Sort by score (wins * 3 + draws), then by wins, then by win rate
    def sort_key(u):
        score = u.score
        win_rate = u.wins / u.total_combats if u.total_combats > 0 else 0
        return (-score, -u.wins, -win_rate)
    
    sorted_users = sorted(users, key=sort_key)
    
    # Filter by rank if specified
    if rank:
        sorted_users = [u for u in sorted_users if u.rank.lower() == rank.lower()]
    
    # Build response with positions
    entries = []
    for idx, user in enumerate(sorted_users[:limit], start=1):
        win_rate = (user.wins / user.total_combats * 100) if user.total_combats > 0 else 0.0
        entries.append(LeaderboardEntryResponse(
            position=idx,
            username=user.username,
            wins=user.wins,
            losses=user.losses,
            draws=user.draws,
            totalCombats=user.total_combats,
            score=user.score,
            rank=user.rank,
            winRate=round(win_rate, 1)
        ))
    
    return LeaderboardResponse(
        entries=entries,
        totalUsers=len(sorted_users)
    )

@app.get("/api/users/{username}", response_model=UserProfileResponse)
def get_user_profile(username: str, db: Session = Depends(get_db)):
    """Get user profile with stats"""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserProfileResponse(
        username=user.username,
        wins=user.wins,
        losses=user.losses,
        draws=user.draws,
        totalCombats=user.total_combats,
        score=user.score,
        rank=user.rank,
        createdAt=user.created_at
    )

@app.get("/api/combats/{code}/result", response_model=CombatResultResponse)
def get_combat_result(code: str, db: Session = Depends(get_db)):
    """Get detailed combat result including winner"""
    combat = db.query(Combat).filter(Combat.code == code).first()
    if not combat:
        raise HTTPException(status_code=404, detail="Combat not found")
    
    if combat.state not in [CombatState.COMPLETED, CombatState.EXPIRED]:
        raise HTTPException(status_code=400, detail="Combat not finished yet")
    
    user_a = db.query(User).filter(User.id == combat.user_a_id).first()
    user_b = db.query(User).filter(User.id == combat.user_b_id).first()
    winner = db.query(User).filter(User.id == combat.winner_id).first() if combat.winner_id else None
    
    sub_a = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == combat.user_a_id
    ).first()
    sub_b = db.query(Submission).filter(
        Submission.combat_id == combat.id,
        Submission.user_id == combat.user_b_id
    ).first()
    
    # Check for new HF-based combat question
    combat_question = db.query(CombatQuestion).filter(CombatQuestion.combat_id == combat.id).first()
    correct_answer = None
    
    if combat_question:
        # Use hash verification for HF questions
        combat_id_int = int(uuid.UUID(combat.id).int % (10**9))
        a_correct = sub_a and check_answer_correct_hashed(sub_a.answer, combat_question.answer_key_hash, combat.id)
        b_correct = sub_b and check_answer_correct_hashed(sub_b.answer, combat_question.answer_key_hash, combat.id)
        # Reveal the actual correct answer by checking which choice matches the hash
        choices = json.loads(combat_question.choices_json)
        for choice in choices:
            if check_answer_correct_hashed(choice, combat_question.answer_key_hash, combat.id):
                correct_answer = choice
                break
        if not correct_answer:
            correct_answer = f"One of: {', '.join(choices)}"
    else:
        # Legacy format
        golden_label = combat.question.golden_label if combat.question else ""
        a_correct = sub_a and check_answer_correct(sub_a.answer, golden_label)
        b_correct = sub_b and check_answer_correct(sub_b.answer, golden_label)
        correct_answer = golden_label
    
    return CombatResultResponse(
        combatId=combat.id,
        winnerId=combat.winner_id,
        winnerUsername=winner.username if winner else None,
        isDraw=bool(combat.is_draw),
        userAUsername=user_a.username if user_a else "unknown",
        userBUsername=user_b.username if user_b else "unknown",
        userACorrect=bool(a_correct),
        userBCorrect=bool(b_correct),
        userAAnswer=sub_a.answer if sub_a else None,
        userBAnswer=sub_b.answer if sub_b else None,
        correctAnswer=correct_answer
    )

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
