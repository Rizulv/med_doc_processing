from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.anthropic_client import client

router = APIRouter()


class SummarizeRequest(BaseModel):
    document_text: str
    document_type: Optional[str] = None
    codes: Optional[List[Dict[str, Any]]] = None


@router.post("/summarize")
async def summarize_document(request: SummarizeRequest):
    """
    Generate clinical summary for document
    
    Returns: {summary, confidence, evidence[]}
    """
    result = client.summarize(
        request.document_text,
        request.document_type,
        request.codes
    )
    return result
