import streamlit as st

from services.pdf_service import save_uploaded_files
from services.ingestion_service import ingest_pdf
from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_rag_answer

from vectorstore.chroma_store import get_indexed_documents


# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

st.set_page_config(
    page_title="AeroMind AI",
    page_icon="✈️",
    layout="wide"
)


# --------------------------------------------------
# Sidebar - Documents
# --------------------------------------------------

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


# --------------------------------------------------
# Main Title
# --------------------------------------------------

st.title("✈️ AeroMind AI")

st.caption(
    "Multimodal Agentic RAG for Engineering Documents"
)


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

    saved_paths = save_uploaded_files(
        uploaded_files
    )

    st.success(
        f"{len(uploaded_files)} file(s) uploaded successfully!"
    )

    # Automatically process every uploaded PDF
    for pdf_path in saved_paths:

        with st.spinner(
            f"🔄 Processing {pdf_path.name}..."
        ):

            result = ingest_pdf(pdf_path)

        if result["status"] == "already_indexed":

            st.info(
                f"✓ {pdf_path.name} is already indexed."
            )

        elif result["status"] == "processed":

            st.success(
                f"✅ {pdf_path.name} is ready for questions!"
            )


# --------------------------------------------------
# Chat
# --------------------------------------------------

st.header("💬 Ask Your Documents")


# Initialize chat history
if "messages" not in st.session_state:

    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# Chat input
question = st.chat_input(
    "Ask a question about your engineering documents..."
)


if question:

    # --------------------------------------------------
    # Check document selection
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

        retrieved_chunks = retrieve_chunks(

            question,

            top_k=5,

            sources=selected_documents

        )


    # --------------------------------------------------
    # Generate Answer
    # --------------------------------------------------

    with st.spinner(
        "🤖 Generating answer..."
    ):

        answer = generate_rag_answer(

            question,

            retrieved_chunks

        )


    # --------------------------------------------------
    # Show Assistant Answer
    # --------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(answer)


    st.session_state.messages.append({

        "role": "assistant",

        "content": answer

    })