#!/usr/bin/env python3
"""
Financial Intelligence Platform - Standalone Server

A simplified version that can run without Docker dependencies.
Serves the frontend and provides demo API endpoints.
"""

import http.server
import socketserver
import json
import threading
from datetime import datetime, timedelta
from decimal import Decimal
import random
import os


class FinancialAPIHandler(http.server.BaseHTTPRequestHandler):
    """Handler for Financial Platform API requests."""
    
    def log_message(self, format, *args):
        """Custom logging."""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {args[0]}")
    
    def send_json_response(self, status_code, data):
        """Send a JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def do_GET(self):
        """Handle GET requests."""
        path = self.path.split('?')[0]
        
        if path == '/' or path == '/index.html':
            self.serve_frontend()
        elif path == '/health':
            self.handle_health()
        elif path == '/api/v1':
            self.handle_api_info()
        elif path == '/api/v1/market/quotes':
            self.handle_quotes()
        elif path == '/api/v1/market/summary':
            self.handle_market_summary()
        elif path == '/api/v1/stocks/info/AAPL':
            self.handle_stock_info()
        elif path == '/api/v1/news/feed':
            self.handle_news()
        elif path == '/api/v1/analytics/risk/AAPL':
            self.handle_risk()
        elif path == '/api/v1/ai/sentiment':
            self.handle_sentiment()
        elif path == '/api/v1/watchlists':
            self.handle_watchlists()
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def do_POST(self):
        """Handle POST requests."""
        path = self.path.split('?')[0]
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else '{}'
        
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}
        
        if path == '/api/v1/ai/sentiment/analyze':
            self.handle_sentiment_analyze(data)
        elif path == '/api/v1/alerts':
            self.handle_create_alert(data)
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def serve_frontend(self):
        """Serve the frontend HTML."""
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Intelligence Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; color: #fff; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        header { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 20px; border-radius: 15px; margin-bottom: 30px; }
        header h1 { font-size: 2.5em; background: linear-gradient(90deg, #00d4ff, #7b2cbf); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .card h3 { color: #00d4ff; margin-bottom: 15px; font-size: 1.3em; }
        .price { font-size: 2.5em; font-weight: bold; color: #4ade80; }
        .change { font-size: 1.2em; margin-top: 10px; }
        .positive { color: #4ade80; }
        .negative { color: #f87171; }
        .btn { background: linear-gradient(90deg, #00d4ff, #7b2cbf); border: none; padding: 12px 25px; border-radius: 8px; color: white; cursor: pointer; font-size: 1em; margin-top: 15px; transition: opacity 0.3s; }
        .btn:hover { opacity: 0.9; }
        .nav { display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap; }
        .nav-item { background: rgba(255,255,255,0.1); padding: 10px 20px; border-radius: 8px; cursor: pointer; transition: background 0.3s; }
        .nav-item:hover { background: rgba(255,255,255,0.2); }
        .nav-item.active { background: linear-gradient(90deg, #00d4ff, #7b2cbf); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin-top: 20px; }
        .stat { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 1.8em; font-weight: bold; color: #00d4ff; }
        .stat-label { font-size: 0.9em; color: #94a3b8; margin-top: 5px; }
        .chart { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; margin-top: 20px; }
        .news-item { border-left: 3px solid #00d4ff; padding-left: 15px; margin-bottom: 15px; }
        .news-title { font-weight: bold; margin-bottom: 5px; }
        .news-source { font-size: 0.85em; color: #94a3b8; }
        .health-status { display: flex; gap: 15px; margin-top: 15px; }
        .health-item { padding: 8px 15px; border-radius: 20px; font-size: 0.9em; }
        .healthy { background: rgba(74, 222, 128, 0.2); color: #4ade80; }
        .degraded { background: rgba(251, 191, 36, 0.2); color: #fbbf24; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏦 Financial Intelligence Platform</h1>
            <p>Bloomberg-Level Real-Time Market Intelligence</p>
            <div class="health-status">
                <span class="health-item healthy">● API Online</span>
                <span class="health-item healthy">● Database Ready</span>
                <span class="health-item healthy">● Cache Active</span>
            </div>
        </header>
        
        <nav class="nav">
            <div class="nav-item active" onclick="showSection('dashboard')">📊 Dashboard</div>
            <div class="nav-item" onclick="showSection('markets')">📈 Markets</div>
            <div class="nav-item" onclick="showSection('stocks')">🏢 Stocks</div>
            <div class="nav-item" onclick="showSection('news')">📰 News</div>
            <div class="nav-item" onclick="showSection('analytics')">📉 Analytics</div>
            <div class="nav-item" onclick="showSection('ai')">🤖 AI Insights</div>
        </nav>
        
        <div id="dashboard" class="section">
            <div class="grid">
                <div class="card">
                    <h3>📈 S&P 500</h3>
                    <div class="price">4,783.45</div>
                    <div class="change positive">▲ +0.85%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">52W High</div><div class="stat-label">4,950</div></div>
                        <div class="stat"><div class="stat-value">52W Low</div><div class="stat-label">3,850</div></div>
                    </div>
                </div>
                <div class="card">
                    <h3>📊 NASDAQ</h3>
                    <div class="price">15,055.65</div>
                    <div class="change positive">▲ +1.23%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">52W High</div><div class="stat-label">15,500</div></div>
                        <div class="stat"><div class="stat-value">52W Low</div><div class="stat-label">11,000</div></div>
                    </div>
                </div>
                <div class="card">
                    <h3>🏭 Industrial Average</h3>
                    <div class="price">37,468.61</div>
                    <div class="change positive">▲ +0.42%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">52W High</div><div class="stat-label">38,000</div></div>
                        <div class="stat"><div class="stat-value">52W Low</div><div class="stat-label">30,000</div></div>
                    </div>
                </div>
                <div class="card">
                    <h3>💼 Russell 2000</h3>
                    <div class="price">2,012.34</div>
                    <div class="change negative">▼ -0.56%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">52W High</div><div class="stat-label">2,200</div></div>
                        <div class="stat"><div class="stat-value">52W Low</div><div class="stat-label">1,500</div></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="markets" class="section" style="display: none;">
            <div class="grid">
                <div class="card">
                    <h3>🍎 Apple Inc. (AAPL)</h3>
                    <div class="price">$185.50</div>
                    <div class="change positive">▲ +1.28%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">Vol</div><div class="stat-label">52M</div></div>
                        <div class="stat"><div class="stat-value">Mkt Cap</div><div class="stat-label">$2.8T</div></div>
                        <div class="stat"><div class="stat-value">P/E</div><div class="stat-label">28.5</div></div>
                    </div>
                    <button class="btn" onclick="showStockDetails('AAPL')">View Details</button>
                </div>
                <div class="card">
                    <h3>🔵 Microsoft (MSFT)</h3>
                    <div class="price">$378.91</div>
                    <div class="change positive">▲ +2.15%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">Vol</div><div class="stat-label">28M</div></div>
                        <div class="stat"><div class="stat-value">Mkt Cap</div><div class="stat-label">$2.7T</div></div>
                        <div class="stat"><div class="stat-value">P/E</div><div class="stat-label">35.2</div></div>
                    </div>
                    <button class="btn" onclick="showStockDetails('MSFT')">View Details</button>
                </div>
                <div class="card">
                    <h3>🟢 Google (GOOGL)</h3>
                    <div class="price">$142.65</div>
                    <div class="change positive">▲ +0.89%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">Vol</div><div class="stat-label">25M</div></div>
                        <div class="stat"><div class="stat-value">Mkt Cap</div><div class="stat-label">$1.8T</div></div>
                        <div class="stat"><div class="stat-value">P/E</div><div class="stat-label">25.8</div></div>
                    </div>
                    <button class="btn" onclick="showStockDetails('GOOGL')">View Details</button>
                </div>
                <div class="card">
                    <h3>🔴 NVIDIA (NVDA)</h3>
                    <div class="price">$495.22</div>
                    <div class="change positive">▲ +3.45%</div>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">Vol</div><div class="stat-value">45M</div></div>
                        <div class="stat"><div class="stat-value">Mkt Cap</div><div class="stat-label">$1.2T</div></div>
                        <div class="stat"><div class="stat-value">P/E</div><div class="stat-label">62.5</div></div>
                    </div>
                    <button class="btn" onclick="showStockDetails('NVDA')">View Details</button>
                </div>
            </div>
        </div>
        
        <div id="stocks" class="section" style="display: none;">
            <div class="card">
                <h3>🏢 Stock Information</h3>
                <div id="stock-details"></div>
            </div>
        </div>
        
        <div id="news" class="section" style="display: none;">
            <div class="grid">
                <div class="card">
                    <h3>📰 Latest News</h3>
                    <div id="news-feed"></div>
                </div>
            </div>
        </div>
        
        <div id="analytics" class="section" style="display: none;">
            <div class="grid">
                <div class="card">
                    <h3>⚠️ Risk Metrics</h3>
                    <div id="risk-metrics"></div>
                </div>
                <div class="card">
                    <h3>📊 Portfolio Analytics</h3>
                    <div id="portfolio-analytics"></div>
                </div>
            </div>
        </div>
        
        <div id="ai" class="section" style="display: none;">
            <div class="grid">
                <div class="card">
                    <h3>🤖 AI Sentiment Analysis</h3>
                    <div id="sentiment-analysis"></div>
                </div>
                <div class="card">
                    <h3>💡 AI Market Insights</h3>
                    <div id="ai-insights"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(sectionId).style.display = 'block';
            event.target.classList.add('active');
            
            if (sectionId === 'news') loadNews();
            if (sectionId === 'analytics') loadAnalytics();
            if (sectionId === 'ai') loadAI();
        }
        
        function loadNews() {
            fetch('/api/v1/news/feed')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('news-feed').innerHTML = data.articles.map(a => 
                        `<div class="news-item">
                            <div class="news-title">${a.title}</div>
                            <div class="news-source">${a.source} • ${a.published_at}</div>
                        </div>`
                    ).join('');
                });
        }
        
        function loadAnalytics() {
            fetch('/api/v1/analytics/risk/AAPL')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('risk-metrics').innerHTML = Object.entries(data).map(([k, v]) => 
                        `<div class="stat"><div class="stat-value">${v}</div><div class="stat-label">${k}</div></div>`
                    ).join('');
                });
        }
        
        function loadAI() {
            fetch('/api/v1/ai/sentiment')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('sentiment-analysis').innerHTML = `
                        <div class="stat"><div class="stat-value">${data.overall_sentiment}</div><div class="stat-label">Sentiment</div></div>
                        <div class="stat"><div class="stat-value">${data.sentiment_score}</div><div class="stat-label">Score</div></div>
                    `;
                });
            
            document.getElementById('ai-insights').innerHTML = `
                <div class="chart">
                    <h4>💡 AI Analysis</h4>
                    <p>Tech sector shows strong momentum driven by AI adoption. Earnings growth expectations remain elevated.</p>
                    <div class="stats">
                        <div class="stat"><div class="stat-value">78%</div><div class="stat-label">Fundamental Score</div></div>
                        <div class="stat"><div class="stat-value">65%</div><div class="stat-label">Technical Score</div></div>
                        <div class="stat"><div class="stat-value">72%</div><div class="stat-label">Confidence</div></div>
                    </div>
                </div>
            `;
        }
        
        function showStockDetails(symbol) {
            fetch('/api/v1/stocks/info/' + symbol)
                .then(r => r.json())
                .then(data => {
                    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
                    document.getElementById('stocks').style.display = 'block';
                    document.getElementById('stock-details').innerHTML = `
                        <div class="grid">
                            <div class="stat"><div class="stat-value">${data.symbol}</div><div class="stat-label">Symbol</div></div>
                            <div class="stat"><div class="stat-value">${data.name}</div><div class="stat-label">Company</div></div>
                            <div class="stat"><div class="stat-value">${data.sector}</div><div class="stat-label">Sector</div></div>
                            <div class="stat"><div class="stat-value">${data.industry}</div><div class="stat-label">Industry</div></div>
                            <div class="stat"><div class="stat-value">$${(data.market_cap / 1000000000000).toFixed(2)}T</div><div class="stat-label">Market Cap</div></div>
                            <div class="stat"><div class="stat-value">${data.currency}</div><div class="stat-label">Currency</div></div>
                        </div>
                        <p style="margin-top: 20px;">${data.description}</p>
                    `;
                });
        }
        
        // Load initial data
        loadAnalytics();
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_health(self):
        """Handle health check."""
        self.send_json_response(200, {
            "status": "healthy",
            "service": "Financial Intelligence Platform",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def handle_api_info(self):
        """Handle API info."""
        self.send_json_response(200, {
            "name": "Financial Intelligence Platform API",
            "version": "1.0.0",
            "description": "Bloomberg-level real-time market intelligence platform",
            "endpoints": [
                "/health",
                "/api/v1/market/quotes",
                "/api/v1/market/summary",
                "/api/v1/stocks/info/{symbol}",
                "/api/v1/news/feed",
                "/api/v1/analytics/risk/{symbol}",
                "/api/v1/ai/sentiment"
            ]
        })
    
    def handle_quotes(self):
        """Handle market quotes."""
        symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "META", "TSLA", "AMZN", "JPM"]
        quotes = []
        for symbol in symbols:
            price = 100 + random.random() * 400
            change = (random.random() - 0.5) * 10
            quotes.append({
                "symbol": symbol,
                "price": round(Decimal(str(price)), 2),
                "change": round(Decimal(str(change)), 2),
                "change_percent": round(change/price*100, 2),
                "volume": random.randint(1000000, 50000000),
                "timestamp": datetime.utcnow().isoformat()
            })
        self.send_json_response(200, quotes)
    
    def handle_market_summary(self):
        """Handle market summary."""
        self.send_json_response(200, {
            "timestamp": datetime.utcnow().isoformat(),
            "indices": [
                {"symbol": "SPX", "name": "S&P 500", "value": 4783.45, "change": 0.85},
                {"symbol": "DJI", "name": "Dow Jones", "value": 37468.61, "change": 0.42},
                {"symbol": "IXIC", "name": "NASDAQ", "value": 15055.65, "change": 1.23},
                {"symbol": "RUT", "name": "Russell 2000", "value": 2012.34, "change": -0.56}
            ],
            "market_status": "open"
        })
    
    def handle_stock_info(self):
        """Handle stock info."""
        self.send_json_response(200, {
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
        })
    
    def handle_news(self):
        """Handle news feed."""
        articles = []
        sources = ["Reuters", "Bloomberg", "CNBC", "WSJ", "Financial Times"]
        for i in range(5):
            articles.append({
                "id": f"article_{i+1}",
                "title": f"Market Update: {random.choice(['Tech', 'Finance', 'Energy'])} sector sees significant movement",
                "source": random.choice(sources),
                "categories": ["Markets", "Economy"],
                "sentiment": random.choice(["positive", "neutral", "negative"]),
                "published_at": (datetime.utcnow() - timedelta(hours=i)).isoformat()
            })
        self.send_json_response(200, {"articles": articles})
    
    def handle_risk(self):
        """Handle risk metrics."""
        self.send_json_response(200, {
            "symbol": "AAPL",
            "volatility": round(random.uniform(20, 35), 2),
            "beta": round(random.uniform(0.8, 1.3), 2),
            "sharpe_ratio": round(random.uniform(0.5, 1.5), 2),
            "max_drawdown": round(random.uniform(-25, -10), 2),
            "var_95": round(random.uniform(-3, -1.5), 2),
            "correlation_benchmark": round(random.uniform(0.9, 1.0), 2)
        })
    
    def handle_sentiment(self):
        """Handle sentiment analysis."""
        self.send_json_response(200, {
            "symbol": "AAPL",
            "overall_sentiment": "bullish",
            "sentiment_score": round(random.uniform(0.2, 0.6), 2),
            "confidence": round(random.uniform(0.8, 0.95), 2),
            "components": {
                "news_sentiment": {"score": 0.45},
                "social_sentiment": {"score": 0.52}
            }
        })
    
    def handle_watchlists(self):
        """Handle watchlists."""
        self.send_json_response(200, {
            "watchlists": [
                {"id": 1, "name": "Tech Stocks", "symbols": ["AAPL", "MSFT", "GOOGL", "NVDA"]},
                {"id": 2, "name": "Finance", "symbols": ["JPM", "BAC", "GS", "MS"]},
                {"id": 3, "name": "Energy", "symbols": ["XOM", "CVX", "COP", "SLB"]}
            ]
        })
    
    def handle_sentiment_analyze(self, data):
        """Handle sentiment analysis request."""
        text = data.get("text", "")
        self.send_json_response(200, {
            "sentiment": "positive",
            "sentiment_score": round(random.uniform(0.5, 0.9), 4),
            "confidence": round(random.uniform(0.85, 0.99), 4),
            "emotions": {
                "joy": round(random.uniform(0.2, 0.5), 2),
                "fear": round(random.uniform(0.0, 0.2), 2),
                "surprise": round(random.uniform(0.1, 0.3), 2)
            }
        })
    
    def handle_create_alert(self, data):
        """Handle alert creation."""
        self.send_json_response(200, {
            "id": f"alert_{random.randint(1000,9999)}",
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        })


def run_server(port=8000):
    """Run the standalone server."""
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", port), FinancialAPIHandler) as httpd:
        print(f"\n{'='*70}")
        print("🏦 FINANCIAL INTELLIGENCE PLATFORM")
        print("   Bloomberg-Level Real-Time Market Intelligence")
        print(f"{'='*70}")
        print(f"\n✅ Server running at: http://localhost:{port}")
        print(f"📊 Frontend: http://localhost:{port}/index.html")
        print(f"📚 API Docs: http://localhost:{port}/api/v1")
        print(f"\n🛑 Press Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")


if __name__ == "__main__":
    run_server()

