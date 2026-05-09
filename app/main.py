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

# Add this temporary test route to app/main.py
@app.get("/test-pipeline")
def test_pipeline():
    from app.pipeline import run_pipeline
    result = run_pipeline(
        message="I need an assessment for a sales manager role",
        conversation_history=[]
    )
    return result