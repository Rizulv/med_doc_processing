# app/routes/eval.py
import re
import json
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.services.gemini_client import client
from app.config import settings

router = APIRouter(prefix="/eval", tags=["eval"])

# Directory to save eval reports
EVAL_REPORTS_DIR = Path(__file__).parent.parent.parent / "eval_reports"
print(f"[DEBUG] Eval reports directory: {EVAL_REPORTS_DIR.absolute()}")
EVAL_REPORTS_DIR.mkdir(exist_ok=True)
print(f"[DEBUG] Directory exists: {EVAL_REPORTS_DIR.exists()}")


def save_eval_report(results: dict):
    """Save evaluation report to file with timestamp"""
    try:
        print(f"[DEBUG] Attempting to save eval report to: {EVAL_REPORTS_DIR.absolute()}")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"eval_report_{timestamp}.json"
        filepath = EVAL_REPORTS_DIR / filename

        print(f"[DEBUG] Full filepath: {filepath.absolute()}")

        # Save as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[DEBUG] Successfully wrote timestamped file")

        # Also save as "latest" for easy access
        latest_path = EVAL_REPORTS_DIR / "eval_report_latest.json"
        with open(latest_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"[DEBUG] Successfully wrote latest file")

        return str(filepath)
    except Exception as e:
        print(f"[ERROR] Failed to save eval report: {e}")
        import traceback
        traceback.print_exc()
        return None


