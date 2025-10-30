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

            # Document-type-specific code extraction
            if document_type == "COMPLETE BLOOD COUNT":
                # CBC-specific codes only
                if "leukocyt" in lt or ("wbc" in lt and ("elevat" in lt or "high" in lt or "13." in lt or "14." in lt or "15." in lt)):
                    codes.append({
                        "code": "D72.829",
                        "description": "Elevated white blood cell count, unspecified",
                        "confidence": 0.85,
                        "evidence": ["WBC elevated", "leukocytosis"]
                    })
                if "anemia" in lt or ("hemoglobin" in lt and ("low" in lt or " 8." in lt or " 9." in lt)):
                    codes.append({
                        "code": "D64.9",
                        "description": "Anemia, unspecified",
                        "confidence": 0.85,
                        "evidence": ["Low hemoglobin", "anemia"]
                    })
                if "thrombocytopenia" in lt or ("platelet" in lt and ("low" in lt or "45" in lt or "critical" in lt)):
                    codes.append({
                        "code": "D69.6",
                        "description": "Thrombocytopenia, unspecified",
                        "confidence": 0.85,
                        "evidence": ["Low platelets", "thrombocytopenia"]
                    })

            elif document_type == "BASIC METABOLIC PANEL":
                # BMP-specific codes only
                if "hypokal" in lt or ("potassium" in lt and ("low" in lt or "3.0" in lt or "2." in lt)):
                    codes.append({
                        "code": "E87.6",
                        "description": "Hypokalemia",
                        "confidence": 0.85,
                        "evidence": ["Low potassium", "hypokalemia"]
                    })
                if "hypernatr" in lt or ("sodium" in lt and ("high" in lt or "15" in lt)):
                    codes.append({
                        "code": "E87.0",
                        "description": "Hyperosmolality and hypernatremia",
                        "confidence": 0.85,
                        "evidence": ["Elevated sodium", "hypernatremia"]
                    })
                if "acute kidney injury" in lt or "aki" in lt or ("creatinine" in lt and ("elevat" in lt or "2." in lt or "3." in lt)):
                    codes.append({
                        "code": "N17.9",
                        "description": "Acute kidney failure, unspecified",
                        "confidence": 0.85,
                        "evidence": ["Elevated creatinine", "acute kidney injury"]
                    })

            elif document_type == "X-RAY":
                # X-Ray-specific codes only
                if "pneumonia" in lt:
                    codes.append({
                        "code": "J18.9",
                        "description": "Pneumonia, unspecified organism",
                        "confidence": 0.85,
                        "evidence": ["Pneumonia on imaging"]
                    })
                if "pleural effusion" in lt or "effusion" in lt:
                    codes.append({
                        "code": "J91.8",
                        "description": "Pleural effusion in other conditions",
                        "confidence": 0.85,
                        "evidence": ["Pleural effusion"]
                    })
                if "osteoarthritis" in lt or ("osteophyte" in lt and "joint space" in lt):
                    codes.append({
                        "code": "M17.12",
                        "description": "Unilateral primary osteoarthritis, left knee",
                        "confidence": 0.85,
                        "evidence": ["Osteoarthritis findings", "joint space narrowing"]
                    })

            elif document_type == "CT":
                # CT-specific codes only
                if "infarct" in lt and ("brain" in lt or "head" in lt or "cerebral" in lt or "basal ganglia" in lt):
                    codes.append({
                        "code": "I63.9",
                        "description": "Cerebral infarction, unspecified",
                        "confidence": 0.85,
                        "evidence": ["Cerebral infarct on CT"]
                    })
                if "pulmonary embol" in lt or "pe " in lt:
                    codes.append({
                        "code": "I26.99",
                        "description": "Other pulmonary embolism without acute cor pulmonale",
                        "confidence": 0.85,
                        "evidence": ["Pulmonary emboli on CT"]
                    })
                if "appendicitis" in lt:
                    codes.append({
                        "code": "K35.80",
                        "description": "Unspecified acute appendicitis",
                        "confidence": 0.85,
                        "evidence": ["Acute appendicitis on CT"]
                    })

            elif document_type == "CLINICAL NOTE":
                # Clinical note codes
                if "diabetes" in lt and "type 2" in lt:
                    codes.append({
                        "code": "E11.9",
                        "description": "Type 2 diabetes mellitus without complications",
                        "confidence": 0.85,
                        "evidence": ["Type 2 diabetes mellitus"]
                    })
                if "neuropath" in lt and "diabet" in lt:
                    codes.append({
                        "code": "E11.40",
                        "description": "Type 2 diabetes mellitus with diabetic neuropathy, unspecified",
                        "confidence": 0.85,
                        "evidence": ["Diabetic neuropathy"]
                    })
                if "heart failure" in lt or "chf" in lt:
                    codes.append({
                        "code": "I50.21",
                        "description": "Acute systolic (congestive) heart failure",
                        "confidence": 0.85,
                        "evidence": ["Congestive heart failure"]
                    })
                if "migraine" in lt:
                    codes.append({
                        "code": "G43.109",
                        "description": "Migraine without aura, not intractable, without status migrainosus",
                        "confidence": 0.85,
                        "evidence": ["Migraine"]
                    })
                if "tuberculosis" in lt or ("tb" in lt and ("lung" in lt or "pulmonary" in lt)):
                    codes.append({
                        "code": "A15.0",
                        "description": "Tuberculosis of lung",
                        "confidence": 0.85,
                        "evidence": ["Suspected pulmonary tuberculosis"]
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

            # Document-type-specific summarization
            if document_type == "COMPLETE BLOOD COUNT":
                if "leukocyt" in lt or ("wbc" in lt and "elevat" in lt):
                    bullets.append("Leukocytosis present with elevated WBC count.")
                if "anemia" in lt or ("hemoglobin" in lt and "low" in lt):
                    bullets.append("Anemia noted with low hemoglobin levels.")
                if "thrombocytopenia" in lt or ("platelet" in lt and "low" in lt):
                    bullets.append("Thrombocytopenia identified with low platelet count.")
                if not bullets:
                    bullets.append("Complete blood count within normal limits.")

            elif document_type == "BASIC METABOLIC PANEL":
                if "hypokal" in lt or ("potassium" in lt and "low" in lt):
                    bullets.append("Hypokalemia detected.")
                if "hypernatr" in lt or ("sodium" in lt and "high" in lt):
                    bullets.append("Hypernatremia present.")
                if "kidney injury" in lt or ("creatinine" in lt and "elevat" in lt):
                    bullets.append("Acute kidney injury indicated by elevated creatinine.")
                if not bullets:
                    bullets.append("Basic metabolic panel shows no critical abnormalities.")

            elif document_type == "X-RAY":
                if "pneumonia" in lt:
                    bullets.append("Radiographic findings consistent with pneumonia.")
                if "effusion" in lt:
                    bullets.append("Pleural effusion visualized.")
                if "osteoarthritis" in lt or "osteophyte" in lt:
                    bullets.append("Degenerative changes consistent with osteoarthritis.")
                if not bullets:
                    bullets.append("X-ray shows no acute abnormalities.")

            elif document_type == "CT":
                if "infarct" in lt:
                    bullets.append("Cerebral infarction identified on CT imaging.")
                if "embol" in lt:
                    bullets.append("Pulmonary emboli detected with evidence of right heart strain.")
                if "appendicitis" in lt:
                    bullets.append("CT findings consistent with acute appendicitis.")
                if not bullets:
                    bullets.append("CT scan shows no acute findings.")

            elif document_type == "CLINICAL NOTE":
                if "diabetes" in lt:
                    bullets.append("Type 2 diabetes mellitus documented.")
                if "neuropath" in lt:
                    bullets.append("Peripheral neuropathy symptoms present.")
                if "heart failure" in lt:
                    bullets.append("Congestive heart failure with reduced ejection fraction.")
                if "migraine" in lt:
                    bullets.append("Acute migraine episode without focal neurologic deficits.")
                if "tuberculosis" in lt or "tb" in lt:
                    bullets.append("Suspected pulmonary tuberculosis pending confirmatory testing.")
                if not bullets:
                    bullets.append("Clinical assessment documented.")

            if not bullets:
                bullets.append("No specific findings documented for this document type.")

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
