"""Business concept data models and validation."""

from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class BusinessDomain(str, Enum):
    """Supported business domains for PRP generation."""
    
    SAAS = "saas"
    E_COMMERCE = "e_commerce"
    MOBILE_APP = "mobile_app"
    WEB_APP = "web_app"
    MARKETPLACE = "marketplace"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    EDTECH = "edtech"
    LOGISTICS = "logistics"
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    IOT = "iot"
    AI_ML = "ai_ml"
    BLOCKCHAIN = "blockchain"
    OTHER = "other"


class BusinessModel(str, Enum):
    """Common business models for context gathering."""
    
    FREEMIUM = "freemium"
    SUBSCRIPTION = "subscription"
    ONE_TIME_PURCHASE = "one_time_purchase"
    TRANSACTION_FEE = "transaction_fee"
    ADVERTISING = "advertising"
    MARKETPLACE_COMMISSION = "marketplace_commission"
    LICENSING = "licensing"
    CONSULTING = "consulting"
    API_USAGE = "api_usage"
    HYBRID = "hybrid"
    OTHER = "other"


class BusinessConceptRequest(BaseModel):
    """Request model for submitting a business concept."""
    
    title: str = Field(
        min_length=5,
        max_length=200,
        description="Concise title describing the business concept"
    )
    
    description: str = Field(
        min_length=20,
        max_length=2000,
        description="Detailed description of the business concept"
    )
    
    target_users: Optional[str] = Field(
        None,
        max_length=500,
        description="Description of target users or market segment"
    )
    
    business_model: Optional[BusinessModel] = Field(
        None,
        description="Primary business model for monetization"
    )
    
    domain: Optional[BusinessDomain] = Field(
        None,
        description="Business domain or industry category"
    )
    
    key_features: Optional[List[str]] = Field(
        None,
        max_items=10,
        description="List of key features or capabilities"
    )
    
    similar_products: Optional[List[str]] = Field(
        None,
        max_items=5,
        description="List of similar products or competitors for reference"
    )
    
    technical_preferences: Optional[Dict[str, str]] = Field(
        None,
        description="Technical preferences (e.g., programming language, framework)"
    )
    
    timeline: Optional[str] = Field(
        None,
        max_length=100,
        description="Desired timeline for implementation"
    )
    
    budget_range: Optional[str] = Field(
        None,
        max_length=50,
        description="Budget range or constraints"
    )
    
    @validator('key_features')
    def validate_key_features(cls, v):
        """Validate key features list."""
        if v:
            for feature in v:
                if not isinstance(feature, str) or len(feature.strip()) < 3:
                    raise ValueError("Each key feature must be at least 3 characters")
                if len(feature) > 200:
                    raise ValueError("Each key feature must be under 200 characters")
        return v
    
    @validator('similar_products')
    def validate_similar_products(cls, v):
        """Validate similar products list."""
        if v:
            for product in v:
                if not isinstance(product, str) or len(product.strip()) < 2:
                    raise ValueError("Each similar product must be at least 2 characters")
                if len(product) > 100:
                    raise ValueError("Each similar product must be under 100 characters")
        return v
    
    @validator('technical_preferences')
    def validate_technical_preferences(cls, v):
        """Validate technical preferences dictionary."""
        if v:
            allowed_keys = {
                'programming_language', 'framework', 'database', 'cloud_provider',
                'deployment', 'architecture', 'mobile_platform', 'ui_framework'
            }
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"Technical preference key '{key}' not allowed")
        return v


class BusinessConceptResponse(BaseModel):
    """Response model for business concept submission."""
    
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str
    domain: Optional[BusinessDomain]
    business_model: Optional[BusinessModel]
    
    # Extracted insights from concept analysis
    complexity_estimate: str = Field(description="Estimated complexity: simple, moderate, complex")
    recommended_tech_stack: Dict[str, str] = Field(description="Recommended technologies")
    estimated_timeline: str = Field(description="Estimated development timeline")
    key_challenges: List[str] = Field(description="Identified implementation challenges")
    
    # Session management
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Next steps
    needs_questionnaire: bool = Field(default=True)
    questionnaire_url: Optional[str] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConceptAnalysisResult(BaseModel):
    """Internal model for concept analysis results."""
    
    concept_id: str
    
    # Analysis results
    complexity_score: float = Field(ge=1.0, le=10.0)
    technical_feasibility: float = Field(ge=1.0, le=10.0)
    business_viability: float = Field(ge=1.0, le=10.0)
    
    # Extracted entities
    identified_features: List[str]
    required_integrations: List[str]
    suggested_architecture: Dict[str, Any]
    
    # Research needs
    research_areas: List[str]
    documentation_needs: List[str]
    
    # Quality metrics
    concept_clarity: float = Field(ge=1.0, le=10.0)
    completeness_score: float = Field(ge=1.0, le=10.0)
    
    def get_complexity_estimate(self) -> str:
        """Convert complexity score to human-readable estimate."""
        if self.complexity_score <= 3.0:
            return "simple"
        elif self.complexity_score <= 7.0:
            return "moderate"
        else:
            return "complex"
    
    def needs_more_information(self) -> bool:
        """Determine if more information is needed via questionnaire."""
        return (
            self.completeness_score < 7.0 or
            self.concept_clarity < 7.0 or
            len(self.research_areas) > 5
        )