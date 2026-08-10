from pathlib import Path

from services.ingestion_service import ingest_pdf


pdf_folder = Path("data/uploaded_pdfs")

pdf_files = list(pdf_folder.glob("*.pdf"))


for pdf_path in pdf_files:

    result = ingest_pdf(pdf_path)

    print("\n# INGESTION COMPLETE")
    print("=" * 50)

    print("Source:", result["source"])
    print("Status:", result["status"])

    if result["status"] == "processed":

        print("Pages:", result["pages"])
        print("Chunks:", result["chunks"])

    elif result["status"] == "already_indexed":

        print("ℹ️ Document was already indexed.")
        print("No embedding was generated.")