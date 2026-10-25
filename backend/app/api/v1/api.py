from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    profile,
    github_engine,
    skill_gap,
    predictor,
    salary,
    roadmap,
    interview,
    certificate,
    exam,
    resume_upload
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Accounts"])
api_router.include_router(profile.router, prefix="/profile", tags=["Profile & Digital Twin"])
api_router.include_router(resume_upload.router, prefix="/resume", tags=["Resume Upload (PDF/Image)"])
api_router.include_router(github_engine.router, prefix="/github", tags=["GitHub Engine"])
api_router.include_router(skill_gap.router, prefix="/gap", tags=["Skill Gap Analysis"])
api_router.include_router(predictor.router, prefix="/predictor", tags=["Career Predictor"])
api_router.include_router(salary.router, prefix="/salary", tags=["Salary & Market Intelligence"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["Learning Roadmap"])
api_router.include_router(interview.router, prefix="/interview", tags=["AI Interview Simulator"])
api_router.include_router(certificate.router, prefix="/certificate", tags=["Certificate Verification"])
api_router.include_router(exam.router, prefix="/exam", tags=["Multi-Format Exam Engine"])
