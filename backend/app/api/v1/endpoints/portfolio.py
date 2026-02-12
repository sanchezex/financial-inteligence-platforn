"""
Financial Intelligence Platform - Portfolio Endpoints

API endpoints for portfolio management, positions, and trading.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.logging import get_logger
from app.services.portfolio_service import PortfolioService, PaperTradingService

logger = get_logger(__name__)

router = APIRouter()


# ============================================================================
# Pydantic Models
# ============================================================================

class OrderRequest(BaseModel):
    """Order request model."""
    symbol: str = Field(..., min_length=1, max_length=10, description="Stock symbol")
    order_type: str = Field(..., description="Order type: market, limit, stop, stop_limit, trailing_stop")
    side: str = Field(..., description="Order side: buy, sell")
    quantity: float = Field(..., gt=0, description="Number of shares")
    price: Optional[float] = Field(None, description="Limit price for limit orders")
    stop_price: Optional[float] = Field(None, description="Stop price for stop orders")
    trailing_amount: Optional[float] = Field(None, description="Trailing amount")
    trailing_percent: Optional[float] = Field(None, description="Trailing percent")
    time_in_force: str = Field("day", description="Time in force: day, gtc, ioc, fok")
    is_paper: bool = Field(True, description="Whether this is a paper trade")


class OrderResponse(BaseModel):
    """Order response model."""
    success: bool
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float]
    status: str
    message: str


class PositionResponse(BaseModel):
    """Position response model."""
    id: int
    symbol: str
    side: str
    quantity: float
    avg_entry_price: float
    current_price: Optional[float]
    total_cost: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float
    day_change: Optional[float]
    day_change_percent: Optional[float]


class PortfolioSummaryResponse(BaseModel):
    """Portfolio summary response model."""
    total_value: float
    total_cost: float
    total_unrealized_pnl: float
    total_return: float
    day_pnl: float
    positions_count: int
    is_paper: bool


class PerformanceResponse(BaseModel):
    """Portfolio performance response model."""
    total_value: float
    total_return: float
    day_pnl: float
    sharpe_ratio: float
    beta: float
    annualized_return: float
    annualized_volatility: float
    max_drawdown: float
    positions_count: int
    win_rate: float


class PaperAccountResponse(BaseModel):
    """Paper trading account response model."""
    initial_balance: float
    current_balance: float
    total_pnl: float
    total_return: float
    day_pnl: float
    day_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    max_drawdown: float
    buying_power: float


class TradeRecordResponse(BaseModel):
    """Trade record response model."""
    id: int
    symbol: str
    side: str
    quantity: float
    execution_price: float
    total_value: float
    total_cost: float
    pnl: float
    executed_at: Optional[str]
    is_paper: bool


# ============================================================================
# Portfolio Endpoints
# ============================================================================

@router.get("/portfolio/{user_id}/summary", response_model=PortfolioSummaryResponse)
async def get_portfolio_summary(
    user_id: int,
    is_paper: bool = Query(True, description="Use paper trading account"),
    db: Session = Depends(get_db)
):
    """
    Get portfolio summary for a user.
    
    Returns total value, P&L, and position counts.
    """
    service = PortfolioService(db, user_id, is_paper)
    summary = service.get_portfolio_summary()
    
    return PortfolioSummaryResponse(**summary)


@router.get("/portfolio/{user_id}/positions", response_model=List[PositionResponse])
async def get_positions(
    user_id: int,
    is_paper: bool = Query(True, description="Use paper trading account"),
    db: Session = Depends(get_db)
):
    """
    Get all current positions for a user.
    
    Returns position details with real-time P&L.
    """
    service = PortfolioService(db, user_id, is_paper)
    positions = service.get_positions()
    
    return [PositionResponse(**pos) for pos in positions]


@router.get("/portfolio/{user_id}/performance", response_model=List[Dict[str, Any]])
async def get_portfolio_performance(
    user_id: int,
    days: int = Query(default=30, le=365, description="Number of days of history"),
    is_paper: bool = Query(True, description="Use paper trading account"),
    db: Session = Depends(get_db)
):
    """
    Get historical portfolio performance.
    
    Returns daily portfolio values and returns.
    """
    service = PortfolioService(db, user_id, is_paper)
    performance = service.get_portfolio_performance(days)
    
    return performance


@router.get("/portfolio/{user_id}/metrics", response_model=PerformanceResponse)
async def get_portfolio_metrics(
    user_id: int,
    is_paper: bool = Query(True, description="Use paper trading account"),
    db: Session = Depends(get_db)
):
    """
    Get portfolio risk and performance metrics.
    
    Returns Sharpe ratio, beta, max drawdown, and other metrics.
    """
    service = PortfolioService(db, user_id, is_paper)
    metrics = service.calculate_portfolio_metrics()
    
    return PerformanceResponse(**metrics)


@router.post("/portfolio/{user_id}/positions/{symbol}/update")
async def update_position_price(
    user_id: int,
    symbol: str,
    current_price: float = Query(..., description="Current market price"),
    is_paper: bool = Query(True, description="Use paper trading account"),
    db: Session = Depends(get_db)
):
    """
    Update position with current market price.
    
    Triggers P&L recalculation.
    """
    service = PortfolioService(db, user_id, is_paper)
    service.update_position_price(symbol, current_price)
    
    return {"success": True, "message": f"Position updated for {symbol}"}


# ============================================================================
# Order Endpoints
# ============================================================================

@router.post("/orders", response_model=OrderResponse)
async def create_order(
    order: OrderRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new order.
    
    For paper trading: Executes immediately at the specified price.
    For live trading: Submits order to broker API.
    """
    user_id = 1  # Would come from auth in production
    
    if order.is_paper:
        # Use paper trading service
        service = PaperTradingService(db, user_id)
        
        if order.side == "buy":
            result = service.execute_buy_order(
                symbol=order.symbol,
                quantity=order.quantity,
                price=order.price or 100.0  # Default price for market orders
            )
        else:
            result = service.execute_sell_order(
                symbol=order.symbol,
                quantity=order.quantity,
                price=order.price or 100.0
            )
    else:
        # Would integrate with live broker API
        result = {
            "success": True,
            "order_id": str(uuid.uuid4())[:8],
            "symbol": order.symbol.upper(),
            "side": order.side,
            "order_type": order.order_type,
            "quantity": order.quantity,
            "price": order.price,
            "status": "pending",
            "message": "Order submitted to broker"
        }
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return OrderResponse(
        success=result["success"],
        order_id=result.get("order_id", str(uuid.uuid4())[:8]),
        symbol=result["symbol"],
        side=result["side"],
        order_type=order.order_type,
        quantity=order.quantity,
        price=order.price,
        status=result.get("status", "filled"),
        message=result.get("message", "Order executed")
    )


