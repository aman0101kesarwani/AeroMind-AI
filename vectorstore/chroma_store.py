import chromadb
import hashlib

DB_PATH = "data/chroma_db"


client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name="engineering_documents"
)



# Create a Function to Store Chunks
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




# def get_collection_count():
#     return collection.count()



def search_chunks(query_embedding, top_k=3):

    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k
    )

    return results

