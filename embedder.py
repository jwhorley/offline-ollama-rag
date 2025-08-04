#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Sends text to Ollama to get embeddings using `nomic-embed-text`

import requests

def embed_text(text: str) -> list:
    """
    Embeds text using the 'nomic-embed-text' model via Ollama's HTTP API.
    Requires Ollama to be running locally.

    Args:
        text (str): Text to embed

    Returns:
        List[float]: Embedding vector
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
        print("❌ Error communicating with Ollama embedding server.")
        print(e)
        return []

    except KeyError:
        print("❌ Unexpected response format from embedding server.")
        return []
