from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer


question = "What are the procedures for glow plug inspection and testing?"


# Retrieve relevant chunks
retrieved_chunks = retrieve_chunks(
    question,
    top_k=5
)


# Generate grounded answer
answer = generate_rag_answer(
    question,
    retrieved_chunks
)


print("\n# QUESTION")
print("=" * 60)
print(question)


print("\n# ANSWER")
print("=" * 60)
print(answer)


print("\n# SOURCES")
print("=" * 60)

for chunk in retrieved_chunks:

    print(
        f"{chunk['source']} "
        f"(Page {chunk['page']})"
    )