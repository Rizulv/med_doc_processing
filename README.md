# 🏥 Patient Medical Document Intelligence

**AI-powered medical document analysis with patient-friendly features** - Built with Google Gemini (Free Tier)

## 🌟 What Makes This Different?

Unlike traditional provider-facing tools, this is built FOR PATIENTS:

- **🔄 Smart Medical Translator** - Convert complex jargon to simple language (ELI5 mode)
- **💊 Medication Intelligence** - Extract medications + check interactions automatically
- **✅ Action Items Generator** - Get clear next steps: "Schedule follow-up in 3 months"
- **💬 Document Chat** - Ask questions: "What does my cholesterol mean?"
- **📊 Health Insights** - Understand your lab results with explanations
- **🌍 Multi-language** - Hindi, Spanish support (coming soon)
- **🔒 Privacy-First** - No data storage, runs locally

---

## 🚀 Quick Start (5 minutes)

### 1. Get Your FREE Gemini API Key

**No credit card required!** Free tier includes:
- ✅ 15 requests per minute
- ✅ 1 million tokens per minute
- ✅ Perfect for testing and personal use

**Steps:**
1. Go to: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your key (starts with `AIza...`)

**🎯 Paste your API key here:** `backend-fastapi/.env` (see step 2 below)

---

### 2. Backend Setup

```bash
cd backend-fastapi

# Create virtual environment (Python 3.10+)
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# 🔑 IMPORTANT: Edit .env and paste your Gemini API key
nano .env  # or use any text editor
```

**Your `.env` file should look like:**
```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX  # Your key here
GEMINI_MODEL=gemini-1.5-flash
USE_GEMINI=true
DB_URL=sqlite:///./app.db
STORAGE_DIR=./local_storage
ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Run the backend:**
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

✅ Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) - You should see the API docs!

---

### 3. Frontend Setup

```bash
cd client

# Install dependencies (Node 18+)
npm install

# Run dev server
npm run dev
```

✅ Open [http://localhost:5173](http://localhost:5173) - You should see the app!

---

## 🎯 Features Guide

### 1. **Document Analysis** (Core)
- Upload medical documents (PDF, TXT)
- Auto-classify: CBC, BMP, X-Ray, CT, Clinical Note
- Extract ICD-10 codes with evidence
- Generate patient-friendly summary

### 2. **🔄 Medical Translator** (NEW!)
```bash
POST /api/translate
{
  "document_text": "Patient has leukocytosis...",
  "target_language": "simple"  # or "hindi", "spanish"
}
```
**Returns:** Simple explanation of medical terms

### 3. **💊 Medication Intelligence** (NEW!)
```bash
# Extract medications from document
POST /api/extract-medications
{
  "document_text": "Patient on Metformin 500mg twice daily..."
}

# Check drug interactions
POST /api/check-interactions
{
  "medications": ["Metformin", "Insulin", "Aspirin"]
}
```

### 4. **✅ Action Items Generator** (NEW!)
```bash
POST /api/action-items
{
  "document_text": "Follow up in 3 months. Repeat CBC.",
  "codes": [...]
}
```
**Returns:**
- Action items: ["Schedule follow-up in 3 months"]
- Questions: ["Ask doctor about elevated WBC"]
- Reminders: ["Bring previous test results"]
- Urgency: "routine" | "urgent" | "emergency"

### 5. **💬 Document Chat** (NEW!)
```bash
POST /api/chat
{
  "document_text": "Your lab report here...",
  "question": "What does my cholesterol result mean?",
  "conversation_history": []
}
```
**Ask anything:**
- "Should I be worried about the elevated WBC?"
- "Explain my X-ray findings in simple terms"
- "What foods should I avoid based on this report?"

---

## 📚 API Endpoints

### Core Features
- `POST /classify` - Classify document type
- `POST /extract-codes` - Extract ICD-10 codes
- `POST /summarize` - Generate summary
- `POST /documents` - Full pipeline (upload → analyze)
- `GET /documents/{id}` - Retrieve results

### Patient-Facing Features (NEW!)
- `POST /api/translate` - Translate medical jargon
- `POST /api/action-items` - Extract action items
- `POST /api/extract-medications` - Extract medications
- `POST /api/check-interactions` - Check drug interactions
- `POST /api/chat` - Chat with your document

### Evaluation
- `GET /eval/quick` - Quick eval metrics

---

## 🧪 Testing with Sample Documents

Create a test file `test_cbc.txt`:
```
CBC Report: WBC 13.2 x10^3/µL (elevated), Hgb 14.1 g/dL, Platelets 250 x10^3/µL.
Impression: leukocytosis.
```

Upload it through the UI or use cURL:
```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"document_text":"CBC Report: WBC 13.2 elevated..."}'
```

---

## 🌐 Deployment

### Option 1: Frontend on Netlify (Free)

```bash
cd client

