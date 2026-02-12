-- Financial Intel Database Schema for MySQL
-- Database: financial_intel

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar TEXT,
    preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Stocks Table
CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    exchange VARCHAR(50),
    current_price DECIMAL(15, 2),
    price_change DECIMAL(15, 2),
    price_change_percent DECIMAL(10, 4),
    market_cap DECIMAL(20, 2),
    pe_ratio DECIMAL(10, 2),
    eps DECIMAL(10, 4),
    dividend_yield DECIMAL(8, 4),
    volume BIGINT,
    avg_volume BIG_INT,
    high52w DECIMAL(15, 2),
    low_52w DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_sector (sector)
);

-- Fundamental Data Table
CREATE TABLE IF NOT EXISTS fundamental_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    period VARCHAR(20) NOT NULL,
    fiscal_year INT,
    revenue DECIMAL(20, 2),
    cost_of_revenue DECIMAL(20, 2),
    gross_profit DECIMAL(20, 2),
    operating_expenses DECIMAL(20, 2),
    operating_income DECIMAL(20, 2),
    net_income DECIMAL(20, 2),
    eps DECIMAL(10, 4),
    total_assets DECIMAL(20, 2),
    total_liabilities DECIMAL(20, 2),
    shareholders_equity DECIMAL(20, 2),
    cash_and_equivalents DECIMAL(20, 2),
    short_term_investments DECIMAL(20, 2),
    long_term_debt DECIMAL(20, 2),
    operating_cash_flow DECIMAL(20, 2),
    capital_expenditures DECIMAL(20, 2),
    free_cash_flow DECIMAL(20, 2),
    dividend_payments DECIMAL(20, 2),
    share_repurchases DECIMAL(20, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_fundamental (stock_id, period),
    INDEX idx_period (period)
);

-- Financial Ratios Table
CREATE TABLE IF NOT EXISTS financial_ratios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    period VARCHAR(20) NOT NULL,
    pe_ratio DECIMAL(10, 2),
    pb_ratio DECIMAL(10, 2),
    ps_ratio DECIMAL(10, 2),
    roe DECIMAL(10, 4),
    roa DECIMAL(10, 4),
    current_ratio DECIMAL(10, 4),
    debt_to_equity DECIMAL(10, 4),
    profit_margin DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_ratios (stock_id, period)
);

-- Growth Metrics Table
CREATE TABLE IF NOT EXISTS growth_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    period VARCHAR(20) NOT NULL,
    revenue_growth DECIMAL(10, 4),
    eps_growth DECIMAL(10, 4),
    revenue_cagr DECIMAL(10, 4),
    eps_cagr DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_growth (stock_id, period)
);

-- Options Data Table
CREATE TABLE IF NOT EXISTS options_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    expiry_date DATE NOT NULL,
    strike_price DECIMAL(15, 2) NOT NULL,
    option_type ENUM('call', 'put') NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last_price DECIMAL(10, 2),
    volume BIGINT,
    open_interest BIGINT,
    implied_volatility DECIMAL(8, 4),
    delta DECIMAL(8, 4),
    gamma DECIMAL(8, 4),
    theta DECIMAL(8, 4),
    vega DECIMAL(8, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    INDEX idx_stock_expiry (stock_id, expiry_date),
    INDEX idx_strike (strike_price)
);

-- Institutional Holdings Table
CREATE TABLE IF NOT EXISTS institutional_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    holder_name VARCHAR(255) NOT NULL,
    shares_held BIGINT,
    ownership_percent DECIMAL(8, 4),
    value DECIMAL(20, 2),
    quarter_reported DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    INDEX idx_holder (holder_name),
    INDEX idx_quarter (quarter_reported)
);

-- Short Interest Table
CREATE TABLE IF NOT EXISTS short_interest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    date DATE NOT NULL,
    shares_shorted BIGINT,
    days_to_cover DECIMAL(10, 2),
    short_percent DECIMAL(8, 4),
    squeeze_potential ENUM('Low', 'Medium', 'High', 'Very High'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_short (stock_id, date),
    INDEX idx_date (date)
);

