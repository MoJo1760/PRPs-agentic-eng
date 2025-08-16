"""PRD document data models for upload and parsing functionality."""

from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class PRDSection(BaseModel):
    """Parsed section from PRD document."""

    title: str = Field(description="Section title/heading")
    content: str = Field(description="Full section content")
    section_type: Literal[
        "overview",
        "users",
        "requirements",
        "technical",
        "business_model",
        "competitive",
        "user_stories",
        "metrics",
        "other",
    ] = Field(description="Categorized section type")
    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        default=0.5,
        description="Confidence in section type classification",
    )
    extracted_keywords: List[str] = Field(
        default_factory=list, description="Key terms extracted from section content"
    )
    section_level: int = Field(
        default=1, ge=1, le=6, description="Markdown heading level (1-6)"
    )
    word_count: int = Field(
        default=0, ge=0, description="Word count of section content"
    )


class PRDDocument(BaseModel):
    """Complete PRD document representation."""

    document_id: str = Field(description="Unique identifier for the PRD document")
    concept_id: str = Field(description="ID of associated business concept")
    filename: str = Field(description="Original filename")
    upload_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When document was uploaded"
    )
    file_size_bytes: int = Field(ge=0, description="File size in bytes")
    sections: List[PRDSection] = Field(
        default_factory=list, description="Parsed sections from the PRD"
    )
    extraction_quality_score: float = Field(
        ge=0.0,
        le=10.0,
        default=0.0,
        description="Overall quality of content extraction",
    )
    processing_status: Literal[
        "uploaded", "parsing", "parsed", "integrated", "failed"
    ] = Field(default="uploaded", description="Current processing status")
    error_message: Optional[str] = Field(
        default=None, description="Error details if processing failed"
    )
    total_word_count: int = Field(
        default=0, ge=0, description="Total word count of entire document"
    )
    coverage_areas: Dict[str, float] = Field(
        default_factory=dict, description="Coverage score for each business area"
    )
    extracted_business_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured business information extracted from PRD",
    )


class PRDUploadRequest(BaseModel):
    """Request model for PRD upload."""

    concept_id: str = Field(description="ID of business concept to enhance")
    filename: str = Field(
        min_length=1, max_length=255, description="Name of the PRD file"
    )
    content_preview: str = Field(
        max_length=500, description="First 500 characters for validation"
    )
    file_size_bytes: Optional[int] = Field(
        default=None,
        ge=0,
        le=10485760,  # 10MB limit
        description="File size for validation",
    )


class PRDUploadResponse(BaseModel):
    """Response model for PRD upload."""

    document_id: str = Field(description="Generated document ID")
    concept_id: str = Field(description="Associated business concept ID")
    processing_status: str = Field(description="Current processing status")
    sections_identified: int = Field(ge=0, description="Number of sections identified")
    coverage_improvement: float = Field(
        ge=0.0, le=100.0, description="Percentage improvement in gap coverage"
    )
    reduced_questions: int = Field(
        ge=0, description="Estimated number of questions eliminated"
    )
    next_steps: List[str] = Field(
        default_factory=list, description="Recommended next actions"
    )
    quality_score: float = Field(
        ge=0.0, le=10.0, description="Quality score of parsed content"
    )
    processing_time_seconds: Optional[float] = Field(
        default=None, ge=0.0, description="Time taken to process the document"
    )


class PRDSectionMapping(BaseModel):
    """Mapping between PRD sections and business concept fields."""

    prd_section_type: str = Field(description="Type of PRD section")
    business_concept_field: str = Field(
        description="Target field in BusinessConceptRequest"
    )
    extraction_confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence in the field mapping"
    )
    extracted_value: str = Field(description="Extracted and processed value")
    original_content: str = Field(description="Original section content")


class PRDAnalysisResult(BaseModel):
    """Result of PRD analysis for business concept enhancement."""

    document_id: str = Field(description="PRD document ID")
    concept_id: str = Field(description="Business concept ID")
    field_mappings: List[PRDSectionMapping] = Field(
        default_factory=list,
        description="Mappings between PRD content and concept fields",
    )
    coverage_by_area: Dict[str, float] = Field(
        default_factory=dict, description="Coverage percentage by knowledge area"
    )
    identified_gaps: List[str] = Field(
        default_factory=list, description="Knowledge areas still needing attention"
    )
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Overall confidence in the analysis"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for next steps"
    )
    analysis_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When analysis was performed"
    )


class PRDContentExtraction(BaseModel):
    """Structured content extracted from PRD for business concept enhancement."""

    product_overview: Optional[str] = Field(
        default=None, description="Product overview and description"
    )
    target_users: Optional[str] = Field(
        default=None, description="Target user segments and personas"
    )
    business_model: Optional[str] = Field(
        default=None, description="Business model and monetization strategy"
    )
    technical_requirements: Optional[str] = Field(
        default=None, description="Technical constraints and requirements"
    )
    competitive_analysis: Optional[str] = Field(
        default=None, description="Competitive landscape analysis"
    )
    user_stories: List[str] = Field(
        default_factory=list, description="Extracted user stories"
    )
    success_metrics: List[str] = Field(
        default_factory=list, description="Success metrics and KPIs"
    )
    functional_requirements: List[str] = Field(
        default_factory=list, description="Functional requirements list"
    )
    non_functional_requirements: List[str] = Field(
        default_factory=list, description="Non-functional requirements"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Product assumptions"
    )
    constraints: List[str] = Field(
        default_factory=list, description="Known constraints"
    )
    risks: List[str] = Field(default_factory=list, description="Identified risks")
    timeline: Optional[str] = Field(
        default=None, description="Project timeline information"
    )
    budget: Optional[str] = Field(default=None, description="Budget information")


class PRDValidationResult(BaseModel):
    """Result of PRD content validation."""

    is_valid: bool = Field(description="Whether PRD content is valid")
    validation_errors: List[str] = Field(
        default_factory=list, description="Validation error messages"
    )
    validation_warnings: List[str] = Field(
        default_factory=list, description="Validation warning messages"
    )
    content_quality_score: float = Field(
        ge=0.0, le=10.0, description="Overall content quality score"
    )
    completeness_score: float = Field(
        ge=0.0, le=1.0, description="Completeness of PRD content"
    )
    structure_score: float = Field(
        ge=0.0, le=1.0, description="Quality of document structure"
    )
    min_sections_found: bool = Field(
        description="Whether minimum required sections were found"
    )
    estimated_coverage_improvement: float = Field(
        ge=0.0, le=100.0, description="Estimated improvement in knowledge coverage"
    )


class PRDProcessingMetrics(BaseModel):
    """Metrics collected during PRD processing."""

    total_processing_time: float = Field(
        ge=0.0, description="Total processing time in seconds"
    )
    parsing_time: float = Field(ge=0.0, description="Time spent parsing markdown")
    analysis_time: float = Field(ge=0.0, description="Time spent analyzing content")
    integration_time: float = Field(
        ge=0.0, description="Time spent integrating with business concept"
    )
    sections_processed: int = Field(ge=0, description="Number of sections processed")
    keywords_extracted: int = Field(ge=0, description="Number of keywords extracted")
    confidence_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Distribution of confidence scores"
    )
    error_count: int = Field(ge=0, description="Number of processing errors")
    warning_count: int = Field(ge=0, description="Number of processing warnings")