# Build for production
npm run build

# Deploy to Netlify
# 1. Install Netlify CLI: npm install -g netlify-cli
# 2. Login: netlify login
# 3. Deploy: netlify deploy --prod
```

### Option 2: Backend on Railway/Render (Free)

**Railway:**
1. Go to [railway.app](https://railway.app)
2. Connect GitHub repo
3. Add `GEMINI_API_KEY` environment variable
4. Deploy!

**Render:**
1. Go to [render.com](https://render.com)
2. New Web Service → Connect repo
3. Build: `pip install -r backend-fastapi/requirements.txt`
4. Start: `uvicorn app.main:app --host 0.0.0.0`
5. Add `GEMINI_API_KEY` environment variable

---

## 🎨 Frontend Customization

The client uses:
- **React** + **Vite** + **TypeScript**
- **TailwindCSS** for styling
- **Chart.js** for visualizations (add this for health timeline!)

To add health timeline feature:
```bash
cd client
npm install chart.js react-chartjs-2
```

Then create a component to visualize lab results over time.

---

## 🔐 Security & Privacy

- ✅ No data storage by default (all processing in-memory)
- ✅ Client-side file processing where possible
- ✅ CORS configured for local dev
- ✅ Gemini API calls are encrypted (HTTPS)
- ⚠️ For production: Add authentication, rate limiting, input validation

---

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- Google Gemini API (gemini-1.5-flash)
- SQLAlchemy (optional DB)
- pypdf (PDF processing)

**Frontend:**
- React + Vite + TypeScript
- TailwindCSS

**Open Source Tools Used:**
- pypdf for PDF extraction (free)
- SQLite for local storage (free)
- Chart.js for visualizations (free)

---

## 📖 How to Use Open Source Alternatives

### For Voice-to-Text:
```bash
# Use browser Web Speech API (free, no API key)
# Or install OpenAI Whisper locally (free, runs on your machine)
pip install openai-whisper
```

### For PDF Generation:
```bash
pip install fpdf2  # Free, open source
```

### For Advanced RAG (Document Chat):
```bash
pip install langchain chromadb  # Already in requirements.txt!
```

---

## 🐛 Troubleshooting

### "Module not found: google.generativeai"
```bash
pip install google-generativeai
```

### "Invalid API key"
- Check your `.env` file has `GEMINI_API_KEY=AIza...`
- Make sure there are no spaces or quotes around the key
- Verify your key at [Google AI Studio](https://makersuite.google.com)

### "CORS error"
- Make sure backend is running on port 8000
- Check `ALLOW_ORIGINS` in `.env` includes your frontend URL

### "Gemini quota exceeded"
Free tier limits:
- 15 requests/minute
- 1M tokens/minute

Solution: Wait a minute or upgrade to paid tier (still very cheap!)

---

## 🎯 Roadmap

- [ ] Add voice input (Web Speech API)
- [ ] Health timeline visualization (Chart.js)
- [ ] Export to PDF reports
- [ ] Multi-language support (Hindi, Spanish)
- [ ] Mobile app (React Native)
- [ ] Offline mode (TensorFlow.js for local inference)

---

## 🤝 Contributing

This is a personal project, but feel free to:
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - Feel free to use for personal or commercial projects!

---

## 🙏 Acknowledgments

Built with:
- Google Gemini API (free tier)
- FastAPI framework
- React + Vite
- Open source Python libraries

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Rizulv/med_doc_processing/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Rizulv/med_doc_processing/discussions)

---

**Made with ❤️ for patients who want to understand their medical documents**

**🔑 Don't forget to get your free Gemini API key:** [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
