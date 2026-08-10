from embeddings.embedding_model import generate_embeddings
from vectorstore.chroma_store import search_chunks


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

    for i in range(
        len(results["documents"][0])
    ):

        retrieved_chunks.append({

            "text": results["documents"][0][i],

            "source":
                results["metadatas"][0][i]["source"],

            "page":
                results["metadatas"][0][i]["page"],

            "distance":
                results["distances"][0][i]
        })

    return retrieved_chunks