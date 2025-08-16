"""Unit tests for PRD-enhanced QuestioningEngine."""

import pytest
from unittest.mock import Mock, AsyncMock
from flask_prp_wrapper.services.questioning_engine import QuestioningEngine
from flask_prp_wrapper.models.business_concept import BusinessConceptRequest, BusinessDomain
from flask_prp_wrapper.models.questionnaire import Question
from flask_prp_wrapper.models.gap_analysis import GapAnalysisResult, KnowledgeGap
from flask_prp_wrapper.models.prd_document import PRDDocument, PRDSection
from datetime import datetime


@pytest.fixture
def questioning_engine():
    """Create QuestioningEngine instance."""
    return QuestioningEngine()


@pytest.fixture
def sample_business_concept():
    """Sample business concept for testing."""
    return BusinessConceptRequest(
        title="SaaS Analytics Platform",
        description="Business intelligence platform for small companies",
        domain=BusinessDomain.SAAS,
        business_model="subscription",
        target_users="Small business analysts"
    )


@pytest.fixture
def sample_prd_document():
    """Sample PRD document with comprehensive sections."""
    sections = [
        PRDSection(
            title="Product Vision",
            content="Analytics platform that provides real-time insights for small businesses to make data-driven decisions",
            section_type="overview",
            confidence_score=0.9,
            extracted_keywords=["analytics", "insights", "data-driven"],
            section_level=1,
            word_count=60
        ),
        PRDSection(
            title="Target Users",
            content="Small business owners and analysts who need easy-to-use business intelligence tools",
            section_type="users",
            confidence_score=0.8,
            extracted_keywords=["business", "owners", "analysts"],
            section_level=1,
            word_count=40
        ),
        PRDSection(
            title="Core Features",
            content="Dashboard creation, data visualization, automated reporting, real-time alerts",
            section_type="requirements",
            confidence_score=0.85,
            extracted_keywords=["dashboard", "visualization", "reporting"],
            section_level=1,
            word_count=35
        )
    ]
    
    return PRDDocument(
        document_id="test_prd_456",
        concept_id="concept_456",
        filename="analytics_prd.md",
        file_size_bytes=1500,
        sections=sections,
        processing_status="processed",
        extraction_quality_score=8.0,
        total_word_count=135
    )


@pytest.fixture
def sample_gap_analysis():
    """Sample gap analysis result."""
    gaps = [
        KnowledgeGap(
            id="gap1",
            domain="saas",
            category="business_model",
            description="Need pricing strategy details",
            priority="high",
            identified_at=datetime.utcnow(),
            confidence_score=0.8
        ),
        KnowledgeGap(
            id="gap2",
            domain="saas",
            category="technical_requirements",
            description="Need database architecture details",
            priority="critical",
            identified_at=datetime.utcnow(),
            confidence_score=0.9
        ),
        KnowledgeGap(
            id="gap3",
            domain="saas",
            category="user_experience",
            description="Need user interface mockups",
            priority="medium",
            identified_at=datetime.utcnow(),
            confidence_score=0.7
        )
    ]
    
    return GapAnalysisResult(
        concept_id="concept_456",
        identified_gaps=gaps,
        coverage_percentage=65.0,
        domain_completeness={"business_model": 60.0, "technical_requirements": 70.0},
        analysis_timestamp=datetime.utcnow(),
        next_research_areas=["technical_requirements", "business_model"],
        critical_gaps_count=1,
        high_priority_gaps_count=1
    )


