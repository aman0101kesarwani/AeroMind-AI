import os
import tempfile
import uuid
from pathlib import Path

import streamlit as st

from services.cloud_ingestion_service import (
    ingest_uploaded_pdf
)

from services.retrieval_service import (
    retrieve_chunks
)

from services.gemini_service import (
    generate_rag_answer
)

from services.document_service import (
    get_user_documents,
    delete_document
)

from services.storage_service import (
    delete_pdf
)


# ============================================================
# AeroMind AI
# Main Streamlit Application
# ============================================================


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide"
)


# ============================================================
# User Identity
# ============================================================

# Anonymous user identity.
#
# No Google authentication.
# No Supabase Auth account.
#
# Each active Streamlit session gets its own user_id.
# All documents/vectors are stored using this user_id.

if "user_id" not in st.session_state:

    st.session_state.user_id = str(
        uuid.uuid4()
    )


user_id = st.session_state.user_id


# ============================================================
# Chat State
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# Page Header
# ============================================================

st.title("✈️ AeroMind AI")

st.caption(
    "Multimodal Agentic RAG for Engineering Documents"
)


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("📚 Your Documents")

st.sidebar.caption(
    "Documents uploaded in this session"
)


# ============================================================
# Load User Documents
# ============================================================

try:

    user_documents = get_user_documents(
        user_id=user_id
    )

except Exception as e:

    st.sidebar.error(
        "Unable to load your documents."
    )

    st.sidebar.caption(
        str(e)
    )

    user_documents = []


# ============================================================
# Document Selection
# ============================================================

if user_documents:

    document_names = [
        document["filename"]
        for document in user_documents
    ]

    selected_documents = st.sidebar.multiselect(
        "Search in:",
        document_names,
        default=document_names
    )

else:

    selected_documents = []

    st.sidebar.info(
        "No documents processed yet."
    )


# ============================================================
# Delete Documents
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("🗑️ Delete Document")


if user_documents:

    delete_options = [
        document["filename"]
        for document in user_documents
    ]

    document_to_delete = st.sidebar.selectbox(
        "Select document:",
        delete_options,
        key="delete_document_select"
    )

    if st.sidebar.button(
        "🗑️ Delete Selected Document",
        use_container_width=True
    ):

        document = next(
            (
                item
                for item in user_documents
                if item["filename"]
                == document_to_delete
            ),
            None
        )

        if document is None:

            st.sidebar.error(
                "Document could not be found."
            )

        else:

            try:

                # ------------------------------------------
                # 1. Delete PDF from Supabase Storage
                # ------------------------------------------

                storage_path = document[
                    "storage_path"
                ]

                if storage_path:

                    delete_pdf(
                        storage_path
                    )

                # ------------------------------------------
                # 2. Delete database document
                # ------------------------------------------

                delete_document(
                    document_id=document["id"],
                    user_id=user_id
                )

                # ------------------------------------------
                # 3. Clear chat
                # ------------------------------------------

                st.session_state.messages = []

                st.sidebar.success(
                    f"Deleted: {document_to_delete}"
                )

                # ------------------------------------------
                # 4. Refresh application
                # ------------------------------------------

                st.rerun()

            except Exception as e:

                st.sidebar.error(
                    "Failed to delete document."
                )

                st.sidebar.caption(
                    str(e)
                )

else:

    st.sidebar.caption(
        "Upload and process a PDF first."
    )


# ============================================================
# Refresh Documents
# ============================================================

if st.sidebar.button(
    "🔄 Refresh Documents",
    use_container_width=True
):

    st.rerun()


# ============================================================
# Upload Section
# ============================================================

st.header("📄 Upload Engineering Documents")

st.write(
    "Upload one or more PDF files. "
    "AeroMind will automatically extract, "
    "embed, and index them."
)


uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader"
)


# ============================================================
# Process Documents
# ============================================================

