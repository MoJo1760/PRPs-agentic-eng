"""Questionnaire data models."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions that can be asked."""

    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_SELECT = "single_select"
    TEXT = "text"
    NUMBER = "number"
    SCALE = "scale"
    BOOLEAN = "boolean"


class QuestionCategory(str, Enum):
    """Categories of questions."""

    BUSINESS_MODEL = "business_model"
    TARGET_MARKET = "target_market"
    TECHNICAL_REQUIREMENTS = "technical_requirements"
    USER_EXPERIENCE = "user_experience"
    MONETIZATION = "monetization"
    SCALABILITY = "scalability"
    INTEGRATION = "integration"
    COMPLIANCE = "compliance"


class Question(BaseModel):
    """Individual question model."""

    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., min_length=10, description="Question text")
    type: QuestionType = Field(..., description="Type of question")
    category: QuestionCategory = Field(..., description="Question category")
    required: bool = Field(default=True, description="Whether answer is required")
    options: Optional[List[str]] = Field(
        None, description="Options for choice questions"
    )
    validation_rules: Optional[Dict[str, Any]] = Field(
        None, description="Validation rules"
    )
    help_text: Optional[str] = Field(None, description="Additional help text")
    depends_on: Optional[str] = Field(None, description="Question this depends on")
    priority: int = Field(
        default=5, ge=1, le=10, description="Question priority (1=highest)"
    )

    @validator("options")
    def options_required_for_choice_questions(cls, v, values):
        """Validate options are provided for choice questions."""
        question_type = values.get("type")
        if question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_SELECT]:
            if not v or len(v) < 2:
                raise ValueError("Choice questions must have at least 2 options")
        return v


class QuestionnaireResponse(BaseModel):
    """User response to a question."""

    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., min_length=1, description="User's answer")
    confidence_score: Optional[float] = Field(
        None, ge=0, le=1, description="User's confidence in their answer (0-1)"
    )
    answered_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("answer")
    def answer_not_empty(cls, v):
        """Validate answer is not empty."""
        if not v or not v.strip():
            raise ValueError("Answer cannot be empty")
        return v.strip()


class QuestionnaireSession(BaseModel):
    """Questionnaire session tracking."""

    session_id: str = Field(..., description="Unique session identifier")
    concept_id: str = Field(..., description="Associated business concept ID")
    questions: List[Question] = Field(default_factory=list)
    responses: List[QuestionnaireResponse] = Field(default_factory=list)
    current_question_index: int = Field(default=0, ge=0)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    completed: bool = Field(default=False)
    completion_percentage: float = Field(default=0.0, ge=0, le=100)

    @property
    def is_complete(self) -> bool:
        """Check if questionnaire is complete."""
        if not self.questions:
            return False

        required_questions = [q for q in self.questions if q.required]
        answered_required = [
            r
            for r in self.responses
            if any(q.id == r.question_id and q.required for q in self.questions)
        ]

        return len(answered_required) >= len(required_questions)

    @property
    def next_question(self) -> Optional[Question]:
        """Get the next unanswered question."""
        answered_ids = {r.question_id for r in self.responses}

        for question in sorted(self.questions, key=lambda q: q.priority):
            if question.id not in answered_ids:
                # Check dependencies
                if question.depends_on:
                    dependency_answered = any(
                        r.question_id == question.depends_on for r in self.responses
                    )
                    if not dependency_answered:
                        continue

                return question

        return None

    def add_response(self, response: QuestionnaireResponse):
        """Add a response and update completion status."""
        # Remove any existing response for this question
        self.responses = [
            r for r in self.responses if r.question_id != response.question_id
        ]

        # Add new response
        self.responses.append(response)

        # Update completion percentage
        if self.questions:
            required_questions = [q for q in self.questions if q.required]
            answered_required = [
                r
                for r in self.responses
                if any(q.id == r.question_id and q.required for q in self.questions)
            ]

            if required_questions:
                self.completion_percentage = (
                    len(answered_required) / len(required_questions)
                ) * 100
            else:
                self.completion_percentage = 100

        # Update activity timestamp
        self.last_activity = datetime.utcnow()

        # Check if completed
        self.completed = self.is_complete


class QuestionnaireGenerationRequest(BaseModel):
    """Request for generating questions."""

    concept_id: str = Field(..., description="Business concept ID")
    max_questions: int = Field(default=10, ge=1, le=15)
    focus_areas: Optional[List[QuestionCategory]] = Field(
        None, description="Specific areas to focus questions on"
    )
    difficulty_level: Literal["basic", "intermediate", "advanced"] = Field(
        default="intermediate"
    )
    existing_responses: Optional[List[QuestionnaireResponse]] = Field(
        None, description="Previous responses to consider"
    )
