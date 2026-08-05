from pathlib import Path

UPLOAD_DIR = Path("data/uploaded_pdfs")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_uploaded_files(uploaded_files):
    for file in uploaded_files:
        file_path = UPLOAD_DIR/file.name

        with open(file_path, "wb") as f:
            f.write(file.getbuffer())