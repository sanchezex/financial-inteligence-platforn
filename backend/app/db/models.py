# Database models for MySQL
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, DECIMAL, Enum, JSON, ForeignKey, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class IdeaType(enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class SignalType(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"
    NEUTRAL = "NEUTRAL"


class Sentiment(enum.Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class AlertType(enum.Enum):
    ABOVE = "above"
    BELOW = "below"
    CHANGE = "change"


class AnomalyType(enum.Enum):
    VOLUME_SPIKE = "volume_spike"
    PRICE_MOVEMENT = "price_movement"
    OPTIONS_ACTIVITY = "options_activity"
    SENTIMENT_SHIFT = "sentiment_shift"
    VOLATILITY_SURGE = "volatility_surge"


class Severity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(Text)
    preferences = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alerts = relationship("PriceAlert", back_populates="user")
    watchlists = relationship("Watchlist", back_populates="user")
    portfolios = relationship("PortfolioHolding", back_populates="user")


class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    exchange = Column(String(50))
    current_price = Column(DECIMAL(15, 2))
    price_change = Column(DECIMAL(15, 2))
    price_change_percent = Column(DECIMAL(10, 4))
    market_cap = Column(DECIMAL(20, 2))
    pe_ratio = Column(DECIMAL(10, 2))
    eps = Column(DECIMAL(10, 4))
    dividend_yield = Column(DECIMAL(8, 4))
    volume = Column(BigInteger)
    avg_volume = Column(BigInteger)
    high_52w = Column(DECIMAL(15, 2))
    low_52w = Column(DECIMAL(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fundamentals = relationship("FundamentalData", back_populates="stock", cascade="all, delete-orphan")
    ratios = relationship("FinancialRatio", back_populates="stock", cascade="all, delete-orphan")
    growth_metrics = relationship("GrowthMetric", back_populates="stock", cascade="all, delete-orphan")
    options = relationship("OptionData", back_populates="stock", cascade="all, delete-orphan")
    institutional_holdings = relationship("InstitutionalHolding", back_populates="stock", cascade="all, delete-orphan")
    short_interest = relationship("ShortInterest", back_populates="stock", cascade="all, delete-orphan")
    earnings = relationship("EarningsCalendar", back_populates="stock", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")
    news = relationship("News", back_populates="stock", cascade="all, delete-orphan")


class FundamentalData(Base):
    __tablename__ = "fundamental_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    period = Column(String(20), nullable=False)
    fiscal_year = Column(Integer)
    revenue = Column(DECIMAL(20, 2))
    cost_of_revenue = Column(DECIMAL(20, 2))
    gross_profit = Column(DECIMAL(20, 2))
    operating_expenses = Column(DECIMAL(20, 2))
    operating_income = Column(DECIMAL(20, 2))
    net_income = Column(DECIMAL(20, 2))
    eps = Column(DECIMAL(10, 4))
    total_assets = Column(DECIMAL(20, 2))
    total_liabilities = Column(DECIMAL(20, 2))
    shareholders_equity = Column(DECIMAL(20, 2))
    cash_and_equivalents = Column(DECIMAL(20, 2))
    short_term_investments = Column(DECIMAL(20, 2))
    long_term_debt = Column(DECIMAL(20, 2))
    operating_cash_flow = Column(DECIMAL(20, 2))
    capital_expenditures = Column(DECIMAL(20, 2))
    free_cash_flow = Column(DECIMAL(20, 2))
    dividend_payments = Column(DECIMAL(20, 2))
    share_repurchases = Column(DECIMAL(20, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="fundamentals")


class FinancialRatio(Base):
    __tablename__ = "financial_ratios"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    period = Column(String(20), nullable=False)
    pe_ratio = Column(DECIMAL(10, 2))
    pb_ratio = Column(DECIMAL(10, 2))
    ps_ratio = Column(DECIMAL(10, 2))
    roe = Column(DECIMAL(10, 4))
    roa = Column(DECIMAL(10, 4))
    current_ratio = Column(DECIMAL(10, 4))
    debt_to_equity = Column(DECIMAL(10, 4))
    profit_margin = Column(DECIMAL(10, 4))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="ratios")


class GrowthMetric(Base):
    __tablename__ = "growth_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    period = Column(String(20), nullable=False)
    revenue_growth = Column(DECIMAL(10, 4))
    eps_growth = Column(DECIMAL(10, 4))
    revenue_cagr = Column(DECIMAL(10, 4))
    eps_cagr = Column(DECIMAL(10, 4))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="growth_metrics")


class OptionData(Base):
    __tablename__ = "options_data"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    expiry_date = Column(Date, nullable=False)
    strike_price = Column(DECIMAL(15, 2), nullable=False)
    option_type = Column(String(10), nullable=False)  # 'call' or 'put'
    bid = Column(DECIMAL(10, 2))
    ask = Column(DECIMAL(10, 2))
    last_price = Column(DECIMAL(10, 2))
    volume = Column(BigInteger)
    open_interest = Column(BigInteger)
    implied_volatility = Column(DECIMAL(8, 4))
    delta = Column(DECIMAL(8, 4))
    gamma = Column(DECIMAL(8, 4))
    theta = Column(DECIMAL(8, 4))
    vega = Column(DECIMAL(8, 4))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="options")


class InstitutionalHolding(Base):
    __tablename__ = "institutional_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    holder_name = Column(String(255), nullable=False)
    shares_held = Column(BigInteger)
    ownership_percent = Column(DECIMAL(8, 4))
    value = Column(DECIMAL(20, 2))
    quarter_reported = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="institutional_holdings")


class ShortInterest(Base):
    __tablename__ = "short_interest"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False)
    shares_shorted = Column(BigInteger)
    days_to_cover = Column(DECIMAL(10, 2))
    short_percent = Column(DECIMAL(8, 4))
    squeeze_potential = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="short_interest")


class EarningsCalendar(Base):
    __tablename__ = "earnings_calendar"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    earnings_date = Column(Date, nullable=False)
    estimate = Column(DECIMAL(10, 4))
    surprise = Column(DECIMAL(10, 4))
    fiscal_quarter = Column(Integer)
    fiscal_year = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="earnings")


