#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Sends text to Ollama to get embeddings using `nomic-embed-text`

import requests

def embed_text(text: str) -> list:
    """
    Embeds text using the 'nomic-embed-text' model via Ollama.
    
    Prerequisites:
    - Ollama must be installed and running locally
    - The 'nomic-embed-text' model must be downloaded

    Args:
        text (str): Text to embed

    Returns:
        List[float]: 768-dimensional embedding vector
    """
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": text
            }
        )
        response.raise_for_status()
        return response.json()["embedding"]

    except requests.RequestException as e:
        print("❌ Error communicating with Ollama. Is Ollama running?")
        print("   Try running: ollama serve")
        print(f"   Error details: {e}")
        return []

    except KeyError:
        print("❌ Unexpected response format from Ollama.")
        print("   Make sure 'nomic-embed-text' model is installed:")
        print("   ollama pull nomic-embed-text")
        return []
