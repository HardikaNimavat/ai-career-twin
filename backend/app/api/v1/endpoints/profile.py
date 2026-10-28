import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.schemas.profile import ResumeParseRequest, DigitalTwinResponse
from backend.app.models.user import User
from backend.app.models.profile import UserProfile
from backend.app.models.roadmap import UserRoadmap
from backend.app.models.exam import ExamSession, SkillHistory
from backend.app.models.interview import InterviewSession
from backend.app.api.deps import get_current_user
from backend.app.services.skill_extractor import skill_extractor
from backend.app.services.github_analyzer import github_analyzer
from backend.app.services.gap_analyzer import gap_analyzer
from backend.app.services.salary_predictor import salary_predictor
from backend.app.services.trajectory_predictor import trajectory_predictor
from backend.app.services.ats_service import ats_service
from backend.app.services.interview_service import interview_service
from backend.app.services.personalization_engine import personalization_engine

logger = logging.getLogger(__name__)

router = APIRouter()

SUPPORTED_ROLES = ["frontend", "backend", "fullstack", "data", "devops", "mobile"]

@router.post("/parse", response_model=DigitalTwinResponse)
def parse_and_generate_twin(
    payload: ResumeParseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_role = payload.target_role.lower().strip()
    if target_role not in SUPPORTED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported role '{payload.target_role}'. Supported roles are: {', '.join(SUPPORTED_ROLES)}"
        )

    gh_handle = (payload.github_username or (current_user and current_user.username) or "HardikaNimavat").strip().lstrip("@")

    # If resume text is not supplied, auto-synthesize from GitHub profile and repository activity
    if not payload.resume_text or not payload.resume_text.strip():
        gh_quick = github_analyzer.analyze_profile(gh_handle, {})
        top_langs = gh_quick.get("top_languages", ["JavaScript", "HTML", "CSS", "Python"])
        notes = " ".join(gh_quick.get("diagnostic_notes", []))
        payload.resume_text = (
            f"Developer Profile: {gh_handle}\n"
            f"Target Career Track: {target_role.capitalize()}\n"
            f"Public Repositories: {gh_quick.get('public_repos', 1)}\n"
            f"Primary Technical Languages: {', '.join(top_langs)}\n"
            f"Engineering Activity: {notes}\n"
            f"Demonstrated Competencies: {', '.join(top_langs)}, Git, GitHub, REST APIs, System Design, Problem Solving."
        )

    # 1. Skill Extraction
    extracted = skill_extractor.extract_skills(payload.resume_text)
    
    # 2. GitHub Intelligence
    gh_stats = github_analyzer.analyze_profile(payload.github_username, extracted["detected_skills"])

    # 3. Gap Analysis
    gap_result = gap_analyzer.analyze_gaps(target_role, extracted["detected_skills"])

    # 4. AI-Personalized Roadmap (FREE courses only)
    class TempProfile:
        def __init__(self, role, skills, exp, pid=None):
            self.id = pid
            self.target_role = role
            self.detected_skills = skills
            self.experience_years = exp

    temp_profile = TempProfile(
        target_role,
        extracted["detected_skills"],
        extracted["experience_years"]
    )
    roadmap = personalization_engine.generate_personalized_roadmap(
        temp_profile, gap_result["gap_rows"]
    )

    # 5. Salary Prediction (Default location: Ahmedabad)
    salary = salary_predictor.estimate_salary(
        role=target_role,
        skill_match_pct=gap_result["readiness_percentage"],
        exp_years=extracted["experience_years"],
        location="Ahmedabad",
        github_score=gh_stats["quality_score"]
    )

    # 6. Trajectory Prediction
    trajectory = trajectory_predictor.predict_progression(
        target_role=target_role,
        current_readiness=gap_result["readiness_percentage"],
        exp_years=extracted["experience_years"],
        learning_hours_weekly=14.0,
        github_score=gh_stats["quality_score"]
    )

    # 7. ATS & CV Match Recommendations
    ats_eval = ats_service.evaluate_cv(
        resume_text=payload.resume_text,
        detected_skills=extracted["detected_skills"],
        target_role=target_role
    )

    # 8. Pre-generate Dynamic MCQs
    mcqs = interview_service.generate_dynamic_mcqs(
        role=target_role,
        detected_skills=extracted["detected_skills"],
        count=5,
        resume_text=payload.resume_text
    )

    # Persist in SQLite Database (Both Profile & Roadmap) linked to authenticated user
    profile_id = None
    try:
        user_record = UserProfile(
            user_id=current_user.id,
            public_id=str(uuid.uuid4()),
            target_role=target_role,
            raw_resume_text=payload.resume_text[:2000],
            detected_skills=extracted["detected_skills"],
            experience_years=extracted["experience_years"],
            dominant_cluster=extracted["dominant_cluster"],
            github_username=payload.github_username,
            github_quality_score=gh_stats["quality_score"],
            github_public_repos=gh_stats["public_repos"],
            github_contributions=gh_stats["contributions_per_year"],
            github_language_dist=dict(zip(gh_stats["top_languages"], gh_stats["language_weights"])),
            github_diagnostic_notes=gh_stats["diagnostic_notes"],
            readiness_percentage=gap_result["readiness_percentage"],
            estimated_salary_min=salary["min_lpa"],
            estimated_salary_max=salary["max_lpa"]
        )
        db.add(user_record)
        db.flush()  # Populates user_record.id
        profile_id = user_record.id

        # Persist generated roadmap into user_roadmaps table
        roadmap_record = UserRoadmap(
            user_id=current_user.id,
            profile_id=user_record.id,
            target_role=target_role,
            total_weeks=len(roadmap),
            total_hours=sum(m.get("estimated_hours", 8) for m in roadmap),
            milestones=roadmap
        )
        db.add(roadmap_record)
        db.commit()
        logger.info("[+] Saved UserProfile #%s and UserRoadmap #%s for User #%s", user_record.id, roadmap_record.id, current_user.id)
    except Exception as e:
        db.rollback()
        logger.error("DB Persistence error: %s", e)

    return {
        "profile": extracted,
        "github": gh_stats,
        "target_role": target_role,
        "readiness_percentage": gap_result["readiness_percentage"],
        "gap_analysis": gap_result["gap_rows"],
        "roadmap": roadmap,
        "salary_estimate": salary,
        "trajectory_prediction": trajectory,
        "ats_analysis": ats_eval,
        "mcqs": mcqs,
        "profile_id": profile_id
    }

