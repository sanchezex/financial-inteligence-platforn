"""
Financial Intelligence Platform - Database Base Models

SQLAlchemy base class and all database models for the financial platform.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    BigInteger, Boolean, Column, DateTime, Float, ForeignKey, 
    Index, Integer, Numeric, String, Text, JSON, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

import uuid

# Create base class
Base = declarative_base()


def generate_uuid() -> uuid.UUID:
    """Generate a new UUID."""
    return uuid.uuid4()


class AssetType(str, Enum):
    """Types of financial assets."""
    STOCK = "stock"
    ETF = "etf"
    FOREX = "forex"
    COMMODITY = "commodity"
    BOND = "bond"
    CRYPTOCURRENCY = "cryptocurrency"
    DERIVATIVE = "derivative"
    INDEX = "index"


class DataSourceType(str, Enum):
    """Types of data sources."""
    EXCHANGE = "exchange"
    DATA_VENDOR = "data_vendor"
    NEWS = "news"
    GOVERNMENT = "government"
    SOCIAL = "social"
    WEBSCRAPE = "webscrape"
    AI_GENERATED = "ai_generated"


class EventType(str, Enum):
    """Types of financial events."""
    EARNINGS = "earnings"
    DIVIDEND = "dividend"
    MACRO_ANNOUNCEMENT = "macro_announcement"
    CENTRAL_BANK = "central_bank"
    GEOPOLITICAL = "geopolitical"
    MERGER = "merger"
    IPO = "ipo"
    ECONOMIC_DATA = "economic_data"
    CUSTOM = "custom"


class SentimentType(str, Enum):
    """Sentiment classification types."""
    VERY_BULLISH = "very_bullish"
    BULLISH = "bullish"
    NEUTRAL = "neutral"
    BEARISH = "bearish"
    VERY_BEARISH = "very_bearish"


# ============================================================================
# Company and Entity Models
# ============================================================================

class Company(Base):
    """Company entity model."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    ticker = Column(String(20), unique=True, nullable=False, index=True)
    exchange = Column(String(50), nullable=True)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    currency = Column(String(10), nullable=True)
    market_cap = Column(Numeric(20, 2), nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("MarketPrice", back_populates="company")
    fundamentals = relationship("FundamentalData", back_populates="company")
    news = relationship("NewsArticle", back_populates="company")


# ============================================================================
# Market Data Models
# ============================================================================

class MarketPrice(Base):
    """Real-time market price data."""
    __tablename__ = "market_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)
    exchange = Column(String(50), nullable=True)
    
    # Price data
    open_price = Column(Numeric(20, 8), nullable=True)
    high_price = Column(Numeric(20, 8), nullable=True)
    low_price = Column(Numeric(20, 8), nullable=True)
    close_price = Column(Numeric(20, 8), nullable=True)
    volume = Column(BigInteger, nullable=True)
    vwap = Column(Numeric(20, 8), nullable=True)
    
    # Additional metrics
    bid_price = Column(Numeric(20, 8), nullable=True)
    ask_price = Column(Numeric(20, 8), nullable=True)
    bid_volume = Column(BigInteger, nullable=True)
    ask_volume = Column(BigInteger, nullable=True)
    spread = Column(Numeric(20, 8), nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    
    # Relationships
    company = relationship("Company", back_populates="prices")
    
    # Indexes
    __table_args__ = (
        Index("idx_market_prices_symbol_timestamp", "symbol", "timestamp"),
        Index("idx_market_prices_asset_type", "asset_type"),
    )


class HistoricalPrice(Base):
    """Historical price data for time-series analysis."""
    __tablename__ = "historical_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)
    exchange = Column(String(50), nullable=True)
    
    # OHLCV data
    open_price = Column(Numeric(20, 8), nullable=False)
    high_price = Column(Numeric(20, 8), nullable=False)
    low_price = Column(Numeric(20, 8), nullable=False)
    close_price = Column(Numeric(20, 8), nullable=False)
    adjusted_close = Column(Numeric(20, 8), nullable=True)
    volume = Column(BigInteger, nullable=True)
    
    # Derived metrics
    returns = Column(Float, nullable=True)
    log_returns = Column(Float, nullable=True)
    
    # Period info
    period = Column(String(10), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Metadata
    data_source = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_historical_prices_symbol_period", "symbol", "period"),
        Index("idx_historical_prices_period_end", "period_end"),
    )


class ForexRate(Base):
    """Foreign exchange rates."""
    __tablename__ = "forex_rates"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    base_currency = Column(String(10), nullable=False, index=True)
    quote_currency = Column(String(10), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, unique=True)
    
    # Rate data
    bid_rate = Column(Numeric(20, 8), nullable=True)
    ask_rate = Column(Numeric(20, 8), nullable=True)
    mid_rate = Column(Numeric(20, 8), nullable=False)
    
    # Change data
    previous_close = Column(Numeric(20, 8), nullable=True)
    change = Column(Numeric(20, 8), nullable=True)
    change_percent = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_forex_rates_currencies", "base_currency", "quote_currency"),
        Index("idx_forex_rates_timestamp", "timestamp"),
    )


class CommodityPrice(Base):
    """Commodity prices (oil, gas, metals, etc.)."""
    __tablename__ = "commodity_prices"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    commodity_type = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    exchange = Column(String(50), nullable=True)
    
    # Price data
    spot_price = Column(Numeric(20, 8), nullable=True)
    futures_price = Column(Numeric(20, 8), nullable=True)
    contract_month = Column(String(10), nullable=True)
    
    # Additional metrics
    open_price = Column(Numeric(20, 8), nullable=True)
    high_price = Column(Numeric(20, 8), nullable=True)
    low_price = Column(Numeric(20, 8), nullable=True)
    close_price = Column(Numeric(20, 8), nullable=True)
    volume = Column(BigInteger, nullable=True)
    
    # Unit info
    unit = Column(String(20), nullable=True)  # barrel, ounce, ton, etc.
    currency = Column(String(10), nullable=True)
    
    # Metadata
    data_source = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_commodity_prices_type_timestamp", "commodity_type", "timestamp"),
    )


