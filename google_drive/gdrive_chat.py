#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google Drive Enhanced Chat Interface
Provides an improved chat experience for Google Drive RAG system.
"""

from gdrive_retriever import search_drive_chunks, rerank_gdrive_results, get_document_stats
from gdrive_embedder import embed_text_gdrive
from ollama_runner import query_llm
from termcolor import colored
from tqdm import tqdm
import time

def simulate_loading(message="🤖 Generating response from Google Drive documents...", seconds=3):
    """Simulate processing time with progress bar."""
    print(colored(message, "green"))
    for _ in tqdm(range(seconds), desc="Processing", ncols=75):
        time.sleep(1)
    print()

def format_drive_source(metadata):
    """
    Format Google Drive source information for display.
    
    Args:
        metadata (dict): Document metadata
    
    Returns:
        str: Formatted source information
    """
    source_parts = []
    
    # Document name
    if 'file' in metadata:
        source_parts.append(f"📄 {metadata['file']}")
    
    # Document type
    if 'source_type' in metadata:
        source_parts.append(f"({metadata['source_type']})")
    
    # Drive link if available
    if 'drive_id' in metadata:
        drive_link = f"https://drive.google.com/file/d/{metadata['drive_id']}/view"
        source_parts.append(f"🔗 {drive_link}")
    
    return " | ".join(source_parts)

def display_welcome_message():
    """Display welcome message with system stats."""
    print(colored("🔗 Google Drive RAG Assistant", "green"))
    print(colored("Connected to your Google Drive documents", "cyan"))
    
    # Show document statistics
    stats = get_document_stats()
    if stats['total_chunks'] > 0:
        print(colored(f"\n📊 Available: {stats['unique_documents']} documents, {stats['total_chunks']} searchable chunks", "yellow"))
        
        if stats['document_types']:
            type_summary = ", ".join([f"{count} {doc_type}" for doc_type, count in stats['document_types'].items()])
            print(colored(f"📁 Document types: {type_summary}", "yellow"))
    else:
        print(colored("\n⚠️ No Google Drive documents found. Make sure documents are processed first.", "yellow"))
    
    print(colored("\nType your question below. Type 'exit' to quit.\n", "cyan"))

def handle_special_commands(query):
    """
    Handle special commands like stats, help, etc.
    
    Args:
        query (str): User input
    
    Returns:
        bool: True if command was handled, False otherwise
    """
    query_lower = query.lower().strip()
    
    if query_lower in ['stats', 'status', 'info']:
        stats = get_document_stats()
        print(colored("\n📊 Google Drive Document Statistics:", "cyan"))
        print(f"   📄 Total documents: {stats['unique_documents']}")
        print(f"   📝 Total chunks: {stats['total_chunks']}")
        
        if stats['document_types']:
            print(f"   📁 Document types:")
            for doc_type, count in stats['document_types'].items():
                print(f"      • {doc_type}: {count} chunks")
        print()
        return True
    
    elif query_lower in ['help', '?']:
        print(colored("\n🔧 Available Commands:", "cyan"))
        print("   • Ask any question about your Google Drive documents")
        print("   • 'stats' - Show document statistics")
        print("   • 'help' - Show this help message")
        print("   • 'exit' - Quit the assistant")
        print()
        return True
    
    return False

def chat_loop_gdrive():
    """
    Main chat loop for Google Drive RAG system.
    Enhanced with Drive-specific features and better UX.
    """
    display_welcome_message()
    
    while True:
        try:
            query = input(colored("> ", "white")).strip()
            
            # Handle exit commands
            if query.lower() in ("exit", "quit", "bye"):
                print(colored("👋 Goodbye! Thanks for using Google Drive RAG Assistant.\n", "cyan"))
                break
            
            # Handle empty input
            if not query:
                continue
            
            # Handle special commands
            if handle_special_commands(query):
                continue
            
            # Process the query
            print(colored("🔍 Searching Google Drive documents...", "yellow"))
            
            # Generate query embedding
            query_embedding = embed_text_gdrive(query)
            if not query_embedding:
                print(colored("❌ Failed to process your question. Please try again.\n", "red"))
                continue
            
            # Search for relevant chunks
            result = search_drive_chunks(query_embedding)
            
            if result is None:
                print(colored("🫥 No relevant documents found in your Google Drive.", "yellow"))
                print(colored("Try rephrasing your question or check if documents are properly processed.\n", "yellow"))
                continue
            
            docs, embs, metas = result
            
            if not docs:
                print(colored("🫥 No relevant content found. Try a different question.\n", "yellow"))
                continue
            
            # Re-rank results with Google Drive specific scoring
            top_results = rerank_gdrive_results(query_embedding, docs, embs, metas)
            
            if not top_results:
                print(colored("🫥 No sufficiently relevant documents found.\n", "yellow"))
                continue
            
            # Get the best result
            doc, meta, score, warn = top_results[0]
            
            # Display warning for low-confidence results
            if warn:
                print(colored("⚠️ Warning: The found document may not be a strong match for your question.\n", "red"))
            
            # Display source information
            source_info = format_drive_source(meta)
            print(colored(f"\n📋 Source: {source_info}\n", "cyan"))
            
            # Display relevant excerpt
            print(colored("📄 Relevant excerpt:", "yellow"))
            print(doc.strip())
            print()
            
            # Generate LLM response
            simulate_loading()
            
            # Create enhanced prompt with Drive context
            enhanced_prompt = f"""Based on the Google Drive document "{meta.get('file', 'Unknown Document')}", please answer this question: {query}

Use the following context from the document:
{doc}

Please provide a helpful and accurate answer based on this information."""
            
            response = query_llm(enhanced_prompt, doc)
            
            # Display response
            print(colored("🤖 Answer:", "green"))
            print(colored(response.strip(), "white"))
            print()
            
            # Show additional relevant results if available
            if len(top_results) > 1:
                print(colored("📚 Other relevant sources found:", "yellow"))
                for i, (_, other_meta, other_score, _) in enumerate(top_results[1:3], 1):  # Show up to 2 more
                    other_source = format_drive_source(other_meta)
                    print(f"   {i+1}. {other_source} (relevance: {other_score:.2f})")
                print()
        
        except KeyboardInterrupt:
            print(colored("\n👋 Interrupted. Exiting Google Drive RAG assistant.\n", "cyan"))
            break
        except Exception as e:
            print(colored(f"❌ An error occurred: {e}\n", "red"))
            print(colored("Please try again or contact support if the issue persists.\n", "yellow"))

def quick_test_chat():
    """Quick test function for development."""
    print("🧪 Testing Google Drive chat interface...")
    
    # Test stats
    stats = get_document_stats()
    print(f"Found {stats['total_chunks']} chunks from {stats['unique_documents']} documents")
    
    if stats['total_chunks'] > 0:
        print("✅ Ready for chat testing")
    else:
        print("⚠️ No documents found - run document processing first")

if __name__ == "__main__":
    # Run quick test or full chat
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test_chat()
    else:
        chat_loop_gdrive()
