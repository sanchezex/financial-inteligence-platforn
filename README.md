# Financial Intelligence Platform

## Bloomberg-Level Real-Time Market Intelligence System

A comprehensive real-time market intelligence platform featuring data ingestion, analytics, AI/NLP integration, and an interactive React dashboard with clickable stock details.

![Platform Overview](docs/screenshot.png)

## Features

### Dashboard & User Interface
- **Real-Time Market Overview** - Live streaming of major indices (S&P 500, Dow Jones, NASDAQ, Russell 2000)
- **Interactive Watchlist** - Clickable stock items with real-time price updates
- **Customizable Navigation** - Sidebar with tabs for Dashboard, Markets, Stocks, Macro, Shipping, News, Analytics, AI Insights, Watchlists, and Alerts
- **AI-Powered Insights** - Smart recommendations and market sentiment analysis
- **Economic Calendar** - Track upcoming economic events and Fed meetings

### Clickable Stock Details
- **Interactive Stock Modal** - Click any stock to view comprehensive details
- **24-Hour Trading Activity** - Hourly price, volume, and change data
- **Interactive Price Chart** - Visual representation with gradient fills
- **Period Selection** - Toggle between 1D, 1W, 1M, 3M, 1Y, and ALL views
- **Key Statistics** - Day High/Low, Volume, Market Cap, P/E Ratio, EPS, 52-Week Range
- **Latest News** - Real-time news articles related to the selected stock
- **Quick Actions** - Add to Watchlist, Set Price Alert, View Full Analysis

### Shipping Intelligence
- **Live Shipping Map** - Interactive vessel tracking visualization
- **Port Activity Monitoring** - Real-time port congestion data
- **Freight Rate Tracking** - Baltic Dry Index and major route rates

### Analytics & AI
- **Correlation Analysis** - Understand relationships between assets
- **Risk Metrics** - VaR, Sharpe ratio, Beta calculations
- **Pattern Detection** - Automated technical pattern recognition
- **Sentiment Analysis** - AI-powered news and social media sentiment

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Docker and Docker Compose (optional, for backend services)
- 8GB+ RAM recommended
- 10GB+ disk space

### Running the Frontend

```bash
# Navigate to frontend directory
cd /home/sanchez/sanchezProjects/future/frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build

# Serve production build
npx serve -s build -l 3000
```

### Frontend Features

| Feature | Description |
|---------|-------------|
| **Hot Reload** | Changes reflect instantly during development |
| **Production Build** | Optimized bundles with code splitting |
| **Service Worker** | Offline caching support |
| **Responsive Design** | Works on desktop and tablet |

## Project Structure

```
financial-intelligence-platform/
├── frontend/                           # React Frontend Application
│   ├── public/
│   │   └── index.html                   # HTML template
│   ├── src/
│   │   ├── App.js                       # Main application component
│   │   ├── App.css                      # Global styles
│   │   ├── index.js                     # Entry point
│   │   └── components/
│   │       ├── ShippingMap.js           # Interactive shipping map
│   │       ├── ShippingMap.css          # Map styles
│   │       ├── StockDetailModal.js     # Clickable stock modal
│   │       ├── StockDetailModal.css    # Modal styles
│   │       ├── MarketImpactPanel.js    # Market impact visualization
│   │       └── VesselMarker.js          # Shipping vessel markers
│   ├── package.json
│   ├── build/                           # Production build output
│   └── node_modules/
│
├── backend/                            # FastAPI Backend
│   ├── app/
│   │   ├── main.py                      # Application entry point
│   │   ├── api/v1/endpoints/            # API route handlers
│   │   │   ├── market.py               # Market data endpoints
│   │   │   ├── stocks.py               # Stock data endpoints
│   │   │   ├── shipping.py             # Shipping data endpoints
│   │   │   ├── news.py                 # News & sentiment
│   │   │   ├── analytics.py            # Analytics endpoints
│   │   │   ├── ai.py                   # AI/NLP endpoints
│   │   │   ├── alerts.py               # Alert management
│   │   │   └── watchlists.py           # Watchlist CRUD
│   │   ├── core/                       # Configuration & utilities
│   │   ├── db/                         # Database models
│   │   └── services/                   # Business logic services
│   ├── requirements.txt
│   └── Dockerfile
│
├── services/                           # Microservices
│   ├── data-ingestion/                 # Data pipeline service
│   ├── analytics/                      # Analytics engine
│   └── ai-nlp/                        # AI/NLP processing
│
├── database/
│   ├── clickhouse-config/              # ClickHouse configuration
│   └── init-scripts/                  # Database initialization
│
├── monitoring/                         # Observability
│   ├── prometheus/                     # Metrics collection
│   └── grafana/                       # Dashboards
│
├── nginx/                             # Reverse proxy
│   └── nginx.conf
│
└── docker-compose.yml                  # Container orchestration
```

## Frontend Components

