from pathlib import Path

from services.pdf_reader import (
    extract_text_from_pdf
)

from services.text_splitter import (
    split_pages_into_chunks
)

from embeddings.embedding_model import (
    generate_embeddings
)

from vectorstore.supabase_vector_store import (
    add_chunks,
    document_exists,
    create_document,
    upload_pdf
)


# ============================================================
# Cloud PDF Ingestion
# ============================================================

def ingest_uploaded_pdf(
    pdf_path: Path,
    user_id: str,
    filename: str
):
    """
    Process an uploaded PDF.

    Pipeline:

    PDF
      ↓
    Supabase Storage
      ↓
    Extract text
      ↓
    Chunk
      ↓
    Qwen embeddings
      ↓
    Supabase pgvector
    """

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    if not user_id:

        raise ValueError(
            "user_id is required."
        )


    if not filename:

        raise ValueError(
            "filename is required."
        )


    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )


    # --------------------------------------------------------
    # Original filename
    # --------------------------------------------------------

    source = filename


    # --------------------------------------------------------
    # Check duplicate document
    # --------------------------------------------------------

    if document_exists(
        filename=source,
        user_id=user_id
    ):

        return {

            "source":
                source,

            "status":
                "already_indexed"
        }


    # --------------------------------------------------------
    # Storage path
    # --------------------------------------------------------
    #
    # Each user gets their own folder.
    #
    # Example:
    #
    # user-id/
    #     engine.pdf
    #
    # --------------------------------------------------------

    storage_path = (
        f"{user_id}/{source}"
    )


    # --------------------------------------------------------
    # 1. Upload PDF to Supabase Storage
    # --------------------------------------------------------

    upload_pdf(
        pdf_path=pdf_path,
        storage_path=storage_path
    )


    print(
        f"Uploaded to Storage: "
        f"{storage_path}"
    )


    try:

        # ----------------------------------------------------
        # 2. Read PDF
        # ----------------------------------------------------

        pages = extract_text_from_pdf(
            pdf_path
        )


        print(
            f"Pages extracted: "
            f"{len(pages)}"
        )


        # ----------------------------------------------------
        # 3. Create Chunks
        # ----------------------------------------------------

        chunks = split_pages_into_chunks(
            pages
        )


        print(
            f"Chunks created: "
            f"{len(chunks)}"
        )


        # ----------------------------------------------------
        # 4. Extract Text
        # ----------------------------------------------------

        texts = [

            chunk["text"]

            for chunk in chunks
        ]


        # ----------------------------------------------------
        # 5. Generate Embeddings
        # ----------------------------------------------------

        embeddings = generate_embeddings(
            texts
        )


        print(
            f"Embeddings generated: "
            f"{len(embeddings)}"
        )


        # ----------------------------------------------------
        # 6. Create Document Record
        # ----------------------------------------------------

        document = create_document(

            filename=source,

            storage_path=storage_path,

            user_id=user_id
        )


        document_id = document["id"]


        print(
            f"Document created: "
            f"{document_id}"
        )


        # ----------------------------------------------------
        # 7. Store Chunks + Embeddings
        # ----------------------------------------------------

        add_chunks(

            document_id=
                document_id,

            chunks=
                chunks,

            embeddings=
                embeddings,

            user_id=
                user_id
        )


        print(
            "Stored chunks and embeddings "
            "in Supabase."
        )


        # ----------------------------------------------------
        # 8. Return
        # ----------------------------------------------------

        return {

            "source":
                source,

            "status":
                "processed",

            "pages":
                len(pages),

            "chunks":
                len(chunks),

            "document_id":
                document_id
        }


    except Exception:

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        #
        # If ingestion fails after Storage upload,
        # remove the orphan PDF.
        #
        # ----------------------------------------------------

        try:

            from vectorstore.supabase_vector_store import (
                delete_pdf
            )

            delete_pdf(
                storage_path
            )

        except Exception:

            pass


        raise