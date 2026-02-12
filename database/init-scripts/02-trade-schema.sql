-- Trade Features Schema for Financial Intelligence Platform
-- Database: financial_intel

-- ============================================================================
-- Extended Users Table (adds trading fields)
-- ============================================================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS paper_trading_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS paper_account_balance DECIMAL(20, 2) DEFAULT 100000.00;
ALTER TABLE users ADD COLUMN IF NOT EXISTS max_position_size DECIMAL(5, 2) DEFAULT 25.00;
ALTER TABLE users ADD COLUMN IF NOT EXISTS max_portfolio_risk DECIMAL(5, 2) DEFAULT 10.00;
ALTER TABLE users ADD COLUMN IF NOT EXISTS allow_short_selling BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS allow_options BOOLEAN DEFAULT FALSE;

-- ============================================================================
-- Orders Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- Order specifications
    order_type ENUM('market', 'limit', 'stop', 'stop_limit', 'trailing_stop') NOT NULL,
    side ENUM('buy', 'sell') NOT NULL,
    quantity DECIMAL(15, 6) NOT NULL,
    
    -- Price specifications
    limit_price DECIMAL(15, 4) NULL,
    stop_price DECIMAL(15, 4) NULL,
    trailing_amount DECIMAL(10, 4) NULL,
    trailing_percent DECIMAL(5, 2) NULL,
    
    -- Time in force
    time_in_force VARCHAR(10) DEFAULT 'day',
    
    -- Order status
    status ENUM('pending', 'submitted', 'filled', 'partial', 'cancelled', 'rejected') DEFAULT 'pending',
    filled_quantity DECIMAL(15, 6) DEFAULT 0,
    remaining_quantity DECIMAL(15, 6) NULL,
    avg_fill_price DECIMAL(15, 4) NULL,
    
    -- Commission and fees
    commission DECIMAL(10, 4) DEFAULT 0,
    
    -- Paper trading flag
    is_paper BOOLEAN DEFAULT TRUE,
    
    -- Strategy association
    strategy_id INT NULL,
    
    -- Reason for rejection
    reject_reason TEXT NULL,
    
    -- Timestamps
    submitted_at DATETIME NULL,
    expired_at DATETIME NULL,
    cancelled_at DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_status (status),
    INDEX idx_order_id (order_id),
    INDEX idx_created_at (created_at)
);

-- ============================================================================
-- Trades Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS trades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Trade identification
    order_id INT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- Trade details
    trade_type VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    quantity DECIMAL(15, 6) NOT NULL,
    execution_price DECIMAL(15, 4) NOT NULL,
    
    -- Order details
    order_type VARCHAR(20) NULL,
    limit_price DECIMAL(15, 4) NULL,
    stop_price DECIMAL(15, 4) NULL,
    
    -- Execution details
    commission DECIMAL(10, 4) DEFAULT 0,
    fees DECIMAL(10, 4) DEFAULT 0,
    slippage DECIMAL(10, 4) DEFAULT 0,
    execution_time DATETIME NULL,
    
    -- Cost basis
    total_value DECIMAL(20, 4) NOT NULL,
    total_cost DECIMAL(20, 4) NOT NULL,
    
    -- Paper trading flag
    is_paper BOOLEAN DEFAULT TRUE,
    
    -- Notes and tags
    notes TEXT NULL,
    tags JSON NULL,
    
    -- Timestamps
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_executed_at (executed_at)
);

-- ============================================================================
-- Positions Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    
    -- Position details
    side VARCHAR(10) DEFAULT 'long',
    quantity DECIMAL(15, 6) NOT NULL,
    
    -- Cost basis
    avg_entry_price DECIMAL(15, 4) NOT NULL,
    total_cost DECIMAL(20, 4) NOT NULL,
    
    -- Market data
    current_price DECIMAL(15, 4) NULL,
    market_value DECIMAL(20, 4) NULL,
    
    -- P&L calculations
    unrealized_pnl DECIMAL(20, 4) NULL,
    unrealized_pnl_percent DECIMAL(10, 4) NULL,
    
    -- Day's P&L
    day_change DECIMAL(20, 4) NULL,
    day_change_percent DECIMAL(10, 4) NULL,
    
    -- Paper trading flag
    is_paper BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint for user-symbol combination
    UNIQUE KEY unique_user_symbol (user_id, symbol),
    INDEX idx_user_symbol (user_id, symbol)
);

