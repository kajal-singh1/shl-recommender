from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="SHL Assessment Recommender",
    description="Conversational RAG-based SHL product recommender",
    version="1.0.0"
)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": settings.model_name,
        "embedding_model": settings.embedding_model
    }