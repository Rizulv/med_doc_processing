# 🚀 Free Deployment Guide - Frontend (Vercel) + Backend (Render.com)

## Why This Setup?
- ✅ **100% FREE** - Both platforms have generous free tiers
- ✅ **Vercel**: Perfect for Vite/React (unlimited bandwidth, fast CDN)
- ✅ **Render.com**: Free tier for FastAPI (512MB RAM, auto-wake from sleep)
- ✅ **No Code Changes** - Deploy as-is

---

## 📦 STEP 1: Deploy Backend on Render.com (Free Tier)

### 1.1 Sign Up & Create Service

1. Go to **[render.com](https://render.com)** and sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `Rizulv/med_doc_processing`
4. Configure the service:

   **Service Settings:**
   - **Name**: `med-doc-backend`
   - **Region**: Choose closest to you (e.g., Oregon USA)
   - **Root Directory**: `backend-fastapi`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 1.2 Add Environment Variables

Click **"Environment"** tab and add:

```
ANTHROPIC_API_KEY=sk-ant-XXXXXXXXXXXXXXXXXXXXXXXX
CLAUDE_MODEL=claude-sonnet-4-5-20250929
USE_CLAUDE=true
DB_URL=sqlite:///./app.db
STORAGE_DIR=./local_storage
ALLOW_ORIGINS=*
```

**🔑 IMPORTANT**: Replace `sk-ant-XXX` with your actual Claude API key from [Anthropic Console](https://console.anthropic.com/)

### 1.3 Select Free Plan

- **Instance Type**: Free
- **Auto-Deploy**: Yes (enable)

### 1.4 Deploy!

Click **"Create Web Service"** and wait 3-5 minutes.

✅ **Your backend URL**: `https://med-doc-backend.onrender.com`

**Note**: Free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30 seconds to wake up.

---

## 🎨 STEP 2: Deploy Frontend on Vercel (Free Tier)

### 2.1 Prepare Frontend Environment

Create `.env.production` in `client/` folder:

```bash
cd /path/to/med_doc_processing/client
```

Create file: `.env.production`

```env
VITE_API_URL=https://med-doc-backend.onrender.com
```

**Replace `med-doc-backend.onrender.com` with your actual Render backend URL from Step 1.4**

### 2.2 Deploy to Vercel

**Option A: Using Vercel CLI (Recommended)**

```bash
# Install Vercel CLI globally
npm install -g vercel

# Go to project root
cd /path/to/med_doc_processing

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

When prompted:
- **Set up and deploy?**: `Y`
- **Scope**: Choose your account
- **Link to existing project?**: `N`
- **Project name**: `med-doc-processing`
- **Directory**: `./client`
- **Override settings?**: `N`

**Option B: Using Vercel Dashboard**

1. Go to **[vercel.com](https://vercel.com)** and sign up with GitHub
2. Click **"Add New..."** → **"Project"**
3. Import `Rizulv/med_doc_processing`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `client`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
5. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://med-doc-backend.onrender.com`
6. Click **"Deploy"**

✅ **Your frontend URL**: `https://med-doc-processing.vercel.app`

---

## 🧪 STEP 3: Test Your Deployment

### 3.1 Test Backend

Open: `https://med-doc-backend.onrender.com/docs`

You should see the FastAPI Swagger UI.

### 3.2 Test Frontend

Open: `https://med-doc-processing.vercel.app`

Upload a test medical document and verify it works!

---

## 🔧 Troubleshooting

### Backend Issues

**"Service unavailable" or slow response:**
- Free tier sleeps after inactivity. First request wakes it up (~30 seconds)
- Subsequent requests are fast

**"Invalid API key" error:**
- Check Environment Variables in Render dashboard
- Ensure `ANTHROPIC_API_KEY` has no quotes or spaces
- Verify at [Anthropic Console](https://console.anthropic.com/)

**Build fails:**
- Check Render logs (Dashboard → Logs tab)
- Ensure `requirements.txt` is in `backend-fastapi/` folder
- Try manual deploy: Dashboard → Manual Deploy → Deploy latest commit

### Frontend Issues

**API connection error / CORS:**
- Verify `VITE_API_URL` in Vercel environment variables
- Should match your Render backend URL exactly
- Ensure backend has `ALLOW_ORIGINS=*` (or your Vercel URL)

**Build fails:**
- Check Vercel deployment logs
- Ensure `package.json` is in `client/` folder
- Try: Delete `.vercel` folder and redeploy

**Blank page:**
- Check browser console (F12 → Console tab)
- Verify `VITE_API_URL` is set correctly
- Try: Redeploy with environment variable

---

## 💰 Free Tier Limits

### Render.com Free Tier
- ✅ 512 MB RAM
- ✅ Shared CPU
- ✅ 100 GB bandwidth/month
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ 750 hours/month (enough for 1 always-on service)

### Vercel Free Tier
- ✅ Unlimited bandwidth
- ✅ 100 GB-hours serverless execution
- ✅ Fast global CDN
- ✅ Auto HTTPS
- ✅ 100 deployments/day

---

## 🔄 Auto-Deployment

Both platforms auto-deploy on git push:

```bash
# Make changes to your code
git add .
git commit -m "Update feature"
git push origin main
```

- **Render**: Auto-deploys backend in ~3 minutes
- **Vercel**: Auto-deploys frontend in ~1 minute

---

## 🎯 Your Live URLs

After deployment, save these:

- **Frontend**: `https://med-doc-processing.vercel.app`
- **Backend**: `https://med-doc-backend.onrender.com`
- **API Docs**: `https://med-doc-backend.onrender.com/docs`

---

## 📊 Monitor Your App

### Render Dashboard
- **Logs**: Real-time backend logs
- **Metrics**: CPU, memory usage
- **Events**: Deployment history

### Vercel Dashboard
- **Analytics**: Page views, performance
- **Logs**: Build and runtime logs
- **Speed Insights**: Core Web Vitals

---

## 🚀 Next Steps

1. ✅ Share your app URL with users
2. ✅ Monitor API usage at [Anthropic Console](https://console.anthropic.com/)
3. ✅ Add custom domain (optional):
   - Vercel: Settings → Domains
   - Render: Settings → Custom Domain
4. ✅ Set up alerts:
   - Render: Settings → Notifications
   - Vercel: Settings → Notifications

---

## 💡 Tips

- **Keep backend warm**: Use a service like [UptimeRobot](https://uptimerobot.com/) to ping your backend every 5 minutes (prevents sleep)
- **API costs**: Monitor Claude API usage to stay within budget
- **Logs**: Always check logs first when debugging issues
- **Environment**: Never commit `.env` files to git

---

**🎉 Congratulations! Your app is now live and accessible worldwide!**

**Frontend**: Your Vercel URL
**Backend**: Your Render URL
**Cost**: $0/month
