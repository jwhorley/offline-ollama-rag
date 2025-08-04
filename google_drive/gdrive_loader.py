#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Document Loader
Handles loading and processing different document types from Google Drive.
"""

import io
import os
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import docx
import pandas as pd
from pdf_loader import load_pdf_chunks

def load_drive_document(service, file_id, file_type, file_name):
    """
    Downloads and processes a document from Google Drive.
    
    Args:
        service: Authenticated Google Drive service
        file_id: Google Drive file ID
        file_type: Type of document ('docs', 'sheets', 'pdf')
        file_name: Name of the file for metadata
    
    Returns:
        List of text chunks with metadata
    """
    try:
        if file_type == 'docs':
            return _load_google_doc(service, file_id, file_name)
        elif file_type == 'sheets':
            return _load_google_sheet(service, file_id, file_name)
        elif file_type == 'pdf':
            return _load_pdf_from_drive(service, file_id, file_name)
        else:
            print(f"⚠️ Unsupported file type: {file_type}")
            return []
    except HttpError as error:
        print(f"❌ Error loading document {file_name}: {error}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error loading {file_name}: {e}")
        return []

def _load_google_doc(service, file_id, file_name):
    """Load and chunk a Google Doc."""
    try:
        # Export as plain text
        request = service.files().export_media(
            fileId=file_id,
            mimeType='text/plain'
        )
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Get text content
        text_content = file_content.getvalue().decode('utf-8')
        
        # Chunk the text
        return _chunk_text(text_content, file_name, file_id, 'Google Doc')
        
    except Exception as e:
        print(f"❌ Error processing Google Doc {file_name}: {e}")
        return []

def _load_google_sheet(service, file_id, file_name):
    """Load and process a Google Sheet."""
    try:
        # Export as CSV
        request = service.files().export_media(
            fileId=file_id,
            mimeType='text/csv'
        )
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Process CSV content
        csv_content = file_content.getvalue().decode('utf-8')
        
        # Convert to structured text
        structured_text = _process_csv_content(csv_content)
        
        # Chunk the processed text
        return _chunk_text(structured_text, file_name, file_id, 'Google Sheet')
        
    except Exception as e:
        print(f"❌ Error processing Google Sheet {file_name}: {e}")
        return []

def _load_pdf_from_drive(service, file_id, file_name):
    """Download and process a PDF from Google Drive."""
    try:
        # Download PDF file
        request = service.files().get_media(fileId=file_id)
        
        file_content = io.BytesIO()
        downloader = MediaIoBaseDownload(file_content, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Save temporarily and process with existing PDF loader
        temp_path = f"/tmp/{file_name}"
        with open(temp_path, 'wb') as f:
            f.write(file_content.getvalue())
        
        # Use existing PDF processing
        chunks = load_pdf_chunks(temp_path)
        
        # Update metadata to include Drive info
        for chunk in chunks:
            chunk['metadata']['drive_id'] = file_id
            chunk['metadata']['source_type'] = 'Google Drive PDF'
        
        # Clean up temp file
        os.remove(temp_path)
        
        return chunks
        
    except Exception as e:
        print(f"❌ Error processing PDF {file_name}: {e}")
        return []

def _process_csv_content(csv_content):
    """Convert CSV content to structured text."""
    try:
        # Parse CSV
        lines = csv_content.strip().split('\n')
        if not lines:
            return ""
        
        # Create structured representation
        structured_parts = []
        
        # Add header information
        if lines:
            headers = lines[0].split(',')
            structured_parts.append(f"Spreadsheet with columns: {', '.join(headers)}")
        
        # Process rows
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                cells = line.split(',')
                row_text = f"Row {i}: " + " | ".join([
                    f"{headers[j] if j < len(headers) else f'Col{j}'}: {cell.strip()}"
                    for j, cell in enumerate(cells) if cell.strip()
                ])
                structured_parts.append(row_text)
        
        return "\n".join(structured_parts)
        
    except Exception as e:
        print(f"⚠️ Error processing CSV content: {e}")
        return csv_content  # Return raw content as fallback

def _chunk_text(text, file_name, file_id, source_type, chunk_size=200, overlap=50):
    """
    Chunk text content with Google Drive metadata.
    
    Args:
        text: Text content to chunk
        file_name: Name of the source file
        file_id: Google Drive file ID
        source_type: Type of source document
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words
    
    Returns:
        List of chunks with metadata
    """
    if not text.strip():
        return []
    
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk_words = words[i:i + chunk_size]
        if not chunk_words:
            continue
            
        chunk_text = ' '.join(chunk_words)
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "file": file_name,
                "drive_id": file_id,
                "source_type": source_type,
                "chunk_index": i,
                "word_count": len(chunk_words)
            }
        })
    
    return chunks

def get_file_type(mime_type):
    """
    Determine file type from MIME type.
    
    Args:
        mime_type: Google Drive MIME type
    
    Returns:
        str: Simplified file type ('docs', 'sheets', 'pdf', or 'unknown')
    """
    mime_type_map = {
        'application/vnd.google-apps.document': 'docs',
        'application/vnd.google-apps.spreadsheet': 'sheets',
        'application/pdf': 'pdf',
        'text/plain': 'text',
    }
    
    return mime_type_map.get(mime_type, 'unknown')

if __name__ == "__main__":
    # Test the loader functions
    from gdrive_auth import authenticate_google_drive
    
    service = authenticate_google_drive()
    if service:
        print("✅ Ready to test document loading")
        # Add test file IDs here for testing
    else:
        print("❌ Authentication failed")
