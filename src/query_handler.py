"""Query processing and structured response generation."""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from loguru import logger

from src.models import QueryResponse, Source
from src.pdf_processor import PDFProcessor
from src.config import config


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
            model="gpt-4o-mini",
            temperature=0.1,
            openai_api_key=config.OPENAI_API_KEY
        )
        logger.info("QueryHandler initialized with gpt-4o-mini")
    
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
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        question = question.strip()
        logger.info(f"Processing query: {question}")
        
        try:
            # Retrieve relevant chunks
            relevant_chunks = self.pdf_processor.retrieve_relevant_chunks(
                query=question,
                k=5
            )
            
            if not relevant_chunks:
                logger.warning("No relevant chunks found")
                return QueryResponse(
                    answer="I couldn't find any relevant information in the documents to answer your question.",
                    sources=[],
                    confidence_score=0.0
                )
            
            # Build context from chunks
            context = self._build_context(relevant_chunks)
            
            # Generate answer using LLM
            answer = self._generate_answer(question, context)
            
            # Extract sources
            sources = self._extract_sources(relevant_chunks)
            
            # Estimate confidence (simple heuristic)
            confidence = self._estimate_confidence(answer, len(relevant_chunks))
            
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
    
    def _generate_answer(self, question: str, context: str) -> str:
        """
        Generate an answer using the LLM.
        
        Args:
            question: The user's question.
            context: Retrieved context from documents.
            
        Returns:
            Generated answer.
        """
        system_prompt = """You are a helpful assistant that answers questions based on the provided document context.

Instructions:
- Answer the question using ONLY the information from the provided context
- If the context doesn't contain enough information, say so clearly
- Be concise and accurate
- Cite specific sources when possible
- Do not make up information not present in the context"""

        user_prompt = f"""Context from documents:
{context}

Question: {question}

Answer:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content.strip()
    
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
            
            # Truncate chunk text for readability
            chunk_text = chunk.page_content[:200]
            if len(chunk.page_content) > 200:
                chunk_text += "..."
            
            sources.append(Source(
                document_name=source_name,
                page_number=page_number,
                chunk_text=chunk_text
            ))
        
        return sources
    
    def _estimate_confidence(self, answer: str, num_chunks: int) -> float:
        """
        Estimate confidence score based on simple heuristics.
        
        Args:
            answer: Generated answer.
            num_chunks: Number of retrieved chunks.
            
        Returns:
            Confidence score between 0.0 and 1.0.
        """
        # Simple heuristic based on:
        # 1. Answer length (longer = more confident)
        # 2. Number of chunks (more = more confident)
        # 3. Presence of uncertainty phrases
        
        confidence = 0.5  # Base confidence
        
        # Adjust based on answer length
        if len(answer) > 100:
            confidence += 0.2
        elif len(answer) < 30:
            confidence -= 0.2
        
        # Adjust based on number of chunks
        if num_chunks >= 3:
            confidence += 0.2
        elif num_chunks == 1:
            confidence -= 0.1
        
        # Check for uncertainty phrases
        uncertainty_phrases = [
            "i don't know",
            "i couldn't find",
            "not enough information",
            "unclear",
            "uncertain"
        ]
        
        answer_lower = answer.lower()
        if any(phrase in answer_lower for phrase in uncertainty_phrases):
            confidence -= 0.3
        
        # Clamp to [0.0, 1.0]
        return max(0.0, min(1.0, confidence))
