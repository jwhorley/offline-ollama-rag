#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive RAG Pipeline - Part 2 Implementation
This extends the offline RAG system to work with Google Drive documents.
"""

from google_drive.gdrive_manager import process_new_gdrive_docs
from google_drive.gdrive_embedder import embed_text_gdrive
from google_drive.gdrive_retriever import add_chunks_gdrive
from google_drive.gdrive_chat import chat_loop_gdrive
from termcolor import colored
import os

def main():
    print(colored("\n🔗 Google Drive RAG System Starting...\n", "cyan"))
    
    # Check for credentials
    if not os.path.exists("google_drive/credentials.json"):
        print(colored("❌ Missing credentials.json file!", "red"))
        print(colored("Please follow the setup instructions in google_drive/README.md", "yellow"))
        return
    
    print(colored("📥 Checking for new Google Drive documents...\n", "cyan"))
    
    try:
        # Process new documents from Google Drive
        process_new_gdrive_docs(
            embed_func=embed_text_gdrive, 
            add_func=add_chunks_gdrive
        )
        
        print(colored("\n✅ All Google Drive documents processed and embedded.\n", "green"))
        print(colored("🚀 Launching Google Drive RAG assistant...\n", "cyan"))
        
        # Start the chat interface
        chat_loop_gdrive()
        
    except Exception as e:
        print(colored(f"❌ Error: {e}", "red"))
        print(colored("Please check your Google Drive setup and credentials.", "yellow"))

if __name__ == "__main__":
    main()
