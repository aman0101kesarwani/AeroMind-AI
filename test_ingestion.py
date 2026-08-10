from pathlib import Path

from services.ingestion_service import ingest_pdf


pdf_path = next(
    Path("data/uploaded_pdfs").glob("*.pdf")
)

result = ingest_pdf(pdf_path)

print("\nINGESTION COMPLETE")
print("=" * 60)

print("Source:", result["source"])
print("Pages:", result["pages"])
print("Chunks:", result["chunks"])