"""
Financial Intelligence Platform - Watchlists Endpoints

API endpoints for managing user watchlists and symbol collections.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import uuid

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class WatchlistItem(BaseModel):
    """Watchlist item model."""
    symbol: str
    name: Optional[str]
    added_at: datetime


class WatchlistCreate(BaseModel):
    """Watchlist creation model."""
    name: str
    description: Optional[str]
    symbols: List[str]


class WatchlistUpdate(BaseModel):
    """Watchlist update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    symbols: Optional[List[str]] = None


class WatchlistResponse(BaseModel):
    """Watchlist response model."""
    id: str
    user_id: str
    name: str
    description: Optional[str]
    symbols: List[str]
    item_count: int
    created_at: datetime
    updated_at: datetime


class WatchlistWithData(WatchlistResponse):
    """Watchlist with current market data."""
    items: List[Dict[str, Any]]


# ============================================================================
# Watchlists CRUD Endpoints
# ============================================================================

@router.get("/")
async def get_watchlists(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """
    Get user's watchlists.
    
    Returns list of watchlists.
    """
    # Mock watchlists data
    watchlists = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_123",
            "name": "Tech Stocks",
            "description": "Technology sector watchlist",
            "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD"],
            "created_at": datetime.utcnow() - timedelta(days=90),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_123",
            "name": "Dividend Aristocrats",
            "description": "Stocks with 25+ years of dividend increases",
            "symbols": ["KO", "JNJ", "PG", "MCD", "WMT", "PEP"],
            "created_at": datetime.utcnow() - timedelta(days=60),
            "updated_at": datetime.utcnow()
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "user_123",
            "name": "Commodities",
            "description": "Commodity-related stocks",
            "symbols": ["XOM", "CVX", "COP", "NEM", "FCX", "SLB"],
            "created_at": datetime.utcnow() - timedelta(days=30),
            "updated_at": datetime.utcnow()
        }
    ]
    
    return {
        "watchlists": watchlists[offset:offset + limit],
        "total": len(watchlists),
        "limit": limit,
        "offset": offset
    }


@router.get("/{watchlist_id}", response_model=WatchlistResponse)
async def get_watchlist(watchlist_id: str):
    """
    Get a specific watchlist.
    
    Returns watchlist details.
    """
    # Mock single watchlist
    watchlist = {
        "id": watchlist_id,
        "user_id": "user_123",
        "name": "Tech Stocks",
        "description": "Technology sector watchlist",
        "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD"],
        "created_at": datetime.utcnow() - timedelta(days=90),
        "updated_at": datetime.utcnow()
    }
    
    return WatchlistResponse(**watchlist)


@router.get("/{watchlist_id}/data")
async def get_watchlist_with_data(watchlist_id: str):
    """
    Get watchlist with current market data.
    
    Returns watchlist with real-time prices and metrics.
    """
    import random
    
    watchlist = {
        "id": watchlist_id,
        "user_id": "user_123",
        "name": "Tech Stocks",
        "description": "Technology sector watchlist",
        "symbols": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD"],
        "created_at": datetime.utcnow() - timedelta(days=90),
        "updated_at": datetime.utcnow(),
        "items": []
    }
    
    # Add market data for each symbol
    symbol_data = {
        "AAPL": {"name": "Apple Inc.", "price": 178.50, "change": 2.35},
        "MSFT": {"name": "Microsoft Corporation", "price": 378.25, "change": 4.12},
        "GOOGL": {"name": "Alphabet Inc.", "price": 141.80, "change": -1.25},
        "AMZN": {"name": "Amazon.com Inc.", "price": 178.35, "change": 3.45},
        "NVDA": {"name": "NVIDIA Corporation", "price": 495.22, "change": 12.50},
        "META": {"name": "Meta Platforms Inc.", "price": 505.75, "change": 8.25},
        "TSLA": {"name": "Tesla Inc.", "price": 248.50, "change": -5.75},
        "AMD": {"name": "Advanced Micro Devices", "price": 145.30, "change": 3.80}
    }
    
    for symbol in watchlist["symbols"]:
        data = symbol_data.get(symbol, {"name": symbol, "price": 100 + random.random() * 200, "change": random.uniform(-5, 5)})
        watchlist["items"].append({
            "symbol": symbol,
            "name": data["name"],
            "price": Decimal(str(round(data["price"], 2))),
            "change": Decimal(str(round(data["change"], 2))),
            "change_percent": round(data["change"] / data["price"] * 100, 2),
            "volume": int(random.randint(1000000, 50000000)),
            "market_cap": Decimal(str(round(100 + random.random() * 2000, 0))) + "B",
            "pe_ratio": round(random.uniform(15, 50), 1),
            "dividend_yield": round(random.uniform(0, 3), 2),
            "high_52w": round(data["price"] * (1 + random.uniform(0.1, 0.3)), 2),
            "low_52w": round(data["price"] * (1 - random.uniform(0.1, 0.3)), 2)
        })
    
    return WatchlistWithData(**watchlist)


