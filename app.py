import streamlit as st
from pathlib import Path
import tempfile
import os
import uuid

from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer

from services.cloud_ingestion_service import ingest_uploaded_pdf

from vectorstore.supabase_vector_store import get_indexed_documents


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# USER ID
# ============================================================

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

user_id = st.session_state.user_id


# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at top center,
                #252632 0%,
                #17181e 42%,
                #101116 100%
            );
        color: #f5f5f7;
    }

    .main .block-container {
        max-width: 1180px;
        padding-top: 1rem;
        padding-bottom: 7rem;
    }

    /* Hide Streamlit default chrome */
    #MainMenu {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    footer {
        visibility: hidden;
    }


    /* =====================================================
       TOP NAVIGATION
       ===================================================== */

    .aero-nav {
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;

        padding: 0 24px;

        margin-bottom: 18px;

        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;

        background: rgba(30,31,39,0.82);

        box-shadow:
            0 10px 30px rgba(0,0,0,0.20);
    }

    .aero-logo {
        display: flex;
        align-items: center;
        gap: 10px;

        font-size: 18px;
        font-weight: 700;
        color: #ffffff;
    }

    .aero-plane {
        font-size: 24px;
    }

    .aero-nav-right {
        display: flex;
        align-items: center;
        gap: 24px;

        font-size: 13px;
        color: #b9bbc5;
    }

    .aero-nav-right span {
        cursor: default;
    }

    .aero-new-chat {
        padding: 8px 14px;

        border-radius: 8px;

        background: #ffffff;
        color: #17181e;

        font-size: 12px;
        font-weight: 700;
    }


    /* =====================================================
       SERVICE STATUS
       ===================================================== */

    .service-status {
        text-align: center;

        padding: 10px;

        border-top: 1px solid rgba(255,255,255,0.06);
        border-bottom: 1px solid rgba(255,255,255,0.06);

        color: #c6c7cf;

        font-size: 13px;
    }

    .service-active {
        color: #61d391;
        font-weight: 600;
    }


    /* =====================================================
       HERO
       ===================================================== */

    .hero {
        text-align: center;

        padding: 42px 20px 32px;

        border: 1px solid rgba(255,255,255,0.13);

        border-radius: 14px;

        background:
            linear-gradient(
                145deg,
                rgba(44,45,55,0.94),
                rgba(28,29,37,0.94)
            );

        box-shadow:
            0 18px 45px rgba(0,0,0,0.22);
    }

    .hero h1 {
        margin: 0;

        font-size: clamp(32px, 4vw, 48px);

        line-height: 1.12;

        color: #ffffff;

        letter-spacing: -1px;
    }

    .hero-subtitle {
        margin-top: 16px;

        color: #aeb0ba;

        font-size: 15px;

        line-height: 1.6;
    }

    .hero-icon {
        font-size: 28px;
        margin-left: 6px;
    }


    /* =====================================================
       SECTION TITLES
       ===================================================== */

    .section-title {
        display: flex;
        align-items: center;

        gap: 8px;

        margin-top: 28px;
        margin-bottom: 8px;

        font-size: 14px;
        font-weight: 700;

        color: #ffffff;
    }

    .section-description {
        color: #8f919d;

        font-size: 12px;

        margin-bottom: 12px;
    }


    /* =====================================================
       DOCUMENT LIBRARY
       ===================================================== */

    .document-library {
        padding: 16px;

        border-radius: 10px;

        background: #20222c;

        border: 1px solid rgba(255,255,255,0.07);

        color: #c5c7d0;

        font-size: 13px;
    }

    .document-library-empty {
        color: #75b7ff;
    }


    /* =====================================================
       UPLOAD AREA
       ===================================================== */

    .upload-helper {
        text-align: center;

        color: #aaaeba;

        font-size: 12px;

        margin: 14px 0;
    }

    div[data-testid="stFileUploader"] {
        border: 1px dashed rgba(255,255,255,0.28);

        border-radius: 10px;

        background: rgba(28,29,36,0.8);

        padding: 8px;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        border-radius: 8px;

        border: 1px solid rgba(255,255,255,0.15);

        background: #242631;

        color: #ffffff;

        font-weight: 600;

        min-height: 40px;
    }

    .stButton > button:hover {
        border-color: rgba(255,255,255,0.35);

        background: #30323f;

        color: #ffffff;
    }


    /* =====================================================
       CHAT
       ===================================================== */

    .chat-section {
        margin-top: 22px;

        padding-bottom: 20px;
    }

    div[data-testid="stChatMessage"] {
        background: rgba(34,35,44,0.75);

        border: 1px solid rgba(255,255,255,0.06);

        border-radius: 12px;

        padding: 10px 14px;

        margin-bottom: 10px;
    }

    div[data-testid="stChatInput"] {
        background: rgba(25,26,33,0.96);

        border: 1px solid rgba(255,255,255,0.18);

        border-radius: 10px;
    }


    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {
        border-radius: 9px;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .aero-footer {
        text-align: center;

        margin-top: 35px;

        padding: 18px;

        color: #646774;

        font-size: 11px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP NAVIGATION
# ============================================================

st.markdown(
    """
    <div class="aero-nav">

        <div class="aero-logo">
            <span class="aero-plane">✈️</span>
            <span>AeroMind</span>
        </div>

        <div class="aero-nav-right">
            <span>My Library</span>
            <span>AeroMind</span>
            <span>Account</span>
            <span class="aero-new-chat">New Chat</span>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SERVICE STATUS
# ============================================================

st.markdown(
    """
    <div class="service-status">
        Service Status:
        <span class="service-active">Active</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <h1>
            Pick a PDF.
            <br>
            AeroMind Analyzes.
            📄
            <br>
            Then Ask Questions.
        </h1>

        <div class="hero-subtitle">
            Upload your engineering document and let AeroMind
            retrieve accurate answers directly from it.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# GET USER DOCUMENTS
# ============================================================

try:

    indexed_documents = get_indexed_documents(
        user_id=user_id
    )

except Exception as e:

    indexed_documents = []

    st.error(
        "Unable to load your document library."
    )


# ============================================================
# DOCUMENT LIBRARY
# ============================================================

st.markdown(
    """
    <div class="section-title">
        📚 My Document Library
    </div>
    """,
    unsafe_allow_html=True,
)


if indexed_documents:

    st.markdown(
        f"""
        <div class="document-library">
            {len(indexed_documents)}
            document(s) available for this session.
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="document-library document-library-empty">
            No documents uploaded yet.
            Upload a PDF below to get started.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DOCUMENT SELECTION
# ============================================================

if indexed_documents:

    selected_documents = st.multiselect(
        "Search in:",
        indexed_documents,
        default=indexed_documents,
        label_visibility="collapsed",
    )

else:

    selected_documents = []


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    """
    <div class="section-title">
        📄 Upload a PDF
    </div>

    <div class="upload-helper">
        Upload a PDF and AeroMind will analyze it automatically.
    </div>
    """,
    unsafe_allow_html=True,
)


uploaded_files = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)


# ============================================================
# PROCESS BUTTON
# ============================================================

if uploaded_files:

    if st.button(
        "🚀 Process Documents",
        type="primary",
        use_container_width=False,
    ):

        processed_any = False

        for uploaded_file in uploaded_files:

            temp_path = None

            with st.status(
                f"Processing {uploaded_file.name}...",
                expanded=True,
            ) as status:

                try:

                    # ----------------------------------------
                    # Temporary PDF
                    # ----------------------------------------

                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=".pdf",
                    ) as temp_file:

                        temp_file.write(
                            uploaded_file.getbuffer()
                        )

                        temp_path = Path(
                            temp_file.name
                        )


                    st.write(
                        "📖 Reading PDF..."
                    )


                    # ----------------------------------------
                    # CLOUD INGESTION
                    # ----------------------------------------

                    result = ingest_uploaded_pdf(
                        temp_path,
                        user_id=user_id,
                    )


                    # ----------------------------------------
                    # RESULT
                    # ----------------------------------------

                    if result["status"] == "already_indexed":

                        st.info(
                            f"{uploaded_file.name} "
                            "is already indexed."
                        )

                        status.update(
                            label=f"Already indexed: {uploaded_file.name}",
                            state="complete",
                        )


                    elif result["status"] == "processed":

                        st.write(
                            "🧠 Generating embeddings..."
                        )

                        st.success(
                            f"✅ {uploaded_file.name} "
                            "is ready for questions!"
                        )

                        st.caption(
                            f"Pages: {result.get('pages', 0)} | "
                            f"Chunks: {result.get('chunks', 0)}"
                        )

                        processed_any = True

                        status.update(
                            label=f"Completed: {uploaded_file.name}",
                            state="complete",
                        )


                    else:

                        st.warning(
                            f"Unexpected result: {result}"
                        )

                        status.update(
                            label=f"Finished with warning: {uploaded_file.name}",
                            state="error",
                        )


                except Exception as e:

                    st.error(
                        f"❌ Failed to process "
                        f"{uploaded_file.name}: {e}"
                    )

                    status.update(
                        label=f"Failed: {uploaded_file.name}",
                        state="error",
                    )


                finally:

                    # ----------------------------------------
                    # REMOVE LOCAL TEMP FILE
                    # ----------------------------------------

                    if (
                        temp_path
                        and temp_path.exists()
                    ):

                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass


        # --------------------------------------------
        # REFRESH AFTER PROCESSING
        # --------------------------------------------

        if processed_any:

            st.success(
                "🎉 Document processing completed."
            )

            st.rerun()


# ============================================================
# CHAT SECTION
# ============================================================

st.markdown(
    """
    <div class="chat-section">

        <div class="section-title">
            💬 Ask AeroMind
        </div>

        <div class="section-description">
            Ask questions about the engineering documents
            available in your document library.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
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
    "Ask AeroMind about your document..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # CHECK DOCUMENTS
    # --------------------------------------------------------

    if not selected_documents:

        st.warning(
            "⚠️ Please upload and process a PDF first."
        )

        st.stop()


    # --------------------------------------------------------
    # USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(question)


    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )


    # --------------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------------

    with st.spinner(
        "🔎 Searching your documents..."
    ):

        try:

            retrieved_chunks = retrieve_chunks(

                question,

                top_k=5,

                sources=selected_documents,

                user_id=user_id,

            )

        except Exception as e:

            st.error(
                f"❌ Retrieval failed: {e}"
            )

            st.stop()


    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not retrieved_chunks:

        answer = (
            "I couldn't find relevant information "
            "in the selected documents."
        )


    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    else:

        with st.spinner(
            "🤖 Generating answer..."
        ):

            try:

                answer = generate_rag_answer(
                    question,
                    retrieved_chunks,
                )

            except Exception as e:

                answer = (
                    "⚠️ I couldn't generate an answer "
                    "right now. Please try again."
                )


    # --------------------------------------------------------
    # SHOW ANSWER
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)


    # --------------------------------------------------------
    # SAVE ANSWER
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="aero-footer">
        AeroMind AI · Engineering Document Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)