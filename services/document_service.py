from services.supabase_service import supabase


# ============================================================
# AeroMind AI - Document Database Service
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
    Create a document record in Supabase.

    Every document belongs to exactly one anonymous user.
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
            "Failed to create document record."
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
    Check whether this user has already indexed
    a document with the same filename.
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
    Get a specific document belonging to the user.
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
# Get Document By ID
# ============================================================

def get_document_by_id(
    document_id: str,
    user_id: str
):
    """
    Get a document by ID while enforcing user isolation.
    """

    response = (
        supabase
        .table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


# ============================================================
# Get All User Documents
# ============================================================

def get_user_documents(
    user_id: str
):
    """
    Return all documents belonging to the current user.
    """

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
# Get Indexed Document Names
# ============================================================

def get_indexed_documents(
    user_id: str
):
    """
    Return only filenames belonging to this user.
    """

    documents = get_user_documents(
        user_id
    )

    return [
        document["filename"]
        for document in documents
    ]


# ============================================================
# Delete Document Database Record
# ============================================================

def delete_document(
    document_id: str,
    user_id: str
):
    """
    Delete a user's document database record.

    Because document_chunks.document_id has
    ON DELETE CASCADE, its vector chunks are
    automatically deleted by PostgreSQL.
    """

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
    Delete a document using its filename.

    User isolation is enforced.
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