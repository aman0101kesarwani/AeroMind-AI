from services.storage_service import upload_pdf


file_path = "data/uploaded_pdfs/Engine-Maintenance-Manual.pdf"

storage_path = upload_pdf(
    file_path,
    "Engine-Maintenance-Manual.pdf"
)

print("Uploaded successfully!")
print("Storage path:", storage_path)