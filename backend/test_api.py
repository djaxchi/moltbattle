import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import app
from database import Base, get_db
from models import User, Combat, ApiKey, Question, CombatState

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_question(db):
    """Create a sample question"""
    question = Question(
        prompt="What is 2+2?",
        golden_label='{"answer": "4"}'
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

def test_health_check(client):
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_combat(client):
    """Test combat creation"""
    response = client.post("/api/combats", json={"handle": "TestUser"})
    assert response.status_code == 200
    data = response.json()
    assert "combatId" in data
    assert "code" in data
    assert "inviteUrl" in data
    assert len(data["code"]) == 6

def test_accept_combat(client):
    """Test combat acceptance"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    
    accept_response = client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    assert accept_response.status_code == 200
    data = accept_response.json()
    assert data["state"] == "ACCEPTED"

def test_cannot_accept_own_combat(client):
    """Test that user cannot accept their own combat"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    
    accept_response = client.post(f"/api/combats/{code}/accept", json={"handle": "UserA"})
    assert accept_response.status_code == 400

def test_cannot_accept_twice(client):
    """Test that combat cannot be accepted twice"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    
    second_accept = client.post(f"/api/combats/{code}/accept", json={"handle": "UserC"})
    assert second_accept.status_code == 400

def test_issue_keys(client, sample_question):
    """Test API key issuance"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    
    keys_response = client.post(f"/api/combats/{code}/keys")
    assert keys_response.status_code == 200
    data = keys_response.json()
    assert "keyA" in data
    assert "keyB" in data
    assert data["keyA"] != data["keyB"]
    
    status_response = client.get(f"/api/combats/{code}")
    assert status_response.json()["state"] == "RUNNING"

def test_cannot_issue_keys_twice(client, sample_question):
    """Test that keys cannot be issued twice"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    
    client.post(f"/api/combats/{code}/keys")
    
    second_keys = client.post(f"/api/combats/{code}/keys")
    assert second_keys.status_code == 400

def test_agent_auth_required(client):
    """Test that agent endpoints require authentication"""
    response = client.get("/agent/me")
    assert response.status_code == 401

def test_agent_invalid_token(client):
    """Test that invalid tokens are rejected"""
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/agent/me", headers=headers)
    assert response.status_code == 401

def test_agent_submit_answer(client, sample_question):
    """Test agent answer submission"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    keys_response = client.post(f"/api/combats/{code}/keys")
    key_a = keys_response.json()["keyA"]
    
    headers = {"Authorization": f"Bearer {key_a}"}
    submit_response = client.post(
        "/agent/submit",
        headers=headers,
        json={"answer": "My answer"}
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["ok"] == True

def test_cannot_submit_twice(client, sample_question):
    """Test that user cannot submit answer twice"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    keys_response = client.post(f"/api/combats/{code}/keys")
    key_a = keys_response.json()["keyA"]
    
    headers = {"Authorization": f"Bearer {key_a}"}
    
    client.post("/agent/submit", headers=headers, json={"answer": "Answer 1"})
    
    second_submit = client.post("/agent/submit", headers=headers, json={"answer": "Answer 2"})
    assert second_submit.status_code == 400

def test_combat_completes_after_both_submit(client, sample_question):
    """Test that combat completes after both users submit"""
    create_response = client.post("/api/combats", json={"handle": "UserA"})
    code = create_response.json()["code"]
    client.post(f"/api/combats/{code}/accept", json={"handle": "UserB"})
    keys_response = client.post(f"/api/combats/{code}/keys")
    key_a = keys_response.json()["keyA"]
    key_b = keys_response.json()["keyB"]
    
    client.post("/agent/submit", headers={"Authorization": f"Bearer {key_a}"}, json={"answer": "Answer A"})
    client.post("/agent/submit", headers={"Authorization": f"Bearer {key_b}"}, json={"answer": "Answer B"})
    
    status_response = client.get(f"/api/combats/{code}")
    assert status_response.json()["state"] == "COMPLETED"

def test_admin_endpoints_require_auth(client):
    """Test that admin endpoints require authentication"""
    response = client.get("/admin/combats")
    assert response.status_code == 401

def test_admin_can_list_combats(client):
    """Test admin can list combats"""
    headers = {"Authorization": "Bearer admin-secret-token"}
    response = client.get("/admin/combats", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
