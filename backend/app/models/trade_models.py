"""
Trade Models for Financial Intelligence Platform

Database models for portfolio management, orders, positions, and trade tracking.
Supports both live trading and paper trading simulation.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, DECIMAL, 
    Enum, JSON, ForeignKey, Boolean, BigInteger, Index
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class OrderType(enum.Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderSide(enum.Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderStatus(enum.Enum):
    """Order status enumeration."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class OrderTimeInForce(enum.Enum):
    """Time in force enumeration."""
    DAY = "day"
    GTC = "gtc"  # Good till cancelled
    IOC = "ioc"  # Immediate or cancel
    FOK = "fok"  # Fill or kill


class PositionSide(enum.Enum):
    """Position side enumeration."""
    LONG = "long"
    SHORT = "short"


class TradeType(enum.Enum):
    """Trade type enumeration."""
    OPENING = "opening"
    CLOSING = "closing"


class JournalEntryType(enum.Enum):
    """Journal entry type enumeration."""
    PRE_TRADE = "pre_trade"
    POST_TRADE = "post_trade"
    DAILY_NOTES = "daily_notes"
    LESSON_LEARNED = "lesson_learned"
    STRATEGY_REVIEW = "strategy_review"


class RiskLevel(enum.Enum):
    """Risk level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class User(Base):
    """
    Extended user model with paper trading support.
    
    Extends the base User model with additional fields for trading functionality.
    """
    __tablename__ = "users"
    
    # Paper trading settings
    paper_trading_enabled = Column(Boolean, default=False)
    paper_account_balance = Column(DECIMAL(20, 2), default=100000.00)
    
    # Risk settings
    max_position_size = Column(DECIMAL(5, 2), default=25.00)  # Max % per position
    max_portfolio_risk = Column(DECIMAL(5, 2), default=10.00)  # Max VaR as % of portfolio
    allow_short_selling = Column(Boolean, default=True)
    allow_options = Column(Boolean, default=False)
    
    # Notification preferences
    alert_on_fill = Column(Boolean, default=True)
    alert_on_cancel = Column(Boolean, default=False)
    risk_warning_threshold = Column(String(20), default="medium")
    
    # Relationships
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="user", cascade="all, delete-orphan")
    journal_entries = relationship("TradeJournalEntry", back_populates="user", cascade="all, delete-orphan")


class Trade(Base):
    """
    Individual trade record model.
    
    Records all trades with execution details for performance tracking and analysis.
    """
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Trade identification
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Trade details
    trade_type = Column(String(20), nullable=False)  # opening, closing
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(DECIMAL(15, 6), nullable=False)
    execution_price = Column(DECIMAL(15, 4), nullable=False)
    
    # Order details
    order_type = Column(String(20), nullable=True)  # market, limit, etc.
    limit_price = Column(DECIMAL(15, 4), nullable=True)
    stop_price = Column(DECIMAL(15, 4), nullable=True)
    
    # Execution details
    commission = Column(DECIMAL(10, 4), default=0)
    fees = Column(DECIMAL(10, 4), default=0)
    slippage = Column(DECIMAL(10, 4), default=0)
    execution_time = Column(DateTime, nullable=True)
    
    # Cost basis
    total_value = Column(DECIMAL(20, 4), nullable=False)
    total_cost = Column(DECIMAL(20, 4), nullable=False)
    
    # Paper trading flag
    is_paper = Column(Boolean, default=True)
    
    # Notes and tags
    notes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    
    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    order = relationship("Order", back_populates="trades")


class Order(Base):
    """
    Order management model.
    
    Supports various order types including market, limit, stop, and trailing stop orders.
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Order identification
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Order specifications
    order_type = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(DECIMAL(15, 6), nullable=False)
    
    # Price specifications
    limit_price = Column(DECIMAL(15, 4), nullable=True)
    stop_price = Column(DECIMAL(15, 4), nullable=True)
    trailing_amount = Column(DECIMAL(10, 4), nullable=True)
    trailing_percent = Column(DECIMAL(5, 2), nullable=True)
    
    # Time in force
    time_in_force = Column(String(10), default="day")
    
    # Order status
    status = Column(String(20), default="pending", index=True)
    filled_quantity = Column(DECIMAL(15, 6), default=0)
    remaining_quantity = Column(DECIMAL(15, 6), nullable=True)
    
    # Average fill price
    avg_fill_price = Column(DECIMAL(15, 4), nullable=True)
    
    # Commission and fees
    commission = Column(DECIMAL(10, 4), default=0)
    
    # Paper trading flag
    is_paper = Column(Boolean, default=True)
    
    # Strategy association
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True)
    
    # Reason for rejection
    reject_reason = Column(Text, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    trades = relationship("Trade", back_populates="order", cascade="all, delete-orphan")


class Position(Base):
    """
    Current position model.
    
    Tracks current holdings with real-time P&L calculations.
    """
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Position details
    side = Column(String(10), default="long")  # long, short
    quantity = Column(DECIMAL(15, 6), nullable=False)
    
    # Cost basis
    avg_entry_price = Column(DECIMAL(15, 4), nullable=False)
    total_cost = Column(DECIMAL(20, 4), nullable=False)
    
    # Market data
    current_price = Column(DECIMAL(15, 4), nullable=True)
    market_value = Column(DECIMAL(20, 4), nullable=True)
    
    # P&L calculations
    unrealized_pnl = Column(DECIMAL(20, 4), nullable=True)
    unrealized_pnl_percent = Column(DECIMAL(10, 4), nullable=True)
    
    # Day's P&L
    day_change = Column(DECIMAL(20, 4), nullable=True)
    day_change_percent = Column(DECIMAL(10, 4), nullable=True)
    
    # Paper trading flag
    is_paper = Column(Boolean, default=True)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint for user-symbol combination
    __table_args__ = (
        Index('idx_user_symbol_position', 'user_id', 'symbol'),
    )
    
    # Relationships
    user = relationship("User", back_populates="positions")


class PortfolioHistory(Base):
    """
    Historical portfolio value tracking.
    
    Stores daily portfolio snapshots for performance analysis.
    """
    __tablename__ = "portfolio_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Portfolio values
    total_value = Column(DECIMAL(20, 4), nullable=False)
    cash_balance = Column(DECIMAL(20, 4), default=0)
    securities_value = Column(DECIMAL(20, 4), default=0)
    
    # P&L
    unrealized_pnl = Column(DECIMAL(20, 4), default=0)
    realized_pnl = Column(DECIMAL(20, 4), default=0)
    day_pnl = Column(DECIMAL(20, 4), default=0)
    
    # Portfolio metrics snapshot
    day_return = Column(DECIMAL(10, 6), nullable=True)
    total_return = Column(DECIMAL(10, 6), nullable=True)
    
    # Risk metrics snapshot
    portfolio_beta = Column(DECIMAL(8, 4), nullable=True)
    portfolio_var = Column(DECIMAL(10, 4), nullable=True)
    
    # Cash flows
    deposits = Column(DECIMAL(20, 4), default=0)
    withdrawals = Column(DECIMAL(20, 4), default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint for user-date combination
    __table_args__ = (
        Index('idx_user_date_portfolio', 'user_id', 'date'),
    )


class TradeJournalEntry(Base):
    """
    Trading journal entry model.
    
    Supports pre-trade plans, post-trade reviews, and learning entries.
    """
    __tablename__ = "trade_journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Entry identification
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    symbol = Column(String(20), nullable=True, index=True)
    
    # Entry type
    entry_type = Column(String(20), nullable=False)
    
    # Entry content
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Pre-trade fields
    entry_plan = Column(Text, nullable=True)
    entry_reason = Column(Text, nullable=True)
    expected_outcome = Column(Text, nullable=True)
    risk_management_plan = Column(Text, nullable=True)
    
    # Post-trade fields
    actual_outcome = Column(Text, nullable=True)
    what_went_well = Column(Text, nullable=True)
    what_could_be_improved = Column(Text, nullable=True)
    
    # Emotion tracking
    emotion_before = Column(String(50), nullable=True)
    emotion_after = Column(String(50), nullable=True)
    emotion_intensity = Column(Integer, nullable=True)  # 1-10 scale
    
    # Results
    pnl = Column(DECIMAL(20, 4), nullable=True)
    success = Column(Boolean, nullable=True)
    
    # Tags and categories
    tags = Column(JSON, nullable=True)
    strategies_used = Column(JSON, nullable=True)
    
    # Timestamps
    entry_date = Column(Date, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="journal_entries")


class Strategy(Base):
    """
    Trading strategy model.
    
    Defines reusable trading strategies with entry/exit rules.
    """
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Strategy details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), nullable=True)  # trend_following, mean_reversion, etc.
    
    # Rules configuration (JSON)
    entry_rules = Column(JSON, nullable=True)
    exit_rules = Column(JSON, nullable=True)
    position_sizing = Column(JSON, nullable=True)
    risk_rules = Column(JSON, nullable=True)
    
    # Backtest results
    backtest_enabled = Column(Boolean, default=False)
    backtest_results = Column(JSON, nullable=True)
    
    # Performance metrics
    total_trades = Column(Integer, default=0)
    win_rate = Column(DECIMAL(5, 2), nullable=True)
    profit_factor = Column(DECIMAL(8, 4), nullable=True)
    avg_trade_pnl = Column(DECIMAL(15, 4), nullable=True)
    max_drawdown = Column(DECIMAL(5, 2), nullable=True)
    
    # Active status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = relationship("Order", back_populates="strategy")