class TradeIdea(Base):
    __tablename__ = "trade_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    author_name = Column(String(255), nullable=False)
    author_avatar = Column(String(10))
    symbol = Column(String(20), nullable=False, index=True)
    idea_type = Column(String(10), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text)
    analysis = Column(Text)
    entry_price = Column(DECIMAL(15, 2))
    current_price = Column(DECIMAL(15, 2))
    target_price = Column(DECIMAL(15, 2))
    stop_loss = Column(DECIMAL(15, 2))
    risk_reward = Column(String(20))
    timeframe = Column(String(50))
    confidence = Column(Integer)
    ai_score = Column(Integer)
    sentiment = Column(String(20))
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    tags = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AISignal(Base):
    __tablename__ = "ai_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    signal = Column(String(20), nullable=False)
    confidence = Column(DECIMAL(5, 2), nullable=False)
    reason = Column(Text)
    current_price = Column(DECIMAL(15, 2))
    target_price = Column(DECIMAL(15, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock")


class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    anomaly_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text)
    current_value = Column(String(50))
    threshold_value = Column(String(50))
    probability = Column(DECIMAL(5, 2))
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock")


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    alert_type = Column(String(20), nullable=False)
    target_price = Column(DECIMAL(15, 2))
    percent_change = Column(DECIMAL(8, 4))
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="alerts")


class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")


class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    symbol = Column(String(20), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    stock = relationship("Stock")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    shares = Column(DECIMAL(15, 4), nullable=False)
    avg_cost = Column(DECIMAL(15, 2), nullable=False)
    current_price = Column(DECIMAL(15, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    stock = relationship("Stock")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(Date, nullable=False)
    open_price = Column(DECIMAL(15, 2))
    high_price = Column(DECIMAL(15, 2))
    low_price = Column(DECIMAL(15, 2))
    close_price = Column(DECIMAL(15, 2))
    volume = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="price_history")


class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    symbol = Column(String(20), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    source = Column(String(100))
    url = Column(Text)
    sentiment = Column(String(20))
    published_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    stock = relationship("Stock", back_populates="news")

