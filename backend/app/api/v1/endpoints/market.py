"""
Financial Intelligence Platform - Market Data Endpoints

API endpoints for real-time market data including stocks, forex, and commodities.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.services.redis_service import redis_manager
from app.services.kafka_service import kafka_manager

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class QuoteRequest(BaseModel):
    """Request model for fetching quotes."""
    symbols: List[str] = Field(..., description="List of asset symbols")
    asset_type: Optional[str] = Field(None, description="Asset type (stock, forex, commodity)")


class QuoteResponse(BaseModel):
    """Real-time quote response model."""
    symbol: str
    asset_type: str
    exchange: Optional[str]
    price: Optional[Decimal]
    change: Optional[Decimal]
    change_percent: Optional[float]
    volume: Optional[int]
    bid: Optional[Decimal]
    ask: Optional[Decimal]
    timestamp: datetime
    data_source: str


class HistoricalDataRequest(BaseModel):
    """Request model for historical data."""
    symbol: str
    asset_type: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    period: str = Field(default="daily", description="daily, weekly, monthly")
    limit: int = Field(default=100, le=5000)


class OHLCV(BaseModel):
    """OHLCV bar data model."""
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Optional[int]
    vwap: Optional[Decimal]


class HistoricalDataResponse(BaseModel):
    """Historical data response model."""
    symbol: str
    asset_type: str
    data: List[OHLCV]
    total_records: int
    period: str


class MarketSummary(BaseModel):
    """Market summary for indices."""
    symbol: str
    name: str
    current_value: Decimal
    change: Decimal
    change_percent: float
    high: Optional[Decimal]
    low: Optional[Decimal]
    volume: Optional[int]
    timestamp: datetime


class MarketStatus(BaseModel):
    """Market status response."""
    market_status: str  # open, closed, pre-market, after-hours
    trading_hours: Dict[str, Any]
    upcoming_events: List[Dict[str, Any]]


# ============================================================================
# Real-time Quote Endpoints
# ============================================================================

@router.get("/quotes/{symbol}", response_model=QuoteResponse)
async def get_quote(symbol: str, asset_type: Optional[str] = None):
    """
    Get real-time quote for a single symbol.
    
    Returns the latest price, volume, and bid/ask data.
    """
    cache_key = f"quote:{symbol}:{asset_type or 'stock'}"
    
    try:
        # Try to get from Redis cache first
        cached_data = await redis_manager.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {cache_key}")
            return QuoteResponse(**cached_data)
        
        # If not in cache, fetch from data source
        # This is where you'd integrate with actual market data APIs
        quote_data = {
            "symbol": symbol,
            "asset_type": asset_type or "stock",
            "exchange": "NASDAQ",
            "price": Decimal("150.25"),
            "change": Decimal("2.50"),
            "change_percent": 1.69,
            "volume": 15000000,
            "bid": Decimal("150.20"),
            "ask": Decimal("150.30"),
            "timestamp": datetime.utcnow(),
            "data_source": "mock_data"
        }
        
        # Cache the data for 1 second (real-time data)
        await redis_manager.setex(cache_key, 1, quote_data)
        
        return QuoteResponse(**quote_data)
        
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching quote: {str(e)}")


@router.post("/quotes", response_model=List[QuoteResponse])
async def get_batch_quotes(request: QuoteRequest):
    """
    Get real-time quotes for multiple symbols.
    
    Efficiently fetches quotes for multiple assets in a single request.
    """
    quotes = []
    
    for symbol in request.symbols:
        try:
            quote = await get_quote(symbol, request.asset_type)
            quotes.append(quote)
        except Exception as e:
            logger.warning(f"Error fetching quote for {symbol}: {e}")
            quotes.append(QuoteResponse(
                symbol=symbol,
                asset_type=request.asset_type or "stock",
                exchange=None,
                price=None,
                change=None,
                change_percent=None,
                volume=None,
                bid=None,
                ask=None,
                timestamp=datetime.utcnow(),
                data_source="error"
            ))
    
    return quotes


@router.get("/quotes/stream/{symbol}")
async def stream_quote(symbol: str, asset_type: Optional[str] = None):
    """
    Stream real-time quotes via WebSocket.
    
    Note: This is a placeholder. Actual streaming requires WebSocket setup.
    """
    return {
        "message": "WebSocket streaming endpoint",
        "symbol": symbol,
        "asset_type": asset_type or "stock",
        "instructions": "Connect to ws://host:8000/ws/quotes/{symbol} for real-time streaming"
    }


# ============================================================================
# Historical Data Endpoints
# ============================================================================

@router.get("/historical/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str,
    asset_type: str = Query(..., description="Asset type: stock, forex, commodity"),
    period: str = Query(default="daily", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    limit: int = Query(default=100, le=5000)
):
    """
    Get historical price data for a symbol.
    
    Returns OHLCV data for the specified time period.
    """
    cache_key = f"historical:{symbol}:{asset_type}:{period}:{start_date}:{end_date}:{limit}"
    
    try:
        # Try cache first
        cached_data = await redis_manager.get(cache_key)
        if cached_data:
            return HistoricalDataResponse(**cached_data)
        
        # Generate mock historical data
        # In production, this would query ClickHouse or the database
        end = end_date or datetime.utcnow()
        start = start_date or (end - timedelta(days=limit))
        
        data = []
        current_date = start
        base_price = Decimal("150.00")
        
        while current_date <= end:
            # Skip weekends for daily data
            if period == "daily" and current_date.weekday() >= 5:
                current_date += timedelta(days=1)
                continue
            
            # Generate realistic-looking price movement
            import random
            change = (random.random() - 0.5) * 5
            open_price = base_price
            close_price = base_price + change
            high_price = max(open_price, close_price) + random.random() * 2
            low_price = min(open_price, close_price) - random.random() * 2
            
            data.append(OHLCV(
                timestamp=current_date,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=int(random.random() * 10000000),
                vwap=round((open_price + close_price) / 2, 2)
            ))
            
            base_price = close_price
            current_date += timedelta(days=1)
        
        response = HistoricalDataResponse(
            symbol=symbol,
            asset_type=asset_type,
            data=data,
            total_records=len(data),
            period=period
        )
        
        # Cache for 5 minutes
        await redis_manager.setex(cache_key, 300, response.dict())
        
        return response
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")


# ============================================================================
# Market Summary Endpoints
# ============================================================================

@router.get("/summary", response_model=List[MarketSummary])
async def get_market_summary():
    """
    Get NSE Kenya indices summary.
    """
    # NSE Kenya indices
    indices = [
        {"symbol": "NSE20", "name": "NSE 20 Index"},
        {"symbol": "NSI", "name": "NSE All Share Index"},
    ]
    
    summaries = []
    for index in indices:
        base_values = {'NSE20': 1850, 'NSI': 165}
        value = base_values.get(index["symbol"], 1800)
        value += (random.random() - 0.5) * 20
        change = (random.random() - 0.5) * 10
        
        summaries.append(MarketSummary(
            symbol=index["symbol"],
            name=index["name"],
            current_value=round(Decimal(str(value)), 2),
            change=round(Decimal(str(change)), 2),
            change_percent=round(change / value * 100, 2),
            high=round(Decimal(str(value + abs(change) + random.random() * 5)), 2),
            low=round(Decimal(str(value - abs(change) - random.random() * 5)), 2),
            volume=int(random.random() * 10000000),
            timestamp=datetime.utcnow()
        ))
    
    return summaries


@router.get("/status", response_model=MarketStatus)
async def get_market_status():
    """
    Get NSE Kenya market status.
    """
    from datetime import datetime, time
    from zoneinfo import ZoneInfo
    
    # Nairobi time (EAT UTC+3)
    nairobi_tz = ZoneInfo("Africa/Nairobi")
    now = datetime.now(nairobi_tz)
    current_time = now.time()
    
    # NSE hours: 10:00 AM - 3:00 PM EAT Mon-Fri
    market_open = time(10, 0)
    market_close = time(15, 0)
    
    weekday = now.weekday()
    if weekday >= 5:  # Weekend
        status = "closed"
    elif current_time >= market_open and current_time <= market_close:
        status = "open"
    elif current_time < market_open:
        status = "pre-open"
    else:
        status = "closed"
    
    return MarketStatus(
        market_status=status,
        trading_hours={
            "NSE Kenya": {
                "pre_open": {"start": "09:00", "end": "10:00"},
                "regular": {"start": "10:00", "end": "15:00"}
            }
        },
        upcoming_events=[
            {
                "type": "earnings",
                "symbol": "SCOM",
                "date": (now + timedelta(days=2)).isoformat(),
                "importance": "high"
            },
            {
                "type": "economic",
                "event": "CBK Rate Decision",
                "date": (now + timedelta(days=5)).isoformat(),
                "importance": "high"
            }
        ]
    )


# ============================================================================
# Search and Discovery Endpoints
# ============================================================================

@router.get("/search")
async def search_symbols(
    query: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(default=10, le=50)
):
    """
    Search NSE symbols.
    """
    nse_stocks = [
        {"symbol": "SCOM", "name": "Safaricom PLC", "exchange": "NSE", "sector": "Telecom"},
        {"symbol": "NBK", "name": "NCBA Bank", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "KCB", "name": "KCB Group", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "EABL", "name": "East African Breweries", "exchange": "NSE", "sector": "Beverages"},
        {"symbol": "BAT", "name": "British American Tobacco", "exchange": "NSE", "sector": "Tobacco"},
        {"symbol": "ABSA", "name": "ABSA Bank Kenya", "exchange": "NSE", "sector": "Banking"},
    ]
    
    query_lower = query.lower()
    results = [
        r for r in nse_stocks 
        if query_lower in r["symbol"].lower() or query_lower in r["name"].lower()
    ]
    
    return {
        "query": query,
        "results": results[:limit],
        "total": len(results)
    }


@router.get("/trending")
async def get_trending_symbols(limit: int = Query(default=10, le=50)):
    """
    Get NSE trending stocks.
    """
    trending = [
        {"symbol": "SCOM", "name": "Safaricom", "reason": "High volume", "score": 95},
        {"symbol": "KCB", "name": "KCB Group", "reason": "Earnings beat", "score": 88},
        {"symbol": "NBK", "name": "NCBA Bank", "reason": "Dividend announcement", "score": 82},
        {"symbol": "EABL", "name": "East African Breweries", "reason": "Sector rotation", "score": 78},
        {"symbol": "BAT", "name": "BAT Kenya", "reason": "Defensive play", "score": 75},
    ]
    
    return {
        "timestamp": datetime.utcnow(),
        "trending": trending[:limit]
    }

