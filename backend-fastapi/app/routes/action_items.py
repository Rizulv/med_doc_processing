# app/routes/action_items.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.services.claude_client import client

router = APIRouter()


class ActionItemsRequest(BaseModel):
    document_text: str
    codes: Optional[List[Dict[str, Any]]] = None


@router.post("/action-items")
async def extract_action_items(request: ActionItemsRequest):
    """
    Extract actionable items from medical document

    Returns:
    {
      action_items: ["Schedule follow-up", "Bring previous X-ray"],
      questions: ["Ask doctor about elevated WBC"],
      reminders: ["Take medication twice daily"],
      urgency: "routine|urgent|emergency"
    }
    """
    result = client.extract_action_items(
        request.document_text,
        request.codes or []
    )
    return result
