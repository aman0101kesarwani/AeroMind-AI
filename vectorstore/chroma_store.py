import chromadb
import hashlib

DB_PATH = "data/chroma_db"

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="engineering_documents"
)


# Store chunks
def add_chunks(chunks, embeddings, source):

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        chunk_id = hashlib.md5(
            f"{source}_{i}".encode()
        ).hexdigest()

        ids.append(chunk_id)

        documents.append(chunk["text"])

        metadatas.append({
            "source": source,
            "page": chunk["page"]
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )


# Search chunks
def search_chunks(
    query_embedding,
    top_k=5,
    sources=None
):

    query_params = {
        "query_embeddings": [query_embedding.tolist()],
        "n_results": top_k
    }

    if sources:

        query_params["where"] = {
            "source": {
                "$in": sources
            }
        }

    results = collection.query(
        **query_params
    )

    return results


# Check whether document is already indexed
def document_exists(source):

    results = collection.get(
        where={
            "source": source
        },
        limit=1
    )

    return len(results["ids"]) > 0


# Get all indexed document names
def get_indexed_documents():

    results = collection.get(
        include=["metadatas"]
    )

    sources = set()

    for metadata in results["metadatas"]:

        if metadata and "source" in metadata:

            sources.add(
                metadata["source"]
            )

    return sorted(sources)