import faiss
import json
import numpy as np
from app.config import settings

# Load index and metadata once at startup
_index = None
_metadata = None

def load_store():
    global _index, _metadata
    if _index is None:
        print(f"Loading FAISS index from {settings.faiss_index_path}")
        _index = faiss.read_index(settings.faiss_index_path)
        with open(settings.metadata_path, "r", encoding="utf-8") as f:
            _metadata = json.load(f)
        print(f"  Loaded {_index.ntotal} vectors, {len(_metadata)} products")

def search(query_vector: np.ndarray, k: int = 10) -> list[dict]:
    """
    Search FAISS for top-k most similar products.
    Returns list of product metadata dicts.
    """
    load_store()

    distances, indices = _index.search(query_vector, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:  # FAISS returns -1 for empty slots
            continue
        product = _metadata[idx].copy()
        product["relevance_score"] = float(dist)
        results.append(product)

    return results

def search_with_filter(
    query_vector: np.ndarray,
    k: int = 10,
    job_level: str | None = None,
    max_duration: int | None = None,
    remote_only: bool = False
) -> list[dict]:
    """
    Search FAISS then apply metadata filters.
    Fetch 3x candidates to ensure enough survive filtering.
    """
    # Fetch more candidates to account for filtering
    candidates = search(query_vector, k=min(k * 3, 50))

    filtered = []
    for product in candidates:
        # Job level filter
        if job_level:
            levels_lower = [l.lower() for l in product["job_levels"]]
            if job_level.lower() not in " ".join(levels_lower):
                continue

        # Duration filter
        if max_duration and product["duration_minutes"]:
            if product["duration_minutes"] > max_duration:
                continue

        # Remote testing filter
        if remote_only and not product["remote_testing"]:
            continue

        filtered.append(product)

        if len(filtered) >= k:
            break

    # If filtering removed too many, fall back to unfiltered
    if len(filtered) < 3:
        return candidates[:k]

    return filtered