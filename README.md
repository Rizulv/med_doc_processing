# Medical Doc AI

AI-powered medical document classification, ICD-10 code extraction, and clinical summarization system for healthcare providers.

## Features

- **Document Classification**: Automatically classify medical documents into 5 types (CBC, BMP, X-Ray, CT, Clinical Note)
- **ICD-10 Code Extraction**: Extract diagnostic codes with confidence scoring and evidence-based validation
- **Clinical Summarization**: Generate provider-facing summaries with key findings and recommendations
- **Full Pipeline Processing**: Upload → Classify → Extract Codes → Summarize in one operation
- **Stub Mode**: Test the system without API costs using deterministic responses

## Tech Stack

### Frontend
- React + TypeScript + Vite
- Shadcn/UI components with Tailwind CSS
- React Query for data fetching
- Wouter for routing

### Backend
- FastAPI (Python)
- SQLite database for metadata
- Anthropic Claude API integration
- Local file storage for uploads
- Production-ready prompt engineering

## Quick Start (Replit)

### 1. Set Up Environment Variables

Add these secrets in Replit Secrets:

```
ANTHROPIC_API_KEY=your_api_key_here  (optional for stub mode)
USE_CLAUDE_REAL=false               (true to use real API)
ALLOW_ORIGINS=http://localhost:5173
```

### 2. Start Backend

```bash
cd backend-fastapi
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start Frontend

In a new terminal:

```bash
npm run dev -- --host
```

### 4. Open the Application

- Frontend: http://localhost:5173 (or Replit preview URL)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## API Endpoints

### Document Management

**POST /documents**
Upload and process medical documents
- Accepts: PDF, TXT files
- Query param: `run_pipeline=true` (runs full pipeline)
- Returns: Classification, ICD-10 codes, and summary

**GET /documents**
List all uploaded documents (50 most recent)

**GET /documents/{id}**
Get document details with processing results

### Individual Operations

**POST /classify**
```json
{
  "document_text": "string"
}
```
Returns: Document type, confidence, rationale, evidence

**POST /extract-codes**
```json
{
  "document_text": "string",
  "document_type": "COMPLETE BLOOD COUNT" // optional
}
```
Returns: ICD-10 codes with descriptions, confidence, evidence

**POST /summarize**
```json
{
  "document_text": "string",
  "document_type": "X-RAY", // optional
  "codes": [...] // optional
}
```
Returns: Clinical summary with confidence and evidence

## Prompts

All prompts are stored as markdown files in `backend-fastapi/app/services/prompts/`:

- **classification.md**: 5-type document classification with few-shot examples
- **codes.md**: ICD-10 extraction with hallucination prevention
- **summary.md**: Provider-facing clinical summaries

### Editing Prompts

1. Navigate to `backend-fastapi/app/services/prompts/`
2. Edit the relevant `.md` file
3. Restart the backend server
4. Test with evaluation dataset in `/evals`

## ICD-10 Codes

ICD-10 (International Classification of Diseases, 10th Revision) is a standardized diagnostic coding system. This system:

- Only extracts codes explicitly supported by document evidence
- Includes confidence scoring (≥0.8 = high, 0.5-0.79 = medium, <0.5 = low)
- Prevents hallucinations through strict evidence requirements
- Provides exact quotes supporting each code

**Anti-Hallucination Policy:** Codes are only included when directly supported by document text. Empty code lists are valid and preferred over speculative coding.

## Stub Mode vs Real API

### Stub Mode (USE_CLAUDE_REAL=false)
- **Default behavior** - no API key required
- Deterministic responses based on keyword matching
- Perfect for development and testing
- Zero API costs

### Real API Mode (USE_CLAUDE_REAL=true)
- Requires `ANTHROPIC_API_KEY` in environment
- Uses Claude AI for actual analysis
- Higher accuracy, handles edge cases better
- Production-ready performance

## Evaluation

Test cases are in `evals/datasets/test-documents.json`:

- 5 sample documents (CBC, BMP, X-Ray, CT, Clinical Note)
- Ground truth for validation
- Ready for Claude Eval Tool integration

### Quick Smoke Test

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"document_text": "COMPLETE BLOOD COUNT\nWBC 12.5 K/uL\nHemoglobin 9.2 g/dL"}'
```

See `evals/README.md` for detailed testing instructions.

## Project Structure

```
medical-doc-ai/
├── README.md
├── replit_setup.md
├── .env.example
├── .gitignore
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/           # Main pages (Upload, Documents, Detail)
│   │   └── lib/             # API client and utilities
│   └── index.html
├── backend-fastapi/          # Python FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── config.py        # Configuration and settings
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   │   ├── anthropic_client.py  # Claude AI integration
│   │   │   ├── text_extract.py      # PDF/TXT extraction
│   │   │   └── prompts/     # Production-ready prompts
│   │   └── db/              # Database models and CRUD
│   └── requirements.txt
├── shared/                   # Shared TypeScript types
│   └── schema.ts
└── evals/                    # Evaluation datasets
    ├── datasets/
    │   └── test-documents.json
    └── README.md
```

## Environment Variables

See `.env.example` for all configuration options:

```bash
# Required for real API mode
ANTHROPIC_API_KEY=sk-ant-...

# Model configuration
CLAUDE_MODEL=claude-3-5-sonnet-latest
PROMPT_CACHE_TTL_SECONDS=3600

# Database
DB_URL=sqlite:///./app.db

# CORS configuration
ALLOW_ORIGINS=http://localhost:5173

# API mode
USE_CLAUDE_REAL=false  # Set to true for production

# Frontend API base
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Development

### Frontend Development

```bash
npm run dev
```

Hot reload enabled, runs on port 5173

### Backend Development

```bash
cd backend-fastapi
python -m uvicorn app.main:app --reload
```

Auto-reload on file changes, runs on port 8000

### Adding New Document Types

1. Update `DOCUMENT_TYPES` in `shared/schema.ts`
2. Add classification rules in `prompts/classification.md`
3. Update icon mappings in `ClassificationPanel.tsx`
4. Add test cases to `evals/datasets/test-documents.json`

## Advanced Features

### Prompt Caching

Enable in `anthropic_client.py` by adding cache_control parameter:
```python
# Reduces latency and cost for frequently used prompts
```

### Extended Thinking

Use Claude models with extended thinking for complex edge cases:
- Improves accuracy on ambiguous documents
- Increases latency slightly
- Ideal for low-confidence scenarios

## Troubleshooting

**Backend won't start:**
- Check Python dependencies: `pip list | grep fastapi`
- Verify port 8000 is available
- Check database permissions

**Frontend can't connect to backend:**
- Verify `VITE_API_BASE_URL` is set correctly
- Check CORS configuration in backend
- Ensure both servers are running

**Stub mode not working:**
- Confirm `USE_CLAUDE_REAL=false`
- Check console for error messages
- Verify prompt files exist in `backend-fastapi/app/services/prompts/`

## Security Notes

- Never commit API keys to version control
- Use Replit Secrets for sensitive environment variables
- File uploads are stored locally (not in production database)
- PHI (Protected Health Information) should be de-identified before processing

## License

This is a demonstration project for Replit. See LICENSE file for details.

## Support

For issues or questions:
1. Check `evals/README.md` for testing guidance
2. Review prompt files for expected behavior
3. Test with evaluation dataset first
4. Verify environment variables are set correctly
