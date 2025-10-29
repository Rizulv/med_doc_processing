# MedicalDocAI — MVP

AI pipeline to analyze medical documents: **classify (5 types)**, **extract ICD-10 codes with evidence**, and **generate a provider-facing summary**.  
Stack: **FastAPI** (backend) + **React/TypeScript** (client). Claude can be toggled on/off.

---

## Table of Contents
- [Repo Structure](#repo-structure)
- [Document Types](#document-types)
- [1) Backend — Setup & Run](#1-backend--setup--run)
- [2) Client — Setup & Run](#2-client--setup--run)
- [3) Evals — What & Why](#3-evals--what--why)
- [4) Testing with Real Claude](#4-testing-with-real-claude)
- [5) Sample Test Documents](#5-sample-test-documents)
- [6) Common Issues](#6-common-issues)
- [7) Minimal Team Workflow](#7-minimal-team-workflow)
- [8) Next Steps](#8-next-steps)

---

## Repo Structure

```
MedicalDocAI/
├─ README.md
├─ backend-fastapi/
│  ├─ requirements.txt
│  ├─ .env                  # create manually; values shared separately
│  └─ app/
│     ├─ main.py
│     ├─ config.py
│     ├─ db/
│     │  ├─ database.py
│     │  ├─ models.py
│     │  └─ crud.py
│     ├─ routes/
│     │  ├─ health.py
│     │  ├─ classify.py
│     │  ├─ extract_codes.py
│     │  ├─ summarize.py
│     │  ├─ pipeline.py      # previously documents.py
│     │  └─ eval.py
│     └─ services/
│        ├─ anthropic_client.py
│        ├─ text_extract.py
│        └─ storage_local.py
├─ client/                   # React + Vite app
│  ├─ package.json
│  └─ src/...
└─ evals/
   ├─ datasets/
   │  └─ synthetic_v1.json
   └─ run_eval.py
```

---

## Document Types

Exact strings returned by classification:

- `COMPLETE BLOOD COUNT`
- `BASIC METABOLIC PANEL`
- `X-RAY`
- `CT`
- `CLINICAL NOTE`

---

## 1) Backend — Setup & Run

**Prereqs:** Python **3.12**

```bash
cd backend-fastapi
python -m venv .venv

# Windows PowerShell
. .venv/Scripts/activate

# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend-fastapi/.env` (values shared separately). Example:

```env
DB_URL=sqlite:///./app.db
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# LLM
USE_CLAUDE_REAL=true
ANTHROPIC_API_KEY=sk-********
# Prefer latest; if your org doesn't have it, use the dated model below
CLAUDE_MODEL=claude-4-5
```

Run the API:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open Swagger docs: http://127.0.0.1:8000/docs

**Core endpoints** (paths are defined in routers; these are the usual defaults):

- `POST /classify`
- `POST /extract-codes`
- `POST /summarize`
- `POST /documents`  ← pipeline upload/process (if you renamed to `/pipeline`, use that)
- `GET  /documents/{id}`  ← fetch stored result
- `GET  /eval/quick`      ← tiny smoke metrics

Sample cURL:

```bash
curl -X POST http://127.0.0.1:8000/classify   -H "Content-Type: application/json"   -d '{"document_text":"CBC: WBC 12.8, Hb 9.2, Platelets 240"}'
```

---

## 2) Client — Setup & Run

**Prereqs:** Node **20+**

```bash
cd client
npm install
npm run dev
# open http://localhost:5173
```

- Select a document type from the dropdown (or `AUTO`).
- Upload a `.txt` or `.pdf`.
- View **classification**, **ICD-10 codes** (with evidence + confidence), and **summary**.

If your backend origin differs, set `VITE_API_BASE` in `client/.env`:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

Sample docs for testing live in `test_docs/`.

---

## 3) Evals — What & Why

**What:** dataset-level checks to measure prompt quality and extraction accuracy over labeled examples.  
**Why:** to iterate prompts reliably. You tweak prompt → run eval → see precision/recall/F1 and summary coverage change.

Quick smoke metrics:

```bash
# returns small JSON metrics from a tiny labeled set
curl http://127.0.0.1:8000/eval/quick
```

Programmatic runner:

```bash
cd evals
python run_eval.py --base-url http://127.0.0.1:8000   --dataset evals/datasets/synthetic_v1.json   --mode with_hint
```

**Modes:**
- `with_hint`: simulates the user selecting type in the UI (classification skipped).
- `classify_only`: calls `/classify` and reports classification accuracy.

**UI vs Evals**
- UI: per-document results for a single upload.
- Evals: metrics across a labeled set to guide prompt improvements.

---

## 4) Testing with Real Claude

`.env` example above uses `USE_CLAUDE_REAL=true`.

Model names:
- Prefer: `claude-4-5`
- If you get “model not found (404)”, try `claude-4-5-latest`

Prompt caching is configured with **ephemeral** cache blocks only (no `ttl_seconds`).

Known-good versions:

```text
anthropic==0.40.0
httpx==0.27.2
pydantic-settings>=2.3
```

---

## 5) Sample Test Documents

Save as `.txt` and upload:

**cbc_demo.txt**
```
CBC Report: WBC 13.2 x10^3/µL (elevated), Hgb 14.1 g/dL, Platelets 250 x10^3/µL.
Impression: leukocytosis.
```

**bmp_demo.txt**
```
Basic Metabolic Panel: Sodium 138 mmol/L, Potassium 3.0 mmol/L (low),
Chloride 101, BUN 22 mg/dL, Creatinine 1.5 mg/dL.
```

**xray_demo.txt**
```
Chest X-ray: Right lower lobe airspace opacity consistent with pneumonia.
No pleural effusion.
```

**ct_demo.txt**
```
CT Head (non-contrast): No acute hemorrhage.
Chronic lacunar infarct in left basal ganglia.
```

**note_demo.txt**
```
52-year-old with type 2 diabetes; HbA1c 8.4%.
On metformin. Complains of burning feet suggestive of neuropathy.
```

---

## 6) Common Issues

- **404 model not found**  
  Your org may not have `claude-3-5-sonnet-latest`. Switch to `claude-3-5-sonnet-20241022` or use `claude-4-5(-latest)`.

- **Prompt cache errors (extra inputs/TTL)**  
  Only send `{"cache_control":{"type":"ephemeral"}}`. Do not add `ttl_seconds`.

- **Proxies error**  
  Use `anthropic==0.40.0` and `httpx==0.27.2`. Don’t pass a `proxies` arg to the SDK.

- **CORS**  
  Add your client origins to `ALLOW_ORIGINS` in backend `.env`.

---

## 7) Minimal Team Workflow

1. Pull repo  
2. Create `backend-fastapi/.env` (values provided privately)  
3. Start backend → open Swagger → sanity-check endpoints  
4. Start client → upload a sample → verify all panels  
5. Run `GET /eval/quick` → capture baseline metrics  
6. Improve prompts → re-run evals → document metric deltas

---

## 8) Next Steps

- Add Docker for backend and client (+ optional `docker-compose.yml`)
- Expand eval dataset (≥10 docs per type) and keep a hold-out set
- Track prompt versions and metrics in `docs/`
- Wire S3 for file storage when moving off local dev
- Add CI later (GitHub Actions) once Docker is in
