from services.supabase_service import supabase


BUCKET_NAME = "uploaded-pdfs"


def upload_pdf(file_path, filename):

    with open(file_path, "rb") as file:

        file_bytes = file.read()

    storage_path = filename

    supabase.storage \
        .from_(BUCKET_NAME) \
        .upload(
            storage_path,
            file_bytes,
            {
                "content-type": "application/pdf",
                "upsert": "true"
            }
        )

    return storage_path