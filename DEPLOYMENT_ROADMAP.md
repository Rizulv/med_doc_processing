# Medical Document AI — Step-by-Step AWS Deployment Roadmap

> **Goal:** Take your local dev setup to production-ready AWS infrastructure with CI/CD, evaluation gates, and team collaboration workflows.

---

## 📋 Overview

**Current State:**
- ✅ Backend FastAPI working locally (port 8000)
- ✅ Frontend React/Vite working locally (port 5173)
- ✅ Claude integration functional
- ✅ Basic eval endpoint (`/eval/quick`)

**Target State:**
- ✅ Dockerized backend & frontend
- ✅ Deployed to AWS EKS (Kubernetes)
- ✅ CI/CD with GitHub Actions
- ✅ Evaluation gates blocking bad deployments
- ✅ Team-ready with proper secrets management

---

## 🗺️ Deployment Phases

| Phase | What | Time Estimate |
|-------|------|---------------|
| **Phase 0** | Repo Hygiene & Local Hardening | 2-3 hours |
| **Phase 1** | Dockerization (Local Testing) | 2-4 hours |
| **Phase 2** | AWS Foundation Setup | 3-4 hours |
| **Phase 3** | EKS Cluster Creation | 1-2 hours |
| **Phase 4** | Kubernetes Manifests | 2-3 hours |
| **Phase 5** | CI/CD Pipeline | 3-4 hours |
| **Phase 6** | Evaluation Improvements | 4-6 hours |
| **Phase 7** | Production Hardening | 2-3 hours |
| **Total** | | **~20-30 hours** |

---

# PHASE 0: Repo Hygiene & Local Hardening

## Step 0.1: Create Environment Template

**Why:** Never commit secrets; teammates create their own `.env` from a template.

**Action:**

```bash
# From repo root
cd backend-fastapi
```

Create `backend-fastapi/.env.sample`:

```env
# LLM Configuration
USE_CLAUDE_REAL=false
CLAUDE_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=YOUR_KEY_HERE

# Database
DB_URL=sqlite:///./app.db

# CORS (comma-separated)
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# AWS (for production)
AWS_REGION=ap-south-1
S3_BUCKET=med-docs-dev
```

**Add to `.gitignore`:**

```bash
# Add this to your root .gitignore
backend-fastapi/.env
.env
*.env
!.env.sample
```

**Verify:**

```bash
git status  # .env should NOT appear
```

---

## Step 0.2: Update Current .env

**Action:** Update your actual `.env` to fix the CORS trailing slash issue:

```bash
# In backend-fastapi/.env
ALLOW_ORIGINS=http://localhost:5173,http://localhost:5174,http://127.0.0.1:8000
```

**Why:** Remove trailing slash from `http://localhost:5174/` — causes CORS errors.

---

## Step 0.3: Create Documentation Structure

**Action:**

```bash
mkdir -p docs
```

