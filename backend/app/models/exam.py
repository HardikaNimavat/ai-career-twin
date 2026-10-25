"""
ExamSession and SkillHistory database models.

ExamSession: Tracks every exam taken (MCQ, code, essay, debug, design)
SkillHistory: Logs every skill confidence change with timestamp for tracking progression
"""

import uuid
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON, Boolean
from datetime import datetime, timezone
from backend.app.core.database import Base


class ExamSession(Base):
    """Tracks each exam session with questions, answers, scores, and twin updates."""
    __tablename__ = "exam_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=True, index=True)
    exam_type = Column(String(20), nullable=False, default="mcq")  # mcq, code, essay, debug, design
    target_role = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced

    # Exam content & results
    questions = Column(JSON, default=list)           # Full question objects (server-side answer keys)
    answers = Column(JSON, default=list)             # User's answers
    scores = Column(JSON, default=dict)              # Per-question scores
    total_score = Column(Float, default=0.0)
    accuracy_pct = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, default=0)
    time_limit_seconds = Column(Integer, default=1800)

    # Lifecycle state: "generated", "submitted", "expired"
    status = Column(String(20), default="generated", index=True)
    submitted_at = Column(DateTime, nullable=True)

    # Diagnostics
    clearance_status = Column(String(30), default="PENDING")
    is_cleared = Column(Boolean, default=False)
    diagnostics = Column(JSON, default=list)          # Skill-by-skill breakdown
    summary = Column(Text, nullable=True)

    # Skill updates triggered by this exam
    skill_updates = Column(JSON, default=dict)       # {"React": +10, "Node.js": -5}
    twin_updated = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SkillHistory(Base):
    """Tracks skill confidence changes over time for progression visualization."""
    __tablename__ = "skill_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    old_confidence = Column(Float, default=0.0)
    new_confidence = Column(Float, default=0.0)
    change_amount = Column(Float, default=0.0)       # Positive = improvement
    change_source = Column(String(50), nullable=False)  # exam_mcq, exam_code, exam_essay, certificate, manual
    exam_session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
