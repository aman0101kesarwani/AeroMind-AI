from services.retrieval_service import retrieve_chunks


question = "What are the procedures for glow plug inspection and testing?"

results = retrieve_chunks(
    question,
    top_k=5
)


print("\n# SEARCH RESULTS")
print("=" * 60)

for i, chunk in enumerate(results):

    print(f"\nResult {i + 1}")

    print("Source:", chunk["source"])
    print("Page:", chunk["page"])
    print("Distance:", chunk["distance"])

    print("Text:")
    print(chunk["text"][:500])











