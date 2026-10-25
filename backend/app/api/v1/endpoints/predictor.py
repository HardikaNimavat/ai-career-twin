from fastapi import APIRouter
from backend.app.schemas.prediction import TrajectoryRequest, TrajectoryResponse
from backend.app.services.trajectory_predictor import trajectory_predictor

router = APIRouter()

@router.post("/trajectory", response_model=TrajectoryResponse)
def predict_trajectory(payload: TrajectoryRequest):
    return trajectory_predictor.predict_progression(
        target_role=payload.target_role,
        current_readiness=payload.current_readiness,
        exp_years=payload.experience_years,
        learning_hours_weekly=payload.learning_hours_weekly,
        github_score=payload.github_score
    )
