from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.gemini_client import client

router = APIRouter()


class ExtractCodesRequest(BaseModel):
    document_text: str
    document_type: Optional[str] = None


@router.post("/extract-codes")
async def extract_codes(request: ExtractCodesRequest):
    """
    Extract ICD-10 diagnostic codes from document
    
    Returns: {codes: [{code, description, confidence, evidence[]}]}
    """
    result = client.extract_codes(request.document_text, request.document_type)
    return result
