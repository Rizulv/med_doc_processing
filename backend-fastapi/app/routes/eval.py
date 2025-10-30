# app/routes/eval.py
import re
from fastapi import APIRouter
from app.services.anthropic_client import client

router = APIRouter(prefix="/eval", tags=["eval"])

# Comprehensive evaluation dataset
DATA = [
    {
        "id": "cbc_001",
        "text": "CBC Report: WBC 13.2 x10^3/µL (elevated), Hgb 14.1 g/dL, Platelets 250 x10^3/µL. Impression: leukocytosis.",
        "gold_codes": ["D72.829"],
        "gold_facts": ["leukocytosis", "hemoglobin normal", "platelets normal"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_002",
        "text": "Complete Blood Count: WBC 4.5 x10^3/µL, Hemoglobin 9.2 g/dL (low), Hematocrit 28%, Platelets 180 x10^3/µL. Findings consistent with anemia.",
        "gold_codes": ["D64.9"],
        "gold_facts": ["anemia", "low hemoglobin", "normal white blood cells"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_003",
        "text": "CBC: WBC 5.8 x10^3/µL, Hgb 15.2 g/dL, Platelets 45 x10^3/µL (critically low). Impression: thrombocytopenia.",
        "gold_codes": ["D69.6"],
        "gold_facts": ["thrombocytopenia", "critically low platelets", "normal hemoglobin"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "bmp_001",
        "text": "Basic Metabolic Panel: Sodium 138 mmol/L, Potassium 3.0 mmol/L (low), Chloride 101, BUN 22 mg/dL, Creatinine 1.5 mg/dL.",
        "gold_codes": ["E87.6"],
        "gold_facts": ["hypokalemia", "renal function borderline"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "bmp_002",
        "text": "BMP Results: Sodium 152 mmol/L (high), Potassium 4.2 mmol/L, Glucose 245 mg/dL (elevated), BUN 45 mg/dL, Creatinine 2.8 mg/dL (elevated). Findings: hypernatremia and acute kidney injury.",
        "gold_codes": ["E87.0", "N17.9"],
        "gold_facts": ["hypernatremia", "acute kidney injury", "elevated creatinine"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "xray_001",
        "text": "Chest X-ray: Right lower lobe airspace opacity consistent with pneumonia. No pleural effusion. Heart size normal.",
        "gold_codes": ["J18.9"],
        "gold_facts": ["right lower lobe pneumonia", "no effusion"],
        "doc_type": "X-RAY",
    },
    {
        "id": "xray_002",
        "text": "Chest Radiograph PA and Lateral: Large right-sided pleural effusion. Blunting of right costophrenic angle. No pneumothorax identified.",
        "gold_codes": ["J91.8"],
        "gold_facts": ["right pleural effusion", "no pneumothorax"],
        "doc_type": "X-RAY",
    },
    {
        "id": "xray_003",
        "text": "Left knee X-ray 2 views: Severe joint space narrowing. Large marginal osteophytes. Subchondral sclerosis. Findings consistent with osteoarthritis.",
        "gold_codes": ["M17.12"],
        "gold_facts": ["left knee osteoarthritis", "severe joint space narrowing", "osteophytes"],
        "doc_type": "X-RAY",
    },
    {
        "id": "ct_001",
        "text": "CT Head (non-contrast): No acute hemorrhage. Chronic lacunar infarct in left basal ganglia. No mass effect or midline shift.",
        "gold_codes": ["I63.9"],
        "gold_facts": ["no acute bleed", "lacunar infarct"],
        "doc_type": "CT",
    },
    {
        "id": "ct_002",
        "text": "CT Chest with contrast: Multiple bilateral pulmonary emboli involving segmental branches. Right heart strain noted. Recommendation: anticoagulation.",
        "gold_codes": ["I26.99"],
        "gold_facts": ["bilateral pulmonary emboli", "right heart strain"],
        "doc_type": "CT",
    },
    {
        "id": "ct_003",
        "text": "CT Abdomen/Pelvis: Acute appendicitis with periappendiceal fat stranding. Appendix measures 12mm in diameter. Small amount of free fluid in right lower quadrant.",
        "gold_codes": ["K35.80"],
        "gold_facts": ["acute appendicitis", "fat stranding", "free fluid"],
        "doc_type": "CT",
    },
    {
        "id": "note_001",
        "text": "52-year-old male with type 2 diabetes mellitus; HbA1c 8.4% (poorly controlled). On metformin 1000mg BID. Complains of burning sensation in feet bilaterally, worse at night, suggestive of peripheral neuropathy.",
        "gold_codes": ["E11.9", "E11.40"],
        "gold_facts": ["type 2 diabetes", "poor glycemic control", "neuropathy symptoms"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "note_002",
        "text": "68 y/o F presents with progressive dyspnea and orthopnea. Physical exam: bilateral lower extremity edema, elevated JVP, crackles at lung bases. Echo shows EF 30%. Assessment: congestive heart failure, systolic dysfunction.",
        "gold_codes": ["I50.21"],
        "gold_facts": ["congestive heart failure", "reduced ejection fraction", "dyspnea"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "note_003",
        "text": "35-year-old woman with history of migraine presents with severe unilateral headache, photophobia, and nausea for 6 hours. No focal neurologic deficits. Diagnosis: acute migraine without aura.",
        "gold_codes": ["G43.109"],
        "gold_facts": ["migraine", "unilateral headache", "photophobia"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "note_004",
        "text": "Patient is a 45-year-old male smoker presenting with productive cough for 3 weeks, fever, night sweats, and 10 lb weight loss. CXR shows right upper lobe cavitary lesion. Sputum AFB pending. Impression: suspected pulmonary tuberculosis.",
        "gold_codes": ["A15.0"],
        "gold_facts": ["suspected tuberculosis", "cavitary lesion", "constitutional symptoms"],
        "doc_type": "CLINICAL NOTE",
    },
]


def _norm(c: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", c.upper())


@router.get("/quick")
def quick_eval():
    n = len(DATA)
    tp = fp = fn = 0
    cov_sum = 0.0
    test_results = []

    for item in DATA:
        # Extract codes
        pred_response = client.extract_codes(item["text"], item["doc_type"])
        pred = pred_response.get("codes", [])
        pred_set = {_norm(x.get("code", "")) for x in pred}
        gold_set = {_norm(x) for x in item["gold_codes"]}

        # Calculate per-item metrics
        item_tp = len(pred_set & gold_set)
        item_fp = len(pred_set - gold_set)
        item_fn = len(gold_set - pred_set)

        tp += item_tp
        fp += item_fp
        fn += item_fn

        item_precision = item_tp / (item_tp + item_fp) if (item_tp + item_fp) else 0.0
        item_recall = item_tp / (item_tp + item_fn) if (item_tp + item_fn) else 0.0
        item_f1 = (
            2 * item_precision * item_recall / (item_precision + item_recall)
            if (item_precision + item_recall)
            else 0.0
        )

        # Generate summary
        summ = client.summarize(item["text"], item["doc_type"], pred)
        s = (summ.get("summary") or "").lower()
        got = sum(1 for f in item["gold_facts"] if f.lower() in s)
        item_coverage = got / max(1, len(item["gold_facts"]))
        cov_sum += item_coverage

        # Store detailed results
        test_results.append(
            {
                "id": item["id"],
                "document_type": item["doc_type"],
                "query": item["text"],
                "expected_codes": item["gold_codes"],
                "predicted_codes": [c.get("code", "") for c in pred],
                "expected_facts": item["gold_facts"],
                "generated_summary": summ.get("summary", ""),
                "metrics": {
                    "precision": round(item_precision, 2),
                    "recall": round(item_recall, 2),
                    "f1": round(item_f1, 2),
                    "coverage": round(item_coverage, 2),
                },
            }
        )

    # Calculate overall metrics
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    )

    return {
        "items": n,
        "codes_precision": round(precision, 2),
        "codes_recall": round(recall, 2),
        "codes_f1": round(f1, 2),
        "summary_coverage": round(cov_sum / n, 2),
        "mode": "USE_CLAUDE_REAL=" + str(client.use_real),
        "test_results": test_results,
    }
