# 🚀 Deployment Guide

## Frontend (Netlify) - FREE

### Option 1: Netlify UI (Easiest)

1. Push your code to GitHub
2. Go to [Netlify](https://netlify.com) and sign up/login
3. Click "Add new site" → "Import an existing project"
4. Connect to GitHub and select `med_doc_processing` repo
5. **Build settings:**
   - Base directory: `client`
   - Build command: `npm run build`
   - Publish directory: `client/dist`
6. Add environment variable:
   - `VITE_API_BASE` = your backend URL (see backend deployment below)
7. Click "Deploy site"

✅ Your frontend will be live at `https://your-site.netlify.app`

### Option 2: Netlify CLI

```bash
cd client

# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Initialize (first time only)
netlify init

# Deploy
netlify deploy --prod
```

---

## Backend (Railway/Render) - FREE

### Option 1: Railway (Recommended)

**Why Railway?**
- ✅ Generous free tier
- ✅ Auto SSL/HTTPS
- ✅ Easy environment variables
- ✅ GitHub integration

**Steps:**

1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select `med_doc_processing` repo
5. Railway will auto-detect Python
6. **Add environment variables:**
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-1.5-flash
   USE_GEMINI=true
   DB_URL=sqlite:///./app.db
   STORAGE_DIR=./local_storage
   ALLOW_ORIGINS=https://your-netlify-site.netlify.app
   ```
7. **Add `railway.json` to backend-fastapi folder:**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```
8. Deploy!

✅ Your backend will be live at `https://your-app.up.railway.app`

### Option 2: Render

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. New → "Web Service"
4. Connect `med_doc_processing` repo
5. **Settings:**
   - Name: `med-doc-api`
   - Region: Choose closest to you
   - Branch: `main`
   - Root Directory: `backend-fastapi`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables:** (same as Railway above)
7. Click "Create Web Service"

✅ Your backend will be live at `https://your-app.onrender.com`

---

## Connect Frontend to Backend

After deploying backend, update frontend:

### On Netlify:

1. Go to Site settings → Environment variables
2. Add:
   ```
   VITE_API_BASE = https://your-backend-url.railway.app
   ```
3. Redeploy site

### In code (client/.env.production):

```env
VITE_API_BASE=https://your-backend-url.railway.app
```

---

## Update Backend CORS

After deploying frontend, update backend environment variable:

```env
ALLOW_ORIGINS=https://your-netlify-site.netlify.app,http://localhost:5173
```

This allows your frontend to make API calls.

---

## Testing Deployment

1. **Backend health check:**
   ```bash
   curl https://your-backend-url.railway.app/health
   ```

2. **Frontend access:**
   Open `https://your-netlify-site.netlify.app` in browser

3. **Full test:**
   - Upload a sample medical document
   - Should see classification, codes, summary
   - Try chat feature

---

## Custom Domain (Optional)

### Netlify:
1. Site settings → Domain management
2. Add custom domain
3. Follow DNS instructions

### Railway:
1. Project settings → Domains
2. Add custom domain
3. Point DNS to Railway

---

## Cost Estimate

**Monthly costs for moderate usage:**

| Service | Free Tier | Paid (if needed) |
|---------|-----------|------------------|
| Netlify | 100GB bandwidth | $19/month for Pro |
| Railway | 500 hours/month | $5/month for extra hours |
| Render | 750 hours/month | $7/month for paid tier |
| Gemini API | 15 req/min (free!) | $0.35 per 1M tokens |

**Total: $0/month for personal use, ~$20-30/month for production**

---

## Monitoring & Logs

### Railway:
- Click on your service → "Logs" tab
- Real-time log streaming

### Render:
- Dashboard → Your service → "Logs"

### Netlify:
- Site dashboard → "Deploys" → Click deploy → "Deploy log"

---

## Troubleshooting

### "502 Bad Gateway" on backend
- Check Railway/Render logs
- Verify `PORT` environment variable is set correctly
- Make sure `--host 0.0.0.0 --port $PORT` in start command

### "Failed to fetch" on frontend
- Check CORS settings in backend `.env`
- Verify `VITE_API_BASE` in Netlify environment variables
- Make sure backend is running (check health endpoint)

### Gemini API errors
- Verify `GEMINI_API_KEY` is set in backend environment
- Check quota at [Google AI Studio](https://makersuite.google.com)
- Free tier: 15 requests/minute

---

## Auto-Deploy (CD)

Both Netlify and Railway support auto-deploy:

1. Push to `main` branch
2. Netlify automatically rebuilds frontend
3. Railway automatically rebuilds backend

✅ No manual deployment needed!

---

## Rollback

### Netlify:
- Site dashboard → "Deploys"
- Click on old deploy → "Publish deploy"

### Railway:
- Project → "Deployments"
- Click on old deployment → "Redeploy"

---

**Need help?** Open an issue on GitHub or check the logs!
