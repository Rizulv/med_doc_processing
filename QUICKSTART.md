# Medical Doc AI - Quick Start Guide

## 🚀 Starting the Application

The Medical Doc AI system requires **two servers** to run:

### Option 1: Automated Scripts (Recommended)

```bash
# Terminal 1: Start FastAPI Backend
chmod +x start-backend.sh
./start-backend.sh

# Terminal 2: Start Vite Frontend (already running via workflow)
# The Replit workflow automatically starts this
```

### Option 2: Manual Commands

```bash
# Terminal 1: FastAPI Backend
cd backend-fastapi
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Vite Frontend (already running)
# The workflow runs: npm run dev
```

## 🎯 Using the System

1. **Upload Page** (/)
   - Drag & drop or click to upload medical documents (PDF/TXT)
   - Supports CBC, BMP, X-Ray, CT Scan, and Clinical Notes
   - System auto-classifies and processes in one click

2. **Documents Page** (/documents)
   - View all uploaded documents
   - See classification results and confidence scores
   - Click any document to see full analysis

3. **Detail Page** (/documents/:id)
   - View classification with confidence score
   - See extracted ICD-10 codes with evidence
   - Read AI-generated clinical summary

## ⚙️ Configuration Modes

### Stub Mode (Default - No API Key Required)
```bash
# In backend-fastapi/.env
USE_CLAUDE_REAL=false
```
Returns deterministic test data instantly - perfect for testing!

### Real Claude Mode (Requires API Key)
```bash
# In backend-fastapi/.env
USE_CLAUDE_REAL=true
ANTHROPIC_API_KEY=your_key_here
```
Uses Claude 3.5 Sonnet for real AI classification, code extraction, and summarization.

## 📊 Test Data

Sample documents are in `evals/datasets/test-documents.json`:
- Complete Blood Count (CBC)
- Basic Metabolic Panel (BMP)
- Chest X-Ray
- Head CT Scan
- Clinical Progress Note

## 🔍 API Endpoints

All endpoints available at `http://localhost:8000`:

- `GET /health` - Health check
- `POST /documents` - Upload & process (full pipeline)
- `GET /documents` - List all documents
- `GET /documents/{id}` - Get document details
- `POST /classify` - Classify only
- `POST /extract-codes` - Extract ICD-10 codes only
- `POST /summarize` - Generate summary only

## 📚 Documentation

- **README.md** - Full system overview and architecture
- **replit_setup.md** - Detailed Replit-specific setup guide
- **design_guidelines.md** - UI/UX design principles

## ⚡ Quick Test

```bash
# Test backend is running
curl http://localhost:8000/health

# Upload a test document
curl -X POST http://localhost:8000/documents \
  -F "file=@evals/datasets/sample-cbc.txt" \
  -F "filename=test-cbc.txt"
```

## 🎨 Frontend Stack
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui components
- Material Design 3 principles
- TanStack Query for data fetching

## 🔧 Backend Stack
- Python 3.11 + FastAPI
- SQLite database
- Anthropic Claude 3.5 Sonnet
- PyPDF for text extraction

---

**Need Help?** Check README.md for full documentation or replit_setup.md for Replit-specific troubleshooting.
