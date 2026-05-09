from app.utils.query_rewriter import rewrite_query
from app.retriever.embedder import embed_query
from app.retriever.faiss_store import search
from app.llm.prompts import build_prompt
from app.llm.groq_client import call_llm
from app.llm.parser import parse_llm_response
from app.config import settings

def run_pipeline(
    message: str,
    conversation_history: list[dict]
) -> dict:
    """
    Full 6-step RAG pipeline.

    Step 1: Rewrite query using conversation history
    Step 2: Embed the enriched query
    Step 3: Retrieve top-k products from FAISS
    Step 4: Build grounded prompt
    Step 5: Call Groq LLM
    Step 6: Parse and return structured response
    """

    # Step 1 — Query rewriting
    enriched_query = rewrite_query(message, conversation_history)

    # Step 2 — Embed
    query_vector = embed_query(enriched_query)

    # Step 3 — Retrieve from FAISS
    retrieved_products = search(query_vector, k=settings.top_k)

    # Step 4 — Build prompt
    messages = build_prompt(
        query=message,
        retrieved_products=retrieved_products,
        conversation_history=conversation_history
    )

    # Step 5 — Call LLM
    raw_response = call_llm(messages)

    # Step 6 — Parse response
    result = parse_llm_response(raw_response)

    return result