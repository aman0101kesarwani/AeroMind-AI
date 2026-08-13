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
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# USER IDENTITY
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
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
    ====================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at top,
                rgba(70, 70, 90, 0.30),
                transparent 45%
            ),
            #17181d;
        color: #f5f5f7;
    }

    .main .block-container {
        max-width: 900px;
        padding-top: 0rem;
        padding-bottom: 3rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }


    /* ======================================================
       HIDE STREAMLIT DEFAULT ELEMENTS
       ====================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* ======================================================
       TOP NAVIGATION
       ====================================================== */

    .aero-navbar {
        width: 100%;
        height: 62px;

        display: flex;
        align-items: center;
        justify-content: space-between;

        padding: 0 22px;

        background: rgba(30, 30, 36, 0.95);

        border-bottom:
            1px solid rgba(255,255,255,0.10);

        margin-bottom: 18px;

        border-radius: 0 0 12px 12px;

        box-sizing: border-box;
    }

    .aero-logo {
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.3px;
    }

    .aero-nav-right {
        display: flex;
        gap: 24px;
        align-items: center;

        color: #d7d7dc;

        font-size: 13px;
    }

    .aero-status {
        color: #7bd88f;
    }


    /* ======================================================
       MAIN CARD
       ====================================================== */

    .aero-card {
        width: 100%;

        background:
            linear-gradient(
                145deg,
                rgba(65,65,76,0.90),
                rgba(40,40,48,0.94)
            );

        border:
            1px solid rgba(255,255,255,0.14);

        border-radius: 14px;

        box-shadow:
            0 18px 60px rgba(0,0,0,0.30);

        overflow: hidden;
    }


    /* ======================================================
       SERVICE STATUS
       ====================================================== */

    .service-status {
        text-align: center;

        padding: 10px;

        font-size: 12px;

        color: #eeeeee;

        border-bottom:
            1px solid rgba(255,255,255,0.10);
    }

    .service-active {
        color: #72d88a;
    }


    /* ======================================================
       HERO
       ====================================================== */

    .hero {
        text-align: center;

        padding:
            45px 30px 25px 30px;
    }

    .hero h1 {
        margin: 0;

        font-size: 36px;

        line-height: 1.12;

        font-weight: 700;

        letter-spacing: -1px;
    }

    .hero p {
        margin-top: 14px;

        color: #b9b9c1;

        font-size: 14px;
    }


    /* ======================================================
       UPLOAD AREA
       ====================================================== */

    .upload-info {
        text-align: center;

        margin:
            5px auto 20px auto;

        color: #c9c9cf;

        font-size: 13px;
    }


    /* ======================================================
       BUTTONS
       ====================================================== */

    .stButton > button {

        border-radius: 8px;

        border:
            1px solid rgba(255,255,255,0.22);

        background:
            linear-gradient(
                180deg,
                #ffffff,
                #e8e8ea
            );

        color: #15151a;

        font-weight: 600;

        min-height: 42px;

        transition: all 0.2s ease;
    }

    .stButton > button:hover {

        transform: translateY(-1px);

        border-color: #ffffff;

        box-shadow:
            0 6px 20px rgba(0,0,0,0.25);
    }


    /* ======================================================
       PRIMARY PROCESS BUTTON
       ====================================================== */

    .process-button button {

        background:
            linear-gradient(
                135deg,
                #ffffff,
                #dddddf
            ) !important;

        color: #17171b !important;

        border:
            1px solid #ffffff !important;

        font-weight: 700 !important;
    }


    /* ======================================================
       FILE UPLOADER
       ====================================================== */

    [data-testid="stFileUploader"] {

        background:
            rgba(25,25,30,0.45);

        border:
            1px dashed rgba(255,255,255,0.30);

        border-radius: 10px;

        padding: 8px;
    }

    [data-testid="stFileUploaderDropzone"] {

        background:
            rgba(255,255,255,0.025);

        border-radius: 8px;
    }


    /* ======================================================
       DOCUMENT LIBRARY
       ====================================================== */

    .library-title {

        font-size: 14px;

        font-weight: 600;

        color: #eeeeef;

        margin-top: 5px;

        margin-bottom: 8px;
    }


    /* ======================================================
       CHAT AREA
       ====================================================== */

    .chat-title {

        text-align: left;

        font-size: 14px;

        font-weight: 600;

        color: #eeeeee;

        margin:
            10px 0 10px 0;
    }


    /* ======================================================
       CHAT MESSAGES
       ====================================================== */

    [data-testid="stChatMessage"] {

        background:
            rgba(255,255,255,0.035);

        border:
            1px solid rgba(255,255,255,0.08);

        border-radius: 10px;

        margin-bottom: 8px;
    }


    /* ======================================================
       CHAT INPUT
       ====================================================== */

    [data-testid="stChatInput"] {

        margin-top: 12px;
    }

    [data-testid="stChatInput"] textarea {

        background:
            rgba(35,35,42,0.95) !important;

        color: #ffffff !important;

        border:
            1px solid rgba(255,255,255,0.35) !important;

        border-radius: 10px !important;
    }


    /* ======================================================
       INFO / SUCCESS / WARNING
       ====================================================== */

    [data-testid="stAlert"] {

        border-radius: 9px;
    }


    /* ======================================================
       DIVIDER
       ====================================================== */

    .aero-divider {

        height: 1px;

        background:
            rgba(255,255,255,0.10);

        margin:
            8px 0 20px 0;
    }


    /* ======================================================
       FOOTER
       ====================================================== */

    .aero-footer {

        text-align: center;

        color: #777780;

        font-size: 11px;

        padding: 22px 0 5px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP NAVBAR
# ============================================================

st.markdown(
    """
    <div class="aero-navbar">

        <div class="aero-logo">
            ✈️ AeroMind
        </div>

        <div class="aero-nav-right">
            <span>My Library</span>
            <span>AeroMind</span>
            <span>Account</span>
            <span class="aero-status">● Active</span>
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MAIN CARD
# ============================================================

st.markdown(
    """
    <div class="aero-card">

        <div class="service-status">
            Service Status:
            <span class="service-active">Active</span>
        </div>

        <div class="hero">

            <h1>
                Pick a PDF.<br>
                AeroMind Analyzes.<br>
                Then Ask Questions. 📄
            </h1>

            <p>
                Upload your engineering document and let AeroMind
                retrieve answers directly from it.
            </p>

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DOCUMENTS FROM SUPABASE
# ============================================================

try:

    indexed_documents = get_indexed_documents(
        user_id=user_id
    )

except Exception as e:

    indexed_documents = []

    st.error(
        f"Unable to load your document library: {e}"
    )


# ============================================================
# DOCUMENT LIBRARY
# ============================================================

st.markdown(
    '<div class="library-title">📚 My Document Library</div>',
    unsafe_allow_html=True,
)


if indexed_documents:

    selected_documents = st.multiselect(
        "Select documents to search",
        indexed_documents,
        default=indexed_documents,
        label_visibility="collapsed",
    )

else:

    selected_documents = []

    st.info(
        "No documents uploaded yet. Upload a PDF below to get started."
    )


# ============================================================
# DIVIDER
# ============================================================

st.markdown(
    '<div class="aero-divider"></div>',
    unsafe_allow_html=True,
)


# ============================================================
# UPLOAD SECTION
# ============================================================

st.markdown(
    """
    <div class="upload-info">
        📄 Upload a PDF and AeroMind will automatically analyze it.
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

    st.markdown(
        '<div class="process-button">',
        unsafe_allow_html=True,
    )

    process_clicked = st.button(
        "⬆️  ANALYZE PDF",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    if process_clicked:

        processed_any = False

        for uploaded_file in uploaded_files:

            with st.spinner(
                f"Analyzing {uploaded_file.name}..."
            ):

                temp_path = None

                try:

                    # ------------------------------------------
                    # TEMPORARY PDF
                    # ------------------------------------------

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

                    # ------------------------------------------
                    # EXISTING CLOUD INGESTION
                    # ------------------------------------------

                    result = ingest_uploaded_pdf(
                        temp_path,
                        user_id=user_id,
                    )

                    # ------------------------------------------
                    # RESULT
                    # ------------------------------------------

                    if result.get("status") == "already_indexed":

                        st.info(
                            f"✓ {uploaded_file.name} "
                            "is already available."
                        )

                        processed_any = True

                    elif result.get("status") == "processed":

                        st.success(
                            f"✅ {uploaded_file.name} "
                            "has been analyzed successfully."
                        )

                        st.caption(
                            f"Pages: {result.get('pages', 0)}  •  "
                            f"Chunks: {result.get('chunks', 0)}"
                        )

                        processed_any = True

                    else:

                        st.warning(
                            f"Unexpected result for "
                            f"{uploaded_file.name}: {result}"
                        )

                except Exception as e:

                    st.error(
                        f"❌ Could not analyze "
                        f"{uploaded_file.name}: {e}"
                    )

                finally:

                    # ------------------------------------------
                    # REMOVE TEMPORARY LOCAL FILE
                    # ------------------------------------------

                    if (
                        temp_path is not None
                        and temp_path.exists()
                    ):

                        try:
                            os.remove(temp_path)

                        except Exception:
                            pass

        # ----------------------------------------------
        # REFRESH DOCUMENT LIBRARY
        # ----------------------------------------------

        if processed_any:

            st.success(
                "Your document is now ready for questions."
            )

            st.rerun()


# ============================================================
# CHAT SECTION
# ============================================================

st.markdown(
    '<div class="chat-title">💬 Ask AeroMind</div>',
    unsafe_allow_html=True,
)


# ============================================================
# EXISTING CHAT HISTORY
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
# QUESTION PROCESSING
# ============================================================

if question:

    # --------------------------------------------------------
    # DOCUMENT CHECK
    # --------------------------------------------------------

    if not selected_documents:

        st.warning(
            "Please upload and analyze a PDF first."
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
    # RETRIEVAL
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
                f"❌ Document search failed: {e}"
            )

            st.stop()


    # --------------------------------------------------------
    # NO RESULTS
    # --------------------------------------------------------

    if not retrieved_chunks:

        answer = (
            "I couldn't find relevant information "
            "in your selected documents."
        )


    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    else:

        with st.spinner(
            "🤖 AeroMind is thinking..."
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
    # ASSISTANT MESSAGE
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)


    # --------------------------------------------------------
    # SAVE MESSAGE
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
        AeroMind AI • Engineering Document Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)