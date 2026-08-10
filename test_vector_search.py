from embeddings.embedding_model import generate_embeddings
from services.supabase_service import supabase


# --------------------------------------------------
# Tiny test data
# --------------------------------------------------

texts = [
    "Aircraft engines require regular maintenance and inspection.",
    "Glow plugs are inspected for damage and thread condition.",
    "The battery system stores electrical energy for the aircraft."
]


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

print("Generating test embeddings...")

embeddings = generate_embeddings(
    texts
)


# --------------------------------------------------
# Insert test document
# --------------------------------------------------

document = (
    supabase
    .table("documents")
    .insert({
        "filename": "vector-test.pdf",
        "storage_path": "test/vector-test.pdf"
    })
    .execute()
)

document_id = document.data[0]["id"]


# --------------------------------------------------
# Insert chunks
# --------------------------------------------------

rows = []

for i, (text, embedding) in enumerate(
    zip(texts, embeddings)
):

    rows.append({
        "document_id": document_id,
        "content": text,
        "page": i + 1,
        "chunk_index": i,
        "embedding": embedding.tolist()
    })


supabase \
    .table("document_chunks") \
    .insert(rows) \
    .execute()


print("Test vectors inserted.")


# --------------------------------------------------
# Search
# --------------------------------------------------

question = "How are glow plugs inspected?"

print("\nGenerating question embedding...")

query_embedding = generate_embeddings(
    [question]
)[0]


response = (
    supabase
    .rpc(
        "match_document_chunks",
        {
            "query_embedding":
                query_embedding.tolist(),

            "match_count": 3
        }
    )
    .execute()
)


print("\n# SEARCH RESULTS")

for i, result in enumerate(
    response.data,
    start=1
):

    print(f"\nResult {i}")

    print(
        "Page:",
        result["page"]
    )

    print(
        "Similarity:",
        result["similarity"]
    )

    print(
        "Text:",
        result["content"]
    )