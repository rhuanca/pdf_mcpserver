"""Pydantic models for structured JSON responses."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Source(BaseModel):
    """Represents a source citation for an answer."""
    
    document_name: str = Field(..., description="Name of the PDF document")
    page_number: Optional[int] = Field(None, description="Page number in the document")
    chunk_text: Optional[str] = Field(None, description="Relevant text chunk from the source")


class QueryResponse(BaseModel):
    """Structured response for PDF queries."""
    
    answer: str = Field(..., description="The answer to the user's question")
    sources: List[Source] = Field(default_factory=list, description="List of source citations")
    confidence_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Confidence score of the answer (0.0 to 1.0)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "The capital of France is Paris.",
                "sources": [
                    {
                        "document_name": "geography.pdf",
                        "page_number": 42,
                        "chunk_text": "Paris is the capital and largest city of France..."
                    }
                ],
                "confidence_score": 0.95
            }
        }
    }
