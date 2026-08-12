import streamlit as st
import numpy as np

from sentence_transformers import SentenceTransformer


# ============================================================
# Model configuration
# ============================================================

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"

EMBEDDING_DIMENSION = 1024

BATCH_SIZE = 8


# ============================================================
# Load model once
# ============================================================

@st.cache_resource(
    show_spinner=False
)
def load_embedding_model():

    model = SentenceTransformer(
        MODEL_NAME,
        device="cpu",
        trust_remote_code=True
    )

    return model


# ============================================================
# Generate embeddings
# ============================================================

def generate_embeddings(texts):

    if not texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    model = load_embedding_model()

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    return embeddings