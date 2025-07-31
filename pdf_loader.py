#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz  # PyMuPDF

def load_pdf_chunks(path, chunk_size=200, overlap=50):
    """
    Loads and chunks a PDF into overlapping text chunks.

    Args:
        path (str): File path to the PDF.
        chunk_size (int): Number of words per chunk.
        overlap (int): Number of overlapping words between chunks.

    Returns:
        List[Dict]: Each dict contains 'text' and 'metadata' keys.
    """
    doc = fitz.open(path)
    chunks = []

    for page_num, page in enumerate(doc):
        words = page.get_text().split()
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            if not chunk_words:
                continue
            chunk_text = ' '.join(chunk_words)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "page": page_num + 1,
                    "file": path,
                    "chunk_index": i
                }
            })

    return chunks
