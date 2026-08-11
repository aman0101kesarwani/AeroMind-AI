from embeddings.embedding_model import generate_embeddings

from vectorstore.supabase_vector_store import (
    search_chunks
)


# ============================================================
# Retrieve Relevant Chunks
# ============================================================

def retrieve_chunks(
    question,
    top_k=5,
    sources=None,
    user_id=None
):
    """
    Generate an embedding for the user's question
    and retrieve relevant document chunks from
    Supabase.

    Retrieval is restricted to the current user's
    documents using user_id.
    """

    # --------------------------------------------------------
    # 1. Generate Question Embedding
    # --------------------------------------------------------

    query_embedding = generate_embeddings(
        [question]
    )[0]


    # --------------------------------------------------------
    # 2. Search Supabase
    # --------------------------------------------------------

    results = search_chunks(

        query_embedding,

        top_k=top_k,

        sources=sources,

        user_id=user_id
    )


    # --------------------------------------------------------
    # 3. Convert Results
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # 4. Return Retrieved Chunks
    # --------------------------------------------------------

    return retrieved_chunks