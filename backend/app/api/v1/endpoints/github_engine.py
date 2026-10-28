from fastapi import APIRouter, Query, Body, HTTPException, status
from typing import Optional
from backend.app.services.github_analyzer import github_analyzer

router = APIRouter()

@router.get("/verify")
def verify_github_user_get(username: str = Query(..., description="GitHub account handle")):
    """
    Checks if a GitHub user exists and returns public profile metadata.
    """
    res = github_analyzer.verify_user(username)
    if not res.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error", f"GitHub user '{username}' not found.")
        )
    return res

@router.post("/verify")
def verify_github_user_post(payload: dict = Body(...)):
    """
    POST payload: {"username": "HardikaNimavat"}
    Checks if a GitHub user exists and returns public profile metadata.
    """
    username = payload.get("username") or payload.get("github_username")
    res = github_analyzer.verify_user(username)
    if not res.get("valid"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error", f"GitHub user '{username}' not found.")
        )
    return res

@router.get("/analyze")
def analyze_github(username: Optional[str] = Query("HardikaNimavat")):
    dummy_skills = {"JavaScript": 80.0, "React": 75.0, "Node.js": 70.0}
    return github_analyzer.analyze_profile(username, dummy_skills)