class RiskLimit(Base):
    """
    User-defined risk limits model.
    
    Stores configurable risk limits for portfolio management.
    """
    __tablename__ = "risk_limits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Limit type
    limit_type = Column(String(50), nullable=False)  # position_size, concentration, etc.
    
    # Limit configuration
    limit_name = Column(String(100), nullable=False)
    limit_value = Column(DECIMAL(20, 4), nullable=False)
    limit_unit = Column(String(20), nullable=True)  # percent, dollars, etc.
    
    # Actions when limit breached
    alert_enabled = Column(Boolean, default=True)
    auto_close_enabled = Column(Boolean, default=False)
    notification_channel = Column(String(50), default="app")
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        Index('idx_user_limit_type', 'user_id', 'limit_type'),
    )


class PaperTradingAccount(Base):
    """
    Paper trading account model.
    
    Tracks virtual trading performance separate from live trading.
    """
    __tablename__ = "paper_trading_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Account settings
    initial_balance = Column(DECIMAL(20, 2), default=100000.00)
    current_balance = Column(DECIMAL(20, 2), default=100000.00)
    buying_power = Column(DECIMAL(20, 2), default=100000.00)
    
    # Performance metrics
    total_pnl = Column(DECIMAL(20, 4), default=0)
    total_return = Column(DECIMAL(10, 4), default=0)
    day_pnl = Column(DECIMAL(20, 4), default=0)
    day_return = Column(DECIMAL(10, 4), default=0)
    
    # Trading statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(DECIMAL(5, 2), default=0)
    
    # Current drawdown
    peak_value = Column(DECIMAL(20, 2), default=100000.00)
    current_drawdown = Column(DECIMAL(10, 4), default=0)
    max_drawdown = Column(DECIMAL(10, 4), default=0)
    
    # Last updated
    last_trade_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Note: Order.strategy relationship requires Strategy model to be loaded first
# This is handled at the bottom of the file to avoid circular imports

# Import Strategy here to avoid circular import
from app.models.trade_models import Strategy

# Add the missing relationship after Strategy is defined
Order.strategy = relationship("Strategy", back_populates="orders")