@router.post("/")
async def create_watchlist(watchlist: WatchlistCreate):
    """
    Create a new watchlist.
    
    Returns created watchlist with ID.
    """
    watchlist_id = str(uuid.uuid4())
    
    created = {
        "id": watchlist_id,
        "user_id": "user_123",  # Would come from auth
        "name": watchlist.name,
        "description": watchlist.description,
        "symbols": watchlist.symbols,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    logger.info(f"Created watchlist: {watchlist_id}")
    
    return WatchlistResponse(**created)


@router.put("/{watchlist_id}")
async def update_watchlist(watchlist_id: str, update: WatchlistUpdate):
    """
    Update an existing watchlist.
    
    Returns updated watchlist.
    """
    updated = {
        "id": watchlist_id,
        "user_id": "user_123",
        "name": update.name or "Updated Watchlist",
        "description": update.description,
        "symbols": update.symbols or [],
        "created_at": datetime.utcnow() - timedelta(days=30),
        "updated_at": datetime.utcnow()
    }
    
    return WatchlistResponse(**updated)


@router.delete("/{watchlist_id}")
async def delete_watchlist(watchlist_id: str):
    """
    Delete a watchlist.
    
    Returns confirmation of deletion.
    """
    logger.info(f"Deleting watchlist: {watchlist_id}")
    
    return {
        "status": "deleted",
        "watchlist_id": watchlist_id,
        "deleted_at": datetime.utcnow()
    }


# ============================================================================
# Watchlist Items Endpoints
# ============================================================================

@router.post("/{watchlist_id}/items/{symbol}")
async def add_symbol_to_watchlist(watchlist_id: str, symbol: str):
    """
    Add a symbol to a watchlist.
    
    Returns updated watchlist.
    """
    return {
        "watchlist_id": watchlist_id,
        "symbol": symbol.upper(),
        "action": "added",
        "added_at": datetime.utcnow()
    }


@router.delete("/{watchlist_id}/items/{symbol}")
async def remove_symbol_from_watchlist(watchlist_id: str, symbol: str):
    """
    Remove a symbol from a watchlist.
    
    Returns updated watchlist.
    """
    return {
        "watchlist_id": watchlist_id,
        "symbol": symbol.upper(),
        "action": "removed",
        "removed_at": datetime.utcnow()
    }


@router.put("/{watchlist_id}/items/reorder")
async def reorder_watchlist_items(watchlist_id: str, symbols: List[str]):
    """
    Reorder symbols in a watchlist.
    
    Returns updated watchlist.
    """
    return {
        "watchlist_id": watchlist_id,
        "symbols": symbols,
        "reordered_at": datetime.utcnow()
    }


# ============================================================================
# Shared Watchlists Endpoints
# ============================================================================

@router.get("/shared/{share_id}")
async def get_shared_watchlist(share_id: str):
    """
    Get a shared watchlist by share ID.
    
    Returns public watchlist data.
    """
    import random
    
    return {
        "share_id": share_id,
        "name": "Public Tech Watchlist",
        "description": "A curated list of top tech stocks",
        "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA", "META"],
        "created_by": "Financial Analyst",
        "created_at": datetime.utcnow() - timedelta(days=60),
        "items": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 178.50,
                "change_percent": 1.33,
                "reason": "Strong iPhone sales and services growth"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "price": 378.25,
                "change_percent": 1.10,
                "reason": "Cloud growth and AI integration"
            },
            {
                "symbol": "GOOGL",
                "name": "Alphabet Inc.",
                "price": 141.80,
                "change_percent": -0.87,
                "reason": "Advertising recovery and AI investments"
            }
        ]
    }


