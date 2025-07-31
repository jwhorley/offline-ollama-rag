from embedder import embed_text
from retriever import collection

query = "Who wrote Hamlet?"
query_embedding = embed_text(query)
print("Query embedding length:", len(query_embedding))

results = collection.query(query_embeddings=[query_embedding], n_results=5)
print("Raw results:", results)
