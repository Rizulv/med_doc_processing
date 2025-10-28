from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db.database import init_db
from app.routes import health, documents, classify, codes, summary

# Initialize FastAPI app
app = FastAPI(
    title="Medical Doc AI",
    description="AI-powered medical document classification, ICD-10 code extraction, and clinical summarization",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, tags=["Documents"])
app.include_router(classify.router, tags=["Classification"])
app.include_router(codes.router, tags=["Codes"])
app.include_router(summary.router, tags=["Summary"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
async def root():
    """Root endpoint - service information"""
    return {
        "service": "Medical Doc AI",
        "version": "1.0.0",
        "description": "AI-powered medical document analysis",
        "endpoints": {
            "health": "/health",
            "upload": "POST /documents",
            "list": "GET /documents",
            "detail": "GET /documents/{id}",
            "classify": "POST /classify",
            "extract_codes": "POST /extract-codes",
            "summarize": "POST /summarize"
        },
        "stub_mode": not settings.use_claude_real
    }
