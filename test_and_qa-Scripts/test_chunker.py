from retriever import collection
print("Total docs stored:", collection.count())

peek = collection.peek()
print("Sample doc:", peek["documents"][0])
print("Sample embedding length:", len(peek["embeddings"][0]))
