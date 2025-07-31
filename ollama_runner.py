#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Formats prompt and sends it to `llama3.1:latest` using Ollama
# ollama_runner.py

import subprocess
import json
from termcolor import colored

def query_llm(prompt, context):
    """
    Generates a response using Ollama's llama3.1:latest model.
    
    Prerequisites:
    - Ollama must be installed and running
    - The 'llama3.1:latest' model must be downloaded

    Args:
        prompt (str): User question.
        context (str): Relevant chunk of text from document.

    Returns:
        str: LLM-generated response.
    """
    full_prompt = f"""Answer the following question using the context below:

    Question: {prompt}

    Context: {context}

    Your answer:"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.1:latest"],
            input=full_prompt,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(colored("❌ Error running Ollama:", "red"))
        print(colored("   Make sure Ollama is installed and the model is available:", "yellow"))
        print(colored("   ollama pull llama3.1:latest", "yellow"))
        if e.stderr:
            print(colored(f"   Error details: {e.stderr}", "red"))
        return "⚠️ Unable to get a response from the local model. Check Ollama installation and model availability."
