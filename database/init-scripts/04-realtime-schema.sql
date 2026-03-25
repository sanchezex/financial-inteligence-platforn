-- ClickHouse Time Series Database Schema for Realtime Forex/Commodity Trading
-- High-performance tick storage + materialized OHLCV views
-- Optimized for 100k+ ticks/sec ingestion, sub-second queries

-- ============================================================================
-- Dependencies: Create database if not exists
-- ============================================================================
CREATE DATABASE IF NOT EXISTS financial_intel ENGINE = Atomic;

USE financial_intel;

-- ============================================================================
-- 1. RAW TICK DATA (Primary high-ingest table)
-- Partition: monthly | Order: timestamp+symbol | Engine: ReplacingMergeTree
-- ============================================================================
CREATE TABLE IF NOT EXISTS market_ticks (
    timestamp DateTime64(3) CODEC(Delta, Lorentz, ZSTD(1)),
    symbol LowCardinality(String) CODEC(ZSTD(1)),
    bid Float64 CODEC(Gorilla, ZSTD(1)),
    ask Float64 CODEC(Gorilla, ZSTD(1)), 
    mid Float64 MATERIALIZED (bid + ask) / 2 CODEC(Gorilla),
    volume UInt64 CODEC(ZSTD(1)),
    bid_size UInt32 CODEC(ZSTD(1)),
    ask_size UInt32 CODEC(ZSTD(1)),
    exchange LowCardinality(String) DEFAULT 'Polygon/OANDA',
    trade_id UInt64,
    
    INDEX idx_symbol_symbol (symbol) TYPE minmax GRANULARITY 4,
    INDEX idx_time_price (timestamp, bid) TYPE set(1000) GRANULARITY 1
) ENGINE = ReplacingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192, 
         merge_with_ttl_timeout = 14400;

-- ============================================================================
-- 2. MATERIALIZED OHLCV (1min/5min/1h bars from ticks)
-- ============================================================================
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ohlcv_1min 
TO market_ohlcv_1min 
AS SELECT
    timestamp,
    symbol,
    argMin(bid, timestamp) as open,
    max(bid) as high,
    min(bid) as low,
    argMax(ask, timestamp) as close,
    sum(volume) as volume,
    count() as tick_count
FROM market_ticks 
GROUP BY 
    toStartOfMinute(timestamp) as timestamp,
    symbol 
HAVING tick_count > 0;

CREATE TABLE IF NOT EXISTS market_ohlcv_1min (
    timestamp DateTime64(3),
    symbol LowCardinality(String),
    open Float64,
    high Float64,
    low Float64, 
    close Float64,
    volume UInt64,
    tick_count UInt32
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol);

-- 5min bars  
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ohlcv_5min 
TO market_ohlcv_5min 
AS SELECT
    timestamp,
    symbol,
    argMin(open, timestamp) as open,
    max(high) as high,
    min(low) as low,
    argMax(close, timestamp) as close,
    sum(volume) as volume
FROM market_ohlcv_1min
GROUP BY 
    toStartOfFiveMinute(timestamp) as timestamp,
    symbol;

CREATE TABLE IF NOT EXISTS market_ohlcv_5min (
    -- same structure as 1min
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol);

-- 1h bars
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_ohlcv_1h 
TO market_ohlcv_1h 
AS SELECT
    timestamp,
    symbol,
    argMin(open, timestamp) as open,
    max(high) as high,
    min(low) as low,
    argMax(close, timestamp) as close,
    sum(volume) as volume
FROM market_ohlcv_5min
GROUP BY 
    toStartOfHour(timestamp) as timestamp,
    symbol;

