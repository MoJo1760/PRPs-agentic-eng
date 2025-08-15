"""Coverage metrics and validation models for iterative research."""

from datetime import datetime
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

from .gap_analysis import CoverageMetrics


class DomainCoverageRequirement(BaseModel):
    """Defines coverage requirements for a specific domain."""

    domain: str = Field(description="Domain name (saas, e_commerce, etc.)")
    category: str = Field(description="Requirement category")
    requirement: str = Field(description="Specific requirement description")
    priority: Literal["critical", "high", "medium", "low"] = Field(
        description="Priority level"
    )
    coverage_weight: float = Field(
        ge=0.0,
        le=1.0,
        description="Weight of this requirement in overall coverage calculation",
    )
    validation_criteria: List[str] = Field(
        default_factory=list,
        description="Criteria for validating this requirement is met",
    )


class CoverageGate(BaseModel):
    """Represents a quality gate that must be passed."""

    gate_name: str = Field(description="Name of the quality gate")
    description: str = Field(description="Description of what this gate validates")
    threshold: float = Field(
        ge=0.0, le=100.0, description="Minimum threshold to pass this gate"
    )
    current_score: float = Field(
        default=0.0, ge=0.0, le=100.0, description="Current score for this gate"
    )
    passed: bool = Field(default=False, description="Whether this gate has been passed")
    required_for_completion: bool = Field(
        default=True, description="Whether this gate is required for completion"
    )
    validation_rules: List[str] = Field(
        default_factory=list, description="Rules for validating this gate"
    )


class StoppingCriteria(BaseModel):
    """Defines criteria for stopping the iterative research process."""

    minimum_overall_coverage: float = Field(
        default=95.0,
        ge=0.0,
        le=100.0,
        description="Minimum overall coverage percentage required",
    )
    minimum_domain_coverage: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Minimum coverage required for each domain",
    )
    minimum_critical_gaps_filled: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Minimum percentage of critical gaps that must be filled",
    )
    minimum_high_priority_gaps_filled: float = Field(
        default=90.0,
        ge=0.0,
        le=100.0,
        description="Minimum percentage of high priority gaps that must be filled",
    )
    required_quality_gates: List[str] = Field(
        default_factory=list, description="Names of quality gates that must pass"
    )
    maximum_iterations: int = Field(
        default=5, ge=1, description="Maximum number of iterations allowed"
    )
    maximum_time_minutes: float = Field(
        default=15.0, ge=1.0, description="Maximum time allowed for research in minutes"
    )
    minimum_official_source_ratio: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Minimum ratio of official sources required",
    )


class DetailedCoverageMetrics(CoverageMetrics):
    """Extended coverage metrics with detailed breakdown."""

    requirements_coverage: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, description="Coverage by domain and requirement category"
    )
    quality_gates: List[CoverageGate] = Field(
        default_factory=list, description="All quality gates and their status"
    )
    stopping_criteria: StoppingCriteria = Field(
        description="Stopping criteria configuration"
    )
    gaps_by_priority: Dict[str, int] = Field(
        default_factory=dict, description="Number of gaps by priority level"
    )
    filled_gaps_by_priority: Dict[str, int] = Field(
        default_factory=dict, description="Number of filled gaps by priority level"
    )
    coverage_trend: List[float] = Field(
        default_factory=list, description="Coverage percentage over iterations"
    )
    bottleneck_areas: List[str] = Field(
        default_factory=list,
        description="Areas with lowest coverage that are blocking completion",
    )
    research_efficiency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Score indicating research process efficiency",
    )
    time_to_coverage_ratio: float = Field(
        default=0.0, description="Coverage gained per minute of research time"
    )


class CoverageAssessmentResult(BaseModel):
    """Result of a coverage assessment."""

    assessment_id: str = Field(description="Unique assessment identifier")
    concept_id: str = Field(description="Concept being assessed")
    assessment_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When assessment was performed"
    )
    coverage_metrics: DetailedCoverageMetrics = Field(
        description="Detailed coverage metrics"
    )
    should_continue: bool = Field(description="Whether research should continue")
    stop_reason: Optional[str] = Field(
        default=None, description="Reason for stopping if should_continue is False"
    )
    next_iteration_focus: List[str] = Field(
        default_factory=list, description="Areas to focus on in next iteration"
    )
    estimated_iterations_remaining: int = Field(
        default=0, description="Estimated iterations needed to reach completion"
    )
    confidence_in_assessment: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence in the accuracy of this assessment",
    )
