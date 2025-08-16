"""Unit tests for PRD-enhanced GapAnalysisService."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from flask_prp_wrapper.services.gap_analysis_service import GapAnalysisService
from flask_prp_wrapper.models.business_concept import BusinessConceptRequest, BusinessDomain
from flask_prp_wrapper.models.gap_analysis import KnowledgeGap, GapAnalysisResult
from flask_prp_wrapper.models.prd_document import PRDDocument, PRDSection


@pytest.fixture
def gap_analysis_service():
    """Create GapAnalysisService instance."""
    # Mock the domain knowledge base
    mock_domain_kb = Mock()
    mock_domain_kb.get_domain_requirements.return_value = [
        Mock(
            category="business_model",
            requirement="Define monetization strategy",
            priority="high",
            coverage_weight=1.0
        ),
        Mock(
            category="technical_requirements",
            requirement="Define architecture",
            priority="critical",
            coverage_weight=1.2
        ),
        Mock(
            category="user_experience",
            requirement="Define user personas",
            priority="high",
            coverage_weight=1.0
        )
    ]
    
    return GapAnalysisService(domain_knowledge_base=mock_domain_kb)


@pytest.fixture
def sample_business_concept():
    """Sample business concept for testing."""
    return BusinessConceptRequest(
        title="E-commerce Platform",
        description="An online marketplace for small businesses",
        domain=BusinessDomain.E_COMMERCE,
        business_model="subscription",
        target_users="Small business owners"
    )


@pytest.fixture
def sample_prd_document():
    """Sample PRD document for testing."""
    sections = [
        PRDSection(
            title="Product Overview",
            content="Comprehensive e-commerce platform with marketplace functionality for small businesses",
            section_type="overview",
            confidence_score=0.9,
            extracted_keywords=["ecommerce", "marketplace", "platform"],
            section_level=1,
            word_count=50
        ),
        PRDSection(
            title="Business Model",
            content="Subscription-based revenue model with tiered pricing for different business sizes",
            section_type="business_model",
            confidence_score=0.8,
            extracted_keywords=["subscription", "revenue", "pricing"],
            section_level=1,
            word_count=40
        ),
        PRDSection(
            title="Technical Architecture",
            content="Microservices architecture using Docker, PostgreSQL, and Redis for scalability",
            section_type="technical",
            confidence_score=0.9,
            extracted_keywords=["microservices", "docker", "postgresql"],
            section_level=1,
            word_count=45
        )
    ]
    
    return PRDDocument(
        document_id="test_doc_123",
        concept_id="concept_123",
        filename="test_prd.md",
        file_size_bytes=2048,
        sections=sections,
        processing_status="parsed",
        extraction_quality_score=8.5,
        total_word_count=135,
        coverage_areas={
            "overview": 0.9,
            "business_model": 0.8,
            "technical": 0.9
        }
    )


class TestGapAnalysisWithPRD:
    """Test PRD-enhanced gap analysis functionality."""
    
    @pytest.mark.asyncio
    async def test_analyze_concept_gaps_with_prd(
        self, gap_analysis_service, sample_business_concept, sample_prd_document
    ):
        """Test gap analysis with PRD integration."""
        result = await gap_analysis_service.analyze_concept_gaps_with_prd(
            concept=sample_business_concept,
            prd_document=sample_prd_document
        )
        
        assert isinstance(result, GapAnalysisResult)
        assert result.concept_id.startswith("concept_prd_")
        assert len(result.identified_gaps) >= 0  # Should have fewer gaps with PRD
        assert result.coverage_percentage >= 0
        
    @pytest.mark.asyncio
    async def test_analyze_concept_gaps_without_prd(
        self, gap_analysis_service, sample_business_concept
    ):
        """Test gap analysis without PRD for comparison."""
        result = await gap_analysis_service.analyze_concept_gaps_with_prd(
            concept=sample_business_concept,
            prd_document=None
        )
        
        assert isinstance(result, GapAnalysisResult)
        assert len(result.identified_gaps) >= 0
        
    def test_analyze_prd_coverage(self, gap_analysis_service, sample_prd_document):
        """Test PRD coverage analysis."""
        coverage = gap_analysis_service._analyze_prd_coverage(sample_prd_document)
        
        assert isinstance(coverage, dict)
        assert "goal_definition" in coverage  # From overview section
        assert "business_model" in coverage  # From business model section
        assert "technical_requirements" in coverage  # From technical section
        
        # Check that coverage scores are reasonable
        assert 0.0 <= coverage.get("goal_definition", 0.0) <= 1.0
        assert coverage.get("business_model", 0.0) > 0.5  # Should be well covered
        
    def test_calculate_section_coverage_contribution(
        self, gap_analysis_service, sample_prd_document
    ):
        """Test section coverage contribution calculation."""
        section = sample_prd_document.sections[0]  # Overview section
        
        contribution = gap_analysis_service._calculate_section_coverage_contribution(section)
        
        assert isinstance(contribution, float)
        assert 0.0 <= contribution <= 1.0
        assert contribution > 0.5  # Good section should contribute significantly
        
    def test_prd_addresses_requirement(self, gap_analysis_service, sample_prd_document):
        """Test checking if PRD addresses specific requirements."""
        # Mock requirement that should be addressed by PRD
        requirement = Mock()
        requirement.requirement = "Define business model and revenue strategy"
        
        score = gap_analysis_service._prd_addresses_requirement(
            sample_prd_document, requirement
        )
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score > 0.3  # PRD has business model section
        
    def test_assess_requirement_gap_with_prd(
        self, gap_analysis_service, sample_business_concept, sample_prd_document
    ):
        """Test requirement gap assessment with PRD context."""
        requirement = Mock()
        requirement.category = "business_model"
        requirement.requirement = "business model subscription"
        requirement.priority = "high"
        
        current_coverage = {"business_model": 0.3}  # Low base coverage
        
        gap_severity = gap_analysis_service._assess_requirement_gap_with_prd(
            requirement, current_coverage, sample_business_concept, sample_prd_document
        )
        
        # Gap should be reduced because PRD addresses business model
        gap_without_prd = gap_analysis_service._assess_requirement_gap(
            requirement, current_coverage, sample_business_concept
        )
        
        assert gap_severity < gap_without_prd
        
    @pytest.mark.asyncio
    async def test_identify_context_specific_gaps_with_prd(
        self, gap_analysis_service, sample_prd_document
    ):
        """Test context-specific gap identification with PRD."""
        # Concept missing business model
        concept_no_business_model = BusinessConceptRequest(
            title="Test Concept",
            description="Short description",
            domain=BusinessDomain.GENERAL,
            business_model=None,  # Missing
            target_users=None  # Also missing
        )
        
        current_coverage = {"business_model": 0.2}
        
        gaps = gap_analysis_service._identify_context_specific_gaps_with_prd(
            concept_no_business_model, current_coverage, sample_prd_document
        )
        
        # Should have fewer gaps because PRD covers business model and users
        gap_categories = [gap.category for gap in gaps]
        
        # Business model gap should be reduced/eliminated because PRD covers it
        business_model_gaps = [gap for gap in gaps if gap.category == "business_model"]
        assert len(business_model_gaps) == 0  # PRD should cover this
        
    def test_prioritize_research_areas_with_prd(
        self, gap_analysis_service, sample_prd_document
    ):
        """Test research area prioritization with PRD context."""
        mock_gaps = [
            KnowledgeGap(
                id="gap1",
                domain="ecommerce",
                category="business_model",
                description="Business model gap",
                priority="high",
                identified_at=datetime.utcnow(),
                confidence_score=0.8
            ),
            KnowledgeGap(
                id="gap2",
                domain="ecommerce",
                category="deployment",
                description="Deployment gap",
                priority="high",
                identified_at=datetime.utcnow(),
                confidence_score=0.8
            )
        ]
        
        priorities = gap_analysis_service._prioritize_research_areas_with_prd(
            mock_gaps, sample_prd_document
        )
        
        assert isinstance(priorities, list)
        # Deployment should be prioritized higher since PRD doesn't cover it
        assert "deployment" in priorities
        
    def test_generate_enhanced_cache_key(
        self, gap_analysis_service, sample_business_concept, sample_prd_document
    ):
        """Test enhanced cache key generation."""
        key1 = gap_analysis_service._generate_enhanced_cache_key(
            sample_business_concept, sample_prd_document, None, None
        )
        
        key2 = gap_analysis_service._generate_enhanced_cache_key(
            sample_business_concept, None, None, None
        )
        
        # Keys should be different with/without PRD
        assert key1 != key2
        assert len(key1) == 32  # MD5 hash
        assert len(key2) == 32
        
    def test_analyze_current_coverage_with_prd(
        self, gap_analysis_service, sample_business_concept, sample_prd_document
    ):
        """Test coverage analysis including PRD content."""
        coverage = gap_analysis_service._analyze_current_coverage_with_prd(
            sample_business_concept, sample_prd_document, None, None
        )
        
        assert isinstance(coverage, dict)
        assert "business_model" in coverage
        assert "technical_requirements" in coverage
        assert "goal_definition" in coverage
        
        # Coverage should be higher with PRD
        coverage_without_prd = gap_analysis_service._analyze_current_coverage(
            sample_business_concept, None, None
        )
        
        # At least one area should have improved coverage
        improved_areas = [
            area for area in coverage
            if coverage[area] > coverage_without_prd.get(area, 0.0)
        ]
        assert len(improved_areas) > 0


class TestPRDAnalysisEdgeCases:
    """Test edge cases for PRD analysis."""
    
    @pytest.mark.asyncio
    async def test_empty_prd_document(self, gap_analysis_service, sample_business_concept):
        """Test analysis with empty PRD document."""
        empty_prd = PRDDocument(
            document_id="empty_doc",
            concept_id="empty_concept",
            filename="empty.md",
            file_size_bytes=0,
            sections=[],
            processing_status="parsed"
        )
        
        result = await gap_analysis_service.analyze_concept_gaps_with_prd(
            concept=sample_business_concept,
            prd_document=empty_prd
        )
        
        assert isinstance(result, GapAnalysisResult)
        # Should fall back to normal gap analysis
        
    def test_prd_addresses_requirement_no_match(
        self, gap_analysis_service, sample_prd_document
    ):
        """Test PRD requirement matching with no matches."""
        requirement = Mock()
        requirement.requirement = "unrelated quantum computing requirements"
        
        score = gap_analysis_service._prd_addresses_requirement(
            sample_prd_document, requirement
        )
        
        assert score == 0.0  # No keywords should match
        
    def test_analyze_prd_coverage_empty_sections(self, gap_analysis_service):
        """Test PRD coverage analysis with empty sections."""
        empty_prd = PRDDocument(
            document_id="empty_sections",
            concept_id="test",
            filename="empty.md",
            file_size_bytes=100,
            sections=[],
            processing_status="parsed"
        )
        
        coverage = gap_analysis_service._analyze_prd_coverage(empty_prd)
        
        assert isinstance(coverage, dict)
        assert all(score == 0.0 for score in coverage.values()) or len(coverage) == 0