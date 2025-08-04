# Local RAG with Ollama

![Ollama title slide](slide_images/a.png)


This is a fully local Retrieval-Augmented Generation (RAG) system using:

- Ollama (`phi4-mini` and `nomic-embed-text`) https://github.com/ollama/ollama
- ChromaDB for vector storage https://github.com/chroma-core/chroma
- PyMuPDF (`fitz`) for PDF parsing
- A terminal-based chat interface

## 🔧 Setup

### 1. Install Dependencies

Setup a virtual .env for the project: 

```
python3 -m venv .venv && source .venv/bin/activate
```

> Please refer the the `requirements.txt` file for the full list.
```bash
pip install -r requirements.txt
```

### 2. Install Ollama

- **Ubuntu**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

- **macOS**:
```bash
brew install ollama
```
- **Windows**:
Download from https://ollama.com/download and install.

### 3. Then pull the required models:

```bash
ollama pull nomic-embed-text
ollama pull phi4-mini
```

You can check all the model files you have downloaded locall via ollama using: 
```bash
ollama list
```
Removing a model file is as easy as: 
```bash
ollama rm [model_name]
```
You can view the Ollama server on your machine once it's installed and launched by using
```
ollama serve
```

## 📂 Project Structure

```
rag_local_ollama/
├── GettingStarted/         # Lab guide we'll walk through in class
├── docs/                   # Place your PDFs here
├── test_and_qa-Scripts/    # Extra testing scripts used for build - you won't need these
├── ingested.json           # Tracks processed PDFs
├── pdf_loader.py           # PDF chunking logic
├── embedder.py             # Embedding via Ollama
├── retriever.py            # ChromaDB vector store + reranking
├── ollama_runner.py        # LLM prompt handling via Ollama
├── chat_loop.py            # Terminal input/output
├── pdf_manager.py          # Handles new PDF detection
├── rag_pipeline.py         # Main entrypoint
```

### 🪠 How our pipeline works:

**`pdf_manager`.py**
🔹 Purpose: Handles loading and chunking of PDFs into text blocks for embedding.

- Reads PDFs from the docs/ directory using PyMuPDF or similar, and splits their content into structured, overlapping chunks.
- Tracks which PDFs have already been embedded using ingested.json, ensuring new files are the only ones reprocessed.
- Critical Function: process_new_pdfs(embed_func, add_func) ties together loading, chunking, embedding, and storage — it is the ingestion entry point.

📍 Offline Note: No cloud or web access is needed — all PDF processing happens locally.

**`embedder.py`**
🔹 Purpose: Converts text chunks and queries into dense numerical vectors.

- Uses Ollama's locally running nomic-embed-text model to generate 768-dimensional embeddings.
- Implements both embed_text(text: str) and embed_text_batch(texts: List[str]) to handle single or bulk embedding.
- Critical Function: embed_text_batch() is used during ingestion; embed_text() is used during query time.

📍 Offline Note: Runs entirely on your local machine via Ollama's local embedding model — _no API calls or internet required_.

**`retriever.py`**
🔹 Purpose: Stores and retrieves document chunks based on similarity to user queries.

- Initializes a persistent ChromaDB collection in a local folder (e.g., chroma_db/), which stores both documents and embeddings.
- Provides retrieval (search_similar_chunks) and reranking (rerank_results) based on cosine similarity with sentence_transformers.util.cos_sim
- Critical Function: add_chunks() saves documents and their embeddings; search_similar_chunks() is the heart of offline semantic search.

📍 Offline Note: ChromaDB operates locally and persistently without a server — all retrieval is vector-based and offline.

**`ollama_runner.py`**
🔹 Purpose: Sends the retrieved document and user question to a local LLM to generate a natural language response.

- Uses subprocess to call ollama run with a specified model like openthinker:7b or llama3, passing the prompt directly.
- Formats the context and question into a single prompt before sending it to the model.
- Critical Function: query_llm(question, context) — this is what generates your final answer.

📍 Offline Note: The LLM runs 100% locally via the Ollama runtime — _no internet, no API tokens_.

**`chat_loop.py`**
🔹 Purpose: Handles the interactive user interface in the terminal.

- Prompts the user for questions, embeds the query, retrieves relevant documents, and reranks them for relevance.
- Displays the source document info, a relevant excerpt, and a generated LLM response.
- Critical Flow: chat_loop() is the main interactive REPL loop — calling all components in sequence: embed_text, search_similar_chunks, rerank_results, query_llm.

📍 Offline Note: Runs in the terminal with no need for web UI or servers — user asks, local stack answers

**`rag_pipeline.py`**
🔹 Purpose: Orchestrates the full pipeline: ingestion + REPL loop.

- Runs process_new_pdfs() to ingest any new PDFs and embed them before launching the chat loop.
- Acts as your single-file entry point (python rag_pipeline.py) for both setup and use.
- Critical Sequence: ingestion -> chat → the full RAG cycle.

📍 Offline Note: No services are called — it checks folders, updates the vector store, and launches the chat — all from your machine.


#### Summary of Offline RAG Workflow
- What makes it "offline"?
    - Embedding is handled by nomic-embed-text via Ollama (local model).
    - Document storage & search are powered by local persistent ChromaDB (vector DB).
    - Answer generation is done by a locally run LLM like llama3.1, using no external API.

**You've created a fully self-contained question-answering system that doesn't require internet.** It can be
updated to support multiple PDFs over time. For adding effective parsiing of other structured and unstructed
data lik images and tables, I reccomend using a different parsing (`llamaparse`). They currently offer a free tier, 
but for unrestricted use of LlamaParse, it does require a credit card: https://www.llamaindex.ai/llamaparse

## 🚀 Run It

```bash
python rag_pipeline.py
```

Place any PDFs in the `docs/` directory. They'll be automatically processed and embedded.
This RAG is updatable and supports multiple PDF's. 
- You can drop as many PDFs as you want into the docs/ folder.
- The `pdf_manager.py` script will only process the new ones by using `ingested.json` to remember what's been done already.
- This ensure efficient use of embedding resources on your machine and only embedding new PDF's.

## ❓ Ask Questions

Ask a question in the terminal. Type `exit` or `bye` to quit.

---

This project is designed for use in Ubuntu, but works equally on macOS and Windows.
