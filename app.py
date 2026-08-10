import streamlit as st
from pathlib import Path
import tempfile
import os

from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer

from services.cloud_ingestion_service import (
    ingest_uploaded_pdf
)

from vectorstore.supabase_vector_store import (
    get_indexed_documents
)


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide"
)


# ==================================================
# Sidebar - Indexed Documents
# ==================================================

st.sidebar.title("📚 Your Documents")

indexed_documents = get_indexed_documents()

if indexed_documents:

    selected_documents = st.sidebar.multiselect(
        "Search in:",
        indexed_documents,
        default=indexed_documents
    )

else:

    selected_documents = []

    st.sidebar.info(
        "Upload a PDF to get started."
    )


# ==================================================
# Main Title
# ==================================================

st.title("✈️ AeroMind AI")

st.caption(
    "Multimodal Agentic RAG for Engineering Documents"
)


# ==================================================
# PDF Upload
# ==================================================

st.header("📄 Upload Engineering Documents")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ==================================================
# Process Uploaded PDFs
# ==================================================

if uploaded_files:

    if st.button(
        "🚀 Process Documents",
        type="primary"
    ):

        for uploaded_file in uploaded_files:

            with st.spinner(
                f"🔄 Processing {uploaded_file.name}..."
            ):

                temp_path = None

                try:

                    # ------------------------------------------
                    # Save PDF temporarily
                    # ------------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getbuffer()
                        )

                        temp_path = Path(
                            temp_file.name
                        )

                    # ------------------------------------------
                    # Automatic Cloud Ingestion
                    # ------------------------------------------

                    result = ingest_uploaded_pdf(
                        temp_path
                    )

                    # ------------------------------------------
                    # Already Indexed
                    # ------------------------------------------

                    if result["status"] == "already_indexed":

                        st.info(
                            f"✓ {uploaded_file.name} "
                            "is already indexed."
                        )

                    # ------------------------------------------
                    # Successfully Processed
                    # ------------------------------------------

                    elif result["status"] == "processed":

                        st.success(
                            f"✅ {uploaded_file.name} "
                            "is ready for questions!"
                        )

                        st.caption(
                            f"Pages: {result['pages']} | "
                            f"Chunks: {result['chunks']}"
                        )

                    # ------------------------------------------
                    # Unexpected Status
                    # ------------------------------------------

                    else:

                        st.warning(
                            f"⚠️ {uploaded_file.name}: "
                            f"{result}"
                        )

                except Exception as e:

                    st.error(
                        f"❌ Failed to process "
                        f"{uploaded_file.name}: {e}"
                    )

                finally:

                    # ------------------------------------------
                    # Delete Temporary PDF
                    # ------------------------------------------

                    if (
                        temp_path
                        and temp_path.exists()
                    ):

                        try:

                            os.remove(temp_path)

                        except Exception:

                            pass

        # Refresh automatically after processing
        st.rerun()


# ==================================================
# Refresh Documents
# ==================================================

if st.button("🔄 Refresh Documents"):

    st.rerun()


# ==================================================
# Chat
# ==================================================

st.header("💬 Ask Your Documents")


# ==================================================
# Initialize Chat History
# ==================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ==================================================
# Display Previous Messages
# ==================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==================================================
# Chat Input
# ==================================================

question = st.chat_input(
    "Ask a question about your engineering documents..."
)


# ==================================================
# Process Question
# ==================================================

if question:

    # --------------------------------------------------
    # Check Document Selection
    # --------------------------------------------------

    if not selected_documents:

        st.warning(
            "⚠️ Please select at least one document "
            "from the sidebar."
        )

        st.stop()

    # --------------------------------------------------
    # Show User Message
    # --------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # --------------------------------------------------
    # Retrieve Relevant Chunks
    # --------------------------------------------------

    with st.spinner(
        "🔎 Searching documents..."
    ):

        try:

            retrieved_chunks = retrieve_chunks(
                question,
                top_k=5,
                sources=selected_documents
            )

        except Exception as e:

            st.error(
                f"❌ Retrieval failed: {e}"
            )

            st.stop()

    # --------------------------------------------------
    # Check Retrieval
    # --------------------------------------------------

    if not retrieved_chunks:

        answer = (
            "I couldn't find relevant information "
            "in the selected documents."
        )

    else:

        # --------------------------------------------------
        # Generate Answer
        # --------------------------------------------------

        with st.spinner(
            "🤖 Generating answer..."
        ):

            try:

                answer = generate_rag_answer(
                    question,
                    retrieved_chunks
                )

            except Exception as e:

                answer = (
                    "⚠️ I couldn't generate an answer "
                    "right now. Please try again."
                )

    # --------------------------------------------------
    # Show Assistant Answer
    # --------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)

    # --------------------------------------------------
    # Save Assistant Message
    # --------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })