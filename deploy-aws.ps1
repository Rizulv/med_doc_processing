# Medical Doc AI - AWS Deployment Script
# Run this after making code changes to deploy to EKS

Write-Host "🚀 Medical Doc AI - Deployment to AWS EKS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$AWS_REGION = "ap-south-1"
$AWS_ACCOUNT_ID = "503837496832"
$ECR_BACKEND = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/med-doc-backend"
$ECR_FRONTEND = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/med-doc-frontend"
$ECR_REGISTRY = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
$EKS_CLUSTER = "med-doc-dev"
$NAMESPACE = "dev"

# Step 1: Login to ECR
Write-Host "📦 Step 1: Logging into Amazon ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REGISTRY

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ECR login failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ ECR login successful" -ForegroundColor Green
Write-Host ""

# Step 2: Build and push backend
Write-Host "🔨 Step 2: Building backend image..." -ForegroundColor Yellow
docker build -f backend-fastapi/Dockerfile -t med-doc-backend:latest ./backend-fastapi

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend build failed!" -ForegroundColor Red
    exit 1
}

docker tag med-doc-backend:latest "${ECR_BACKEND}:latest"
docker push "${ECR_BACKEND}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Backend image pushed to ECR" -ForegroundColor Green
Write-Host ""

# Step 3: Build and push frontend
Write-Host "🎨 Step 3: Building frontend image..." -ForegroundColor Yellow
docker build -f Dockerfile.frontend -t med-doc-frontend:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}

docker tag med-doc-frontend:latest "${ECR_FRONTEND}:latest"
docker push "${ECR_FRONTEND}:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend image pushed to ECR" -ForegroundColor Green
Write-Host ""

# Step 4: Apply Kubernetes manifests
Write-Host "☸️  Step 4: Applying Kubernetes manifests..." -ForegroundColor Yellow

# Apply IAM service account first
kubectl apply -f k8s/base/iam-serviceaccount.yaml

# Apply deployments
kubectl apply -f k8s/base/api-deployment.yaml
kubectl apply -f k8s/base/web-deployment.yaml

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Kubernetes apply failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Kubernetes manifests applied" -ForegroundColor Green
Write-Host ""

# Step 5: Restart deployments to pull new images
Write-Host "🔄 Step 5: Restarting deployments..." -ForegroundColor Yellow
kubectl -n $NAMESPACE rollout restart deployment/api
kubectl -n $NAMESPACE rollout restart deployment/web

Write-Host "⏳ Waiting for rollout to complete..." -ForegroundColor Yellow
kubectl -n $NAMESPACE rollout status deployment/api --timeout=5m
kubectl -n $NAMESPACE rollout status deployment/web --timeout=5m

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Rollout failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""

# Step 6: Get service status
Write-Host "📊 Step 6: Getting service status..." -ForegroundColor Yellow
kubectl -n $NAMESPACE get pods
Write-Host ""
kubectl -n $NAMESPACE get svc web

Write-Host ""
Write-Host "✨ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Get your LoadBalancer URL above" -ForegroundColor Cyan
