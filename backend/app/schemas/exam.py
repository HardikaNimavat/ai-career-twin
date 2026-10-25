"""
Exam schemas — Pydantic request/response models for the multi-format exam system.
Includes Time Complexity, Space Complexity, Accuracy, and Dynamic Twin updates.
Safe client-facing models strictly hide answer keys and expected evaluation criteria.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ─── Exam Generation Request ───
class GenerateExamRequest(BaseModel):
    """Request to generate a personalized exam."""
    profile_id: Optional[int] = None
    role: str = Field("frontend", description="Target role for the exam")
    exam_type: str = Field("mcq", description="Exam type: mcq, code, essay, debug, design, mixed")
    count: int = Field(5, description="Number of questions", ge=1, le=20)
    difficulty: str = Field("intermediate", description="Difficulty: beginner, intermediate, advanced")
    detected_skills: Dict[str, float] = Field(default_factory=dict)
    weak_skills: List[str] = Field(default_factory=list, description="Skills to focus on (from gaps)")
    resume_text: Optional[str] = ""


# ─── Safe Question Model (Client Facing) ───
class SafeExamQuestion(BaseModel):
    """A single exam question containing only safe fields (no answer keys)."""
    id: str
    exam_type: str
    skill: str = "General"
    topic: str = ""
    difficulty: str = "intermediate"
    question: str
    options: Optional[List[str]] = None
    starter_code: Optional[str] = None
    language: Optional[str] = None
    max_word_count: Optional[int] = None
    buggy_code: Optional[str] = None
    bug_description: Optional[str] = None
    time_limit_seconds: Optional[int] = None
    points: int = 10


# Kept for backward compatibility if imported internally
ExamQuestion = SafeExamQuestion


class GenerateExamResponse(BaseModel):
    """Response with generated exam questions and server-side exam_id."""
    exam_id: str
    role: str
    exam_type: str
    difficulty: str
    questions: List[SafeExamQuestion]
    total_questions: int
    time_limit_seconds: int
    instructions: str


# ─── Answer Submission ───
class ExamAnswer(BaseModel):
    """A single answer submitted by the client."""
    question_id: str
    exam_type: Optional[str] = None
    selected_index: Optional[int] = None
    code_answer: Optional[str] = None
    text_answer: Optional[str] = None
    time_taken_seconds: Optional[int] = None

    # Any client-supplied answer keys will be ignored server-side
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    expected_points: Optional[List[str]] = None
    skill: Optional[str] = None
    topic: Optional[str] = None


class SubmitExamRequest(BaseModel):
    """Submit exam answers for server-side evaluation."""
    exam_id: str
    answers: List[ExamAnswer]
    profile_id: Optional[int] = None
    role: Optional[str] = None
    exam_type: Optional[str] = None
    total_time_seconds: Optional[int] = None
    questions: Optional[List[Dict[str, Any]]] = None  # Ignored server-side


# ─── Evaluation Results ───
class QuestionResult(BaseModel):
    """Result for a single question post-evaluation."""
    question_id: str
    skill: str
    topic: str
    exam_type: str
    is_correct: bool
    score: float  # 0-100
    accuracy_pct: Optional[float] = None
    time_complexity: Optional[str] = None
    time_rating: Optional[str] = None
    space_complexity: Optional[str] = None
    space_rating: Optional[str] = None
    complexity_analysis: Optional[str] = None
    feedback: str
    explanation: Optional[str] = None
    correct_answer: Optional[str] = None
    skill_impact: float = 0.0


class ExamEvaluationResponse(BaseModel):
    """Full exam evaluation with diagnostics, complexity analysis, and skill updates."""
    exam_id: Optional[str] = None
    overall_score: float
    accuracy_pct: float
    total_questions: int
    correct_count: int
    clearance_status: str
    is_cleared: bool
    exam_type: str
    difficulty: str
    results: List[QuestionResult]
    skill_updates: Dict[str, float]
    twin_updated: bool
    new_readiness_pct: Optional[float] = None
    new_skills: Optional[Dict[str, float]] = None
    new_gap_analysis: Optional[List[Dict[str, Any]]] = None
    new_salary_estimate: Optional[Dict[str, Any]] = None
    new_trajectory: Optional[Dict[str, Any]] = None
    new_roadmap: Optional[List[Dict[str, Any]]] = None
    overall_time_complexity: Optional[str] = None
    overall_space_complexity: Optional[str] = None
    complexity_summary: Optional[str] = None
    summary: str
    recommendations: List[str] = []


# ─── Skill History ───
class SkillHistoryItem(BaseModel):
    """A single skill history entry."""
    skill_name: str
    old_confidence: float
    new_confidence: float
    change_amount: float
    change_source: str
    notes: Optional[str] = None
    created_at: Optional[str] = None


class SkillProgressionResponse(BaseModel):
    """Skill progression timeline for a user."""
    profile_id: int
    history: List[SkillHistoryItem]
    current_skills: Dict[str, float]
    total_exams_taken: int
    improvement_summary: str