if uploaded_files:

    st.write(
        f"**{len(uploaded_files)} PDF(s) selected**"
    )

    for uploaded_file in uploaded_files:

        st.caption(
            f"📄 {uploaded_file.name} "
            f"({uploaded_file.size / 1024:.1f} KB)"
        )

    if st.button(
        "🚀 Process Documents",
        type="primary",
        use_container_width=True
    ):

        total_files = len(
            uploaded_files
        )

        successful = 0

        already_indexed = 0

        failed = 0

        progress = st.progress(0)

        status_box = st.empty()

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            status_box.info(
                f"🔄 Processing "
                f"{uploaded_file.name} "
                f"({index + 1}/{total_files})"
            )

            temp_path = None

            try:

                # ==========================================
                # Save temporary copy
                # ==========================================

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

                # ==========================================
                # Process PDF
                # ==========================================

                result = ingest_uploaded_pdf(

                    pdf_path=temp_path,

                    user_id=user_id,

                    original_filename=
                        uploaded_file.name
                )

                # ==========================================
                # Already Indexed
                # ==========================================

                if (
                    result["status"]
                    == "already_indexed"
                ):

                    already_indexed += 1

                    st.info(
                        f"✓ {uploaded_file.name} "
                        "is already indexed."
                    )

                # ==========================================
                # Successfully Processed
                # ==========================================

                elif (
                    result["status"]
                    == "processed"
                ):

                    successful += 1

                    st.success(
                        f"✅ {uploaded_file.name} "
                        "processed successfully."
                    )

                    st.caption(
                        f"Pages: "
                        f"{result.get('pages', '?')} | "
                        f"Chunks: "
                        f"{result.get('chunks', '?')}"
                    )

                # ==========================================
                # Unknown Result
                # ==========================================

                else:

                    failed += 1

                    st.warning(
                        f"⚠️ Unexpected result for "
                        f"{uploaded_file.name}: "
                        f"{result}"
                    )

            except Exception as e:

                failed += 1

                st.error(
                    f"❌ Failed to process "
                    f"{uploaded_file.name}"
                )

                st.exception(e)

            finally:

                # ==========================================
                # Delete temporary local PDF
                # ==========================================

                if (
                    temp_path is not None
                    and temp_path.exists()
                ):

                    try:

                        os.remove(
                            temp_path
                        )

                    except Exception:

                        pass

            progress.progress(
                (index + 1) / total_files
            )

        # ==================================================
        # Final Processing Status
        # ==================================================

        status_box.success(
            "Processing completed."
        )

        st.write("---")

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Processed",
                successful
            )

        with col2:

            st.metric(
                "Already Indexed",
                already_indexed
            )

        with col3:

            st.metric(
                "Failed",
                failed
            )

        # ==================================================
        # Refresh sidebar
        # ==================================================

        st.rerun()


# ============================================================
# Chat Section
# ============================================================

st.header("💬 Ask Your Documents")


# ============================================================
# Current Document Status
# ============================================================

if selected_documents:

    st.success(
        f"Searching in "
        f"{len(selected_documents)} "
        f"document(s)."
    )

else:

    st.info(
        "Select at least one document "
        "from the sidebar."
    )


# ============================================================
# Display Chat History
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# Chat Input
# ============================================================

question = st.chat_input(
    "Ask a question about your engineering documents..."
)


# ============================================================
# Process Question
# ============================================================

if question:

    # ========================================================
    # Validate Documents
    # ========================================================

    if not selected_documents:

        st.warning(
            "⚠️ Please select at least one "
            "document from the sidebar."
        )

        st.stop()

    # ========================================================
    # Display User Question
    # ========================================================

    with st.chat_message("user"):

        st.markdown(
            question
        )

    st.session_state.messages.append({

        "role": "user",

        "content": question
    })

    # ========================================================
    # Retrieve
    # ========================================================

    with st.chat_message("assistant"):

        retrieval_status = st.empty()

        retrieval_status.info(
            "🔎 Searching your documents..."
        )

        try:

            retrieved_chunks = retrieve_chunks(

                question=question,

                top_k=5,

                sources=selected_documents,

                user_id=user_id
            )

        except Exception as e:

            retrieval_status.error(
                "❌ Document search failed."
            )

            st.exception(e)

            st.stop()

        # ====================================================
        # No Results
        # ====================================================

        if not retrieved_chunks:

            answer = (
                "I couldn't find relevant "
                "information in the selected "
                "documents."
            )

            retrieval_status.empty()

            st.markdown(
                answer
            )

        else:

            retrieval_status.success(
                f"🔎 Found "
                f"{len(retrieved_chunks)} "
                f"relevant sections."
            )

            # =================================================
            # Generate Gemini Answer
            # =================================================

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
                        "⚠️ I couldn't generate "
                        "an answer right now."
                    )

                    st.error(
                        str(e)
                    )

            # =================================================
            # Show Answer
            # =================================================

            st.markdown(
                answer
            )

            # =================================================
            # Sources
            # =================================================

            st.markdown(
                "### 📚 Sources"
            )

            shown_sources = set()

            for chunk in retrieved_chunks:

                source = chunk.get(
                    "source",
                    "Unknown"
                )

                page = chunk.get(
                    "page",
                    "?"
                )

                source_key = (
                    source,
                    page
                )

                if source_key in shown_sources:

                    continue

                shown_sources.add(
                    source_key
                )

                st.caption(
                    f"📄 {source} "
                    f"— Page {page}"
                )

    # ========================================================
    # Save Assistant Message
    # ========================================================

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer
    })