# ⚡ Quick Start Guide - 5 Minutes Setup

## 📋 Prerequisites
- Python 3.10+ installed
- Node.js 18+ installed
- Git installed
- Text editor (VS Code recommended)

---

## 🔑 Step 1: Get Your FREE Gemini API Key (2 minutes)

1. **Open this link:** [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** button
4. Click **"Create API key in new project"**
5. **Copy the key** (starts with `AIza...`)

✅ **No credit card required!** Free tier includes:
- 15 requests per minute
- 1 million tokens per minute
- Perfect for personal use

---

## 🚀 Step 2: Run the Backend (2 minutes)

Open terminal and run:

```bash
# Navigate to project
cd ~/Desktop/neuralwaverizul/med_doc_processing/backend-fastapi

# Create virtual environment
python3 -m venv .venv

# Activate it (choose your OS)
# Linux/Mac:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# 🔑 EDIT .env FILE - PASTE YOUR API KEY HERE!
nano .env  # or open with VS Code/any editor
```

**Edit the `.env` file and paste your Gemini API key:**

```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXX  # 👈 PASTE YOUR KEY HERE!
GEMINI_MODEL=gemini-1.5-flash
USE_GEMINI=true
DB_URL=sqlite:///./app.db
STORAGE_DIR=./local_storage
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Save the file (Ctrl+O, Enter, Ctrl+X in nano)**

**Start the backend:**

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

✅ **Test it:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

You should see the API documentation!

---

## 🎨 Step 3: Run the Frontend (1 minute)

**Open a NEW terminal window** (keep backend running!) and run:

```bash
# Navigate to client folder
cd ~/Desktop/neuralwaverizul/med_doc_processing/client

# Install dependencies
npm install

# Start dev server
npm run dev
```

✅ **Open in browser:** [http://localhost:5173](http://localhost:5173)

You should see the app interface!

---

## 🧪 Step 4: Test It!

1. **Create a test file** `test_cbc.txt`:
   ```
   CBC Report: WBC 13.2 x10^3/µL (elevated), Hemoglobin 14.1 g/dL, Platelets 250 x10^3/µL.
   Impression: leukocytosis noted.
   ```

2. **Upload through the UI:**
   - Open [http://localhost:5173](http://localhost:5173)
   - Click "Upload Document"
   - Select `test_cbc.txt`
   - Click "Analyze"

3. **See the results:**
   - Document Type: COMPLETE BLOOD COUNT
   - ICD-10 Codes extracted
   - Patient-friendly summary

4. **Try the NEW features:**
   - Click "Translate to Simple English" (ELI5 mode)
   - Click "Extract Action Items"
   - Try the "Ask a Question" chat feature
   - Check "Medication Intelligence"

---

## 🎯 What You Can Do Now

### Core Features:
- ✅ Upload medical documents (PDF, TXT)
- ✅ Auto-classify document types
- ✅ Extract ICD-10 codes
- ✅ Generate summaries

### NEW Patient-Facing Features:
- 🔄 **Medical Translator** - "What does leukocytosis mean?"
- 💊 **Medication Checker** - Extract meds + check interactions
- ✅ **Action Items** - "Schedule follow-up in 3 months"
- 💬 **Document Chat** - Ask questions about your results
- 📊 **Simple Explanations** - No more medical jargon!

---

## 🔧 Troubleshooting

### "Module not found: google.generativeai"
```bash
pip install google-generativeai
```

### "Invalid API key"
- Double-check your `.env` file
- Make sure no spaces before/after the key
- Verify key at [Google AI Studio](https://makersuite.google.com)

### "CORS error"
- Make sure backend is running on port 8000
- Check `ALLOW_ORIGINS` in `.env`

### "Port already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python -m uvicorn app.main:app --port 8001 --reload
```

### Backend not starting?
```bash
# Check if virtual environment is activated
which python  # should show .venv path

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

---

## 📚 Next Steps

1. **Read full README:** `README.md`
2. **Deployment guide:** `DEPLOYMENT.md`
3. **API documentation:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
4. **Try all features:** Translator, Chat, Medications
5. **Deploy to Netlify:** See `DEPLOYMENT.md`

---

## 🆘 Need Help?

- **Gemini API Issues:** [Google AI Studio Help](https://ai.google.dev/docs)
- **Project Issues:** [GitHub Issues](https://github.com/Rizulv/med_doc_processing/issues)
- **Questions:** [GitHub Discussions](https://github.com/Rizulv/med_doc_processing/discussions)

---

## 🎉 You're All Set!

Your patient-facing medical document intelligence system is now running locally!

**Key points to remember:**
- ✅ Gemini API key goes in `backend-fastapi/.env`
- ✅ Free tier: 15 requests/minute
- ✅ No credit card required
- ✅ Built for patients, not providers

**Happy analyzing! 🏥**