Create placeholder docs (we'll fill these in phases):

```bash
# docs/deployment.md
# docs/evaluation.md
# docs/prompts-guide.md
# docs/team-workflow.md
```

---

## Step 0.4: Test Local Setup

**Verify everything works before containerizing:**

```bash
# Terminal 1: Backend
cd backend-fastapi
. .venv/Scripts/Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2: Frontend (from repo root)
npm install
npm run frontend:dev

# Terminal 3: Test
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/eval/quick
```

**Expected:**
- Backend: `{"status": "healthy"}`
- Eval: JSON with metrics
- Frontend: Opens at http://localhost:5173

**✅ Checkpoint:** Local dev works perfectly.

---

# PHASE 1: Dockerization (Local Testing)

## Step 1.1: Create Backend Dockerfile

**Action:** Create `backend-fastapi/Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies (for psycopg2 if using PostgreSQL later)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Create directory for SQLite (if using file-based DB)
RUN mkdir -p /data

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Test build:**

```bash
cd backend-fastapi
docker build -t med-doc-backend:local .
```

**Test run:**

```bash
docker run -p 8000:8000 \
  -e USE_CLAUDE_REAL=false \
  -e CLAUDE_MODEL=claude-3-5-sonnet-20241022 \
  -e DB_URL=sqlite:////data/app.db \
  -e ALLOW_ORIGINS=http://localhost:5173 \
  med-doc-backend:local
```

**Verify:**

```bash
curl http://127.0.0.1:8000/health
# Should return: {"status": "healthy"}
```

**✅ Checkpoint:** Backend Docker image works.

---

## Step 1.2: Create Frontend Dockerfile

**Action:** Create `client/Dockerfile`:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build app
ENV VITE_API_BASE_URL=http://localhost:8000
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config (optional, create if needed)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Wait!** The frontend build needs to happen from repo root (because `vite.config.ts` is there).

**Better approach:** Create `Dockerfile` at repo root for frontend:

Create `Dockerfile.frontend` at repo root:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies
RUN npm ci

# Copy all source (client/, shared/, vite.config.ts, etc.)
COPY . .

# Build frontend
ENV VITE_API_BASE_URL=http://localhost:8000
RUN npm run frontend:build

# Stage 2: Serve
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist/public /usr/share/nginx/html

# Create nginx config for SPA routing
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Test build:**

```bash
# From repo root
docker build -f Dockerfile.frontend -t med-doc-frontend:local .
```

**Test run:**

```bash
docker run -p 5173:80 med-doc-frontend:local
```

**Verify:** Open http://localhost:5173 in browser.

**✅ Checkpoint:** Frontend Docker image works.

---

## Step 1.3: Create Docker Compose for Local Testing

**Action:** Create `docker-compose.yml` at repo root:

```yaml
version: "3.9"

services:
  backend:
    build:
      context: ./backend-fastapi
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - USE_CLAUDE_REAL=false
      - CLAUDE_MODEL=claude-3-5-sonnet-20241022
      - DB_URL=sqlite:////data/app.db
      - ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
      - AWS_REGION=ap-south-1
      - S3_BUCKET=med-docs-dev
    volumes:
      - backend-data:/data
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 10s
      timeout: 5s
      retries: 3

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:80"
    depends_on:
      backend:
        condition: service_healthy
    environment:
      - VITE_API_BASE_URL=http://localhost:8000

volumes:
  backend-data:
```

**Test:**

```bash
docker compose up --build
```

**Verify:**
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Upload a test document

**✅ Checkpoint:** Full stack works in Docker locally.

---

# PHASE 2: AWS Foundation Setup

## Step 2.1: Install AWS CLI & eksctl

**Install AWS CLI:**

```bash
# Windows (PowerShell as Admin)
msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi

# Verify
aws --version
```

**Install eksctl:**

```bash
# Windows (using Chocolatey)
choco install eksctl

# Or download from: https://github.com/weaveworks/eksctl/releases
# Verify
eksctl version
```

**Install kubectl:**

```bash
choco install kubernetes-cli

# Verify
kubectl version --client
```

---

## Step 2.2: Configure AWS Credentials

**Action:**

```bash
aws configure
```

**Enter:**
- AWS Access Key ID: `[from IAM user]`
- AWS Secret Access Key: `[from IAM user]`
- Default region: `ap-south-1`
- Default output format: `json`

**Verify:**

```bash
aws sts get-caller-identity
# Should show your AWS account ID and user ARN
```

**✅ Checkpoint:** AWS CLI configured.

---

## Step 2.3: Create ECR Repositories

**Action:**

```bash
# Create backend repository
aws ecr create-repository \
  --repository-name med-doc-backend \
  --region ap-south-1

# Create frontend repository
aws ecr create-repository \
  --repository-name med-doc-frontend \
  --region ap-south-1
```

**Save the repository URIs** (you'll need them later):

```bash
aws ecr describe-repositories \
  --repository-names med-doc-backend med-doc-frontend \
  --region ap-south-1 \
  --query 'repositories[*].[repositoryName,repositoryUri]' \
  --output table
```

**Example output:**
```
---------------------------------------------------------
|                 DescribeRepositories                   |
+-------------------+------------------------------------+
|  med-doc-backend  |  123456789.dkr.ecr.ap-south-1...   |
|  med-doc-frontend |  123456789.dkr.ecr.ap-south-1...   |
+-------------------+------------------------------------+
```

**Save these URIs** — we'll use them in k8s manifests.

**✅ Checkpoint:** ECR repositories created.

---

## Step 2.4: Create S3 Buckets

**Action:**

```bash
# Dev bucket
aws s3 mb s3://med-docs-dev --region ap-south-1

# Enable versioning (optional but recommended)
aws s3api put-bucket-versioning \
  --bucket med-docs-dev \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket med-docs-dev \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

**Verify:**

```bash
aws s3 ls
# Should show: med-docs-dev
```

**✅ Checkpoint:** S3 bucket created.

---

## Step 2.5: Push Initial Images to ECR

**Login to ECR:**

```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.ap-south-1.amazonaws.com
```

**Tag and push backend:**

```bash
# Get your ECR URI from step 2.3
export ECR_BACKEND="123456789.dkr.ecr.ap-south-1.amazonaws.com/med-doc-backend"

docker tag med-doc-backend:local $ECR_BACKEND:latest
docker push $ECR_BACKEND:latest
```

**Tag and push frontend:**

```bash
export ECR_FRONTEND="123456789.dkr.ecr.ap-south-1.amazonaws.com/med-doc-frontend"

docker tag med-doc-frontend:local $ECR_FRONTEND:latest
docker push $ECR_FRONTEND:latest
```

**Verify:**

```bash
aws ecr list-images --repository-name med-doc-backend --region ap-south-1
aws ecr list-images --repository-name med-doc-frontend --region ap-south-1
```

**✅ Checkpoint:** Docker images in ECR.

---

# PHASE 3: EKS Cluster Creation

## Step 3.1: Create Cluster Config

**Action:** Create `cloud/eksctl/cluster-config.yaml`:

```bash
mkdir -p cloud/eksctl
```

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: med-doc-dev
  region: ap-south-1
  version: "1.30"

# Managed node groups (auto-scaling)
managedNodeGroups:
  - name: ng-general
    instanceTypes: ["t3.medium"]  # 2 vCPU, 4GB RAM
    desiredCapacity: 2
    minSize: 2
    maxSize: 4
    volumeSize: 20
    volumeType: gp3
    labels:
      role: general
    tags:
      environment: dev
      project: med-doc-ai

# IAM OIDC provider (needed for service accounts with IAM roles)
iam:
  withOIDC: true

# CloudWatch logging
cloudWatch:
  clusterLogging:
    enableTypes: ["api", "audit", "authenticator"]
```

---

## Step 3.2: Create EKS Cluster

**Action:**

```bash
eksctl create cluster -f cloud/eksctl/cluster-config.yaml
```

**This will take ~15-20 minutes.** It creates:
- EKS control plane
- VPC with subnets
- Node group (2x t3.medium EC2 instances)
- Security groups
- IAM roles

**Monitor progress:**

```bash
# In another terminal
aws eks describe-cluster --name med-doc-dev --region ap-south-1 --query 'cluster.status'
```

**When complete:**

```bash
# Update kubeconfig
aws eks update-kubeconfig --name med-doc-dev --region ap-south-1

# Verify nodes
kubectl get nodes
```

**Expected output:**
```
NAME                                           STATUS   ROLES    AGE   VERSION
ip-192-168-X-X.ap-south-1.compute.internal     Ready    <none>   5m    v1.30.x
ip-192-168-Y-Y.ap-south-1.compute.internal     Ready    <none>   5m    v1.30.x
```

**✅ Checkpoint:** EKS cluster running.

---

## Step 3.3: Create Kubernetes Namespace

**Action:**

```bash
kubectl create namespace dev
kubectl get namespaces
```

**✅ Checkpoint:** `dev` namespace created.

---

# PHASE 4: Kubernetes Manifests

## Step 4.1: Create Directory Structure

**Action:**

```bash
mkdir -p k8s/base
mkdir -p k8s/dev
```

---

## Step 4.2: Create ConfigMap

**Action:** Create `k8s/dev/api-config.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
  namespace: dev
data:
  DB_URL: "sqlite:////data/app.db"
  ALLOW_ORIGINS: "http://localhost:5173,http://localhost:8000"
  AWS_REGION: "ap-south-1"
  S3_BUCKET: "med-docs-dev"
  CLAUDE_MODEL: "claude-3-5-sonnet-20241022"
```

**Apply:**

```bash
kubectl apply -f k8s/dev/api-config.yaml
```

---

## Step 4.3: Create Secrets

**Action:**

```bash
# Replace YOUR_ANTHROPIC_KEY with your actual key
kubectl -n dev create secret generic api-secrets \
  --from-literal=USE_CLAUDE_REAL=true \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

**Verify:**

```bash
kubectl -n dev get secrets
kubectl -n dev describe secret api-secrets
```

**✅ Checkpoint:** ConfigMap and Secrets created.

---

## Step 4.4: Create Backend Deployment

**Action:** Create `k8s/base/api-deployment.yaml`:

**⚠️ Important:** Replace `<YOUR_ECR_URI>` with your actual ECR URI from Step 2.3.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  namespace: dev
  labels:
    app: api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: 123456789.dkr.ecr.ap-south-1.amazonaws.com/med-doc-backend:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
              name: http
          env:
            - name: USE_CLAUDE_REAL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: USE_CLAUDE_REAL
            - name: ANTHROPIC_API_KEY
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: ANTHROPIC_API_KEY
            - name: CLAUDE_MODEL
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: CLAUDE_MODEL
            - name: DB_URL
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: DB_URL
            - name: ALLOW_ORIGINS
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: ALLOW_ORIGINS
            - name: AWS_REGION
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: AWS_REGION
            - name: S3_BUCKET
              valueFrom:
                configMapKeyRef:
                  name: api-config
                  key: S3_BUCKET
          resources:
            requests:
              memory: "512Mi"
              cpu: "250m"
            limits:
              memory: "1Gi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api
  namespace: dev
spec:
  selector:
    app: api
  ports:
    - name: http
      port: 80
      targetPort: 8000
  type: ClusterIP
```

**Apply:**

```bash
kubectl apply -f k8s/base/api-deployment.yaml
```

**Verify:**

```bash
kubectl -n dev get pods
kubectl -n dev get svc
```

**Test backend (port-forward):**

```bash
kubectl -n dev port-forward svc/api 8000:80
```

**In another terminal:**

```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy"}
```

**✅ Checkpoint:** Backend deployed to EKS.

---

## Step 4.5: Create Frontend Deployment

**Action:** Create `k8s/base/web-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
  namespace: dev
  labels:
    app: web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: 123456789.dkr.ecr.ap-south-1.amazonaws.com/med-doc-frontend:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 80
              name: http
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: web
  namespace: dev
spec:
  selector:
    app: web
  ports:
    - name: http
      port: 80
      targetPort: 80
  type: LoadBalancer
```

**Apply:**

```bash
kubectl apply -f k8s/base/web-deployment.yaml
```

**Get external IP (this may take 2-3 minutes):**

```bash
kubectl -n dev get svc web -w
```

**Wait for EXTERNAL-IP to appear:**

```
NAME   TYPE           CLUSTER-IP     EXTERNAL-IP                                     PORT(S)
web    LoadBalancer   10.100.X.X     a1234567890abcdef.ap-south-1.elb.amazonaws.com  80:30XXX/TCP
```

**Copy the EXTERNAL-IP** and open in browser.

**⚠️ Problem:** Frontend will try to call backend at `http://localhost:8000` (from browser), which won't work.

**Fix:** We need to update frontend to call the internal K8s service or expose backend via Ingress.

---

## Step 4.6: Fix Frontend-Backend Communication

**Option A: Use Ingress (Recommended)**

We'll set up nginx-ingress to route:
- `/` → frontend
- `/api/*` → backend

**Install nginx-ingress controller:**

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.1/deploy/static/provider/aws/deploy.yaml
```

**Wait for LoadBalancer IP:**

```bash
kubectl -n ingress-nginx get svc ingress-nginx-controller -w
```

**Create Ingress:** `k8s/dev/ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: app-ingress
  namespace: dev
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: api
                port:
                  number: 80
          - path: /()(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: web
                port:
                  number: 80
```

**Apply:**

```bash
kubectl apply -f k8s/dev/ingress.yaml
```

**Get Ingress IP:**

```bash
kubectl -n dev get ingress
```

**Update frontend build** to use `/api` prefix:

Update `Dockerfile.frontend`:

```dockerfile
# Change this line:
ENV VITE_API_BASE_URL=http://localhost:8000
# To:
ENV VITE_API_BASE_URL=/api
```

**Rebuild and push:**

```bash
docker build -f Dockerfile.frontend -t $ECR_FRONTEND:latest .
docker push $ECR_FRONTEND:latest

# Restart frontend pods
kubectl -n dev rollout restart deployment/web
```

**Update backend CORS** in ConfigMap:

```yaml
# k8s/dev/api-config.yaml
data:
  ALLOW_ORIGINS: "*"  # Or specific domain later
```

```bash
kubectl apply -f k8s/dev/api-config.yaml
kubectl -n dev rollout restart deployment/api
```

**Test:** Open Ingress LoadBalancer URL in browser.

**✅ Checkpoint:** Full app accessible via single LoadBalancer URL.

---

# PHASE 5: CI/CD Pipeline

## Step 5.1: Create GitHub Repository Secrets

**Go to GitHub repo → Settings → Secrets and variables → Actions**

**Add these secrets:**

| Name | Value | How to Get |
|------|-------|------------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | IAM user credentials |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | IAM user credentials |
| `AWS_REGION` | `ap-south-1` | Your region |
| `ECR_BACKEND_URI` | `123...ecr...med-doc-backend` | From Step 2.3 |
| `ECR_FRONTEND_URI` | `123...ecr...med-doc-frontend` | From Step 2.3 |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | Your Anthropic key |

---

## Step 5.2: Create CI Workflow (Build & Push)

**Action:** Create `.github/workflows/ci-build.yml`:

```yaml
name: CI Build & Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: ap-south-1

jobs:
  build-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        id: ecr-login
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push backend
        run: |
          cd backend-fastapi
          docker build -t ${{ secrets.ECR_BACKEND_URI }}:${{ github.sha }} .
          docker tag ${{ secrets.ECR_BACKEND_URI }}:${{ github.sha }} ${{ secrets.ECR_BACKEND_URI }}:latest
          docker push ${{ secrets.ECR_BACKEND_URI }}:${{ github.sha }}
          docker push ${{ secrets.ECR_BACKEND_URI }}:latest

  build-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push frontend
        run: |
          docker build -f Dockerfile.frontend -t ${{ secrets.ECR_FRONTEND_URI }}:${{ github.sha }} .
          docker tag ${{ secrets.ECR_FRONTEND_URI }}:${{ github.sha }} ${{ secrets.ECR_FRONTEND_URI }}:latest
          docker push ${{ secrets.ECR_FRONTEND_URI }}:${{ github.sha }}
          docker push ${{ secrets.ECR_FRONTEND_URI }}:latest
```

---

## Step 5.3: Create CD Workflow (Deploy to EKS)

**Action:** Create `.github/workflows/cd-deploy-dev.yml`:

```yaml
name: CD Deploy Dev

on:
  push:
    branches: [main]

env:
  AWS_REGION: ap-south-1
  EKS_CLUSTER: med-doc-dev

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }} --region ${{ env.AWS_REGION }}

      - name: Deploy to Kubernetes
        run: |
          kubectl -n dev apply -f k8s/dev/api-config.yaml
          kubectl -n dev apply -f k8s/base/api-deployment.yaml
          kubectl -n dev apply -f k8s/base/web-deployment.yaml
          kubectl -n dev apply -f k8s/dev/ingress.yaml
          
          # Force rollout to pull latest images
          kubectl -n dev rollout restart deployment/api
          kubectl -n dev rollout restart deployment/web
          
          # Wait for rollout
          kubectl -n dev rollout status deployment/api --timeout=5m
          kubectl -n dev rollout status deployment/web --timeout=5m

  eval-gate:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }} --region ${{ env.AWS_REGION }}

      - name: Run evaluation gate
        run: |
          # Port-forward API service in background
          kubectl -n dev port-forward svc/api 18000:80 &
          PF_PID=$!
          sleep 5
          
          # Hit eval endpoint
          RESP=$(curl -s http://127.0.0.1:18000/eval/quick || echo '{}')
          echo "Eval response: $RESP"
          
          # Kill port-forward
          kill $PF_PID || true
          
          # Parse metrics (simple bash example - improve later)
          echo "$RESP" | jq .
          
          # TODO: Add threshold checks
          # For now, just log the response
```

---

## Step 5.4: Test CI/CD

**Action:**

```bash
# Create a small change
echo "# CI/CD test" >> README.md

git add .
git commit -m "test: trigger CI/CD pipeline"
git push origin main
```

**Monitor:**
- Go to GitHub → Actions tab
- Watch workflows run
- Check pods update in EKS:

```bash
kubectl -n dev get pods -w
```

**✅ Checkpoint:** CI/CD pipeline working.

---

# PHASE 6: Evaluation Improvements

## Step 6.1: Create Pre-Classifier Rules

**Action:** Create `backend-fastapi/app/services/pre_classifier.py`:

```python
"""
Pre-classification rules for quick, deterministic classification.
"""
import re
from typing import Optional, Dict, Any

# Document type constants
DOC_TYPE_CBC = "COMPLETE BLOOD COUNT"
DOC_TYPE_BMP = "BASIC METABOLIC PANEL"
DOC_TYPE_XRAY = "X-RAY"
DOC_TYPE_CT = "CT"
DOC_TYPE_NOTE = "CLINICAL NOTE"


def pre_classify(text: str) -> Optional[Dict[str, Any]]:
    """
    Attempt rule-based classification before calling LLM.
    Returns classification dict if confident, None otherwise.
    """
    text_lower = text.lower()
    
    # CBC markers
    cbc_markers = ["wbc", "hemoglobin", "hb", "hematocrit", "platelet", "rbc"]
    cbc_count = sum(1 for m in cbc_markers if m in text_lower)
    
    if cbc_count >= 3:
        return {
            "document_type": DOC_TYPE_CBC,
            "confidence": 0.9,
            "rationale": f"Rule-based: Found {cbc_count} CBC markers ({', '.join([m for m in cbc_markers if m in text_lower])})"
        }
    
    # BMP markers
    bmp_markers = ["sodium", "potassium", "chloride", "bun", "creatinine", "glucose"]
    bmp_count = sum(1 for m in bmp_markers if m in text_lower)
    
    if bmp_count >= 3:
        return {
            "document_type": DOC_TYPE_BMP,
            "confidence": 0.9,
            "rationale": f"Rule-based: Found {bmp_count} BMP markers"
        }
    
    # Imaging markers
    imaging_keywords = ["x-ray", "xray", "radiograph", "chest film"]
    if any(kw in text_lower for kw in imaging_keywords):
        # Look for anatomy
        if any(word in text_lower for word in ["chest", "lung", "rib", "pneumonia"]):
            return {
                "document_type": DOC_TYPE_XRAY,
                "confidence": 0.85,
                "rationale": "Rule-based: X-ray keyword + anatomical terms"
            }
    
    ct_keywords = ["ct scan", "ct head", "ct chest", "computed tomography"]
    if any(kw in text_lower for kw in ct_keywords):
        return {
            "document_type": DOC_TYPE_CT,
            "confidence": 0.85,
            "rationale": "Rule-based: CT imaging keywords"
        }
    
    # If no clear classification, return None (let LLM decide)
    return None
```

**Update `backend-fastapi/app/services/anthropic_client.py`:**

```python
# Add import at top
from app.services.pre_classifier import pre_classify

# In ClaudeClient class, update classify method:
def classify(self, document_text: str):
    """Classify document type with pre-classifier first."""
    
    # Try rule-based first
    pre_result = pre_classify(document_text)
    if pre_result:
        return pre_result
    
    # Fall back to LLM
    if not self.use_real:
        return self._stub_classify()
    
    # ... rest of LLM classification logic
```

**✅ Checkpoint:** Pre-classifier reduces LLM calls.

---

## Step 6.2: Add Evidence-Required Extraction

**Update prompts:** `backend-fastapi/app/services/prompts/codes.md`:

```markdown
# ICD-10 Code Extraction

Extract ICD-10 codes from the medical document.

## CRITICAL RULES:
1. **Evidence Required**: Every code MUST include verbatim quotes from the document
2. **No Hallucinations**: If no clear evidence exists, output ZERO codes
3. **Confidence Scoring**: Rate 0.0-1.0 based on evidence strength

## Output Format (JSON):
```json
{
  "codes": [
    {
      "code": "D64.9",
      "description": "Anemia, unspecified",
      "evidence": ["Hemoglobin 9.2 g/dL (Low)"],
      "confidence": 0.95
    }
  ]
}
```

## Document:
{document_text}

## Document Type:
{document_type}
```

**Update backend validation** in `backend-fastapi/app/routes/extract_codes.py`:

```python
@router.post("/extract-codes")
async def extract_codes(request: ExtractCodesRequest):
    result = client.extract_codes(request.document_text, request.document_type)
    
    # Validate evidence exists
    codes = result.get("codes", [])
    for code in codes:
        if not code.get("evidence"):
            code["confidence"] = max(0.0, code.get("confidence", 0.5) - 0.3)
            code["evidence"] = ["[No evidence found - low confidence]"]
    
    return result
```

**✅ Checkpoint:** Evidence requirement reduces hallucinations.

---

## Step 6.3: Create Full Eval Runner

**Action:** Create `evals/run_full_eval.py`:

```python
"""
Full evaluation runner for classification, extraction, and summarization.
"""
import json
import sys
import argparse
from typing import Dict, List
import requests
from datetime import datetime

def load_dataset(path: str) -> List[Dict]:
    """Load labeled evaluation dataset."""
    with open(path, 'r') as f:
        return json.load(f)

def run_classification_eval(api_base: str, dataset: List[Dict]) -> Dict:
    """Evaluate classification accuracy."""
    correct = 0
    total = len(dataset)
    errors = []
    
    for item in dataset:
        text = item['document_text']
        expected_type = item['expected_type']
        
        resp = requests.post(
            f"{api_base}/classify",
            json={"document_text": text}
        )
        result = resp.json()
        predicted_type = result.get('document_type')
        
        if predicted_type == expected_type:
            correct += 1
        else:
            errors.append({
                'expected': expected_type,
                'predicted': predicted_type,
                'text_preview': text[:100]
            })
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        'accuracy': accuracy,
        'correct': correct,
        'total': total,
        'errors': errors[:10]  # Top 10 errors
    }

