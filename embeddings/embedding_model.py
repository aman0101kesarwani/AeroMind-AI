from sentence_transformers import SentenceTransformer


model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")


def generate_embeddings(texts):

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    return embeddings