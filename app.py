import os
import tempfile
import uuid

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
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# USER ID
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

user_id = st.session_state.user_id


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "upload_trigger" not in st.session_state:
    st.session_state.upload_trigger = 0


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ------------------------------------------------------
       GLOBAL
    ------------------------------------------------------ */

    .stApp {
        background: #f5f7fa;
    }

    .main {
        padding-top: 1.2rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    /* ------------------------------------------------------
       SIDEBAR
    ------------------------------------------------------ */

    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1f2937;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: #1f2937;
        color: #e5e7eb;
        border: 1px solid #374151;
        border-radius: 8px;
        min-height: 38px;
    }

    section[data-testid="stSidebar"]
    .stButton > button:hover {
        background: #273449;
        border-color: #4b5563;
    }

    /* ------------------------------------------------------
       HEADER
    ------------------------------------------------------ */

    .aero-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .aero-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }

    .aero-logo {
        width: 44px;
        height: 44px;
        border-radius: 10px;
        background: #162033;
        color: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        font-weight: 700;
    }

    .aero-title {
        font-size: 22px;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }

    .aero-subtitle {
        font-size: 13px;
        color: #6b7280;
        margin-top: 3px;
    }

    .system-status {
        display: flex;
        align-items: center;
        gap: 7px;
        font-size: 12px;
        color: #4b5563;
        white-space: nowrap;
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #16a34a;
    }

    /* ------------------------------------------------------
       SECTION LABEL
    ------------------------------------------------------ */

    .section-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
        color: #6b7280;
        margin-bottom: 8px;
    }

    /* ------------------------------------------------------
       UPLOAD CARD
    ------------------------------------------------------ */

    .upload-card {
        background: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .upload-title {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
    }

    .upload-description {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 14px;
    }

    /* ------------------------------------------------------
       CHAT AREA
    ------------------------------------------------------ */

    .workspace-card {
        background: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 14px;
        padding: 20px;
        min-height: 340px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .workspace-title {
        font-size: 18px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 3px;
    }

    .workspace-description {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 18px;
    }

    /* ------------------------------------------------------
       METRICS
    ------------------------------------------------------ */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 12px;
        padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #6b7280;
    }

    .metric-value {
        font-size: 21px;
        font-weight: 700;
        color: #111827;
        margin-top: 4px;
    }

    /* ------------------------------------------------------
       DOCUMENT ITEM
    ------------------------------------------------------ */

    .document-row {
        background: #ffffff;
        border: 1px solid #e3e7ed;
        border-radius: 10px;
        padding: 11px 13px;
        margin-bottom: 8px;
    }

    .document-name {
        font-size: 13px;
        font-weight: 600;
        color: #111827;
    }

    /* ------------------------------------------------------
       SOURCE
    ------------------------------------------------------ */

    .source-chip {
        display: inline-block;
        padding: 5px 9px;
        background: #f0f4f8;
        border: 1px solid #dbe2e8;
        border-radius: 7px;
        font-size: 11px;
        color: #374151;
        margin-right: 5px;
        margin-bottom: 5px;
    }

    /* ------------------------------------------------------
       BUTTONS
    ------------------------------------------------------ */

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* ------------------------------------------------------
       CHAT INPUT
    ------------------------------------------------------ */

    [data-testid="stChatInput"] {
        border-radius: 12px;
    }

    /* ------------------------------------------------------
       FILE UPLOADER
    ------------------------------------------------------ */

    [data-testid="stFileUploader"] {
        background: #fafbfc;
        border: 1px dashed #cbd5e1;
        border-radius: 10px;
        padding: 10px;
    }

    /* ------------------------------------------------------
       REMOVE EXCESSIVE STREAMLIT SPACING
    ------------------------------------------------------ */

    div.block-container {
        padding-bottom: 4rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD USER DOCUMENTS
# ============================================================

try:
    user_documents = get_user_documents(
        user_id=user_id
    )
except Exception as e:
    user_documents = []
    st.sidebar.error(
        "Unable to load documents."
    )


document_names = [
    document["filename"]
    for document in user_documents
]


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="aero-header">

        <div class="aero-brand">

            <div class="aero-logo">
                ✈
            </div>

            <div>
                <div class="aero-title">
                    AeroMind AI
                </div>

                <div class="aero-subtitle">
                    Engineering Intelligence Workspace
                </div>
            </div>

        </div>

        <div class="system-status">
            <div class="status-dot"></div>
            System ready
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 4px;
        ">
            Workspace
        </div>

        <div style="
            font-size: 12px;
            color: #9ca3af;
            margin-bottom: 18px;
        ">
            Manage your engineering documents
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # Document count
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div style="
            background:#1f2937;
            border:1px solid #374151;
            border-radius:9px;
            padding:11px 12px;
            margin-bottom:16px;
        ">
            <div style="
                font-size:11px;
                color:#9ca3af;
                text-transform:uppercase;
            ">
                Indexed documents
            </div>

            <div style="
                font-size:22px;
                font-weight:700;
                margin-top:3px;
            ">
                {len(document_names)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------------
    # Document list
    # --------------------------------------------------------

    if document_names:

        st.markdown(
            "### Documents"
        )

        for filename in document_names:

            st.markdown(
                f"""
                <div style="
                    background:#1b2533;
                    border:1px solid #2d3a4d;
                    border-radius:8px;
                    padding:10px 11px;
                    margin-bottom:7px;
                    font-size:12px;
                ">
                    <span style="color:#93c5fd;">
                        FILE
                    </span>
                    &nbsp;
                    {filename}
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            """
            <div style="
                color:#9ca3af;
                font-size:12px;
                padding:10px 0;
            ">
                No documents yet.
            </div>
            """,
            unsafe_allow_html=True
        )


    st.divider()


    # --------------------------------------------------------
    # Search selection
    # --------------------------------------------------------

    if document_names:

        selected_documents = st.multiselect(
            "Search scope",
            document_names,
            default=document_names
        )

    else:

        selected_documents = []


    # --------------------------------------------------------
    # Delete
    # --------------------------------------------------------

    if document_names:

        st.markdown(
            "### Document actions"
        )

        document_to_delete = st.selectbox(
            "Delete document",
            document_names,
            key="delete_document_select"
        )

        if st.button(
            "Delete selected document",
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

            if document:

                try:

                    storage_path = document.get(
                        "storage_path"
                    )

                    if storage_path:

                        delete_pdf(
                            storage_path
                        )

                    delete_document(
                        document_id=document["id"],
                        user_id=user_id
                    )

                    st.session_state.messages = []

                    st.success(
                        "Document deleted."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Delete failed: {e}"
                    )


# ============================================================
# TOP METRICS
# ============================================================

metric_1, metric_2, metric_3 = st.columns(
    3
)


with metric_1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">
                Documents
            </div>

            <div class="metric-value">
                {len(document_names)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with metric_2:

    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">
                Search
            </div>

            <div class="metric-value">
                Vector
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with metric_3:

    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-label">
                Model
            </div>

            <div class="metric-value">
                Gemini
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# ============================================================
# UPLOAD AREA
# ============================================================

st.markdown(
    """
    <div class="upload-card">

        <div class="section-label">
            Document ingestion
        </div>

        <div class="upload-title">
            Add engineering documents
        </div>

        <div class="upload-description">
            Upload PDF manuals, technical reports,
            specifications, research papers, or other
            engineering documents.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


uploaded_files = st.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True,
    key="pdf_uploader",
    label_visibility="collapsed"
)


# ============================================================
# PROCESS UPLOADS
# ============================================================

if uploaded_files:

    st.write("")

    process_button = st.button(
        "Process documents",
        type="primary"
    )

    if process_button:

        progress = st.progress(0)

        total = len(uploaded_files)

        processed_count = 0
        already_count = 0
        failed_count = 0

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            temp_path = None

            with st.status(
                f"Processing {uploaded_file.name}...",
                expanded=False
            ) as status:

                try:

                    file_bytes = (
                        uploaded_file.getvalue()
                    )

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf"
                    ) as temp_file:

                        temp_file.write(
                            file_bytes
                        )

                        temp_path = Path(
                            temp_file.name
                        )


                    result = ingest_uploaded_pdf(
                        pdf_path=temp_path,
                        user_id=user_id,
                        original_filename=(
                            uploaded_file.name
                        )
                    )


                    if (
                        result["status"]
                        == "processed"
                    ):

                        processed_count += 1

                        status.update(
                            label=(
                                f"Processed "
                                f"{uploaded_file.name}"
                            ),
                            state="complete"
                        )


                    elif (
                        result["status"]
                        == "already_indexed"
                    ):

                        already_count += 1

                        status.update(
                            label=(
                                f"Already indexed: "
                                f"{uploaded_file.name}"
                            ),
                            state="complete"
                        )


                    else:

                        failed_count += 1

                        status.update(
                            label=(
                                f"Unexpected result: "
                                f"{uploaded_file.name}"
                            ),
                            state="error"
                        )

                except Exception as e:

                    failed_count += 1

                    status.update(
                        label=(
                            f"Failed: "
                            f"{uploaded_file.name}"
                        ),
                        state="error"
                    )

                    st.error(
                        str(e)
                    )

                finally:

                    if (
                        temp_path
                        and temp_path.exists()
                    ):

                        try:
                            os.remove(
                                temp_path
                            )
                        except Exception:
                            pass

            progress.progress(
                (index + 1) / total
            )


        st.success(
            f"Processing finished — "
            f"{processed_count} processed, "
            f"{already_count} already indexed, "
            f"{failed_count} failed."
        )

        st.rerun()


# ============================================================
# MAIN WORKSPACE
# ============================================================

st.markdown(
    """
    <div class="workspace-card">

        <div class="section-label">
            Document intelligence
        </div>

        <div class="workspace-title">
            Ask your engineering documents
        </div>

        <div class="workspace-description">
            Search across the selected documents and
            get answers grounded in their content.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# EMPTY STATE
# ============================================================

if not document_names:

    st.info(
        "Upload a PDF above to start your workspace."
    )


# ============================================================
# CHAT HISTORY
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
    "Ask about your selected documents..."
)


# ============================================================
# ANSWER QUESTION
# ============================================================

if question:

    if not selected_documents:

        st.warning(
            "Select at least one document "
            "from the sidebar."
        )

        st.stop()


    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            question
        )


    st.session_state.messages.append({
        "role": "user",
        "content": question
    })


    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "Searching documents..."
        ):

            try:

                retrieved_chunks = retrieve_chunks(
                    question=question,
                    top_k=5,
                    sources=selected_documents,
                    user_id=user_id
                )

            except Exception as e:

                st.error(
                    f"Search failed: {e}"
                )

                st.stop()


        if not retrieved_chunks:

            answer = (
                "I couldn't find relevant information "
                "in the selected documents."
            )

            st.markdown(
                answer
            )

        else:

            with st.spinner(
                "Generating response..."
            ):

                try:

                    answer = generate_rag_answer(
                        question,
                        retrieved_chunks
                    )

                except Exception as e:

                    st.error(
                        f"Generation failed: {e}"
                    )

                    answer = (
                        "I couldn't generate an answer "
                        "right now."
                    )


            st.markdown(
                answer
            )


            # ------------------------------------------------
            # SOURCES
            # ------------------------------------------------

            unique_sources = set()

            for chunk in retrieved_chunks:

                source = chunk.get(
                    "source",
                    "Unknown"
                )

                page = chunk.get(
                    "page",
                    "?"
                )

                unique_sources.add(
                    (source, page)
                )


            if unique_sources:

                st.markdown(
                    "#### Sources"
                )

                for source, page in sorted(
                    unique_sources
                ):

                    st.markdown(
                        f"""
                        <span class="source-chip">
                            {source} · Page {page}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )


    # --------------------------------------------------------
    # SAVE MESSAGE
    # --------------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# ============================================================
# FOOTER
# ============================================================

st.write("")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#9ca3af;
        font-size:11px;
        padding:18px 0 5px 0;
    ">
        AeroMind AI · Engineering Intelligence Workspace
        &nbsp;·&nbsp;
        Supabase Vector Search
        &nbsp;·&nbsp;
        Gemini
    </div>
    """,
    unsafe_allow_html=True
)