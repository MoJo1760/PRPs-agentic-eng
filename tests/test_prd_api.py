"""Unit tests for PRD API endpoints."""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from io import BytesIO
from flask_prp_wrapper.app import create_app
from flask_prp_wrapper.models.prd_document import PRDDocument, PRDSection


@pytest.fixture
def app():
    """Create test application."""
    app = create_app('testing')
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def sample_prd_file_data():
    """Sample PRD file content for upload testing."""
    return b"""# Product Requirements Document

## Overview
This is a comprehensive PRD for testing purposes.

## Target Users
Small business owners and entrepreneurs.

## Requirements
- User authentication
- Dashboard functionality
- Reporting features

## Technical Specifications
- REST API
- PostgreSQL database
- React frontend
"""


@pytest.fixture
def sample_prd_document():
    """Sample PRD document object."""
    sections = [
        PRDSection(
            title="Overview",
            content="Comprehensive PRD for testing",
            section_type="overview",
            confidence_score=0.9,
            extracted_keywords=["comprehensive", "testing"],
            section_level=1,
            word_count=25
        )
    ]
    
    return PRDDocument(
        document_id="test_doc_789",
        concept_id="concept_789",
        filename="test_prd.md",
        file_size_bytes=1024,
        sections=sections,
        processing_status="parsed",
        extraction_quality_score=8.0
    )


class TestPRDUploadEndpoints:
    """Test PRD upload and management endpoints."""
    
    @patch('flask_prp_wrapper.api.routes.PRDParserService')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_upload_prd_document_success(
        self, mock_storage_service, mock_parser_service, client, sample_prd_file_data
    ):
        """Test successful PRD document upload."""
        # Mock service responses
        mock_parser = mock_parser_service.return_value
        mock_parser.parse_prd_content = AsyncMock(return_value=[])
        mock_parser.extract_business_context = AsyncMock(return_value=Mock())
        mock_parser.validate_prd_content = AsyncMock(return_value=Mock(is_valid=True))
        
        mock_storage = mock_storage_service.return_value
        mock_storage.store_prd_document = AsyncMock(return_value="doc_123")
        
        # Create file upload
        data = {
            'prd_file': (BytesIO(sample_prd_file_data), 'test_prd.md')
        }
        
        response = client.post(
            '/api/v1/concepts/concept_123/prd-upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'document_id' in response_data
        assert 'processing_status' in response_data
        
    def test_upload_prd_document_no_file(self, client):
        """Test PRD upload without file."""
        response = client.post('/api/v1/concepts/concept_123/prd-upload')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        
    def test_upload_prd_document_invalid_extension(self, client):
        """Test PRD upload with invalid file extension."""
        data = {
            'prd_file': (BytesIO(b"content"), 'test.pdf')
        }
        
        response = client.post(
            '/api/v1/concepts/concept_123/prd-upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'Invalid file type' in response_data['error']
        
    def test_upload_prd_document_too_large(self, client):
        """Test PRD upload with file too large."""
        # Create file larger than 10MB limit
        large_content = b"x" * (11 * 1024 * 1024)
        data = {
            'prd_file': (BytesIO(large_content), 'large.md')
        }
        
        response = client.post(
            '/api/v1/concepts/concept_123/prd-upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'too large' in response_data['error']
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_get_prd_document_success(self, mock_storage_service, client, sample_prd_document):
        """Test successful PRD document retrieval."""
        mock_storage = mock_storage_service.return_value
        mock_storage.get_prd_document = AsyncMock(return_value=sample_prd_document)
        
        response = client.get('/api/v1/prd-documents/test_doc_789')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['document_id'] == 'test_doc_789'
        assert response_data['concept_id'] == 'concept_789'
        assert 'sections' in response_data
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_get_prd_document_not_found(self, mock_storage_service, client):
        """Test PRD document retrieval when not found."""
        mock_storage = mock_storage_service.return_value
        mock_storage.get_prd_document = AsyncMock(return_value=None)
        
        response = client.get('/api/v1/prd-documents/nonexistent')
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'error' in response_data
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_list_concept_prds(self, mock_storage_service, client):
        """Test listing PRDs for a concept."""
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[])
        
        response = client.get('/api/v1/concepts/concept_123/prd-documents')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'documents' in response_data
        assert isinstance(response_data['documents'], list)
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_delete_prd_document_success(self, mock_storage_service, client):
        """Test successful PRD document deletion."""
        mock_storage = mock_storage_service.return_value
        mock_storage.delete_prd_document = AsyncMock(return_value=True)
        
        response = client.delete('/api/v1/prd-documents/test_doc_789')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['success'] is True
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_delete_prd_document_not_found(self, mock_storage_service, client):
        """Test PRD document deletion when not found."""
        mock_storage = mock_storage_service.return_value
        mock_storage.delete_prd_document = AsyncMock(return_value=False)
        
        response = client.delete('/api/v1/prd-documents/nonexistent')
        
        assert response.status_code == 404
        response_data = response.get_json()
        assert 'error' in response_data


class TestPRDEnhancedEndpoints:
    """Test PRD-enhanced existing endpoints."""
    
    @patch('flask_prp_wrapper.api.routes.QuestioningEngine')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_get_prd_enhancement_questions(
        self, mock_storage_service, mock_questioning_engine, client, sample_prd_document
    ):
        """Test PRD enhancement questions endpoint."""
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[sample_prd_document])
        
        mock_engine = mock_questioning_engine.return_value
        mock_questions = [
            Mock(content="What is your deployment strategy?", 
                 question_type="open_ended",
                 category="technical",
                 priority="medium",
                 metadata={})
        ]
        mock_engine.generate_prd_aware_questions = AsyncMock(return_value=mock_questions)
        
        response = client.get('/api/v1/concepts/concept_789/prd-enhancement-questions')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert 'questions' in response_data
        assert 'prd_documents_found' in response_data
        assert response_data['prd_documents_found'] == 1
        
    @patch('flask_prp_wrapper.api.routes.QuestioningEngine')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_get_prd_enhancement_questions_no_prd(
        self, mock_storage_service, mock_questioning_engine, client
    ):
        """Test PRD enhancement questions when no PRD exists."""
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[])
        
        response = client.get('/api/v1/concepts/concept_456/prd-enhancement-questions')
        
        assert response.status_code == 200
        response_data = response.get_json()
        assert response_data['prd_documents_found'] == 0
        assert 'questions' in response_data
        
    @patch('flask_prp_wrapper.api.routes.GapAnalysisService')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_analyze_business_concept_with_prd(
        self, mock_storage_service, mock_gap_service, client, sample_prd_document
    ):
        """Test business concept analysis with PRD integration."""
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[sample_prd_document])
        
        mock_gap_analysis = mock_gap_service.return_value
        mock_result = Mock()
        mock_result.dict.return_value = {"coverage_percentage": 85.0}
        mock_gap_analysis.analyze_concept_gaps_with_prd = AsyncMock(return_value=mock_result)
        
        concept_data = {
            "title": "Test Concept",
            "description": "Test description",
            "domain": "saas",
            "business_model": "subscription"
        }
        
        response = client.post(
            '/api/v1/analyze',
            data=json.dumps(concept_data),
            content_type='application/json'
        )
        
        # Should use PRD-enhanced analysis
        mock_gap_analysis.analyze_concept_gaps_with_prd.assert_called_once()


