"""Document retrieval handler - returns raw chunks for agent processing."""

from typing import List
from loguru import logger

from src.models import RetrievalResponse, DocumentChunk
from src.pdf_processor import PDFProcessor
from src.constants import DEFAULT_CHUNK_LIMIT


class RetrievalHandler:
    """
    Handles document retrieval from indexed PDFs.
    
    Returns raw document chunks for processing by calling agents.
    No LLM-based answer generation - pure retrieval only.
    """
    
    def __init__(self, pdf_processor: PDFProcessor):
        """
        Initialize the retrieval handler.
        
        Args:
            pdf_processor: Initialized PDFProcessor instance.
        """
        self.pdf_processor = pdf_processor
        logger.info("RetrievalHandler initialized (pure retrieval mode)")
    
    def retrieve(self, query: str, max_chunks: int = DEFAULT_CHUNK_LIMIT) -> RetrievalResponse:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: The search query.
            max_chunks: Maximum number of chunks to return.
            
        Returns:
            RetrievalResponse with retrieved chunks.
            
        Raises:
            ValueError: If query is empty or invalid.
        """
        self._validate_query(query)
        query = query.strip()
        logger.info(f"Retrieving chunks for query: {query}")
        
        try:
            # Retrieve relevant chunks using hybrid search
            raw_chunks = self.pdf_processor.retrieve_relevant_chunks(
                query=query,
                k=max_chunks
            )
            
            # Convert to structured format
            document_chunks = self._convert_to_document_chunks(raw_chunks)
            
            response = RetrievalResponse(
                query=query,
                chunks=document_chunks,
                total_chunks=len(document_chunks)
            )
            
            logger.info(f"Retrieved {len(document_chunks)} chunk(s)")
            return response
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise
    
    def _validate_query(self, query: str) -> None:
        """Validate that query is not empty."""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
    
    def _convert_to_document_chunks(self, raw_chunks: List) -> List[DocumentChunk]:
        """
        Convert raw langchain chunks to DocumentChunk models.
        
        Args:
            raw_chunks: List of langchain document chunks.
            
        Returns:
            List of DocumentChunk objects.
        """
        document_chunks = []
        
        for chunk in raw_chunks:
            doc_chunk = DocumentChunk(
                content=chunk.page_content,
                document_name=chunk.metadata.get("source", "Unknown"),
                page_number=chunk.metadata.get("page", None),
                metadata=chunk.metadata
            )
            document_chunks.append(doc_chunk)
        
        return document_chunks
