"""
Personalization Engine — Per-user dynamic recalculation of digital twin.

Handles:
- Skill confidence updates after exams
- Skill history tracking
- Dynamic roadmap regeneration on skill changes (100% free courses only)
- Gap analysis recalculation
- Salary and trajectory ML re-estimation

Time Complexity: O(s) where s = number of skills per recalculation
Space Complexity: O(h) where h = history entries per user
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.profile import UserProfile
from backend.app.models.roadmap import UserRoadmap
from backend.app.models.exam import ExamSession, SkillHistory
from backend.app.services.gap_analyzer import gap_analyzer
from backend.app.services.salary_predictor import salary_predictor
from backend.app.services.trajectory_predictor import trajectory_predictor
from backend.app.services.roadmap_generator import roadmap_generator
from backend.app.services.ai_service import ai_service
from backend.app.services.ats_service import ats_service

logger = logging.getLogger(__name__)


class PersonalizationEngine:
    """
    Per-user personalization engine that keeps the digital twin live and dynamic.
    Every exam, certificate, or manual update triggers a full recalculation.
    """

    def apply_skill_updates(
        self,
        db: Session,
        profile_id: int,
        skill_updates: Dict[str, float],
        source: str = "exam_mcq",
        exam_session_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Apply skill confidence changes to a user's profile and record history.
        Immediately recalculates gap analysis, salary, trajectory ML, and personalized roadmap.
        """
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            logger.warning(f"Profile {profile_id} not found for skill updates.")
            return {"error": "Profile not found"}

        current_skills = dict(profile.detected_skills or {})
        history_entries = []

        for skill, delta in skill_updates.items():
            old_conf = current_skills.get(skill, 0.0)
            new_conf = max(0.0, min(100.0, old_conf + delta))
            current_skills[skill] = round(new_conf, 1)

            # Record history
            history = SkillHistory(
                profile_id=profile_id,
                skill_name=skill,
                old_confidence=round(old_conf, 1),
                new_confidence=round(new_conf, 1),
                change_amount=round(delta, 1),
                change_source=source,
                exam_session_id=exam_session_id,
                notes=f"{'+' if delta > 0 else ''}{delta:.1f}% from {source}"
            )
            db.add(history)
            history_entries.append({
                "skill": skill,
                "old": round(old_conf, 1),
                "new": round(new_conf, 1),
                "delta": round(delta, 1)
            })

        # Update profile with new skills
        profile.detected_skills = current_skills

        # 1. Recalculate gap analysis
        gap_result = gap_analyzer.analyze_gaps(profile.target_role, current_skills)
        profile.readiness_percentage = gap_result["readiness_percentage"]

        # 2. Recalculate salary estimate
        github_score = profile.github_quality_score or 0.0
        salary = salary_predictor.estimate_salary(
            role=profile.target_role,
            skill_match_pct=gap_result["readiness_percentage"],
            exp_years=profile.experience_years,
            location="Ahmedabad",
            github_score=github_score
        )
        profile.estimated_salary_min = salary["min_lpa"]
        profile.estimated_salary_max = salary["max_lpa"]

        # 3. Recalculate ML Career Trajectory
        trajectory = trajectory_predictor.predict_progression(
            target_role=profile.target_role,
            current_readiness=gap_result["readiness_percentage"],
            exp_years=profile.experience_years,
            learning_hours_weekly=14.0,
            github_score=github_score
        )

        # 4. Dynamically Regenerate Personalized Roadmap (100% Free Courses only)
        roadmap = self.generate_personalized_roadmap(profile, gap_result["gap_rows"])

        # Update or create UserRoadmap record
        try:
            roadmap_rec = db.query(UserRoadmap).filter(UserRoadmap.profile_id == profile_id).first()
            if roadmap_rec:
                roadmap_rec.milestones = roadmap
                roadmap_rec.total_weeks = len(roadmap)
                roadmap_rec.total_hours = sum(m.get("estimated_hours", 8) for m in roadmap)
            else:
                roadmap_rec = UserRoadmap(
                    profile_id=profile_id,
                    target_role=profile.target_role,
                    total_weeks=len(roadmap),
                    total_hours=sum(m.get("estimated_hours", 8) for m in roadmap),
                    milestones=roadmap
                )
                db.add(roadmap_rec)
        except Exception as e:
            logger.warning(f"Could not update roadmap record: {e}")

        try:
            db.commit()
            logger.info(f"Updated {len(skill_updates)} skills for profile {profile_id}. New readiness: {gap_result['readiness_percentage']}%")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to save skill updates: {e}")
            return {"error": str(e)}

        # Invalidate AI cache for this user
        ai_service.invalidate_user_cache()

        # 5. Recalculate ATS & Job Match Recommendations based on updated skills
        try:
            resume_text = profile.raw_resume_text or ""
            ats_eval = ats_service.evaluate_cv(
                resume_text=resume_text,
                detected_skills=current_skills,
                target_role=profile.target_role
            )
        except Exception as e:
            logger.warning(f"ATS evaluation error during skill update: {e}")
            ats_eval = None

        return {
            "profile_id": profile_id,
            "skill_changes": history_entries,
            "new_skills": current_skills,
            "new_readiness_pct": gap_result["readiness_percentage"],
            "new_gap_analysis": gap_result["gap_rows"],
            "new_salary_estimate": salary,
            "new_trajectory": trajectory,
            "new_roadmap": roadmap,
            "new_ats_analysis": ats_eval,
            "source": source
        }

    def get_skill_progression(self, db: Session, profile_id: int) -> Dict[str, Any]:
        """
        Get skill progression history for a user.
        Returns timeline data for visualization.
        """
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            return {"error": "Profile not found", "history": []}

        history = (
            db.query(SkillHistory)
            .filter(SkillHistory.profile_id == profile_id)
            .order_by(SkillHistory.created_at.asc())
            .all()
        )

        exam_count = (
            db.query(ExamSession)
            .filter(ExamSession.profile_id == profile_id)
            .count()
        )

        history_items = []
        for h in history:
            history_items.append({
                "skill_name": h.skill_name,
                "old_confidence": h.old_confidence,
                "new_confidence": h.new_confidence,
                "change_amount": h.change_amount,
                "change_source": h.change_source,
                "notes": h.notes,
                "created_at": h.created_at.isoformat() if h.created_at else None
            })

        if history_items:
            total_positive = sum(h["change_amount"] for h in history_items if h["change_amount"] > 0)
            total_negative = sum(h["change_amount"] for h in history_items if h["change_amount"] < 0)
            summary = (
                f"You've taken {exam_count} assessments. "
                f"Total skill improvement: +{total_positive:.1f}%. "
                f"Areas to revisit: {abs(total_negative):.1f}% flagged for review."
            )
        else:
            summary = "No exam history yet. Take an exam to start tracking your dynamic digital twin progress!"

        return {
            "profile_id": profile_id,
            "history": history_items,
            "current_skills": dict(profile.detected_skills or {}),
            "total_exams_taken": exam_count,
            "improvement_summary": summary
        }

    def generate_personalized_roadmap(
        self,
        profile: Any,
        gap_rows: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate a game-like chained staged roadmap strictly with 100% FREE YouTube & platform courses.
        """
        return roadmap_generator.generate_roadmap(
            gap_rows=gap_rows,
            experience_years=getattr(profile, "experience_years", 0.5),
            target_role=getattr(profile, "target_role", "frontend"),
            detected_skills=getattr(profile, "detected_skills", {})
        )

    def recalculate_full_twin(self, db: Session, profile_id: int) -> Optional[Dict[str, Any]]:
        """
        Full recalculation of a user's digital twin.
        Called after exam completion, certificate verification, or role switch.
        """
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        if not profile:
            return None

        current_skills = dict(profile.detected_skills or {})
        target_role = profile.target_role

        # 1. Gap analysis
        gap_result = gap_analyzer.analyze_gaps(target_role, current_skills)
        profile.readiness_percentage = gap_result["readiness_percentage"]

        # 2. Salary prediction
        github_score = profile.github_quality_score or 0.0
        salary = salary_predictor.estimate_salary(
            role=target_role,
            skill_match_pct=gap_result["readiness_percentage"],
            exp_years=profile.experience_years,
            location="Ahmedabad",
            github_score=github_score
        )
        profile.estimated_salary_min = salary["min_lpa"]
        profile.estimated_salary_max = salary["max_lpa"]

        # 3. ML Career Trajectory
        trajectory = trajectory_predictor.predict_progression(
            target_role=target_role,
            current_readiness=gap_result["readiness_percentage"],
            exp_years=profile.experience_years,
            learning_hours_weekly=14.0,
            github_score=github_score
        )

        # 4. Personalized Roadmap (100% Free Courses)
        roadmap = self.generate_personalized_roadmap(profile, gap_result["gap_rows"])

        # Update UserRoadmap record
        try:
            roadmap_rec = db.query(UserRoadmap).filter(UserRoadmap.profile_id == profile_id).first()
            if roadmap_rec:
                roadmap_rec.milestones = roadmap
                roadmap_rec.total_weeks = len(roadmap)
                roadmap_rec.total_hours = sum(m.get("estimated_hours", 8) for m in roadmap)
            else:
                roadmap_rec = UserRoadmap(
                    profile_id=profile_id,
                    target_role=target_role,
                    total_weeks=len(roadmap),
                    total_hours=sum(m.get("estimated_hours", 8) for m in roadmap),
                    milestones=roadmap
                )
                db.add(roadmap_rec)
        except Exception as e:
            logger.warning(f"Could not update roadmap record: {e}")

        try:
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to recalculate twin: {e}")

        return {
            "profile_id": profile_id,
            "skills": current_skills,
            "readiness_percentage": gap_result["readiness_percentage"],
            "gap_analysis": gap_result["gap_rows"],
            "roadmap": roadmap,
            "salary_estimate": salary,
            "trajectory_prediction": trajectory
        }


# Singleton instance
personalization_engine = PersonalizationEngine()