class TestQuestioningEngineWithPRD:
    """Test PRD-aware questioning functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_prd_aware_questions_basic(
        self, questioning_engine, sample_business_concept, sample_prd_document, sample_gap_analysis
    ):
        """Test basic PRD-aware question generation."""
        questions = await questioning_engine.generate_prd_aware_questions(
            concept=sample_business_concept,
            prd_document=sample_prd_document,
            gap_analysis=sample_gap_analysis,
            max_questions=5
        )
        
        assert isinstance(questions, list)
        assert len(questions) <= 5
        assert all(isinstance(q, Question) for q in questions)
        
    @pytest.mark.asyncio
    async def test_generate_prd_aware_questions_no_prd(
        self, questioning_engine, sample_business_concept, sample_gap_analysis
    ):
        """Test question generation without PRD document."""
        questions = await questioning_engine.generate_prd_aware_questions(
            concept=sample_business_concept,
            prd_document=None,
            gap_analysis=sample_gap_analysis,
            max_questions=5
        )
        
        assert isinstance(questions, list)
        assert len(questions) <= 5
        # Should generate questions normally without PRD
        
    @pytest.mark.asyncio
    async def test_generate_prd_aware_questions_filters_covered_topics(
        self, questioning_engine, sample_business_concept, sample_prd_document
    ):
        """Test that PRD-aware questions filter out covered topics."""
        # Mock gap analysis with gaps that PRD covers
        gaps_covered_by_prd = [
            KnowledgeGap(
                id="gap_covered",
                domain="saas",
                category="user_experience",  # Covered by PRD users section
                description="Need user persona details",
                priority="high",
                identified_at=datetime.utcnow(),
                confidence_score=0.8
            )
        ]
        
        gap_analysis_covered = GapAnalysisResult(
            concept_id="concept_covered",
            identified_gaps=gaps_covered_by_prd,
            coverage_percentage=80.0,
            domain_completeness={"user_experience": 85.0},
            analysis_timestamp=datetime.utcnow(),
            next_research_areas=["user_experience"],
            critical_gaps_count=0,
            high_priority_gaps_count=1
        )
        
        questions = await questioning_engine.generate_prd_aware_questions(
            concept=sample_business_concept,
            prd_document=sample_prd_document,
            gap_analysis=gap_analysis_covered,
            max_questions=10
        )
        
        # Should generate fewer questions since PRD covers user experience
        assert len(questions) <= 10
        
    def test_analyze_prd_content_overlap(self, questioning_engine, sample_prd_document):
        """Test PRD content overlap analysis."""
        test_content = "analytics dashboard visualization business intelligence"
        
        overlap_score = questioning_engine._analyze_prd_content_overlap(
            test_content, sample_prd_document
        )
        
        assert isinstance(overlap_score, float)
        assert 0.0 <= overlap_score <= 1.0
        assert overlap_score > 0.3  # Should have significant overlap
        
    def test_analyze_prd_content_overlap_no_overlap(self, questioning_engine, sample_prd_document):
        """Test PRD content overlap with no overlapping content."""
        test_content = "quantum computing blockchain cryptocurrency mining"
        
        overlap_score = questioning_engine._analyze_prd_content_overlap(
            test_content, sample_prd_document
        )
        
        assert overlap_score < 0.2  # Should have minimal overlap
        
    def test_filter_questions_by_prd_coverage(
        self, questioning_engine, sample_prd_document
    ):
        """Test question filtering based on PRD coverage."""
        # Mock questions - some covered by PRD, some not
        mock_questions = [
            Mock(
                content="What is your target user demographic?",  # Covered by PRD
                metadata={"primary_keywords": ["target", "user", "demographic"]}
            ),
            Mock(
                content="What is your pricing strategy?",  # Partially covered
                metadata={"primary_keywords": ["pricing", "strategy"]}
            ),
            Mock(
                content="What are your deployment requirements?",  # Not covered
                metadata={"primary_keywords": ["deployment", "requirements"]}
            )
        ]
        
        filtered_questions = questioning_engine._filter_questions_by_prd_coverage(
            mock_questions, sample_prd_document, overlap_threshold=0.4
        )
        
        # Should filter out questions with high PRD overlap
        assert len(filtered_questions) <= len(mock_questions)
        
    def test_calculate_prd_coverage_for_area(self, questioning_engine, sample_prd_document):
        """Test PRD coverage calculation for specific areas."""
        # Test coverage for user experience (should be high)
        user_coverage = questioning_engine._calculate_prd_coverage_for_area(
            "user_experience", sample_prd_document
        )
        assert user_coverage > 0.5  # Should be well covered
        
        # Test coverage for deployment (should be low)
        deploy_coverage = questioning_engine._calculate_prd_coverage_for_area(
            "deployment", sample_prd_document
        )
        assert deploy_coverage < 0.3  # Should not be well covered


class TestQuestioningEngineEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.mark.asyncio
    async def test_generate_prd_aware_questions_empty_gaps(
        self, questioning_engine, sample_business_concept, sample_prd_document
    ):
        """Test question generation with no gaps."""
        empty_gap_analysis = GapAnalysisResult(
            concept_id="no_gaps",
            identified_gaps=[],
            coverage_percentage=100.0,
            domain_completeness={},
            analysis_timestamp=datetime.utcnow(),
            next_research_areas=[],
            critical_gaps_count=0,
            high_priority_gaps_count=0
        )
        
        questions = await questioning_engine.generate_prd_aware_questions(
            concept=sample_business_concept,
            prd_document=sample_prd_document,
            gap_analysis=empty_gap_analysis,
            max_questions=5
        )
        
        assert isinstance(questions, list)
        # Should still be able to generate some questions
        
    @pytest.mark.asyncio
    async def test_generate_prd_aware_questions_max_limit(
        self, questioning_engine, sample_business_concept, sample_gap_analysis
    ):
        """Test question generation respects max limit."""
        questions = await questioning_engine.generate_prd_aware_questions(
            concept=sample_business_concept,
            prd_document=None,
            gap_analysis=sample_gap_analysis,
            max_questions=2
        )
        
        assert len(questions) <= 2
        
    def test_analyze_prd_content_overlap_empty_content(
        self, questioning_engine, sample_prd_document
    ):
        """Test PRD overlap analysis with empty content."""
        overlap_score = questioning_engine._analyze_prd_content_overlap(
            "", sample_prd_document
        )
        
        assert overlap_score == 0.0
        
    def test_filter_questions_empty_list(self, questioning_engine, sample_prd_document):
        """Test filtering empty question list."""
        filtered = questioning_engine._filter_questions_by_prd_coverage(
            [], sample_prd_document, overlap_threshold=0.5
        )
        
        assert filtered == []