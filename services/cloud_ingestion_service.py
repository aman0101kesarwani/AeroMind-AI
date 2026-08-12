from pathlib import Path
import re

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks
from embeddings.embedding_model import generate_embeddings

from services.document_service import (
    create_document,
    document_exists,
)

from services.storage_service import (
    upload_pdf,
    delete_pdf,
)


# ============================================================
# AeroMind AI - Cloud PDF Ingestion
# ============================================================


def _safe_filename(filename: str) -> str:
    """
    Keep the original filename while removing characters
    that could cause problems in a storage path.
    """

    filename = Path(filename).name

    filename = re.sub(
        r"[^a-zA-Z0-9._()\- ]",
        "_",
        filename
    )

    return filename.strip() or "document.pdf"


# ============================================================
# Ingest Uploaded PDF
# ============================================================

def ingest_uploaded_pdf(
    pdf_path: Path,
    user_id: str,
    original_filename: str | None = None
):
    """
    Complete PDF ingestion pipeline.

    The PDF is:
        1. Read
        2. Stored in Supabase Storage
        3. Text extracted
        4. Split into chunks
        5. Embedded
        6. Stored in Supabase

    Everything persistent is stored in Supabase.
    """

    # --------------------------------------------------------
    # Validate user
    # --------------------------------------------------------

    if not user_id:
        raise ValueError(
            "user_id is required for document isolation."
        )

    # --------------------------------------------------------
    # Determine real filename
    # --------------------------------------------------------

    if original_filename:
        filename = _safe_filename(
            original_filename
        )
    else:
        filename = _safe_filename(
            pdf_path.name
        )

    # --------------------------------------------------------
    # Storage path
    # --------------------------------------------------------

    storage_path = (
        f"{user_id}/{filename}"
    )

    # --------------------------------------------------------
    # Check duplicate for THIS user
    # --------------------------------------------------------

    if document_exists(
        filename=filename,
        user_id=user_id
    ):

        return {
            "source": filename,
            "status": "already_indexed"
        }

    # --------------------------------------------------------
    # Validate PDF
    # --------------------------------------------------------

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    if pdf_path.stat().st_size == 0:

        raise ValueError(
            "The uploaded PDF is empty."
        )

    uploaded_to_storage = False

    try:

        # ====================================================
        # 1. Read PDF bytes
        # ====================================================

        with open(
            pdf_path,
            "rb"
        ) as file:

            pdf_bytes = file.read()

        # ====================================================
        # 2. Upload original PDF to Supabase Storage
        # ====================================================

        upload_pdf(
            file_bytes=pdf_bytes,
            storage_path=storage_path
        )

        uploaded_to_storage = True

        # ====================================================
        # 3. Extract PDF text
        # ====================================================

        pages = extract_text_from_pdf(
            pdf_path
        )

        if not pages:

            raise ValueError(
                "No readable text was found in the PDF."
            )

        # ====================================================
        # 4. Create chunks
        # ====================================================

        chunks = split_pages_into_chunks(
            pages
        )

        if not chunks:

            raise ValueError(
                "No text chunks could be created from the PDF."
            )

        # ====================================================
        # 5. Extract chunk text
        # ====================================================

        texts = [
            chunk["text"]
            for chunk in chunks
        ]

        # Remove empty chunks
        valid_chunks = []

        valid_texts = []

        for chunk, text in zip(
            chunks,
            texts
        ):

            if text and text.strip():

                valid_chunks.append(
                    chunk
                )

                valid_texts.append(
                    text
                )

        if not valid_chunks:

            raise ValueError(
                "The PDF contains no usable text."
            )

        # ====================================================
        # 6. Generate embeddings
        # ====================================================

        embeddings = generate_embeddings(
            valid_texts
        )

        if embeddings is None:
            raise RuntimeError(
                "Embedding generation returned no result."
            )

        if len(embeddings) != len(valid_chunks):

            raise RuntimeError(
                "Embedding count does not match "
                "the number of document chunks."
            )

        # ====================================================
        # 7. Create document database record
        # ====================================================

        document = create_document(

            filename=filename,

            storage_path=storage_path,

            user_id=user_id
        )

        document_id = document["id"]

        # ====================================================
        # 8. Store vectors/chunks
        # ====================================================

        from vectorstore.supabase_vector_store import add_chunks

        add_chunks(

            document_id=document_id,

            chunks=valid_chunks,

            embeddings=embeddings,

            user_id=user_id
        )

        # ====================================================
        # 9. Return success
        # ====================================================

        return {

            "source": filename,

            "status": "processed",

            "pages": len(pages),

            "chunks": len(valid_chunks),

            "document_id": document_id,

            "storage_path": storage_path
        }

    except Exception:

        # ----------------------------------------------------
        # Cleanup Storage if processing failed
        # ----------------------------------------------------

        if uploaded_to_storage:

            try:

                delete_pdf(
                    storage_path
                )

            except Exception:

                pass

        raise