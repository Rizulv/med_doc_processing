# 📋 Medical Document AI - Current Setup Summary

**Last Updated**: October 30, 2025  
**Status**: ✅ Deployed to AWS EKS  
**Environment**: Development (`dev` namespace)

---

## 🏗️ Infrastructure Overview

### AWS Resources

| Resource | Name/ID | Purpose | Status |
|----------|---------|---------|--------|
| **EKS Cluster** | `med-doc-dev` | Kubernetes cluster | ✅ Running |
| **ECR Repository** | `med-doc-backend` | Backend Docker images | ✅ Active |
| **ECR Repository** | `med-doc-frontend` | Frontend Docker images | ✅ Active |
| **S3 Bucket** | `med-docs-dev` | Document storage | ✅ Active |
| **LoadBalancer** | Auto-generated | Public access point | ✅ Active |
| **IAM Role** | `med-doc-api-role` | Pod S3 access | ✅ Active |
| **IAM User** | `ci-cd-user` | Manual deployments | ✅ Active |

### Kubernetes Resources

| Resource | Name | Replicas | Status |
|----------|------|----------|--------|
| **Deployment** | `api` | 2 pods | ✅ Running |
| **Deployment** | `web` | 2 pods | ✅ Running |
| **Service** | `api` (ClusterIP) | Internal | ✅ Active |
| **Service** | `web` (LoadBalancer) | External | ✅ Active |
| **ServiceAccount** | `api-sa` | IAM integration | ✅ Active |
| **Secret** | `api-secrets` | Anthropic API key | ✅ Active |
| **Namespace** | `dev` | Application isolation | ✅ Active |

---

## 💾 Storage Architecture

### Current Implementation (v1)

```
┌─────────────────┐
│   User Upload   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI Backend│─────▶│  Amazon S3   │  ← Uploaded documents
└────────┬────────┘      │ med-docs-dev │
         │               └──────────────┘
         ▼
┌─────────────────┐
│  SQLite (Pod)   │  ← Metadata (ephemeral)
└─────────────────┘
```

**Features**:
- ✅ Documents stored in S3 (`med-docs-dev` bucket)
- ✅ Metadata stored in SQLite (inside pod - ephemeral)
- ✅ Pods have IAM role for S3 access
- ⚠️ Database resets on pod restart (OK for testing)

### Storage Configuration

**Backend Environment Variables**:
```bash
STORAGE_BACKEND=s3              # Use S3 for file storage
S3_BUCKET_NAME=med-docs-dev     # S3 bucket name
AWS_REGION=ap-south-1           # AWS region
DB_URL=sqlite:////data/app.db   # SQLite database (ephemeral)
```

**Local Development**:
```bash
STORAGE_BACKEND=local           # Use local filesystem
```

---

## 🔐 Security & Credentials

### Secrets Management

**Kubernetes Secrets** (`api-secrets`):
```yaml
ANTHROPIC_API_KEY: sk-ant-api03-...
```

**IAM Permissions**:
- `med-doc-api-role`: Allows pods to read/write S3
- `ci-cd-user`: Allows manual deployments (ECR, EKS, S3)

### API Keys

- **Claude API**: Stored in Kubernetes secret
- **AWS Credentials**: Pod IAM role (no long-lived keys in code)

---

## 🚀 Deployment Methods

### Method 1: Manual Deployment (Current)

```powershell
# From local machine
.\deploy-aws.ps1
```

**What it does**:
1. Builds Docker images locally
2. Pushes to ECR
3. Applies Kubernetes manifests
4. Restarts pods with new images

**When to use**: Development, testing, manual updates

### Method 2: GitHub Actions CI/CD (Next Step)

```yaml
# Triggers on: push to main branch
# Workflow: .github/workflows/ci-cd.yml
```

**What it does**:
1. Automatically builds images on code push
2. Pushes to ECR
3. Deploys to EKS
4. Zero manual intervention

**When to use**: Production, team collaboration

---

## 🌐 Access Points

### Production URLs

| Service | URL | Access |
|---------|-----|--------|
| **Frontend** | `http://ad28ddbf3abfb43588a27433f489cfb0-826398851.ap-south-1.elb.amazonaws.com` | Public |
| **API** | Internal only (ClusterIP) | Pod-to-pod |

### API Endpoints

```
GET  /health                    - Health check
POST /documents                 - Upload document
GET  /documents                 - List documents
GET  /documents/{id}            - Get document details
POST /classify                  - Classify document
POST /extract                   - Extract codes
POST /summarize                 - Summarize document
POST /pipeline                  - Run full pipeline
```

---

## 📦 Docker Images

### Backend (`med-doc-backend:latest`)

**Base**: `python:3.12-slim`  
**Dependencies**: FastAPI, Anthropic SDK, boto3, SQLAlchemy  
**Port**: 8000  
**Health**: `/health` endpoint

**Recent Changes**:
- ✅ Added boto3 for S3 access
- ✅ Storage factory (auto-switches local/S3)
- ✅ Runs as non-root user (`appuser`)

### Frontend (`med-doc-frontend:latest`)

**Base**: `node:20-alpine` → `nginx:alpine`  
**Build Tool**: Vite  
**Port**: 80  
**Proxy**: Nginx reverse proxy to backend

