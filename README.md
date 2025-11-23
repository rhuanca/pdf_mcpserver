# PDF MCP Server

A Model Context Protocol (MCP) server for querying PDF documents using AI-powered retrieval-augmented generation (RAG).

## 🚀 Features

- **PDF Document Processing**: Automatic parsing and indexing of PDF files using Docling
- **Hybrid Retrieval**: Combines BM25 and vector search for accurate information retrieval
- **Structured Responses**: Returns JSON with answers, source citations, and confidence scores
- **MCP Integration**: Exposes `query_pdf` tool via FastMCP for seamless integration

## 📋 Prerequisites

- Python 3.11 or later
- OpenAI API key
- PDF documents to query

## 🛠️ Installation

### 1. Clone the Repository (if not already done)

```bash
git clone <repository-url>
cd pdf_mcpserver
```

### 2. Install Dependencies with uv

```bash
uv sync
```

This will automatically:
- Create a virtual environment (`.venv`)
- Install all dependencies from `pyproject.toml`
- Set up the project

### 3. Configure Environment

Copy the example environment file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env` and set your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
PDF_DOCUMENTS_DIR=./documents
CHROMA_DB_DIR=./chroma_db
LOG_LEVEL=INFO
```

### 5. Add PDF Documents

Create a `documents` directory and add your PDF files:

```bash
mkdir documents
# Copy your PDF files to the documents/ directory
```

## 🎯 Usage

### Running the Server

```bash
uv run python main.py
```

Or activate the virtual environment first:

```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python main.py
```

The server will:
1. Validate configuration
2. Load and index all PDF files from the `documents/` directory
3. Build hybrid retriever (BM25 + Vector Search)
4. Start the MCP server

### Using the `query_pdf` Tool

The server exposes a single MCP tool: `query_pdf(question: str) -> str`

**Example Query:**
```python
query_pdf("What is the main topic of this document?")
```

**Example Response:**
```json
{
  "answer": "The main topic is artificial intelligence and machine learning...",
  "sources": [
    {
      "document_name": "ai_research.pdf",
      "page_number": 1,
      "chunk_text": "Artificial intelligence (AI) is the simulation of human intelligence..."
    }
  ],
  "confidence_score": 0.85
}
```

### Response Structure

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated answer to the question |
| `sources` | array | List of source citations with document name, page number, and relevant text |
| `confidence_score` | float | Estimated confidence (0.0 to 1.0) |

## 🏗️ Architecture

```
pdf_mcpserver/
├── src/
│   ├── config.py           # Configuration management
│   ├── models.py           # Pydantic models for responses
│   ├── pdf_processor.py    # PDF loading and indexing
│   └── query_handler.py    # Query processing and LLM integration
├── main.py                 # MCP server entry point
├── requirements.txt        # Python dependencies
└── .env                    # Environment configuration
```

### Key Components

- **PDFProcessor**: Singleton class that loads PDFs, converts to Markdown using Docling, and builds hybrid retriever
- **QueryHandler**: Processes queries, retrieves relevant chunks, and generates answers using OpenAI GPT-4o-mini
- **FastMCP**: MCP server framework that exposes the `query_pdf` tool

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `PDF_DOCUMENTS_DIR` | `./documents` | Directory containing PDF files |
| `CHROMA_DB_DIR` | `./chroma_db` | ChromaDB storage directory |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

## 🧪 Testing

Run unit tests:

```bash
uv run pytest tests/
```

## 📝 Troubleshooting

### No PDF files found

**Error**: `No PDF files found in ./documents`

**Solution**: Add PDF files to the `documents/` directory or update `PDF_DOCUMENTS_DIR` in `.env`

### OpenAI API key missing

**Error**: `OPENAI_API_KEY is required`

**Solution**: Set your OpenAI API key in the `.env` file

### Import errors

**Error**: `ModuleNotFoundError: No module named 'docling'`

**Solution**: Ensure all dependencies are installed: `uv sync`

## 📚 Dependencies

- **fastmcp**: MCP server framework
- **docling**: Document processing and parsing
- **chromadb**: Vector database for embeddings
- **langchain**: RAG framework
- **openai**: LLM provider
- **loguru**: Logging

## 🤝 Contributing

This is a Proof of Concept (PoC) implementation. For production use, consider:
- Adding caching for processed documents
- Implementing multi-agent workflow with fact verification
- Supporting additional document formats (DOCX, TXT, etc.)
- Adding authentication and rate limiting

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Based on the [docchat-docling](https://github.com/HaileyTQuach/docchat-docling) architecture.
