# Free HTTPS Setup Script for Windows PowerShell
# This uses Let's Encrypt (free) + cert-manager + NGINX Ingress

Write-Host "🔒 Setting up FREE HTTPS with Let's Encrypt..." -ForegroundColor Green

# Step 1: Install cert-manager
Write-Host "`n📦 Installing cert-manager..." -ForegroundColor Yellow
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

Write-Host "⏳ Waiting for cert-manager pods to be ready (this may take 2-3 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-webhook -n cert-manager
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager-cainjector -n cert-manager

Write-Host "✅ cert-manager installed!" -ForegroundColor Green

# Step 2: Install NGINX Ingress Controller
Write-Host "`n📦 Installing NGINX Ingress Controller..." -ForegroundColor Yellow
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/aws/deploy.yaml

Write-Host "⏳ Waiting for NGINX Ingress Controller to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 30
kubectl wait --namespace ingress-nginx `
  --for=condition=ready pod `
  --selector=app.kubernetes.io/component=controller `
  --timeout=300s

Write-Host "✅ NGINX Ingress Controller installed!" -ForegroundColor Green

# Step 3: Apply Let's Encrypt Issuer
Write-Host "`n📝 Creating Let's Encrypt certificate issuer..." -ForegroundColor Yellow
kubectl apply -f k8s/https/letsencrypt-issuer.yaml

Write-Host "✅ Let's Encrypt issuer created!" -ForegroundColor Green

# Step 4: Apply Ingress with TLS
Write-Host "`n🌐 Creating Ingress with HTTPS..." -ForegroundColor Yellow
kubectl apply -f k8s/https/ingress.yaml

Write-Host "`n⏳ Waiting for certificate to be issued (this may take 1-2 minutes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Check certificate status
kubectl describe certificate med-doc-tls -n dev

Write-Host "`n✅ HTTPS setup complete!" -ForegroundColor Green
Write-Host "`n📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Get the new HTTPS LoadBalancer URL:" -ForegroundColor White
Write-Host "   kubectl get ingress -n dev" -ForegroundColor Gray
Write-Host "`n2. Check certificate status:" -ForegroundColor White
Write-Host "   kubectl get certificate -n dev" -ForegroundColor Gray
Write-Host "`n3. Your app will be available at:" -ForegroundColor White
Write-Host "   https://<INGRESS_LOADBALANCER_URL>" -ForegroundColor Yellow
Write-Host "`n💡 Certificate will auto-renew before expiration (90 days)" -ForegroundColor Cyan
