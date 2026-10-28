from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DynamicMCQRequest(BaseModel):
    role: str
    detected_skills: Dict[str, float] = Field(default_factory=dict)
    count: int = 5
    resume_text: Optional[str] = ""

class MCQItem(BaseModel):
    id: str
    skill: Optional[str] = "General"
    topic: str
    question: str
    options: List[str]
    deficiency_diagnostic: Optional[str] = ""
    correct_index: Optional[int] = None
    explanation: Optional[str] = None

class MCQListResponse(BaseModel):
    exam_id: Optional[str] = "mcq-session-default"
    role: str
    mcqs: List[MCQItem]
    time_limit_seconds: int = 1800

class UserAnswerItem(BaseModel):
    id: str
    selected_index: int
    # Client-supplied evaluation fields are strictly ignored by server
    question: Optional[str] = None
    skill: Optional[str] = None
    topic: Optional[str] = None
    is_correct: Optional[bool] = None
    deficiency_diagnostic: Optional[str] = None

class EvaluateMCQSessionRequest(BaseModel):
    exam_id: Optional[str] = None
    answers: List[UserAnswerItem]
    role: Optional[str] = "frontend"  # Optional role field

class DiagnosticItem(BaseModel):
    question_id: Optional[str] = ""
    skill: str
    topic: str
    is_correct: bool
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    status_badge: str
    diagnostic_message: str

class EvaluateMCQSessionResponse(BaseModel):
    exam_id: Optional[str] = None
    overall_score: int
    accuracy_pct: int
    total_questions: int
    correct_count: int
    clearance_status: str
    is_cleared: bool
    diagnostics: List[DiagnosticItem]
    summary: str

class QuestionListResponse(BaseModel):
    role: str
    questions: List[Dict[str, Any]]

class ScoreAnswerRequest(BaseModel):
    role: str
    question: str
    answer_text: str

class ScoreAnswerResponse(BaseModel):
    technical_score: float
    clarity_score: float
    confidence_score: float
    overall_score: float
    is_valid_answer: bool
    detected_concepts: List[str]
    missing_concepts: List[str]
    model_answer: str
    feedback_notes: str
