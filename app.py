import streamlit as st
from pathlib import Path
import tempfile
import os
import uuid

from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer

from services.cloud_ingestion_service import (
    ingest_uploaded_pdf
)

from vectorstore.supabase_vector_store import (
    get_indexed_documents
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide"
)


# ============================================================
# USER ID
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

user_id = st.session_state.user_id


# ============================================================
# INITIALIZE CHAT
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# TITLE
# ============================================================

st.title("✈️ AeroMind AI")

st.caption(
    "Multimodal Agentic RAG for Engineering Documents"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 Your Documents")

try:

    indexed_documents = get_indexed_documents(
        user_id=user_id
    )

except Exception as e:

    indexed_documents = []

    st.sidebar.error(
        "Unable to load documents."
    )

    st.sidebar.caption(
        f"Database error: {e}"
    )


if indexed_documents:

    selected_documents = st.sidebar.multiselect(
        "Search in:",
        indexed_documents,
        default=indexed_documents
    )

else:

    selected_documents = []

    st.sidebar.info(
        "No documents uploaded yet."
    )


# ============================================================
# UPLOAD
# ============================================================

st.header("📄 Upload Engineering Documents")

uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)


# ============================================================
# PROCESS DOCUMENTS
# ============================================================

if uploaded_files:

    st.success(
        f"{len(uploaded_files)} PDF(s) selected."
    )

    if st.button(
        "🚀 Process Documents",
        type="primary",
        use_container_width=False
    ):

        total_files = len(uploaded_files)

        for file_number, uploaded_file in enumerate(
            uploaded_files,
            start=1
        ):

            st.divider()

            st.subheader(
                f"📄 {uploaded_file.name}"
            )

            progress = st.progress(0)

            status = st.empty()

            temp_path = None

            try:

                # ------------------------------------------------
                # STEP 1 — SAVE TEMPORARILY
                # ------------------------------------------------

                status.info(
                    "1/5 💾 Saving PDF temporarily..."
                )

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

                progress.progress(10)


                # ------------------------------------------------
                # STEP 2 — INGEST PDF
                # ------------------------------------------------

                status.info(
                    "2/5 📖 Reading and splitting PDF..."
                )

                result = ingest_uploaded_pdf(
                    temp_path,
                    user_id=user_id
                )

                progress.progress(100)


                # ------------------------------------------------
                # ALREADY INDEXED
                # ------------------------------------------------

                if result.get("status") == "already_indexed":

                    status.success(
                        f"✓ {uploaded_file.name} "
                        "is already indexed."
                    )


                # ------------------------------------------------
                # SUCCESS
                # ------------------------------------------------

                elif result.get("status") == "processed":

                    status.success(
                        f"✅ {uploaded_file.name} "
                        "processed successfully!"
                    )

                    st.write(
                        f"📄 Pages: "
                        f"{result.get('pages', 0)}"
                    )

                    st.write(
                        f"🧩 Chunks: "
                        f"{result.get('chunks', 0)}"
                    )

                else:

                    status.warning(
                        f"⚠️ Unexpected result: {result}"
                    )


            except Exception as e:

                progress.progress(0)

                status.error(
                    f"❌ Processing failed: {e}"
                )

                st.exception(e)


            finally:

                # ------------------------------------------------
                # DELETE TEMPORARY PDF
                # ------------------------------------------------

                if temp_path is not None:

                    try:

                        if temp_path.exists():

                            os.remove(temp_path)

                    except Exception:

                        pass


        # ========================================================
        # REFRESH AFTER PROCESSING
        # ========================================================

        st.success(
            "🎉 Processing finished. "
            "Refreshing your document list..."
        )

        st.rerun()


# ============================================================
# REFRESH BUTTON
# ============================================================

if st.sidebar.button(
    "🔄 Refresh Documents"
):

    st.rerun()


# ============================================================
# CHAT
# ============================================================

st.header("💬 Ask Your Documents")


# ============================================================
# DOCUMENT CHECK
# ============================================================

if not indexed_documents:

    st.info(
        "📄 Upload and process a PDF above. "
        "Once processing finishes, you can ask questions here."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your engineering documents..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # ----------------------------------------------------------
    # DOCUMENT CHECK
    # ----------------------------------------------------------

    if not indexed_documents:

        st.warning(
            "⚠️ Please upload and process a PDF first."
        )

        st.stop()


    if not selected_documents:

        st.warning(
            "⚠️ Please select at least one document "
            "from the sidebar."
        )

        st.stop()


    # ----------------------------------------------------------
    # USER MESSAGE
    # ----------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.messages.append({
        "role": "user",
        "content": question
    })


    # ----------------------------------------------------------
    # RETRIEVAL
    # ----------------------------------------------------------

    with st.spinner(
        "🔎 Searching your documents..."
    ):

        try:

            retrieved_chunks = retrieve_chunks(
                question,
                top_k=5,
                sources=selected_documents,
                user_id=user_id
            )

        except Exception as e:

            st.error(
                f"❌ Retrieval failed: {e}"
            )

            st.exception(e)

            st.stop()


    # ----------------------------------------------------------
    # NO RESULTS
    # ----------------------------------------------------------

    if not retrieved_chunks:

        answer = (
            "I couldn't find relevant information "
            "in the selected documents."
        )


    # ----------------------------------------------------------
    # GENERATE ANSWER
    # ----------------------------------------------------------

    else:

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
                    "right now."
                )

                st.error(
                    f"Generation error: {e}"
                )


    # ----------------------------------------------------------
    # SHOW ANSWER
    # ----------------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)


    # ----------------------------------------------------------
    # SAVE ANSWER
    # ----------------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })