from services.supabase_service import supabase


# --------------------------------------------------
# Document
# --------------------------------------------------

def create_document(filename, storage_path):

    response = (
        supabase
        .table("documents")
        .insert({
            "filename": filename,
            "storage_path": storage_path
        })
        .execute()
    )

    return response.data[0]


# --------------------------------------------------
# Check document
# --------------------------------------------------

def document_exists(filename):

    response = (
        supabase
        .table("documents")
        .select("id")
        .eq("filename", filename)
        .limit(1)
        .execute()
    )

    return len(response.data) > 0


# --------------------------------------------------
# Get document
# --------------------------------------------------

def get_document(filename):

    response = (
        supabase
        .table("documents")
        .select("*")
        .eq("filename", filename)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# --------------------------------------------------
# Store chunks
# --------------------------------------------------

def add_chunks(
    document_id,
    chunks,
    embeddings
):

    rows = []

    for i, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):

        rows.append({
            "document_id": document_id,
            "content": chunk["text"],
            "page": chunk["page"],
            "chunk_index": i,
            "embedding": embedding.tolist()
        })

    if rows:

        supabase \
            .table("document_chunks") \
            .insert(rows) \
            .execute()


# --------------------------------------------------
# Get indexed documents
# --------------------------------------------------

def get_indexed_documents():

    response = (
        supabase
        .table("documents")
        .select("filename")
        .order("created_at", desc=True)
        .execute()
    )

    return [
        row["filename"]
        for row in response.data
    ]






# Add search to our vector store
def search_chunks(
    query_embedding,
    top_k=5,
    sources=None
):

    params = {
        "query_embedding":
            query_embedding.tolist(),

        "match_count":
            top_k
    }

    if sources:

        params["filter_filenames"] = sources

    response = (
        supabase
        .rpc(
            "match_document_chunks",
            params
        )
        .execute()
    )

    return response.data