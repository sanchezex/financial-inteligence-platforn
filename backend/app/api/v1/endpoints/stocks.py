"""
Financial Intelligence Platform - Stocks Endpoints

API endpoints for stock-specific data including fundamentals, earnings, and company info.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class CompanyInfo(BaseModel):
    """Company information model."""
    symbol: str
    name: str
    exchange: Optional[str]
    sector: Optional[str]
    industry: Optional[str]
    country: Optional[str]
    currency: Optional[str]
    market_cap: Optional[Decimal]
    description: Optional[str]
    website: Optional[str]


class FundamentalData(BaseModel):
    """Fundamental data model."""
    symbol: str
    period_type: str
    period_end: datetime
    revenue: Optional[Decimal]
    net_income: Optional[Decimal]
    eps: Optional[Decimal]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    roe: Optional[float]


class EarningsData(BaseModel):
    """Earnings data model."""
    symbol: str
    quarter: str
    fiscal_year: int
    eps_estimate: Optional[Decimal]
    eps_actual: Optional[Decimal]
    revenue_estimate: Optional[Decimal]
    revenue_actual: Optional[Decimal]
    report_date: Optional[datetime]
    call_date: Optional[datetime]


class StockScreenerRequest(BaseModel):
    """Stock screener request model."""
    min_market_cap: Optional[Decimal] = None
    max_market_cap: Optional[Decimal] = None
    min_pe: Optional[float] = None
    max_pe: Optional[float] = None
    min_dividend_yield: Optional[float] = None
    sectors: Optional[List[str]] = None
    exchanges: Optional[List[str]] = None
    limit: int = 50


class StockScreenerResult(BaseModel):
    """Stock screener result model."""
    symbol: str
    name: str
    sector: Optional[str]
    market_cap: Optional[Decimal]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    price: Optional[Decimal]
    change_percent: Optional[float]


# ============================================================================
# Company Info Endpoints
# ============================================================================

@router.get("/info/{symbol}", response_model=CompanyInfo)
async def get_company_info(symbol: str, db: Session = Depends(get_db)):
    """
    Get company information for a symbol.
    
    Returns basic company details, sector, industry, and market cap.
    """
    from app.db.models import Stock
    
    # Try to get from database
    stock = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    
    if stock:
        return CompanyInfo(
            symbol=stock.symbol,
            name=stock.company_name,
            exchange=stock.exchange,
            sector=stock.sector,
            industry=stock.industry,
            country=None,
            currency="USD",
            market_cap=stock.market_cap,
            description=None,
            website=None
        )
    
    # Fallback to mock data if not in database
nse_companies = {
        "SCOM": {
            "symbol": "SCOM",
            "name": "Safaricom PLC",
            "exchange": "NSE",
            "sector": "Telecommunications",
            "industry": "Mobile Services",
            "country": "Kenya",
            "currency": "KES",
            "market_cap": Decimal("850000000000"),
            "description": "Safaricom PLC provides mobile, fixed line and financial services in Kenya.",
            "website": "https://www.safaricom.co.ke"
        },
        "NBK": {
            "symbol": "NBK",
            "name": "NCBA Bank Group PLC",
            "exchange": "NSE",
            "sector": "Financial Services",
            "industry": "Banking",
            "country": "Kenya",
            "currency": "KES",
            "market_cap": Decimal("120000000000"),
            "description": "NCBA Bank Group PLC provides banking services to corporate, SME and retail customers.",
            "website": "https://ke.ncbagroup.com"
        },
        "KCB": {
            "symbol": "KCB",
            "name": "KCB Group PLC",
            "exchange": "NSE",
            "sector": "Financial Services",
            "industry": "Banking",
            "country": "Kenya",
            "currency": "KES",
            "market_cap": Decimal("110000000000"),
            "description": "KCB Group PLC is a financial services organization.",
            "website": "https://kcbgroup.com"
        }
    }
    
    company = nse_companies.get(symbol.upper())
    
    if not company:
        raise HTTPException(status_code=404, detail=f"NSE company not found: {symbol}")
    
    return CompanyInfo(**company)


@router.get("/list")
async def get_stock_list(
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    limit: int = Query(default=100, le=500)
):
    """
    Get list of stocks with optional filtering.
    
    Returns stocks filtered by exchange and/or sector.
    """
    # Mock data
    nse_stocks = [
        {"symbol": "SCOM", "name": "Safaricom PLC", "exchange": "NSE", "sector": "Telecommunications"},
        {"symbol": "NBK", "name": "NCBA Bank", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "KCB", "name": "KCB Group", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "EABL", "name": "East African Breweries", "exchange": "NSE", "sector": "Beverages"},
        {"symbol": "BAT", "name": "British American Tobacco Kenya", "exchange": "NSE", "sector": "Tobacco"},
        {"symbol": "ABSA", "name": "ABSA Bank Kenya", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "GLD", "name": "Gold Trust", "exchange": "NSE", "sector": "ETFs"},
        {"symbol": "COOP", "name": "Co-operative Bank", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "EQTY", "name": "Equity Group", "exchange": "NSE", "sector": "Banking"},
        {"symbol": "KLB", "name": "KCB Bank", "exchange": "NSE", "sector": "Banking"},
    ]
    
    # Apply filters
    if exchange:
        nse_stocks = [s for s in nse_stocks if s["exchange"].upper() == exchange.upper()]
    if sector:
        nse_stocks = [s for s in nse_stocks if s["sector"].lower() == sector.lower()]
    
    return {
        "stocks": stocks[:limit],
        "total": len(stocks[:limit]),
        "filters": {
            "exchange": exchange,
            "sector": sector
        }
    }


@router.get("/by-exchange/{exchange}")
async def get_stocks_by_exchange(
    exchange: str,
    limit: int = Query(default=100, le=200)
):
    """
    Get stocks listed on a specific exchange.
    
    Supported exchanges: NYSE, NASDAQ, AMEX
    """
    if exchange.upper() != "NSE":
        raise HTTPException(status_code=400, detail="NSE Kenya only")
    
    # Extended stock list with more companies per exchange
    stocks_by_exchange = {
        "NYSE": [
            {"symbol": "BRK.B", "name": "Berkshire Hathaway", "sector": "Financial"},
            {"symbol": "JPM", "name": "JPMorgan Chase", "sector": "Financial"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial"},
            {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer"},
            {"symbol": "UNH", "name": "UnitedHealth Group", "sector": "Healthcare"},
            {"symbol": "HD", "name": "Home Depot", "sector": "Consumer"},
            {"symbol": "MA", "name": "Mastercard", "sector": "Financial"},
            {"symbol": "DIS", "name": "Walt Disney", "sector": "Media"},
            {"symbol": "CRM", "name": "Salesforce", "sector": "Technology"},
            {"symbol": "TMO", "name": "Thermo Fisher", "sector": "Healthcare"},
            {"symbol": "ABBV", "name": "AbbVie", "sector": "Healthcare"},
            {"symbol": "ACN", "name": "Accenture", "sector": "Technology"},
            {"symbol": "CSCO", "name": "Cisco Systems", "sector": "Technology"},
            {"symbol": "ABT", "name": "Abbott Labs", "sector": "Healthcare"},
            {"symbol": "NKE", "name": "Nike Inc.", "sector": "Consumer"},
            {"symbol": "MCD", "name": "McDonald's", "sector": "Consumer"},
            {"symbol": "WMT", "name": "Walmart", "sector": "Consumer"},
            {"symbol": "BA", "name": "Boeing", "sector": "Industrial"},
            {"symbol": "CAT", "name": "Caterpillar", "sector": "Industrial"},
        ],
        "NASDAQ": [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon", "sector": "Consumer"},
            {"symbol": "META", "name": "Meta Platforms", "sector": "Media"},
            {"symbol": "NVDA", "name": "NVIDIA", "sector": "Technology"},
            {"symbol": "TSLA", "name": "Tesla", "sector": "Consumer"},
            {"symbol": "PYPL", "name": "PayPal", "sector": "Financial"},
            {"symbol": "ADBE", "name": "Adobe", "sector": "Technology"},
            {"symbol": "NFLX", "name": "Netflix", "sector": "Media"},
            {"symbol": "AMD", "name": "AMD", "sector": "Technology"},
            {"symbol": "INTC", "name": "Intel", "sector": "Technology"},
            {"symbol": "COST", "name": "Costco", "sector": "Consumer"},
            {"symbol": "AVGO", "name": "Broadcom", "sector": "Technology"},
            {"symbol": "PEP", "name": "PepsiCo", "sector": "Consumer"},
            {"symbol": "CMCSA", "name": "Comcast", "sector": "Media"},
            {"symbol": "CSCO", "name": "Cisco", "sector": "Technology"},
            {"symbol": "TXN", "name": "Texas Instruments", "sector": "Technology"},
            {"symbol": "AMAT", "name": "Applied Materials", "sector": "Technology"},
            {"symbol": "MU", "name": "Micron Tech", "sector": "Technology"},
        ],
        "AMEX": [
            {"symbol": "SPY", "name": "SPDR S&P 500 ETF", "sector": "ETF"},
            {"symbol": "QQQ", "name": "Invesco QQQ Trust", "sector": "ETF"},
            {"symbol": "IWM", "name": "iShares Russell 2000", "sector": "ETF"},
            {"symbol": "DIA", "name": "SPDR Dow Jones ETF", "sector": "ETF"},
            {"symbol": "XLF", "name": "Financial Select Sector", "sector": "ETF"},
            {"symbol": "XLK", "name": "Technology Select Sector", "sector": "ETF"},
            {"symbol": "XLE", "name": "Energy Select Sector", "sector": "ETF"},
            {"symbol": "XLV", "name": "Health Care Select", "sector": "ETF"},
            {"symbol": "ARGO", "name": "Argo Graphics", "sector": "Technology"},
            {"symbol": "BCS", "name": "Barclays Bank", "sector": "Financial"},
        ]
    }
    
    stocks = stocks_by_exchange.get(exchange.upper(), [])[:limit]
    
    # Generate mock price data
    import random
    stocks_with_prices = []
    for stock in stocks:
        base_price = random.randint(20, 500)
        stocks_with_prices.append({
            **stock,
            "price": round(base_price + random.random() * 50, 2),
            "change_percent": round((random.random() - 0.5) * 10, 2),
            "market_cap": random.randint(1000000000, 3000000000000)
        })
    
    return {
        "exchange": exchange.upper(),
        "total_stocks": len(stocks_with_prices),
        "stocks": stocks_with_prices
    }


@router.get("/search")
async def search_stocks(
    q: str = Query(..., min_length=1, max_length=10, description="Search query (symbol or company name)"),
    limit: int = Query(default=10, le=50)
):
    """
    Search stocks by symbol or company name.
    
    Returns matching stocks for autocomplete functionality.
    """
    import random
    
    # NSE Kenya searchable stocks
    nse_search_stocks = [
        {"symbol": "SCOM", "name": "Safaricom PLC", "exchange": "NSE"},
        {"symbol": "NBK", "name": "NCBA Bank", "exchange": "NSE"},
        {"symbol": "KCB", "name": "KCB Group", "exchange": "NSE"},
        {"symbol": "EABL", "name": "East African Breweries", "exchange": "NSE"},
        {"symbol": "BAT", "name": "BAT Kenya", "exchange": "NSE"},
        {"symbol": "ABSA", "name": "ABSA Bank Kenya", "exchange": "NSE"},
        {"symbol": "COOP", "name": "Co-operative Bank", "exchange": "NSE"},
        {"symbol": "EQTY", "name": "Equity Group", "exchange": "NSE"},
        {"symbol": "KLB", "name": "Kalanzi", "exchange": "NSE"},
        {"symbol": "NSE20", "name": "NSE 20 Index", "exchange": "NSE"},
    ]
    
    query_lower = q.lower()
    
    # Filter matching stocks
    matches = [
        stock for stock in all_stocks
        if stock["symbol"].lower().startswith(query_lower) or 
           stock["name"].lower().find(query_lower) != -1
    ][:limit]
    
    # Add mock price data
    results = []
    for stock in matches:
        base_price = random.randint(20, 500)
        results.append({
            **stock,
            "price": round(base_price + random.random() * 50, 2),
            "change_percent": round((random.random() - 0.5) * 10, 2)
        })
    
    return {
        "query": q,
        "total_results": len(results),
        "results": results
    }


# ============================================================================
# Fundamental Data Endpoints
# ============================================================================

@router.get("/fundamentals/{symbol}", response_model=List[FundamentalData])
async def get_fundamentals(
    symbol: str,
    period_type: str = Query(default="annual", regex="^(annual|quarterly)$"),
    limit: int = Query(default=10, le=20)
):
    """
    Get fundamental data for a stock.
    
    Returns financial metrics including P/E, dividend yield, ROE, etc.
    """
    import random
    
    fundamentals = []
    base_date = datetime.utcnow()
    
    for i in range(limit):
        period_end = base_date - timedelta(days=90 * i)
        
        fundamentals.append(FundamentalData(
            symbol=symbol.upper(),
            period_type=period_type,
            period_end=period_end,
            revenue=Decimal(str(100000 + random.randint(-50000, 100000))),
            net_income=Decimal(str(20000 + random.randint(-10000, 30000))),
            eps=Decimal(str(round(2.5 + random.random() * 2, 2))),
            pe_ratio=round(15 + random.random() * 20, 2),
            dividend_yield=round(random.random() * 3, 2),
            roe=round(10 + random.random() * 30, 2)
        ))
    
    return fundamentals


@router.get("/earnings/{symbol}", response_model=List[EarningsData])
async def get_earnings(
    symbol: str,
    limit: int = Query(default=8, le=12)
):
    """
    Get earnings data for a stock.
    
    Returns historical and upcoming earnings dates and EPS estimates.
    """
    import random
    
    earnings = []
    base_date = datetime.utcnow()
    
    for i in range(limit):
        quarter_num = 4 - (i % 4) if i % 4 != 0 else 4
        fiscal_year = base_date.year - (i // 4) - (1 if base_date.month < quarter_num * 3 else 0)
        
        eps_estimate = Decimal(str(round(1.0 + random.random() * 2, 2)))
        
        # Past quarters have actual EPS, future quarters don't
        is_past = i < 3
        
        earnings.append(EarningsData(
            symbol=symbol.upper(),
            quarter=f"Q{quarter_num}",
            fiscal_year=fiscal_year,
            eps_estimate=eps_estimate,
            eps_actual=Decimal(str(round(float(eps_estimate) + random.uniform(-0.5, 0.5), 2))) if is_past else None,
            revenue_estimate=Decimal(str(20000 + random.randint(-5000, 10000))),
            revenue_actual=Decimal(str(20000 + random.randint(-5000, 10000))) if is_past else None,
            report_date=base_date - timedelta(days=30 * i) if is_past else None,
            call_date=base_date - timedelta(days=28 * i) if is_past else None
        ))
    
    return earnings


@router.get("/ratios/{symbol}")
async def get_stock_ratios(symbol: str):
    """
    Get key financial ratios for a stock.
    
    Returns valuation, profitability, and liquidity ratios.
    """
    import random
    
    return {
        "symbol": symbol.upper(),
        "valuation": {
            "pe_ratio": round(15 + random.random() * 30, 2),
            "forward_pe": round(12 + random.random() * 25, 2),
            "peg_ratio": round(0.5 + random.random() * 2, 2),
            "price_to_book": round(1 + random.random() * 8, 2),
            "price_to_sales": round(1 + random.random() * 10, 2),
            "ev_to_ebitda": round(5 + random.random() * 20, 2)
        },
        "profitability": {
            "roe": round(10 + random.random() * 30, 2),
            "roa": round(2 + random.random() * 15, 2),
            "net_margin": round(5 + random.random() * 25, 2),
            "gross_margin": round(30 + random.random() * 40, 2),
            "operating_margin": round(10 + random.random() * 25, 2)
        },
        "liquidity": {
            "current_ratio": round(0.5 + random.random() * 3, 2),
            "quick_ratio": round(0.3 + random.random() * 2.5, 2),
            "cash_ratio": round(0.1 + random.random() * 1.5, 2)
        },
        "leverage": {
            "debt_to_equity": round(0 + random.random() * 200, 2),
            "debt_to_assets": round(0 + random.random() * 0.6, 2),
            "interest_coverage": round(5 + random.random() * 30, 2)
        },
        "dividends": {
            "dividend_yield": round(random.random() * 4, 2),
            "payout_ratio": round(20 + random.random() * 60, 2),
            "dividend_growth_5y": round(-5 + random.random() * 20, 2)
        },
        "growth": {
            "revenue_growth_5y": round(-5 + random.random() * 30, 2),
            "eps_growth_5y": round(-5 + random.random() * 30, 2),
            "eps_growth_next_5y": round(2 + random.random() * 20, 2)
        },
        "efficiency": {
            "asset_turnover": round(0.1 + random.random() * 0.8, 2),
            "inventory_turnover": round(2 + random.random() * 15, 2),
            "receivables_turnover": round(2 + random.random() * 20, 2)
        }
    }


# ============================================================================
# Stock Screener Endpoints
# ============================================================================

@router.post("/screener", response_model=List[StockScreenerResult])
async def stock_screener(request: StockScreenerRequest):
    """
    Screen stocks based on criteria.
    
    Returns stocks matching the specified financial criteria.
    """
    import random
    
    # Mock screener results
    results = []
    sectors = ["Technology", "Healthcare", "Financial Services", "Consumer Cyclical", "Industrials"]
    
    for i in range(30):
        pe = round(10 + random.random() * 40, 2)
        
        # Apply filters
        if request.min_pe and pe < request.min_pe:
            continue
        if request.max_pe and pe > request.max_pe:
            continue
        
        result = StockScreenerResult(
            symbol=f"STK{i}",
            name=f"Company {i}",
            sector=random.choice(sectors),
            market_cap=Decimal(str(1000000000 + random.randint(0, 2000000000000))),
            pe_ratio=pe,
            dividend_yield=round(random.random() * 5, 2),
            price=Decimal(str(50 + random.random() * 500)),
            change_percent=round(-10 + random.random() * 20, 2)
        )
        results.append(result)
    
    # Apply limit
    return results[:request.limit]


@router.get("/screener/presets")
async def get_screener_presets():
    """
    Get predefined stock screeners.
    
    Returns common screening criteria presets.
    """
    presets = [
        {
            "id": "high_growth",
            "name": "High Growth Stocks",
            "description": "Stocks with high revenue and earnings growth",
            "criteria": {
                "min_revenue_growth": 15,
                "min_eps_growth": 10,
                "min_roe": 15
            }
        },
        {
            "id": "dividend_ aristocrats",
            "name": "Dividend Aristocrats",
            "description": "Stocks with 25+ years of dividend increases",
            "criteria": {
                "min_dividend_yield": 2,
                "min_payout_ratio": 30,
                "max_payout_ratio": 75,
                "min_years_dividend_increase": 25
            }
        },
        {
            "id": "value_stocks",
            "name": "Undervalued Stocks",
            "description": "Stocks with low valuations relative to fundamentals",
            "criteria": {
                "max_pe": 15,
                "max_pb": 2,
                "min_pe_ratio": 0
            }
        },
        {
            "id": "quality_stocks",
            "name": "Quality Stocks",
            "description": "High quality companies with strong fundamentals",
            "criteria": {
                "min_roe": 15,
                "min_net_margin": 10,
                "max_debt_to_equity": 50
            }
        },
        {
            "id": "momentum_stocks",
            "name": "Momentum Stocks",
            "description": "Stocks with strong recent price momentum",
            "criteria": {
                "min_change_1m": 5,
                "min_change_3m": 10,
                "min_average_volume": 1000000
            }
        }
    ]
    
    return {"presets": presets}


# ============================================================================
# Sector/Industry Endpoints
# ============================================================================

@router.get("/sectors")
async def get_sectors():
    """
    Get list of available sectors.
    
    Returns all sectors with company counts and performance data.
    """
    import random
    
    sectors = [
        {"name": "Technology", "companies": 500, "avg_pe": 25.5, "ytd_return": 15.2},
        {"name": "Healthcare", "companies": 400, "avg_pe": 18.3, "ytd_return": 8.5},
        {"name": "Financial Services", "companies": 350, "avg_pe": 12.2, "ytd_return": 10.1},
        {"name": "Consumer Cyclical", "companies": 300, "avg_pe": 22.1, "ytd_return": 12.3},
        {"name": "Industrials", "companies": 280, "avg_pe": 16.8, "ytd_return": 9.8},
        {"name": "Energy", "companies": 120, "avg_pe": 10.5, "ytd_return": -5.2},
        {"name": "Utilities", "companies": 80, "avg_pe": 14.2, "ytd_return": 5.1},
        {"name": "Real Estate", "companies": 150, "avg_pe": 35.2, "ytd_return": 2.3},
        {"name": "Materials", "companies": 100, "avg_pe": 15.8, "ytd_return": 7.2},
        {"name": "Communication Services", "companies": 180, "avg_pe": 20.5, "ytd_return": 18.5}
    ]
    
    return {
        "sectors": sectors,
        "total_sectors": len(sectors),
        "total_companies": sum(s["companies"] for s in sectors)
    }


@router.get("/sectors/{sector_name}/performance")
async def get_sector_performance(sector_name: str):
    """
    Get sector performance data.
    
    Returns performance metrics for a specific sector.
    """
    import random
    
    return {
        "sector": sector_name,
        "periods": {
            "1d": {"return": round(-2 + random.random() * 4, 2), "volume": random.randint(1000000, 10000000)},
            "1w": {"return": round(-3 + random.random() * 6, 2), "volume": random.randint(5000000, 50000000)},
            "1m": {"return": round(-5 + random.random() * 15, 2), "volume": random.randint(20000000, 100000000)},
            "3m": {"return": round(-10 + random.random() * 25, 2), "volume": random.randint(50000000, 300000000)},
            "ytd": {"return": round(-5 + random.random() * 30, 2), "volume": random.randint(100000000, 500000000)},
            "1y": {"return": round(-15 + random.random() * 50, 2), "volume": random.randint(200000000, 1000000000)}
        },
        "top_gainers": [
            {"symbol": "GAIN1", "return": round(15 + random.random() * 20, 2)},
            {"symbol": "GAIN2", "return": round(12 + random.random() * 15, 2)},
            {"symbol": "GAIN3", "return": round(10 + random.random() * 12, 2)}
        ],
        "top_losers": [
            {"symbol": "LOSE1", "return": round(-20 + random.random() * 5, 2)},
            {"symbol": "LOSE2", "return": round(-15 + random.random() * 5, 2)},
            {"symbol": "LOSE3", "return": round(-12 + random.random() * 4, 2)}
        ],
        "most_active": [
            {"symbol": "VOL1", "volume": random.randint(50000000, 100000000)},
            {"symbol": "VOL2", "volume": random.randint(40000000, 80000000)},
            {"symbol": "VOL3", "volume": random.randint(30000000, 60000000)}
        ]
    }

