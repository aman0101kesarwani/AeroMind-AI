from embeddings.embedding_model import generate_embeddings
from vectorstore.chroma_store import search_chunks
from services.gemini_service import generate_rag_answer


question = "What is the engine maintenance procedure?"


# 1. Convert question to embedding
query_embedding = generate_embeddings([question])[0]


# 2. Search ChromaDB
results = search_chunks(
    query_embedding,
    top_k=3
)


# 3. Convert Chroma results into our format
retrieved_chunks = []

for i in range(len(results["documents"][0])):

    retrieved_chunks.append({
        "text": results["documents"][0][i],
        "source": results["metadatas"][0][i]["source"],
        "page": results["metadatas"][0][i]["page"]
    })


# 4. Send retrieved context to Gemini
answer = generate_rag_answer(
    question,
    retrieved_chunks
)


print("\nQUESTION")
print("=" * 60)
print(question)

print("\nANSWER")
print("=" * 60)
print(answer)

print("\nSOURCES")
print("=" * 60)

for chunk in retrieved_chunks:

    print(
        f"{chunk['source']} "
        f"(Page {chunk['page']})"
    )


