# Financial Intelligence Platform - Trade Features Module

## Overview
This module adds trade-related features including:
- Portfolio Management
- Order Management
- Risk Management
- Position Tracking
- Trade Journal

## Database Models Added

### Trade Models
- **Trade** - Individual trade records
- **Order** - Pending and executed orders
- **Position** - Current holdings with unrealized P&L
- **TradeJournalEntry** - Trading journal entries

### Risk Models
- **PortfolioMetrics** - Portfolio performance metrics
- **RiskLimits** - User-defined risk limits

## Files Added

### Backend
1. `backend/app/models/trade_models.py` - SQLAlchemy models for trade features
2. `backend/app/api/v1/endpoints/portfolio.py` - Portfolio API endpoints
3. `backend/app/api/v1/endpoints/orders.py` - Order management endpoints
4. `backend/app/services/portfolio_service.py` - Portfolio business logic
5. `backend/app/services/risk_service.py` - Risk calculation service

### Database
6. `database/init-scripts/02-trade-schema.sql` - Trade tables schema

### Frontend
7. `frontend/src/components/Portfolio.js` - Enhanced portfolio dashboard
8. `frontend/src/components/OrderEntry.js` - Order entry component
9. `frontend/src/components/Positions.js` - Positions view
10. `frontend/src/components/TradeHistory.js` - Trade history
11. `frontend/src/components/RiskDashboard.js` - Risk metrics dashboard

## Usage

### Portfolio API Endpoints

```bash
# Get user portfolio
GET /api/v1/portfolio/{user_id}

# Get positions
GET /api/v1/portfolio/{user_id}/positions

# Get portfolio performance
GET /api/v1/portfolio/{user_id}/performance

# Get portfolio metrics
GET /api/v1/portfolio/{user_id}/metrics
```

### Order API Endpoints

```bash
# Create order
POST /api/v1/orders
{
    "user_id": 1,
    "symbol": "AAPL",
    "order_type": "market",
    "side": "buy",
    "quantity": 10,
    "price": 150.00
}

# Get orders
GET /api/v1/orders?user_id=1&status=pending

# Cancel order
DELETE /api/v1/orders/{order_id}
```

## Portfolio Metrics Included

- Total portfolio value
- Unrealized P&L
- Realized P&L
- Day's P&L
- Beta (portfolio sensitivity)
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Value at Risk (VaR)
- Alpha
- Information ratio

## Order Types Supported

- **Market** - Execute at best available price
- **Limit** - Execute at specified price or better
- **Stop** - Trigger market order when price reached
- **Stop-Limit** - Trigger limit order when price reached
- **Trailing Stop** - Dynamic stop based on price movement

## Position Tracking

- Average cost basis
- Current market value
- Unrealized P&L
- P&L percentage
- Day's change
- Weight in portfolio
- Beta-weighted exposure
- Greeks exposure (for options)

## Risk Management

### Real-Time Risk Metrics
- Portfolio VaR (95% confidence)
- Portfolio beta
- Correlation to benchmark
- Sector concentration
- Single stock exposure limits

### Alerts
- Position threshold alerts
- Concentration warnings
- Margin call warnings

## Database Schema Changes

### New Tables
- `trades` - Individual trade records
- `orders` - Order management
- `positions` - Current holdings
- `portfolio_history` - Historical portfolio values
- `trade_journal` - Trading journal entries
- `risk_limits` - User risk configurations

### Modified Tables
- `users` - Added paper_trading_enabled field
- `portfolio_holdings` - Enhanced with cost basis tracking