@router.get("/orders")
async def get_orders(
    user_id: int = Query(1, description="User ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    is_paper: bool = Query(True, description="Use paper trading account"),
    limit: int = Query(50, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get orders with optional filtering.
    
    Returns orders filtered by status, symbol, or other criteria.
    """
    from app.models.trade_models import Order
    
    query = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .filter(Order.is_paper == is_paper)
    )
    
    if status:
        query = query.filter(Order.status == status)
    
    if symbol:
        query = query.filter(Order.symbol == symbol.upper())
    
    orders = (
        query.order_by(Order.created_at.desc())
        .limit(limit)
        .all()
    )
    
    return {
        "orders": [
            {
                "id": o.id,
                "order_id": o.order_id,
                "symbol": o.symbol,
                "side": o.side,
                "order_type": o.order_type,
                "quantity": float(o.quantity),
                "filled_quantity": float(o.filled_quantity),
                "status": o.status,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "stop_price": float(o.stop_price) if o.stop_price else None,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ],
        "total": len(orders)
    }


@router.delete("/orders/{order_id}")
async def cancel_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    """
    Cancel a pending order.
    
    Only pending orders can be cancelled.
    """
    from app.models.trade_models import Order
    
    order = (
        db.query(Order)
        .filter(Order.order_id == order_id)
        .first()
    )
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    order.status = "cancelled"
    order.cancelled_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "order_id": order_id,
        "status": "cancelled",
        "message": "Order cancelled successfully"
    }


# ============================================================================
# Trade History Endpoints
# ============================================================================

@router.get("/trades", response_model=List[TradeRecordResponse])
async def get_trades(
    user_id: int = Query(1, description="User ID"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    is_paper: bool = Query(True, description="Use paper trading account"),
    limit: int = Query(50, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Get trade history.
    
    Returns executed trades with P&L information.
    """
    from app.models.trade_models import Trade
    
    query = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .filter(Trade.is_paper == is_paper)
    )
    
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    
    trades = (
        query.order_by(Trade.executed_at.desc())
        .limit(limit)
        .all()
    )
    
    return [
        TradeRecordResponse(
            id=t.id,
            symbol=t.symbol,
            side=t.side,
            quantity=float(t.quantity),
            execution_price=float(t.execution_price),
            total_value=float(t.total_value),
            total_cost=float(t.total_cost),
            pnl=float(t.total_value - t.total_cost) if t.total_value and t.total_cost else 0,
            executed_at=t.executed_at.isoformat() if t.executed_at else None,
            is_paper=t.is_paper,
        )
        for t in trades
    ]


# ============================================================================
# Paper Trading Endpoints
# ============================================================================

@router.get("/paper-trading/account", response_model=PaperAccountResponse)
async def get_paper_account(
    user_id: int = Query(1, description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Get paper trading account summary.
    
    Returns account balance, P&L, and trading statistics.
    """
    service = PaperTradingService(db, user_id)
    account = service.get_account_summary()
    
    return PaperAccountResponse(**account)


@router.post("/paper-trading/reset")
async def reset_paper_account(
    user_id: int = Query(1, description="User ID"),
    db: Session = Depends(get_db)
):
    """
    Reset paper trading account.
    
    Resets balance to $100,000 and closes all positions.
    WARNING: This action cannot be undone.
    """
    service = PaperTradingService(db, user_id)
    result = service.reset_account()
    
    return {
        "success": True,
        "message": "Paper trading account reset",
        **result
    }


@router.post("/paper-trading/buy")
async def paper_buy(
    user_id: int = Query(1, description="User ID"),
    symbol: str = Query(..., min_length=1, max_length=10, description="Stock symbol"),
    quantity: float = Query(..., gt=0, description="Number of shares"),
    price: float = Query(..., gt=0, description="Price per share"),
    db: Session = Depends(get_db)
):
    """
    Execute a paper trading buy order.
    
    Immediately fills at the specified price.
    """
    service = PaperTradingService(db, user_id)
    result = service.execute_buy_order(symbol, quantity, price)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.post("/paper-trading/sell")
async def paper_sell(
    user_id: int = Query(1, description="User ID"),
    symbol: str = Query(..., min_length=1, max_length=10, description="Stock symbol"),
    quantity: float = Query(..., gt=0, description="Number of shares"),
    price: float = Query(..., gt=0, description="Price per share"),
    db: Session = Depends(get_db)
):
    """
    Execute a paper trading sell order.
    
    Immediately fills at the specified price.
    """
    service = PaperTradingService(db, user_id)
    result = service.execute_sell_order(symbol, quantity, price)
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result

