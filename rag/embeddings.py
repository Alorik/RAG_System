from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def create_embeddings(texts: list[str]):
    """Create embeddings for a list of catalogue texts."""
    return model.encode(texts, normalize_embeddings=True)