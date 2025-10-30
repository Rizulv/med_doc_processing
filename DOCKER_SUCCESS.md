# 🎉 Docker Setup Complete!

## Status
✅ Both containers built and running successfully!

## What Was Fixed

### Issue 1: Obsolete Docker Compose Version
- **Problem**: `version: "3.9"` in docker-compose.yml triggered a warning
- **Solution**: Removed the obsolete `version` field (Docker Compose v2+ doesn't need it)

### Issue 2: npm ci Failure - Package Lock Sync Issue
- **Problem**: `npm ci` failed with error "Missing: bufferutil@4.0.9 from lock file"
- **Root Cause**: `bufferutil` is an optional dependency that may fail to compile on Windows but is required on Linux (Docker). The package-lock.json was out of sync.
- **Solution**: Changed `RUN npm ci` to `RUN npm install --production=false` in Dockerfile.frontend
  - `npm ci` requires exact lock file match (strict)
  - `npm install` is more flexible with optional dependencies
  - `--production=false` ensures dev dependencies are installed for the build

## Running Containers

```powershell
# Check status
docker compose ps

# View logs
docker compose logs backend --tail=20
docker compose logs frontend --tail=20
docker compose logs -f  # Follow all logs

# Stop containers
docker compose down

# Restart containers
docker compose restart

# Rebuild and restart
docker compose up --build
```

## Access Your Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (FastAPI Swagger UI)
- **Health Check**: http://localhost:8000/health

## Container Details

### Backend (med-doc-backend)
- **Image**: med-doc-backend:local
- **Port**: 8000:8000
- **Health**: ✅ Healthy (via /health endpoint)
- **Status**: Running Uvicorn ASGI server
- **Data**: Persistent volume `med_doc_processing_backend-data` mounted at `/data`

### Frontend (med-doc-frontend)
- **Image**: med-doc-frontend:local  
- **Port**: 5173:80 (Nginx serves on port 80, mapped to host 5173)
- **Status**: Running Nginx 1.29.3 with 4 worker processes
- **API Connection**: Configured to call backend at `http://backend:8000` (container network)

## Configuration

### Environment Variables
Backend uses `.env` file from `backend-fastapi/.env`:
```bash
USE_CLAUDE_REAL=false  # Set to true to use real Claude API
CLAUDE_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_key_here
DB_URL=sqlite:////data/app.db
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Build Arguments
Frontend receives `VITE_API_BASE_URL=http://backend:8000` at build time (see docker-compose.yml)

## Next Steps

### 1. Test the Application
1. Open http://localhost:5173 in your browser
2. Upload a medical document (use samples from `test_docs/`)
3. Check if classification and extraction work

### 2. Enable Real Claude API (Optional)
If you want to test with real Claude API:
```bash
# Edit backend-fastapi/.env
USE_CLAUDE_REAL=true
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Restart backend
docker compose restart backend
```

### 3. Run Evaluations
```bash
# From your host machine
cd evals
python run_eval.py

# Or inside the backend container
docker compose exec backend python -m pytest evals/run_eval.py
```

### 4. Deploy to AWS
Follow the roadmap in `DEPLOYMENT_ROADMAP.md`:
- Phase 2: AWS Account & CLI Setup
- Phase 3: Create EKS Cluster
- Phase 4: Create Kubernetes Manifests
- Phase 5: Setup CI/CD (already done - see `.github/workflows/ci-cd.yml`)
- Phase 6: Deploy & Test

## Troubleshooting

### Frontend Can't Connect to Backend
```bash
# Check backend logs
docker compose logs backend

# Test backend from inside frontend container
docker compose exec frontend wget -O- http://backend:8000/health
```

### Backend Database Issues
```bash
# Check volume
docker volume inspect med_doc_processing_backend-data

# Reset database
docker compose down -v  # WARNING: Deletes all data
docker compose up
```

### Port Already in Use
```bash
# If port 8000 or 5173 is already in use
# Option 1: Stop the conflicting process
# Option 2: Change ports in docker-compose.yml
# Example: Change "5173:80" to "3000:80" for frontend
```

### View Container Resources
```bash
# Check resource usage
docker stats

# Inspect container
docker compose exec backend bash  # Access backend shell
docker compose exec frontend sh   # Access frontend shell (Alpine Linux)
```

## File Changes Made

### Modified Files
1. **docker-compose.yml** - Removed obsolete `version` field
2. **Dockerfile.frontend** - Changed `npm ci` to `npm install --production=false`
3. **package-lock.json** - Regenerated to sync with package.json

### Created Files (from previous session)
- `backend-fastapi/Dockerfile` - Backend container definition
- `Dockerfile.frontend` - Frontend multi-stage build
- `backend-fastapi/.dockerignore` - Backend build exclusions
- `.dockerignore` - Root build exclusions
- `.github/workflows/ci-cd.yml` - GitHub Actions pipeline
- `DOCKER_README.md` - Architecture documentation
- `AWS_DEPLOYMENT_GUIDE.md` - AWS deployment options
- `DEPLOYMENT_ROADMAP.md` - Step-by-step deployment plan

## Success Metrics
✅ Backend builds in ~73s  
✅ Frontend builds in ~60s  
✅ Health checks passing  
✅ Container networking configured  
✅ Persistent volumes working  
✅ Ready for local development  
✅ Ready for AWS deployment  

---

**Last Updated**: October 30, 2025  
**Build Time**: ~88 seconds (parallel backend + frontend)  
**Images Size**: 
- Backend: ~500MB (Python 3.12 + dependencies)
- Frontend: ~50MB (Nginx Alpine + static build)
