# PDF Retrieval MCP Server

A **completely free** Model Context Protocol (MCP) server for retrieving relevant chunks from PDF documents using hybrid search (BM25 + Vector Search).

## 🚀 Features

- **PDF Document Processing**: Automatic parsing and indexing of PDF files using Docling
- **Hybrid Retrieval**: Combines BM25 (keyword) and vector search (semantic) for accurate retrieval
- **Free Embeddings**: Uses ChromaDB's default sentence-transformers (no API costs!)
- **Pure Retrieval Mode**: Returns raw document chunks for agent processing (no LLM answer generation)
- **Fresh Start**: Clears vector database on each startup for clean indexing
- **MCP Integration**: Exposes `retrieve_pdf_chunks` tool via FastMCP for seamless agent integration

## 📋 Prerequisites

- Python 3.11 or later
- PDF documents to index
- **No API keys required!** ✨

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

### 3. Add PDF Documents

Create a `documents` directory and add your PDF files:

```bash
mkdir documents
# Copy your PDF files to the documents/ directory
```

That's it! No API keys or additional configuration needed.

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

## 🔍 Testing with MCP Inspector

The MCP Inspector is a web-based tool for testing and debugging MCP servers interactively.

### Running the Inspector

```bash
npx @modelcontextprotocol/inspector uv run python main.py
```

This command will:
1. Start the MCP Inspector proxy server
2. Launch your PDF Retrieval Server
3. Open a web browser with the Inspector UI

### What You'll See

The Inspector provides:
- **Tool Discovery**: View available tools (`retrieve_pdf_chunks`)
- **Interactive Testing**: Test queries with custom parameters
- **Real-time Responses**: See JSON responses in real-time
- **Request/Response Logs**: Debug the MCP protocol communication

### Example Inspector Workflow

1. **Open the Inspector** - Browser opens automatically at `http://localhost:6274`
2. **Wait for Initialization** - Server loads and indexes PDFs on first query (~1-2 minutes)
3. **Select Tool** - Click on `retrieve_pdf_chunks` in the tools list
4. **Enter Query** - Type your search query (e.g., "machine learning")
5. **Set Parameters** - Optionally adjust `max_chunks` (default: 5)
6. **Execute** - Click "Run" to see the results
7. **View Response** - Inspect the returned chunks and metadata

### Inspector Tips

- **First query is slow**: PDF indexing happens on first query (87 seconds for typical PDFs)
- **Subsequent queries are fast**: Embeddings are cached in ChromaDB
- **Fresh start**: Server clears ChromaDB on each restart for clean indexing
- **Check logs**: Terminal shows detailed logging of the indexing process


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
- **RetrievalHandler**: Retrieves relevant chunks for queries - no LLM answer## 🔧 Configuration

Configuration is managed through environment variables. Create a `.env` file in the project root:

```bash
# Optional: PDF Documents Directory (defaults to ./documents)
PDF_DOCUMENTS_DIR=./documents

# Optional: ChromaDB Directory (defaults to ./chroma_db)
CHROMA_DB_DIR=./chroma_db

# Optional: Log Level (defaults to INFO)
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PDF_DOCUMENTS_DIR` | No | `./documents` | Directory containing PDF files to index |
| `CHROMA_DB_DIR` | No | `./chroma_db` | Directory for ChromaDB vector storage |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

**Note**: No API keys required! ChromaDB uses free local embeddings (sentence-transformers).

## 🧪 Testing

Run unit tests:

```bash
uv run pytest tests/
```

## 📝 Troubleshooting

### No PDF files found

**Error**: `No PDF files found in ./documents`

**Solution**: Add PDF files to the `documents/` directory or update `PDF_DOCUMENTS_DIR` in `.env`

### Import errors

**Error**: `ModuleNotFoundError: No module named 'docling'`

**Solution**: Ensure all dependencies are installed: `uv sync`

### CUDA out of memory

**Error**: `CUDA out of memory`

**Solution**: The server is configured to use CPU-only mode. If you still see this error, check that `CUDA_VISIBLE_DEVICES=""` is set in `src/pdf_processor.py`

## 📚 Dependencies

- **fastmcp**: MCP server framework
- **docling**: Document processing and parsing
- **chromadb**: Vector database with free sentence-transformers embeddings
- **langchain**: RAG framework and retrievers
- **loguru**: Logging

**No paid APIs required!** All embeddings are generated locally using ChromaDB's default model (all-MiniLM-L6-v2).

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