### App.js - Main Dashboard
The core React component containing:
- **State Management**: Active tab, watchlist, market data
- **Navigation**: Sidebar with 10 functional sections
- **Market Display**: Indices, watchlist, quick stats
- **Modal Integration**: Click handlers for stock details

```javascript
// State for selected stock (opens detail modal)
const [selectedStock, setSelectedStock] = useState(null);

// Click handler for watchlist items
<WatchlistItem onClick={() => setSelectedStock(symbol)} />
```

### StockDetailModal - Clickable Stock Details
A comprehensive modal component showing:

```javascript
// Features
- Real-time price display
- Interactive SVG chart with gradient
- 24-hour hourly trading data table
- Key statistics grid
- Latest news feed
- Period tabs (1D, 1W, 1M, 3M, 1Y, ALL)
- Action buttons
```

### ShippingMap Component
- Leaflet-based interactive map
- Vessel tracking visualization
- Port activity markers
- Real-time updates

### MarketImpactPanel
- Visual impact analysis
- Correlation matrices
- Risk indicators

## Styling

The application uses a professional dark theme:

```css
/* Color Palette */
--primary: #1d9bf0        /* Twitter blue */
--positive: #22c55e        /* Green for gains */
--negative: #ef4444       /* Red for losses */
--background: #0f1419     /* Dark background */
--card-bg: #16181c        /* Card background */
--text-primary: #e0e0e0   /* Primary text */
--text-secondary: #8b98a5 /* Secondary text */
```

## API Endpoints

### Market Data
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/market/quotes/{symbol}` | GET | Real-time quote |
| `/api/v1/market/summary` | GET | Market indices |
| `/api/v1/market/historical/{symbol}` | GET | Historical data |

### Stocks
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/stocks/info/{symbol}` | GET | Company info |
| `/api/v1/stocks/fundamentals/{symbol}` | GET | Fundamentals |
| `/api/v1/stocks/earnings/{symbol}` | GET | Earnings data |

### News & AI
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/news/feed` | GET | News feed |
| `/api/v1/ai/sentiment/analyze` | POST | Sentiment analysis |
| `/api/v1/ai/insights/generate` | POST | AI insights |

## Configuration

### Frontend Configuration (package.json)

```json
{
  "name": "financial-intelligence-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }
}
```

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_MAPBOX_TOKEN=your-mapbox-token
```

## Architecture

```
+---------------------------------------------------------------------+
|                        React Frontend                                |
|  +-------------+  +---------------+  +----------------------------+  |
|  |  Dashboard  |  |  Stock Modal |  |      Shipping Map         |  |
|  +------+------+  +------+-------+  +------------+-------------+   |
|         |                 |                        |               |
|         +-----------------+------------------------+               |
|                              |                                      |
|                              v                                      |
|              +---------------------------+                          |
|              |   React State/Props       |                          |
|              +------------+--------------+                          |
+---------------------------+-----------------------------------------+
                            |
                            v
+---------------------------------------------------------------------+
|                        REST API Layer                                |
|              (FastAPI Backend @ localhost:8000)                    |
+---------------------------+-----------------------------------------+
                            |
          +------------------+-------------------+
          v                   v                   v
   +-------------+    +----------------+    +----------------+
   |  Market     |    |    Stocks      |    |    AI/NLP      |
   |  Service    |    |    Service     |    |    Service     |
   +------+------+    +-------+--------+    +-------+--------+
          |                   |                   |
          v                   v                   v
   +----------------------------------------------------------------+
   |                    Data Infrastructure                         |
   |  PostgreSQL | ClickHouse | Redis | Kafka | MinIO                |
   +----------------------------------------------------------------+
```

## Responsive Design

| Breakpoint | Layout |
|------------|--------|
| Desktop (>1200px) | Full sidebar, multi-column grid |
| Tablet (768-1200px) | Collapsed sidebar, adaptive grid |
| Mobile (<768px) | Bottom navigation, single column |

## Testing

```bash
# Run frontend tests
cd frontend
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

## Build & Deployment

### Production Build
```bash
npm run build
# Creates optimized production bundle in /build
```

### Serve Production Build
```bash
npx serve -s build -l 3000
```

### Docker Deployment
```bash
# Build frontend image
docker build -t financial-intel-frontend ./frontend

# Run container
docker run -p 3000:3000 financial-intel-frontend
```

## Security Considerations

For production deployment:
- Enable HTTPS/SSL
- Implement authentication (OAuth2/JWT)
- Add rate limiting on API endpoints
- Enable CORS restrictions
- Use environment secrets for API keys
- Implement proper CSP headers

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For questions or issues:
- Open a GitHub issue
- Check the API documentation at `/docs`
- Review backend logs in Grafana

---

Built with love for the financial technology community

**Version:** 1.0.0
**Last Updated:** 2024
**Frontend Stack:** React 18, CSS Modules

