import uuid
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.models.roadmap import UserRoadmap

def get_new_client():
    return TestClient(app)

def create_user(client: TestClient, email: str = None, password: str = "StrongPass123!"):
    if email is None:
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "username": f"u_{uuid.uuid4().hex[:6]}"
    })
    assert resp.status_code == 201, f"Failed to register user: {resp.text}"
    token = resp.json()["access_token"]
    user_data = resp.json()["user"]
    auth_headers = {"Authorization": f"Bearer {token}"}
    return email, password, token, user_data, auth_headers

def test_user_registration_and_login():
    client = get_new_client()
    email = f"register_{uuid.uuid4().hex[:8]}@example.com"
    password = "SecurePassword123!"

    # 1. Register
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == email

    # 2. Duplicate registration fails
    dup_resp = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password
    })
    assert dup_resp.status_code == 400

    # 3. Login with correct password
    login_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

    # 4. Login with wrong password fails (401)
    wrong_resp = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "WrongPassword!"
    })
    assert wrong_resp.status_code == 401

def test_unauthenticated_access_rejected_with_401():
    client = get_new_client()
    # Profile routes
    assert client.post("/api/v1/profile/parse", json={"resume_text": "text"}).status_code == 401
    assert client.get("/api/v1/profile/1").status_code == 401
    assert client.delete("/api/v1/profile/me").status_code == 401
    assert client.get("/api/v1/profile/me/export").status_code == 401

    # Exam routes
    assert client.post("/api/v1/exam/generate", json={"role": "frontend"}).status_code == 401
    assert client.post("/api/v1/exam/submit", json={"role": "frontend", "answers": []}).status_code == 401
    assert client.get("/api/v1/exam/history/1").status_code == 401

    # Roadmap route
    assert client.post("/api/v1/roadmap/generate", json={"gap_rows": []}).status_code == 401

    # Certificate route
    assert client.post("/api/v1/certificate/verify", json={"filename": "cert.pdf"}).status_code == 401

def test_cookie_authentication_supported():
    client = get_new_client()
    _, _, token, _, _ = create_user(client)
    # Clear authorization header, set cookie
    client.headers.pop("Authorization", None)
    client.cookies.set("access_token", token)

    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    assert "email" in resp.json()

def test_profile_ownership_enforcement_returns_404_not_403():
    client1 = get_new_client()
    _, _, _, _, headers1 = create_user(client1)

    client2 = get_new_client()
    _, _, _, _, headers2 = create_user(client2)

    # User 1 creates a profile
    create_resp = client1.post("/api/v1/profile/parse", json={
        "resume_text": "Candidate resume with Python, SQL, and Git experience.",
        "target_role": "backend"
    }, headers=headers1)
    assert create_resp.status_code == 200
    profile_id = create_resp.json()["profile_id"]
    assert profile_id is not None

    # User 1 can view their own profile
    u1_view = client1.get(f"/api/v1/profile/{profile_id}", headers=headers1)
    assert u1_view.status_code == 200

    # User 2 attempts to view User 1's profile -> MUST return 404 (IDOR protection)
    u2_view = client2.get(f"/api/v1/profile/{profile_id}", headers=headers2)
    assert u2_view.status_code == 404
    assert u2_view.json()["detail"] == "Profile not found."

    # User 2 attempts to recalculate User 1's profile -> MUST return 404
    u2_recalc = client2.post(f"/api/v1/profile/{profile_id}/recalculate", headers=headers2)
    assert u2_recalc.status_code == 404

    # User 2 attempts to view exam history for User 1's profile -> MUST return 404
    u2_exam_hist = client2.get(f"/api/v1/exam/history/{profile_id}", headers=headers2)
    assert u2_exam_hist.status_code == 404

    # User 2 attempts to generate roadmap using User 1's profile -> MUST return 404
    u2_roadmap = client2.post("/api/v1/roadmap/generate", json={
        "gap_rows": [{"skill": "Python", "match_pct": 50}],
        "profile_id": profile_id
    }, headers=headers2)
    assert u2_roadmap.status_code == 404

def test_delete_profile_me_and_export():
    client = get_new_client()
    _, _, _, user_data, headers = create_user(client)

    # 1. Create a profile and roadmap
    parse_resp = client.post("/api/v1/profile/parse", json={
        "resume_text": "Software engineer with React, JavaScript, and CSS.",
        "target_role": "frontend"
    }, headers=headers)
    assert parse_resp.status_code == 200
    profile_id = parse_resp.json()["profile_id"]

    # 2. Export user data (privacy endpoint)
    export_resp = client.get("/api/v1/profile/me/export", headers=headers)
    assert export_resp.status_code == 200
    exp_data = export_resp.json()
    assert exp_data["user"]["id"] == user_data["id"]
    assert len(exp_data["profiles"]) >= 1
    assert exp_data["profiles"][0]["id"] == profile_id
    assert len(exp_data["roadmaps"]) >= 1

    # 3. Delete user data
    del_resp = client.delete("/api/v1/profile/me", headers=headers)
    assert del_resp.status_code == 200
    assert "successfully deleted" in del_resp.json()["message"]

    # 4. Profile is now gone
    get_resp = client.get(f"/api/v1/profile/{profile_id}", headers=headers)
    assert get_resp.status_code == 404

    # 5. Export now shows empty profiles list
    export_after = client.get("/api/v1/profile/me/export", headers=headers)
    assert export_after.status_code == 200
    assert len(export_after.json()["profiles"]) == 0

def test_github_verification_and_session():
    client = get_new_client()

    # 1. Verify valid GitHub user
    resp_valid = client.get("/api/v1/github/verify?username=HardikaNimavat")
    assert resp_valid.status_code == 200
    data = resp_valid.json()
    assert data["valid"] is True
    assert "username" in data

    # 2. Verify invalid GitHub user fails with 404
    resp_invalid = client.get("/api/v1/github/verify?username=invalid_user_never_exists_129471924")
    assert resp_invalid.status_code == 404

    # 3. Establish session directly with GitHub account (zero passwords, zero signup)
    session_resp = client.post("/api/v1/auth/github-session", json={
        "github_username": "HardikaNimavat"
    })
    assert session_resp.status_code == 200
    s_data = session_resp.json()
    assert "access_token" in s_data
    token = s_data["access_token"]
    assert s_data["user"]["username"] == "HardikaNimavat"

    # 4. Generate digital twin using ONLY GitHub handle (resume text completely optional)
    auth_headers = {"Authorization": f"Bearer {token}"}
    twin_resp = client.post("/api/v1/profile/parse", json={
        "github_username": "HardikaNimavat",
        "target_role": "frontend",
        "resume_text": ""
    }, headers=auth_headers)
    assert twin_resp.status_code == 200
    twin = twin_resp.json()
    assert twin["github"]["username"] in ["HardikaNimavat", "hardikanimavat"]
    assert len(twin["roadmap"]) >= 1
    assert twin["salary_estimate"]["median_lpa"] > 0