# ============================================================================
# Macroeconomic Data Models
# ============================================================================

class MacroIndicator(Base):
    """Macroeconomic indicators (GDP, inflation, etc.)."""
    __tablename__ = "macro_indicators"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    indicator_code = Column(String(50), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # growth, inflation, employment, etc.
    country = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    
    # Description
    description = Column(Text, nullable=True)
    calculation_method = Column(Text, nullable=True)
    frequency = Column(String(20), nullable=True)  # monthly, quarterly, annual
    
    # Unit info
    unit = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MacroDataPoint(Base):
    """Individual macroeconomic data points."""
    __tablename__ = "macro_data_points"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    indicator_id = Column(BigInteger, ForeignKey("macro_indicators.id"), nullable=False)
    
    # Value
    value = Column(Numeric(20, 4), nullable=True)
    previous_value = Column(Numeric(20, 4), nullable=True)
    revised_value = Column(Numeric(20, 4), nullable=True)
    
    # Change metrics
    change = Column(Numeric(20, 4), nullable=True)
    change_percent = Column(Float, nullable=True)
    
    # Comparison to forecast
    forecast = Column(Numeric(20, 4), nullable=True)
    surprise = Column(Numeric(20, 4), nullable=True)
    surprise_percent = Column(Float, nullable=True)
    
    # Period info
    period = Column(String(20), nullable=False)  # 2024-Q1, 2024-01, etc.
    period_start = Column(DateTime, nullable=True)
    period_end = Column(DateTime, nullable=True)
    
    # Release info
    release_date = Column(DateTime, nullable=True)
    next_release = Column(DateTime, nullable=True)
    revision_date = Column(DateTime, nullable=True)
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    indicator = relationship("MacroIndicator")
    
    # Indexes
    __table_args__ = (
        Index("idx_macro_data_indicator_period", "indicator_id", "period"),
        Index("idx_macro_data_release_date", "release_date"),
    )


class CentralBankDecision(Base):
    """Central bank interest rate decisions and policy statements."""
    __tablename__ = "central_bank_decisions"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    central_bank = Column(String(100), nullable=False, index=True)
    
    # Decision details
    decision_date = Column(DateTime, nullable=False, index=True)
    announcement_time = Column(DateTime, nullable=True)
    
    # Interest rates
    interest_rate = Column(Float, nullable=True)
    previous_rate = Column(Float, nullable=True)
    rate_change = Column(Float, nullable=True)
    
    # Policy
    policy_statement = Column(Text, nullable=True)
    meeting_minutes = Column(Text, nullable=True)
    
    # Voting
    hawkish_votes = Column(Integer, nullable=True)
    dovish_votes = Column(Integer, nullable=True)
    
    # Forward guidance
    forward_guidance = Column(Text, nullable=True)
    
    # Impact assessment
    market_reaction = Column(Text, nullable=True)
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# Shipping and Supply Chain Data Models
# ============================================================================

class ShippingRoute(Base):
    """Shipping routes and freight lanes."""
    __tablename__ = "shipping_routes"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    route_code = Column(String(50), nullable=False, unique=True)
    origin_port = Column(String(100), nullable=False)
    destination_port = Column(String(100), nullable=False)
    route_type = Column(String(50), nullable=False)  # container, bulk, tanker
    
    # Distance and time
    distance_nm = Column(Float, nullable=True)  # nautical miles
    transit_time_days = Column(Float, nullable=True)
    
    # Commodities typically shipped
    commodity_types = Column(ARRAY(String), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FreightRate(Base):
    """Freight rates for different shipping routes."""
    __tablename__ = "freight_rates"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    route_id = Column(BigInteger, ForeignKey("shipping_routes.id"), nullable=False)
    
    # Rate data
    rate = Column(Numeric(20, 4), nullable=False)  # $/day or $/container
    rate_unit = Column(String(20), nullable=True)  # per TEU, per day, etc.
    
    # Rate type
    spot_rate = Column(Numeric(20, 4), nullable=True)
    contract_rate = Column(Numeric(20, 4), nullable=True)
    
    # Change
    previous_rate = Column(Numeric(20, 4), nullable=True)
    rate_change = Column(Numeric(20, 4), nullable=True)
    change_percent = Column(Float, nullable=True)
    
    # Index reference
    index_name = Column(String(50), nullable=True)  # BDI, SCFI, etc.
    index_value = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    route = relationship("ShippingRoute")
    
    # Indexes
    __table_args__ = (
        Index("idx_freight_routes_timestamp", "route_id", "timestamp"),
    )


class PortActivity(Base):
    """Port activity and congestion data."""
    __tablename__ = "port_activity"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    port_code = Column(String(20), nullable=False, index=True)
    port_name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=True)
    
    # Activity metrics
    vessels_in_port = Column(Integer, nullable=True)
    vessels_anchored = Column(Integer, nullable=True)
    vessels_awaiting = Column(Integer, nullable=True)
    
    # Congestion metrics
    average_wait_time_hours = Column(Float, nullable=True)
    max_wait_time_hours = Column(Float, nullable=True)
    
    # Throughput
    container_throughput_teu = Column(BigInteger, nullable=True)
    cargo_volume = Column(BigInteger, nullable=True)
    
    # Capacity utilization
    utilization_percent = Column(Float, nullable=True)
    
    # Operational status
    status = Column(String(50), nullable=True)  # normal, congested, severe
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_port_activity_code_timestamp", "port_code", "timestamp"),
    )