@router.delete("/me")
def delete_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Removes all of the user's data (profile, roadmap, exams, skill history)."""
    user_profiles = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).all()
    profile_ids = [p.id for p in user_profiles]

    if profile_ids:
        db.query(SkillHistory).filter(
            (SkillHistory.user_id == current_user.id) | (SkillHistory.profile_id.in_(profile_ids))
        ).delete(synchronize_session=False)

        db.query(ExamSession).filter(
            (ExamSession.user_id == current_user.id) | (ExamSession.profile_id.in_(profile_ids))
        ).delete(synchronize_session=False)

        db.query(InterviewSession).filter(
            (InterviewSession.user_id == current_user.id) | (InterviewSession.profile_id.in_(profile_ids))
        ).delete(synchronize_session=False)

        db.query(UserRoadmap).filter(
            (UserRoadmap.user_id == current_user.id) | (UserRoadmap.profile_id.in_(profile_ids))
        ).delete(synchronize_session=False)
    else:
        db.query(SkillHistory).filter(SkillHistory.user_id == current_user.id).delete(synchronize_session=False)
        db.query(ExamSession).filter(ExamSession.user_id == current_user.id).delete(synchronize_session=False)
        db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).delete(synchronize_session=False)
        db.query(UserRoadmap).filter(UserRoadmap.user_id == current_user.id).delete(synchronize_session=False)

    db.query(UserProfile).filter(UserProfile.user_id == current_user.id).delete(synchronize_session=False)
    db.commit()

    logger.info("Deleted all data for user #%s (%s)", current_user.id, current_user.email)
    return {"message": "All user profile and associated twin data have been successfully deleted."}

