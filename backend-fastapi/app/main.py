# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.routes import health, pipeline, classify, extract_codes, summarize
from app.routes.eval import router as eval_router

app = FastAPI(
    title="Medical Doc AI",
    version="0.1.0",
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
app.include_router(health.router, tags=["health"])
app.include_router(classify.router, tags=["classify"])
app.include_router(extract_codes.router, tags=["codes"])
app.include_router(summarize.router, tags=["summary"])
app.include_router(pipeline.router, tags=["pipeline"])
app.include_router(eval_router)  # /eval/*
