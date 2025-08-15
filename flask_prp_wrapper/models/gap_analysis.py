"""Gap analysis data models for iterative research engine."""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class KnowledgeGap(BaseModel):
    """Represents a specific knowledge gap identified during analysis."""

    id: str = Field(description="Unique identifier for the gap")
    domain: str = Field(description="Business domain this gap belongs to")
    category: str = Field(
        description="Category of the gap (technical, business, integration, etc.)"
    )
    description: str = Field(
        description="Detailed description of what information is missing"
    )
    priority: Literal["critical", "high", "medium", "low"] = Field(
        default="medium", description="Priority level for addressing this gap"
    )
    identified_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this gap was first identified",
    )
    research_attempts: int = Field(
        default=0,
        description="Number of times research has been attempted for this gap",
    )
    filled: bool = Field(
        default=False, description="Whether this gap has been satisfactorily filled"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence that this gap has been adequately addressed",
    )
    related_questions: List[str] = Field(
        default_factory=list, description="Question IDs that relate to this gap"
    )
    research_sources: List[str] = Field(
        default_factory=list, description="Sources used to research this gap"
    )


class GapAnalysisResult(BaseModel):
    """Result of analyzing a business concept for knowledge gaps."""

    concept_id: str = Field(description="ID of the concept being analyzed")
    identified_gaps: List[KnowledgeGap] = Field(
        default_factory=list, description="List of identified knowledge gaps"
    )
    coverage_percentage: float = Field(
        ge=0.0, le=100.0, description="Overall percentage of requirements coverage"
    )
    domain_completeness: Dict[str, float] = Field(
        default_factory=dict, description="Coverage percentage by domain area"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When this analysis was performed"
    )
    next_research_areas: List[str] = Field(
        default_factory=list,
        description="Prioritized areas for next research iteration",
    )
    critical_gaps_count: int = Field(
        default=0, description="Number of critical priority gaps identified"
    )
    high_priority_gaps_count: int = Field(
        default=0, description="Number of high priority gaps identified"
    )


class ResearchIteration(BaseModel):
    """Represents a single iteration of the research process."""

    id: str = Field(description="Unique identifier for this iteration")
    concept_id: str = Field(description="ID of the concept being researched")
    iteration_number: int = Field(
        ge=1, description="Iteration number in the research sequence"
    )
    gaps_targeted: List[str] = Field(
        default_factory=list, description="Gap IDs that this iteration targeted"
    )
    research_queries: List[str] = Field(
        default_factory=list, description="Research queries executed in this iteration"
    )
    official_sources_found: int = Field(
        default=0, description="Number of official documentation sources found"
    )
    questions_generated: int = Field(
        default=0, description="Number of questions generated from research"
    )
    coverage_improvement: float = Field(
        default=0.0,
        description="Improvement in coverage percentage from this iteration",
    )
    official_source_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Ratio of official vs. third-party sources used",
    )
    started_at: datetime = Field(
        default_factory=datetime.utcnow, description="When this iteration was started"
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When this iteration was completed"
    )
    status: Literal["pending", "running", "completed", "failed"] = Field(
        default="pending", description="Current status of this iteration"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if iteration failed"
    )


class CoverageMetrics(BaseModel):
    """Metrics for assessing requirement coverage completeness."""

    overall_coverage: float = Field(
        ge=0.0, le=100.0, description="Overall coverage percentage"
    )
    domain_coverage: Dict[str, float] = Field(
        default_factory=dict, description="Coverage percentage by domain"
    )
    technical_requirements_coverage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Coverage of technical requirements"
    )
    business_model_coverage: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Coverage of business model aspects"
    )
    integration_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Coverage of integration requirements",
    )
    validation_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Coverage of validation and testing requirements",
    )
    user_experience_coverage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Coverage of user experience requirements",
    )
    stopping_criteria_met: bool = Field(
        default=False, description="Whether stopping criteria have been satisfied"
    )
    recommended_next_steps: List[str] = Field(
        default_factory=list,
        description="Recommended next steps based on current coverage",
    )
    quality_gates_passed: Dict[str, bool] = Field(
        default_factory=dict, description="Status of various quality gates"
    )
    research_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Overall quality score of research conducted",
    )


class IterativeResearchResult(BaseModel):
    """Final result of the complete iterative research process."""

    concept_id: str = Field(description="ID of the concept researched")
    iterations: List[ResearchIteration] = Field(
        default_factory=list, description="All research iterations performed"
    )
    final_coverage_metrics: CoverageMetrics = Field(
        description="Final coverage metrics after all iterations"
    )
    total_gaps_identified: int = Field(
        default=0, description="Total number of gaps identified across all iterations"
    )
    gaps_filled: int = Field(
        default=0, description="Number of gaps successfully filled"
    )
    total_research_time_minutes: float = Field(
        default=0.0, description="Total time spent on research in minutes"
    )
    official_sources_used: int = Field(
        default=0, description="Total number of official sources consulted"
    )
    questions_generated: int = Field(
        default=0, description="Total number of questions generated"
    )
    early_stop_reason: Optional[str] = Field(
        default=None, description="Reason for early stopping if applicable"
    )
    success: bool = Field(
        default=False, description="Whether the research process was successful"
    )
    ready_for_prp_generation: bool = Field(
        default=False,
        description="Whether sufficient information has been gathered for PRP generation",
    )
