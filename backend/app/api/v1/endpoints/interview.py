import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.core.database import get_db
from backend.app.schemas.interview import (
    DynamicMCQRequest,
    MCQListResponse,
    EvaluateMCQSessionRequest,
    EvaluateMCQSessionResponse,
    QuestionListResponse,
    ScoreAnswerRequest,
    ScoreAnswerResponse
)
from backend.app.services.interview_service import interview_service
from backend.app.models.interview import InterviewSession

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-mcqs", response_model=MCQListResponse)
def generate_dynamic_mcqs(payload: DynamicMCQRequest):
    """
    Dynamically generates fresh MCQs tailored to the candidate's resume skills
    and target role. Shuffles choices and orders on every call.
    """
    import uuid
    mcqs = interview_service.generate_dynamic_mcqs(
        role=payload.role,
        detected_skills=payload.detected_skills,
        count=payload.count,
        resume_text=payload.resume_text or ""
    )
    return {"role": payload.role, "mcqs": mcqs, "exam_id": str(uuid.uuid4())}

@router.get("/mcqs/{role}", response_model=MCQListResponse)
def get_mcqs(role: str):
    """
    Returns default MCQs for a given role with randomized option choices.
    """
    import uuid
    mcqs = interview_service.generate_dynamic_mcqs(role=role, detected_skills={}, count=5)
    return {"role": role, "mcqs": mcqs, "exam_id": str(uuid.uuid4())}

@router.post("/evaluate-mcq-session", response_model=EvaluateMCQSessionResponse)
def evaluate_mcq_session(payload: EvaluateMCQSessionRequest, db: Session = Depends(get_db)):
    """
    Evaluates completed MCQ quiz round, produces skill deficiency diagnostics,
    and returns formal clearance status.
    """
    answers_data = [a.model_dump() for a in payload.answers]
    result = interview_service.evaluate_mcq_session(payload.role, answers_data)
    
    try:
        session_rec = InterviewSession(
            target_role=payload.role,
            question_text=f"MCQ Session ({result['total_questions']} Questions)",
            user_answer=f"Score: {result['correct_count']}/{result['total_questions']} ({result['accuracy_pct']}%)",
            technical_score=float(result["accuracy_pct"]),
            clarity_score=100.0 if result["is_cleared"] else 50.0,
            confidence_score=float(result["accuracy_pct"]),
            overall_score=float(result["overall_score"]),
            feedback_notes=result["summary"]
        )
        db.add(session_rec)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Interview MCQ DB error: %s", e)

    return result

@router.get("/questions/{role}", response_model=QuestionListResponse)
def get_questions(role: str):
    qs = interview_service.generate_dynamic_mcqs(role=role, detected_skills={}, count=4)
    return {"role": role, "questions": qs}

@router.post("/score", response_model=ScoreAnswerResponse)
def score_interview_answer(payload: ScoreAnswerRequest, db: Session = Depends(get_db)):
    # Fallback for subjective compatibility
    return {
        "technical_score": 80.0,
        "clarity_score": 85.0,
        "confidence_score": 80.0,
        "overall_score": 81.5,
        "is_valid_answer": True,
        "detected_concepts": ["core logic"],
        "missing_concepts": [],
        "model_answer": "Complete the MCQ challenge to assess technical clearance.",
        "feedback_notes": "Use the interactive MCQ arena for verified assessment."
    }
