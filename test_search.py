from embeddings.embedding_model import generate_embeddings
from vectorstore.chroma_store import search_chunks


# query = "What is the engine maintenance procedure?"
# query = "What inspection procedures are described?"
# query = "What are the safety requirements?"
query = "What maintenance schedule is recommended?"

query_embedding = generate_embeddings([query])[0]

results = search_chunks(query_embedding, top_k=3)

print("\nSEARCH RESULTS")
print("=" * 60)

for i in range(3):

    print(f"\nResult {i + 1}")

    print("Source:", results["metadatas"][0][i]["source"])

    print("Page:", results["metadatas"][0][i]["page"])

    print("Text:")
    print(results["documents"][0][i][:500])

    print("\nDistances:")
    print(results["distances"])