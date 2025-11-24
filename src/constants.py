"""Constants for the PDF MCP Server."""

# Retrieval Configuration
DEFAULT_CHUNK_LIMIT = 5
BM25_TOP_K = 3
VECTOR_SEARCH_TOP_K = 3
HYBRID_RETRIEVER_WEIGHTS = [0.5, 0.5]  # [BM25, Vector]

# Text Processing
MAX_CHUNK_PREVIEW_LENGTH = 200
MARKDOWN_HEADERS = [("#", "Header 1"), ("##", "Header 2")]

# LLM Configuration
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1
EMBEDDING_MODEL = "text-embedding-3-small"

# Confidence Scoring
BASE_CONFIDENCE = 0.5
CONFIDENCE_LONG_ANSWER_THRESHOLD = 100
CONFIDENCE_SHORT_ANSWER_THRESHOLD = 30
CONFIDENCE_MIN_CHUNKS_THRESHOLD = 3
CONFIDENCE_BOOST_LONG = 0.2
CONFIDENCE_PENALTY_SHORT = 0.2
CONFIDENCE_BOOST_MANY_CHUNKS = 0.2
CONFIDENCE_PENALTY_FEW_CHUNKS = 0.1
CONFIDENCE_PENALTY_UNCERTAINTY = 0.3

# Uncertainty Detection
UNCERTAINTY_PHRASES = [
    "i don't know",
    "i couldn't find",
    "not enough information",
    "unclear",
    "uncertain"
]

# System Prompts
SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided document context.

Instructions:
- Answer the question using ONLY the information from the provided context
- If the context doesn't contain enough information, say so clearly
- Be concise and accurate
- Cite specific sources when possible
- Do not make up information not present in the context"""

# Response Messages
NO_CHUNKS_FOUND_MESSAGE = "I couldn't find any relevant information in the documents to answer your question."
