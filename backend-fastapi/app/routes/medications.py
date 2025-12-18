# app/routes/medications.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.gemini_client import client

router = APIRouter()


class MedicationRequest(BaseModel):
    document_text: str


class InteractionCheckRequest(BaseModel):
    medications: List[str]


@router.post("/extract-medications")
async def extract_medications(request: MedicationRequest):
    """
    Extract medications from medical document

    Returns: {medications: [{name, dosage, frequency, instructions}]}
    """
    if not client.use_gemini:
        return {"medications": [], "error": "Gemini API not configured"}

    prompt = """Extract ALL medications mentioned in this document.

For each medication, provide:
- name: medication name
- dosage: amount (e.g., "500mg", "10 units")
- frequency: how often (e.g., "twice daily", "as needed")
- instructions: any special instructions

Return JSON:
{
  "medications": [
    {
      "name": "Metformin",
      "dosage": "500mg",
      "frequency": "twice daily",
      "instructions": "Take with meals"
    }
  ]
}"""

    try:
        result = client._call_json(prompt, request.document_text)
        return result
    except Exception as e:
        return {"medications": [], "error": str(e)}


@router.post("/check-interactions")
async def check_medication_interactions(request: InteractionCheckRequest):
    """
    Check for drug interactions between medications

    Returns: {interactions: [{severity, description, medications_involved}], warnings: []}
    """
    if not client.use_gemini:
        return {"interactions": [], "warnings": [], "error": "Gemini API not configured"}

    meds_text = ", ".join(request.medications)
    prompt = f"""Check for drug interactions between these medications: {meds_text}

For each interaction found, provide:
- severity: "mild" | "moderate" | "severe"
- description: what happens
- medications_involved: which drugs interact
- recommendation: what to do

Return JSON:
{{
  "interactions": [
    {{
      "severity": "moderate",
      "description": "May increase risk of hypoglycemia",
      "medications_involved": ["Metformin", "Insulin"],
      "recommendation": "Monitor blood sugar closely"
    }}
  ],
  "warnings": ["Consult your doctor before making changes"],
  "safe_to_take_together": false
}}"""

    try:
        result = client._call_json(prompt, "")
        return result
    except Exception as e:
        return {"interactions": [], "warnings": [str(e)], "error": str(e)}
