#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# chat_loop.py

from retriever import search_similar_chunks, rerank_results
from embedder import embed_text
from ollama_runner import query_llm
from termcolor import colored
from tqdm import tqdm
import time

def simulate_loading(message="🤖 Generating response from LLM...", seconds=5):
    print(colored(message, "green"))
    for _ in tqdm(range(seconds), desc="Processing", ncols=75):
        time.sleep(1)
    print()

def chat_loop():
    print(colored("📚 Ollama Offline RAG Assistant", "green"))
    print(colored("Type your question below. Type 'exit' to quit.\n", "cyan"))

    while True:
        try:
            query = input("> ").strip()
            if query.lower() in ("exit", "quit", "bye"):
                print(colored("👋 Goodbye! Exiting RAG assistant.\n", "cyan"))
                break

            query_embedding = embed_text(query)
            result = search_similar_chunks(query_embedding)

            if result is None:
                print(colored("🫥 No relevant documents found. Try rephrasing your question.\n", "yellow"))
                continue

            docs, embs, metas = result

            if not docs:
                print(colored("🫥 No relevant documents found. Try rephrasing your question.\n", "yellow"))
                continue

            top_results = rerank_results(query_embedding, docs, embs, metas)

            if not top_results:
                print(colored("🫥 No relevant documents found. Try rephrasing your question.\n", "yellow"))
                continue

            doc, meta, score, warn = top_results[0]

            if warn:
                print(colored("⚠️ Warning: The retrieved document may not be a strong match.\n", "red"))

            print(colored(f"📄 Based on page {meta['page']} of {meta['file']}\n", "cyan"))
            print(doc.strip())
            print()

            simulate_loading()

            response = query_llm(query, doc)
            print(colored(response.strip(), "white"))
            print()

        except KeyboardInterrupt:
            print(colored("\n👋 Interrupted. Exiting RAG assistant.\n", "cyan"))
            break
        except Exception as e:
            print(colored(f"❌ An error occurred: {e}\n", "red"))
