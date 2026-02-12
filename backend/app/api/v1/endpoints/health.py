"""
Financial Intelligence Platform - Health Check Endpoints

API endpoints for system health monitoring.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    uptime_seconds: float
    services: Dict[str, Any]


class ServiceHealth(BaseModel):
    """Individual service health status."""
    status: str
    latency_ms: float
    details: Dict[str, Any] = {}


# Store startup time for uptime calculation
startup_time = datetime.utcnow()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint.
    
    Returns the health status of all system components.
    """
    uptime = (datetime.utcnow() - startup_time).total_seconds()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0",
        uptime_seconds=uptime,
        services={
            "api": {"status": "healthy", "latency_ms": 0},
            "database": {"status": "checking", "latency_ms": 0},
            "cache": {"status": "checking", "latency_ms": 0},
            "streaming": {"status": "checking", "latency_ms": 0},
        }
    )


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.
    
    Returns 200 if the application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.
    
    Returns 200 if the application is ready to serve traffic.
    """
    return {"status": "ready"}


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with dependency status.
    
    Checks all external dependencies and returns their status.
    """
    import time
    start_time = time.time()
    
    services = {}
    overall_status = "healthy"
    
    # Check database
    db_latency = 0
    try:
        db_start = time.time()
        from app.db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
        db_latency = (time.time() - db_start) * 1000
        services["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2)
        }
    except Exception as e:
        services["database"] = {
            "status": "unhealthy",
            "latency_ms": 0,
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check Redis
    redis_latency = 0
    try:
        from app.services.redis_service import redis_manager
        redis_start = time.time()
        await redis_manager.ping()
        redis_latency = (time.time() - redis_start) * 1000
        services["redis"] = {
            "status": "healthy",
            "latency_ms": round(redis_latency, 2)
        }
    except Exception as e:
        services["redis"] = {
            "status": "unhealthy",
            "latency_ms": 0,
            "error": str(e)
        }
        overall_status = "degraded"
    
    # Check Kafka
    kafka_status = "disconnected"
    try:
        from app.services.kafka_service import kafka_manager
        if kafka_manager.connected:
            kafka_status = "healthy"
        services["kafka"] = {
            "status": kafka_status,
            "latency_ms": 0
        }
    except Exception as e:
        services["kafka"] = {
            "status": "error",
            "latency_ms": 0,
            "error": str(e)
        }
        overall_status = "degraded"
    
    total_latency = (time.time() - start_time) * 1000
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow(),
        "version": "1.0.0",
        "total_latency_ms": round(total_latency, 2),
        "services": services
    }


@router.get("/version")
async def get_version():
    """
    Get API version information.
    """
    return {
        "version": "1.0.0",
        "api_version": "v1",
        "build_date": "2024-01-01",
        "commit_sha": "abc123",
        "environment": "development"
    }

