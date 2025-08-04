#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Formats prompt and sends it to `openthinker:7b` using Ollama
# ollama_runner.py

import subprocess
import json
from termcolor import colored

def query_llm(prompt, context):
    """
    Uses Ollama to run the LLM and return a response.

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
        print(colored("❌ Error running Ollama subprocess:", "red"))
        print(colored(e.stderr, "red"))
        return "⚠️ Unable to get a response from the local model."
