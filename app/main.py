from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import get_settings
from app.database.connection import init_db
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="RAG-based Location Safety Analysis System using Groq & HuggingFace",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("=" * 60)
    logger.info("🚀 Starting Location Safety RAG Application...")
    logger.info("=" * 60)
    try:
        # Initialize database tables
        init_db()
        logger.info("✅ Database ready")
        logger.info("✅ RAG Pipeline initialized")
        logger.info("✅ Application started successfully")
        logger.info("=" * 60)
        logger.info("📖 Documentation: http://localhost:8000/docs")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down application...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
