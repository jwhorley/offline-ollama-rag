#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Enhanced Retriever
Extends the base retrieval functionality with Google Drive specific features.
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers.util import cos_sim
import numpy as np
from datetime import datetime, timedelta

# Initialize ChromaDB client for Google Drive documents
client = chromadb.PersistentClient(path="chroma_db_gdrive")
collection_name = "gdrive_rag_chunks"
collection = client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

def add_chunks_gdrive(chunks, embeddings):
    """
    Add Google Drive document chunks to the vector store.
    
    Args:
        chunks: List of chunk dictionaries with text and metadata
        embeddings: List of embedding vectors
    
    Returns:
        List of chunk IDs
    """
    ids = []
    documents = []
    metadatas = []
    
    for i, chunk in enumerate(chunks):
        # Create unique ID for Google Drive documents
        drive_id = chunk['metadata'].get('drive_id', 'unknown')
        chunk_index = chunk['metadata'].get('chunk_index', i)
        chunk_id = f"gdrive_{drive_id}_{chunk_index}"
        
        ids.append(chunk_id)
        documents.append(chunk["text"])
        
        # Enhance metadata with additional fields
        enhanced_metadata = {
            **chunk["metadata"],
            "ingested_at": datetime.now().isoformat(),
            "collection_type": "google_drive"
        }
        metadatas.append(enhanced_metadata)
    
    # Add to ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings,
    )
    
    return ids

def search_drive_chunks(query_embedding, filters=None, top_k=5):
    """
    Search Google Drive chunks with optional filters.
    
    Args:
        query_embedding: Query vector
        filters (dict): Optional filters for document type, date range, etc.
        top_k (int): Number of results to return
    
    Returns:
        Tuple of (documents, embeddings, metadatas) or None
    """
    try:
        # Build ChromaDB where clause from filters
        where_clause = {"collection_type": "google_drive"}
        
        if filters:
            if 'source_type' in filters:
                where_clause['source_type'] = filters['source_type']
            
            if 'file_name' in filters:
                where_clause['file'] = {"$contains": filters['file_name']}
        
        # Execute search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "embeddings", "metadatas"],
        )
        
        if (
            not results
            or not results.get("documents")
            or not results["documents"][0]
        ):
            return None
        
        return (
            results["documents"][0],
            results["embeddings"][0],
            results["metadatas"][0],
        )
        
    except Exception as e:
        print(f"❌ Google Drive retrieval error: {e}")
        return None

def rerank_gdrive_results(query_embedding, docs, embs, metas, threshold=0.2):
    """
    Re-rank Google Drive results with enhanced scoring.
    
    Args:
        query_embedding: Original query vector
        docs: Retrieved documents
        embs: Retrieved embeddings
        metas: Retrieved metadata
        threshold: Minimum similarity threshold
    
    Returns:
        List of (doc, meta, score, warning) tuples, ranked by relevance
    """
    # Calculate base cosine similarity scores
    base_scores = cos_sim(np.array(query_embedding), np.array(embs))[0]
    
    enhanced_results = []
    
    for i, (doc, meta, base_score) in enumerate(zip(docs, metas, base_scores)):
        # Start with base similarity score
        final_score = float(base_score)
        
        # Boost recent documents
        if 'ingested_at' in meta:
            try:
                ingested_time = datetime.fromisoformat(meta['ingested_at'])
                days_old = (datetime.now() - ingested_time).days
                
                # Boost documents ingested in the last 7 days
                if days_old <= 7:
                    recency_boost = 0.1 * (7 - days_old) / 7
                    final_score += recency_boost
            except:
                pass  # Skip if date parsing fails
        
        # Boost based on document type preferences
        source_type = meta.get('source_type', '')
        if 'Google Doc' in source_type:
            final_score += 0.05  # Slight boost for text documents
        elif 'Google Sheet' in source_type:
            final_score += 0.03  # Smaller boost for spreadsheets
        
        # Check if score meets threshold
        warning = base_score < threshold
        
        enhanced_results.append((doc, meta, final_score, warning))
    
    # Sort by enhanced score
    enhanced_results.sort(key=lambda x: x[2], reverse=True)
    
    return enhanced_results

def get_document_stats():
    """
    Get statistics about stored Google Drive documents.
    
    Returns:
        Dict with document statistics
    """
    try:
        # Get all documents
        all_docs = collection.get(include=["metadatas"])
        
        if not all_docs or not all_docs.get("metadatas"):
            return {"total_chunks": 0, "documents": 0, "types": {}}
        
        metadatas = all_docs["metadatas"]
        
        # Count by document type
        type_counts = {}
        unique_docs = set()
        
        for meta in metadatas:
            source_type = meta.get('source_type', 'Unknown')
            type_counts[source_type] = type_counts.get(source_type, 0) + 1
            
            # Track unique documents
            if 'drive_id' in meta:
                unique_docs.add(meta['drive_id'])
        
        return {
            "total_chunks": len(metadatas),
            "unique_documents": len(unique_docs),
            "document_types": type_counts
        }
        
    except Exception as e:
        print(f"❌ Error getting document stats: {e}")
        return {"total_chunks": 0, "unique_documents": 0, "document_types": {}}

def search_by_document_name(document_name, query_embedding=None, top_k=10):
    """
    Search for chunks from a specific document.
    
    Args:
        document_name (str): Name of the document to search
        query_embedding: Optional query vector for semantic search within document
        top_k (int): Number of results to return
    
    Returns:
        List of matching chunks
    """
    try:
        where_clause = {
            "collection_type": "google_drive",
            "file": {"$contains": document_name}
        }
        
        if query_embedding is not None:
            # Semantic search within the document
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_clause,
                include=["documents", "embeddings", "metadatas"],
            )
        else:
            # Just get all chunks from the document
            results = collection.get(
                where=where_clause,
                limit=top_k,
                include=["documents", "metadatas"],
            )
        
        return results
        
    except Exception as e:
        print(f"❌ Error searching by document name: {e}")
        return None

if __name__ == "__main__":
    # Test the Google Drive retriever
    stats = get_document_stats()
    print(f"📊 Google Drive Document Stats:")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Unique documents: {stats['unique_documents']}")
    print(f"   Document types: {stats['document_types']}")
