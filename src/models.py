"""Response models for PDF retrieval."""

from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    """Represents a retrieved document chunk."""
    
    content: str = Field(..., description="The text content of the chunk")
    document_name: str = Field(..., description="Name of the source PDF document")
    page_number: Optional[int] = Field(None, description="Page number in the document")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class RetrievalResponse(BaseModel):
    """Response containing retrieved document chunks."""
    
    query: str = Field(..., description="The original search query")
    chunks: List[DocumentChunk] = Field(
        default_factory=list,
        description="List of relevant document chunks"
    )
    total_chunks: int = Field(..., description="Total number of chunks retrieved")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What is machine learning?",
                "chunks": [
                    {
                        "content": "Machine learning is a subset of artificial intelligence...",
                        "document_name": "ai_basics.pdf",
                        "page_number": 5,
                        "metadata": {"source": "ai_basics.pdf"}
                    }
                ],
                "total_chunks": 1
            }
        }
    }
