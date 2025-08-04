#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Main entrypoint that ties all components together
# rag_pipeline.py

from pdf_manager import process_new_pdfs
from embedder import embed_text
from retriever import add_chunks
from chat_loop import chat_loop
from termcolor import colored

def main():
    print(colored("\n📥 Checking for new PDFs to ingest since last time...\n", "cyan"))
    process_new_pdfs(embed_func=embed_text, add_func=add_chunks)

    print(colored("\n✅ All available documents have been embedded and stored.\n", "green"))
    print(colored("Launching your RAG assistant...\n", "cyan"))
    chat_loop()

if __name__ == "__main__":
    main()
