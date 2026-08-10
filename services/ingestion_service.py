from pathlib import Path

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks
from embeddings.embedding_model import generate_embeddings
from vectorstore.chroma_store import add_chunks


def ingest_pdf(pdf_path: Path):

    print(f"\nProcessing: {pdf_path.name}")

    # 1. Read PDF
    pages = extract_text_from_pdf(pdf_path)

    print(f"Pages extracted: {len(pages)}")

    # 2. Create chunks
    chunks = split_pages_into_chunks(pages)

    print(f"Chunks created: {len(chunks)}")

    # 3. Extract chunk text
    texts = [chunk["text"] for chunk in chunks]

    # 4. Generate embeddings
    embeddings = generate_embeddings(texts)

    print(f"Embeddings generated: {len(embeddings)}")

    # 5. Store in ChromaDB
    add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        source=pdf_path.name
    )

    print("Stored in ChromaDB.")

    return {
        "source": pdf_path.name,
        "pages": len(pages),
        "chunks": len(chunks)
    }