class TestPRDAPIErrorHandling:
    """Test error handling in PRD API endpoints."""
    
    @patch('flask_prp_wrapper.api.routes.PRDParserService')
    def test_upload_prd_parsing_error(self, mock_parser_service, client, sample_prd_file_data):
        """Test handling of PRD parsing errors."""
        mock_parser = mock_parser_service.return_value
        mock_parser.parse_prd_content = AsyncMock(side_effect=Exception("Parsing failed"))
        
        data = {
            'prd_file': (BytesIO(sample_prd_file_data), 'error_test.md')
        }
        
        response = client.post(
            '/api/v1/concepts/concept_123/prd-upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 500
        response_data = response.get_json()
        assert 'error' in response_data
        
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_get_prd_document_storage_error(self, mock_storage_service, client):
        """Test handling of storage errors during retrieval."""
        mock_storage = mock_storage_service.return_value
        mock_storage.get_prd_document = AsyncMock(side_effect=Exception("Storage error"))
        
        response = client.get('/api/v1/prd-documents/error_doc')
        
        assert response.status_code == 500
        response_data = response.get_json()
        assert 'error' in response_data
        
    @patch('flask_prp_wrapper.api.routes.QuestioningEngine')
    def test_prd_enhancement_questions_service_error(self, mock_questioning_engine, client):
        """Test handling of service errors in enhancement questions."""
        mock_engine = mock_questioning_engine.return_value
        mock_engine.generate_prd_aware_questions = AsyncMock(
            side_effect=Exception("Question generation failed")
        )
        
        response = client.get('/api/v1/concepts/concept_123/prd-enhancement-questions')
        
        assert response.status_code == 500
        response_data = response.get_json()
        assert 'error' in response_data


class TestPRDAPIValidation:
    """Test validation in PRD API endpoints."""
    
    def test_upload_prd_invalid_concept_id(self, client, sample_prd_file_data):
        """Test PRD upload with invalid concept ID format."""
        data = {
            'prd_file': (BytesIO(sample_prd_file_data), 'test.md')
        }
        
        # Test with very short concept ID
        response = client.post(
            '/api/v1/concepts/x/prd-upload',
            data=data,
            content_type='multipart/form-data'
        )
        
        # Should handle gracefully (may succeed depending on validation rules)
        assert response.status_code in [200, 400]
        
    def test_get_prd_document_invalid_id_format(self, client):
        """Test PRD retrieval with invalid document ID format."""
        response = client.get('/api/v1/prd-documents/invalid-id-format!')
        
        # Should handle gracefully
        assert response.status_code in [404, 400]
        
    def test_prd_enhancement_questions_invalid_params(self, client):
        """Test PRD enhancement questions with invalid parameters."""
        # Test with invalid max_questions parameter
        response = client.get(
            '/api/v1/concepts/concept_123/prd-enhancement-questions?max_questions=invalid'
        )
        
        # Should handle gracefully, likely using default
        assert response.status_code in [200, 400]
        
        # Test with negative max_questions
        response = client.get(
            '/api/v1/concepts/concept_123/prd-enhancement-questions?max_questions=-5'
        )
        
        assert response.status_code in [200, 400]


class TestPRDIntegrationEndpoints:
    """Test PRD integration with existing endpoints."""
    
    @patch('flask_prp_wrapper.api.routes.GapAnalysisService')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_analyze_concept_uses_prd_when_available(
        self, mock_storage_service, mock_gap_service, client, sample_prd_document
    ):
        """Test that analyze endpoint uses PRD when available."""
        # Mock PRD storage to return a document
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[sample_prd_document])
        
        # Mock gap analysis service
        mock_gap_analysis = mock_gap_service.return_value
        mock_result = Mock()
        mock_result.dict.return_value = {
            "coverage_percentage": 90.0,
            "identified_gaps": [],
            "prd_enhanced": True
        }
        mock_gap_analysis.analyze_concept_gaps_with_prd = AsyncMock(return_value=mock_result)
        
        concept_data = {
            "title": "Test Concept with PRD",
            "description": "Test description",
            "domain": "saas"
        }
        
        response = client.post(
            '/api/v1/analyze',
            data=json.dumps(concept_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        # Verify PRD-enhanced analysis was called
        mock_gap_analysis.analyze_concept_gaps_with_prd.assert_called_once()
        
    @patch('flask_prp_wrapper.api.routes.QuestioningEngine')
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_generate_questions_uses_prd_context(
        self, mock_storage_service, mock_questioning_engine, client, sample_prd_document
    ):
        """Test that question generation uses PRD context when available."""
        # Mock PRD storage
        mock_storage = mock_storage_service.return_value
        mock_storage.list_concept_prds = AsyncMock(return_value=[sample_prd_document])
        
        # Mock questioning engine
        mock_engine = mock_questioning_engine.return_value
        mock_questions = [Mock(dict=Mock(return_value={"content": "Test question"}))]
        mock_engine.generate_prd_aware_questions = AsyncMock(return_value=mock_questions)
        
        concept_data = {
            "title": "Test Concept",
            "description": "Test description",
            "domain": "saas"
        }
        
        response = client.post(
            '/api/v1/generate-questions',
            data=json.dumps(concept_data),
            content_type='application/json'
        )
        
        # Should call PRD-aware question generation
        mock_engine.generate_prd_aware_questions.assert_called_once()


class TestPRDAPIDocumentation:
    """Test API documentation and response formats."""
    
    @patch('flask_prp_wrapper.api.routes.PRDStorageService')
    def test_prd_document_response_format(self, mock_storage_service, client, sample_prd_document):
        """Test PRD document response contains all expected fields."""
        mock_storage = mock_storage_service.return_value
        mock_storage.get_prd_document = AsyncMock(return_value=sample_prd_document)
        
        response = client.get('/api/v1/prd-documents/test_doc_789')
        
        assert response.status_code == 200
        response_data = response.get_json()
        
        # Check required fields
        required_fields = [
            'document_id', 'concept_id', 'filename', 'file_size_bytes',
            'upload_timestamp', 'processing_status', 'sections'
        ]
        for field in required_fields:
            assert field in response_data
            
        # Check section format
        if response_data['sections']:
            section = response_data['sections'][0]
            section_fields = [
                'title', 'content', 'section_type', 'confidence_score',
                'extracted_keywords', 'section_level', 'word_count'
            ]
            for field in section_fields:
                assert field in section
                
    def test_prd_upload_response_format(self, client):
        """Test PRD upload response format for successful upload."""
        # This test would need actual file processing to work
        # For now, just test the error response format
        response = client.post('/api/v1/concepts/concept_123/prd-upload')
        
        assert response.status_code == 400
        response_data = response.get_json()
        assert 'error' in response_data
        assert isinstance(response_data['error'], str)