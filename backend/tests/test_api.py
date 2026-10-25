import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.profile import UserProfile
from backend.app.models.roadmap import UserRoadmap

import uuid

client = TestClient(app)
_reg = client.post("/api/v1/auth/register", json={
    "email": f"test_api_{uuid.uuid4().hex[:8]}@example.com",
    "password": "Password123!"
})
if _reg.status_code == 201:
    client.headers["Authorization"] = f"Bearer {_reg.json()['access_token']}"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.parametrize("role", ["frontend", "backend", "fullstack", "data", "devops", "mobile"])
def test_all_supported_roles_parse_and_generate(role):
    payload = {
        "resume_text": "Hardika Nimavat. B.Tech Computer Engineering student with foundational knowledge of HTML/CSS, JavaScript, and Git. Built static portfolio projects.",
        "github_username": "hardika-nimavat-dev",
        "target_role": role
    }
    response = client.post("/api/v1/profile/parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_role"] == role
    assert "profile" in data
    assert "ats_analysis" in data
    assert data["ats_analysis"]["role_coverage"]["total_required"] > 0
    assert "mcqs" in data and len(data["mcqs"]) >= 3
    assert len(data["roadmap"]) >= 0
    assert data["salary_estimate"]["min_lpa"] > 0

def test_dynamic_mcq_generation_endpoint():
    payload = {
        "role": "backend",
        "detected_skills": {"Node.js": 80.0, "SQL": 85.0, "Git": 70.0},
        "count": 5,
        "resume_text": "Hardika Nimavat - Backend Developer with Node.js, SQL, Git"
    }
    resp = client.post("/api/v1/interview/generate-mcqs", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["mcqs"]) == 5
    assert all("options" in q and "correct_index" in q and "explanation" in q for q in data["mcqs"])
    assert all("skill" in q and "deficiency_diagnostic" in q for q in data["mcqs"])

def test_evaluate_mcq_session_diagnostics():
    eval_payload = {
        "role": "backend",
        "answers": [
            {
                "id": "node_1",
                "skill": "Node.js",
                "topic": "Event Loop",
                "question": "What runs first?",
                "selected_index": 0,
                "is_correct": True,
                "deficiency_diagnostic": "Lacking event loop knowledge."
            },
            {
                "id": "sql_1",
                "skill": "SQL",
                "topic": "Indexing",
                "question": "Why B-Trees?",
                "selected_index": 0,
                "is_correct": False,
                "deficiency_diagnostic": "Lacks fundamental knowledge of SQL database indexing."
            }
        ]
    }
    resp = client.post("/api/v1/interview/evaluate-mcq-session", json=eval_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_questions"] == 2
    assert data["correct_count"] == 1
    assert data["accuracy_pct"] == 50
    assert data["clearance_status"] == "CLEARANCE BLOCKED"
    assert len(data["diagnostics"]) == 2
    assert data["diagnostics"][0]["status_badge"] == "MASTERED"
    assert data["diagnostics"][1]["status_badge"] == "SKILL GAP DETECTED"

def test_certificate_verification_with_ats_boost():
    payload = {
        "filename": "react-advanced-coursera-cert.pdf",
        "target_role": "frontend",
        "current_skills": {"HTML/CSS": 85.0, "JavaScript": 80.0}
    }
    response = client.post("/api/v1/certificate/verify", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verified"] is True
    assert data["skill"] == "React"
    assert data["score_boost"] == 25.0
    assert "updated_ats_analysis" in data
    assert data["updated_ats_analysis"] is not None
    assert data["updated_ats_analysis"]["role_coverage"]["matched_count"] == 3
