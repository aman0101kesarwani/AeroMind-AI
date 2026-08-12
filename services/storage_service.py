from services.supabase_service import supabase


# ============================================================
# AeroMind AI - Supabase PDF Storage
# ============================================================

BUCKET_NAME = "aeromind-pdfs"


# ============================================================
# Upload PDF
# ============================================================

def upload_pdf(
    file_bytes: bytes,
    storage_path: str
):
    """
    Upload PDF to Supabase Storage.

    The PDF is permanently stored in Supabase,
    not on the Streamlit server.
    """

    response = supabase.storage.from_(
        BUCKET_NAME
    ).upload(
        path=storage_path,
        file=file_bytes,
        file_options={
            "content-type": "application/pdf",
            "upsert": "true"
        }
    )

    return response


# ============================================================
# Delete PDF
# ============================================================

def delete_pdf(
    storage_path: str
):
    """
    Delete PDF from Supabase Storage.
    """

    response = supabase.storage.from_(
        BUCKET_NAME
    ).remove([
        storage_path
    ])

    return response


# ============================================================
# Check PDF
# ============================================================

def pdf_exists(
    storage_path: str
):
    """
    Check whether a PDF exists in Supabase Storage.
    """

    folder = "/".join(
        storage_path.split("/")[:-1]
    )

    filename = storage_path.split("/")[-1]

    try:

        files = (
            supabase
            .storage
            .from_(BUCKET_NAME)
            .list(folder)
        )

        for file in files:

            if file.get("name") == filename:
                return True

        return False

    except Exception:

        return False