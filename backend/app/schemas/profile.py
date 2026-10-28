from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

class ResumeParseRequest(BaseModel):
    resume_text: Optional[str] = Field("", description="Plain text or parsed resume contents")
    github_username: Optional[str] = Field(None, description="GitHub profile handle")
    target_role: str = Field("frontend", description="Selected target dream role")

class DetectedProfile(BaseModel):
    detected_skills: Dict[str, float]
    experience_years: float
    dominant_cluster: str
    skills_count: int

class GitHubAnalysisResult(BaseModel):
    username: str
    quality_score: float
    public_repos: int
    contributions_per_year: int
    top_languages: List[str]
    language_weights: List[int]
    diagnostic_notes: List[str]
    avatar_url: Optional[str] = None
    name: Optional[str] = None
    bio: Optional[str] = None
    html_url: Optional[str] = None

class DigitalTwinResponse(BaseModel):
    profile: DetectedProfile
    github: GitHubAnalysisResult
    target_role: str
    readiness_percentage: float
    gap_analysis: List[Dict[str, Any]]
    roadmap: List[Dict[str, Any]]
    salary_estimate: Dict[str, Any]
    trajectory_prediction: Dict[str, Any]
    ats_analysis: Optional[Dict[str, Any]] = None
    mcqs: Optional[List[Dict[str, Any]]] = None
    profile_id: Optional[int] = None

