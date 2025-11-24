"""MCP Server for querying PDF documents."""

import sys
from mcp.server.fastmcp import FastMCP
from loguru import logger

from src.config import config
from src.pdf_processor import PDFProcessor
from src.query_handler import QueryHandler

# Configure logging
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=config.LOG_LEVEL
)

# Initialize MCP server
mcp = FastMCP(name="PDF Query Server")

# Global instances (initialized at startup)
pdf_processor: PDFProcessor = None
query_handler: QueryHandler = None


@mcp.tool()
def query_pdf(question: str) -> str:
    """
    Query PDF documents and get structured answers with source citations.
    
    Args:
        question: The question to ask about the PDF documents.
        
    Returns:
        JSON string containing the answer, sources, and confidence score.
        
    Example:
        >>> query_pdf("What is the main topic of the document?")
        {
            "answer": "The main topic is...",
            "sources": [
                {
                    "document_name": "example.pdf",
                    "page_number": 1,
                    "chunk_text": "..."
                }
            ],
            "confidence_score": 0.85
        }
    """
    try:
        # Lazy initialization on first query
        if query_handler is None:
            logger.info("First query received - initializing server...")
            initialize_server()
        
        # Process query
        response = query_handler.query(question)
        
        # Return as JSON string
        return response.model_dump_json(indent=2)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return f'{{"error": "Validation error: {str(e)}"}}'
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f'{{"error": "Internal error: {str(e)}"}}'


def initialize_server():
    """Initialize PDF processor and query handler (lazy - called on first query)."""
    global pdf_processor, query_handler
    
    if query_handler is not None:
        # Already initialized
        return
    
    try:
        logger.info("=" * 60)
        logger.info("PDF MCP Server - Initializing (first query)")
        logger.info("=" * 60)
        
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
        
        # Initialize query handler
        logger.info("Initializing query handler...")
        query_handler = QueryHandler(pdf_processor)
        
        logger.info("=" * 60)
        logger.info("PDF MCP Server - Ready")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PDF MCP Server - Starting")
    logger.info("PDF documents will be loaded on first query")
    logger.info("=" * 60)
    
    # Run MCP server immediately (lazy initialization)
    mcp.run()
