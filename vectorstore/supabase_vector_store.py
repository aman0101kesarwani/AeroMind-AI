from services.supabase_service import supabase


# ============================================================
# AeroMind AI - Supabase Vector Store
# ============================================================


# ============================================================
# Create Document
# ============================================================

def create_document(
    filename: str,
    storage_path: str,
    user_id: str
):
    """
    Create a document record.

    NOTE:
    This function is kept here for backward compatibility.
    The main document service also provides this operation.
    """

    response = (
        supabase
        .table("documents")
        .insert({
            "filename": filename,
            "storage_path": storage_path,
            "user_id": user_id
        })
        .execute()
    )

    if not response.data:
        raise RuntimeError(
            "Failed to create document."
        )

    return response.data[0]


# ============================================================
# Check Document Exists
# ============================================================

def document_exists(
    filename: str,
    user_id: str
):
    """
    Check whether a document already exists
    for this specific user.
    """

    response = (
        supabase
        .table("documents")
        .select("id")
        .eq("filename", filename)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    return bool(response.data)


# ============================================================
# Get Document
# ============================================================

def get_document(
    filename: str,
    user_id: str
):
    """
    Get a specific user's document.
    """

    response = (
        supabase
        .table("documents")
        .select("*")
        .eq("filename", filename)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# ============================================================
# Add Document Chunks + Embeddings
# ============================================================

def add_chunks(
    document_id: str,
    chunks,
    embeddings,
    user_id: str
):
    """
    Store document chunks and their embeddings
    in Supabase.

    Every chunk receives the same document_id
    and user_id as its parent document.
    """

    if not document_id:
        raise ValueError(
            "document_id is required."
        )

    if not user_id:
        raise ValueError(
            "user_id is required."
        )

    if chunks is None:
        raise ValueError(
            "chunks cannot be None."
        )

    if embeddings is None:
        raise ValueError(
            "embeddings cannot be None."
        )

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Number of chunks and embeddings "
            "must be identical."
        )

    rows = []

    for index, (
        chunk,
        embedding
    ) in enumerate(
        zip(chunks, embeddings)
    ):

        text = chunk.get(
            "text",
            ""
        )

        if not text or not text.strip():
            continue

        page = chunk.get(
            "page",
            1
        )

        rows.append({

            "document_id":
                document_id,

            "user_id":
                user_id,

            "content":
                text,

            "page":
                page,

            "chunk_index":
                index,

            "embedding":
                embedding.tolist()
                if hasattr(
                    embedding,
                    "tolist"
                )
                else list(embedding)
        })

    if not rows:
        raise ValueError(
            "No valid chunks were available "
            "to store."
        )

    # --------------------------------------------------------
    # Insert in batches
    # --------------------------------------------------------

    batch_size = 100

    for start in range(
        0,
        len(rows),
        batch_size
    ):

        batch = rows[
            start:start + batch_size
        ]

        (
            supabase
            .table("document_chunks")
            .insert(batch)
            .execute()
        )


# ============================================================
# Get Indexed Documents
# ============================================================

def get_indexed_documents(
    user_id: str
):
    """
    Return filenames belonging ONLY to the current user.
    """

    if not user_id:
        return []

    response = (
        supabase
        .table("documents")
        .select("filename")
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    return [
        row["filename"]
        for row in (response.data or [])
        if row.get("filename")
    ]


# ============================================================
# Get User Documents
# ============================================================

def get_user_documents(
    user_id: str
):
    """
    Return complete document information
    belonging ONLY to the current user.
    """

    if not user_id:
        return []

    response = (
        supabase
        .table("documents")
        .select(
            "id, filename, storage_path, created_at"
        )
        .eq("user_id", user_id)
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )

    return response.data or []


# ============================================================
# Search Vector Database
# ============================================================

def search_chunks(
    query_embedding,
    top_k: int = 5,
    sources=None,
    user_id: str | None = None
):
    """
    Search document vectors using the Supabase RPC.

    IMPORTANT:
    user_id is mandatory for real user isolation.
    """

    if not user_id:
        raise ValueError(
            "user_id is required for vector search."
        )

    if query_embedding is None:
        raise ValueError(
            "query_embedding cannot be None."
        )

    # --------------------------------------------------------
    # Convert embedding to normal Python list
    # --------------------------------------------------------

    if hasattr(
        query_embedding,
        "tolist"
    ):

        embedding = (
            query_embedding.tolist()
        )

    else:

        embedding = list(
            query_embedding
        )

    # --------------------------------------------------------
    # Build RPC parameters
    # --------------------------------------------------------

    params = {

        "query_embedding":
            embedding,

        "match_count":
            int(top_k),

        "filter_user_id":
            user_id,

        "filter_filenames":
            sources
            if sources
            else None
    }

    # --------------------------------------------------------
    # Supabase vector search
    # --------------------------------------------------------

    response = (
        supabase
        .rpc(
            "match_document_chunks",
            params
        )
        .execute()
    )

    return response.data or []


# ============================================================
# Delete Document
# ============================================================

def delete_document(
    document_id: str,
    user_id: str
):
    """
    Delete a document from Supabase.

    PostgreSQL ON DELETE CASCADE automatically
    removes all document_chunks belonging to it.
    """

    if not document_id:
        raise ValueError(
            "document_id is required."
        )

    if not user_id:
        raise ValueError(
            "user_id is required."
        )

    response = (
        supabase
        .table("documents")
        .delete()
        .eq("id", document_id)
        .eq("user_id", user_id)
        .execute()
    )

    return response.data or []


# ============================================================
# Delete Document By Filename
# ============================================================

def delete_document_by_filename(
    filename: str,
    user_id: str
):
    """
    Delete a user's document using its filename.

    The document is first looked up using user_id,
    preventing another user's document from being deleted.
    """

    document = get_document(
        filename=filename,
        user_id=user_id
    )

    if not document:
        return None

    return delete_document(
        document_id=document["id"],
        user_id=user_id
    )