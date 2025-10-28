# Replit Setup Guide - Medical Doc AI

Complete setup instructions for running Medical Doc AI in Replit.

## Prerequisites

- Replit account
- (Optional) Anthropic API key for real Claude integration

## Step 1: Environment Configuration

### Add Replit Secrets

Click the "Secrets" icon in Replit and add these keys:

**Required for Stub Mode (Default):**
```
USE_CLAUDE_REAL=false
ALLOW_ORIGINS=http://localhost:5173
```

**Optional - For Real Claude API:**
```
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
USE_CLAUDE_REAL=true
CLAUDE_MODEL=claude-3-5-sonnet-latest
```

**Database (Auto-configured):**
```
DB_URL=sqlite:///./app.db
```

### Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_CLAUDE_REAL` | `false` | Set to `true` to use actual Claude API |
| `ANTHROPIC_API_KEY` | - | Required when `USE_CLAUDE_REAL=true` |
| `CLAUDE_MODEL` | `claude-3-5-sonnet-latest` | Claude model to use |
| `DB_URL` | `sqlite:///./app.db` | Database connection string |
| `ALLOW_ORIGINS` | `http://localhost:5173` | CORS allowed origins |
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Frontend API endpoint |

## Step 2: Install Dependencies

Dependencies should auto-install, but if needed:

### Backend (Python)
```bash
cd backend-fastapi
pip install -r requirements.txt
```

### Frontend (Node.js)
```bash
npm install
```

## Step 3: Start the Application

You need to run **two separate processes** - one for backend, one for frontend.

### Option A: Using Replit Shell (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend-fastapi
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
npm run dev -- --host
```

### Option B: Using .replit Configuration

Configure `.replit` file:

```toml
run = "npm run dev -- --host & cd backend-fastapi && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

Then click the "Run" button in Replit.

## Step 4: Access the Application

### Frontend (User Interface)
- **Local:** http://localhost:5173
- **Replit Preview:** Click the preview window or use the Replit-generated URL

### Backend (API)
- **Local:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check:** http://localhost:8000/health

## Step 5: Test the System

### Quick Health Check

Visit: http://localhost:8000/

Expected response:
```json
{
  "service": "Medical Doc AI",
  "version": "1.0.0",
  "stub_mode": true,
  "endpoints": {...}
}
```

### Upload a Test Document

1. Open the frontend UI (http://localhost:5173)
2. Click or drag a PDF/TXT file
3. Click "Upload & Run Pipeline"
4. View classification, codes, and summary results

### Manual API Test

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "document_text": "COMPLETE BLOOD COUNT\nWBC 12.5 K/uL (H)\nHemoglobin 9.2 g/dL (L)\nPlatelets 245 K/uL"
  }'
```

Expected: `"document_type": "COMPLETE BLOOD COUNT"` with high confidence

## Step 6: Testing with Evaluation Dataset

Use the provided test cases:

```bash
# View test cases
cat evals/datasets/test-documents.json

# Test classification (copy document_text from test case)
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"document_text": "..."}'
```

See `evals/README.md` for more test examples.

## Common Issues & Solutions

### Issue: Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
cd backend-fastapi
pip install -r requirements.txt
```

### Issue: Frontend can't connect to backend

**Error:** Network errors in browser console

**Solution:**
1. Verify backend is running: http://localhost:8000/health
2. Check `VITE_API_BASE_URL` in `.env` or Replit Secrets
3. Update CORS in backend if using different origins:
   - Add your Replit preview URL to `ALLOW_ORIGINS`

### Issue: Database errors

**Error:** `sqlite3.OperationalError`

**Solution:**
```bash
cd backend-fastapi
# Remove existing database
rm app.db
# Restart backend (database will auto-initialize)
```

### Issue: Stub mode not returning results

**Symptom:** Empty or missing classifications

**Solution:**
1. Verify `USE_CLAUDE_REAL=false` in Secrets
2. Check backend logs for errors
3. Ensure prompt files exist: `ls backend-fastapi/app/services/prompts/`

### Issue: Port already in use

**Error:** `OSError: [Errno 98] Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
# Or use different port
uvicorn app.main:app --port 8001
```

## Development Workflow

### Making Changes to Prompts

1. Edit prompt files in `backend-fastapi/app/services/prompts/`
2. Save changes
3. Restart backend server (auto-reload enabled with `--reload` flag)
4. Test with evaluation dataset

### Adding New Features

1. **Frontend:** Edit files in `client/src/`
   - Hot reload is automatic
2. **Backend:** Edit files in `backend-fastapi/app/`
   - Auto-reload enabled with `--reload` flag
3. **Shared Types:** Edit `shared/schema.ts`
   - May need to restart both servers

### Database Schema Changes

1. Edit models in `backend-fastapi/app/db/models.py`
2. Delete existing database: `rm backend-fastapi/app.db`
3. Restart backend (database auto-recreates)

## Deploying to Production

### Enable Real Claude API

1. Get API key from https://console.anthropic.com/
2. Add to Replit Secrets: `ANTHROPIC_API_KEY=sk-ant-...`
3. Set `USE_CLAUDE_REAL=true`
4. Restart backend

### Security Checklist

- [ ] All secrets in Replit Secrets (not in code)
- [ ] CORS origins properly configured
- [ ] File upload limits set appropriately
- [ ] API rate limiting configured (if needed)
- [ ] PHI data de-identified before processing

## Getting Help

### Check Logs

**Backend logs:**
```bash
# Logs appear in terminal where uvicorn is running
# Look for stack traces and error messages
```

**Frontend logs:**
```bash
# Open browser DevTools > Console
# Check for network errors and API responses
```

### Test Individual Components

**Test classification:**
```bash
curl -X POST http://localhost:8000/classify -H "Content-Type: application/json" -d '{"document_text": "CHEST X-RAY: Mild cardiomegaly"}'
```

**Test code extraction:**
```bash
curl -X POST http://localhost:8000/extract-codes -H "Content-Type: application/json" -d '{"document_text": "Hemoglobin 9.2 g/dL - anemia"}'
```

**Test summary:**
```bash
curl -X POST http://localhost:8000/summarize -H "Content-Type: application/json" -d '{"document_text": "Potassium 6.1 mEq/L (H)"}'
```

### Resources

- **API Documentation:** http://localhost:8000/docs
- **Evaluation Tests:** `evals/README.md`
- **Prompt Engineering:** `backend-fastapi/app/services/prompts/README.md`
- **Main README:** `README.md`

## Next Steps

1. ✅ Complete setup and test basic upload
2. ✅ Run evaluation dataset tests
3. ✅ Customize prompts for your use case
4. ✅ Enable real Claude API when ready
5. ✅ Add custom document types if needed
6. ✅ Integrate with your clinical workflow

Happy coding! 🚀
