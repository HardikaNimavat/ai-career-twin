from pydantic import BaseModel, Field
from typing import Optional

class SalaryEstimateRequest(BaseModel):
    role: str = Field("frontend", description="Target job role")
    skill_match_pct: float = Field(..., ge=0.0, le=100.0, description="Readiness percentage 0-100")
    experience_years: float = Field(0.5, ge=0.0, le=30.0, description="Years of professional experience")
    location: str = Field("Ahmedabad", description="Regional tech hub city")
    github_score: float = Field(70.0, ge=0.0, le=100.0, description="Developer maturity score 0-100")

class SalaryEstimateResponse(BaseModel):
    role: str
    location: str
    min_lpa: float
    max_lpa: float
    median_lpa: float
    demand_trend: str
    currency: str = "INR (Lakhs per Annum)"