# ============================================================================
# News and Events Models
# ============================================================================

class NewsArticle(Base):
    """News articles and press releases."""
    __tablename__ = "news_articles"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Content
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(2000), nullable=False, unique=True)
    
    # Source
    source = Column(String(100), nullable=False, index=True)
    author = Column(String(100), nullable=True)
    
    # Categorization
    categories = Column(ARRAY(String), nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    
    # Entities mentioned
    mentioned_companies = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    mentioned_tickers = Column(ARRAY(String), nullable=True)
    mentioned_countries = Column(ARRAY(String), nullable=True)
    mentioned_commodities = Column(ARRAY(String), nullable=True)
    
    # Sentiment (AI analyzed)
    sentiment = Column(String(20), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    # AI Summary
    ai_summary = Column(Text, nullable=True)
    key_topics = Column(ARRAY(String), nullable=True)
    
    # Timestamps
    published_at = Column(DateTime, nullable=False, index=True)
    scraped_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="news")
    
    # Indexes
    __table_args__ = (
        Index("idx_news_published_at", "published_at"),
        Index("idx_news_source", "source"),
        Index("idx_news_sentiment", "sentiment"),
    )


class EconomicEvent(Base):
    """Scheduled economic events and announcements."""
    __tablename__ = "economic_events"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    event_name = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False, index=True)
    indicator = Column(String(100), nullable=True)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=False, index=True)
    time = Column(String(20), nullable=True)  # UTC time
    timezone = Column(String(50), nullable=True)
    
    # Importance
    importance = Column(Integer, nullable=True)  # 1-3 scale
    market_impact = Column(String(50), nullable=True)  # high, medium, low
    
    # Forecast
    previous_value = Column(Numeric(20, 4), nullable=True)
    forecast = Column(Numeric(20, 4), nullable=True)
    consensus = Column(Text, nullable=True)
    
    # Description
    description = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    relevance = Column(Text, nullable=True)
    
    # Release info
    source = Column(String(100), nullable=True)
    release_url = Column(String(500), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_events_scheduled_date", "scheduled_date"),
        Index("idx_events_country_date", "country", "scheduled_date"),
    )