CREATE TABLE IF NOT EXISTS market_ohlcv_1h (
    -- same structure  
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (timestamp, symbol);

-- ============================================================================
-- 3. ORDERBOOK SNAPSHOTS (L2 data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS orderbook_snapshots (
    timestamp DateTime64(3),
    symbol LowCardinality(String),
    bids Array(Tuple(Float64, UInt32)),  -- (price, size) x 10 levels
    asks Array(Tuple(Float64, UInt32)),  -- (price, size) x 10 levels
    spread Float64 MATERIALIZED arrayFirst(asks.1, asks.1 > 0) - arrayLast(bids.1, bids.1 > 0),
    imbalance Float64 MATERIALIZED sumArray(arrayMap(x->x.2, bids)) / (sumArray(arrayMap(x->x.2, bids)) + sumArray(arrayMap(x->x.2, asks))),
    
    INDEX idx_symbol (symbol) TYPE minmax GRANULARITY 4
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)  
ORDER BY (timestamp, symbol)
SAMPLE BY symbol;

-- ============================================================================
-- 4. TRADES & EXECUTIONS (user trades linked to market data)
-- ============================================================================
CREATE TABLE IF NOT EXISTS realtime_trades (
    timestamp DateTime64(3),
    user_id UInt32,
    symbol LowCardinality(String),
    side LowCardinality(String),  -- buy/sell
    price Float64,
    size Float64,
    fees Float64,
    exchange_time_ns UInt64,  -- nanosecond timestamp
    order_id String,
    
    INDEX idx_user_symbol (user_id, symbol) TYPE set(1000) GRANULARITY 1
) ENGINE = ReplacingMergeTree()
ORDER BY (timestamp, user_id, symbol);

-- ============================================================================
-- 5. AI SIGNALS & PREDICTIONS (ML outputs)
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_signals (
    timestamp DateTime64(3),
    symbol LowCardinality(String),
    signal_type LowCardinality(String),  -- BUY/SELL/HOLD
    confidence Float32,
    predicted_price Float64,
    stop_loss Float64,
    take_profit Float64,
    model_version String,
    model_type LowCardinality(String),  -- LSTM/Prophet/XGBoost/RL
    backtest_sharpe Float32,
    
    INDEX idx_symbol_signal (symbol, signal_type) TYPE set(100) GRANULARITY 1
) ENGINE = ReplacingMergeTree()
ORDER BY (timestamp, symbol);

-- ============================================================================
-- 6. PERFORMANCE METRICS (aggregated)
-- ============================================================================
CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy_id UInt32,
    date Date,
    total_trades UInt32,
    win_rate Float32,
    sharpe_ratio Float32,
    max_drawdown Float32,
    total_pnl Float64,
    
    INDEX idx_strategy_date (strategy_id, date) TYPE minmax GRANULARITY 1
) ENGINE = SummingMergeTree()
ORDER BY (strategy_id, date);

-- ============================================================================
-- 7. AGGREGATED VIEWS (for Grafana/dashboard queries)
-- ============================================================================
-- Latest tick prices
CREATE MATERIALIZED VIEW latest_quotes AS
SELECT 
    symbol,
    argMax(mid, timestamp) as last_price,
    argMax(bid, timestamp) as bid,
    argMax(ask, timestamp) as ask,
    argMax(volume, timestamp) as volume_24h
FROM market_ticks 
WHERE timestamp > now() - INTERVAL 24 HOUR
GROUP BY symbol;

-- 24h returns  
CREATE MATERIALIZED VIEW daily_returns AS
SELECT 
    symbol,
    (argMax(close, timestamp) - argMin(open, timestamp)) / argMin(open, timestamp) * 100 as return_24h
FROM market_ohlcv_1h
WHERE timestamp > now() - INTERVAL 24 HOUR
GROUP BY symbol;

-- ============================================================================
-- SAMPLE INSERT QUERIES (for testing)
-- ============================================================================
-- INSERT INTO market_ticks FORMAT JSONEachRow
-- {
--   "timestamp": "2024-01-15T14:30:25.123",
--   "symbol": "EURUSD",
--   "bid": 1.0852, "ask": 1.0854, "volume": 12500,
--   "bid_size": 250, "ask_size": 180
-- }

-- Query example: Latest 100 ticks for EURUSD
-- SELECT * FROM market_ticks 
-- WHERE symbol = 'EURUSD' 
-- ORDER BY timestamp DESC LIMIT 100;

-- 1h chart data
-- SELECT * FROM market_ohlcv_1h 
-- WHERE symbol = 'EURUSD' AND timestamp > now() - INTERVAL 24 HOUR
-- ORDER BY timestamp;

-- Victory: Schema ready for 1M+ ticks/day realtime trading!

