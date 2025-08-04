#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Detects new PDFs in docs/, skips already processed ones

import os
import json
from pdf_loader import load_pdf_chunks

TRACK_FILE = "ingested.json"
PDF_FOLDER = "docs"

def load_ingestion_index():
    """
    Load the ingested.json file which tracks already-processed PDFs.
    Returns an empty dict if it doesn't exist yet.
    """
    if not os.path.exists(TRACK_FILE):
        return {}
    with open(TRACK_FILE, "r") as f:
        return json.load(f)

def update_ingestion_index(index):
    """
    Save the updated ingestion index to disk.
    """
    with open(TRACK_FILE, "w") as f:
        json.dump(index, f, indent=2)

def get_all_pdf_paths():
    """
    Scans the /docs folder and returns a list of full paths to PDF files.
    Ignores any non-PDF files.
    """
    if not os.path.exists(PDF_FOLDER):
        os.makedirs(PDF_FOLDER)
    return [
        os.path.join(PDF_FOLDER, f)
        for f in os.listdir(PDF_FOLDER)
        if f.lower().endswith(".pdf")
    ]

def get_new_pdfs_to_process():
    """
    Returns a list of PDFs that have not yet been processed.
    """
    ingested = load_ingestion_index()
    all_pdfs = get_all_pdf_paths()
    new_pdfs = [path for path in all_pdfs if path not in ingested]
    return new_pdfs

def process_new_pdfs(embed_func, add_func):
    """
    Loads, embeds, and stores chunks from newly added PDFs.
    Updates ingested.json to track them.
    
    Args:
        embed_func (callable): A function that takes a string and returns an embedding.
        add_func (callable): A function that takes (chunks, embeddings) and stores them.
    """
    index = load_ingestion_index()
    new_pdfs = get_new_pdfs_to_process()

    if not new_pdfs:
        print("📁 No new PDFs found. You're up to date!")
        return

    for pdf_path in new_pdfs:
        print(f"📄 Processing: {pdf_path}")
        chunks = load_pdf_chunks(pdf_path)
        if not chunks:
            print(f"⚠️  No text found in {pdf_path}. Skipping.")
            continue
        embeddings = [embed_func(chunk["text"]) for chunk in chunks]
        ids = add_func(chunks, embeddings)
        index[pdf_path] = ids
        print(f"✅ Added {len(chunks)} chunks from {pdf_path}")

    update_ingestion_index(index)
