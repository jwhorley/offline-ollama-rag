from retriever import collection
print(f"Collection has {collection.count()} documents.")

# Try to inspect shape of one stored embedding
sample = collection.peek()
sample_vec = sample["embeddings"][0]
print(f"Sample embedding dimension in DB: {len(sample_vec)}")

# Check embedding model output
from embedder import embed_text
test_vec = embed_text("This is a test.")
print(f"Embedder output dimension: {len(test_vec)}")
