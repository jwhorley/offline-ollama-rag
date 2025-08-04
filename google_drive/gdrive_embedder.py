#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Enhanced Embedder
Extends the base embedding functionality with Google Drive context.
"""

import requests
from embedder import embed_text

def embed_text_gdrive(text, metadata=None):
    """
    Embeds text with additional Google Drive context.
    
    Args:
        text (str): Text content to embed
        metadata (dict): Optional metadata with Drive document info
    
    Returns:
        List[float]: Embedding vector
    """
    # Enhance text with context if metadata is available
    enhanced_text = text
    
    if metadata:
        context_parts = []
        
        # Add document type context
        if 'source_type' in metadata:
            context_parts.append(f"Document type: {metadata['source_type']}")
        
        # Add file name context
        if 'file' in metadata:
            context_parts.append(f"From document: {metadata['file']}")
        
        # Create enhanced text with context
        if context_parts:
            context_prefix = " | ".join(context_parts) + " | Content: "
            enhanced_text = context_prefix + text
    
    # Use the base embedding function
    return embed_text(enhanced_text)

def embed_text_batch_gdrive(texts_and_metadata):
    """
    Batch embedding for Google Drive documents with context.
    
    Args:
        texts_and_metadata: List of (text, metadata) tuples
    
    Returns:
        List of embedding vectors
    """
    embeddings = []
    
    for text, metadata in texts_and_metadata:
        embedding = embed_text_gdrive(text, metadata)
        embeddings.append(embedding)
    
    return embeddings

def create_contextual_prompt(text, metadata):
    """
    Creates a contextually enhanced prompt for embedding.
    
    Args:
        text (str): Original text content
        metadata (dict): Document metadata
    
    Returns:
        str: Enhanced text with context
    """
    if not metadata:
        return text
    
    context_elements = []
    
    # Document source information
    if metadata.get('source_type'):
        context_elements.append(f"Source: {metadata['source_type']}")
    
    # Document title/name
    if metadata.get('file'):
        context_elements.append(f"Document: {metadata['file']}")
    
    # Document section (for sheets/structured docs)
    if metadata.get('chunk_index') is not None:
        context_elements.append(f"Section: {metadata['chunk_index']}")
    
    # Combine context with content
    if context_elements:
        context_header = "[" + " | ".join(context_elements) + "]"
        return f"{context_header}\n\n{text}"
    
    return text

def get_embedding_with_retry(text, max_retries=3):
    """
    Get embedding with retry logic for reliability.
    
    Args:
        text (str): Text to embed
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        List[float]: Embedding vector or empty list on failure
    """
    for attempt in range(max_retries):
        try:
            embedding = embed_text(text)
            if embedding:  # Check if embedding is not empty
                return embedding
        except Exception as e:
            print(f"⚠️ Embedding attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                print(f"❌ Failed to generate embedding after {max_retries} attempts")
    
    return []

# Enhanced embedding function with all features
def embed_gdrive_chunk(chunk_data):
    """
    Complete embedding function for Google Drive chunks.
    
    Args:
        chunk_data (dict): Chunk with 'text' and 'metadata' keys
    
    Returns:
        List[float]: Embedding vector
    """
    text = chunk_data.get('text', '')
    metadata = chunk_data.get('metadata', {})
    
    # Create contextual prompt
    enhanced_text = create_contextual_prompt(text, metadata)
    
    # Get embedding with retry
    embedding = get_embedding_with_retry(enhanced_text)
    
    return embedding

if __name__ == "__main__":
    # Test the enhanced embedding
    test_text = "This is a test document about machine learning."
    test_metadata = {
        'file': 'ML Research Notes',
        'source_type': 'Google Doc',
        'chunk_index': 0
    }
    
    # Test basic embedding
    basic_embedding = embed_text(test_text)
    print(f"Basic embedding length: {len(basic_embedding)}")
    
    # Test enhanced embedding
    enhanced_embedding = embed_text_gdrive(test_text, test_metadata)
    print(f"Enhanced embedding length: {len(enhanced_embedding)}")
    
    # Test contextual prompt creation
    contextual_text = create_contextual_prompt(test_text, test_metadata)
    print(f"Contextual prompt: {contextual_text[:100]}...")