-- ============================================================================
-- Portfolio History Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS portfolio_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    
    -- Portfolio values
    total_value DECIMAL(20, 4) NOT NULL,
    cash_balance DECIMAL(20, 4) DEFAULT 0,
    securities_value DECIMAL(20, 4) DEFAULT 0,
    
    -- P&L
    unrealized_pnl DECIMAL(20, 4) DEFAULT 0,
    realized_pnl DECIMAL(20, 4) DEFAULT 0,
    day_pnl DECIMAL(20, 4) DEFAULT 0,
    
    -- Portfolio metrics snapshot
    day_return DECIMAL(10, 6) NULL,
    total_return DECIMAL(10, 6) NULL,
    
    -- Risk metrics snapshot
    portfolio_beta DECIMAL(8, 4) NULL,
    portfolio_var DECIMAL(10, 4) NULL,
    
    -- Cash flows
    deposits DECIMAL(20, 4) DEFAULT 0,
    withdrawals DECIMAL(20, 4) DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint for user-date combination
    UNIQUE KEY unique_user_date (user_id, date),
    INDEX idx_user_date (user_id, date),
    INDEX idx_date (date)
);

-- ============================================================================
-- Trade Journal Entries Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS trade_journal_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Entry identification
    trade_id INT NULL,
    symbol VARCHAR(20) NULL,
    
    -- Entry type
    entry_type ENUM('pre_trade', 'post_trade', 'daily_notes', 'lesson_learned', 'strategy_review') NOT NULL,
    
    -- Entry content
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    
    -- Pre-trade fields
    entry_plan TEXT NULL,
    entry_reason TEXT NULL,
    expected_outcome TEXT NULL,
    risk_management_plan TEXT NULL,
    
    -- Post-trade fields
    actual_outcome TEXT NULL,
    what_went_well TEXT NULL,
    what_could_be_improved TEXT NULL,
    
    -- Emotion tracking
    emotion_before VARCHAR(50) NULL,
    emotion_after VARCHAR(50) NULL,
    emotion_intensity INT NULL,
    
    -- Results
    pnl DECIMAL(20, 4) NULL,
    success BOOLEAN NULL,
    
    -- Tags and categories
    tags JSON NULL,
    strategies_used JSON NULL,
    
    -- Timestamps
    entry_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trade_id) REFERENCES trades(id) ON DELETE SET NULL,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_symbol (symbol),
    INDEX idx_entry_type (entry_type),
    INDEX idx_entry_date (entry_date)
);

-- ============================================================================
-- Strategies Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS strategies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Strategy details
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    strategy_type VARCHAR(50) NULL,
    
    -- Rules configuration (JSON)
    entry_rules JSON NULL,
    exit_rules JSON NULL,
    position_sizing JSON NULL,
    risk_rules JSON NULL,
    
    -- Backtest results
    backtest_enabled BOOLEAN DEFAULT FALSE,
    backtest_results JSON NULL,
    
    -- Performance metrics
    total_trades INT DEFAULT 0,
    win_rate DECIMAL(5, 2) NULL,
    profit_factor DECIMAL(8, 4) NULL,
    avg_trade_pnl DECIMAL(15, 4) NULL,
    max_drawdown DECIMAL(5, 2) NULL,
    
    -- Active status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id),
    INDEX idx_strategy_type (strategy_type)
);

