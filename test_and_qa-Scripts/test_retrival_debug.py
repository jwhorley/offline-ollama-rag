# test_retrieval_debug.py

from embedder import embed_text
from retriever import collection
from sklearn.metrics.pairwise import cosine_similarity

def test_similarity(query: str, top_k=5):
    print(f"\n🔍 Testing similarity for query: '{query}'")

    # Step 1: Embed the user query
    query_embedding = embed_text(query)
    if not query_embedding:
        print("❌ No embedding returned for query.")
        return

    # Step 2: Pull all stored embeddings and metadata
    print("📥 Retrieving all stored embeddings from Chroma...")
    records = collection.get(include=["embeddings", "documents", "metadatas"])

    all_embeddings = records["embeddings"]
    all_documents = records["documents"]
    all_metadatas = records["metadatas"]

    if len(all_embeddings) == 0:
        print("⚠️  No embeddings found in ChromaDB.")
        return

    # Step 3: Compute cosine similarity scores
    print("📊 Calculating similarity scores...")
    scores = cosine_similarity([query_embedding], all_embeddings)[0]

    ranked = sorted(zip(scores, all_documents, all_metadatas), reverse=True)

    # Step 4: Print top results
    print(f"\n🏁 Top {top_k} most relevant chunks:\n")
    for i, (score, doc, meta) in enumerate(ranked[:top_k]):
        preview = doc.strip().replace("\n", " ")[:100]
        source = meta.get("file", "unknown")
        page = meta.get("page", "?")
        print(f"{i+1}. {score:.4f} | Page {page} | {source}")
        print(f"    {preview}...")
    print("\n✅ Done.\n")

if __name__ == "__main__":
    test_similarity("What is Article 1 of the Constitution?")
    test_similarity("How does the Constitution define the role of the President?")
