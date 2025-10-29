# MedicalDocAI — MVP

AI pipeline to analyze medical documents: classify (5 types), extract ICD-10 codes with evidence, and generate a provider-facing summary.  
Stack: **FastAPI** (backend) + **React/TypeScript** (client). Claude can be toggled on/off.

---

## Repo structure

MedicalDocAI/
├─ README.md
├─ backend-fastapi/
│ ├─ requirements.txt
│ ├─ .env # create manually; values shared separately
│ └─ app/
│ ├─ main.py
│ ├─ config.py
│ ├─ db/
│ │ ├─ database.py ├─ models.py └─ crud.py
│ ├─ routes/
│ │ ├─ health.py
│ │ ├─ classify.py
│ │ ├─ extract_codes.py
│ │ ├─ summarize.py
│ │ ├─ pipeline.py # previously documents.py
│ │ └─ eval.py
│ └─ services/
│ ├─ anthropic_client.py
│ ├─ text_extract.py
│ └─ storage_local.py
├─ client/ # React + Vite app
│ ├─ package.json
│ └─ src/...
└─ evals/
├─ datasets/
│ └─ synthetic_v1.json
└─ run_eval.py


**Document types (exact strings):**

- COMPLETE BLOOD COUNT  
- BASIC METABOLIC PANEL  
- X-RAY  
- CT  
- CLINICAL NOTE

---

## 1) Backend — setup and run

**Prereqs:** Python 3.12

```bash
cd backend-fastapi
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt

Create a blank .env in backend-fastapi/ (values are shared separately). Example keys:

DB_URL=sqlite:///./app.db
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# LLM
USE_CLAUDE_REAL=true
ANTHROPIC_API_KEY=sk-********
# Prefer latest; if your org doesn't have it, use the dated model below
CLAUDE_MODEL=claude-4-5

Run the API:
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload


Open docs: http://127.0.0.1:8000/docs

Core endpoints

Your route filenames are extract_codes.py, summarize.py, and pipeline.py.
The actual paths are defined inside those routers. If you kept the original paths:

POST /classify

POST /extract-codes

POST /summarize

POST /documents (pipeline upload/process). If you changed the route prefix to “pipeline”, use that instead.

GET /documents/{id} (fetch stored result)

GET /eval/quick (tiny smoke metrics)

Sample cURL:
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d "{\"document_text\":\"CBC: WBC 12.8, Hb 9.2, Platelets 240\"}"

2) Client — setup and run
Prereqs: Node 20+

cd client
npm install
npm run dev

Open http://localhost:5173

Select a document type from the dropdown (or AUTO).

Upload a .txt or .pdf.

View classification, codes, and summary panels.

If your backend origin differs, set VITE_API_BASE in client/.env:
VITE_API_BASE=http://127.0.0.1:8000


Sample Docs or txt files for testing are in test_docs folder

3) Evals — what they are and how they fit

What: dataset-level checks to measure prompt quality and extraction accuracy over labeled examples (not a single upload).
Why: to iterate prompts reliably. You tweak prompt → run eval → see precision/recall/F1 and summary coverage change.

Quick smoke metrics:
# returns JSON with tiny metrics from a small labeled set
curl http://127.0.0.1:8000/eval/quick


Programmatic runner:
cd evals
python run_eval.py --base-url http://127.0.0.1:8000 \
  --dataset evals/datasets/synthetic_v1.json \
  --mode with_hint

with_hint: simulates the user selecting type in the UI (classification is skipped).

classify_only: calls /classify and reports classification accuracy.

UI vs Evals:

UI shows per-document results for a single upload.

Evals compute metrics across a labeled set to guide prompt improvements.

4) Testing with real Claude

.env already uses USE_CLAUDE_REAL=true.

Ensure the model name exists for your org:

Prefer claude-4-5

If you get “model not found (404)”, use claude-4-5-latest

Prompt caching is configured correctly (ephemeral cache blocks only; no ttl_seconds field).

Versions known good:
anthropic==0.40.0
httpx==0.27.2
pydantic-settings>=2.3

5) Sample test documents (save as .txt)

cbc_demo.txt

CBC Report: WBC 13.2 x10^3/µL (elevated), Hgb 14.1 g/dL, Platelets 250 x10^3/µL. Impression: leukocytosis.


bmp_demo.txt

Basic Metabolic Panel: Sodium 138 mmol/L, Potassium 3.0 mmol/L (low), Chloride 101, BUN 22 mg/dL, Creatinine 1.5 mg/dL.


xray_demo.txt

Chest X-ray: Right lower lobe airspace opacity consistent with pneumonia. No pleural effusion.


ct_demo.txt

CT Head (non-contrast): No acute hemorrhage. Chronic lacunar infarct in left basal ganglia.


note_demo.txt

52-year-old with type 2 diabetes; HbA1c 8.4%. On metformin. Complains of burning feet suggestive of neuropathy

6) Common issues

404 model not found
Your org may not have claude-3-5-sonnet-latest. Switch to claude-3-5-sonnet-20241022.

Prompt cache errors (extra inputs/TTL)
We only send {"cache_control":{"type":"ephemeral"}}. Ensure you didn’t add ttl_seconds.

Proxies error
Use anthropic==0.40.0 and httpx==0.27.2. Don’t pass a proxies arg to the SDK client.

CORS
Add your client origins to ALLOW_ORIGINS in backend .env.

7) Minimal workflow for the team

Pull repo

Create backend-fastapi/.env (values provided privately)

Start backend → open Swagger → sanity-check endpoints

Start client → upload a sample → verify all panels

Run GET /eval/quick → capture baseline metrics

Improve prompts → re-run evals → document metric deltas

8) What’s next (after this README)

Add Docker for backend and client (+ optional docker-compose.yml)

Expand eval dataset (≥10 docs per type) and keep a hold-out set

Track prompt versions and metrics in docs/

Wire S3 for file storage when moving off local dev

Add CI later (GitHub Actions) once Docker is in