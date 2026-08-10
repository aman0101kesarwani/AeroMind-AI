from embeddings.embedding_model import generate_embeddings

from vectorstore.supabase_vector_store import (
    search_chunks
)


def retrieve_chunks(
    question,
    top_k=5,
    sources=None
):

    query_embedding = generate_embeddings(
        [question]
    )[0]

    results = search_chunks(
        query_embedding,
        top_k=top_k,
        sources=sources
    )

    retrieved_chunks = []

    for result in results:

        retrieved_chunks.append({

            "text":
                result["content"],

            "source":
                result["filename"],

            "page":
                result["page"],

            "similarity":
                result["similarity"]
        })

    return retrieved_chunks