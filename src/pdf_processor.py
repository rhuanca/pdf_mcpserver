"""PDF processing and indexing using docling and ChromaDB."""

import os
import hashlib
import shutil
from pathlib import Path
from typing import List, Optional

# Force CPU-only processing to avoid GPU memory issues
os.environ["CUDA_VISIBLE_DEVICES"] = ""

from docling.document_converter import DocumentConverter
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from loguru import logger

from src.config import config
from src.constants import (
    BM25_TOP_K,
    VECTOR_SEARCH_TOP_K,
    HYBRID_RETRIEVER_WEIGHTS,
    MARKDOWN_HEADERS,
)


class PDFProcessor:
    """
    Singleton class for processing and indexing PDF documents.
    
    Uses docling for PDF parsing, ChromaDB for vector storage,
    and hybrid retrieval (BM25 + Vector Search).
    
    Uses ChromaDB's default free embeddings (no OpenAI required).
    """
    
    _instance: Optional['PDFProcessor'] = None
    
    def __new__(cls):
        """Implement Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the PDF processor (only once due to Singleton)."""
        if self._initialized:
            return
            
        self.headers = MARKDOWN_HEADERS
        self.chunks: List = []
        self.hybrid_retriever: Optional[EnsembleRetriever] = None
        self._initialized = True
        
        logger.info("PDFProcessor initialized (using free ChromaDB embeddings)")
    
    @staticmethod
    def clear_vector_db():
        """Clear the ChromaDB directory for a fresh start."""
        if config.CHROMA_DB_DIR.exists():
            try:
                shutil.rmtree(config.CHROMA_DB_DIR)
                logger.info(f"Cleared vector database: {config.CHROMA_DB_DIR}")
            except Exception as e:
                logger.warning(f"Failed to clear vector database: {e}")
    
    def load_and_index_pdfs(self) -> None:
        """
        Load and index all PDF files from the configured directory.
        
        Raises:
            ValueError: If no PDF files are found in the directory.
        """
        pdf_files = config.get_pdf_files()
        
        if not pdf_files:
            raise ValueError(
                f"No PDF files found in {config.PDF_DOCUMENTS_DIR}. "
                f"Please add PDF files to index."
            )
        
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
        
        all_chunks = []
        seen_hashes = set()
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing: {pdf_file.name}")
                chunks = self._process_pdf(pdf_file)
                
                # Deduplicate chunks across files
                for chunk in chunks:
                    chunk_hash = self._generate_hash(chunk.page_content.encode())
                    if chunk_hash not in seen_hashes:
                        all_chunks.append(chunk)
                        seen_hashes.add(chunk_hash)
                
                logger.info(f"Processed {len(chunks)} chunks from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {str(e)}")
                continue
        
        if not all_chunks:
            raise ValueError("No chunks were successfully processed from PDF files")
        
        self.chunks = all_chunks
        logger.info(f"Total unique chunks: {len(self.chunks)}")
        
        # Build hybrid retriever
        self._build_hybrid_retriever()
    
    def _process_pdf(self, pdf_path: Path) -> List:
        """
        Process a single PDF file using docling.
        
        Args:
            pdf_path: Path to the PDF file.
            
        Returns:
            List of document chunks.
        """
        # Convert PDF to Markdown using docling
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        markdown = result.document.export_to_markdown()
        
        # Split markdown by headers
        splitter = MarkdownHeaderTextSplitter(self.headers)
        chunks = splitter.split_text(markdown)
        
        # Add metadata to chunks
        for chunk in chunks:
            chunk.metadata["source"] = pdf_path.name
        
        return chunks
    
    def _build_hybrid_retriever(self) -> None:
        """Build a hybrid retriever using BM25 and vector-based retrieval."""
        try:
            # Create Chroma vector store with default free embeddings
            # ChromaDB will use sentence-transformers (all-MiniLM-L6-v2) by default
            vector_store = Chroma.from_documents(
                documents=self.chunks,
                persist_directory=str(config.CHROMA_DB_DIR)
            )
            logger.info("Vector store created with free ChromaDB embeddings")
            
            # Create BM25 retriever
            bm25 = BM25Retriever.from_documents(self.chunks)
            bm25.k = BM25_TOP_K
            logger.info("BM25 retriever created successfully")
            
            # Create vector-based retriever
            vector_retriever = vector_store.as_retriever(
                search_kwargs={"k": VECTOR_SEARCH_TOP_K}
            )
            logger.info("Vector retriever created successfully")
            
            # Combine retrievers into a hybrid retriever
            self.hybrid_retriever = EnsembleRetriever(
                retrievers=[bm25, vector_retriever],
                weights=HYBRID_RETRIEVER_WEIGHTS
            )
            logger.info("Hybrid retriever created successfully")
            
        except Exception as e:
            logger.error(f"Failed to build hybrid retriever: {e}")
            raise
    
    def retrieve_relevant_chunks(self, query: str, k: int = 5) -> List:
        """
        Retrieve relevant chunks for a given query.
        
        Args:
            query: The search query.
            k: Number of chunks to retrieve.
            
        Returns:
            List of relevant document chunks.
            
        Raises:
            ValueError: If retriever is not initialized.
        """
        if self.hybrid_retriever is None:
            raise ValueError(
                "Retriever not initialized. Call load_and_index_pdfs() first."
            )
        
        try:
            results = self.hybrid_retriever.invoke(query)
            # Limit to k results
            return results[:k]
        except Exception as e:
            logger.error(f"Failed to retrieve chunks: {e}")
            raise
    
    @staticmethod
    def _generate_hash(content: bytes) -> str:
        """Generate SHA256 hash of content."""
        return hashlib.sha256(content).hexdigest()
