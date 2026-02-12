# Database session configuration for MySQL
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from app.core.config import settings

# Create MySQL engine (for MySQL database)
engine = create_engine(
    settings.MYSQL_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Import all models to ensure they're registered
    from app.db.models import Base, User, Stock, FundamentalData, FinancialRatio, GrowthMetric, OptionData, InstitutionalHolding, ShortInterest, EarningsCalendar, TradeIdea, AISignal, Anomaly, PriceAlert, Watchlist, WatchlistItem, PortfolioHolding, PriceHistory, News
    
    # Create all tables
    Base.metadata.create_all(bind=engine)

