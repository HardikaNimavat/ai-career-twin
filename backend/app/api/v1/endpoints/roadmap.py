from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.api.deps import get_current_user
from backend.app.services.personalization_engine import personalization_engine
from backend.app.services.roadmap_generator import roadmap_generator

router = APIRouter()


class GenerateRoadmapRequest(BaseModel):
    gap_rows: List[Dict[str, Any]]
    experience_years: Optional[float] = 0.5
    target_role: Optional[str] = "frontend"
    detected_skills: Optional[Dict[str, float]] = Field(default_factory=dict)
    profile_id: Optional[int] = None


@router.post("/generate")
def generate_roadmap(
    payload: GenerateRoadmapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an AI-personalized or adaptive learning roadmap.
    Guarantees ONLY 100% FREE courses.
    Requires authentication; enforces profile ownership.
    """
    if payload.profile_id:
        profile = db.query(UserProfile).filter(UserProfile.id == payload.profile_id).first()
        if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
            raise HTTPException(status_code=404, detail="Profile not found.")
        return personalization_engine.generate_personalized_roadmap(profile, payload.gap_rows)

    class DummyProfile:
        def __init__(self, role, exp, skills, uid):
            self.target_role = role
            self.experience_years = exp
            self.detected_skills = skills
            self.id = uid

    profile = DummyProfile(payload.target_role, payload.experience_years, payload.detected_skills, current_user.id)
    return personalization_engine.generate_personalized_roadmap(profile, payload.gap_rows)
