# Free HTTPS Setup Guide

Get **FREE HTTPS certificates** from Let's Encrypt for your medical document processing app!

## 🎯 What This Does

- ✅ **FREE SSL/TLS certificates** from Let's Encrypt
- ✅ **Auto-renewal** (certificates renew automatically every 90 days)
- ✅ **Zero cost** - no AWS Certificate Manager fees
- ✅ **HTTPS redirect** - HTTP automatically redirects to HTTPS
- ✅ **Works immediately** - no domain name required (can use LoadBalancer DNS)

## 📋 Prerequisites

- EKS cluster running
- `kubectl` configured
- Your app already deployed

## 🚀 Quick Setup (5 minutes)

### Option 1: Automated Setup (Recommended)

```powershell
# Run the automated setup script
.\scripts\setup-https.ps1
```

This will:
1. Install cert-manager
2. Install NGINX Ingress Controller
3. Configure Let's Encrypt
4. Get your free certificate
5. Enable HTTPS

### Option 2: Manual Setup

```powershell
# 1. Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Wait for cert-manager to be ready
kubectl wait --for=condition=available --timeout=300s deployment/cert-manager -n cert-manager

# 2. Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/aws/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s

# 3. Update email in k8s/https/letsencrypt-issuer.yaml
# Change: email: your-email@example.com

# 4. Apply the configurations
kubectl apply -f k8s/https/letsencrypt-issuer.yaml
kubectl apply -f k8s/https/ingress.yaml
```

## 🔍 Verify Setup

### Check Certificate Status
```powershell
kubectl get certificate -n dev
```

You should see:
```
NAME           READY   SECRET         AGE
med-doc-tls    True    med-doc-tls    2m
```

### Get HTTPS URL
```powershell
kubectl get ingress -n dev
```

Look for the `ADDRESS` column - that's your new HTTPS URL!

### Test Certificate
```powershell
# Check certificate details
kubectl describe certificate med-doc-tls -n dev

# View certificate secret
kubectl get secret med-doc-tls -n dev -o yaml
```

## 🌐 Access Your App

After setup completes (1-2 minutes for certificate issuance):

```
https://<INGRESS-LOADBALANCER-ADDRESS>
```

Example:
```
https://a1b2c3d4e5f6-123456789.ap-south-1.elb.amazonaws.com
```

## 🔧 Troubleshooting

### Certificate Not Issuing?

```powershell
# Check certificate request
kubectl describe certificaterequest -n dev

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check challenge status
kubectl get challenges -n dev
```

### Common Issues

**Issue**: Certificate stuck in "Pending"
**Solution**: Check that your LoadBalancer is accessible from the internet (Let's Encrypt needs to verify it)

**Issue**: "Issuer not found"
**Solution**: Make sure you applied `letsencrypt-issuer.yaml` first

**Issue**: "Failed to perform self check GET request"
**Solution**: Ensure your web service is running and responding to health checks

## 📝 Configuration Files

### `k8s/https/letsencrypt-issuer.yaml`
Configures Let's Encrypt as the certificate authority.

**⚠️ IMPORTANT**: Update the email address to yours!

### `k8s/https/ingress.yaml`
Defines routing rules and HTTPS settings.

**For custom domain**: Replace the LoadBalancer DNS with your domain name:
```yaml
tls:
- hosts:
  - medai.yourdomain.com  # Your domain
  secretName: med-doc-tls
```

## 🎁 Benefits vs AWS Certificate Manager

| Feature | Let's Encrypt (Free) | AWS ACM |
|---------|---------------------|---------|
| **Cost** | FREE ✅ | FREE ✅ |
| **Setup** | 5 minutes | Requires domain + DNS |
| **Domain Required** | NO ✅ | YES ❌ |
| **Auto-Renewal** | YES ✅ | YES ✅ |
| **Works with LB DNS** | YES ✅ | NO ❌ |
| **Certificate Duration** | 90 days | 13 months |

## 🔄 Certificate Renewal

Certificates auto-renew automatically! cert-manager will:
- Check expiration 30 days before
- Request new certificate from Let's Encrypt
- Update the secret automatically
- Zero downtime

## 🗑️ Cleanup (if needed)

To remove HTTPS and revert to HTTP:

```powershell
# Delete ingress
kubectl delete -f k8s/https/ingress.yaml

# Delete issuer
kubectl delete -f k8s/https/letsencrypt-issuer.yaml

# Uninstall cert-manager (optional)
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml

# Uninstall NGINX Ingress (optional)
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.9.4/deploy/static/provider/aws/deploy.yaml
```

## 💰 Cost Impact

**Additional AWS Costs**: ~$18/month
- New LoadBalancer for NGINX Ingress: ~$18/month
- You can delete the old web service LoadBalancer: Save ~$18/month
- **Net cost**: $0 (just replacing one LB with another)

**To save money** after HTTPS is working:
```powershell
# Change web service from LoadBalancer to ClusterIP
kubectl patch service web -n dev -p '{"spec":{"type":"ClusterIP"}}'
```

This removes the old LoadBalancer, keeping only the NGINX Ingress LoadBalancer.

## 📚 Learn More

- [cert-manager docs](https://cert-manager.io/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

---

**Questions?** Check the troubleshooting section or run:
```powershell
kubectl get all -n cert-manager
kubectl get all -n ingress-nginx
kubectl describe ingress -n dev
```
