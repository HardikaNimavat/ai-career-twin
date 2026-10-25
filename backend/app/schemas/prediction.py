from pydantic import BaseModel, Field
from typing import Dict, Optional

class TrajectoryRequest(BaseModel):
    target_role: str = Field("frontend", description="Target job role")
    current_readiness: float = Field(..., ge=0.0, le=100.0, description="Current match percentage 0-100")
    experience_years: float = Field(0.5, ge=0.0, le=30.0, description="Years of experience")
    learning_hours_weekly: float = Field(14.0, ge=1.0, le=80.0, description="Hours dedicated per week to studying")
    github_score: float = Field(70.0, ge=0.0, le=100.0, description="Developer maturity score 0-100")

class TrajectoryResponse(BaseModel):
    target_role: str
    prob_3m: float
    prob_6m: float
    prob_12m: float
    readiness_3m: float
    readiness_6m: float
    readiness_12m: float
    summary: str
