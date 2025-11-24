"""Query processing and structured response generation."""

from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

from src.models import QueryResponse, Source
from src.pdf_processor import PDFProcessor
from src.config import config
from src.constants import (
    DEFAULT_CHUNK_LIMIT,
    LLM_MODEL,
    LLM_TEMPERATURE,
    MAX_CHUNK_PREVIEW_LENGTH,
    SYSTEM_PROMPT,
    NO_CHUNKS_FOUND_MESSAGE
)
from src.confidence import estimate_confidence


class QueryHandler:
    """
    Handles query processing and structured response generation.
    
    Retrieves relevant chunks from PDFs and generates answers using OpenAI LLM.
    """
    
    def __init__(self, pdf_processor: PDFProcessor):
        """
        Initialize the query handler.
        
        Args:
            pdf_processor: Initialized PDFProcessor instance.
        """
        self.pdf_processor = pdf_processor
        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=config.OPENAI_API_KEY
        )
        logger.info(f"QueryHandler initialized with {LLM_MODEL}")
    
    def query(self, question: str) -> QueryResponse:
        """
        Process a query and generate a structured response.
        
        Args:
            question: The user's question.
            
        Returns:
            QueryResponse with answer, sources, and confidence score.
            
        Raises:
            ValueError: If question is empty or invalid.
        """
        self._validate_question(question)
        question = question.strip()
        logger.info(f"Processing query: {question}")
        
        try:
            relevant_chunks = self._retrieve_chunks(question)
            
            if not relevant_chunks:
                return self._create_no_results_response()
            
            answer = self._generate_answer(question, relevant_chunks)
            sources = self._extract_sources(relevant_chunks)
            confidence = estimate_confidence(answer, len(relevant_chunks))
            
            response = QueryResponse(
                answer=answer,
                sources=sources,
                confidence_score=confidence
            )
            
            logger.info(f"Query processed successfully. Confidence: {confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
    
    def _validate_question(self, question: str) -> None:
        """Validate that question is not empty."""
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
    
    def _retrieve_chunks(self, question: str) -> List:
        """Retrieve relevant chunks for the question."""
        chunks = self.pdf_processor.retrieve_relevant_chunks(
            query=question,
            k=DEFAULT_CHUNK_LIMIT
        )
        
        if not chunks:
            logger.warning("No relevant chunks found")
        
        return chunks
    
    def _create_no_results_response(self) -> QueryResponse:
        """Create response when no relevant chunks are found."""
        return QueryResponse(
            answer=NO_CHUNKS_FOUND_MESSAGE,
            sources=[],
            confidence_score=0.0
        )
    
    def _generate_answer(self, question: str, chunks: List) -> str:
        """
        Generate an answer using the LLM.
        
        Args:
            question: The user's question.
            chunks: Retrieved document chunks.
            
        Returns:
            Generated answer.
        """
        context = self._build_context(chunks)
        user_prompt = self._build_user_prompt(question, context)
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()
    
    def _build_context(self, chunks: List) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of document chunks.
            
        Returns:
            Formatted context string.
        """
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source", "Unknown")
            content = chunk.page_content
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_user_prompt(self, question: str, context: str) -> str:
        """Build the user prompt with context and question."""
        return f"""Context from documents:
{context}

Question: {question}

Answer:"""
    
    def _extract_sources(self, chunks: List) -> List[Source]:
        """
        Extract source citations from chunks.
        
        Args:
            chunks: List of document chunks.
            
        Returns:
            List of Source objects.
        """
        sources = []
        seen_sources = set()
        
        for chunk in chunks:
            source_name = chunk.metadata.get("source", "Unknown")
            page_number = chunk.metadata.get("page", None)
            
            # Create unique key to avoid duplicates
            source_key = (source_name, page_number)
            if source_key in seen_sources:
                continue
            
            seen_sources.add(source_key)
            
            chunk_text = self._truncate_text(
                chunk.page_content,
                MAX_CHUNK_PREVIEW_LENGTH
            )
            
            sources.append(Source(
                document_name=source_name,
                page_number=page_number,
                chunk_text=chunk_text
            ))
        
        return sources
    
    @staticmethod
    def _truncate_text(text: str, max_length: int) -> str:
        """Truncate text to max_length with ellipsis if needed."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."
