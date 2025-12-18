# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.routes import health, pipeline, classify, extract_codes, summarize
from app.routes.eval import router as eval_router
from app.routes.translator import router as translator_router
from app.routes.action_items import router as action_items_router
from app.routes.medications import router as medications_router
from app.routes.chat import router as chat_router

app = FastAPI(
    title="Patient Medical Document Intelligence",
    description="AI-powered medical document analysis with patient-friendly features",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---- CORS ----
# Prefer comma-separated ALLOW_ORIGINS env (e.g., "http://localhost:5173,http://127.0.0.1:5173")
origins = (
    settings.allow_origins.split(",")
    if getattr(settings, "allow_origins", None)
    else ["http://localhost:5173", "http://127.0.0.1:5173"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Startup hooks ----
@app.on_event("startup")
def _on_startup():
    init_db()

# ---- Routers ----
# Core features
app.include_router(health.router, tags=["health"])
app.include_router(classify.router, tags=["classify"])
app.include_router(extract_codes.router, tags=["codes"])
app.include_router(summarize.router, tags=["summary"])
app.include_router(pipeline.router, tags=["pipeline"])
app.include_router(eval_router)  # /eval/*

# Innovative patient-facing features
app.include_router(translator_router, tags=["translator"], prefix="/api")
app.include_router(action_items_router, tags=["action-items"], prefix="/api")
app.include_router(medications_router, tags=["medications"], prefix="/api")
app.include_router(chat_router, tags=["chat"], prefix="/api")
