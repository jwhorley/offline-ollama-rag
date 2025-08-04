#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Document Manager
Handles discovery, tracking, and processing of Google Drive documents.
"""

import os
import json
from datetime import datetime
from gdrive_auth import authenticate_google_drive
from gdrive_loader import load_drive_document, get_file_type
from termcolor import colored

GDRIVE_TRACK_FILE = "google_drive/ingested_gdrive.json"
SUPPORTED_MIME_TYPES = [
    'application/vnd.google-apps.document',  # Google Docs
    'application/vnd.google-apps.spreadsheet',  # Google Sheets
    'application/pdf'  # PDFs
]

def load_gdrive_ingestion_index():
    """
    Load the ingested Google Drive documents index.
    Returns an empty dict if it doesn't exist yet.
    """
    if not os.path.exists(GDRIVE_TRACK_FILE):
        return {}
    
    try:
        with open(GDRIVE_TRACK_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def update_gdrive_ingestion_index(index):
    """
    Save the updated Google Drive ingestion index to disk.
    """
    os.makedirs(os.path.dirname(GDRIVE_TRACK_FILE), exist_ok=True)
    with open(GDRIVE_TRACK_FILE, "w") as f:
        json.dump(index, f, indent=2)

def scan_drive_documents(service, folder_id=None, max_results=100):
    """
    Scans Google Drive for supported documents.
    
    Args:
        service: Authenticated Google Drive service
        folder_id: Optional folder to scan (None for all accessible docs)
        max_results: Maximum number of documents to return
    
    Returns:
        List of document metadata dictionaries
    """
    try:
        # Build query for supported file types
        mime_query = " or ".join([f"mimeType='{mime}'" for mime in SUPPORTED_MIME_TYPES])
        query = f"({mime_query}) and trashed=false"
        
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        # Execute search
        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink, size)"
        ).execute()
        
        documents = results.get('files', [])
        
        print(f"📁 Found {len(documents)} supported documents in Google Drive")
        
        return documents
        
    except Exception as e:
        print(f"❌ Error scanning Google Drive: {e}")
        return []

def get_new_gdrive_docs_to_process(service):
    """
    Returns a list of Google Drive documents that have not yet been processed
    or have been modified since last processing.
    """
    ingested = load_gdrive_ingestion_index()
    all_docs = scan_drive_documents(service)
    
    new_docs = []
    
    for doc in all_docs:
        doc_id = doc['id']
        modified_time = doc['modifiedTime']
        
        # Check if document is new or modified
        if doc_id not in ingested:
            new_docs.append(doc)
        elif ingested[doc_id].get('modified_time') != modified_time:
            print(f"📄 Document updated: {doc['name']}")
            new_docs.append(doc)
    
    return new_docs

def process_new_gdrive_docs(embed_func, add_func):
    """
    Main processing function for Google Drive documents.
    Similar to process_new_pdfs but for Google Drive.
    
    Args:
        embed_func (callable): Function that takes text and returns embedding
        add_func (callable): Function that takes (chunks, embeddings) and stores them
    """
    print(colored("🔗 Authenticating with Google Drive...", "cyan"))
    
    service = authenticate_google_drive()
    if not service:
        print(colored("❌ Failed to authenticate with Google Drive", "red"))
        return
    
    print(colored("✅ Google Drive authentication successful", "green"))
    
    # Load tracking index
    index = load_gdrive_ingestion_index()
    new_docs = get_new_gdrive_docs_to_process(service)
    
    if not new_docs:
        print(colored("📁 No new or updated Google Drive documents found.", "yellow"))
        return
    
    print(colored(f"📄 Processing {len(new_docs)} documents from Google Drive...", "cyan"))
    
    for doc in new_docs:
        doc_id = doc['id']
        doc_name = doc['name']
        mime_type = doc['mimeType']
        modified_time = doc['modifiedTime']
        
        print(f"📄 Processing: {doc_name}")
        
        # Determine file type
        file_type = get_file_type(mime_type)
        
        if file_type == 'unknown':
            print(f"⚠️ Unsupported file type for {doc_name}: {mime_type}")
            continue
        
        try:
            # Load and chunk the document
            chunks = load_drive_document(service, doc_id, file_type, doc_name)
            
            if not chunks:
                print(f"⚠️ No content extracted from {doc_name}")
                continue
            
            # Generate embeddings
            print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
            embeddings = []
            for chunk in chunks:
                embedding = embed_func(chunk["text"])
                if embedding:
                    embeddings.append(embedding)
                else:
                    print(f"⚠️ Failed to generate embedding for chunk in {doc_name}")
            
            if len(embeddings) != len(chunks):
                print(f"⚠️ Embedding count mismatch for {doc_name}")
                continue
            
            # Store chunks and embeddings
            chunk_ids = add_func(chunks, embeddings)
            
            # Update tracking index
            index[doc_id] = {
                'name': doc_name,
                'modified_time': modified_time,
                'processed_time': datetime.now().isoformat(),
                'chunk_count': len(chunks),
                'chunk_ids': chunk_ids,
                'file_type': file_type,
                'mime_type': mime_type
            }
            
            print(colored(f"✅ Added {len(chunks)} chunks from {doc_name}", "green"))
            
        except Exception as e:
            print(colored(f"❌ Error processing {doc_name}: {e}", "red"))
            continue
    
    # Save updated index
    update_gdrive_ingestion_index(index)
    print(colored(f"💾 Updated Google Drive ingestion index", "green"))

def list_processed_documents():
    """
    Display a summary of all processed Google Drive documents.
    """
    index = load_gdrive_ingestion_index()
    
    if not index:
        print("📁 No Google Drive documents have been processed yet.")
        return
    
    print(f"\n📚 Processed Google Drive Documents ({len(index)} total):")
    print("-" * 80)
    
    for doc_id, info in index.items():
        print(f"📄 {info['name']}")
        print(f"   Type: {info['file_type']} | Chunks: {info['chunk_count']}")
        print(f"   Processed: {info['processed_time']}")
        print(f"   Modified: {info['modified_time']}")
        print()

if __name__ == "__main__":
    # Test the manager functions
    service = authenticate_google_drive()
    if service:
        docs = scan_drive_documents(service)
        print(f"Found {len(docs)} documents")
        for doc in docs[:5]:  # Show first 5
            print(f"- {doc['name']} ({get_file_type(doc['mimeType'])})")
    else:
        print("❌ Authentication failed")
