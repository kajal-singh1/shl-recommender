import json
import re

def parse_llm_response(raw_response: str) -> dict:
    """
    Parse LLM text output into structured dict.
    Handles common LLM formatting issues.
    """
    # Strip markdown code fences if present
    clean = raw_response.strip()
    clean = re.sub(r"^```json\s*", "", clean)
    clean = re.sub(r"^```\s*", "", clean)
    clean = re.sub(r"\s*```$", "", clean)
    clean = clean.strip()

    try:
        parsed = json.loads(clean)
    except json.JSONDecodeError:
        # Attempt to extract JSON from surrounding text
        match = re.search(r"\{.*\}", clean, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
            except json.JSONDecodeError:
                return _fallback_response("Could not parse LLM response.")
        else:
            return _fallback_response("No JSON found in LLM response.")

    # Validate and fill required fields
    return {
        "recommendations": parsed.get("recommendations", []),
        "clarification_needed": parsed.get("clarification_needed", False),
        "clarification_question": parsed.get("clarification_question", None),
        "reasoning": parsed.get("reasoning", "")
    }


def _fallback_response(reason: str) -> dict:
    """Safe fallback when parsing fails."""
    return {
        "recommendations": [],
        "clarification_needed": True,
        "clarification_question": "Could you rephrase your request?",
        "reasoning": f"System error: {reason}"
    }