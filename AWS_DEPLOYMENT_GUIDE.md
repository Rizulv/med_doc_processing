# Medical Document AI — AWS Deployment Guide

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Code Structure](#code-structure)
- [Tech Stack](#tech-stack)
- [Environment Variables](#environment-variables)
- [AWS Architecture](#aws-architecture)
- [Deployment Options](#deployment-options)
- [Step-by-Step AWS Setup](#step-by-step-aws-setup)
- [Cost Estimates](#cost-estimates)
- [Security Considerations](#security-considerations)

---

## 📊 Project Overview

**Medical Document AI** is an AI-powered pipeline that processes medical documents (PDFs/TXT files) and provides:

1. **Document Classification** — Identifies document type with confidence score
   - Complete Blood Count (CBC)
   - Basic Metabolic Panel (BMP)
   - X-Ray
   - CT Scan
   - Clinical Note

2. **ICD-10 Code Extraction** — Extracts medical billing codes with:
   - Evidence snippets from document
   - Confidence scores per code
   - Clinical rationale

3. **Clinical Summaries** — Generates provider-facing summaries

**AI Model:** Anthropic Claude 3.5 Sonnet (via API)

---

## 🏗️ Code Structure

```
med_doc_processing/
├── backend-fastapi/              # Python FastAPI REST API
│   ├── app/
│   │   ├── main.py              # FastAPI app entry, CORS, router registration
│   │   ├── config.py            # Settings (loads .env)
│   │   ├── db/
│   │   │   ├── database.py      # SQLAlchemy engine & session
│   │   │   ├── models.py        # ORM models (Document, DocumentResult)
│   │   │   └── crud.py          # Database operations
│   │   ├── routes/              # API endpoints
│   │   │   ├── health.py        # GET /health
│   │   │   ├── classify.py      # POST /classify
│   │   │   ├── extract_codes.py # POST /extract-codes
│   │   │   ├── summarize.py     # POST /summarize
│   │   │   ├── pipeline.py      # POST /documents (full pipeline)
│   │   │   │                    # GET /documents, GET /documents/{id}
│   │   │   └── eval.py          # GET /eval/quick
│   │   └── services/
│   │       ├── anthropic_client.py  # Claude API wrapper
│   │       ├── text_extract.py      # PDF text extraction (PyPDF)
│   │       ├── storage_local.py     # File storage (local/S3)
│   │       └── prompts/             # Claude prompt templates
│   │           ├── classification.md
│   │           ├── codes.md
│   │           └── summary.md
│   ├── local_storage/           # Runtime file uploads (dev only)
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Backend environment config
│
├── client/                      # React + TypeScript SPA
│   ├── src/
│   │   ├── main.tsx             # React app entry
│   │   ├── App.tsx              # Router & layout
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx   # Upload UI + doc type selector
│   │   │   ├── DocumentsPage.tsx # List all documents
│   │   │   └── DocumentDetailPage.tsx # View results
│   │   ├── components/          # UI components (shadcn/ui)
│   │   │   ├── UploadCard.tsx
│   │   │   ├── ClassificationPanel.tsx
│   │   │   ├── CodeCard.tsx
│   │   │   ├── SummaryCard.tsx
│   │   │   └── ui/              # shadcn/ui primitives
│   │   └── lib/
│   │       ├── api.ts           # Axios client
│   │       ├── queryClient.ts   # TanStack Query setup
│   │       └── utils.ts
│   └── index.html
│
├── package.json                 # Frontend deps + Vite scripts
├── vite.config.ts               # Vite build config
├── tsconfig.json                # TypeScript config
├── tailwind.config.ts           # Tailwind CSS config
├── evals/                       # Evaluation datasets
│   ├── datasets/
│   │   └── synthetic_v1.json    # Labeled test data
│   └── run_eval.py              # Eval runner
└── test_docs/                   # Sample medical documents
```

---

## 🔧 Tech Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Runtime |
| **FastAPI** | 0.115.2 | Web framework |
| **Uvicorn** | 0.30.6 | ASGI server |
| **SQLAlchemy** | 2.0.36 | ORM |
| **Pydantic** | 2.9.2 | Data validation |
| **Anthropic SDK** | 0.39.0 | Claude API client |
| **PyPDF** | 5.0.1 | PDF text extraction |
| **httpx** | 0.28.1 | HTTP client |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI framework |
| **TypeScript** | 5.6.3 | Type safety |
| **Vite** | 5.4.20 | Build tool |
| **TanStack Query** | 5.60.5 | Data fetching |
| **Axios** | 1.13.0 | HTTP client |
| **Tailwind CSS** | 3.4.17 | Styling |
| **shadcn/ui** | Latest | Component library |
| **Wouter** | 3.3.5 | Routing |

### Database
- **Development:** SQLite (file-based)
- **Production:** PostgreSQL (RDS recommended)

---

## 🔑 Environment Variables

### Backend (`.env` in `backend-fastapi/`)

```env
# Database
DB_URL=sqlite:///./app.db
# For production (PostgreSQL on RDS):
# DB_URL=postgresql://username:password@rds-endpoint:5432/medai_db

# CORS (comma-separated frontend origins)
ALLOW_ORIGINS=http://localhost:5173,https://your-domain.com

# LLM Configuration
USE_CLAUDE_REAL=true                      # false = stub mode (no API calls)
ANTHROPIC_API_KEY=sk-ant-api03-...        # Anthropic API key
CLAUDE_MODEL=claude-sonnet-4-5            # Or claude-3-5-sonnet-20241022
PROMPT_CACHE_TTL_SECONDS=3600             # Optional: prompt caching

# File Storage
STORAGE_DIR=./local_storage               # Local dev
# For production (S3):
# STORAGE_BUCKET=med-doc-ai-uploads
```

### Frontend (`.env` in root or `client/`)

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
# For production:
# VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 🏛️ AWS Architecture

### Recommended Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  USERS (Browser)                                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Route 53 (DNS)                                                 │
│  └─ yourdomain.com → CloudFront                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  CloudFront Distribution (CDN + HTTPS)                          │
│  ├─ Origin 1: S3 (Frontend) → / (React SPA)                    │
│  └─ Origin 2: ALB (Backend) → /api/* (FastAPI)                 │
└────────────┬────────────────────────┬─────────────────────────────┘
             │                        │
             ▼                        ▼
┌─────────────────────────┐  ┌─────────────────────────────────────┐
│  S3 Bucket (Frontend)   │  │  Application Load Balancer (ALB)    │
│  └─ dist/public/        │  │  └─ HTTPS listener (port 443)       │
└─────────────────────────┘  └────────────┬────────────────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────────────────┐
                             │  ECS Fargate (Backend)              │
                             │  ├─ Task Definition                 │
                             │  │  └─ Docker: FastAPI + Uvicorn    │
                             │  ├─ Service (2-10 tasks)            │
                             │  └─ Auto Scaling (CPU/Memory)       │
                             └────────┬────────────┬───────────────┘
                                      │            │
                                      ▼            ▼
                    ┌──────────────────────┐  ┌─────────────────────┐
                    │  RDS PostgreSQL      │  │  S3 (File Storage)  │
                    │  ├─ Multi-AZ         │  │  └─ Uploaded PDFs   │
                    │  └─ Encrypted        │  └─────────────────────┘
                    └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │  Secrets Manager     │
                    │  ├─ ANTHROPIC_API_KEY│
                    │  └─ DB Password      │
                    └──────────────────────┘
                             │
                             ▼
                    ┌──────────────────────┐
                    │  Anthropic API       │
                    │  (External - Claude) │
                    └──────────────────────┘
```

---

## 🚀 Deployment Options

### Option 1: Serverless (Low/Variable Traffic)

| Component | AWS Service | Notes |
|-----------|-------------|-------|
| Backend API | **Lambda + API Gateway** | Use Mangum adapter for FastAPI |
| Frontend | **S3 + CloudFront** | Static hosting |
| Database | **Aurora Serverless v2** | Auto-scales based on usage |
| File Storage | **S3** | Upload bucket |
| Secrets | **Secrets Manager** | API keys & DB credentials |

**Pros:**
- Pay-per-use pricing
- Auto-scales to zero
- Minimal ops overhead

**Cons:**
- Cold start latency (1-3s)
- 15min Lambda timeout (may not work for long Claude requests)
- More complex debugging

**Best for:** MVPs, demos, unpredictable traffic

---

### Option 2: Container-based (Recommended for Production)

| Component | AWS Service | Notes |
|-----------|-------------|-------|
| Backend API | **ECS Fargate + ALB** | Dockerized FastAPI |
| Frontend | **S3 + CloudFront** | Static hosting |
| Database | **RDS PostgreSQL** | Multi-AZ, automated backups |
| File Storage | **S3** | Upload bucket |
| Secrets | **Secrets Manager** | API keys & DB credentials |
| Container Registry | **ECR** | Store Docker images |

**Pros:**
- No cold starts
- Predictable performance
- Easy auto-scaling
- Better for long-running requests

**Cons:**
- Higher baseline cost (always-on)
- Requires Docker knowledge

**Best for:** Production deployments, consistent traffic

---

### Option 3: VM-based (Simple, Full Control)

| Component | AWS Service | Notes |
|-----------|-------------|-------|
| Backend + Frontend | **EC2 (t3.medium)** | Single instance for both |
| Database | **RDS** or **local PostgreSQL** | |
| File Storage | **S3** or **local disk** | |
| Load Balancer | **ALB** (if multi-instance) | |

**Pros:**
- Full SSH access
- Simple debugging
- Familiar deployment model

**Cons:**
- Manual scaling
- More ops work (updates, monitoring)
- Single point of failure

**Best for:** Small teams, quick prototypes, full control needs

---

## 📝 Step-by-Step AWS Setup (Option 2: ECS Fargate)

### Phase 1: Database Setup

#### 1.1 Create RDS PostgreSQL Instance

```bash
# Via AWS Console:
# 1. RDS → Create Database
# 2. Choose PostgreSQL 15.x
# 3. Template: Dev/Test (for lower cost) or Production
# 4. DB instance class: db.t3.micro (dev) or db.t4g.medium (prod)
# 5. Storage: 20 GB GP3, enable auto-scaling
# 6. Multi-AZ: Yes (for production)
# 7. VPC: Default or create new
# 8. Public access: No (security best practice)
# 9. Database name: medai_db
# 10. Enable automated backups (7-day retention)
```

#### 1.2 Store DB Password in Secrets Manager

```bash
aws secretsmanager create-secret \
  --name med-doc-ai/db-password \
  --secret-string "your-secure-password"
```

#### 1.3 Update Backend Code

**File: `backend-fastapi/.env.production`**
```env
DB_URL=postgresql://admin:PASSWORD@your-rds-endpoint.region.rds.amazonaws.com:5432/medai_db
```

**Note:** Don't commit this file. Use Secrets Manager or ECS task definition env vars.

---

### Phase 2: Backend Containerization

#### 2.1 Create Dockerfile

**File: `backend-fastapi/Dockerfile`**
```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2.2 Build and Test Locally

```bash
cd backend-fastapi
docker build -t med-doc-ai-backend .
docker run -p 8000:8000 --env-file .env med-doc-ai-backend

# Test in browser: http://localhost:8000/docs
```

#### 2.3 Push to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name med-doc-ai-backend

# Get ECR login
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Tag and push
docker tag med-doc-ai-backend:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/med-doc-ai-backend:latest
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/med-doc-ai-backend:latest
```

---

### Phase 3: S3 File Storage Setup

#### 3.1 Create S3 Bucket for Uploads

```bash
aws s3 mb s3://med-doc-ai-uploads --region us-east-1

# Enable versioning (optional)
aws s3api put-bucket-versioning \
  --bucket med-doc-ai-uploads \
  --versioning-configuration Status=Enabled

# Block public access
aws s3api put-public-access-block \
  --bucket med-doc-ai-uploads \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

#### 3.2 Update Backend Code for S3

**File: `backend-fastapi/app/services/storage_s3.py`** (create new file)
```python
import boto3
from typing import Optional
from app.config import settings

s3_client = boto3.client('s3')

def save_file(filename: str, content: bytes) -> str:
    """Save file to S3 and return S3 key"""
    key = f"uploads/{filename}"
    s3_client.put_object(
        Bucket=settings.storage_bucket,
        Key=key,
        Body=content
    )
    return key

def get_file(key: str) -> bytes:
    """Retrieve file from S3"""
    response = s3_client.get_object(
        Bucket=settings.storage_bucket,
        Key=key
    )
    return response['Body'].read()
```

**Update `backend-fastapi/app/config.py`:**
```python
class Settings(BaseSettings):
    # ... existing fields ...
    storage_bucket: str = "med-doc-ai-uploads"
```

---

### Phase 4: ECS Fargate Deployment

#### 4.1 Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name med-doc-ai-cluster
```

#### 4.2 Create IAM Role for ECS Task

**Task Execution Role** (for pulling ECR images, CloudWatch logs):
```bash
# Create trust policy
cat > ecs-task-execution-trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "ecs-tasks.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF

# Create role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document file://ecs-task-execution-trust-policy.json

# Attach AWS managed policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

**Task Role** (for S3 access, Secrets Manager):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::med-doc-ai-uploads/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:med-doc-ai/*"
    }
  ]
}
```

#### 4.3 Create Task Definition

**File: `ecs-task-definition.json`**
```json
{
  "family": "med-doc-ai-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "taskRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskRole",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT_ID:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/med-doc-ai-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "USE_CLAUDE_REAL",
          "value": "true"
        },
        {
          "name": "CLAUDE_MODEL",
          "value": "claude-sonnet-4-5"
        },
        {
          "name": "STORAGE_BUCKET",
          "value": "med-doc-ai-uploads"
        },
        {
          "name": "ALLOW_ORIGINS",
          "value": "https://yourdomain.com"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:med-doc-ai/anthropic-key"
        },
        {
          "name": "DB_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:YOUR_ACCOUNT_ID:secret:med-doc-ai/db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/med-doc-ai-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

#### 4.4 Create Application Load Balancer

```bash
# Via AWS Console:
# 1. EC2 → Load Balancers → Create Application Load Balancer
# 2. Scheme: Internet-facing
# 3. IP address type: IPv4
# 4. VPC: Select your VPC
# 5. Subnets: Select 2+ subnets in different AZs
# 6. Security group: Allow inbound 80 (HTTP) and 443 (HTTPS)
# 7. Target group:
#    - Type: IP
#    - Protocol: HTTP
#    - Port: 8000
#    - Health check path: /health
```

#### 4.5 Create ECS Service

```bash
aws ecs create-service \
  --cluster med-doc-ai-cluster \
  --service-name backend-service \
  --task-definition med-doc-ai-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-east-1:xxx:targetgroup/xxx,containerName=backend,containerPort=8000"
```

---

### Phase 5: Frontend Deployment

#### 5.1 Build Frontend

Update `VITE_API_BASE_URL` before building:

**File: `.env.production`**
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

Build:
```bash
cd med_doc_processing
npm install
npm run frontend:build
# Output: dist/public/
```

#### 5.2 Create S3 Bucket for Frontend

```bash
aws s3 mb s3://med-doc-ai-frontend --region us-east-1

# Enable static website hosting
aws s3 website s3://med-doc-ai-frontend \
  --index-document index.html \
  --error-document index.html
```

#### 5.3 Upload Build to S3

```bash
aws s3 sync dist/public/ s3://med-doc-ai-frontend/ --delete
```

#### 5.4 Create CloudFront Distribution

```bash
# Via AWS Console:
# 1. CloudFront → Create Distribution
# 2. Origin:
#    - Domain: med-doc-ai-frontend.s3.us-east-1.amazonaws.com
#    - Origin access: Origin access control (recommended)
# 3. Default cache behavior:
#    - Viewer protocol policy: Redirect HTTP to HTTPS
#    - Allowed HTTP methods: GET, HEAD
# 4. Settings:
#    - Custom SSL certificate: Request from ACM
#    - Default root object: index.html
# 5. Error pages:
#    - 404 → /index.html (for SPA routing)
#    - 403 → /index.html
```

#### 5.5 Update S3 Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::med-doc-ai-frontend/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::YOUR_ACCOUNT_ID:distribution/YOUR_DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

---

### Phase 6: DNS & SSL

#### 6.1 Request SSL Certificate (ACM)

```bash
# Via AWS Console:
# 1. Certificate Manager → Request certificate
# 2. Domain: yourdomain.com, *.yourdomain.com
# 3. Validation: DNS validation
# 4. Add CNAME records to Route 53 or your DNS provider
```

#### 6.2 Configure Route 53

```bash
# Via AWS Console:
# 1. Route 53 → Hosted zones → Create hosted zone (yourdomain.com)
# 2. Create A record:
#    - Name: yourdomain.com
#    - Type: A - IPv4 address
#    - Alias: Yes → CloudFront distribution
# 3. Create A record:
#    - Name: api.yourdomain.com
#    - Type: A - IPv4 address
#    - Alias: Yes → ALB
```

---

### Phase 7: Security Hardening

#### 7.1 Security Group Rules

**ALB Security Group:**
```
Inbound:
- Port 443 (HTTPS) from 0.0.0.0/0
- Port 80 (HTTP) from 0.0.0.0/0 (redirect to HTTPS)

Outbound:
- Port 8000 to ECS security group
```

**ECS Security Group:**
```
Inbound:
- Port 8000 from ALB security group

Outbound:
- Port 443 to 0.0.0.0/0 (for Anthropic API)
- Port 5432 to RDS security group
```

**RDS Security Group:**
```
Inbound:
- Port 5432 from ECS security group

Outbound:
- None required
```

#### 7.2 Enable Encryption

- **RDS:** Enable encryption at rest (KMS)
- **S3:** Enable default encryption (SSE-S3 or SSE-KMS)
- **Secrets Manager:** Encrypted by default (KMS)
- **CloudFront:** Force HTTPS

#### 7.3 Enable Logging

- **ALB:** Enable access logs to S3
- **CloudFront:** Enable standard logs to S3
- **ECS:** CloudWatch Logs (already configured)
- **RDS:** Enable query logging (optional)

---

## 💰 Cost Estimates

### Monthly Cost Breakdown (US East 1)

| Service | Configuration | Monthly Cost |
|---------|---------------|--------------|
| **ECS Fargate** | 2 tasks × 0.5 vCPU × 1GB RAM × 730 hours | ~$30 |
| **RDS PostgreSQL** | db.t3.micro (Multi-AZ) + 20GB storage | ~$30 |
| **ALB** | 1 load balancer + 10GB data processed | ~$20 |
| **S3 (Uploads)** | 10GB storage + 100K requests | ~$3 |
| **S3 (Frontend)** | 1GB storage + 1M requests | ~$1 |
| **CloudFront** | 100GB data transfer | ~$10 |
| **Secrets Manager** | 2 secrets | ~$1 |
| **Route 53** | 1 hosted zone | ~$0.50 |
| **ECR** | 10GB storage | ~$1 |
| **Data Transfer** | 50GB outbound | ~$5 |
| **CloudWatch Logs** | 5GB ingestion + 1GB storage | ~$3 |
| **Total** | | **~$105/month** |

**Additional Costs (Not Included):**
- **Anthropic API:** $3/million input tokens, $15/million output tokens
  - Estimate: ~$50-200/month depending on usage
- **Domain name:** $12/year (Route 53)
- **SSL certificate:** Free (AWS ACM)

**Cost Optimization Tips:**
- Use **Fargate Spot** for non-critical tasks (70% cheaper)
- Enable **S3 Intelligent-Tiering** for uploads
- Use **RDS Reserved Instances** (40% savings)
- Set up **CloudWatch billing alarms**

---

## 🛡️ Security Considerations

### 1. API Security
- [ ] Enable **rate limiting** on ALB/API Gateway
- [ ] Add **authentication** (Cognito, Auth0, or custom JWT)
- [ ] Implement **API key rotation** for Anthropic
- [ ] Use **AWS WAF** to block malicious requests

### 2. Data Protection
- [ ] **Encrypt DB** at rest (RDS encryption)
- [ ] **Encrypt S3** at rest (SSE-S3 or SSE-KMS)
- [ ] **Enable S3 versioning** for uploads (disaster recovery)
- [ ] **HIPAA compliance** (if handling real PHI):
  - Sign BAA with AWS
  - Enable CloudTrail logging
  - Use dedicated VPC
  - Implement access controls

### 3. Network Security
- [ ] Use **private subnets** for ECS and RDS
- [ ] **NAT Gateway** for ECS outbound traffic
- [ ] **VPC Flow Logs** for network monitoring
- [ ] Restrict **security group rules** (principle of least privilege)

### 4. Application Security
- [ ] **Input validation** (already done via Pydantic)
- [ ] **File upload limits** (max size, allowed types)
- [ ] **SQL injection protection** (SQLAlchemy parameterized queries)
- [ ] **CORS whitelist** (set `ALLOW_ORIGINS` carefully)

### 5. Monitoring & Alerts
- [ ] **CloudWatch alarms** for:
  - ECS CPU/memory > 80%
  - RDS connections > 80%
  - ALB 5xx errors > threshold
  - Anthropic API errors
- [ ] **X-Ray** tracing for request debugging
- [ ] **GuardDuty** for threat detection

---

## 📊 CI/CD Pipeline (Optional)

### GitHub Actions Workflow

**File: `.github/workflows/deploy.yml`**
```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | \
            docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
      
      - name: Build and push backend
        run: |
          cd backend-fastapi
          docker build -t ${{ secrets.ECR_REGISTRY }}/med-doc-ai-backend:latest .
          docker push ${{ secrets.ECR_REGISTRY }}/med-doc-ai-backend:latest
      
      - name: Deploy to ECS
        run: |
          aws ecs update-service \
            --cluster med-doc-ai-cluster \
            --service backend-service \
            --force-new-deployment

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 20
      
      - name: Build frontend
        run: |
          npm install
          VITE_API_BASE_URL=${{ secrets.API_URL }} npm run frontend:build
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy to S3
        run: |
          aws s3 sync dist/public/ s3://med-doc-ai-frontend/ --delete
      
      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DIST_ID }} \
            --paths "/*"
```

---

## 🔍 Troubleshooting

### Backend Not Starting
1. Check ECS task logs in CloudWatch
2. Verify environment variables in task definition
3. Test DB connection: `psql -h RDS_ENDPOINT -U admin -d medai_db`
4. Check security groups (ECS → RDS, ECS → Internet)

### Frontend Can't Reach Backend
1. Verify `VITE_API_BASE_URL` is correct (should be ALB URL)
2. Check CORS settings in backend `.env`
3. Test backend directly: `curl https://api.yourdomain.com/health`
4. Check CloudFront origin settings

### Database Connection Errors
1. Check RDS security group (allow port 5432 from ECS)
2. Verify `DB_URL` format: `postgresql://user:pass@host:5432/dbname`
3. Check RDS is in same VPC as ECS
4. Test from ECS task: `nc -zv RDS_ENDPOINT 5432`

### File Upload Errors
1. Check S3 bucket exists and is in correct region
2. Verify ECS task IAM role has S3 permissions
3. Check S3 bucket policy (block public access)
4. Test S3 access from ECS task: `aws s3 ls s3://med-doc-ai-uploads/`

### Anthropic API Errors
1. Verify API key in Secrets Manager
2. Check ECS task has internet access (NAT Gateway or public IP)
3. Test API directly: `curl https://api.anthropic.com/v1/messages -H "x-api-key: $API_KEY"`
4. Check CloudWatch logs for error messages

---

## 📚 Additional Resources

- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [AWS ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Test application locally (backend + frontend)
- [ ] Run evals: `python evals/run_eval.py`
- [ ] Review security settings (CORS, HTTPS, secrets)
- [ ] Estimate costs with AWS Calculator
- [ ] Get Anthropic API key with sufficient quota

### AWS Setup
- [ ] Create RDS PostgreSQL instance
- [ ] Store secrets in Secrets Manager
- [ ] Create S3 buckets (uploads + frontend)
- [ ] Create ECR repository
- [ ] Build and push Docker image
- [ ] Create ECS cluster and task definition
- [ ] Create ALB and target group
- [ ] Create ECS service
- [ ] Build and upload frontend to S3
- [ ] Create CloudFront distribution
- [ ] Request SSL certificate (ACM)
- [ ] Configure Route 53 DNS

### Post-Deployment
- [ ] Test end-to-end (upload → classify → codes → summary)
- [ ] Set up CloudWatch alarms
- [ ] Enable CloudTrail logging
- [ ] Configure automatic backups (RDS, S3)
- [ ] Set up CI/CD pipeline (optional)
- [ ] Document runbook for team
- [ ] Monitor costs in AWS Cost Explorer

---

## 🎯 Quick Start Commands

### Local Development
```bash
# Backend
cd backend-fastapi
python -m venv .venv
. .venv/Scripts/Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend (from repo root)
npm install
npm run frontend:dev
```

### Production Deployment
```bash
# Build backend
cd backend-fastapi
docker build -t med-doc-ai-backend .
docker tag med-doc-ai-backend:latest YOUR_ECR_REPO:latest
docker push YOUR_ECR_REPO:latest

# Build frontend
cd ..
VITE_API_BASE_URL=https://api.yourdomain.com npm run frontend:build
aws s3 sync dist/public/ s3://med-doc-ai-frontend/ --delete
aws cloudfront create-invalidation --distribution-id XXX --paths "/*"
```

---

**Questions?** Open an issue or contact the dev team.
