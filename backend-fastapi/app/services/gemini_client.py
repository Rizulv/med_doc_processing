# app/services/gemini_client.py
import json
import re
from typing import Any, Dict, List

import google.generativeai as genai
from app.config import settings


def _parse_json_from_response(text: str) -> Dict[str, Any]:
    """Parse JSON from Gemini response text"""
    try:
        return json.loads(text)
    except Exception:
        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass

        # Try to find any JSON object
        m = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass

        # Last resort: return raw text
        return {"raw": text, "error": "Failed to parse JSON"}


def _clamp01(x) -> float:
    """Clamp value between 0 and 1"""
    try:
        v = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, v))


class GeminiClient:
    """Client for Google Gemini API - Medical Document Analysis"""

    def __init__(self) -> None:
        self.use_gemini = settings.use_gemini
        self.model_name = settings.gemini_model or "gemini-1.5-flash"
        self.model = None

        if self.use_gemini and settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={
                        "temperature": 0.1,
                        "top_p": 0.95,
                        "top_k": 40,
                        "max_output_tokens": 8192,
                    }
                )
                print(f"[OK] Using Gemini model: {self.model_name}")
            except Exception as e:
                print(f"[WARNING] Failed to initialize Gemini: {e}")
                self.use_gemini = False
                self.model = None

    def _call_json(self, system_prompt: str, user_text: str) -> Dict[str, Any]:
        """Call Gemini and parse JSON response"""
        if not self.model:
            raise RuntimeError("Gemini client not configured")

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{user_text}"

        response = self.model.generate_content(full_prompt)
        return _parse_json_from_response(response.text)

    def classify(self, document_text: str) -> Dict[str, Any]:
        """Classify medical document type"""
        if not self.use_gemini:
            # Heuristic fallback
            txt = document_text.lower()
            if any(k in txt for k in ["wbc", "hemoglobin", "platelets", "rbc"]):
                t = "COMPLETE BLOOD COUNT"
            elif any(k in txt for k in ["sodium", "potassium", "creatinine", "glucose"]):
                t = "BASIC METABOLIC PANEL"
            elif "ct " in txt or "ct-" in txt or "computed tomography" in txt:
                t = "CT"
            elif "x-ray" in txt or "xray" in txt or "radiograph" in txt:
                t = "X-RAY"
            else:
                t = "CLINICAL NOTE"
            return {
                "document_type": t,
                "confidence": 0.9,
                "rationale": "Heuristic classification (Gemini not configured).",
                "evidence": [],
            }

        system_prompt = """You are a medical document classifier.
Classify into exactly one of: COMPLETE BLOOD COUNT, BASIC METABOLIC PANEL, X-RAY, CT, CLINICAL NOTE.

Return strict JSON with keys:
- document_type: one of the 5 types above
- confidence: float between 0 and 1
- rationale: brief explanation
- evidence: array of quoted text from document

Example:
{
  "document_type": "COMPLETE BLOOD COUNT",
  "confidence": 0.95,
  "rationale": "Contains CBC lab values like WBC, hemoglobin",
  "evidence": ["WBC 13.2", "Hemoglobin 14.1"]
}"""

        result = self._call_json(system_prompt, document_text)

        # Ensure evidence is always an array
        if "evidence" not in result or not isinstance(result["evidence"], list):
            result["evidence"] = []

        return result

    def extract_codes(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Extract ICD-10 codes from medical document"""
        if not self.use_gemini:
            # Heuristic fallback with common codes
            codes: List[Dict[str, Any]] = []
            lt = document_text.lower()

            if "wbc" in lt and any(word in lt for word in ["elevated", "high", "13"]):
                codes.append({
                    "code": "D72.829",
                    "description": "Elevated white blood cell count",
                    "confidence": 0.85,
                    "evidence": ["elevated WBC"]
                })
            if "anemia" in lt or ("hemoglobin" in lt and "low" in lt):
                codes.append({
                    "code": "D64.9",
                    "description": "Anemia, unspecified",
                    "confidence": 0.85,
                    "evidence": ["low hemoglobin", "anemia"]
                })
            if "pneumonia" in lt:
                codes.append({
                    "code": "J18.9",
                    "description": "Pneumonia, unspecified",
                    "confidence": 0.88,
                    "evidence": ["pneumonia"]
                })
            if "diabetes" in lt:
                codes.append({
                    "code": "E11.9",
                    "description": "Type 2 diabetes mellitus",
                    "confidence": 0.88,
                    "evidence": ["diabetes"]
                })

            return {"codes": codes}

        system_prompt = f"""You are a medical coding expert. Extract ALL ICD-10 codes from this {document_type} document.

For EACH abnormal finding, condition, or diagnosis, provide:
- code: ICD-10 code
- description: plain language description
- confidence: float 0-1
- evidence: array of quoted text from document

Return JSON format:
{{
  "codes": [
    {{
      "code": "D72.829",
      "description": "Elevated white blood cell count",
      "confidence": 0.90,
      "evidence": ["WBC 13.2 elevated"]
    }}
  ]
}}

CODE ALL abnormalities, conditions, and diagnoses. If nothing abnormal, return empty codes array."""

        return self._call_json(system_prompt, f"Document: {document_text}")

    def summarize(self, document_text: str, document_type: str, codes: list) -> Dict[str, Any]:
        """Generate patient-friendly summary of medical document"""
        if not self.use_gemini:
            # Simple fallback
            return {
                "summary": "Document analysis not available. Please configure Gemini API.",
                "bullets": ["Gemini API not configured"],
                "citations": [],
                "confidence": 0.5
            }

        system_prompt = f"""You are a medical document summarizer. Create a PATIENT-FRIENDLY summary of this {document_type}.

Requirements:
1. List ALL values with exact numbers and units
2. Explain what each value means in simple terms
3. Highlight abnormal findings
4. Make it easy to understand for non-medical people

Return JSON:
{{
  "summary": "Brief 2-3 sentence overview",
  "bullets": ["Detailed bullet points with explanations"],
  "citations": ["Direct quotes from document"],
  "confidence": 0.85
}}"""

        codes_text = json.dumps(codes) if codes else "No ICD-10 codes extracted"
        payload = f"Document Type: {document_type}\nCodes: {codes_text}\n\nDocument:\n{document_text}"

        data = self._call_json(system_prompt, payload)

        # Ensure confidence is numeric
        if "confidence" not in data or not isinstance(data["confidence"], (int, float)):
            data["confidence"] = 0.75
        else:
            data["confidence"] = _clamp01(data["confidence"])

        return data

    def translate_medical_terms(self, document_text: str, target_language: str = "simple") -> Dict[str, Any]:
        """
        Translate complex medical terms to patient-friendly language
        target_language can be: 'simple', 'hindi', 'spanish', etc.
        """
        if not self.use_gemini:
            return {
                "translated_text": document_text,
                "explanations": [],
                "error": "Gemini API not configured"
            }

        if target_language == "simple":
            prompt = """Translate this medical document to simple, patient-friendly language.
Replace medical jargon with everyday words. Explain what each term means.

Return JSON:
{
  "translated_text": "Simple version of the document",
  "explanations": [
    {"term": "Leukocytosis", "simple": "High white blood cell count", "meaning": "Your body is fighting something"}
  ]
}"""
        else:
            prompt = f"""Translate this medical document to {target_language}.
Keep medical accuracy but make it understandable.

Return JSON with 'translated_text' and 'notes'."""

        return self._call_json(prompt, document_text)

    def extract_action_items(self, document_text: str, codes: list) -> Dict[str, Any]:
        """
        Extract actionable items from medical document
        (follow-ups, questions to ask doctor, medication reminders)
        """
        if not self.use_gemini:
            return {"action_items": [], "questions": [], "reminders": []}

        codes_text = json.dumps(codes) if codes else "No codes"

        prompt = f"""Analyze this medical document and extract actionable items for the patient.

Document: {document_text}
ICD-10 Codes: {codes_text}

Return JSON:
{{
  "action_items": ["Schedule follow-up in 3 months", "Bring previous X-ray"],
  "questions": ["Ask doctor about elevated WBC", "What caused the abnormal results?"],
  "reminders": ["Take medication twice daily", "Fast before next blood test"],
  "urgency": "routine|urgent|emergency"
}}"""

        return self._call_json(prompt, "")

    def validate_medical_document(self, document_text: str) -> bool:
        """Check if document is actually a medical document (not resume, etc.)"""
        if not self.use_gemini:
            doc_lower = document_text.lower()
            medical_keywords = ["patient", "diagnosis", "lab", "test", "blood", "imaging"]
            non_medical = ["resume", "cv", "work experience", "education"]

            med_score = sum(1 for kw in medical_keywords if kw in doc_lower)
            non_med_score = sum(1 for kw in non_medical if kw in doc_lower)

            return med_score >= 2 and non_med_score < 2

        prompt = """Is this a MEDICAL document (lab report, imaging, clinical note)?
Or is it something else (resume, CV, business doc)?

Return JSON: {"is_medical": true} or {"is_medical": false}"""

        try:
            data = self._call_json(prompt, document_text[:1000])
            return data.get("is_medical", True)
        except:
            return True


# Global client instance
client = GeminiClient()
