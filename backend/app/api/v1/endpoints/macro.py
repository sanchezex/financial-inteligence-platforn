"""
Financial Intelligence Platform - Macroeconomic Data Endpoints

API endpoints for macroeconomic data including GDP, inflation, interest rates, and economic events.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Models
# ============================================================================

class MacroIndicator(BaseModel):
    """Macroeconomic indicator model."""
    code: str
    name: str
    category: str
    country: str
    source: str
    frequency: str
    unit: Optional[str]


class MacroDataPoint(BaseModel):
    """Individual macroeconomic data point model."""
    indicator_code: str
    value: Optional[Decimal]
    previous_value: Optional[Decimal]
    change: Optional[Decimal]
    change_percent: Optional[float]
    forecast: Optional[Decimal]
    surprise: Optional[Decimal]
    period: str
    release_date: datetime


class CentralBankDecision(BaseModel):
    """Central bank decision model."""
    central_bank: str
    decision_date: datetime
    interest_rate: Optional[float]
    previous_rate: Optional[float]
    rate_change: Optional[float]
    policy_statement: Optional[str]
    forward_guidance: Optional[str]


class EconomicEvent(BaseModel):
    """Economic event model."""
    event_type: str
    event_name: str
    country: str
    scheduled_date: datetime
    importance: int
    previous_value: Optional[Decimal]
    forecast: Optional[Decimal]
    market_impact: str


class MacroCalendar(BaseModel):
    """Economic calendar model."""
    date: datetime
    events: List[EconomicEvent]
    total_events: int
    high_impact_count: int


# ============================================================================
# Indicator Endpoints
# ============================================================================

@router.get("/indicators")
async def get_macro_indicators(
    country: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(default=50, le=200)
):
    """
    Get list of macroeconomic indicators.
    
    Returns available indicators with their details.
    """
    # Mock data - in production, query database
    indicators = [
        {
            "code": "GDP",
            "name": "Gross Domestic Product",
            "category": "Growth",
            "country": "United States",
            "source": "Bureau of Economic Analysis",
            "frequency": "quarterly",
            "unit": "percent"
        },
        {
            "code": "CPI",
            "name": "Consumer Price Index",
            "category": "Inflation",
            "country": "United States",
            "source": "Bureau of Labor Statistics",
            "frequency": "monthly",
            "unit": "percent"
        },
        {
            "code": "PPI",
            "name": "Producer Price Index",
            "category": "Inflation",
            "country": "United States",
            "source": "Bureau of Labor Statistics",
            "frequency": "monthly",
            "unit": "percent"
        },
        {
            "code": "NFP",
            "name": "Non-Farm Payrolls",
            "category": "Employment",
            "country": "United States",
            "source": "Bureau of Labor Statistics",
            "frequency": "monthly",
            "unit": "thousands"
        },
        {
            "code": "UNRATE",
            "name": "Unemployment Rate",
            "category": "Employment",
            "country": "United States",
            "source": "Bureau of Labor Statistics",
            "frequency": "monthly",
            "unit": "percent"
        },
        {
            "code": "FEDRATE",
            "name": "Federal Funds Rate",
            "category": "Interest Rates",
            "country": "United States",
            "source": "Federal Reserve",
            "frequency": "daily",
            "unit": "percent"
        },
        {
            "code": "10Y",
            "name": "10-Year Treasury Yield",
            "category": "Interest Rates",
            "country": "United States",
            "source": "Federal Reserve",
            "frequency": "daily",
            "unit": "percent"
        },
        {
            "code": "RETAIL",
            "name": "Retail Sales",
            "category": "Consumption",
            "country": "United States",
            "source": "Census Bureau",
            "frequency": "monthly",
            "unit": "percent"
        },
        {
            "code": "PMI_MFG",
            "name": "Manufacturing PMI",
            "category": "Manufacturing",
            "country": "United States",
            "source": "ISM",
            "frequency": "monthly",
            "unit": "index"
        },
        {
            "code": "CONFC",
            "name": "Consumer Confidence Index",
            "category": "Sentiment",
            "country": "United States",
            "source": "Conference Board",
            "frequency": "monthly",
            "unit": "index"
        }
    ]
    
    # Apply filters
    if country:
        indicators = [i for i in indicators if i["country"].lower() == country.lower()]
    if category:
        indicators = [i for i in indicators if i["category"].lower() == category.lower()]
    
    return {
        "indicators": indicators[:limit],
        "total": len(indicators[:limit])
    }


@router.get("/indicators/{indicator_code}", response_model=List[MacroDataPoint])
async def get_indicator_data(
    indicator_code: str,
    country: str = Query(default="United States"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(default=20, le=100)
):
    """
    Get historical data for a macroeconomic indicator.
    
    Returns time series data for the specified indicator.
    """
    import random
    
    data_points = []
    end = end_date or datetime.utcnow()
    start = start_date or (end - timedelta(days=365 * limit // 12))
    
    current_date = start
    
    while current_date <= end and len(data_points) < limit:
        # Skip certain dates based on frequency
        if current_date.month in [1, 4, 7, 10] or indicator_code in ["GDP"]:
            if indicator_code in ["GDP"]:
                current_date = end - timedelta(days=365 * (limit - len(data_points) - 1))
            
            base_value = {
                "GDP": 2.5,
                "CPI": 3.0,
                "PPI": 1.5,
                "NFP": 200,
                "UNRATE": 4.0,
                "FEDRATE": 5.25,
                "10Y": 4.5,
                "RETAIL": 0.3,
                "PMI_MFG": 50,
                "CONFC": 100
            }.get(indicator_code, 0)
            
            value = Decimal(str(round(base_value + random.uniform(-1, 1), 2)))
            previous_value = Decimal(str(round(base_value + random.uniform(-1.5, 1.5), 2)))
            forecast = Decimal(str(round(base_value + random.uniform(-0.5, 0.5), 2)))
            
            data_points.append(MacroDataPoint(
                indicator_code=indicator_code,
                value=value,
                previous_value=previous_value,
                change=value - previous_value,
                change_percent=round(float((value - previous_value) / previous_value * 100), 2) if previous_value else None,
                forecast=forecast,
                surprise=value - forecast if forecast else None,
                period=current_date.strftime("%Y-%m") if indicator_code not in ["GDP"] else f"{current_date.year}-Q{(current_date.month - 1) // 3 + 1}",
                release_date=current_date + timedelta(days=random.randint(1, 30))
            ))
        
        # Increment based on indicator frequency
        if indicator_code == "GDP":
            current_date = current_date + timedelta(days=90)
        else:
            current_date = current_date + timedelta(days=30)
    
    return data_points


# ============================================================================
# Central Bank Endpoints
# ============================================================================

@router.get("/central-banks")
async def get_central_bank_decisions(
    central_bank: Optional[str] = None,
    limit: int = Query(default=20, le=50)
):
    """
    Get central bank interest rate decisions.
    
    Returns historical and upcoming central bank decisions.
    """
    import random
    
    decisions = []
    banks = central_bank.split(",") if central_bank else [
        "Federal Reserve", "European Central Bank", "Bank of England", 
        "Bank of Japan", "Swiss National Bank", "Bank of Canada"
    ]
    
    base_date = datetime.utcnow()
    
    for bank in banks:
        for i in range(limit // len(banks) + 1):
            decision_date = base_date - timedelta(days=45 * i)
            
            rate = {
                "Federal Reserve": 5.25,
                "European Central Bank": 4.00,
                "Bank of England": 5.25,
                "Bank of Japan": 0.10,
                "Swiss National Bank": 1.75,
                "Bank of Canada": 5.00
            }.get(bank, 2.5)
            
            rate_change = random.choice([0, 0.25, -0.25, 0.5, -0.5])
            new_rate = rate + rate_change
            
            decisions.append(CentralBankDecision(
                central_bank=bank,
                decision_date=decision_date,
                interest_rate=new_rate,
                previous_rate=rate,
                rate_change=rate_change,
                policy_statement="The committee decided to maintain the policy rate. Inflation remains elevated but is moderating towards target." if rate_change == 0 else f"The committee decided to {'raise' if rate_change > 0 else 'lower'} the policy rate by {abs(rate_change)}%.",
                forward_guidance="The committee will continue to monitor economic conditions and adjust policy as appropriate."
            ))
    
    return sorted(decisions, key=lambda x: x.decision_date, reverse=True)[:limit]


@router.get("/central-banks/{bank}/rates")
async def get_central_bank_rates(bank: str):
    """
    Get current central bank rates and rate history.
    
    Returns current rates and historical rate decisions.
    """
    import random
    
    current_rates = {
        "Federal Reserve": {"rate": 5.25, "since": "2023-12", "next_meeting": "2024-03"},
        "European Central Bank": {"rate": 4.00, "since": "2023-10", "next_meeting": "2024-03"},
        "Bank of England": {"rate": 5.25, "since": "2023-12", "next_meeting": "2024-03"},
        "Bank of Japan": {"rate": 0.10, "since": "2024-01", "next_meeting": "2024-04"},
        "Swiss National Bank": {"rate": 1.75, "since": "2023-12", "next_meeting": "2024-03"},
        "Bank of Canada": {"rate": 5.00, "since": "2023-12", "next_meeting": "2024-04"}
    }
    
    info = current_rates.get(bank)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Central bank not found: {bank}")
    
    # Generate rate history
    history = []
    rate = info["rate"]
    for i in range(12):
        history.append({
            "date": datetime.utcnow() - timedelta(days=30 * i),
            "rate": rate,
            "change": 0
        })
        rate = max(rate + random.choice([-0.25, 0, 0.25]), 0)
    
    return {
        "bank": bank,
        "current_rate": info["rate"],
        "rate_since": info["since"],
        "next_meeting": info["next_meeting"],
        "history": history
    }


# ============================================================================
# Economic Calendar Endpoints
# ============================================================================

@router.get("/calendar", response_model=List[EconomicEvent])
async def get_economic_calendar(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    countries: Optional[str] = None,
    importance: Optional[int] = Query(None, ge=1, le=3),
    limit: int = Query(default=50, le=200)
):
    """
    Get economic calendar for upcoming events.
    
    Returns scheduled economic announcements and data releases.
    """
    import random
    
    start = start_date or datetime.utcnow()
    end = end_date or (start + timedelta(days=30))
    
    events = []
    
    event_templates = [
        {"type": "employment", "name": "Non-Farm Payrolls", "importance": 3},
        {"type": "inflation", "name": "CPI Release", "importance": 3},
        {"type": "gdp", "name": "GDP Growth Rate", "importance": 2},
        {"type": "retail", "name": "Retail Sales", "importance": 2},
        {"type": "manufacturing", "name": "Manufacturing PMI", "importance": 2},
        {"type": "consumer", "name": "Consumer Confidence", "importance": 1},
        {"type": "housing", "name": "Housing Starts", "importance": 1},
        {"type": "trade", "name": "Trade Balance", "importance": 1},
        {"type": "productivity", "name": "Productivity Data", "importance": 1},
        {"type": "jobless", "name": "Jobless Claims", "importance": 2}
    ]
    
    country_list = countries.split(",") if countries else ["United States", "Euro Area", "United Kingdom"]
    
    current_date = start
    while current_date <= end and len(events) < limit:
        # Skip weekends
        if current_date.weekday() < 5:
            # Select random events for this day
            num_events = random.randint(1, 3)
            for _ in range(num_events):
                template = random.choice(event_templates)
                
                if importance and template["importance"] != importance:
                    continue
                
                country = random.choice(country_list)
                
                events.append(EconomicEvent(
                    event_type=template["type"],
                    event_name=template["name"],
                    country=country,
                    scheduled_date=current_date.replace(hour=8, minute=30) if country == "United States" else current_date.replace(hour=2, minute=0),
                    importance=template["importance"],
                    previous_value=Decimal(str(round(random.uniform(150, 300), 0))),
                    forecast=Decimal(str(round(random.uniform(150, 300), 0))),
                    market_impact=["low", "medium", "high"][template["importance"] - 1]
                ))
        
        current_date += timedelta(days=1)
    
    return sorted(events, key=lambda x: x.scheduled_date)[:limit]


@router.get("/calendar/today")
async def get_today_events():
    """
    Get today's economic events.
    
    Returns all scheduled economic events for today.
    """
    today = datetime.utcnow().date()
    return await get_economic_calendar(
        start_date=datetime.combine(today, datetime.min.time()),
        end_date=datetime.combine(today, datetime.max.time())
    )


@router.get("/calendar/this-week")
async def get_this_week_events():
    """
    Get this week's economic events.
    
    Returns all scheduled economic events for the current week.
    """
    today = datetime.utcnow()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    return await get_economic_calendar(
        start_date=week_start,
        end_date=week_end
    )


# ============================================================================
# Macro Analysis Endpoints
# ============================================================================

@router.get("/analysis/sentiment")
async def get_macro_sentiment():
    """
    Get macroeconomic sentiment analysis.
    
    Returns aggregated sentiment from economic data and news.
    """
    import random
    
    return {
        "timestamp": datetime.utcnow(),
        "overall_sentiment": random.choice(["bullish", "neutral", "bearish"]),
        "sentiment_score": round(random.uniform(-1, 1), 2),
        "factors": {
            "growth": {
                "sentiment": random.choice(["bullish", "neutral", "bearish"]),
                "score": round(random.uniform(-1, 1), 2),
                "drivers": ["GDP growth", "Manufacturing data", "Consumer spending"]
            },
            "inflation": {
                "sentiment": random.choice(["bullish", "neutral", "bearish"]),
                "score": round(random.uniform(-1, 1), 2),
                "drivers": ["CPI trend", "PPI data", "Commodity prices"]
            },
            "monetary_policy": {
                "sentiment": random.choice(["bullish", "neutral", "bearish"]),
                "score": round(random.uniform(-1, 1), 2),
                "drivers": ["Fed comments", "Rate expectations", "Central bank actions"]
            },
            "employment": {
                "sentiment": random.choice(["bullish", "neutral", "bearish"]),
                "score": round(random.uniform(-1, 1), 2),
                "drivers": ["Job creation", "Wage growth", "Unemployment rate"]
            }
        },
        "outlook": {
            "short_term": random.choice(["positive", "neutral", "cautious"]),
            "medium_term": random.choice(["positive", "neutral", "cautious"]),
            "long_term": random.choice(["positive", "neutral", "cautious"])
        }
    }


@router.get("/analysis/correlations")
async def get_macro_correlations(
    indicator1: str,
    indicator2: str
):
    """
    Get correlation between two macroeconomic indicators.
    
    Returns statistical correlation and historical relationship.
    """
    import random
    
    return {
        "indicator1": indicator1,
        "indicator2": indicator2,
        "correlation": round(random.uniform(-1, 1), 3),
        "correlation_p_value": round(random.uniform(0, 0.1), 4),
        "relationship": random.choice(["positive", "negative", "none"]),
        "strength": random.choice(["strong", "moderate", "weak"]),
        "historical_period": {
            "start": "2019-01-01",
            "end": datetime.utcnow().strftime("%Y-%m-%d")
        },
        "observations": [
            "Strong positive correlation observed in 2020-2022",
            "Correlation weakened during 2023",
            "Recent data suggests decoupling"
        ]
    }


@router.get("/analysis/regime")
async def get_macro_regime():
    """
    Get current macroeconomic regime analysis.
    
    Identifies current economic regime based on multiple indicators.
    """
    import random
    
    regimes = ["expansion", "peak", "contraction", "trough"]
    
    return {
        "timestamp": datetime.utcnow(),
        "current_regime": random.choice(regimes),
        "regime_probability": {
            "expansion": round(random.uniform(0, 0.4), 2),
            "peak": round(random.uniform(0, 0.3), 2),
            "contraction": round(random.uniform(0, 0.3), 2),
            "trough": round(random.uniform(0, 0.2), 2)
        },
        "indicators": {
            "gdp_growth": {"value": round(random.uniform(1, 4), 1), "status": "above_trend"},
            "unemployment": {"value": round(random.uniform(3, 6), 1), "status": "low"},
            "inflation": {"value": round(random.uniform(2, 6), 1), "status": "elevated"},
            "interest_rates": {"value": round(random.uniform(4, 6), 1), "status": "restrictive"}
        },
        "transition_probabilities": {
            "to_expansion": round(random.uniform(0, 0.2), 2),
            "to_peak": round(random.uniform(0, 0.3), 2),
            "to_contraction": round(random.uniform(0, 0.3), 2),
            "to_trough": round(random.uniform(0, 0.1), 2)
        },
        "key_metrics": {
            "yield_curve_10y2y": round(random.uniform(-0.5, 0.5), 2),
            "credit_spreads": round(random.uniform(100, 300), 0),
            "vix": round(random.uniform(10, 30), 1),
            "leading_indicator": round(random.uniform(95, 110), 1)
        }
    }

