# app/routes/chat.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.claude_client import client

router = APIRouter()


class ChatRequest(BaseModel):
    document_text: str
    question: str
    conversation_history: Optional[list] = None


@router.post("/chat")
async def chat_with_document(request: ChatRequest):
    """
    Ask questions about your medical document

    Examples:
    - "What does my cholesterol result mean?"
    - "Should I be worried about the elevated WBC?"
    - "Explain my X-ray findings in simple terms"

    Returns: {answer, confidence, sources: [quoted text from document]}
    """
    if not client.use_claude:
        return {
            "answer": "Chat feature requires Claude API to be configured.",
            "confidence": 0.0,
            "sources": []
        }

    # Build context from conversation history
    context = ""
    if request.conversation_history:
        context = "\n".join([
            f"Q: {msg['question']}\nA: {msg['answer']}"
            for msg in request.conversation_history[-3:]  # Last 3 exchanges
        ])

    prompt = f"""You are a helpful medical AI assistant. Answer the patient's question about their medical document.

Requirements:
1. Use ONLY information from the document provided
2. Explain in simple, patient-friendly language
3. If you're not sure, say so
4. Quote specific text from the document as sources
5. Be empathetic and reassuring when appropriate

Document:
{request.document_text}

{f"Previous conversation:{context}" if context else ""}

Patient's question: {request.question}

Return JSON:
{{
  "answer": "Your detailed, friendly answer here",
  "confidence": 0.85,
  "sources": ["Quoted text from document"],
  "follow_up_questions": ["Suggested next question 1", "Suggested next question 2"]
}}"""

    try:
        result = client._call_json(prompt, "")

        # Ensure required fields
        if "answer" not in result:
            result["answer"] = "I couldn't understand the document well enough to answer that."
        if "confidence" not in result:
            result["confidence"] = 0.5
        if "sources" not in result:
            result["sources"] = []

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")
