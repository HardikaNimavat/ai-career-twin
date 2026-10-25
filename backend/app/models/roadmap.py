from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from datetime import datetime, timezone
from backend.app.core.database import Base

class UserRoadmap(Base):
    __tablename__ = "user_roadmaps"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=True)
    target_role = Column(String(50), nullable=False)
    total_weeks = Column(Integer, default=4)
    total_hours = Column(Integer, default=40)
    milestones = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
