from app.utils.query_rewriter import rewrite_query
from app.retriever.embedder import embed_query
from app.retriever.faiss_store import search, search_with_filter
from app.llm.prompts import build_prompt
from app.llm.groq_client import call_llm
from app.llm.parser import parse_llm_response
from app.config import settings
import re

def extract_duration_constraint(message: str) -> int | None:
    """Extract max duration if user specifies one."""
    match = re.search(
        r"under\s+(\d+)\s*min|less\s+than\s+(\d+)\s*min|(\d+)\s*min(?:utes?)?\s+or\s+less",
        message, re.IGNORECASE
    )
    if match:
        val = next(v for v in match.groups() if v is not None)
        return int(val)
    return None

def run_pipeline(
    message: str,
    conversation_history: list[dict]
) -> dict:

    # Step 1 — Query rewriting
    enriched_query = rewrite_query(message, conversation_history)

    # Step 2 — Embed
    query_vector = embed_query(enriched_query)

    # Step 3 — Retrieve with optional duration filter
    max_duration = extract_duration_constraint(message)

    if max_duration:
        retrieved_products = search_with_filter(
            query_vector,
            k=settings.top_k,
            max_duration=max_duration
        )
    else:
        retrieved_products = search(query_vector, k=settings.top_k)

    # Step 4 — Build prompt
    messages = build_prompt(
        query=message,
        retrieved_products=retrieved_products,
        conversation_history=conversation_history
    )

    # Step 5 — Call LLM
    raw_response = call_llm(messages)

    # Step 6 — Parse
    result = parse_llm_response(raw_response)

    return result