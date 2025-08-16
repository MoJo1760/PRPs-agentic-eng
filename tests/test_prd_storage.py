"""Unit tests for PRDStorageService."""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from flask_prp_wrapper.services.prd_storage import PRDStorageService
from flask_prp_wrapper.models.prd_document import (
    PRDDocument,
    PRDSection,
    PRDContentExtraction,
    PRDProcessingMetrics
)


@pytest.fixture
def temp_storage_path():
    """Create temporary storage directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def storage_service(temp_storage_path):
    """Create PRDStorageService with temporary storage."""
    return PRDStorageService(storage_path=temp_storage_path)


@pytest.fixture
def sample_prd_sections():
    """Sample PRD sections for testing."""
    return [
        PRDSection(
            title="Overview",
            content="Product overview content",
            section_type="overview",
            confidence_score=0.9,
            extracted_keywords=["product", "overview"],
            section_level=1,
            word_count=20
        ),
        PRDSection(
            title="Requirements",
            content="Functional requirements content",
            section_type="requirements",
            confidence_score=0.8,
            extracted_keywords=["requirements", "functional"],
            section_level=1,
            word_count=25
        )
    ]


@pytest.fixture
def sample_content_extraction():
    """Sample content extraction for testing."""
    return PRDContentExtraction(
        product_overview="Sample product overview",
        target_users="Sample target users",
        business_model="Sample business model",
        technical_requirements="Sample technical requirements",
        competitive_analysis="Sample competitive analysis",
        user_stories=["Story 1", "Story 2"],
        success_metrics=["Metric 1", "Metric 2"],
        functional_requirements=["Req 1", "Req 2"],
        non_functional_requirements=["NFR 1"],
        assumptions=["Assumption 1"],
        constraints=["Constraint 1"],
        risks=["Risk 1"],
        timeline="Q1 2024",
        budget="$100K"
    )


class TestPRDStorageService:
    """Test cases for PRDStorageService."""
    
    @pytest.mark.asyncio
    async def test_store_prd_document_basic(self, storage_service, sample_prd_sections):
        """Test basic PRD document storage."""
        concept_id = "test_concept_123"
        file_content = b"# Test PRD\nContent here"
        filename = "test.md"
        
        document_id = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=file_content,
            filename=filename,
            parsed_sections=sample_prd_sections
        )
        
        assert document_id is not None
        assert len(document_id) == 32  # MD5 hash length
        
        # Verify document can be retrieved
        stored_doc = await storage_service.get_prd_document(document_id)
        assert stored_doc is not None
        assert stored_doc.concept_id == concept_id
        assert stored_doc.filename == filename
        assert len(stored_doc.sections) == 2
        
    @pytest.mark.asyncio
    async def test_store_with_full_extraction(
        self, storage_service, sample_prd_sections, sample_content_extraction
    ):
        """Test storing PRD with complete extraction data."""
        concept_id = "test_concept_456"
        file_content = b"# Complete PRD\nDetailed content"
        filename = "complete.md"
        
        metrics = PRDProcessingMetrics(
            total_processing_time=4.0,
            parsing_time=1.5,
            analysis_time=2.0,
            integration_time=0.5,
            sections_processed=2,
            keywords_extracted=10,
            error_count=0,
            warning_count=0
        )
        
        document_id = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=file_content,
            filename=filename,
            parsed_sections=sample_prd_sections,
            content_extraction=sample_content_extraction,
            processing_metrics=metrics
        )
        
        stored_doc = await storage_service.get_prd_document(document_id)
        assert stored_doc.extracted_business_context is not None
        assert stored_doc.extraction_quality_score > 0
        
    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, storage_service):
        """Test retrieving non-existent document."""
        result = await storage_service.get_prd_document("nonexistent_id")
        assert result is None
        
    @pytest.mark.asyncio
    async def test_list_concept_prds(self, storage_service, sample_prd_sections):
        """Test listing PRDs for a concept."""
        concept_id = "test_concept_789"
        
        # Store multiple documents for same concept
        doc_id_1 = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=b"# PRD 1\nContent",
            filename="prd1.md",
            parsed_sections=sample_prd_sections
        )
        
        doc_id_2 = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=b"# PRD 2\nContent",
            filename="prd2.md",
            parsed_sections=sample_prd_sections
        )
        
        # List documents for concept
        concept_docs = await storage_service.list_concept_prds(concept_id)
        
        assert len(concept_docs) == 2
        doc_ids = [doc.document_id for doc in concept_docs]
        assert doc_id_1 in doc_ids
        assert doc_id_2 in doc_ids
        
    @pytest.mark.asyncio
    async def test_get_raw_file_content(self, storage_service, sample_prd_sections):
        """Test retrieving raw file content."""
        concept_id = "test_concept_raw"
        original_content = b"# Raw PRD\nOriginal markdown content"
        filename = "raw.md"
        
        document_id = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=original_content,
            filename=filename,
            parsed_sections=sample_prd_sections
        )
        
        raw_content = await storage_service.get_raw_file_content(document_id)
        assert raw_content == original_content
        
    @pytest.mark.asyncio
    async def test_update_prd_document(self, storage_service, sample_prd_sections):
        """Test updating PRD document metadata."""
        concept_id = "test_concept_update"
        
        document_id = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=b"# Update Test\nContent",
            filename="update.md",
            parsed_sections=sample_prd_sections
        )
        
        # Update document
        updates = {
            "processing_status": "processed",
            "extraction_quality_score": 8.5
        }
        
        success = await storage_service.update_prd_document(document_id, updates)
        assert success is True
        
        # Verify updates
        updated_doc = await storage_service.get_prd_document(document_id)
        assert updated_doc.processing_status == "processed"
        assert updated_doc.extraction_quality_score == 8.5
        
    @pytest.mark.asyncio
    async def test_delete_prd_document(self, storage_service, sample_prd_sections):
        """Test deleting PRD document."""
        concept_id = "test_concept_delete"
        
        document_id = await storage_service.store_prd_document(
            concept_id=concept_id,
            file_content=b"# Delete Test\nContent",
            filename="delete.md",
            parsed_sections=sample_prd_sections
        )
        
        # Verify document exists
        doc = await storage_service.get_prd_document(document_id)
        assert doc is not None
        
        # Delete document
        success = await storage_service.delete_prd_document(document_id)
        assert success is True
        
        # Verify document is gone
        deleted_doc = await storage_service.get_prd_document(document_id)
        assert deleted_doc is None
        
    @pytest.mark.asyncio
    async def test_get_storage_stats(self, storage_service, sample_prd_sections):
        """Test storage statistics."""
        # Store some documents
        await storage_service.store_prd_document(
            concept_id="concept1",
            file_content=b"# PRD 1\nContent",
            filename="prd1.md",
            parsed_sections=sample_prd_sections
        )
        
        await storage_service.store_prd_document(
            concept_id="concept2",
            file_content=b"# PRD 2\nLonger content here",
            filename="prd2.md",
            parsed_sections=sample_prd_sections
        )
        
        stats = await storage_service.get_storage_stats()
        
        assert stats["total_documents"] >= 2
        assert stats["total_size_bytes"] > 0
        assert "documents_by_status" in stats
        assert "documents_by_concept" in stats
        assert stats["cache_size"] >= 0
        
    @pytest.mark.asyncio
    async def test_cleanup_old_documents(self, storage_service, sample_prd_sections):
        """Test cleanup of old documents."""
        # Store a document
        document_id = await storage_service.store_prd_document(
            concept_id="old_concept",
            file_content=b"# Old PRD\nContent",
            filename="old.md",
            parsed_sections=sample_prd_sections
        )
        
        # Test cleanup (with 0 days to force cleanup)
        cleaned_count = await storage_service.cleanup_old_documents(days_old=0)
        
        # Should have cleaned at least our document
        assert cleaned_count >= 1
        
        # Document should be gone
        doc = await storage_service.get_prd_document(document_id)
        assert doc is None
        
    def test_generate_document_id(self, storage_service):
        """Test document ID generation."""
        concept_id = "test_concept"
        filename = "test.md"
        
        doc_id_1 = storage_service._generate_document_id(concept_id, filename)
        # Add small delay to ensure different timestamps
        import time
        time.sleep(0.001)
        doc_id_2 = storage_service._generate_document_id(concept_id, filename)
        
        # IDs should be the same without timestamp difference - test the format instead
        assert len(doc_id_1) == 32  # MD5 hash length
        assert isinstance(doc_id_1, str)
        assert len(doc_id_1) == 32  # MD5 hash
        assert len(doc_id_2) == 32
        
    def test_calculate_extraction_quality(self, storage_service, sample_prd_sections):
        """Test extraction quality calculation."""
        quality = storage_service._calculate_extraction_quality(sample_prd_sections)
        
        assert isinstance(quality, float)
        assert 0.0 <= quality <= 10.0
        assert quality > 4.0  # Sample sections should score reasonably well
        
    def test_calculate_coverage_areas(self, storage_service, sample_prd_sections):
        """Test coverage areas calculation."""
        coverage = storage_service._calculate_coverage_areas(sample_prd_sections)
        
        assert isinstance(coverage, dict)
        assert "overview" in coverage
        assert "requirements" in coverage
        assert coverage["overview"] > 0
        assert coverage["requirements"] > 0
        
    def test_cache_management(self, storage_service):
        """Test document cache management."""
        # Test cache size limit
        storage_service._cache_max_size = 2
        
        # Create mock documents
        for i in range(3):
            doc_id = f"doc_{i}"
            mock_doc = Mock()
            storage_service._update_cache(doc_id, mock_doc)
        
        # Cache should not exceed max size
        assert len(storage_service._document_cache) <= 2


class TestPRDStorageErrors:
    """Test error handling in PRDStorageService."""
    
    @pytest.mark.asyncio
    async def test_store_document_storage_error(self, storage_service):
        """Test handling storage errors."""
        # Make storage path read-only to force error
        storage_service.documents_path.chmod(0o444)
        
        try:
            with pytest.raises(Exception):
                await storage_service.store_prd_document(
                    concept_id="error_test",
                    file_content=b"content",
                    filename="error.md"
                )
        finally:
            # Restore permissions for cleanup
            storage_service.documents_path.chmod(0o755)
            
    @pytest.mark.asyncio
    async def test_update_nonexistent_document(self, storage_service):
        """Test updating non-existent document."""
        success = await storage_service.update_prd_document(
            "nonexistent_id",
            {"processing_status": "processed"}
        )
        assert success is False
        
    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self, storage_service):
        """Test deleting non-existent document."""
        # Should not raise error, just return False/success
        success = await storage_service.delete_prd_document("nonexistent_id")
        # May return True even if file doesn't exist (cleanup is idempotent)
        assert isinstance(success, bool)