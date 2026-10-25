import uuid
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
from backend.app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=True)
    target_role = Column(String(50), nullable=False, default="frontend")
    raw_resume_text = Column(Text, nullable=True)
    detected_skills = Column(JSON, nullable=False, default=dict)
    experience_years = Column(Float, default=0.0)
    dominant_cluster = Column(String(50), nullable=True)
    
    # GitHub Intelligence Scores
    github_username = Column(String(100), nullable=True)
    github_quality_score = Column(Float, default=0.0)
    github_public_repos = Column(Integer, default=0)
    github_contributions = Column(Integer, default=0)
    github_language_dist = Column(JSON, default=dict)
    github_diagnostic_notes = Column(JSON, default=list)

    # Readiness
    readiness_percentage = Column(Float, default=0.0)
    estimated_salary_min = Column(Float, default=0.0)
    estimated_salary_max = Column(Float, default=0.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
