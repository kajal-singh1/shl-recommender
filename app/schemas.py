from pydantic import BaseModel, Field
from typing import Optional

class ConversationTurn(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: list[ConversationTurn] = Field(default=[])

class AssessmentRecommendation(BaseModel):
    name: str
    url: str
    reason: str
    duration_minutes: Optional[int] = None
    job_levels: list[str] = []
    test_types: list[str] = []

class ChatResponse(BaseModel):
    recommendations: list[AssessmentRecommendation]
    clarification_needed: bool
    clarification_question: Optional[str] = None
    reasoning: str