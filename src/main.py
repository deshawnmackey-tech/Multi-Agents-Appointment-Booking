"""
FastAPI application entry point for Multi-Agent Appointment Booking System.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from src.config import get_settings
from src.database.session import engine, Base, init_db
import src.models  # Register all SQLAlchemy models before startup initialization.

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Multi-Agent Appointment Booking System...")
    
    # Create database tables
    try:
        init_db()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Multi-Agent Appointment Booking System...")
    engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="Multi-Agent Appointment Booking System with LangGraph",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Multi-Agent Appointment Booking System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Import and include routers
from src.api.routes import (
    auth,
    appointments,
    calendars,
    preferences,
    integrations,
    google_oauth,
    microsoft_oauth,
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
app.include_router(calendars.router, prefix="/api/calendars", tags=["Calendars"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["Preferences"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(google_oauth.router, tags=["Google OAuth"])
app.include_router(microsoft_oauth.router, tags=["Microsoft OAuth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

# Made with Bob