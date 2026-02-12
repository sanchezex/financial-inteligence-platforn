"""
Financial Intelligence Platform - API Endpoints Package

Individual endpoint routers for different API areas.
"""

from app.api.v1.endpoints.health import router as health
from app.api.v1.endpoints.market import router as market
from app.api.v1.endpoints.stocks import router as stocks
from app.api.v1.endpoints.macro import router as macro
from app.api.v1.endpoints.shipping import router as shipping
from app.api.v1.endpoints.news import router as news
from app.api.v1.endpoints.analytics import router as analytics
from app.api.v1.endpoints.ai import router as ai
from app.api.v1.endpoints.alerts import router as alerts
from app.api.v1.endpoints.watchlists import router as watchlists

__all__ = [
    "health",
    "market", 
    "stocks",
    "macro",
    "shipping",
    "news",
    "analytics",
    "ai",
    "alerts",
    "watchlists"
]

