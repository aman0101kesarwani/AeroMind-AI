from pathlib import Path

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks

from embeddings.embedding_model import generate_embeddings

from services.storage_service import upload_pdf

from vectorstore.supabase_vector_store import (
    create_document,
    document_exists,
    add_chunks
)


def ingest_uploaded_pdf(pdf_path: Path):

    filename = pdf_path.name

    # -----------------------------------------------
    # Already indexed?
    # -----------------------------------------------

    if document_exists(filename):

        return {
            "status": "already_indexed",
            "filename": filename
        }

    # -----------------------------------------------
    # Upload original PDF
    # -----------------------------------------------

    storage_path = upload_pdf(
        pdf_path,
        filename
    )

    # -----------------------------------------------
    # Create document record
    # -----------------------------------------------

    document = create_document(
        filename,
        storage_path
    )

    document_id = document["id"]

    # -----------------------------------------------
    # Extract
    # -----------------------------------------------

    pages = extract_text_from_pdf(
        pdf_path
    )

    # -----------------------------------------------
    # Chunk
    # -----------------------------------------------

    chunks = split_pages_into_chunks(
        pages
    )

    if not chunks:

        raise ValueError(
            "No readable text found in PDF."
        )

    # -----------------------------------------------
    # Embeddings
    # -----------------------------------------------

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = generate_embeddings(
        texts
    )

    # -----------------------------------------------
    # Store vectors
    # -----------------------------------------------

    add_chunks(
        document_id,
        chunks,
        embeddings
    )

    return {
        "status": "processed",
        "filename": filename,
        "document_id": document_id,
        "pages": len(pages),
        "chunks": len(chunks)
    }