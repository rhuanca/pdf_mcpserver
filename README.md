# PDF Retrieval MCP Server

A Model Context Protocol (MCP) server for retrieving relevant chunks from PDF documents using hybrid search (BM25 + Vector Search).

## 🚀 Features

- **PDF Document Processing**: Automatic parsing and indexing of PDF files using Docling
- **Hybrid Retrieval**: Combines BM25 (keyword) and vector search (semantic) for accurate retrieval
- **Pure Retrieval Mode**: Returns raw document chunks for agent processing (no LLM answer generation)
- **MCP Integration**: Exposes `retrieve_pdf_chunks` tool via FastMCP for seamless agent integration

## 📋 Prerequisites

- Python 3.11 or later
- OpenAI API key (for embeddings only)
- PDF documents to index

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
1. Start immediately (lazy initialization)
2. Load and index PDFs on first query
3. Be ready to retrieve document chunks via MCP

### Using the `retrieve_pdf_chunks` Tool

The server exposes a single MCP tool: `retrieve_pdf_chunks(query: str, max_chunks: int = 5) -> str`

**Example Query:**
```python
retrieve_pdf_chunks("machine learning algorithms", max_chunks=3)
```

**Example Response:**
```json
{
  "query": "machine learning algorithms",
  "chunks": [
    {
      "content": "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning...",
      "document_name": "ml_guide.pdf",
      "page_number": 12,
      "metadata": {"source": "ml_guide.pdf"}
    },
    {
      "content": "Common supervised learning algorithms include linear regression, decision trees, and neural networks...",
      "document_name": "ml_guide.pdf",
      "page_number": 15,
      "metadata": {"source": "ml_guide.pdf"}
    }
  ],
  "total_chunks": 2
}
```

### Response Structure

| Field | Type | Description |
|-------|------|-------------|
| `query` | string | The original search query |
| `chunks` | array | List of relevant document chunks |
| `chunks[].content` | string | The text content of the chunk |
| `chunks[].document_name` | string | Source PDF filename |
| `chunks[].page_number` | int | Page number (if available) |
| `chunks[].metadata` | object | Additional metadata |
| `total_chunks` | int | Number of chunks returned |

### How Agents Use This

When an agent (like Claude) calls this tool:
1. Agent sends a search query
2. Server returns relevant document chunks
3. Agent uses chunks in its context to answer questions

**Example Agent Flow:**
```
User: "What are the main ML algorithms discussed?"
  ↓
Agent calls: retrieve_pdf_chunks("machine learning algorithms")
  ↓
Server returns: 3 relevant chunks from PDFs
  ↓
Agent reads chunks and generates answer for user
```

## 🏗️ Architecture

```
pdf_mcpserver/
├── src/
│   ├── config.py              # Configuration management
│   ├── constants.py           # Configuration constants
│   ├── models.py              # Pydantic response models
│   ├── pdf_processor.py       # PDF loading and hybrid retrieval
│   └── retrieval_handler.py   # Document chunk retrieval
├── main.py                    # MCP server entry point
├── pyproject.toml             # Project metadata
└── .env                       # Environment configuration
```

### Key Components

- **PDFProcessor**: Singleton class that loads PDFs, converts to Markdown using Docling, and builds hybrid retriever (BM25 + Vector Search)
- **RetrievalHandler**: Retrieves relevant chunks for queries - no LLM answer generation
- **FastMCP**: MCP server framework that exposes the `retrieve_pdf_chunks` tool

### Why Pure Retrieval?

This design allows calling agents (Claude, GPT, etc.) to:
- Use their own LLM for answer generation
- Have full control over the reasoning process
- Avoid redundant LLM calls
- Reduce costs and latency

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
- **langchain**: RAG framework and retrievers
- **openai**: Embeddings only (text-embedding-3-small)
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