-- ============================================================================
-- Risk Limits Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS risk_limits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    
    -- Limit type
    limit_type VARCHAR(50) NOT NULL,
    
    -- Limit configuration
    limit_name VARCHAR(100) NOT NULL,
    limit_value DECIMAL(20, 4) NOT NULL,
    limit_unit VARCHAR(20) NULL,
    
    -- Actions when limit breached
    alert_enabled BOOLEAN DEFAULT TRUE,
    auto_close_enabled BOOLEAN DEFAULT FALSE,
    notification_channel VARCHAR(50) DEFAULT 'app',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint
    UNIQUE KEY unique_user_limit (user_id, limit_type),
    INDEX idx_user_limit_type (user_id, limit_type)
);

-- ============================================================================
-- Paper Trading Accounts Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS paper_trading_accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    
    -- Account settings
    initial_balance DECIMAL(20, 2) DEFAULT 100000.00,
    current_balance DECIMAL(20, 2) DEFAULT 100000.00,
    buying_power DECIMAL(20, 2) DEFAULT 100000.00,
    
    -- Performance metrics
    total_pnl DECIMAL(20, 4) DEFAULT 0,
    total_return DECIMAL(10, 4) DEFAULT 0,
    day_pnl DECIMAL(20, 4) DEFAULT 0,
    day_return DECIMAL(10, 4) DEFAULT 0,
    
    -- Trading statistics
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0,
    
    -- Current drawdown
    peak_value DECIMAL(20, 2) DEFAULT 100000.00,
    current_drawdown DECIMAL(10, 4) DEFAULT 0,
    max_drawdown DECIMAL(10, 4) DEFAULT 0,
    
    -- Last updated
    last_trade_date DATETIME NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign key to users
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Indexes
    INDEX idx_user_id (user_id)
);

-- ============================================================================
-- Updated Orders Table - Add strategy foreign key
-- ============================================================================
ALTER TABLE orders ADD COLUMN IF NOT EXISTS strategy_id INT NULL;
ALTER TABLE orders ADD CONSTRAINT IF NOT EXISTS fk_order_strategy 
    FOREIGN KEY (strategy_id) REFERENCES strategies(id) ON DELETE SET NULL;

-- ============================================================================
-- Views for Common Queries
-- ============================================================================

-- View: Active Positions Summary
CREATE OR REPLACE VIEW v_active_positions AS
SELECT 
    user_id,
    symbol,
    side,
    SUM(quantity) as total_quantity,
    SUM(total_cost) as total_cost,
    AVG(avg_entry_price) as avg_price,
    COUNT(*) as position_count
FROM positions
WHERE quantity > 0
GROUP BY user_id, symbol, side;

-- View: Portfolio Performance Summary
CREATE OR REPLACE VIEW v_portfolio_performance AS
SELECT 
    ph.user_id,
    ph.date,
    ph.total_value,
    ph.day_pnl,
    ph.day_return,
    ph.total_return,
    ph.portfolio_beta,
    ph.portfolio_var,
    ph.unrealized_pnl,
    ph.realized_pnl
FROM portfolio_history ph
INNER JOIN (
    SELECT user_id, MAX(date) as max_date
    FROM portfolio_history
    GROUP BY user_id
) latest ON ph.user_id = latest.user_id AND ph.date = latest.max_date;

-- View: Trade Statistics
CREATE OR REPLACE VIEW v_trade_statistics AS
SELECT 
    user_id,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    AVG(pnl) as avg_pnl,
    AVG(CASE WHEN pnl > 0 THEN pnl END) as avg_win,
    AVG(CASE WHEN pnl < 0 THEN pnl END) as avg_loss,
    SUM(pnl) as total_pnl
FROM (
    SELECT 
        t.user_id,
        t.executed_at,
        CASE WHEN t.side = 'buy' 
            THEN (execution_price - o.limit_price) * t.quantity 
            ELSE (o.limit_price - execution_price) * t.quantity 
        END as pnl
    FROM trades t
    LEFT JOIN orders o ON t.order_id = o.id
) trade_pnl
GROUP BY user_id;

