"""Questionnaire and questioning system data models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class QuestionType(str, Enum):
    """Types of questions that can be asked."""
    
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT_SHORT = "text_short"
    TEXT_LONG = "text_long"
    NUMBER = "number"
    BOOLEAN = "boolean"
    RATING = "rating"
    RANKING = "ranking"
    EMAIL = "email"
    URL = "url"


class QuestionPriority(str, Enum):
    """Priority levels for questions."""
    
    CRITICAL = "critical"      # Must be answered
    HIGH = "high"             # Very important
    MEDIUM = "medium"         # Important
    LOW = "low"              # Nice to have
    OPTIONAL = "optional"     # Completely optional


class Question(BaseModel):
    """Individual question in the questionnaire."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    
    # Question content
    text: str = Field(min_length=10, max_length=1000)
    description: Optional[str] = Field(None, max_length=500)
    help_text: Optional[str] = Field(None, max_length=300)
    
    # Question type and validation
    question_type: QuestionType
    priority: QuestionPriority = QuestionPriority.MEDIUM
    
    # Question options (for choice-based questions)
    options: Optional[List[str]] = Field(None, max_items=20)
    
    # Validation rules
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None  # Regex pattern for text validation
    
    # Context and dependencies
    category: str = Field(description="Question category for grouping")
    tags: List[str] = Field(default_factory=list, max_items=10)
    depends_on: Optional[List[str]] = Field(None, description="Question IDs this depends on")
    
    # Display properties
    order: int = Field(default=0, description="Display order within category")
    conditional_display: Optional[Dict[str, Any]] = Field(
        None, 
        description="Conditions for showing this question"
    )
    
    @validator('options')
    def validate_options(cls, v, values):
        """Validate options for choice-based questions."""
        question_type = values.get('question_type')
        
        if question_type in [QuestionType.MULTIPLE_CHOICE, QuestionType.SINGLE_CHOICE]:
            if not v or len(v) < 2:
                raise ValueError(f"{question_type} questions must have at least 2 options")
        elif question_type == QuestionType.RANKING:
            if not v or len(v) < 2:
                raise ValueError("Ranking questions must have at least 2 options to rank")
        elif v:
            raise ValueError(f"Question type {question_type} should not have options")
        
        return v
    
    @validator('min_value', 'max_value')
    def validate_numeric_constraints(cls, v, values):
        """Validate numeric constraints for number and rating questions."""
        question_type = values.get('question_type')
        
        if v is not None and question_type not in [QuestionType.NUMBER, QuestionType.RATING]:
            raise ValueError(f"Numeric constraints not applicable for {question_type}")
        
        return v


class AnswerValidation(BaseModel):
    """Validation result for a questionnaire answer."""
    
    is_valid: bool
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Validation metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validation_method: str = "automatic"


class QuestionnaireResponse(BaseModel):
    """Response to a single questionnaire question."""
    
    question_id: str
    answer: Union[str, int, float, bool, List[str]]
    
    # Response metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    answer_source: str = Field(default="user_input")  # user_input, auto_filled, inferred
    
    # Validation
    validation: Optional[AnswerValidation] = None
    
    # Timestamps
    answered_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QuestionnaireSession(BaseModel):
    """Complete questionnaire session for a business concept."""
    
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    concept_id: str
    
    # Session status
    status: str = Field(default="active")  # active, completed, abandoned
    current_question_index: int = Field(default=0)
    
    # Questions and responses
    questions: List[Question] = Field(default_factory=list)
    responses: List[QuestionnaireResponse] = Field(default_factory=list)
    
    # Session metadata
    total_questions: int = Field(default=0)
    questions_answered: int = Field(default=0)
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Timing information
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    
    # Dynamic questioning state
    context: Dict[str, Any] = Field(default_factory=dict)
    skip_patterns: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def update_progress(self):
        """Update completion percentage and question counts."""
        self.questions_answered = len(self.responses)
        self.total_questions = len(self.questions)
        
        if self.total_questions > 0:
            self.completion_percentage = (self.questions_answered / self.total_questions) * 100
        
        self.last_activity_at = datetime.utcnow()
    
    def get_next_question(self) -> Optional[Question]:
        """Get the next unanswered question considering dependencies."""
        answered_question_ids = {resp.question_id for resp in self.responses}
        
        for question in self.questions:
            if question.id in answered_question_ids:
                continue
            
            # Check dependencies
            if question.depends_on:
                dependencies_met = all(
                    dep_id in answered_question_ids 
                    for dep_id in question.depends_on
                )
                if not dependencies_met:
                    continue
            
            # Check conditional display
            if question.conditional_display:
                if not self._evaluate_display_condition(question.conditional_display):
                    continue
            
            return question
        
        return None
    
    def is_complete(self) -> bool:
        """Check if questionnaire is complete."""
        if self.status == "completed":
            return True
        
        # Check if all critical and high priority questions are answered
        answered_question_ids = {resp.question_id for resp in self.responses}
        
        for question in self.questions:
            if question.priority in [QuestionPriority.CRITICAL, QuestionPriority.HIGH]:
                if question.required and question.id not in answered_question_ids:
                    # Check if question should be displayed
                    if question.conditional_display:
                        if not self._evaluate_display_condition(question.conditional_display):
                            continue
                    return False
        
        return True
    
    def _evaluate_display_condition(self, condition: Dict[str, Any]) -> bool:
        """Evaluate whether a question should be displayed based on conditions."""
        # Simple condition evaluation - can be expanded
        # Example condition: {"question_id": "q1", "answer": "yes"}
        
        if "question_id" in condition and "answer" in condition:
            target_question_id = condition["question_id"]
            expected_answer = condition["answer"]
            
            # Find the response for the target question
            for response in self.responses:
                if response.question_id == target_question_id:
                    return str(response.answer).lower() == str(expected_answer).lower()
            
            return False
        
        return True


class QuestionGenerationRequest(BaseModel):
    """Request for generating follow-up questions."""
    
    concept_id: str
    session_id: str
    
    # Context for question generation
    existing_responses: List[QuestionnaireResponse]
    business_domain: Optional[str] = None
    complexity_estimate: Optional[str] = None
    
    # Generation parameters
    max_questions: int = Field(default=5, ge=1, le=10)
    focus_areas: Optional[List[str]] = None
    avoid_topics: Optional[List[str]] = None
    
    # AI generation settings
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0)
    include_optional_questions: bool = Field(default=True)