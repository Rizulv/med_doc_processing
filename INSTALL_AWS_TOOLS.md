# Installing AWS Tools for Windows

## Prerequisites Check

Before deploying to AWS EKS, you need these tools installed:

### 1. AWS CLI
Check if installed:
```powershell
aws --version
```

If not installed, download from: https://aws.amazon.com/cli/

Or install via Chocolatey (run PowerShell as Administrator):
```powershell
choco install awscli -y
```

### 2. kubectl (Kubernetes CLI)
Check if installed:
```powershell
kubectl version --client
```

Install via Chocolatey (as Administrator):
```powershell
choco install kubernetes-cli -y
```

Or download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

### 3. eksctl (EKS Cluster Manager)
Check if installed:
```powershell
eksctl version
```

**Install via Chocolatey (RECOMMENDED - run PowerShell as Administrator):**
```powershell
choco install eksctl -y
```

**Alternative: Manual Installation (if Chocolatey fails)**

1. Download the latest eksctl for Windows:
   - Go to: https://github.com/weaveworks/eksctl/releases
   - Download `eksctl_windows_amd64.zip` (latest version)

2. Extract the zip file

3. Move `eksctl.exe` to a directory in your PATH:
   ```powershell
   # Create a tools directory if you don't have one
   New-Item -Path "C:\tools\eksctl" -ItemType Directory -Force
   
   # Move eksctl.exe there (adjust source path to your Downloads)
   Move-Item -Path "$env:USERPROFILE\Downloads\eksctl.exe" -Destination "C:\tools\eksctl\eksctl.exe"
   
   # Add to PATH (this session only)
   $env:PATH += ";C:\tools\eksctl"
   
   # Add to PATH permanently (run as Administrator)
   [Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\tools\eksctl", [EnvironmentVariableTarget]::Machine)
   ```

4. Verify installation:
   ```powershell
   eksctl version
   ```

### 4. Docker Desktop (Already Installed ✅)
You already have Docker running, which is great!

## AWS Configuration

After installing the tools, configure AWS credentials:

### Step 1: Get AWS Credentials
1. Log in to AWS Console
2. Go to IAM → Users → Your User → Security Credentials
3. Create Access Key (for CLI)
4. Save the Access Key ID and Secret Access Key

### Step 2: Configure AWS CLI
```powershell
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: [paste your key]
- **AWS Secret Access Key**: [paste your secret]
- **Default region name**: `ap-south-1` (or your preferred region)
- **Default output format**: `json`

### Step 3: Verify AWS Access
```powershell
# Test AWS CLI
aws sts get-caller-identity

# Should show your AWS account details
```

## Quick Fix for Your Current Error

**Your current error**: `eksctl: The term 'eksctl' is not recognized`

**Fastest solution**:

1. **Open PowerShell as Administrator** (right-click → "Run as Administrator")

2. Run:
   ```powershell
   choco install eksctl -y
   ```

3. Close and reopen your PowerShell terminal

4. Verify:
   ```powershell
   eksctl version
   ```

5. Then retry your command:
   ```powershell
   eksctl create cluster -f cloud/eksctl/cluster-config.yaml
   ```

## Alternative: Use AWS Console Instead

If you prefer not to install eksctl, you can:

1. **Create EKS cluster via AWS Console** (web interface)
2. **Use Terraform** (we have Terraform examples in AWS_DEPLOYMENT_GUIDE.md)
3. **Use AWS CDK** (Infrastructure as Code with TypeScript/Python)

## What's Next After Installing Tools?

Once tools are installed:

1. ✅ Configure AWS credentials (`aws configure`)
2. ✅ Verify cluster config exists (`cloud/eksctl/cluster-config.yaml`)
3. ✅ Create EKS cluster (`eksctl create cluster -f cloud/eksctl/cluster-config.yaml`)
4. ✅ Build and push Docker images to ECR
5. ✅ Deploy using kubectl or GitHub Actions

See `DEPLOYMENT_ROADMAP.md` for detailed steps!

---

## Troubleshooting

### "Access Denied" errors with Chocolatey
- Run PowerShell as Administrator
- If still fails, try manual installation method above

### eksctl not found after installation
- Close and reopen PowerShell
- Check if PATH was updated: `$env:PATH`
- Try logging out and back in to Windows

### AWS CLI configuration issues
- Make sure you have valid AWS credentials
- Check IAM permissions (need EKS, EC2, VPC permissions)
- Try `aws sts get-caller-identity` to verify

### Network/Firewall issues
- Some corporate networks block GitHub releases
- Try downloading from a different network
- Use VPN if necessary
