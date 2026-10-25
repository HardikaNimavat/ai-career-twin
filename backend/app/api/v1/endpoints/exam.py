"""
Multi-Format Exam API Endpoints.

Supports: MCQ, Code, Essay, Debug, System Design, Mixed exams.
All questions are AI-generated and personalized to the user's weak skills.
Results automatically update the digital twin via personalization engine.
Protected with JWT authentication and strict ownership verification.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.exam import (
    GenerateExamRequest, SubmitExamRequest,
    ExamEvaluationResponse
)
from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.models.exam import ExamSession
from backend.app.api.deps import get_current_user
from backend.app.services.exam_engine import exam_engine
from backend.app.services.personalization_engine import personalization_engine

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_TYPES = ["mcq", "code", "essay", "debug", "design", "mixed"]
SUPPORTED_ROLES = ["frontend", "backend", "fullstack", "data", "devops", "mobile"]


@router.post("/generate")
def generate_exam(
    payload: GenerateExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a personalized multi-format exam."""
    role = payload.role.lower().strip()
    if role not in SUPPORTED_ROLES:
        raise HTTPException(status_code=400, detail=f"Unsupported role '{role}'.")

    exam_type = payload.exam_type.lower().strip()
    if exam_type not in SUPPORTED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported exam type '{exam_type}'. Supported: {', '.join(SUPPORTED_TYPES)}"
        )

    # If profile_id is provided, verify ownership and fetch user's weak skills automatically
    detected_skills = dict(payload.detected_skills)
    weak_skills = list(payload.weak_skills)

    if payload.profile_id:
        profile = db.query(UserProfile).filter(UserProfile.id == payload.profile_id).first()
        if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
            raise HTTPException(status_code=404, detail="Profile not found.")
        if not detected_skills:
            detected_skills = dict(profile.detected_skills or {})
        # Auto-detect weak skills from gap analysis
        if not weak_skills:
            from backend.app.services.gap_analyzer import gap_analyzer
            gap_result = gap_analyzer.analyze_gaps(role, detected_skills)
            weak_skills = [
                r["skill"] for r in gap_result.get("gap_rows", [])
                if r.get("match_pct", 100) < 60
            ][:5]

    exam = exam_engine.generate_exam(
        role=role,
        exam_type=exam_type,
        count=payload.count,
        difficulty=payload.difficulty,
        detected_skills=detected_skills,
        weak_skills=weak_skills,
        resume_text=payload.resume_text or ""
    )

    return exam


@router.post("/submit")
def submit_exam(
    payload: SubmitExamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit exam answers for evaluation and auto-update digital twin."""
    role = payload.role.lower().strip()
    exam_type = payload.exam_type.lower().strip()

    if not payload.answers:
        raise HTTPException(status_code=400, detail="No answers submitted.")

    detected_skills = {}
    if payload.profile_id:
        profile = db.query(UserProfile).filter(UserProfile.id == payload.profile_id).first()
        if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
            raise HTTPException(status_code=404, detail="Profile not found.")
        detected_skills = dict(profile.detected_skills or {})

    # Convert Pydantic models to dicts
    answers_data = [a.model_dump() for a in payload.answers]
    questions_data = payload.questions or []

    # Run evaluation with complexity benchmarks
    evaluation = exam_engine.evaluate_exam(
        role=role,
        exam_type=exam_type,
        questions=questions_data,
        answers=answers_data,
        detected_skills=detected_skills
    )

    # Save exam session to database
    try:
        exam_session = ExamSession(
            user_id=current_user.id,
            profile_id=payload.profile_id,
            exam_type=exam_type,
            target_role=role,
            difficulty_level=evaluation.get("difficulty", "intermediate"),
            answers=answers_data,
            scores={r["question_id"]: r["score"] for r in evaluation.get("results", [])},
            total_score=evaluation["overall_score"],
            accuracy_pct=evaluation["accuracy_pct"],
            total_questions=evaluation["total_questions"],
            correct_count=evaluation["correct_count"],
            time_taken_seconds=payload.total_time_seconds or 0,
            clearance_status=evaluation["clearance_status"],
            is_cleared=evaluation["is_cleared"],
            diagnostics=evaluation.get("results", []),
            summary=evaluation["summary"],
            skill_updates=evaluation.get("skill_updates", {}),
            twin_updated=True
        )
        db.add(exam_session)
        db.flush()

        # Auto-update digital twin via personalization engine
        if payload.profile_id and evaluation.get("skill_updates"):
            twin_result = personalization_engine.apply_skill_updates(
                db=db,
                profile_id=payload.profile_id,
                skill_updates=evaluation["skill_updates"],
                source=f"exam_{exam_type}",
                exam_session_id=exam_session.id
            )
            evaluation["new_readiness_pct"] = twin_result.get("new_readiness_pct")
            evaluation["new_skills"] = twin_result.get("new_skills", {})
            evaluation["new_gap_analysis"] = twin_result.get("new_gap_analysis", [])
            evaluation["new_salary_estimate"] = twin_result.get("new_salary_estimate", {})
            evaluation["new_trajectory"] = twin_result.get("new_trajectory", {})
            evaluation["new_roadmap"] = twin_result.get("new_roadmap", [])
            evaluation["new_ats_analysis"] = twin_result.get("new_ats_analysis")
            evaluation["skill_changes"] = twin_result.get("skill_changes", [])

        db.commit()
        logger.info("[+] Saved ExamSession #%s and updated twin for profile %s (User #%s)", exam_session.id, payload.profile_id, current_user.id)
    except Exception as e:
        db.rollback()
        logger.error("[!] Exam save error: %s", e)

    return evaluation


@router.get("/history/{profile_id}")
def get_exam_history(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get exam history for a user profile. Enforces ownership: returns 404 for other users' profiles."""
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Profile not found.")

    sessions = (
        db.query(ExamSession)
        .filter(ExamSession.profile_id == profile_id)
        .order_by(ExamSession.created_at.desc())
        .limit(20)
        .all()
    )

    return {
        "profile_id": profile_id,
        "total_exams": len(sessions),
        "sessions": [
            {
                "id": s.id,
                "exam_type": s.exam_type,
                "target_role": s.target_role,
                "difficulty_level": s.difficulty_level,
                "total_score": s.total_score,
                "accuracy_pct": s.accuracy_pct,
                "total_questions": s.total_questions,
                "correct_count": s.correct_count,
                "time_taken_seconds": s.time_taken_seconds,
                "clearance_status": s.clearance_status,
                "is_cleared": s.is_cleared,
                "summary": s.summary,
                "created_at": s.created_at.isoformat() if s.created_at else None
            }
            for s in sessions
        ]
    }


@router.get("/progression/{profile_id}")
def get_skill_progression(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skill progression history for a user profile. Enforces ownership: returns 404 for other users' profiles."""
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Profile not found.")

    return personalization_engine.get_skill_progression(db, profile_id)
