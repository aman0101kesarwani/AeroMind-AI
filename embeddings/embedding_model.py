import os
import numpy as np

from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# Environment
# ============================================================

load_dotenv()


def get_gemini_api_key():
    """
    Get Gemini API key from:
    1. Streamlit Cloud Secrets
    2. Environment variables / .env
    """

    # Streamlit Cloud
    try:
        import streamlit as st

        key = st.secrets.get("GEMINI_API_KEY")

        if key:
            return key

    except Exception:
        pass

    # Local .env / environment
    key = os.getenv("GEMINI_API_KEY")

    if key:
        return key

    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Add it to .env locally or Streamlit Secrets."
    )


# ============================================================
# Gemini Client
# ============================================================

client = genai.Client(
    api_key=get_gemini_api_key()
)


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "gemini-embedding-001"

EMBEDDING_DIMENSION = 1024

BATCH_SIZE = 32


# ============================================================
# Generate Embeddings
# ============================================================

def generate_embeddings(texts):

    if not texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    all_embeddings = []

    for start in range(
        0,
        len(texts),
        BATCH_SIZE
    ):

        batch = texts[
            start:start + BATCH_SIZE
        ]

        result = client.models.embed_content(

            model=MODEL_NAME,

            contents=batch,

            config=types.EmbedContentConfig(

                output_dimensionality=
                    EMBEDDING_DIMENSION,

                task_type="RETRIEVAL_DOCUMENT"
            )
        )

        batch_embeddings = []

        for embedding in result.embeddings:

            vector = np.array(
                embedding.values,
                dtype=np.float32
            )

            # Normalize for cosine similarity
            norm = np.linalg.norm(vector)

            if norm > 0:

                vector = vector / norm

            batch_embeddings.append(vector)

        all_embeddings.extend(
            batch_embeddings
        )

    return np.array(
        all_embeddings,
        dtype=np.float32
    )