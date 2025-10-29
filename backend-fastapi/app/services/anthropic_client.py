# app/services/anthropic_client.py
import json, re
from typing import Any, Dict, List

from app.config import settings

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None


def _parse_json_from_response(resp) -> Dict[str, Any]:
    # Anthropic returns a list of content blocks; join text and parse
    text = "".join([b.text for b in resp.content if getattr(b, "type", "") == "text"])
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        return json.loads(m.group(0)) if m else {"raw": text}


def _clamp01(x) -> float:
    try:
        v = float(x)
    except Exception:
        return 0.0
    return max(0.0, min(1.0, v))


class ClaudeClient:
    def __init__(self) -> None:
        self.use_real = str(settings.use_claude_real).lower() in ("1", "true", "yes")
        # Use a model that actually exists
        self.model = settings.claude_model or "claude-3-5-sonnet-20241022"
        self._client = None

        if self.use_real and Anthropic:
            # No proxies. Prompt caching header is fine; no ttl seconds fields.
            self._client = Anthropic(
                api_key=settings.anthropic_api_key,
                default_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
            )

    # ---------------- Real calls ----------------
    def _call_json(self, system_prompt: str, user_text: str, max_tokens: int = 1024):
        if not self._client:
            raise RuntimeError("Anthropic client not configured")

        resp = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=[
                {"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}
            ],
            messages=[{"role": "user", "content": [{"type": "text", "text": user_text}]}],
        )
        return _parse_json_from_response(resp)

    # ---------------- Public API ----------------
    def classify(self, document_text: str) -> Dict[str, Any]:
        if not self.use_real:
            # Heuristic stub
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
                "rationale": "Heuristic stub (USE_CLAUDE_REAL=false).",
                "evidence": [],
            }

        system_prompt = (
            "You are a medical document classifier. "
            "Classify into exactly one of: COMPLETE BLOOD COUNT, BASIC METABOLIC PANEL, X-RAY, CT, CLINICAL NOTE. "
            "Return strict JSON with keys: document_type, confidence, rationale, evidence."
        )
        return self._call_json(system_prompt, document_text)

    def extract_codes(self, document_text: str, document_type: str) -> Dict[str, Any]:
        if not self.use_real:
            codes: List[Dict[str, Any]] = []
            lt = document_text.lower()
            if "leukocyt" in lt or "wbc" in lt:
                codes.append({
                    "code": "D72.829",
                    "description": "Elevated white blood cell count, unspecified",
                    "confidence": 0.85,
                    "evidence": ["WBC elevated", "leukocytosis"]
                })
            if "hypokal" in lt or "potassium 3.0" in lt:
                codes.append({
                    "code": "E87.6",
                    "description": "Hypokalemia",
                    "confidence": 0.8,
                    "evidence": ["low potassium"]
                })
            if "pneumonia" in lt:
                codes.append({
                    "code": "J18.9",
                    "description": "Pneumonia, unspecified organism",
                    "confidence": 0.8,
                    "evidence": ["pneumonia"]
                })
            if "infarct" in lt:
                codes.append({
                    "code": "I63.9",
                    "description": "Cerebral infarction, unspecified",
                    "confidence": 0.8,
                    "evidence": ["lacunar infarct"]
                })
            if "diabetes" in lt:
                codes.append({
                    "code": "E11.9",
                    "description": "Type 2 diabetes mellitus without complications",
                    "confidence": 0.8,
                    "evidence": ["type 2 diabetes"]
                })
            if "neuropath" in lt:
                codes.append({
                    "code": "E11.40",
                    "description": "Type 2 diabetes mellitus with diabetic neuropathy, unspecified",
                    "confidence": 0.75,
                    "evidence": ["neuropathy symptoms"]
                })
            return {"codes": codes}

        system_prompt = (
            "Extract ICD-10 diagnosis codes with evidence from the document. "
            "Use the given document_type. "
            "Return JSON: {\"codes\": [{\"code\": \"...\", \"description\": \"...\", \"confidence\": 0-1, \"evidence\": [\"...\"]}] }"
        )
        return self._call_json(system_prompt, f"TYPE: {document_type}\n\nTEXT:\n{document_text}", max_tokens=1500)

    def summarize(self, document_text: str, document_type: str, codes: list) -> Dict[str, Any]:
        if not self.use_real:
            lt = document_text.lower()
            bullets = []
            if "leukocyt" in lt or "wbc" in lt:
                bullets.append("Leukocytosis present.")
            if "hemoglobin" in lt and any(x in lt for x in [" low", " 8.", " 9."]):
                bullets.append("Anemia suspected.")
            if "potassium 3.0" in lt or "hypokal" in lt:
                bullets.append("Hypokalemia.")
            if "pneumonia" in lt:
                bullets.append("Imaging suggests pneumonia.")
            if "infarct" in lt:
                bullets.append("Chronic lacunar infarct noted.")
            if not bullets:
                bullets.append("No acute critical findings highlighted.")

            # Simple heuristic confidence: more bullets ⇒ higher confidence
            conf = _clamp01(0.6 + 0.05 * len(bullets))
            return {"summary": " ".join(bullets), "bullets": bullets, "citations": [], "confidence": conf}

        system_prompt = (
            "You are a clinical summarizer. Produce a concise provider-facing summary for the given document. "
            "Return strict JSON with keys: "
            "{\"summary\": str, \"bullets\": [str], \"citations\": [str], \"confidence\": float 0..1}."
        )
        payload = f"TYPE: {document_type}\nCODES: {json.dumps(codes)}\n\nTEXT:\n{document_text}"
        data = self._call_json(system_prompt, payload, max_tokens=1000)

        # Enforce presence of a numeric confidence
        if "confidence" not in data or not isinstance(data["confidence"], (int, float)):
            data["confidence"] = 0.75
        else:
            data["confidence"] = _clamp01(data["confidence"])
        return data


client = ClaudeClient()
