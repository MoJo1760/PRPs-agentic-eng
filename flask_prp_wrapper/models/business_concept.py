"""Business concept data models."""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum


class BusinessDomain(str, Enum):
    """Supported business domains."""

    SAAS = "saas"
    E_COMMERCE = "e_commerce"
    MOBILE_APP = "mobile_app"
    MARKETPLACE = "marketplace"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    PRODUCTIVITY = "productivity"
    SOCIAL = "social"
    GAMING = "gaming"
    IOT = "iot"
    BLOCKCHAIN = "blockchain"
    AI_ML = "ai_ml"
    CONTENT = "content"
    OTHER = "other"


class BusinessModel(str, Enum):
    """Common business models."""

    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    MARKETPLACE = "marketplace"
    TRANSACTION_FEE = "transaction_fee"
    ONE_TIME_PURCHASE = "one_time_purchase"
    ADVERTISING = "advertising"
    ENTERPRISE = "enterprise"
    B2B_SAAS = "b2b_saas"
    B2C_SAAS = "b2c_saas"
    OTHER = "other"


class BusinessConceptRequest(BaseModel):
    """Request model for submitting a business concept."""

    title: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Concise title for the business concept",
    )
    description: str = Field(
        ...,
        min_length=20,
        max_length=2000,
        description="Detailed description of the business idea",
    )
    target_users: Optional[str] = Field(
        None, max_length=500, description="Who are the target users or customers"
    )
    business_model: Optional[BusinessModel] = Field(
        None, description="How the business will make money"
    )
    domain: Optional[BusinessDomain] = Field(
        None, description="Business domain or industry"
    )
    estimated_timeline: Optional[str] = Field(
        None, max_length=100, description="Estimated development timeline"
    )
    budget_range: Optional[str] = Field(
        None, max_length=100, description="Estimated budget range"
    )
    technical_constraints: Optional[str] = Field(
        None, max_length=1000, description="Any technical constraints or preferences"
    )
    existing_competitors: Optional[str] = Field(
        None, max_length=1000, description="Known competitors or similar solutions"
    )

    @validator("title")
    def title_must_be_meaningful(cls, v):
        """Validate title is meaningful."""
        if len(v.strip()) < 5:
            raise ValueError("Title must be at least 5 characters long")
        return v.strip()

    @validator("description")
    def description_must_be_detailed(cls, v):
        """Validate description provides enough detail."""
        if len(v.strip()) < 20:
            raise ValueError("Description must be at least 20 characters long")
        return v.strip()


class BusinessConceptResponse(BaseModel):
    """Response model for business concept submission."""

    concept_id: str = Field(..., description="Unique identifier for the concept")
    title: str
    description: str
    domain: Optional[BusinessDomain]
    business_model: Optional[BusinessModel]
    created_at: datetime
    status: Literal["submitted", "analyzing", "ready_for_questions"] = "submitted"
    next_step: str = Field(..., description="Description of what happens next")
    estimated_questions: int = Field(
        ..., ge=0, le=15, description="Estimated number of follow-up questions"
    )


class ConceptAnalysis(BaseModel):
    """Analysis of a business concept."""

    concept_id: str
    complexity_score: float = Field(..., ge=0, le=10)
    feasibility_score: float = Field(..., ge=0, le=10)
    market_potential_score: float = Field(..., ge=0, le=10)
    technical_challenges: List[str]
    market_opportunities: List[str]
    recommended_mvp_features: List[str]
    similar_successful_products: List[str]
    analysis_timestamp: datetime

    @property
    def overall_score(self) -> float:
        """Calculate overall viability score."""
        return (
            self.complexity_score + self.feasibility_score + self.market_potential_score
        ) / 3
