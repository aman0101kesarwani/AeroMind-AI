import streamlit as st
import tempfile
import os
import uuid

from streamlit_cookies_controller import CookieController

from services.retrieval_service import (
    retrieve_chunks
)

from services.gemini_service import (
    generate_rag_answer
)

from services.cloud_ingestion_service import (
    ingest_uploaded_pdf
)

from vectorstore.supabase_vector_store import (
    get_indexed_documents,
    delete_document
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
# Persistent Anonymous User Identity
# ==================================================

cookies = CookieController()

COOKIE_NAME = "aeromind_user_id"


# --------------------------------------------------
# Get existing user ID
# --------------------------------------------------

user_id = cookies.get(
    COOKIE_NAME
)


# --------------------------------------------------
# Create user ID for first-time visitor
# --------------------------------------------------

if not user_id:

    user_id = str(
        uuid.uuid4()
    )

    cookies.set(
        COOKIE_NAME,
        user_id,
        max_age=60 * 60 * 24 * 365
    )


# ==================================================
# Main Title
# ==================================================

st.title("✈️ AeroMind AI")

st.caption(
    "Multimodal Agentic RAG for Engineering Documents"
)


# ==================================================
# Sidebar - Documents
# ==================================================

st.sidebar.title(
    "📚 Your Documents"
)


documents = get_indexed_documents(
    user_id=user_id
)


# ==================================================
# Document Management
# ==================================================

if documents:

    st.sidebar.caption(
        f"{len(documents)} document(s)"
    )


    for document in documents:

        filename = document[
            "filename"
        ]


        with st.sidebar.container(
            border=True
        ):

            st.write(
                f"📄 {filename}"
            )


            if st.button(
                "🗑️ Delete",
                key=f"delete_{document['id']}",
                use_container_width=True
            ):

                try:

                    with st.spinner(
                        f"Deleting {filename}..."
                    ):

                        deleted = delete_document(

                            filename=
                                filename,

                            user_id=
                                user_id
                        )


                    if deleted:

                        st.success(
                            f"Deleted {filename}"
                        )

                    else:

                        st.warning(
                            "Document not found."
                        )


                    st.rerun()


                except Exception as e:

                    st.error(
                        f"❌ Delete failed: {e}"
                    )


    # --------------------------------------------------
    # Document Selection
    # --------------------------------------------------

    document_names = [

        document["filename"]

        for document in documents
    ]


    selected_documents = st.sidebar.multiselect(

        "Search in:",

        document_names,

        default=document_names
    )


else:

    selected_documents = []

    st.sidebar.info(
        "No documents uploaded yet."
    )


# ==================================================
# PDF Upload
# ==================================================

st.header(
    "📄 Upload Engineering Documents"
)


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
                f"🔄 Processing "
                f"{uploaded_file.name}..."
            ):

                temp_path = None


                try:

                    # ----------------------------------
                    # Temporary processing file
                    # ----------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getbuffer()
                        )

                        temp_path = temp_file.name


                    # ----------------------------------
                    # Cloud ingestion
                    # ----------------------------------

                    result = ingest_uploaded_pdf(

                        pdf_path=
                            temp_path,

                        user_id=
                            user_id,

                        filename=
                            uploaded_file.name
                    )


                    # ----------------------------------
                    # Already indexed
                    # ----------------------------------

                    if (
                        result["status"]
                        ==
                        "already_indexed"
                    ):

                        st.info(
                            f"✓ {uploaded_file.name} "
                            "is already indexed."
                        )


                    # ----------------------------------
                    # Successfully processed
                    # ----------------------------------

                    elif (
                        result["status"]
                        ==
                        "processed"
                    ):

                        st.success(
                            f"✅ {uploaded_file.name} "
                            "is ready for questions!"
                        )


                        st.caption(

                            f"Pages: "
                            f"{result['pages']} | "

                            f"Chunks: "
                            f"{result['chunks']}"
                        )


                    else:

                        st.warning(
                            f"⚠️ "
                            f"{uploaded_file.name}: "
                            f"{result}"
                        )


                except Exception as e:

                    st.error(

                        f"❌ Failed to process "
                        f"{uploaded_file.name}: "
                        f"{e}"
                    )


                finally:

                    # ----------------------------------
                    # Remove temporary server copy
                    # ----------------------------------

                    if (
                        temp_path
                        and os.path.exists(
                            temp_path
                        )
                    ):

                        try:

                            os.remove(
                                temp_path
                            )

                        except Exception:

                            pass


        st.rerun()


# ==================================================
# Chat
# ==================================================

st.header(
    "💬 Ask Your Documents"
)


# ==================================================
# Chat History
# ==================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


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
    # Check documents
    # --------------------------------------------------

    if not selected_documents:

        st.warning(
            "⚠️ Please select at least one "
            "document from the sidebar."
        )

        st.stop()


    # --------------------------------------------------
    # User message
    # --------------------------------------------------

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )


    st.session_state.messages.append({

        "role":
            "user",

        "content":
            question
    })


    # --------------------------------------------------
    # Vector retrieval
    # --------------------------------------------------

    with st.spinner(
        "🔎 Searching your documents..."
    ):

        try:

            retrieved_chunks = retrieve_chunks(

                question=
                    question,

                top_k=
                    5,

                sources=
                    selected_documents,

                user_id=
                    user_id
            )


        except Exception as e:

            st.error(
                f"❌ Retrieval failed: {e}"
            )

            st.stop()


    # --------------------------------------------------
    # No relevant information
    # --------------------------------------------------

    if not retrieved_chunks:

        answer = (
            "I couldn't find relevant information "
            "in the selected documents."
        )


    # --------------------------------------------------
    # Generate answer
    # --------------------------------------------------

    else:

        with st.spinner(
            "🤖 Generating answer..."
        ):

            try:

                answer = generate_rag_answer(

                    question,

                    retrieved_chunks
                )

            except Exception:

                answer = (
                    "⚠️ I couldn't generate an answer "
                    "right now. Please try again."
                )


    # --------------------------------------------------
    # Assistant response
    # --------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        st.markdown(
            answer
        )


    # --------------------------------------------------
    # Save response
    # --------------------------------------------------

    st.session_state.messages.append({

        "role":
            "assistant",

        "content":
            answer
    })