# Google Drive RAG Integration - Part 2

This directory contains the implementation for extending the offline RAG system to work with Google Drive documents.

## 🎯 Learning Objectives

Students will learn to:
- Integrate Google Drive API with existing RAG systems
- Handle different document formats (Docs, Sheets, PDFs)
- Implement OAuth2 authentication flows
- Extend modular RAG architectures
- Handle API rate limiting and error recovery

## 🔧 Setup Instructions

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click "Enable"

### 2. Create Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Configure consent screen if prompted
4. Choose "Desktop application" as application type
5. Download the JSON file and save as `credentials.json` in this directory

### 3. Install Additional Dependencies

```bash
pip install -r requirements_gdrive.txt
```

## 📁 File Structure

```
google_drive/
├── README.md                    # This file
├── credentials.json             # Your Google API credentials (you create this)
├── token.json                   # Auto-generated after first auth
├── gdrive_auth.py              # Google Drive authentication
├── gdrive_loader.py            # Document loading and parsing
├── gdrive_manager.py           # Document management and tracking
├── gdrive_embedder.py          # Embedding with Google Drive context
├── gdrive_retriever.py         # Enhanced retrieval for Drive docs
├── gdrive_chat.py              # Chat interface for Drive RAG
└── implementation_guide.md     # Step-by-step implementation guide
```

## 🚀 Quick Start

1. Complete the setup steps above
2. Run the Google Drive RAG system:
   ```bash
   python rag_pipeline_gdrive.py
   ```
3. Follow the authentication prompts
4. Start asking questions about your Google Drive documents!

## 📚 Implementation Approach

This implementation follows the same modular pattern as the offline RAG system:

- **Authentication**: Secure OAuth2 flow with Google
- **Loading**: Support for Docs, Sheets, and PDFs from Drive
- **Chunking**: Smart chunking that preserves document structure
- **Embedding**: Context-aware embeddings with document metadata
- **Retrieval**: Enhanced search with Drive-specific metadata
- **Chat**: Improved interface showing Drive document sources

## 🔍 Supported Document Types

- **Google Docs**: Full text extraction with formatting preservation
- **Google Sheets**: Cell-by-cell processing with sheet context
- **PDFs**: Same processing as offline system
- **Future**: Slides, Forms, and other Google Workspace formats

## 🛡️ Security Notes

- Credentials are stored locally and never transmitted
- OAuth2 tokens are refreshed automatically
- All processing happens locally after document download
- No document content is sent to external services (except Google Drive API)

## 🎓 Learning Path

1. **Start with `implementation_guide.md`** - Step-by-step walkthrough
2. **Examine the modular architecture** - See how each component extends the base system
3. **Implement authentication first** - Get the OAuth2 flow working
4. **Add document loading** - Support different file types
5. **Enhance retrieval** - Add Drive-specific metadata and search
6. **Test and iterate** - Use your own Drive documents

## 🔧 Troubleshooting

### Common Issues:

**"Credentials not found"**
- Ensure `credentials.json` is in the `google_drive/` directory
- Verify the file was downloaded from Google Cloud Console

**"Access denied"**
- Check that Google Drive API is enabled in your project
- Verify OAuth2 consent screen is configured

**"Token expired"**
- Delete `token.json` and re-authenticate
- Check system clock is accurate

**"No documents found"**
- Verify your Google Drive has accessible documents
- Check sharing permissions on documents

## 📖 Additional Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api)
- [OAuth2 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Google Workspace Document Formats](https://developers.google.com/drive/api/guides/ref-export-formats)
