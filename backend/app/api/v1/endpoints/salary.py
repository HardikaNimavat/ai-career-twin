from fastapi import APIRouter
from backend.app.schemas.salary import SalaryEstimateRequest, SalaryEstimateResponse
from backend.app.services.salary_predictor import salary_predictor

router = APIRouter()

@router.post("/estimate", response_model=SalaryEstimateResponse)
def estimate_salary(payload: SalaryEstimateRequest):
    return salary_predictor.estimate_salary(
        role=payload.role,
        skill_match_pct=payload.skill_match_pct,
        exp_years=payload.experience_years,
        location=payload.location,
        github_score=payload.github_score
    )
