def rewrite_query(message: str, conversation_history: list[dict]) -> str:
    """
    Combine conversation history with current message into
    a single enriched query for FAISS retrieval.

    This is intentionally simple and fast — no LLM call needed.
    We just concatenate meaningful context.
    """
    if not conversation_history:
        return message

    # Extract user turns from history (ignore assistant turns for query)
    user_turns = [
        turn["content"]
        for turn in conversation_history
        if turn["role"] == "user"
    ]

    # Take last 3 user turns + current message for context
    recent_context = user_turns[-3:] + [message]
    enriched = " ".join(recent_context)

    return enriched