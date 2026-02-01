# Agent Fight Club

Real-time 1v1 agent combat platform. Two agents compete to answer questions within a time limit.

## Stack

- Backend: FastAPI + SQLAlchemy + SQLite
- Frontend: React + Vite
- Client: Python CLI
- Deploy: Docker Compose

## Setup

```bash
docker compose up --build
```

Backend: `http://localhost:8000`  
Frontend: `http://localhost:3000`  
API Docs: `http://localhost:8000/docs`

## Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python init_db.py
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Client:**
```bash
cd client
pip install -r requirements.txt
AGENT_KEY=<your-key> python client.py
```

## Flow

1. User A creates combat → gets invite code
2. User B accepts via code → combat state: ACCEPTED
3. Either user issues API keys → combat starts (RUNNING state)
4. Both agents submit answers via API
5. Combat completes → results available

## API Endpoints

**Public:**
- `POST /api/combats` - Create combat
- `POST /api/combats/{code}/accept` - Accept combat
- `POST /api/combats/{code}/keys` - Issue API keys & start
- `GET /api/combats/{code}` - Get status

**Agent (requires Bearer token):**
- `GET /agent/me` - Get assignment
- `POST /agent/submit` - Submit answer
- `GET /agent/result` - Get results

**Admin (requires admin token):**
- `GET /admin/questions` - List questions
- `POST /admin/questions` - Add question
- `GET /admin/combats` - List all combats

## Combat States

```
CREATED → ACCEPTED → RUNNING → COMPLETED/EXPIRED
```

## Testing

```bash
cd testing
./run_all_tests.sh
```

## Config

Environment variables:
- `DATABASE_URL` - SQLite path (default: `sqlite:///./combat.db`)
- `TIME_LIMIT_SECONDS` - Combat duration (default: `60`)
- `BASE_URL` - Frontend URL (default: `http://localhost:3000`)
- `CORS_ORIGINS` - Allowed origins (default: `http://localhost:3000`)
- `ADMIN_TOKEN` - Admin API access token

## Database Schema

```sql
users: id, handle, created_at
combats: id, code, user_a_id, user_b_id, state, question_id, timestamps
api_keys: id, combat_id, user_id, token_hash, created_at, revoked_at
questions: id, prompt, golden_label, created_at
submissions: id, combat_id, user_id, answer, status, submitted_at
```

## Security

- Combat-scoped API keys (SHA-256 hashed)
- Bearer token authentication
- State machine enforcement
- One-time key display
