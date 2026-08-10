from pathlib import Path


UPLOAD_DIR = Path("data/uploaded_pdfs")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def save_uploaded_files(uploaded_files):

    saved_paths = []

    for uploaded_file in uploaded_files:

        file_path = UPLOAD_DIR / uploaded_file.name

        with open(file_path, "wb") as f:

            f.write(
                uploaded_file.getbuffer()
            )

        saved_paths.append(file_path)

    return saved_paths