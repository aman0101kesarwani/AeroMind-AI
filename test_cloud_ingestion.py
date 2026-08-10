from pathlib import Path

from services.cloud_ingestion_service import (
    ingest_uploaded_pdf
)


pdf_path = Path(
    "data/uploaded_pdfs/Engine-Maintenance-Manual.pdf"
)


result = ingest_uploaded_pdf(
    pdf_path
)


print("\nRESULT")
print(result)