@router.post("/{watchlist_id}/share")
async def share_watchlist(watchlist_id: str):
    """
    Create a share link for a watchlist.
    
    Returns share ID and link.
    """
    import random
    
    share_id = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    
    return {
        "watchlist_id": watchlist_id,
        "share_id": share_id,
        "share_link": f"/watchlists/shared/{share_id}",
        "is_public": True,
        "created_at": datetime.utcnow()
    }


# ============================================================================
# Watchlist Templates Endpoints
# ============================================================================

@router.get("/templates")
async def get_watchlist_templates():
    """
    Get predefined watchlist templates.
    
    Returns commonly used watchlist configurations.
    """
    templates = [
        {
            "id": "sp500_top10",
            "name": "S&P 500 Top 10",
            "description": "Largest S&P 500 companies by market cap",
            "symbols": ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK.B", "JPM", "JNJ"],
            "category": "Index"
        },
        {
            "id": "dow_jones",
            "name": "Dow Jones Industrial",
            "description": "30 Dow Jones Industrial Average stocks",
            "symbols": ["AAPL", "AMGN", "AXP", "BA", "CAT", "CRM", "CSCO", "CVX", "DIS", "DD"],
            "category": "Index"
        },
        {
            "id": "nasdaq_100",
            "name": "NASDAQ 100",
            "description": "Largest 100 NASDAQ-listed companies",
            "symbols": ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "AMD", "INTC", "CRM"],
            "category": "Index"
        },
        {
            "id": "aristocrats",
            "name": "Dividend Aristocrats",
            "description": "S&P 500 stocks with 25+ years of dividend increases",
            "symbols": ["KO", "JNJ", "PG", "MCD", "WMT", "PEP", "TGT", "LOW", "MMM", "GPC"],
            "category": "Dividend"
        },
        {
            "id": "cleantech",
            "name": "Clean Technology",
            "description": "Leading clean energy and sustainability stocks",
            "symbols": ["ENPH", "SEDG", "NEE", "DUK", "SO", "ED", "AEE", "EXC", "XEL", "PEG"],
            "category": "Theme"
        },
        {
            "id": "ai_stocks",
            "name": "AI & Machine Learning",
            "description": "Companies leading in artificial intelligence",
            "symbols": ["NVDA", "AMD", "INTC", "QCOM", "MSFT", "GOOGL", "AMZN", "META", "PLTR", "AI"],
            "category": "Theme"
        },
        {
            "id": "ev_transportation",
            "name": "Electric Vehicles",
            "description": "Electric vehicle and autonomous driving stocks",
            "symbols": ["TSLA", "RIVN", "LCID", "NIO", "XPEV", "LI", "F", "GM", "NVDA", "QCOM"],
            "category": "Theme"
        },
        {
            "id": "semiconductors",
            "name": "Semiconductor Leaders",
            "description": "Major semiconductor and chip companies",
            "symbols": ["NVDA", "AMD", "INTC", "QCOM", "TXN", "AVGO", "MU", "AMAT", "LRCX", "KLAC"],
            "category": "Sector"
        },
        {
            "id": "cloud_computing",
            "name": "Cloud Computing",
            "description": "Leading cloud services and infrastructure",
            "symbols": ["AMZN", "MSFT", "GOOGL", "META", "IBM", "ORCL", "CRM", "WORK", "DDOG", "NET"],
            "category": "Sector"
        },
        {
            "id": "global banks",
            "name": "Global Banks",
            "description": "Major international banking institutions",
            "symbols": ["JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW", "AXP", "V"],
            "category": "Sector"
        }
    ]
    
    return {
        "templates": templates,
        "total": len(templates)
    }


@router.post("/from-template/{template_id}")
async def create_from_template(template_id: str, name: str, description: Optional[str] = None):
    """
    Create a watchlist from a template.
    
    Returns created watchlist.
    """
    import random
    
    templates = {
        "sp500_top10": ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK.B", "JPM", "JNJ"],
        "aristocrats": ["KO", "JNJ", "PG", "MCD", "WMT", "PEP", "TGT", "LOW", "MMM", "GPC"],
    }
    
    symbols = templates.get(template_id, [])
    
    if not symbols:
        raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
    
    watchlist_id = str(uuid.uuid4())
    
    created = {
        "id": watchlist_id,
        "user_id": "user_123",
        "name": name,
        "description": description or f"Created from template {template_id}",
        "symbols": symbols,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    return WatchlistResponse(**created)

