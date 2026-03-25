"""
Financial Intelligence Platform - Main Application Package

A Bloomberg-level real-time market intelligence platform with:
- Data ingestion engine
- Intelligence & analytics layer
- AI/NLP integration
- User dashboard
- Realtime TSDB (ClickHouse)
- Multi-API market data (Polygon/OANDA/Binance)
"""

__version__ = "2.0.0-realtime"
__author__ = "Financial Intelligence Team"

# Realtime services
from .services import (
    market_api_service,
    clickhouse_service,
    kafka_manager,
    redis_manager
)

__all__ = [
    'market_api_service',
    'clickhouse_service', 
    'kafka_manager',
    'redis_manager'
]
