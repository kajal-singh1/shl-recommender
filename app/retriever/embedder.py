from sentence_transformers import SentenceTransformer
import numpy as np
import torch
from app.config import settings

_model = None

def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print(f"Loading embedding model: {settings.embedding_model}")
        # Explicitly use CPU to avoid meta tensor issue on Windows
        _model = SentenceTransformer(
            settings.embedding_model,
            device="cpu"
        )
    return _model

def embed_query(text: str) -> np.ndarray:
    model = get_model()
    embedding = model.encode(
        [text],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    return embedding.astype(np.float32)