# Local RAG with Ollama

![Ollama title slide](slide_images/a.png)

This is a fully local Retrieval-Augmented Generation (RAG) system using:

- **Ollama** (`llama3.1:latest` and `nomic-embed-text`) - https://github.com/ollama/ollama
- **ChromaDB** for vector storage - https://github.com/chroma-core/chroma
- **PyMuPDF** (`fitz`) for PDF parsing
- A terminal-based chat interface

## 🔧 Setup

### 1. Install Dependencies

Create a virtual environment and install the required packages:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Ollama

Choose your platform:

**Ubuntu/Debian:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Windows:**
Download from https://ollama.com/download and install.

**Other Linux distributions:**
See installation instructions at https://ollama.com/download

### 3. Download Required Models

After installing Ollama, pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull llama3.1:latest
```

**Verify your models:**
```bash
ollama list
```

**Remove models if needed:**
```bash
ollama rm [model_name]
```

## 📂 Project Structure

```
offline-ollama-rag/
├── docs/                   # Place your PDFs here
├── test_and_qa-Scripts/    # Testing and debugging scripts
├── slide_images/           # Documentation images
├── ingested.json           # Tracks processed PDFs
├── pdf_loader.py           # PDF chunking logic
├── embedder.py             # Embedding via Ollama
├── retriever.py            # ChromaDB vector store + reranking
├── ollama_runner.py        # LLM prompt handling via Ollama
├── chat_loop.py            # Terminal input/output
├── pdf_manager.py          # Handles new PDF detection
├── rag_pipeline.py         # Main entrypoint
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 🔄 How the Pipeline Works

### **`pdf_manager.py`**
🔹 **Purpose**: Handles loading and chunking of PDFs into text blocks for embedding.

- Reads PDFs from the `docs/` directory using PyMuPDF and splits content into structured, overlapping chunks
- Tracks processed PDFs using `ingested.json` to avoid reprocessing
- **Key Function**: `process_new_pdfs(embed_func, add_func)` - the main ingestion entry point

📍 **Offline Operation**: All PDF processing happens locally with no external dependencies.

### **`embedder.py`**
🔹 **Purpose**: Converts text chunks and queries into dense numerical vectors.

- Uses Ollama's local `nomic-embed-text` model to generate 768-dimensional embeddings
- Supports both single text embedding and batch processing
- **Key Functions**: `embed_text()` for queries, batch processing for ingestion

📍 **Offline Operation**: Runs entirely through your local Ollama instance.

### **`retriever.py`**
🔹 **Purpose**: Stores and retrieves document chunks based on similarity to user queries.

- Maintains a persistent ChromaDB collection in the local `chroma_db/` folder
- Provides semantic search and reranking based on cosine similarity
- **Key Functions**: `add_chunks()` for storage, `search_similar_chunks()` for retrieval

📍 **Offline Operation**: ChromaDB operates locally with persistent storage.

### **`ollama_runner.py`**
🔹 **Purpose**: Generates natural language responses using retrieved context.

- Communicates with local Ollama instance running `llama3.1:latest`
- Formats context and questions into effective prompts
- **Key Function**: `query_llm(question, context)` - generates final answers

📍 **Offline Operation**: Uses your local LLM through Ollama's API.

### **`chat_loop.py`**
🔹 **Purpose**: Provides the interactive terminal interface.

- Handles user input and orchestrates the RAG pipeline
- Displays source information and generated responses
- **Key Function**: `chat_loop()` - the main interactive loop

📍 **Offline Operation**: Terminal-based interface with no external connections.

### **`rag_pipeline.py`**
🔹 **Purpose**: Main orchestrator that ties everything together.

- Processes new PDFs before starting the chat interface
- Single entry point for the entire system
- **Key Flow**: Ingestion → Chat → Complete RAG cycle

📍 **Offline Operation**: Coordinates all local components.

## 🚀 Usage

### Quick Start

1. **Place PDFs** in the `docs/` directory
2. **Run the system**:
   ```bash
   python rag_pipeline.py
   ```
3. **Ask questions** in the terminal
4. **Type `exit`** to quit

### Adding More Documents

The system supports multiple PDFs and incremental updates:

- Drop new PDFs into the `docs/` folder
- Run `python rag_pipeline.py` again
- Only new documents will be processed (tracked via `ingested.json`)
- Existing embeddings are preserved for efficiency

## ❓ Example Usage

```
📚 Local RAG Assistant powered by Ollama
Type your question below. Type 'exit' to quit.

> What is the main topic of the document?
📄 Based on page 1 of docs/example.pdf

[Retrieved text chunk appears here]

🤖 Generating response from LLM...
[AI-generated response based on the document]

> exit
👋 Goodbye! Thanks for using the RAG assistant.
```

## 🛠️ Troubleshooting

### Common Issues

**Ollama not responding:**
- Ensure Ollama is running: `ollama serve`
- Check if models are downloaded: `ollama list`

**No documents found:**
- Verify PDFs are in the `docs/` folder
- Check that PDFs contain readable text (not just images)

**Embedding dimension errors:**
- Delete `chroma_db/` folder and restart to rebuild the database
- Ensure you're using the correct embedding model

**Python dependencies:**
- Make sure your virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## 🎯 Educational Goals

This project demonstrates:

- **Local AI deployment** without cloud dependencies
- **Vector database operations** with ChromaDB
- **Retrieval-Augmented Generation** concepts
- **Document processing** and chunking strategies
- **Embedding-based semantic search**
- **LLM integration** through Ollama

## 🔮 Future Enhancements

Potential improvements for advanced users:

- Support for additional document formats (CSV, DOCX, etc.)
- Web-based interface
- Cloud storage integration
- Multi-modal document processing
- Advanced chunking strategies
- Query expansion and refinement

---

**Platform Compatibility**: This project works on Windows, macOS, and Linux systems.

**Hardware Requirements**: Recommended 8GB+ RAM for optimal performance with local LLMs.
