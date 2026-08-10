from pathlib import Path

from services.pdf_reader import extract_text_from_pdf
from services.text_splitter import split_pages_into_chunks
from embeddings.embedding_model import generate_embeddings


# Find the first PDF in our uploaded PDF folder
pdf_path = next(Path("data/uploaded_pdfs").glob("*.pdf"))


# 1. Read PDF
pages = extract_text_from_pdf(pdf_path)


# 2. Split pages into chunks
chunks = split_pages_into_chunks(pages)


# 3. Take first 10 chunks for testing
texts = [chunk["text"] for chunk in chunks[:10]]


# 4. Generate embeddings
embeddings = generate_embeddings(texts)


# 5. Print results
print("=" * 60)
print(f"PDF: {pdf_path.name}")
print(f"Pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")
print(f"Chunks embedded: {len(embeddings)}")
print(f"Embedding shape: {embeddings.shape}")
print("=" * 60)