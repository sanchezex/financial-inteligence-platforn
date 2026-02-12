#!/usr/bin/env python3
"""
Financial Intelligence Platform - API Demo

This script demonstrates the API operations and expected outputs
without requiring Docker or external dependencies.
"""

import json
from datetime import datetime, timedelta
from decimal import Decimal
import random


class FinancialPlatformDemo:
    """
    Demo class to showcase the Financial Intelligence Platform API.
    """
    
    def __init__(self):
        self.symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM"]
        self.sectors = ["Technology", "Healthcare", "Financial", "Energy", "Consumer"]
    
    def demo_health_check(self):
        """Demo: Health check endpoint"""
        print("\n" + "="*60)
        print("🏥 API ENDPOINT: GET /health")
        print("="*60)
        print("""
Response:
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0.0",
    "uptime_seconds": 86400.5,
    "services": {
        "api": {"status": "healthy", "latency_ms": 5},
        "database": {"status": "healthy", "latency_ms": 12},
        "cache": {"status": "healthy", "latency_ms": 2},
        "streaming": {"status": "healthy", "latency_ms": 8}
    }
}
        """)
    
    def demo_market_quotes(self):
        """Demo: Market quotes endpoint"""
        print("\n" + "="*60)
        print("📈 API ENDPOINT: GET /api/v1/market/quotes/{symbol}")
        print("="*60)
        print(f"\nRequest: GET /api/v1/market/quotes/AAPL")
        print("\nResponse:")
        print(json.dumps({
            "symbol": "AAPL",
            "asset_type": "stock",
            "exchange": "NASDAQ",
            "price": Decimal("185.50"),
            "change": Decimal("2.35"),
            "change_percent": 1.28,
            "volume": 52000000,
            "bid": Decimal("185.48"),
            "ask": Decimal("185.52"),
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "realtime_feed"
        }, indent=2, default=str))
    
    def demo_batch_quotes(self):
        """Demo: Batch quotes endpoint"""
        print("\n" + "="*60)
        print("📊 API ENDPOINT: POST /api/v1/market/quotes")
        print("="*60)
        print("\nRequest Body:")
        print(json.dumps({
            "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"],
            "asset_type": "stock"
        }, indent=2))
        print("\nResponse:")
        quotes = []
        for symbol in ["AAPL", "MSFT", "GOOGL", "NVDA"]:
            price = 100 + random.random() * 400
            quotes.append({
                "symbol": symbol,
                "asset_type": "stock",
                "exchange": "NASDAQ",
                "price": round(Decimal(str(price)), 2),
                "change": round(Decimal(str((random.random()-0.5)*10)), 2),
                "change_percent": round((random.random()-0.5)*5, 2),
                "volume": random.randint(10000000, 50000000),
                "timestamp": datetime.utcnow().isoformat(),
                "data_source": "realtime_feed"
            })
        print(json.dumps(quotes, indent=2, default=str))
    
    def demo_historical_data(self):
        """Demo: Historical data endpoint"""
        print("\n" + "="*60)
        print("📉 API ENDPOINT: GET /api/v1/market/historical/{symbol}")
        print("="*60)
        print("\nRequest: GET /api/v1/market/historical/AAPL?period=daily&limit=5")
        print("\nResponse:")
        data = {
            "symbol": "AAPL",
            "asset_type": "stock",
            "period": "daily",
            "data": []
        }
        base_date = datetime.utcnow()
        base_price = 180.0
        for i in range(5):
            price_change = (random.random() - 0.5) * 10
            data["data"].append({
                "timestamp": (base_date - timedelta(days=i+1)).isoformat(),
                "open": round(base_price - random.random() * 5, 2),
                "high": round(base_price + random.random() * 5, 2),
                "low": round(base_price - random.random() * 5, 2),
                "close": round(base_price, 2),
                "volume": random.randint(10000000, 50000000),
                "vwap": round(base_price, 2)
            })
            base_price += price_change
        print(json.dumps(data, indent=2, default=str))
    
    def demo_market_summary(self):
        """Demo: Market summary endpoint"""
        print("\n" + "="*60)
        print("🌐 API ENDPOINT: GET /api/v1/market/summary")
        print("="*60)
        print("\nResponse:")
        indices = [
            {"symbol": "SPX", "name": "S&P 500", "value": 4783.45, "change": 0.85},
            {"symbol": "DJI", "name": "Dow Jones", "value": 37468.61, "change": 0.42},
            {"symbol": "IXIC", "name": "NASDAQ", "value": 15055.65, "change": 1.23},
            {"symbol": "RUT", "name": "Russell 2000", "value": 2012.34, "change": -0.56}
        ]
        print(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "indices": indices,
            "market_status": "open",
            "trading_hours": {
                "US": {"pre_market": "04:00-09:30", "regular": "09:30-16:00", "after_hours": "16:00-20:00"}
            }
        }, indent=2))
    
    def demo_stock_info(self):
        """Demo: Stock info endpoint"""
        print("\n" + "="*60)
        print("🏢 API ENDPOINT: GET /api/v1/stocks/info/{symbol}")
        print("="*60)
        print("\nRequest: GET /api/v1/stocks/info/AAPL")
        print("\nResponse:")
        print(json.dumps({
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Consumer Electronics",
            "country": "United States",
            "currency": "USD",
            "market_cap": Decimal("2800000000000"),
            "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
            "website": "https://www.apple.com"
        }, indent=2, default=str))
    
    def demo_fundamentals(self):
        """Demo: Fundamentals endpoint"""
        print("\n" + "="*60)
        print("📋 API ENDPOINT: GET /api/v1/stocks/fundamentals/{symbol}")
        print("="*60)
        print("\nRequest: GET /api/v1/stocks/fundamentals/AAPL?period_type=quarterly&limit=4")
        print("\nResponse:")
        fundamentals = []
        for i in range(4):
            fundamentals.append({
                "symbol": "AAPL",
                "period_type": "quarterly",
                "period_end": (datetime.utcnow() - timedelta(days=90*i)).strftime("%Y-%m-%d"),
                "revenue": round(Decimal(str(random.randint(80000, 120000))), 2),
                "net_income": round(Decimal(str(random.randint(18000, 30000))), 2),
                "eps": round(Decimal(str(random.uniform(1.2, 2.0))), 2),
                "pe_ratio": round(random.uniform(20, 35), 2),
                "dividend_yield": round(random.uniform(0.3, 0.6), 2),
                "roe": round(random.uniform(120, 180), 2)
            })
        print(json.dumps(fundamentals, indent=2, default=str))
    
    def demo_economic_calendar(self):
        """Demo: Economic calendar endpoint"""
        print("\n" + "="*60)
        print("📅 API ENDPOINT: GET /api/v1/macro/calendar")
        print("="*60)
        print("\nRequest: GET /api/v1/macro/calendar?days=7")
        print("\nResponse:")
        events = []
        for i in range(7):
            events.append({
                "event_type": random.choice(["employment", "inflation", "gdp", "retail"]),
                "event_name": random.choice(["Non-Farm Payrolls", "CPI Release", "GDP Growth Rate", "Retail Sales"]),
                "country": "United States",
                "scheduled_date": (datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "importance": random.randint(1, 3),
                "previous_value": round(Decimal(str(random.uniform(150, 300))), 0),
                "forecast": round(Decimal(str(random.uniform(150, 300))), 0),
                "market_impact": random.choice(["high", "medium", "low"])
            })
        print(json.dumps({
            "events": events,
            "total_events": len(events),
            "high_impact_count": len([e for e in events if e["importance"] == 3])
        }, indent=2, default=str))
    
    def demo_freight_rates(self):
        """Demo: Freight rates endpoint"""
        print("\n" + "="*60)
        print("🚢 API ENDPOINT: GET /api/v1/shipping/freight-rates")
        print("="*60)
        print("\nResponse:")
        routes = [
            {"route_code": "SHA-LAX", "origin": "Shanghai", "destination": "Los Angeles"},
            {"route_code": "SIN-ROT", "origin": "Singapore", "destination": "Rotterdam"},
            {"route_code": "BUS-LA", "origin": "Busan", "destination": "Los Angeles"}
        ]
        rates = []
        for route in routes:
            spot = 1000 + random.random() * 2000
            rates.append({
                "route_code": route["route_code"],
                "origin": route["origin"],
                "destination": route["destination"],
                "spot_rate": round(Decimal(str(spot)), 2),
                "contract_rate": round(Decimal(str(spot * 0.85)), 2),
                "change_percent": round(random.uniform(-15, 15), 2),
                "timestamp": datetime.utcnow().isoformat()
            })
        print(json.dumps(rates, indent=2, default=str))
    
    def demo_news_feed(self):
        """Demo: News feed endpoint"""
        print("\n" + "="*60)
        print("📰 API ENDPOINT: GET /api/v1/news/feed")
        print("="*60)
        print("\nRequest: GET /api/v1/news/feed?limit=3")
        print("\nResponse:")
        articles = []
        for i in range(3):
            articles.append({
                "id": f"article_{i+1}",
                "title": f"Market Update: {random.choice(['Tech', 'Finance', 'Energy'])} sector sees significant movement",
                "summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Market analysis reveals important trends.",
                "source": random.choice(["Reuters", "Bloomberg", "CNBC"]),
                "categories": ["Markets", "Economy"],
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "sentiment_score": round(random.uniform(-0.5, 0.5), 2),
                "mentioned_tickers": random.sample(["AAPL", "MSFT", "GOOGL", "AMZN"], k=2),
                "published_at": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            })
        print(json.dumps({
            "articles": articles,
            "total_count": 150,
            "page": 1,
            "page_size": 3,
            "has_more": True
        }, indent=2))
    
    def demo_sentiment_analysis(self):
        """Demo: Sentiment analysis endpoint"""
        print("\n" + "="*60)
        print("🤖 API ENDPOINT: GET /api/v1/news/sentiment/{symbol}")
        print("="*60)
        print("\nRequest: GET /api/v1/news/sentiment/AAPL?days=7")
        print("\nResponse:")
        print(json.dumps({
            "symbol": "AAPL",
            "period": "Last 7 days",
            "timestamp": datetime.utcnow().isoformat(),
            "overall_sentiment": "bullish",
            "sentiment_score": round(random.uniform(0.2, 0.6), 2),
            "components": {
                "news_sentiment": {"score": 0.45, "articles_analyzed": 85},
                "social_sentiment": {"score": 0.52, "posts_analyzed": 2500}
            },
            "sentiment_history": [
                {"date": "2024-01-15", "score": 0.45, "volume": 35},
                {"date": "2024-01-14", "score": 0.38, "volume": 42},
                {"date": "2024-01-13", "score": 0.52, "volume": 28}
            ]
        }, indent=2))
    
    def demo_correlation_analysis(self):
        """Demo: Correlation analysis endpoint"""
        print("\n" + "="*60)
        print("🔗 API ENDPOINT: GET /api/v1/analytics/correlations/{s1}/{s2}")
        print("="*60)
        print("\nRequest: GET /api/v1/analytics/correlations/AAPL/MSFT?period=daily")
        print("\nResponse:")
        print(json.dumps({
            "symbol1": "AAPL",
            "symbol2": "MSFT",
            "correlation": round(random.uniform(0.6, 0.9), 4),
            "correlation_squared": round(random.uniform(0.36, 0.81), 4),
            "p_value": 0.0001,
            "period": "daily",
            "lookback_days": 252,
            "statistics": {
                "observations": 252,
                "mean_AAPL": 175.50,
                "mean_MSFT": 375.25,
                "std_AAPL": 15.2,
                "std_MSFT": 28.5
            }
        }, indent=2))
    
    def demo_risk_metrics(self):
        """Demo: Risk metrics endpoint"""
        print("\n" + "="*60)
        print("⚠️ API ENDPOINT: GET /api/v1/analytics/risk/{symbol}")
        print("="*60)
        print("\nRequest: GET /api/v1/analytics/risk/AAPL")
        print("\nResponse:")
        print(json.dumps({
            "symbol": "AAPL",
            "volatility": round(random.uniform(20, 35), 2),
            "beta": round(random.uniform(0.8, 1.3), 2),
            "sharpe_ratio": round(random.uniform(0.5, 1.5), 2),
            "max_drawdown": round(random.uniform(-25, -10), 2),
            "var_95": round(random.uniform(-3, -1.5), 2),
            "var_99": round(random.uniform(-5, -2.5), 2),
            "correlation_benchmark": round(random.uniform(0.9, 1.0), 2)
        }, indent=2))
    
    def demo_ai_insights(self):
        """Demo: AI insights endpoint"""
        print("\n" + "="*60)
        print("💡 API ENDPOINT: POST /api/v1/ai/insights/generate")
        print("="*60)
        print("\nRequest Body:")
        print(json.dumps({
            "symbol": "AAPL",
            "insight_type": "comprehensive"
        }, indent=2))
        print("\nResponse:")
        print(json.dumps({
            "insight_type": "comprehensive",
            "title": "Comprehensive Analysis: AAPL",
            "description": "AI analysis reveals multiple factors influencing AAPL with a mixed outlook.",
            "confidence": round(random.uniform(0.8, 0.95), 4),
            "supporting_data": [
                {"metric": "Technical Score", "value": 65, "direction": "neutral"},
                {"metric": "Fundamental Score", "value": 78, "direction": "positive"},
                {"metric": "Sentiment Score", "value": 55, "direction": "neutral"}
            ]
        }, indent=2))
    
    def demo_sentiment_nlp(self):
        """Demo: NLP sentiment analysis"""
        print("\n" + "="*60)
        print("🧠 API ENDPOINT: POST /api/v1/ai/sentiment/analyze")
        print("="*60)
        print("\nRequest Body:")
        print(json.dumps({
            "text": "Apple reports record quarterly earnings, driven by strong iPhone sales and services growth. Analysts remain bullish on the stock."
        }, indent=2))
        print("\nResponse:")
        print(json.dumps({
            "sentiment": "positive",
            "sentiment_score": round(random.uniform(0.5, 0.9), 4),
            "confidence": round(random.uniform(0.85, 0.99), 4),
            "aspects": [
                {"aspect": "overall", "sentiment": "positive", "score": 0.75},
                {"aspect": "price", "sentiment": "positive", "score": 0.68},
                {"aspect": "growth", "sentiment": "positive", "score": 0.82}
            ],
            "emotions": {
                "joy": 0.35,
                "fear": 0.05,
                "anger": 0.02,
                "sadness": 0.03,
                "surprise": 0.15
            }
        }, indent=2))
    
    def demo_create_alert(self):
        """Demo: Create alert endpoint"""
        print("\n" + "="*60)
        print("🔔 API ENDPOINT: POST /api/v1/alerts/")
        print("="*60)
        print("\nRequest Body:")
        print(json.dumps({
            "name": "AAPL Price Alert",
            "description": "Alert when AAPL crosses $200",
            "alert_type": "price",
            "conditions": [
                {"field": "price", "operator": "cross_above", "value": 200}
            ],
            "condition_logic": "AND",
            "symbols": ["AAPL"],
            "asset_types": ["stock"],
            "enabled": True,
            "notifications": [
                {"channel": "push", "settings": {}}
            ]
        }, indent=2))
        print("\nResponse:")
        print(json.dumps({
            "id": "alert_abc123",
            "user_id": "user_123",
            "name": "AAPL Price Alert",
            "status": "active",
            "trigger_count": 0,
            "created_at": datetime.utcnow().isoformat()
        }, indent=2))
    
    def demo_watchlist(self):
        """Demo: Watchlist with data endpoint"""
        print("\n" + "="*60)
        print("⭐ API ENDPOINT: GET /api/v1/watchlists/{id}/data")
        print("="*60)
        print("\nResponse:")
        items = []
        for symbol in ["AAPL", "MSFT", "GOOGL", "NVDA"]:
            price = 100 + random.random() * 400
            change = (random.random() - 0.5) * 10
            items.append({
                "symbol": symbol,
                "name": f"{symbol} Inc.",
                "price": round(Decimal(str(price)), 2),
                "change": round(Decimal(str(change)), 2),
                "change_percent": round(change/price*100, 2),
                "volume": random.randint(1000000, 50000000),
                "market_cap": f"${round(100 + random.random() * 2000)}B",
                "pe_ratio": round(random.uniform(15, 50), 1)
            })
        print(json.dumps({
            "id": "watchlist_xyz789",
            "name": "Tech Stocks",
            "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"],
            "items": items
        }, indent=2, default=str))
    
    def run_all_demos(self):
        """Run all demo operations"""
        print("\n" + "="*70)
        print("🏦 FINANCIAL INTELLIGENCE PLATFORM - API DEMONSTRATION")
        print("="*70)
        print("Bloomberg-Level Real-Time Market Intelligence Platform")
        print("-"*70)
        
        self.demo_health_check()
        self.demo_market_quotes()
        self.demo_batch_quotes()
        self.demo_historical_data()
        self.demo_market_summary()
        self.demo_stock_info()
        self.demo_fundamentals()
        self.demo_economic_calendar()
        self.demo_freight_rates()
        self.demo_news_feed()
        self.demo_sentiment_analysis()
        self.demo_correlation_analysis()
        self.demo_risk_metrics()
        self.demo_ai_insights()
        self.demo_sentiment_nlp()
        self.demo_create_alert()
        self.demo_watchlist()
        
        print("\n" + "="*70)
        print("✅ DEMO COMPLETE")
        print("="*70)
        print("""
To run the actual platform:
1. Install Docker: https://docs.docker.com/get-docker/
2. Navigate to project: cd /home/sanchez/sanchezProjects/future
3. Start services: docker-compose up -d
4. Access API: http://localhost:8000
5. View docs: http://localhost:8000/docs
        """)


if __name__ == "__main__":
    demo = FinancialPlatformDemo()
    demo.run_all_demos()

