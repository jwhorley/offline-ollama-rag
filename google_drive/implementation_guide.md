# Google Drive RAG Implementation Guide

This guide walks you through implementing Google Drive integration for the RAG system step by step.

## 🎯 Overview

You'll extend the existing offline RAG system to:
1. Authenticate with Google Drive
2. Load documents from your Drive
3. Process different document types
4. Provide enhanced search with Drive metadata

## 📋 Prerequisites

- Completed offline RAG system (Part 1)
- Google account with Drive access
- Basic understanding of APIs and OAuth2

## 🚀 Step-by-Step Implementation

### Step 1: Authentication Setup

First, implement the Google Drive authentication:

```python
# gdrive_auth.py - Your implementation here
def authenticate_google_drive():
    """
    Handles OAuth2 flow for Google Drive access.
    Returns authenticated service object.
    """
    # TODO: Implement OAuth2 flow
    # - Load credentials from credentials.json
    # - Handle token refresh
    # - Return authenticated service
    pass
```

**Key concepts to implement:**
- OAuth2 flow with local redirect
- Token storage and refresh
- Error handling for authentication failures

### Step 2: Document Loading

Implement document loading for different file types:

```python
# gdrive_loader.py - Your implementation here
def load_drive_document(service, file_id, file_type):
    """
    Downloads and processes a document from Google Drive.
    
    Args:
        service: Authenticated Google Drive service
        file_id: Google Drive file ID
        file_type: Type of document (docs, sheets, pdf)
    
    Returns:
        List of text chunks with metadata
    """
    # TODO: Implement document loading
    # - Handle different export formats
    # - Extract text content
    # - Preserve document structure
    pass
```

**Document types to support:**
- Google Docs → Plain text export
- Google Sheets → CSV export with cell context
- PDFs → Direct download and existing PDF processing

### Step 3: Document Management

Create a system to track and manage Drive documents:

```python
# gdrive_manager.py - Your implementation here
def scan_drive_documents(service, folder_id=None):
    """
    Scans Google Drive for documents to process.
    
    Args:
        service: Authenticated Google Drive service
        folder_id: Optional folder to scan (None for all accessible docs)
    
    Returns:
        List of document metadata
    """
    # TODO: Implement document scanning
    # - Query Drive API for documents
    # - Filter by supported types
    # - Extract metadata (title, modified date, etc.)
    pass

def process_new_gdrive_docs(embed_func, add_func):
    """
    Main processing function - similar to process_new_pdfs
    but for Google Drive documents.
    """
    # TODO: Implement processing pipeline
    # - Authenticate with Drive
    # - Scan for new/updated documents
    # - Load and chunk documents
    # - Embed and store chunks
    pass
```

### Step 4: Enhanced Embedding

Extend the embedding system to include Drive-specific context:

```python
# gdrive_embedder.py - Your implementation here
def embed_text_gdrive(text, metadata=None):
    """
    Embeds text with additional Google Drive context.
    
    Args:
        text: Text content to embed
        metadata: Drive document metadata
    
    Returns:
        Embedding vector
    """
    # TODO: Enhance embedding with context
    # - Include document title in embedding context
    # - Add document type information
    # - Preserve sharing and permission context
    pass
```

### Step 5: Enhanced Retrieval

Improve retrieval with Drive-specific features:

```python
# gdrive_retriever.py - Your implementation here
def search_drive_chunks(query_embedding, filters=None):
    """
    Search with Google Drive specific filters and ranking.
    
    Args:
        query_embedding: Query vector
        filters: Optional filters (document type, date range, etc.)
    
    Returns:
        Ranked results with Drive metadata
    """
    # TODO: Implement enhanced search
    # - Add document type filtering
    # - Include recency scoring
    # - Show sharing information
    pass
```

### Step 6: Enhanced Chat Interface

Create an improved chat interface for Drive documents:

```python
# gdrive_chat.py - Your implementation here
def chat_loop_gdrive():
    """
    Chat interface optimized for Google Drive documents.
    Shows document links, sharing info, and enhanced context.
    """
    # TODO: Implement enhanced chat
    # - Show clickable Drive links
    # - Display document sharing status
    # - Provide document context in responses
    pass
```

## 🧪 Testing Your Implementation

### Test Cases to Implement:

1. **Authentication Test**
   ```python
   # Test OAuth2 flow
   service = authenticate_google_drive()
   assert service is not None
   ```

2. **Document Loading Test**
   ```python
   # Test different document types
   docs_content = load_drive_document(service, "doc_id", "docs")
   sheets_content = load_drive_document(service, "sheet_id", "sheets")
   pdf_content = load_drive_document(service, "pdf_id", "pdf")
   ```

3. **End-to-End Test**
   ```python
   # Test full pipeline
   process_new_gdrive_docs(embed_text_gdrive, add_chunks_gdrive)
   # Query and verify results
   ```

## 🎓 Learning Checkpoints

After each step, verify your understanding:

### Checkpoint 1: Authentication
- [ ] Can authenticate with Google Drive
- [ ] Tokens are stored and refreshed properly
- [ ] Error handling works for auth failures

### Checkpoint 2: Document Loading
- [ ] Can load Google Docs as text
- [ ] Can process Google Sheets with context
- [ ] Can handle PDFs from Drive
- [ ] Metadata is preserved correctly

### Checkpoint 3: Integration
- [ ] New documents are detected automatically
- [ ] Embeddings include Drive context
- [ ] Search results show Drive metadata
- [ ] Chat interface provides Drive links

## 🔧 Implementation Tips

### API Rate Limiting
```python
import time
from googleapiclient.errors import HttpError

def handle_rate_limit(func):
    """Decorator to handle API rate limiting"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            if e.resp.status == 429:  # Rate limited
                time.sleep(60)  # Wait and retry
                return func(*args, **kwargs)
            raise
    return wrapper
```

### Error Recovery
```python
def safe_document_load(service, file_id):
    """Safely load document with error recovery"""
    try:
        return load_drive_document(service, file_id, "docs")
    except Exception as e:
        print(f"Failed to load {file_id}: {e}")
        return None
```

### Metadata Enhancement
```python
def enrich_metadata(chunk_metadata, drive_metadata):
    """Add Drive-specific metadata to chunks"""
    return {
        **chunk_metadata,
        "drive_id": drive_metadata["id"],
        "drive_title": drive_metadata["name"],
        "drive_modified": drive_metadata["modifiedTime"],
        "drive_link": drive_metadata["webViewLink"]
    }
```

## 🎯 Success Criteria

Your implementation is complete when:

1. ✅ **Authentication works reliably**
2. ✅ **Multiple document types are supported**
3. ✅ **Documents are automatically discovered and processed**
4. ✅ **Search results include Drive context**
5. ✅ **Chat interface shows document sources with links**
6. ✅ **System handles errors gracefully**
7. ✅ **Performance is acceptable for typical Drive usage**

## 🚀 Next Steps

After completing the basic implementation:

1. **Add more document types** (Slides, Forms)
2. **Implement folder-based organization**
3. **Add collaborative features** (comments, suggestions)
4. **Create a web interface** instead of terminal-based
5. **Add real-time document monitoring** with webhooks

## 📚 Resources

- [Google Drive API Quickstart](https://developers.google.com/drive/api/quickstart/python)
- [OAuth2 for Desktop Applications](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Drive API File Export Formats](https://developers.google.com/drive/api/guides/ref-export-formats)
- [Handling API Errors](https://developers.google.com/drive/api/guides/handle-errors)
