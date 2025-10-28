from fastapi import APIRouter
from pydantic import BaseModel
from app.services.anthropic_client import client

router = APIRouter()


class ClassifyRequest(BaseModel):
    document_text: str


@router.post("/classify")
async def classify_document(request: ClassifyRequest):
    """
    Classify a document into one of 5 types
    
    Returns: {document_type, confidence, rationale, evidence[]}
    """
    result = client.classify(request.document_text)
    return result