# ============================================================================
# Fundamental Data Models
# ============================================================================

class FundamentalData(Base):
    """Company fundamental data (financial statements, ratios, etc.)."""
    __tablename__ = "fundamental_data"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Period
    period_type = Column(String(20), nullable=False)  # quarterly, annual
    period_end = Column(DateTime, nullable=False, index=True)
    fiscal_year = Column(Integer, nullable=True)
    fiscal_quarter = Column(Integer, nullable=True)
    
    # Income Statement
    revenue = Column(Numeric(20, 2), nullable=True)
    gross_profit = Column(Numeric(20, 2), nullable=True)
    operating_income = Column(Numeric(20, 2), nullable=True)
    net_income = Column(Numeric(20, 2), nullable=True)
    eps = Column(Numeric(10, 4), nullable=True)
    
    # Balance Sheet
    total_assets = Column(Numeric(20, 2), nullable=True)
    total_liabilities = Column(Numeric(20, 2), nullable=True)
    total_equity = Column(Numeric(20, 2), nullable=True)
    cash = Column(Numeric(20, 2), nullable=True)
    debt = Column(Numeric(20, 2), nullable=True)
    
    # Cash Flow
    operating_cash_flow = Column(Numeric(20, 2), nullable=True)
    investing_cash_flow = Column(Numeric(20, 2), nullable=True)
    financing_cash_flow = Column(Numeric(20, 2), nullable=True)
    free_cash_flow = Column(Numeric(20, 2), nullable=True)
    
    # Key Ratios
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    roa = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    current_ratio = Column(Float, nullable=True)
    gross_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    net_margin = Column(Float, nullable=True)
    
    # Dividends
    dividend_per_share = Column(Numeric(10, 4), nullable=True)
    dividend_yield = Column(Float, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    
    # Growth Rates
    revenue_growth = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="fundamentals")
    
    # Indexes
    __table_args__ = (
        Index("idx_fundamentals_company_period", "company_id", "period_end"),
    )


# ============================================================================
# Analytics and Intelligence Models
# ============================================================================

class Correlation(Base):
    """Asset correlations for different time periods."""
    __tablename__ = "correlations"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Assets
    asset1_type = Column(String(20), nullable=False)
    asset1_symbol = Column(String(20), nullable=False)
    asset2_type = Column(String(20), nullable=False)
    asset2_symbol = Column(String(20), nullable=False)
    
    # Correlation data
    correlation = Column(Float, nullable=True)
    correlation_p_value = Column(Float, nullable=True)
    
    # Period info
    period = Column(String(20), nullable=False)  # daily, weekly, monthly
    lookback_days = Column(Integer, nullable=True)
    
    # Time window
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    calculation_date = Column(DateTime, nullable=False)
    
    # Metadata
    data_source = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (
        Index("idx_correlations_assets_period", "asset1_symbol", "asset2_symbol", "period"),
    )


