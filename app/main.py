from fastapi import FastAPI, HTTPException
from app.config import settings
from app.schemas import ChatRequest, ChatResponse
from app.pipeline import run_pipeline

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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        history = [
            {"role": turn.role, "content": turn.content}
            for turn in request.conversation_history
        ]
        result = run_pipeline(
            message=request.message,
            conversation_history=history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))