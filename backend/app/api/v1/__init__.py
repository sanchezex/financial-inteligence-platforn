"""
Financial Intelligence Platform - API v1 Router

Version 1 API router including all endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health, market, macro, shipping, news, 
    analytics, ai, alerts, watchlists, stocks, portfolio
)

api_router = APIRouter()

# Include all routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(market.router, prefix="/market", tags=["Market Data"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(portfolio.router, prefix="/trading", tags=["Trading"])
api_router.include_router(macro.router, prefix="/macro", tags=["Macroeconomic Data"])
api_router.include_router(shipping.router, prefix="/shipping", tags=["Shipping Data"])
api_router.include_router(news.router, prefix="/news", tags=["News"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI & NLP"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(watchlists.router, prefix="/watchlists", tags=["Watchlists"])


__all__ = ["api_router"]

