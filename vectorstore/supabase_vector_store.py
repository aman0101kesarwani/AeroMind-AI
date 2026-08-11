from services.supabase_service import supabase


# ============================================================
# Storage Bucket
# ============================================================

STORAGE_BUCKET = "aeromind-pdfs"


# ============================================================
# Upload PDF to Supabase Storage
# ============================================================

def upload_pdf(
    pdf_path,
    storage_path
):
    """
    Upload a PDF file to Supabase Storage.
    """

    with open(
        pdf_path,
        "rb"
    ) as file:

        response = (
            supabase
            .storage
            .from_(STORAGE_BUCKET)
            .upload(
                storage_path,
                file,
                {
                    "content-type":
                        "application/pdf",

                    "upsert":
                        "false"
                }
            )
        )

    return response


# ============================================================
# Delete PDF from Supabase Storage
# ============================================================

def delete_pdf(
    storage_path
):
    """
    Delete a PDF from Supabase Storage.
    """

    response = (
        supabase
        .storage
        .from_(STORAGE_BUCKET)
        .remove([
            storage_path
        ])
    )

    return response


# ============================================================
# Create Document
# ============================================================

def create_document(
    filename,
    storage_path,
    user_id
):

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    response = (
        supabase
        .table("documents")
        .insert({
            "filename":
                filename,

            "storage_path":
                storage_path,

            "user_id":
                user_id
        })
        .execute()
    )


    if not response.data:

        raise RuntimeError(
            "Failed to create document."
        )


    return response.data[0]


# ============================================================
# Check Document
# ============================================================

def document_exists(
    filename,
    user_id
):

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    response = (
        supabase
        .table("documents")
        .select("id")
        .eq(
            "filename",
            filename
        )
        .eq(
            "user_id",
            user_id
        )
        .limit(1)
        .execute()
    )


    return len(response.data) > 0


# ============================================================
# Get Document
# ============================================================

def get_document(
    filename,
    user_id
):

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    response = (
        supabase
        .table("documents")
        .select("*")
        .eq(
            "filename",
            filename
        )
        .eq(
            "user_id",
            user_id
        )
        .limit(1)
        .execute()
    )


    if not response.data:

        return None


    return response.data[0]


# ============================================================
# Store Chunks
# ============================================================

def add_chunks(
    document_id,
    chunks,
    embeddings,
    user_id
):

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    rows = []


    for i, (chunk, embedding) in enumerate(
        zip(
            chunks,
            embeddings
        )
    ):

        rows.append({

            "document_id":
                document_id,

            "user_id":
                user_id,

            "content":
                chunk["text"],

            "page":
                chunk["page"],

            "chunk_index":
                i,

            "embedding":
                embedding.tolist()
        })


    if rows:

        response = (
            supabase
            .table("document_chunks")
            .insert(rows)
            .execute()
        )


        if not response.data:

            raise RuntimeError(
                "Failed to store document chunks."
            )


# ============================================================
# Get Indexed Documents
# ============================================================

def get_indexed_documents(
    user_id
):

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    response = (
        supabase
        .table("documents")
        .select(
            "id, filename, storage_path, created_at"
        )
        .eq(
            "user_id",
            user_id
        )
        .order(
            "created_at",
            desc=True
        )
        .execute()
    )


    return response.data


# ============================================================
# Delete Document
# ============================================================

def delete_document(
    filename,
    user_id
):
    """
    Completely delete a user's document.

    Deletes:
        1. PDF from Supabase Storage
        2. document row
        3. document chunks automatically
           through ON DELETE CASCADE
    """

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    # --------------------------------------------------------
    # Find document
    # --------------------------------------------------------

    document = get_document(
        filename=filename,
        user_id=user_id
    )


    if not document:

        return False


    storage_path = document[
        "storage_path"
    ]

    document_id = document[
        "id"
    ]


    # --------------------------------------------------------
    # Delete PDF from Storage
    # --------------------------------------------------------

    if storage_path:

        delete_pdf(
            storage_path
        )


    # --------------------------------------------------------
    # Delete database document
    # --------------------------------------------------------
    #
    # document_chunks.document_id references
    # documents.id ON DELETE CASCADE
    #
    # Therefore deleting this row also deletes:
    #
    # document_chunks
    # embeddings
    #
    # --------------------------------------------------------

    response = (
        supabase
        .table("documents")
        .delete()
        .eq(
            "id",
            document_id
        )
        .eq(
            "user_id",
            user_id
        )
        .execute()
    )


    return bool(response.data)


# ============================================================
# Search Chunks
# ============================================================

def search_chunks(
    query_embedding,
    top_k=5,
    sources=None,
    user_id=None
):

    if not user_id:

        raise ValueError(
            "user_id is required for vector search."
        )


    params = {

        "query_embedding":
            query_embedding.tolist(),

        "match_count":
            top_k,

        "filter_user_id":
            user_id
    }


    if sources:

        params[
            "filter_filenames"
        ] = sources


    response = (
        supabase
        .rpc(
            "match_document_chunks",
            params
        )
        .execute()
    )


    return response.data