# test_query_vector.py

from embedder import embed_text
from retriever import collection

query = "Who wrote Hamlet?"
query_embedding = embed_text(query)

print(f"\nQuery embedding length: {len(query_embedding)}")
print(f"Query embedding sample (first 5): {query_embedding[:5]}")

# Try a direct Chroma query
try:
    results = collection.query(query_embeddings=[query_embedding], n_results=5)
    print("\n📊 Retrieved documents:")
    for i, doc in enumerate(results["documents"][0]):
        print(f"Result {i+1}: {doc[:100]}...")
except Exception as e:
    print(f"❌ Query failed: {e}")
