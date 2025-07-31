from embedder import embed_text
from retriever import collection

query = "Who were the Texas Rangers?"
embedding = embed_text(query)
results = collection.query(
    query_embeddings=[embedding],
    n_results=5,
    include=["documents", "embeddings", "metadatas"]
)

print("\n📊 Retrieved documents:")
for i, doc in enumerate(results["documents"][0]):
    print(f"Result {i+1}: {doc[:300]}...\n")
