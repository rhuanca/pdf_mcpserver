"""Configuration management for the PDF MCP Server."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Centralized configuration management using environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # PDF Documents Directory
    PDF_DOCUMENTS_DIR: Path = Path(os.getenv("PDF_DOCUMENTS_DIR", "./documents"))
    
    # ChromaDB Configuration
    CHROMA_DB_DIR: Path = Path(os.getenv("CHROMA_DB_DIR", "./chroma_db"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate required configuration values.
        
        Raises:
            ValueError: If required configuration is missing or invalid.
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY is required. Please set it in your .env file."
            )
        
        if not cls.PDF_DOCUMENTS_DIR.exists():
            raise ValueError(
                f"PDF_DOCUMENTS_DIR does not exist: {cls.PDF_DOCUMENTS_DIR}. "
                f"Please create the directory or update the path in your .env file."
            )
        
        if not cls.PDF_DOCUMENTS_DIR.is_dir():
            raise ValueError(
                f"PDF_DOCUMENTS_DIR is not a directory: {cls.PDF_DOCUMENTS_DIR}"
            )
    
    @classmethod
    def get_pdf_files(cls) -> list[Path]:
        """
        Get list of PDF files in the configured documents directory.
        
        Returns:
            List of Path objects pointing to PDF files.
        """
        return list(cls.PDF_DOCUMENTS_DIR.glob("*.pdf"))


# Singleton instance
config = Config()
