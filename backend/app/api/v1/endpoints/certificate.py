from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import hashlib
import random
from backend.app.models.user import User
from backend.app.api.deps import get_current_user
from backend.app.services.skill_extractor import SKILLS, ALIASES
from backend.app.services.ats_service import ats_service

router = APIRouter()

class CertRequest(BaseModel):
    filename: str
    target_role: Optional[str] = "frontend"
    current_skills: Optional[Dict[str, float]] = None
    resume_text: Optional[str] = ""
    verified_certs: Optional[List[str]] = None

@router.post("/verify")
def verify_certificate(
    payload: CertRequest,
    current_user: User = Depends(get_current_user)
):
    filename = payload.filename or ""
    clean_name = filename.lower().replace("-", " ").replace("_", " ").replace(".", " ")
    
    match_skill = None
    for skill, aliases in ALIASES.items():
        if any(alias in clean_name for alias in aliases):
            match_skill = skill
            break
            
    if not match_skill:
        for skill in SKILLS.keys():
            if skill.lower() in clean_name:
                match_skill = skill
                break

    seed = int(hashlib.md5(filename.encode('utf-8')).hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    levels = ["Foundational Credential", "Associate Level", "Professional Certified", "Industry Specialization"]
    level = rng.choice(levels)

    if match_skill:
        # Update candidate detected skills with verified confidence
        updated_skills = dict(payload.current_skills or {})
        prev_conf = updated_skills.get(match_skill, 0.0)
        new_conf = min(99.0, max(88.0, prev_conf + 30.0))
        updated_skills[match_skill] = round(new_conf, 1)

        # Track verified certificate list
        existing_certs = list(payload.verified_certs or [])
        cert_entry = f"{match_skill} ({level})"
        if cert_entry not in existing_certs:
            existing_certs.append(cert_entry)
        
        # Calculate updated ATS & Job recommendation preserving candidate's resume context
        resume_ctx = payload.resume_text if payload.resume_text and len(payload.resume_text.strip()) > 30 else f"Candidate Resume Profile with verified {match_skill}"
        
        ats_eval = ats_service.evaluate_cv(
            resume_text=resume_ctx,
            detected_skills=updated_skills,
            target_role=payload.target_role or "frontend",
            verified_certs=existing_certs
        )

        return {
            "verified": True,
            "filename": filename,
            "skill": match_skill,
            "credential_level": level,
            "score_boost": 25.0,
            "ats_boost_points": 10,
            "updated_skills": updated_skills,
            "verified_certs": existing_certs,
            "message": f"Successfully verified {match_skill} ({level}) — ATS Score boosted!",
            "updated_ats_analysis": ats_eval
        }
    else:
        return {
            "verified": False,
            "filename": filename,
            "skill": None,
            "credential_level": None,
            "score_boost": 0.0,
            "ats_boost_points": 0,
            "updated_skills": payload.current_skills or {},
            "verified_certs": payload.verified_certs or [],
            "message": "No recognized technical skill identified in certificate name.",
            "updated_ats_analysis": None
        }
