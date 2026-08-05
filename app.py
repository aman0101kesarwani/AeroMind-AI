import streamlit as st
from services.pdf_service import save_uploaded_files


st.title("AeroMind AI")
# st.write("Welcome to AeroMind AI")

st.header("Upload Engineering Documents")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    save_uploaded_files(uploaded_files)
    st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")