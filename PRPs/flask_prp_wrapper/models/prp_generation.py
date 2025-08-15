"""PRP generation and validation data models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class PRPComplexity(str, Enum):
    """PRP complexity levels."""
    
    SIMPLE = "simple"
    MODERATE = "moderate"  
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


class PRPStatus(str, Enum):
    """PRP generation and validation status."""
    
    PENDING = "pending"
    RESEARCHING = "researching"
    GENERATING = "generating"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_REVISION = "requires_revision"


class ResearchSource(BaseModel):
    """Source of research information."""
    
    url: str
    title: str
    type: str = Field(description="Type of source: official_docs, github, stackoverflow, blog, etc.")
    relevance_score: float = Field(ge=0.0, le=1.0)
    priority: int = Field(ge=1, le=10)  # 1 = highest priority
    
    # Content analysis
    key_points: List[str] = Field(default_factory=list)
    code_examples: List[str] = Field(default_factory=list)
    gotchas: List[str] = Field(default_factory=list)
    
    accessed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ResearchContext(BaseModel):
    """Research context for PRP generation."""
    
    # Business domain research
    domain_insights: Dict[str, Any] = Field(default_factory=dict)
    competitor_analysis: List[Dict[str, str]] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)
    
    # Technical research
    recommended_technologies: Dict[str, str] = Field(default_factory=dict)
    architecture_patterns: List[Dict[str, str]] = Field(default_factory=list)
    implementation_examples: List[Dict[str, str]] = Field(default_factory=list)
    
    # Documentation and resources
    sources: List[ResearchSource] = Field(default_factory=list)
    official_documentation: List[ResearchSource] = Field(default_factory=list)
    community_resources: List[ResearchSource] = Field(default_factory=list)
    
    # Known challenges and solutions
    common_pitfalls: List[str] = Field(default_factory=list)
    best_practices: List[str] = Field(default_factory=list)
    security_considerations: List[str] = Field(default_factory=list)
    
    # Research metadata
    research_depth: str = Field(default="comprehensive")  # basic, comprehensive, deep
    research_duration_seconds: int = Field(default=0)
    research_quality_score: float = Field(default=0.0, ge=0.0, le=10.0)
    
    def get_prioritized_sources(self, source_type: Optional[str] = None) -> List[ResearchSource]:
        """Get sources sorted by priority and relevance."""
        sources = self.sources
        
        if source_type:
            sources = [s for s in sources if s.type == source_type]
        
        return sorted(sources, key=lambda s: (s.priority, -s.relevance_score))
    
    def get_official_docs_first(self) -> List[ResearchSource]:
        """Get official documentation sources first, then others."""
        official = [s for s in self.sources if s.type == "official_docs"]
        others = [s for s in self.sources if s.type != "official_docs"]
        
        return sorted(official, key=lambda s: -s.relevance_score) + sorted(others, key=lambda s: -s.relevance_score)


class ValidationCommand(BaseModel):
    """Command for validating PRP implementation."""
    
    level: int = Field(ge=1, le=4, description="Validation level (1-4)")
    level_name: str = Field(description="Human-readable level name")
    
    command: str = Field(description="Shell command to execute")
    description: str = Field(description="What this command validates")
    
    expected_result: str = Field(description="Expected outcome")
    timeout_seconds: int = Field(default=120, ge=1)
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Commands that must pass first")
    working_directory: Optional[str] = None
    environment_vars: Dict[str, str] = Field(default_factory=dict)
    
    # Validation criteria
    success_criteria: List[str] = Field(default_factory=list)
    failure_indicators: List[str] = Field(default_factory=list)


class PRPQualityMetrics(BaseModel):
    """Quality assessment metrics for generated PRPs."""
    
    # Content quality scores (0-10)
    completeness_score: float = Field(ge=0.0, le=10.0)
    clarity_score: float = Field(ge=0.0, le=10.0)
    context_richness: float = Field(ge=0.0, le=10.0)
    implementation_detail: float = Field(ge=0.0, le=10.0)
    validation_coverage: float = Field(ge=0.0, le=10.0)
    
    # Technical quality scores (0-10)
    architecture_soundness: float = Field(ge=0.0, le=10.0)
    best_practices_adherence: float = Field(ge=0.0, le=10.0)
    security_considerations: float = Field(ge=0.0, le=10.0)
    error_handling_coverage: float = Field(ge=0.0, le=10.0)
    testing_strategy: float = Field(ge=0.0, le=10.0)
    
    # Overall metrics
    overall_score: float = Field(ge=0.0, le=10.0)
    readiness_score: float = Field(ge=0.0, le=10.0)  # Ready for AI implementation
    
    # Detailed analysis
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvement_suggestions: List[str] = Field(default_factory=list)
    
    # Assessment metadata
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    assessment_method: str = Field(default="automated")
    
    def calculate_overall_score(self) -> float:
        """Calculate overall quality score from individual metrics."""
        scores = [
            self.completeness_score,
            self.clarity_score, 
            self.context_richness,
            self.implementation_detail,
            self.validation_coverage,
            self.architecture_soundness,
            self.best_practices_adherence,
            self.security_considerations,
            self.error_handling_coverage,
            self.testing_strategy
        ]
        
        self.overall_score = sum(scores) / len(scores)
        return self.overall_score
    
    def is_production_ready(self, min_score: float = 8.0) -> bool:
        """Check if PRP meets production readiness criteria."""
        return (
            self.overall_score >= min_score and
            self.completeness_score >= min_score and
            self.validation_coverage >= min_score and
            self.security_considerations >= 7.0
        )


class PRPValidationResult(BaseModel):
    """Result of PRP validation execution."""
    
    # Validation metadata
    validation_id: str = Field(default_factory=lambda: str(uuid4()))
    prp_id: str
    
    # Execution results
    level_results: Dict[int, Dict[str, Any]] = Field(default_factory=dict)
    commands_executed: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Overall validation status
    overall_status: str = "pending"  # pending, running, passed, failed, partial
    highest_level_passed: int = 0
    total_commands: int = 0
    passed_commands: int = 0
    failed_commands: int = 0
    
    # Timing and performance
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    
    # Error tracking
    errors: List[Dict[str, str]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def add_command_result(self, command: ValidationCommand, success: bool, 
                          output: str, duration: float, error: Optional[str] = None):
        """Add result for a validation command."""
        result = {
            "command": command.command,
            "description": command.description,
            "level": command.level,
            "success": success,
            "output": output,
            "duration_seconds": duration,
            "error": error,
            "executed_at": datetime.utcnow().isoformat()
        }
        
        self.commands_executed.append(result)
        
        if success:
            self.passed_commands += 1
            if command.level > self.highest_level_passed:
                self.highest_level_passed = command.level
        else:
            self.failed_commands += 1
            if error:
                self.errors.append({
                    "command": command.command,
                    "level": str(command.level),
                    "error": error
                })
        
        self.total_commands = len(self.commands_executed)


class PRPGenerationRequest(BaseModel):
    """Request for generating a PRP."""
    
    concept_id: str
    session_id: Optional[str] = None
    
    # Source data
    business_concept: Dict[str, Any] = Field(description="Original business concept")
    questionnaire_responses: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Responses from questionnaire"
    )
    
    # Generation parameters
    complexity_level: PRPComplexity = PRPComplexity.MODERATE
    research_depth: str = Field(default="comprehensive")  # basic, comprehensive, deep
    include_advanced_features: bool = Field(default=True)
    
    # Technical preferences
    preferred_technologies: Dict[str, str] = Field(default_factory=dict)
    deployment_target: Optional[str] = None
    performance_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    # Validation requirements
    validation_levels: List[int] = Field(default=[1, 2, 3, 4])
    min_quality_score: float = Field(default=8.0, ge=0.0, le=10.0)
    
    # Generation settings
    use_ai_enhancement: bool = Field(default=True)
    creativity_level: float = Field(default=0.7, ge=0.0, le=1.0)
    
    class Config:
        use_enum_values = True


class GeneratedPRP(BaseModel):
    """Complete generated PRP with metadata."""
    
    # Identifiers
    id: str = Field(default_factory=lambda: str(uuid4()))
    concept_id: str
    session_id: Optional[str] = None
    
    # PRP content
    title: str
    content: str = Field(description="Full PRP markdown content")
    
    # Generation metadata
    complexity: PRPComplexity
    status: PRPStatus = PRPStatus.PENDING
    
    # Quality assessment
    quality_metrics: PRPQualityMetrics
    validation_commands: List[ValidationCommand] = Field(default_factory=list)
    
    # Research context
    research_context: ResearchContext
    
    # Technical details
    estimated_implementation_hours: float = Field(default=0.0, ge=0.0)
    technology_stack: Dict[str, str] = Field(default_factory=dict)
    architecture_decisions: List[Dict[str, str]] = Field(default_factory=list)
    
    # File and deployment info
    file_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    
    # Generation tracking
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generation_duration_seconds: float = Field(default=0.0)
    generation_method: str = Field(default="template_based")
    
    # Validation results
    validation_result: Optional[PRPValidationResult] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def is_ready_for_implementation(self) -> bool:
        """Check if PRP is ready for AI implementation."""
        return (
            self.status == PRPStatus.COMPLETED and
            self.quality_metrics.is_production_ready() and
            len(self.validation_commands) >= 4  # Must have all validation levels
        )
    
    def get_file_name(self) -> str:
        """Generate appropriate filename for the PRP."""
        # Convert title to filename-safe format
        safe_title = "".join(c for c in self.title.lower() if c.isalnum() or c in ['-', '_', ' '])
        safe_title = safe_title.replace(' ', '-')
        return f"{safe_title}-prp.md"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the PRP for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "complexity": self.complexity,
            "status": self.status,
            "overall_quality_score": self.quality_metrics.overall_score,
            "estimated_hours": self.estimated_implementation_hours,
            "validation_commands_count": len(self.validation_commands),
            "is_ready": self.is_ready_for_implementation(),
            "generated_at": self.generated_at.isoformat(),
            "file_name": self.get_file_name()
        }