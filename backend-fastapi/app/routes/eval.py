# app/routes/eval.py
from fastapi import APIRouter
from app.services.anthropic_client import client

router = APIRouter(prefix="/eval", tags=["eval"])

# tiny built-in dataset (same shape as synthetic_v1)
DATA = [
    {
        "text": "CBC Report: WBC 13.2 x10^3/µL (elevated), Hgb 14.1 g/dL, Platelets 250 x10^3/µL.",
        "gold_codes": ["D72.829"],
        "gold_facts": ["leukocytosis", "hemoglobin normal", "platelets normal"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "text": "BMP: Sodium 138, Potassium 3.0 (low), BUN 22, Creatinine 1.5.",
        "gold_codes": ["E87.6"],
        "gold_facts": ["hypokalemia", "renal function borderline"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
]

def _norm(c: str) -> str:
    import re
    return re.sub(r"[^A-Z0-9]", "", c.upper())

@router.get("/quick")
def quick_eval():
    n = len(DATA)
    tp=fp=fn=0
    cov_sum = 0.0

    for item in DATA:
        # codes
        pred = client.extract_codes(item["text"], item["doc_type"]).get("codes", [])
        pred_set = {_norm(x.get("code","")) for x in pred}
        gold_set = {_norm(x) for x in item["gold_codes"]}
        tp += len(pred_set & gold_set)
        fp += len(pred_set - gold_set)
        fn += len(gold_set - pred_set)

        # summary coverage
        summ = client.summarize(item["text"], item["doc_type"], pred)
        s = (summ.get("summary") or "").lower()
        got = sum(1 for f in item["gold_facts"] if f.lower() in s)
        cov_sum += got / max(1, len(item["gold_facts"]))

    precision = tp / (tp+fp) if (tp+fp) else 0.0
    recall    = tp / (tp+fn) if (tp+fn) else 0.0
    f1        = 2*precision*recall/(precision+recall) if (precision+recall) else 0.0
    return {
        "items": n,
        "codes_precision": round(precision, 2),
        "codes_recall": round(recall, 2),
        "codes_f1": round(f1, 2),
        "summary_coverage": round(cov_sum/n, 2),
        "mode": "USE_CLAUDE_REAL=" + str(client.use_real),
    }
