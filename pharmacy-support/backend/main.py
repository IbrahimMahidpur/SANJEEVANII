from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from config import get_settings
from routes import vaccine, llm
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Pharmacy Support API",
    description="Backend API for Sanjeevani Pharmacy Support Module",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vaccine.router)
app.include_router(llm.router)

# Import and include health camps router
from routes import health_camps, pharmacy, places
app.include_router(health_camps.router)
app.include_router(pharmacy.router)
app.include_router(places.router)



@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Pharmacy Support API",
        "version": "1.0.0",
        "endpoints": {
            "vaccine_centers": "/api/v1/vaccine-centers",
            "llm_chat": "/api/v1/llm",
            "llm_health": "/api/v1/llm/health",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    # Check Ollama connection
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:11434/api/tags", timeout=3.0)
            ollama_connected = response.status_code == 200
    except:
        ollama_connected = False
    
    return {
        "status": "healthy",
        "ollama_connected": ollama_connected,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("🚀 Pharmacy Support API starting up...")
    logger.info(f"📍 Server running on {settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"🤖 Ollama URL: {settings.OLLAMA_URL}")
    logger.info(f"🧠 Model: {settings.OLLAMA_MODEL}")
    logger.info(f"🌐 CORS origins: {settings.cors_origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("👋 Pharmacy Support API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )



