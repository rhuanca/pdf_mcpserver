"""MCP Server for retrieving relevant chunks from PDF documents."""

import sys
from mcp.server.fastmcp import FastMCP
from loguru import logger

from src.config import config
from src.pdf_processor import PDFProcessor
from src.retrieval_handler import RetrievalHandler

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL
)

# Initialize MCP server
mcp = FastMCP(name="PDF Retrieval Server")

# Global instances (initialized on first query)
pdf_processor: PDFProcessor = None
retrieval_handler: RetrievalHandler = None


@mcp.tool()
def retrieve_pdf_chunks(query: str, max_chunks: int = 5) -> str:
    """
    Retrieve relevant chunks from indexed PDF documents.
    
    This tool performs semantic search over PDF documents and returns
    the most relevant text chunks. The calling agent can then use these
    chunks to answer questions or perform analysis.
    
    Args:
        query: The search query to find relevant document chunks.
        max_chunks: Maximum number of chunks to return (default: 5).
        
    Returns:
        JSON string containing:
        - query: The original search query
        - chunks: List of relevant document chunks with:
          - content: The text content
          - document_name: Source PDF filename
          - page_number: Page number (if available)
          - metadata: Additional metadata
        - total_chunks: Number of chunks returned
        
    Example:
        >>> retrieve_pdf_chunks("machine learning algorithms")
        {
            "query": "machine learning algorithms",
            "chunks": [
                {
                    "content": "Machine learning algorithms can be categorized...",
                    "document_name": "ml_guide.pdf",
                    "page_number": 12,
                    "metadata": {"source": "ml_guide.pdf"}
                }
            ],
            "total_chunks": 1
        }
    """
    try:
        # Lazy initialization on first query
        if retrieval_handler is None:
            logger.info("First query received - initializing server...")
            initialize_server()
        
        # Retrieve chunks
        response = retrieval_handler.retrieve(query, max_chunks)
        
        # Return as JSON string
        return response.model_dump_json(indent=2)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return f'{{"error": "Validation error: {str(e)}"}}'
    except Exception as e:
        logger.error(f"Error retrieving chunks: {e}")
        return f'{{"error": "Internal error: {str(e)}"}}'


def initialize_server():
    """Initialize PDF processor and retrieval handler (lazy - called on first query)."""
    global pdf_processor, retrieval_handler
    
    if retrieval_handler is not None:
        # Already initialized
        return
    
    try:
        logger.info("=" * 60)
        logger.info("PDF Retrieval Server - Initializing (first query)")
        logger.info("=" * 60)
        
        # Clear vector database for fresh start
        logger.info("Clearing vector database for fresh start...")
        PDFProcessor.clear_vector_db()
        
        # Validate configuration
        logger.info("Validating configuration...")
        config.validate()
        logger.info(f"PDF Documents Directory: {config.PDF_DOCUMENTS_DIR}")
        logger.info(f"ChromaDB Directory: {config.CHROMA_DB_DIR}")
        
        # Initialize PDF processor
        logger.info("Initializing PDF processor...")
        pdf_processor = PDFProcessor()
        
        # Load and index PDFs
        logger.info("Loading and indexing PDF documents...")
        pdf_processor.load_and_index_pdfs()
        
        # Initialize retrieval handler
        logger.info("Initializing retrieval handler...")
        retrieval_handler = RetrievalHandler(pdf_processor)
        
        logger.info("=" * 60)
        logger.info("PDF Retrieval Server - Ready")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PDF Retrieval Server - Starting")
    logger.info("Pure retrieval mode - returns chunks for agent processing")
    logger.info("PDF documents will be loaded on first query")
    logger.info("=" * 60)
    
    # Run MCP server immediately (lazy initialization)
    mcp.run()
