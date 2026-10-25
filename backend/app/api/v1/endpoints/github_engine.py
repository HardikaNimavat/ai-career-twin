from fastapi import APIRouter, Query
from typing import Optional
from backend.app.services.github_analyzer import github_analyzer

router = APIRouter()

@router.get("/analyze")
def analyze_github(username: Optional[str] = Query("octocat")):
    dummy_skills = {"JavaScript": 80.0, "React": 75.0, "Node.js": 70.0}
    return github_analyzer.analyze_profile(username, dummy_skills)
