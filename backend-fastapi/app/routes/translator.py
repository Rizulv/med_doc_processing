# app/routes/translator.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.gemini_client import client

router = APIRouter()


class TranslateRequest(BaseModel):
    document_text: str
    target_language: str = "simple"  # simple, hindi, spanish, etc.


@router.post("/translate")
async def translate_medical_text(request: TranslateRequest):
    """
    Translate complex medical jargon to patient-friendly language

    Supported languages:
    - simple: ELI5 (Explain Like I'm 5) mode
    - hindi: Hindi translation
    - spanish: Spanish translation
    - etc.

    Returns: {translated_text, explanations[{term, simple, meaning}]}
    """
    result = client.translate_medical_terms(
        request.document_text,
        request.target_language
    )
    return result
