# SHL Assessment Recommender

A conversational RAG-based API that recommends SHL assessments for hiring needs.

## Live API
- **Base URL:** https://your-url.onrender.com
- **Health:** GET /health
- **Chat:** POST /chat
- **Docs:** GET /docs

## Architecture
- **FastAPI** — stateless REST API
- **FAISS** — vector similarity search over 518 SHL products
- **HuggingFace** — all-MiniLM-L6-v2 embeddings
- **Groq (Llama 3.1)** — grounded recommendation generation
- **RAG pipeline** — retrieval-augmented, hallucination-prevented

## Quick Start
```bash
git clone https://github.com/YOUR_USERNAME/shl-recommender
cd shl-recommender
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Add GROQ_API_KEY to .env
uvicorn app.main:app --reload
```

## API Usage
```bash
curl -X POST "https://your-url.onrender.com/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need an assessment for a sales manager role",
    "conversation_history": []
  }'
```

## Example Response
```json
{
  "recommendations": [
    {
      "name": "Sales Manager Solution",
      "url": "https://www.shl.com/products/product-catalog/view/sales-manager-solution/",
      "reason": "Designed for entry to mid-level sales leadership positions",
      "duration_minutes": 63,
      "job_levels": ["Front Line Manager", "Manager"],
      "test_types": ["N/A"]
    }
  ],
  "clarification_needed": false,
  "clarification_question": null,
  "reasoning": "Recommended assessments specific to sales leadership roles."
}
```

## Key Design Decisions
- **Stateless API** — conversation history sent with every request
- **FAISS over hosted vector DB** — zero cost, works on Render free tier
- **Query rewriting** — enriches queries using conversation history
- **Behavior probes handled** — vague queries trigger clarification
- **Hallucination prevention** — LLM only picks from retrieved catalog