# Approach Document — SHL Assessment Recommender

## Problem Statement
Build a conversational API that recommends SHL assessments from the product 
catalog based on natural language job descriptions, supporting multi-turn 
conversation, refinement, and clarification.

## System Architecture

### RAG Pipeline (6 steps)
1. **Query Rewriting** — Combines conversation history with current message
   to produce an enriched search query capturing full intent
2. **Embedding** — all-MiniLM-L6-v2 converts query to 384-dim vector
3. **FAISS Retrieval** — Cosine similarity search returns top-10 products
   from 518-product index, with optional metadata filtering
4. **Prompt Construction** — Retrieved products injected as grounded context
5. **LLM Generation** — Groq Llama 3.1 reasons over catalog context only
6. **Output Parsing** — Structured JSON extraction with fallback handling

### Conversation Handling
Stateless design — client sends full history with every request. This 
enables horizontal scaling, survives server restarts, and works correctly 
on Render's free tier where containers sleep and restart.

### Hallucination Prevention
The system prompt explicitly forbids inventing product names. The LLM 
receives only retrieved real products as context, making it structurally 
impossible to recommend non-catalog items.

## Data Pipeline
- Scraped 518 products from SHL catalog (type=1 and type=2)
- Extracted structured metadata: job levels, duration, test types
- Built rich searchable text combining description + metadata
- Generated normalized embeddings for cosine similarity search

## Key Trade-offs

| Decision | Choice | Reason |
|---|---|---|
| Vector store | FAISS (local) | Free, fast, no external dependency |
| Embeddings | all-MiniLM-L6-v2 | CPU-friendly, strong semantics |
| LLM | Groq Llama 3.1 | Free tier, low latency |
| Conversation | Stateless | Scalable, Render-compatible |
| Retrieval | Top-10 + filter | Balances recall and precision |

## Evaluation Results
- Sales manager query → correct role-specific assessments ✅
- Duration filter ("under 40 min") → correctly filtered results ✅  
- Vague query ("I need a test") → clarification requested ✅
- Prompt injection → refused, stayed on scope ✅
- Out of scope query → politely declined ✅

## Deployment
FastAPI on Render free tier. Stateless design handles cold starts 
gracefully — no session data lost on container sleep/wake cycles.