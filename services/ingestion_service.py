from pathlib import Path

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks
from embeddings.embedding_model import generate_embeddings

from vectorstore.chroma_store import (
    add_chunks,
    document_exists
)


def ingest_pdf(pdf_path: Path):

    source = pdf_path.name

    # Check if document is already indexed
    if document_exists(source):

        print(f"Already indexed: {source}")

        return {
            "source": source,
            "status": "already_indexed"
        }

    print(f"\nProcessing: {source}")

    # 1. Read PDF
    pages = extract_text_from_pdf(pdf_path)

    print(f"Pages extracted: {len(pages)}")

    # 2. Create chunks
    chunks = split_pages_into_chunks(pages)

    print(f"Chunks created: {len(chunks)}")

    # 3. Extract text
    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    # 4. Generate embeddings
    embeddings = generate_embeddings(texts)

    print(
        f"Embeddings generated: {len(embeddings)}"
    )

    # 5. Store in ChromaDB
    add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        source=source
    )

    print("Stored in ChromaDB.")

    return {
        "source": source,
        "status": "processed",
        "pages": len(pages),
        "chunks": len(chunks)
    }