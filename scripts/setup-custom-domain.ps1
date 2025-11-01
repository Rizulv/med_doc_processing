# Setup Custom Domain for HTTPS
# This script helps you configure a custom domain name for your app

param(
    [string]$DomainName = ""
)

Write-Host "🌐 Custom Domain Setup for HTTPS" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

# Get the Ingress LoadBalancer IP
Write-Host "`n📍 Getting your LoadBalancer address..." -ForegroundColor Yellow
$ingressService = kubectl get service -n ingress-nginx ingress-nginx-controller -o json | ConvertFrom-Json
$loadBalancerDNS = $ingressService.status.loadBalancer.ingress[0].hostname

if (-not $loadBalancerDNS) {
    Write-Host "❌ Could not find LoadBalancer address. Is NGINX Ingress installed?" -ForegroundColor Red
    Write-Host "Run: .\scripts\setup-https.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Your LoadBalancer address: $loadBalancerDNS" -ForegroundColor Green

# Resolve LoadBalancer to IP
Write-Host "`n🔍 Resolving LoadBalancer IP..." -ForegroundColor Yellow
$ipAddress = (Resolve-DnsName $loadBalancerDNS)[0].IPAddress

if (-not $ipAddress) {
    Write-Host "⚠️  Could not resolve IP address" -ForegroundColor Yellow
    $ipAddress = "PENDING"
}

Write-Host "✅ LoadBalancer IP: $ipAddress" -ForegroundColor Green

# If no domain provided, show options
if (-not $DomainName) {
    Write-Host "`n" -NoNewline
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "         Choose Your Domain Option" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    
    Write-Host "`n🆓 FREE Option 1: nip.io (Works Immediately!)" -ForegroundColor Green
    Write-Host "   No registration needed! Magic DNS that points to your IP." -ForegroundColor Gray
    if ($ipAddress -ne "PENDING") {
        $nipDomain = "medai." + $ipAddress.Replace(".", "-") + ".nip.io"
        Write-Host "   Your domain: " -NoNewline -ForegroundColor White
        Write-Host $nipDomain -ForegroundColor Yellow
        Write-Host "`n   Run: " -NoNewline -ForegroundColor White
        Write-Host ".\scripts\setup-custom-domain.ps1 -DomainName $nipDomain" -ForegroundColor Cyan
    } else {
        Write-Host "   Wait for LoadBalancer IP to be assigned, then use:" -ForegroundColor Yellow
        Write-Host "   medai.<IP-WITH-DASHES>.nip.io" -ForegroundColor Gray
    }
    
    Write-Host "`n🆓 FREE Option 2: DuckDNS.org" -ForegroundColor Green
    Write-Host "   1. Visit: https://www.duckdns.org" -ForegroundColor Gray
    Write-Host "   2. Sign in with Google/GitHub" -ForegroundColor Gray
    Write-Host "   3. Create subdomain (e.g., 'medai')" -ForegroundColor Gray
    Write-Host "   4. Point it to: $ipAddress" -ForegroundColor Gray
    Write-Host "   5. Your domain: medai.duckdns.org" -ForegroundColor Yellow
    Write-Host "`n   Then run: " -NoNewline -ForegroundColor White
    Write-Host ".\scripts\setup-custom-domain.ps1 -DomainName medai.duckdns.org" -ForegroundColor Cyan
    
    Write-Host "`n🆓 FREE Option 3: FreeDNS (afraid.org)" -ForegroundColor Green
    Write-Host "   1. Visit: https://freedns.afraid.org" -ForegroundColor Gray
    Write-Host "   2. Sign up (free)" -ForegroundColor Gray
    Write-Host "   3. Create subdomain (many TLDs available: .mooo.com, .zapto.org, etc.)" -ForegroundColor Gray
    Write-Host "   4. Point to: $ipAddress" -ForegroundColor Gray
    Write-Host "   5. Example: medai.mooo.com" -ForegroundColor Yellow
    Write-Host "`n   Then run: " -NoNewline -ForegroundColor White
    Write-Host ".\scripts\setup-custom-domain.ps1 -DomainName medai.mooo.com" -ForegroundColor Cyan
    
    Write-Host "`n💰 Paid Option: Your Own Domain" -ForegroundColor Yellow
    Write-Host "   Buy from: GoDaddy, Namecheap, Google Domains, etc." -ForegroundColor Gray
    Write-Host "   Cost: ~$10-15/year" -ForegroundColor Gray
    Write-Host "   Example: medai.yourdomain.com" -ForegroundColor Yellow
    Write-Host "`n   Then run: " -NoNewline -ForegroundColor White
    Write-Host ".\scripts\setup-custom-domain.ps1 -DomainName medai.yourdomain.com" -ForegroundColor Cyan
    
    Write-Host "`n========================================`n" -ForegroundColor Cyan
    
    # Recommend nip.io for immediate use
    if ($ipAddress -ne "PENDING") {
        Write-Host "💡 RECOMMENDED: Use nip.io for instant HTTPS!" -ForegroundColor Cyan
        $nipDomain = "medai." + $ipAddress.Replace(".", "-") + ".nip.io"
        Write-Host "   Copy this command:" -ForegroundColor Yellow
        Write-Host "`n   .\scripts\setup-custom-domain.ps1 -DomainName $nipDomain`n" -ForegroundColor White
    }
    
    exit 0
}

# Domain name provided - proceed with setup
Write-Host "`n🎯 Setting up domain: " -NoNewline -ForegroundColor Yellow
Write-Host $DomainName -ForegroundColor Cyan

# Check if it's nip.io (no DNS setup needed)
$isNipIo = $DomainName -like "*.nip.io"

if (-not $isNipIo) {
    Write-Host "`n⚠️  IMPORTANT: Make sure you've configured DNS!" -ForegroundColor Yellow
    Write-Host "   Your domain '$DomainName' must point to:" -ForegroundColor White
    Write-Host "   $loadBalancerDNS" -ForegroundColor Cyan
    Write-Host "   OR" -ForegroundColor Gray
    Write-Host "   $ipAddress" -ForegroundColor Cyan
    Write-Host "`n   Press Enter when DNS is configured, or Ctrl+C to cancel..." -ForegroundColor Yellow
    Read-Host
}

# Update ingress with custom domain
Write-Host "`n📝 Updating ingress configuration..." -ForegroundColor Yellow

$ingressContent = Get-Content k8s/https/ingress-custom-domain.yaml -Raw
$ingressContent = $ingressContent -replace "REPLACE_WITH_YOUR_DOMAIN", $DomainName

# Save to temp file and apply
$ingressContent | Set-Content k8s/https/ingress-active.yaml

Write-Host "✅ Configuration updated!" -ForegroundColor Green

# Apply the ingress
Write-Host "`n🚀 Applying ingress configuration..." -ForegroundColor Yellow
kubectl apply -f k8s/https/ingress-active.yaml

Write-Host "✅ Ingress applied!" -ForegroundColor Green

# Wait for certificate
Write-Host "`n⏳ Waiting for SSL certificate to be issued..." -ForegroundColor Yellow
Write-Host "   This may take 1-2 minutes..." -ForegroundColor Gray

Start-Sleep -Seconds 10

# Check certificate status
for ($i = 1; $i -le 12; $i++) {
    $certStatus = kubectl get certificate med-doc-tls -n dev -o json 2>$null | ConvertFrom-Json
    
    if ($certStatus.status.conditions | Where-Object { $_.type -eq "Ready" -and $_.status -eq "True" }) {
        Write-Host "✅ Certificate issued successfully!" -ForegroundColor Green
        break
    }
    
    Write-Host "   Attempt $i/12: Still waiting..." -ForegroundColor Gray
    Start-Sleep -Seconds 10
}

# Final status check
Write-Host "`n📊 Certificate Status:" -ForegroundColor Cyan
kubectl describe certificate med-doc-tls -n dev | Select-String -Pattern "Status|Message|Ready"

Write-Host "`n🎉 Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your app is now available at:" -ForegroundColor White
Write-Host "`n   https://$DomainName`n" -ForegroundColor Yellow -BackgroundColor DarkGreen
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n💡 Troubleshooting:" -ForegroundColor Cyan
Write-Host "   Check certificate: kubectl get certificate -n dev" -ForegroundColor Gray
Write-Host "   Check ingress:     kubectl get ingress -n dev" -ForegroundColor Gray
Write-Host "   View logs:         kubectl logs -n cert-manager deployment/cert-manager" -ForegroundColor Gray
