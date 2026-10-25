import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

import uuid

client = TestClient(app)
_reg = client.post("/api/v1/auth/register", json={
    "email": f"test_roles_{uuid.uuid4().hex[:8]}@example.com",
    "password": "Password123!"
})
if _reg.status_code == 201:
    client.headers["Authorization"] = f"Bearer {_reg.json()['access_token']}"

SAMPLE_RESUME = """Hardika Nimavat
B.Tech Computer Science & Engineering | Indus University, Ahmedabad (2022–2026)

PROFESSIONAL SUMMARY:
Enthusiastic Computer Engineering student with a strong foundation in core web technologies including HTML/CSS and introductory JavaScript. Built personal static projects and a portfolio website using CSS Flexbox/Grid and DOM scripting. Comfortable using Git for version control and collaborating on GitHub repositories. Eager to master modern engineering frameworks and system architecture to build production-grade scalable applications.

CORE FOUNDATIONAL SKILLS:
- Languages: JavaScript (ES6+ basics), HTML/CSS, C++, Python (basics)
- Version Control: Git, GitHub
- Concepts: Responsive Web Design, DOM Manipulation, Problem Solving

ACADEMIC PROJECTS:
1. Interactive Portfolio Website — Built with HTML5 semantic tags, custom CSS animations, and JavaScript event listeners.
2. Web Calculator & Task Tracker — Client-side web application leveraging JavaScript local storage and responsive CSS layout."""

ROLES = ["frontend", "backend", "data", "devops", "fullstack", "mobile"]

@pytest.mark.parametrize("role", ROLES)
def test_role_twin_generation(role):
    payload = {
        "resume_text": SAMPLE_RESUME,
        "github_username": "hardika-nimavat-dev",
        "target_role": role
    }
    res = client.post("/api/v1/profile/parse", json=payload)
    assert res.status_code == 200, f"Role {role} failed: {res.text}"
    data = res.json()
    assert "readiness_percentage" in data
    assert "gap_analysis" in data
    assert isinstance(data["gap_analysis"], list)
    assert len(data["gap_analysis"]) > 0

def test_all_roles_summary():
    for role in ROLES:
        payload = {
            "resume_text": SAMPLE_RESUME,
            "github_username": "hardika-nimavat-dev",
            "target_role": role
        }
        res = client.post("/api/v1/profile/parse", json=payload)
        assert res.status_code == 200

import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    for role in ROLES:
        payload = {
            "resume_text": SAMPLE_RESUME,
            "github_username": "hardika-nimavat-dev",
            "target_role": role
        }
        res = client.post("/api/v1/profile/parse", json=payload)
        logger.info("Role: %s -> %s", role, res.status_code)