@router.get("/me/export")
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data for data privacy and portability."""
    user_profiles = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).all()
    profile_ids = [p.id for p in user_profiles]

    roadmaps = db.query(UserRoadmap).filter(
        (UserRoadmap.user_id == current_user.id) | (UserRoadmap.profile_id.in_(profile_ids))
    ).all() if profile_ids else []

    exams = db.query(ExamSession).filter(
        (ExamSession.user_id == current_user.id) | (ExamSession.profile_id.in_(profile_ids))
    ).all() if profile_ids else []

    skill_history = db.query(SkillHistory).filter(
        (SkillHistory.user_id == current_user.id) | (SkillHistory.profile_id.in_(profile_ids))
    ).all() if profile_ids else []

    interviews = db.query(InterviewSession).filter(
        (InterviewSession.user_id == current_user.id) | (InterviewSession.profile_id.in_(profile_ids))
    ).all() if profile_ids else []

    return {
        "user": {
            "id": current_user.id,
            "public_id": current_user.public_id,
            "email": current_user.email,
            "username": current_user.username,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None
        },
        "profiles": [
            {
                "id": p.id,
                "public_id": p.public_id,
                "target_role": p.target_role,
                "detected_skills": p.detected_skills,
                "experience_years": p.experience_years,
                "github_username": p.github_username,
                "readiness_percentage": p.readiness_percentage,
                "estimated_salary_min": p.estimated_salary_min,
                "estimated_salary_max": p.estimated_salary_max,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in user_profiles
        ],
        "roadmaps": [
            {
                "id": r.id,
                "profile_id": r.profile_id,
                "target_role": r.target_role,
                "total_weeks": r.total_weeks,
                "total_hours": r.total_hours,
                "milestones": r.milestones,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in roadmaps
        ],
        "exam_sessions": [
            {
                "id": e.id,
                "profile_id": e.profile_id,
                "exam_type": e.exam_type,
                "target_role": e.target_role,
                "total_score": e.total_score,
                "accuracy_pct": e.accuracy_pct,
                "created_at": e.created_at.isoformat() if e.created_at else None
            }
            for e in exams
        ],
        "skill_history": [
            {
                "id": sh.id,
                "profile_id": sh.profile_id,
                "skill_name": sh.skill_name,
                "old_confidence": sh.old_confidence,
                "new_confidence": sh.new_confidence,
                "change_amount": sh.change_amount,
                "change_source": sh.change_source,
                "created_at": sh.created_at.isoformat() if sh.created_at else None
            }
            for sh in skill_history
        ],
        "interviews": [
            {
                "id": i.id,
                "profile_id": i.profile_id,
                "target_role": i.target_role,
                "technical_score": i.technical_score,
                "overall_score": i.overall_score,
                "created_at": i.created_at.isoformat() if i.created_at else None
            }
            for i in interviews
        ]
    }

@router.get("/{profile_id}")
def get_user_digital_twin(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve full dynamic digital twin for an existing profile. Enforces ownership: returns 404 for other users' IDs."""
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Profile not found.")

    twin = personalization_engine.recalculate_full_twin(db, profile_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return twin

@router.post("/{profile_id}/recalculate")
def recalculate_user_digital_twin(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Recalculate dynamic digital twin with latest skills and roadmap. Enforces ownership: returns 404 for other users' IDs."""
    profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
    if not profile or (profile.user_id is not None and profile.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Profile not found.")

    twin = personalization_engine.recalculate_full_twin(db, profile_id)
    if not twin:
        raise HTTPException(status_code=404, detail="Profile not found.")
    return twin
