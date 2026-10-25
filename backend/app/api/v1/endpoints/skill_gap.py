from fastapi import APIRouter, HTTPException
from backend.app.schemas.skill import GapAnalysisRequest
from backend.app.services.gap_analyzer import gap_analyzer

router = APIRouter()

SUPPORTED_ROLES = ["frontend", "backend", "fullstack", "data", "devops", "mobile"]

@router.post("/analyze")
def analyze_gaps(payload: GapAnalysisRequest):
    target_role = payload.target_role.lower().strip()
    if target_role not in SUPPORTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported role '{payload.target_role}'. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
        )
    return gap_analyzer.analyze_gaps(target_role, payload.candidate_skills)
