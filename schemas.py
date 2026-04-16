from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class Subject(str, Enum):
    MATHEMATICS = "mathematics"
    ENGLISH = "english"
    SCIENCE = "science"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"

class Question(BaseModel):
    question_id: str
    question_text: str
    max_marks: int
    question_type: str  # e.g., "essay", "multiple_choice", "calculation"

class Answer(BaseModel):
    question_id: str
    student_response: str

class StudentWork(BaseModel):
    questions: List[Question]
    answers: List[Answer]
    subject: Subject
    student_id: Optional[str] = None

class MarkingResult(BaseModel):
    question_id: str
    question_text: str
    student_response: str
    max_marks: int
    marks_awarded: int
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str

class MarkingOutput(BaseModel):
    student_id: Optional[str]
    subject: Subject
    results: List[MarkingResult]
    total_marks_awarded: int
    total_max_marks: int
    percentage: float

class Feedback(BaseModel):
    teacher_feedback: str
    student_feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    next_steps: List[str]

class ValidationResult(BaseModel):
    is_valid: bool
    consistency_score: float = Field(..., ge=0.0, le=1.0)
    validation_notes: List[str]
    suggested_corrections: Optional[Dict[str, Any]] = None

class FinalOutput(BaseModel):
    marking_output: MarkingOutput
    feedback: Feedback
    validation: ValidationResult
    processed_timestamp: str