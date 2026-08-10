import streamlit as st

from pathlib import Path

from services.pdf_service import save_uploaded_files
from services.ingestion_service import ingest_pdf
from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer



st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide"
)


st.title("✈️ AeroMind AI")
st.caption("Multimodal Agentic RAG for Engineering Documents")


# --------------------------------------------------
# PDF Upload
# --------------------------------------------------

st.header("📄 Upload Engineering Documents")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    save_uploaded_files(uploaded_files)

    st.success(
        f"{len(uploaded_files)} file(s) uploaded successfully!"
    )

    if st.button("⚙️ Process Documents"):

        pdf_folder = Path("data/uploaded_pdfs")

        pdf_files = list(pdf_folder.glob("*.pdf"))

        progress_text = st.empty()

        for pdf_path in pdf_files:

            progress_text.write(
                f"Processing: {pdf_path.name}"
            )

            ingest_pdf(pdf_path)

        progress_text.success(
            "✅ All documents processed successfully!"
        )


# --------------------------------------------------
# Chat
# --------------------------------------------------

st.header("💬 Ask Your Documents")


if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


question = st.chat_input(
    "Ask a question about your engineering documents..."
)


if question:

    # Show user message
    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })


    # Retrieve relevant chunks
    with st.spinner("🔎 Searching documents..."):

        retrieved_chunks = retrieve_chunks(
            question,
            top_k=5
        )


    # Generate answer
    with st.spinner("🤖 Generating answer..."):

        answer = generate_rag_answer(
            question,
            retrieved_chunks
        )


    # Show answer
    with st.chat_message("assistant"):

        st.markdown(answer)


    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })