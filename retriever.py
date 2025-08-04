#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# retriever.py

import chromadb
from chromadb.config import Settings
from sentence_transformers.util import cos_sim
import numpy as np

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="chroma_db")
collection_name = "rag_chunks"
collection = client.get_or_create_collection(
    name=collection_name,
    metadata={"hnsw:space": "cosine"}
)

# Check embedding dimension for debugging
def check_embedding_dimension():
    try:
        peek = collection.peek()
        embs = peek.get("embeddings")
        if embs is not None and isinstance(embs, list) and len(embs) > 0:
            dim = len(peek["embeddings"][0])
            if dim == 768:
                print("Collection expects embedding dimension: 768\n")
            elif dim == 384:
                print("⚠️ Collection expects embedding dimension: 384\n")
            else:
                print(f"⚠️ Unexpected embedding dimension: {dim}\n")
        else:
            print("⚠️ No embeddings found in collection.\n")
    except Exception as e:
        print(f"Error checking embedding dimension: {e}")

check_embedding_dimension()

# Add new chunks to the collection
def add_chunks(chunks, embeddings):
    ids = []
    for i, chunk in enumerate(chunks):
        id = f"{chunk['metadata']['file']}_{chunk['metadata']['page']}_{chunk['metadata']['chunk_index']}"
        ids.append(id)
    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
        ids=ids,
        embeddings=embeddings,
    )
    return ids

# Retrieve relevant chunks from Chroma
def search_similar_chunks(query_embedding, top_k=5):
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "embeddings", "metadatas"],
    )

        if results.get("embeddings") is None:
            print("⚠️ Query returned no embeddings. Reranking will fail.")
            return None

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
        print(f"❌ Retrieval error: {e}")
        return None

# Re-rank retrieved chunks based on cosine similarity
def rerank_results(query_embedding, docs, embs, metas, threshold=0.2):
    scores = cos_sim(np.array(query_embedding), np.array(embs))[0]
    ranked = sorted(
        zip(docs, metas, scores), key=lambda x: x[2], reverse=True
    )
    results = []
    for doc, meta, score in ranked:
        warn = score < threshold
        results.append((doc, meta, score, warn))
    return results
