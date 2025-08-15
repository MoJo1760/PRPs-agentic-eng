"""Research iteration tracking models for iterative research engine."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field

from .gap_analysis import KnowledgeGap, ResearchIteration


class ResearchQuery(BaseModel):
    """Represents a research query executed during an iteration."""

    query_text: str = Field(description="The actual search query text")
    target_domain: str = Field(description="Domain this query targets")
    query_type: Literal["gap_targeted", "exploratory", "validation"] = Field(
        description="Type of research query"
    )
    official_sources_preference: bool = Field(
        default=True, description="Whether to prefer official documentation sources"
    )
    executed_at: datetime = Field(
        default_factory=datetime.utcnow, description="When this query was executed"
    )
    results_count: int = Field(default=0, description="Number of results returned")
    official_results_count: int = Field(
        default=0, description="Number of official documentation results"
    )


class ResearchSource(BaseModel):
    """Represents a source found during research."""

    url: str = Field(description="Source URL")
    title: str = Field(description="Source title")
    domain: str = Field(description="Source domain")
    snippet: str = Field(description="Relevant snippet from source")
    is_official_docs: bool = Field(
        default=False, description="Whether this is official documentation"
    )
    relevance_score: float = Field(
        ge=0.0, le=10.0, description="Relevance score for this source"
    )
    quality_score: float = Field(
        ge=0.0, le=10.0, description="Quality assessment score"
    )
    content_type: str = Field(
        default="webpage",
        description="Type of content (documentation, github, stackoverflow, etc.)",
    )
    found_at: datetime = Field(
        default_factory=datetime.utcnow, description="When this source was found"
    )


class GeneratedQuestion(BaseModel):
    """Represents a question generated based on research findings."""

    question_id: str = Field(description="Unique question identifier")
    text: str = Field(description="The question text")
    question_type: str = Field(description="Type of question")
    category: str = Field(description="Question category")
    gap_ids: List[str] = Field(
        default_factory=list, description="Knowledge gap IDs this question addresses"
    )
    priority: int = Field(ge=1, le=10, description="Question priority (1=highest)")
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence in question relevance"
    )
    options: Optional[List[str]] = Field(
        default=None, description="Answer options if multiple choice"
    )
    generated_from_sources: List[str] = Field(
        default_factory=list, description="Source URLs that informed this question"
    )


class IterationMetrics(BaseModel):
    """Metrics for a single research iteration."""

    gaps_addressed: int = Field(
        default=0, description="Number of gaps addressed in this iteration"
    )
    new_gaps_discovered: int = Field(
        default=0, description="Number of new gaps discovered"
    )
    coverage_before: float = Field(
        ge=0.0, le=100.0, description="Coverage percentage before this iteration"
    )
    coverage_after: float = Field(
        ge=0.0, le=100.0, description="Coverage percentage after this iteration"
    )
    research_queries_executed: int = Field(
        default=0, description="Number of research queries executed"
    )
    official_sources_found: int = Field(
        default=0, description="Number of official sources found"
    )
    total_sources_found: int = Field(
        default=0, description="Total number of sources found"
    )
    questions_generated: int = Field(
        default=0, description="Number of questions generated"
    )
    high_quality_sources_ratio: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Ratio of high-quality sources found"
    )
    iteration_time_minutes: float = Field(
        default=0.0, description="Time spent on this iteration in minutes"
    )


class DetailedResearchIteration(ResearchIteration):
    """Extended research iteration with detailed tracking."""

    detailed_research_queries: List[ResearchQuery] = Field(
        default_factory=list, description="Detailed queries executed"
    )
    sources_found: List[ResearchSource] = Field(
        default_factory=list, description="All sources found during research"
    )
    questions_generated_detailed: List[GeneratedQuestion] = Field(
        default_factory=list, description="Detailed questions generated"
    )
    gaps_analysis: List[KnowledgeGap] = Field(
        default_factory=list, description="Gap analysis results for this iteration"
    )
    metrics: IterationMetrics = Field(description="Detailed metrics for this iteration")
    decision_points: List[Dict[str, Any]] = Field(
        default_factory=list, description="Key decision points during iteration"
    )
    quality_assessments: Dict[str, float] = Field(
        default_factory=dict, description="Quality assessments for various aspects"
    )