**Nginx Configuration**:
- Serves React SPA from `/`
- Proxies `/api/*` to backend ClusterIP
- Proxies `/health`, `/documents` to backend

---

## 🔧 Configuration Files

### Kubernetes Manifests

```
k8s/base/
├── api-deployment.yaml          # Backend deployment
├── web-deployment.yaml          # Frontend deployment
└── iam-serviceaccount.yaml      # IAM service account for S3
```

### Docker Files

```
backend-fastapi/
├── Dockerfile                   # Backend container
└── .dockerignore

Dockerfile.frontend              # Frontend container (root)
.dockerignore                    # Frontend ignore rules
```

### CI/CD

```
.github/workflows/
└── ci-cd.yml                    # GitHub Actions workflow (ready)
```

---

## 🧪 Testing

### Local Testing

```powershell
# Start local environment
docker compose up

# Access app
http://localhost:5173  # Frontend
http://localhost:8000  # Backend API
```

### AWS Testing

```powershell
# Deploy to AWS
.\deploy-aws.ps1

# Get LoadBalancer URL
kubectl -n dev get svc web

# Check logs
kubectl -n dev logs -f deployment/api
kubectl -n dev logs -f deployment/web
```

---

## 📊 Monitoring

### Pod Status

```bash
# Check pod health
kubectl -n dev get pods

# View pod details
kubectl -n dev describe pod <pod-name>

# Check pod logs
kubectl -n dev logs -f deployment/api --tail=100
```

### Resource Usage

```bash
# Check pod resource usage
kubectl -n dev top pods

# Check node resource usage
kubectl top nodes
```

### Events

```bash
# View recent events
kubectl -n dev get events --sort-by='.lastTimestamp'
```

---

## 🛠️ Common Tasks

### Update Code

```powershell
# 1. Make code changes
# 2. Run deployment
.\deploy-aws.ps1
```

### Scale Deployments

```bash
# Scale up
kubectl -n dev scale deployment/api --replicas=4

# Scale down
kubectl -n dev scale deployment/api --replicas=1
```

### Update Secrets

```bash
# Delete old secret
kubectl -n dev delete secret api-secrets

# Create new secret
kubectl -n dev create secret generic api-secrets \
  --from-literal=ANTHROPIC_API_KEY=new-key-here
```

### View S3 Files

```bash
# List uploaded documents
aws s3 ls s3://med-docs-dev/ --recursive

# Download a file
aws s3 cp s3://med-docs-dev/<uuid>/<filename> ./
```

---

## 🚧 Roadmap (v2)

### Planned Improvements

1. **Persistent Database**
   - Replace SQLite with Amazon RDS PostgreSQL
   - Or mount EFS/EBS for SQLite persistence

2. **GitHub Actions CI/CD**
   - Set up OIDC authentication
   - Automated deployments on PR merge
   - Automated tests before deploy

3. **Custom Domain + HTTPS**
   - Register domain in Route53
   - SSL certificate from ACM
   - HTTPS termination at LoadBalancer

4. **Monitoring & Alerts**
   - CloudWatch dashboards
   - Prometheus + Grafana
   - Slack/email alerts

5. **Blue-Green Deployments**
   - Zero-downtime deployments
   - Automatic rollback on failure

6. **Multi-Environment**
   - Staging environment
   - Production environment
   - Environment-specific configs

---

## 📝 Team Collaboration

### Git Workflow (Recommended)

```
main ← production branch (protected)
  ↑
develop ← staging branch
  ↑
feature/... ← feature branches
```

### Branch Protection

- Require pull request reviews
- Require CI checks to pass
- No direct pushes to `main`

### PR Process

1. Create feature branch: `feature/add-pdf-support`
2. Make changes
3. Open PR to `develop`
4. Team reviews code
5. Merge to `develop` → auto-deploy to staging
6. Test in staging
7. Merge `develop` to `main` → auto-deploy to production

---

## 🆘 Troubleshooting

### Issue: Pods in CrashLoopBackOff

```bash
# Check logs
kubectl -n dev logs <pod-name>

# Check events
kubectl -n dev describe pod <pod-name>

# Common causes:
# - Missing environment variables
# - Invalid API keys
# - Health check failures
```

### Issue: LoadBalancer Not Accessible

```bash
# Check service
kubectl -n dev get svc web

# Check security groups
aws ec2 describe-security-groups --group-ids <sg-id>

# Common causes:
# - LoadBalancer still provisioning (wait 5 min)
# - Security group blocking traffic
```

### Issue: S3 Access Denied

```bash
# Check IAM role
aws iam get-role --role-name med-doc-api-role

# Check pod service account
kubectl -n dev get pod <pod-name> -o yaml | grep serviceAccountName

# Common causes:
# - ServiceAccount not attached to pod
# - IAM role trust policy incorrect
```

---

## 📚 Documentation Links

- [AWS Deployment Guide](./AWS_DEPLOYMENT_GUIDE.md)
- [GitHub Actions Setup](./GITHUB_ACTIONS_SETUP.md)
- [Docker Guide](./DOCKER_README.md)
- [Quick Start](./QUICKSTART.md)

---

**🎉 Status**: All systems operational! Ready for GitHub CI/CD integration.
