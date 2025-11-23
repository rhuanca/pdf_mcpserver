"""Unit tests for QueryHandler."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.query_handler import QueryHandler
from src.models import QueryResponse, Source


class TestQueryHandler:
    """Test suite for QueryHandler class."""
    
    @pytest.fixture
    def mock_pdf_processor(self):
        """Create a mock PDFProcessor."""
        processor = Mock()
        processor.retrieve_relevant_chunks = Mock()
        return processor
    
    @pytest.fixture
    def query_handler(self, mock_pdf_processor):
        """Create a QueryHandler instance with mocked dependencies."""
        with patch('src.query_handler.ChatOpenAI'):
            handler = QueryHandler(mock_pdf_processor)
            return handler
    
    def test_query_with_empty_question(self, query_handler):
        """Test that empty questions raise ValueError."""
        with pytest.raises(ValueError, match="Question cannot be empty"):
            query_handler.query("")
        
        with pytest.raises(ValueError, match="Question cannot be empty"):
            query_handler.query("   ")
    
    def test_query_with_no_relevant_chunks(self, query_handler, mock_pdf_processor):
        """Test query when no relevant chunks are found."""
        mock_pdf_processor.retrieve_relevant_chunks.return_value = []
        
        response = query_handler.query("What is AI?")
        
        assert isinstance(response, QueryResponse)
        assert "couldn't find" in response.answer.lower()
        assert len(response.sources) == 0
        assert response.confidence_score == 0.0
    
    def test_build_context(self, query_handler):
        """Test context building from chunks."""
        mock_chunk1 = Mock()
        mock_chunk1.page_content = "Content 1"
        mock_chunk1.metadata = {"source": "doc1.pdf"}
        
        mock_chunk2 = Mock()
        mock_chunk2.page_content = "Content 2"
        mock_chunk2.metadata = {"source": "doc2.pdf"}
        
        context = query_handler._build_context([mock_chunk1, mock_chunk2])
        
        assert "doc1.pdf" in context
        assert "doc2.pdf" in context
        assert "Content 1" in context
        assert "Content 2" in context
    
    def test_extract_sources(self, query_handler):
        """Test source extraction from chunks."""
        mock_chunk = Mock()
        mock_chunk.page_content = "This is a test content that is longer than 200 characters. " * 5
        mock_chunk.metadata = {"source": "test.pdf", "page": 42}
        
        sources = query_handler._extract_sources([mock_chunk])
        
        assert len(sources) == 1
        assert isinstance(sources[0], Source)
        assert sources[0].document_name == "test.pdf"
        assert sources[0].page_number == 42
        assert len(sources[0].chunk_text) <= 203  # 200 + "..."
    
    def test_extract_sources_deduplication(self, query_handler):
        """Test that duplicate sources are removed."""
        mock_chunk1 = Mock()
        mock_chunk1.page_content = "Content 1"
        mock_chunk1.metadata = {"source": "test.pdf", "page": 1}
        
        mock_chunk2 = Mock()
        mock_chunk2.page_content = "Content 2"
        mock_chunk2.metadata = {"source": "test.pdf", "page": 1}  # Same source
        
        sources = query_handler._extract_sources([mock_chunk1, mock_chunk2])
        
        assert len(sources) == 1  # Deduplicated
    
    def test_estimate_confidence_high(self, query_handler):
        """Test confidence estimation for high-quality answers."""
        answer = "This is a comprehensive answer that provides detailed information about the topic." * 2
        confidence = query_handler._estimate_confidence(answer, num_chunks=5)
        
        assert 0.7 <= confidence <= 1.0
    
    def test_estimate_confidence_low(self, query_handler):
        """Test confidence estimation for uncertain answers."""
        answer = "I don't know the answer to this question."
        confidence = query_handler._estimate_confidence(answer, num_chunks=1)
        
        assert 0.0 <= confidence <= 0.3
    
    def test_estimate_confidence_bounds(self, query_handler):
        """Test that confidence is always between 0.0 and 1.0."""
        # Test various scenarios
        test_cases = [
            ("Short", 1),
            ("Medium length answer here", 3),
            ("Very long answer " * 20, 5),
            ("I couldn't find any information", 1),
        ]
        
        for answer, num_chunks in test_cases:
            confidence = query_handler._estimate_confidence(answer, num_chunks)
            assert 0.0 <= confidence <= 1.0


class TestQueryResponse:
    """Test suite for QueryResponse model."""
    
    def test_query_response_creation(self):
        """Test creating a QueryResponse instance."""
        response = QueryResponse(
            answer="Test answer",
            sources=[
                Source(
                    document_name="test.pdf",
                    page_number=1,
                    chunk_text="Test chunk"
                )
            ],
            confidence_score=0.85
        )
        
        assert response.answer == "Test answer"
        assert len(response.sources) == 1
        assert response.confidence_score == 0.85
    
    def test_query_response_json_serialization(self):
        """Test JSON serialization of QueryResponse."""
        response = QueryResponse(
            answer="Test answer",
            sources=[],
            confidence_score=0.5
        )
        
        json_str = response.model_dump_json()
        assert "Test answer" in json_str
        assert "0.5" in json_str
    
    def test_confidence_score_validation(self):
        """Test that confidence score is validated to be between 0 and 1."""
        # Valid scores
        QueryResponse(answer="Test", sources=[], confidence_score=0.0)
        QueryResponse(answer="Test", sources=[], confidence_score=1.0)
        QueryResponse(answer="Test", sources=[], confidence_score=0.5)
        
        # Invalid scores should raise validation error
        with pytest.raises(Exception):  # Pydantic validation error
            QueryResponse(answer="Test", sources=[], confidence_score=1.5)
        
        with pytest.raises(Exception):
            QueryResponse(answer="Test", sources=[], confidence_score=-0.1)