-- Earnings Calendar Table
CREATE TABLE IF NOT EXISTS earnings_calendar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    earnings_date DATE NOT NULL,
    estimate DECIMAL(10, 4),
    surprise DECIMAL(10, 4),
    fiscal_quarter INT,
    fiscal_year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_earnings (stock_id, earnings_date),
    INDEX idx_date (earnings_date)
);

-- Trade Ideas Table
CREATE TABLE IF NOT EXISTS trade_ideas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    author_name VARCHAR(255) NOT NULL,
    author_avatar VARCHAR(10),
    symbol VARCHAR(20) NOT NULL,
    idea_type ENUM('LONG', 'SHORT') NOT NULL,
    title VARCHAR(500) NOT NULL,
    summary TEXT,
    analysis TEXT,
    entry_price DECIMAL(15, 2),
    current_price DECIMAL(15, 2),
    target_price DECIMAL(15, 2),
    stop_loss DECIMAL(15, 2),
    risk_reward VARCHAR(20),
    timeframe VARCHAR(50),
    confidence INT,
    ai_score INT,
    sentiment ENUM('bullish', 'bearish', 'neutral'),
    upvotes INT DEFAULT 0,
    downvotes INT DEFAULT 0,
    comments INT DEFAULT 0,
    tags JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_type (idea_type),
    INDEX idx_sentiment (sentiment),
    INDEX idx_timestamp (timestamp)
);

-- AI Signals Table
CREATE TABLE IF NOT EXISTS ai_signals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    symbol VARCHAR(20) NOT NULL,
    signal ENUM('BUY', 'SELL', 'HOLD', 'WATCH', 'NEUTRAL') NOT NULL,
    confidence DECIMAL(5, 2) NOT NULL,
    reason TEXT,
    current_price DECIMAL(15, 2),
    target_price DECIMAL(15, 2),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_signal (signal),
    INDEX idx_timestamp (timestamp)
);

-- Anomalies Table
CREATE TABLE IF NOT EXISTS anomalies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    symbol VARCHAR(20) NOT NULL,
    anomaly_type ENUM('volume_spike', 'price_movement', 'options_activity', 'sentiment_shift', 'volatility_surge') NOT NULL,
    severity ENUM('low', 'medium', 'high') NOT NULL,
    description TEXT,
    current_value VARCHAR(50),
    threshold_value VARCHAR(50),
    probability DECIMAL(5, 2),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_type (anomaly_type),
    INDEX idx_severity (severity),
    INDEX idx_timestamp (timestamp)
);

-- Price Alerts Table
CREATE TABLE IF NOT EXISTS price_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    alert_type ENUM('above', 'below', 'change') NOT NULL,
    target_price DECIMAL(15, 2),
    percent_change DECIMAL(8, 4),
    is_active BOOLEAN DEFAULT TRUE,
    is_triggered BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_active (is_active)
);

-- Watchlists Table
CREATE TABLE IF NOT EXISTS watchlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

-- Watchlist Items Table
CREATE TABLE IF NOT EXISTS watchlist_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    watchlist_id INT NOT NULL,
    stock_id INT,
    symbol VARCHAR(20) NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE SET NULL,
    UNIQUE KEY unique_watchlist_item (watchlist_id, symbol)
);

-- Portfolio Holdings Table
CREATE TABLE IF NOT EXISTS portfolio_holdings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    stock_id INT,
    symbol VARCHAR(20) NOT NULL,
    shares DECIMAL(15, 4) NOT NULL,
    avg_cost DECIMAL(15, 2) NOT NULL,
    current_price DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_symbol (symbol)
);

-- Price History Table
CREATE TABLE IF NOT EXISTS price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(15, 2),
    high_price DECIMAL(15, 2),
    low_price DECIMAL(15, 2),
    close_price DECIMAL(15, 2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE KEY unique_price (stock_id, date),
    INDEX idx_date (date)
);

-- News Table
CREATE TABLE IF NOT EXISTS news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT,
    symbol VARCHAR(20),
    title VARCHAR(500) NOT NULL,
    content TEXT,
    source VARCHAR(100),
    url TEXT,
    sentiment ENUM('positive', 'negative', 'neutral'),
    published_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_sentiment (sentiment),
    INDEX idx_published (published_at)
);