class AIInsight(Base):
    """AI-generated insights and analysis."""
    __tablename__ = "ai_insights"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Insight details
    insight_type = Column(String(50), nullable=False)  # sentiment, trend, anomaly, prediction
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    
    # Related assets
    related_assets = Column(ARRAY(String), nullable=True)
    related_sectors = Column(ARRAY(String), nullable=True)
    related_countries = Column(ARRAY(String), nullable=True)
    
    # Sentiment and impact
    sentiment = Column(String(20), nullable=True)
    impact_score = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Evidence
    supporting_evidence = Column(JSON, nullable=True)
    related_articles = Column(ARRAY(BigInteger), nullable=True)
    
    # Generation info
    model_used = Column(String(100), nullable=True)
    generation_params = Column(JSON, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Status
    status = Column(String(20), default="active")  # active, expired, reviewed
    reviewed_by = Column(String(100), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index("idx_insights_type", "insight_type"),
        Index("idx_insights_generated", "generated_at"),
        Index("idx_insights_sentiment", "sentiment"),
    )


# ============================================================================
# User and Alert Models
# ============================================================================

class Watchlist(Base):
    """User watchlists."""
    __tablename__ = "watchlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    symbols = Column(ARRAY(String), nullable=True)
    
    # Settings
    alert_enabled = Column(Boolean, default=True)
    refresh_interval_seconds = Column(Integer, default=60)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Alert(Base):
    """User-defined alerts."""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Alert configuration
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(50), nullable=False)  # price, volume, news, macro, correlation
    
    # Conditions
    conditions = Column(JSON, nullable=False)
    condition_logic = Column(String(10), default="AND")  # AND, OR
    
    # Assets
    symbols = Column(ARRAY(String), nullable=True)
    asset_types = Column(ARRAY(String), nullable=True)
    
    # Thresholds
    threshold_value = Column(Numeric(20, 8), nullable=True)
    threshold_direction = Column(String(10), nullable=True)  # above, below, change
    
    # Notifications
    notification_channels = Column(ARRAY(String), nullable=True)  # email, sms, push, webhook
    notification_settings = Column(JSON, nullable=True)
    
    # Schedule
    active_hours = Column(ARRAY(Integer), nullable=True)  # hours of day [0, 23]
    active_days = Column(ARRAY(Integer), nullable=True)  # days of week [0, 6]
    timezone = Column(String(50), default="UTC")
    
    # Status
    status = Column(String(20), default="active")  # active, paused, triggered, expired
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    # Expiration
    expires_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index("idx_alerts_user_status", "user_id", "status"),
    )


class AlertTrigger(Base):
    """Record of triggered alerts."""
    __tablename__ = "alert_triggers"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Trigger details
    triggered_at = Column(DateTime, default=datetime.utcnow, index=True)
    triggered_value = Column(Numeric(20, 8), nullable=True)
    trigger_message = Column(Text, nullable=True)
    
    # Notification status
    notifications_sent = Column(ARRAY(String), nullable=True)
    notifications_failed = Column(ARRAY(String), nullable=True)
    
    # Resolution
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    
    # Relationships
    alert = relationship("Alert")
    
    # Indexes
    __table_args__ = (
        Index("idx_alert_triggers_user_time", "user_id", "triggered_at"),
    )


# ============================================================================
# Data Pipeline Models
# ============================================================================

class DataSource(Base):
    """Configuration for data sources."""
    __tablename__ = "data_sources"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Source details
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)
    provider = Column(String(100), nullable=True)
    
    # Connection info
    base_url = Column(String(500), nullable=True)
    api_key_encrypted = Column(String(500), nullable=True)
    credentials = Column(JSON, nullable=True)
    
    # Configuration
    data_types = Column(ARRAY(String), nullable=True)
    symbols_covered = Column(ARRAY(String), nullable=True)
    
    # Schedule
    update_frequency = Column(String(50), nullable=True)  # real-time, hourly, daily
    schedule_cron = Column(String(100), nullable=True)
    
    # Status
    status = Column(String(20), default="active")  # active, inactive, error
    last_sync = Column(DateTime, nullable=True)
    next_sync = Column(DateTime, nullable=True)
    
    # Metrics
    records_pulled = Column(BigInteger, default=0)
    records_failed = Column(BigInteger, default=0)
    
    # Cost
    monthly_cost = Column(Numeric(10, 2), nullable=True)
    cost_per_record = Column(Float, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DataIngestionLog(Base):
    """Log of data ingestion runs."""
    __tablename__ = "data_ingestion_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    data_source_id = Column(BigInteger, ForeignKey("data_sources.id"), nullable=False)
    
    # Run details
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False)  # running, completed, failed, partial
    
    # Metrics
    records_processed = Column(BigInteger, default=0)
    records_failed = Column(BigInteger, default=0)
    records_deduplicated = Column(BigInteger, default=0)
    
    # Error info
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Data quality
    quality_score = Column(Float, nullable=True)
    quality_issues = Column(JSON, nullable=True)
    
    # Relationships
    data_source = relationship("DataSource")
    
    # Indexes
    __table_args__ = (
        Index("idx_ingestion_source_time", "data_source_id", "started_at"),
        Index("idx_ingestion_status", "status"),
    )

