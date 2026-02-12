"""
Financial Intelligence Platform - Main FastAPI Application

A Bloomberg-level real-time market intelligence platform with:
- Data ingestion engine
- Intelligence & analytics layer
- AI/NLP integration
- User dashboard

This is the main entry point for the backend API service.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import init_db
from app.services.kafka_service import kafka_manager
from app.services.redis_service import redis_manager

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging incoming requests and response times."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            logger.info(
                f"Response: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Time: {process_time:.2f}s"
            )
            
            response.headers["X-Process-Time"] = str(process_time)
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise


class ExceptionHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent exception handling."""

    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(f"Unhandled exception: {exc}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
                }
            )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Financial Intelligence Platform...")
    
    startup_success = True
    services_status = {}
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        services_status["database"] = "healthy"
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        services_status["database"] = "unhealthy"
        startup_success = False
    
    try:
        # Initialize Redis connection
        logger.info("Connecting to Redis...")
        await redis_manager.connect()
        logger.info("Redis connected successfully")
        services_status["redis"] = "healthy"
        
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        services_status["redis"] = "unhealthy"
    
    try:
        # Initialize Kafka connection
        logger.info("Connecting to Kafka...")
        await kafka_manager.connect()
        logger.info("Kafka connected successfully")
        services_status["kafka"] = "healthy"
        
    except Exception as e:
        logger.error(f"Kafka connection failed: {e}")
        services_status["kafka"] = "unhealthy"
    
    if startup_success:
        logger.info("Financial Intelligence Platform started successfully!")
    else:
        logger.warning("Platform started with degraded services")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Financial Intelligence Platform...")
    
    disconnect_results = {}
    
    try:
        await kafka_manager.disconnect()
        disconnect_results["kafka"] = "disconnected"
    except Exception as e:
        logger.error(f"Error disconnecting Kafka: {e}")
        disconnect_results["kafka"] = "error"
    
    try:
        await redis_manager.disconnect()
        disconnect_results["redis"] = "disconnected"
    except Exception as e:
        logger.error(f"Error disconnecting Redis: {e}")
        disconnect_results["redis"] = "error"
    
    logger.info(f"All connections closed: {disconnect_results}")
    logger.info("Financial Intelligence Platform shut down successfully")


def create_app() -> FastAPI:
    """
    Factory function to create FastAPI application.
    Useful for testing and modular configuration.
    """
    app = FastAPI(
        title="Financial Intelligence Platform API",
        description="""
        ## Bloomberg-Level Real-Time Market Intelligence Platform
        
        A comprehensive financial intelligence system with:
        
        - **Real-Time Data**: Market data, macro data, shipping data, news
        - **Analytics Engine**: Correlation analysis, event impact analysis
        - **AI/NLP**: Sentiment analysis, summarization, intelligent insights
        - **Dashboard**: Real-time visualization, alerts, scenario simulation
        
        ### Core Features
        
        - Data ingestion from multiple sources
        - Time-series data storage and analysis
        - AI-powered insights generation
        - Customizable dashboards and watchlists
        - Real-time alerting system
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        debug=getattr(settings, 'DEBUG', True)
    )
    
    # Add middleware
    app.add_middleware(ExceptionHandlingMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if getattr(settings, 'DEBUG', True) else settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(api_router, prefix="/api/v1")
    
    return app


# Create FastAPI application
app = create_app()


# Health check endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Basic health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "Financial Intelligence Platform",
        "version": "1.0.0"
    }


@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """
    Detailed health check including dependency status.
    """
    health_status = {
        "status": "healthy",
        "service": "Financial Intelligence Platform",
        "version": "1.0.0",
        "dependencies": {}
    }
    
    # Check Redis
    try:
        await redis_manager.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Kafka
    try:
        if kafka_manager.connected:
            health_status["dependencies"]["kafka"] = "healthy"
        else:
            health_status["dependencies"]["kafka"] = "disconnected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["kafka"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "Financial Intelligence Platform API",
        "version": "1.0.0",
        "description": "Bloomberg-level real-time market intelligence platform",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=getattr(settings, 'DEBUG', False),
        log_level="info"
    )