@router.get("/latest")
def get_latest_eval():
    """Fetch the latest pre-computed eval results from S3"""
    # Try local cache first (for development), then S3 (for production)
    try:
        latest_local = EVAL_REPORTS_DIR / "eval_report_latest.json"
        if latest_local.exists():
            print(f"[INFO] Serving from local cache: {latest_local}")
            with open(latest_local, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as local_err:
        print(f"[WARNING] Local cache failed: {local_err}")

    # Try S3 as fallback
    try:
        import boto3
        s3 = boto3.client('s3', region_name=settings.aws_region)
        response = s3.get_object(
            Bucket=settings.s3_bucket_name,
            Key='eval-results/latest.json'
        )
        eval_results = json.loads(response['Body'].read())
        print(f"[INFO] Served from S3")
        return eval_results
    except Exception as e:
        print(f"[WARNING] S3 fetch failed: {e}")

    raise HTTPException(
        status_code=404,
        detail="No evaluation results found. Results are generated during deployment."
    )


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
    # Additional CBC tests
    {
        "id": "cbc_004",
        "text": "CBC: WBC 3.2 x10^3/µL (low), Hemoglobin 13.5 g/dL, Platelets 220 x10^3/µL, Neutrophils 40% (low). Impression: leukopenia with neutropenia.",
        "gold_codes": ["D70.9", "D72.819"],
        "gold_facts": ["leukopenia", "neutropenia", "low WBC"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_005",
        "text": "Complete Blood Count: WBC 8.5 x10^3/µL, Hemoglobin 18.5 g/dL (elevated), Hematocrit 55% (high), Platelets 450 x10^3/µL. Findings consistent with polycythemia.",
        "gold_codes": ["D75.1"],
        "gold_facts": ["polycythemia", "elevated hemoglobin", "elevated hematocrit"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    # Additional BMP tests
    {
        "id": "bmp_003",
        "text": "Basic Metabolic Panel: Sodium 128 mmol/L (low), Potassium 5.8 mmol/L (high), Chloride 98, BUN 65 mg/dL (elevated), Creatinine 4.2 mg/dL (elevated). Findings: hyponatremia, hyperkalemia, and chronic kidney disease.",
        "gold_codes": ["E87.1", "E87.5", "N18.9"],
        "gold_facts": ["hyponatremia", "hyperkalemia", "chronic kidney disease", "elevated creatinine"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "bmp_004",
        "text": "BMP Results: Sodium 142 mmol/L, Potassium 4.0 mmol/L, Glucose 450 mg/dL (critically high), BUN 18 mg/dL, Creatinine 1.0 mg/dL. Impression: severe hyperglycemia.",
        "gold_codes": ["E11.65"],
        "gold_facts": ["severe hyperglycemia", "glucose 450"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    # Additional X-RAY tests
    {
        "id": "xray_004",
        "text": "Chest X-ray PA and Lateral: Left upper lobe mass measuring 4.5 cm. Spiculated margins. Hilar lymphadenopathy. Findings suspicious for malignancy.",
        "gold_codes": ["R91.1"],
        "gold_facts": ["lung mass", "suspicious for malignancy", "lymphadenopathy"],
        "doc_type": "X-RAY",
    },
    {
        "id": "xray_005",
        "text": "Right wrist X-ray: Transverse fracture through distal radius metaphysis with 15-degree dorsal angulation. No intra-articular extension.",
        "gold_codes": ["S52.501A"],
        "gold_facts": ["distal radius fracture", "dorsal angulation"],
        "doc_type": "X-RAY",
    },
    # Additional CT tests
    {
        "id": "ct_004",
        "text": "CT Abdomen with contrast: Acute diverticulitis in sigmoid colon with pericolonic fat stranding and fluid collection. No free air or perforation.",
        "gold_codes": ["K57.32"],
        "gold_facts": ["acute diverticulitis", "sigmoid colon", "fat stranding"],
        "doc_type": "CT",
    },
    {
        "id": "ct_005",
        "text": "CT Head non-contrast: Large acute right middle cerebral artery territory infarct with mass effect and 5mm midline shift. No hemorrhagic transformation.",
        "gold_codes": ["I63.511"],
        "gold_facts": ["acute MCA infarct", "mass effect", "midline shift"],
        "doc_type": "CT",
    },
    # Additional Clinical Notes
    {
        "id": "note_005",
        "text": "72-year-old male with hypertension, hyperlipidemia, and COPD. Current medications: lisinopril 20mg daily, atorvastatin 40mg daily, albuterol inhaler PRN. No acute complaints today.",
        "gold_codes": ["I10", "E78.5", "J44.9"],
        "gold_facts": ["hypertension", "hyperlipidemia", "COPD"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "note_006",
        "text": "38-year-old pregnant female at 28 weeks gestation with gestational diabetes. Fasting glucose 145 mg/dL. Started on insulin regimen. Blood pressure 145/95 mmHg. Assessment: gestational diabetes and gestational hypertension.",
        "gold_codes": ["O24.419", "O13"],
        "gold_facts": ["gestational diabetes", "gestational hypertension", "28 weeks pregnant"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "note_007",
        "text": "25-year-old woman presents with polyuria, polydipsia, and 15 lb weight loss over 2 months. Random glucose 385 mg/dL. Hemoglobin A1c 11.2%. Positive anti-GAD antibodies. Diagnosis: Type 1 diabetes mellitus, newly diagnosed.",
        "gold_codes": ["E10.9"],
        "gold_facts": ["type 1 diabetes", "newly diagnosed", "polyuria", "polydipsia"],
        "doc_type": "CLINICAL NOTE",
    },
    # Additional test cases for better coverage
    {
        "id": "cbc_006",
        "text": "CBC: WBC 6.8 x10^3/µL, Hemoglobin 11.2 g/dL (low), MCV 72 fL (low), Platelets 310 x10^3/µL. Findings consistent with microcytic anemia.",
        "gold_codes": ["D50.9"],
        "gold_facts": ["microcytic anemia", "low hemoglobin", "low MCV"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "bmp_005",
        "text": "BMP: Sodium 140 mmol/L, Potassium 4.1 mmol/L, Glucose 58 mg/dL (critically low), BUN 18 mg/dL, Creatinine 0.9 mg/dL. Impression: hypoglycemia.",
        "gold_codes": ["E16.2"],
        "gold_facts": ["hypoglycemia", "glucose 58"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "xray_006",
        "text": "Chest X-ray: Bilateral diffuse interstitial infiltrates. Ground glass opacities throughout both lung fields. Findings consistent with ARDS.",
        "gold_codes": ["J80"],
        "gold_facts": ["ARDS", "bilateral infiltrates", "ground glass opacities"],
        "doc_type": "X-RAY",
    },
    {
        "id": "ct_006",
        "text": "CT Chest with IV contrast: Multiple bilateral pulmonary nodules, largest 2.3 cm in right upper lobe. Mediastinal lymphadenopathy. Findings suspicious for metastatic disease.",
        "gold_codes": ["C78.00"],
        "gold_facts": ["pulmonary metastases", "multiple nodules", "lymphadenopathy"],
        "doc_type": "CT",
    },
    {
        "id": "note_008",
        "text": "82-year-old male with Alzheimer's disease, moderate stage. MMSE score 15/30. Patient confused to time and place. Requiring assistance with ADLs. Current medications include donepezil 10mg daily.",
        "gold_codes": ["G30.1"],
        "gold_facts": ["Alzheimer's disease", "moderate stage", "cognitive impairment"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "ct_007",
        "text": "CT Abdomen/Pelvis: Renal mass in left kidney measuring 5.2 cm, heterogeneous enhancement. No lymphadenopathy. No metastases identified. Suspicious for renal cell carcinoma.",
        "gold_codes": ["C64.2"],
        "gold_facts": ["renal mass", "left kidney", "suspicious for malignancy"],
        "doc_type": "CT",
    },
    {
        "id": "xray_007",
        "text": "Lumbar spine X-ray: Compression fracture of L1 vertebral body with approximately 40% loss of height. Osteopenia noted. No retropulsion.",
        "gold_codes": ["S32.018A", "M80.08XA"],
        "gold_facts": ["L1 compression fracture", "osteoporosis", "vertebral fracture"],
        "doc_type": "X-RAY",
    },
    {
        "id": "note_009",
        "text": "48-year-old female with major depressive disorder, recurrent, severe. Currently experiencing suicidal ideation without plan. PHQ-9 score 23. Started on escitalopram 10mg daily.",
        "gold_codes": ["F33.2"],
        "gold_facts": ["major depression", "recurrent", "severe", "suicidal ideation"],
        "doc_type": "CLINICAL NOTE",
    },
    {
        "id": "bmp_006",
        "text": "BMP: Sodium 135 mmol/L, Potassium 4.0 mmol/L, Calcium 13.2 mg/dL (high), BUN 28 mg/dL, Creatinine 1.8 mg/dL. Diagnosis: hypercalcemia.",
        "gold_codes": ["E83.52"],
        "gold_facts": ["hypercalcemia", "elevated calcium"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "ct_008",
        "text": "CT Head with contrast: Ring-enhancing lesion in right frontal lobe, 3.5 cm with surrounding vasogenic edema and 8mm midline shift. Differential includes abscess versus high-grade glioma.",
        "gold_codes": ["R90.0"],
        "gold_facts": ["brain lesion", "ring enhancement", "mass effect"],
        "doc_type": "CT",
    },
    # Additional CBC tests (7-10)
    {
        "id": "cbc_007",
        "text": "CBC: WBC 22.5 x10^3/µL (markedly elevated), Neutrophils 85%, Bands 12%. Hemoglobin 13.8 g/dL, Platelets 380 x10^3/µL. Impression: leukocytosis with left shift, suggestive of bacterial infection.",
        "gold_codes": ["D72.829"],
        "gold_facts": ["leukocytosis", "left shift", "elevated WBC"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_008",
        "text": "Complete Blood Count: WBC 2.1 x10^3/µL (critically low), Hemoglobin 10.2 g/dL, Platelets 95 x10^3/µL (low). Pancytopenia present. Findings concerning for bone marrow suppression.",
        "gold_codes": ["D61.9"],
        "gold_facts": ["pancytopenia", "low WBC", "low platelets", "bone marrow suppression"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_009",
        "text": "CBC: WBC 5.2 x10^3/µL, Hemoglobin 16.8 g/dL, Platelets 850 x10^3/µL (elevated). Findings: thrombocytosis.",
        "gold_codes": ["D75.838"],
        "gold_facts": ["thrombocytosis", "elevated platelets"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    {
        "id": "cbc_010",
        "text": "Complete Blood Count: WBC 45.8 x10^3/µL with 88% lymphocytes. Hemoglobin 11.5 g/dL, Platelets 145 x10^3/µL. Atypical lymphocytes noted. Findings suggestive of lymphocytosis.",
        "gold_codes": ["D72.820"],
        "gold_facts": ["lymphocytosis", "elevated lymphocytes", "atypical lymphocytes"],
        "doc_type": "COMPLETE BLOOD COUNT",
    },
    # Additional BMP tests (7-10)
    {
        "id": "bmp_007",
        "text": "BMP: Sodium 148 mmol/L (high), Potassium 3.8 mmol/L, Chloride 112 mmol/L (high), BUN 32 mg/dL, Creatinine 1.2 mg/dL. Findings: hypernatremia and hyperchloremia.",
        "gold_codes": ["E87.0"],
        "gold_facts": ["hypernatremia", "elevated sodium"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "bmp_008",
        "text": "Basic Metabolic Panel: Sodium 142 mmol/L, Potassium 6.8 mmol/L (critically high), Chloride 105 mmol/L, BUN 55 mg/dL, Creatinine 5.2 mg/dL. Diagnosis: severe hyperkalemia with renal failure.",
        "gold_codes": ["E87.5", "N19"],
        "gold_facts": ["severe hyperkalemia", "renal failure", "elevated creatinine"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "bmp_009",
        "text": "BMP: Sodium 136 mmol/L, Potassium 2.5 mmol/L (low), Chloride 88 mmol/L (low), CO2 38 mmol/L (high), BUN 15 mg/dL, Creatinine 0.8 mg/dL. Metabolic alkalosis with hypokalemia.",
        "gold_codes": ["E87.6", "E87.3"],
        "gold_facts": ["hypokalemia", "metabolic alkalosis", "low chloride"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    {
        "id": "bmp_010",
        "text": "Basic Metabolic Panel: Sodium 138 mmol/L, Potassium 4.2 mmol/L, Glucose 320 mg/dL (very high), BUN 45 mg/dL, Creatinine 2.1 mg/dL. Anion gap 22 (elevated). Findings: hyperglycemia with high anion gap metabolic acidosis.",
        "gold_codes": ["E11.65", "E87.2"],
        "gold_facts": ["severe hyperglycemia", "metabolic acidosis", "high anion gap"],
        "doc_type": "BASIC METABOLIC PANEL",
    },
    # Additional X-RAY tests (8-10)
    {
        "id": "xray_008",
        "text": "Chest X-ray: Cardiomegaly with cardiothoracic ratio 0.62. Pulmonary vascular congestion. Bilateral pleural effusions. Findings consistent with congestive heart failure.",
        "gold_codes": ["I50.9"],
        "gold_facts": ["cardiomegaly", "pulmonary congestion", "congestive heart failure"],
        "doc_type": "X-RAY",
    },
    {
        "id": "xray_009",
        "text": "Right hip X-ray: Displaced subcapital femoral neck fracture. Posterior displacement of femoral head. Garden stage IV fracture.",
        "gold_codes": ["S72.051A"],
        "gold_facts": ["femoral neck fracture", "displaced fracture", "right hip"],
        "doc_type": "X-RAY",
    },
    {
        "id": "xray_010",
        "text": "Abdominal X-ray supine and upright: Multiple dilated loops of small bowel. Air-fluid levels present. Paucity of gas in colon. Findings consistent with small bowel obstruction.",
        "gold_codes": ["K56.60"],
        "gold_facts": ["small bowel obstruction", "dilated bowel loops", "air-fluid levels"],
        "doc_type": "X-RAY",
    },
    # Additional CT tests (9-10)
    {
        "id": "ct_009",
        "text": "CT Chest without contrast: Saddle pulmonary embolism extending into bilateral main pulmonary arteries. Right ventricular dilation. Findings indicate massive pulmonary embolism.",
        "gold_codes": ["I26.92"],
        "gold_facts": ["saddle pulmonary embolism", "bilateral PE", "RV dilation"],
        "doc_type": "CT",
    },
    {
        "id": "ct_010",
        "text": "CT Abdomen/Pelvis with contrast: Pancreatic head mass 4.2 cm causing bile duct dilation. Pancreatic duct cutoff sign present. Findings highly suspicious for pancreatic adenocarcinoma.",
        "gold_codes": ["C25.0"],
        "gold_facts": ["pancreatic mass", "bile duct dilation", "suspicious for malignancy"],
        "doc_type": "CT",
    },
    # Additional CLINICAL NOTE test (10)
    {
        "id": "note_010",
        "text": "62-year-old male with end-stage renal disease on hemodialysis three times weekly. Last dialysis yesterday. Currently anuric. Arteriovenous fistula in left forearm functioning well. Assessment: ESRD on maintenance hemodialysis.",
        "gold_codes": ["N18.6"],
        "gold_facts": ["end-stage renal disease", "hemodialysis", "anuric"],
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

    results = {
        "items": n,
        "codes_precision": round(precision, 2),
        "codes_recall": round(recall, 2),
        "codes_f1": round(f1, 2),
        "summary_coverage": round(cov_sum / n, 2),
        "test_results": test_results,
        "timestamp": datetime.now().isoformat(),
    }

    # Save the report
    saved_path = save_eval_report(results)
    if saved_path:
        results["report_saved_to"] = saved_path

    return results
