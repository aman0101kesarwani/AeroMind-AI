from pathlib import Path

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks
from embeddings.embedding_model import generate_embeddings
from vectorstore.chroma_store import add_chunks

from vectorstore.chroma_store import get_collection_count





pdf_path = next(Path("data/uploaded_pdfs").glob("*.pdf"))

pages = extract_text_from_pdf(pdf_path)

chunks = split_pages_into_chunks(pages)

chunks = chunks[:10]

texts = [chunk["text"] for chunk in chunks]

embeddings = generate_embeddings(texts)

add_chunks(
    chunks=chunks,
    embeddings=embeddings,
    source=pdf_path.name
)

print("Successfully stored chunks in ChromaDB.")

print("Stored documents:", get_collection_count())

