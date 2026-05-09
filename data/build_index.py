import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

CATALOG_PATH = "data/catalog.json"
INDEX_PATH = "indexes/faiss.index"
METADATA_PATH = "indexes/metadata.json"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def load_catalog(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_index():
    # ── 1. Load catalog ──────────────────────────────────────────
    print("Loading catalog...")
    products = load_catalog(CATALOG_PATH)
    print(f"  {len(products)} products loaded")

    # ── 2. Extract texts to embed ────────────────────────────────
    texts = [p["searchable_text"] for p in products]
    print(f"  {len(texts)} texts prepared for embedding")

    # ── 3. Load embedding model ──────────────────────────────────
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    print("  (First run downloads ~80MB — normal)")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # ── 4. Generate embeddings ───────────────────────────────────
    print("\nGenerating embeddings...")
    print("  This takes 1-3 minutes for 518 products...")
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True  # critical for cosine similarity
    )
    print(f"  Embedding shape: {embeddings.shape}")
    # Expected: (518, 384) — 518 products, 384 dimensions

    # ── 5. Build FAISS index ─────────────────────────────────────
    print("\nBuilding FAISS index...")
    dimension = embeddings.shape[1]  # 384

    # IndexFlatIP = Inner Product (dot product on normalized vectors = cosine similarity)
    # This is the correct index type for normalized embeddings
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings.astype(np.float32))
    print(f"  Index built with {index.ntotal} vectors")

    # ── 6. Save index to disk ────────────────────────────────────
    os.makedirs("indexes", exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    print(f"  FAISS index saved to {INDEX_PATH}")

    # ── 7. Save metadata parallel to index ──────────────────────
    # We store the full product metadata so at retrieval time
    # we can look up product[i] using the FAISS result index i
    metadata = []
    for product in products:
        metadata.append({
            "name": product["name"],
            "url": product["url"],
            "catalog_type": product["catalog_type"],
            "description": product["clean_description"],
            "job_levels": product["job_levels"],
            "test_types": product["test_types"],
            "duration_minutes": product["duration_minutes"],
            "remote_testing": product["remote_testing"],
            "adaptive_irt": product["adaptive_irt"],
            "searchable_text": product["searchable_text"]
        })

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Metadata saved to {METADATA_PATH}")

    # ── 8. Verify with a test query ──────────────────────────────
    print("\nVerifying index with test query...")
    test_query = "personality assessment for sales manager leadership"
    query_embedding = model.encode(
        [test_query],
        normalize_embeddings=True,
        convert_to_numpy=True
    )
    distances, indices = index.search(query_embedding.astype(np.float32), k=5)

    print(f"\nTop 5 results for: '{test_query}'")
    print("-" * 60)
    for rank, (dist, idx) in enumerate(zip(distances[0], indices[0]), 1):
        product = metadata[idx]
        print(f"{rank}. {product['name']}")
        print(f"   Score: {dist:.4f} | Levels: {product['job_levels'][:2]}")

    print("\n✅ Index built and verified successfully!")
    print(f"   Total vectors: {index.ntotal}")
    print(f"   Vector dimensions: {dimension}")

if __name__ == "__main__":
    build_index()