def run_codes_eval(api_base: str, dataset: List[Dict]) -> Dict:
    """Evaluate ICD-10 code extraction."""
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    
    for item in dataset:
        if 'expected_codes' not in item:
            continue
        
        text = item['document_text']
        doc_type = item['expected_type']
        expected_codes = set(item['expected_codes'])
        
        resp = requests.post(
            f"{api_base}/extract-codes",
            json={"document_text": text, "document_type": doc_type}
        )
        result = resp.json()
        predicted_codes = set(c['code'] for c in result.get('codes', []))
        
        true_positives += len(expected_codes & predicted_codes)
        false_positives += len(predicted_codes - expected_codes)
        false_negatives += len(expected_codes - predicted_codes)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-base', default='http://127.0.0.1:8000')
    parser.add_argument('--dataset', default='evals/datasets/synthetic_v1.json')
    parser.add_argument('--output', default=f'evals/results/report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json')
    args = parser.parse_args()
    
    print(f"Loading dataset: {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(f"Loaded {len(dataset)} examples")
    
    print("\nRunning classification eval...")
    classification_results = run_classification_eval(args.api_base, dataset)
    print(f"  Accuracy: {classification_results['accuracy']:.2%}")
    
    print("\nRunning codes extraction eval...")
    codes_results = run_codes_eval(args.api_base, dataset)
    print(f"  Precision: {codes_results['precision']:.2%}")
    print(f"  Recall: {codes_results['recall']:.2%}")
    print(f"  F1: {codes_results['f1']:.2%}")
    
    # Compile full report
    report = {
        'timestamp': datetime.now().isoformat(),
        'api_base': args.api_base,
        'dataset': args.dataset,
        'num_examples': len(dataset),
        'classification': classification_results,
        'codes': codes_results
    }
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved: {args.output}")
    
    # Exit with error if below thresholds
    if classification_results['accuracy'] < 0.75 or codes_results['f1'] < 0.65:
        print("\n❌ EVAL GATE FAILED: Metrics below threshold")
        sys.exit(1)
    
    print("\n✅ EVAL GATE PASSED")
    sys.exit(0)

if __name__ == '__main__':
    main()
```

**Test locally:**

```bash
cd evals
python run_full_eval.py --api-base http://127.0.0.1:8000
```

**✅ Checkpoint:** Full eval runner working.

---

## Step 6.4: Add Eval Gate to CI/CD

**Update `.github/workflows/cd-deploy-dev.yml`:**

```yaml
  eval-gate:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install requests

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: |
          aws eks update-kubeconfig --name ${{ env.EKS_CLUSTER }} --region ${{ env.AWS_REGION }}

      - name: Run full evaluation
        run: |
          # Port-forward API
          kubectl -n dev port-forward svc/api 18000:80 &
          PF_PID=$!
          sleep 5
          
          # Run eval
          python evals/run_full_eval.py \
            --api-base http://127.0.0.1:18000 \
            --dataset evals/datasets/synthetic_v1.json \
            --output evals/results/ci-report.json
          
          EXIT_CODE=$?
          
          # Cleanup
          kill $PF_PID || true
          
          # Upload report as artifact
          echo "exit_code=$EXIT_CODE" >> $GITHUB_OUTPUT
          
          exit $EXIT_CODE
        id: eval

      - name: Upload eval report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: eval-report
          path: evals/results/ci-report.json
```

**✅ Checkpoint:** Eval gate integrated in CI/CD.

---

# PHASE 7: Production Hardening

## Step 7.1: Add Resource Limits & Auto-Scaling

**Update deployments with HPA:**

Create `k8s/base/api-hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
  namespace: dev
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

**Apply:**

```bash
kubectl apply -f k8s/base/api-hpa.yaml
```

---

## Step 7.2: Add Monitoring

**Install Metrics Server:**

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

**Verify:**

```bash
kubectl top nodes
kubectl top pods -n dev
```

---

## Step 7.3: Production Checklist

Create `docs/production-checklist.md`:

```markdown
# Production Deployment Checklist

## Pre-Deployment
- [ ] All tests passing locally
- [ ] Eval metrics above thresholds (accuracy ≥0.75, F1 ≥0.65)
- [ ] Docker images built and pushed to ECR
- [ ] Secrets verified in Kubernetes
- [ ] Resource limits configured
- [ ] HPA configured

## Security
- [ ] Secrets stored in Kubernetes Secrets (not ConfigMaps)
- [ ] API keys rotated
- [ ] CORS properly configured
- [ ] HTTPS enabled (via Ingress + cert-manager)
- [ ] Network policies in place

## Monitoring
- [ ] CloudWatch logs enabled
- [ ] Metrics server installed
- [ ] Alerts configured for:
  - Pod crashes
  - High CPU/memory
  - API errors
  - Eval failures

## Backup & Recovery
- [ ] Database backups enabled
- [ ] S3 versioning enabled
- [ ] Disaster recovery plan documented

## Performance
- [ ] Load testing completed
- [ ] Auto-scaling tested
- [ ] Cache strategy implemented

## Documentation
- [ ] README.md updated
- [ ] API docs current
- [ ] Runbooks created
- [ ] Team trained
```

---

# 🎯 Quick Reference Commands

## Local Development

```bash
# Backend
cd backend-fastapi
. .venv/Scripts/Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (from repo root)
npm run frontend:dev

# Docker Compose
docker compose up --build
```

## AWS/Kubernetes

```bash
# Update kubeconfig
aws eks update-kubeconfig --name med-doc-dev --region ap-south-1

# View resources
kubectl -n dev get all
kubectl -n dev get pods
kubectl -n dev logs -f deployment/api

# Port forward for testing
kubectl -n dev port-forward svc/api 8000:80
kubectl -n dev port-forward svc/web 5173:80

# Restart deployments
kubectl -n dev rollout restart deployment/api
kubectl -n dev rollout restart deployment/web

# View logs
kubectl -n dev logs -f deployment/api
kubectl -n dev logs -f deployment/web
```

## ECR

```bash
# Login
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.ap-south-1.amazonaws.com

# Push images
docker tag med-doc-backend:local $ECR_BACKEND:latest
docker push $ECR_BACKEND:latest
```

## Evaluation

```bash
# Quick eval
curl http://127.0.0.1:8000/eval/quick

# Full eval
python evals/run_full_eval.py --api-base http://127.0.0.1:8000
```

---

# 🚨 Troubleshooting

## Pods Not Starting

```bash
# Check pod status
kubectl -n dev describe pod <pod-name>

# Check logs
kubectl -n dev logs <pod-name>

# Common issues:
# - Image pull errors: Check ECR permissions
# - CrashLoopBackOff: Check env vars in secrets/configmaps
# - Pending: Check node resources
```

## Frontend Can't Reach Backend

```bash
# Verify Ingress
kubectl -n dev get ingress
kubectl -n dev describe ingress app-ingress

# Check service endpoints
kubectl -n dev get endpoints

# Test backend directly
kubectl -n dev port-forward svc/api 8000:80
curl http://localhost:8000/health
```

## CI/CD Failing

```bash
# Check GitHub Actions logs
# Common issues:
# - AWS credentials: Verify secrets
# - ECR push: Check repository exists
# - kubectl: Verify kubeconfig update
# - Eval gate: Check /eval/quick endpoint
```

---

# 📚 Next Steps

After completing all phases:

1. **Add HTTPS:** Install cert-manager and configure SSL
2. **Add PostgreSQL:** Replace SQLite with RDS PostgreSQL
3. **Add Redis:** For caching and rate limiting
4. **Improve Evals:** Expand dataset to 50+ examples
5. **Add Monitoring:** Prometheus + Grafana dashboards
6. **Add Alerting:** PagerDuty/Slack integration
7. **Load Testing:** Use k6 or Locust
8. **Cost Optimization:** Spot instances, Reserved capacity

---

**Questions?** Open an issue or check `docs/` folder for detailed guides.
