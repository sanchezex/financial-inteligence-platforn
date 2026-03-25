-- ============================================================================
-- Satellite-Based Forex Trading Signals Schema
-- Database: financial_intel
-- ============================================================================

-- ============================================================================
-- Satellite Data Types Enum
-- ============================================================================
CREATE TABLE IF NOT EXISTS satellite_data_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    historical_accuracy DECIMAL(5,2),
    typical_lead_time_minutes INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert satellite data types
INSERT INTO satellite_data_types (type_name, description, historical_accuracy, typical_lead_time_minutes) VALUES
('port_activity', 'Satellite imagery of major global ports tracking vessel counts, container density, and port utilization', 78.00, 30),
('shipping_route', 'Tracking of major shipping lanes and freight activity across oceans', 72.00, 45),
('commodity_storage', 'Monitoring of petroleum, grain, and other commodity storage facilities', 75.00, 60),
('agricultural', 'Crop condition and harvest activity monitoring for major agricultural regions', 68.00, 120),
('industrial', 'Factory and industrial facility activity monitoring via night lights and satellite imagery', 71.00, 90);

-- ============================================================================
-- Satellite Data Regions
-- ============================================================================
CREATE TABLE IF NOT EXISTS satellite_regions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    region_code VARCHAR(20) NOT NULL UNIQUE,
    region_name VARCHAR(100) NOT NULL,
    satellite_type_id INT NOT NULL,
    correlated_forex_pairs JSON,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (satellite_type_id) REFERENCES satellite_data_types(id) ON DELETE CASCADE
);

-- Insert regions
INSERT INTO satellite_regions (region_code, region_name, satellite_type_id, correlated_forex_pairs, latitude, longitude) VALUES
('CNSGH', 'Shanghai', 1, '["USD/CNY", "AUD/USD"]', 31.2304, 121.4737),
('SGSIN', 'Singapore', 1, '["USD/SGD", "AUD/USD"]', 1.3521, 103.8198),
('USLAX', 'Los Angeles', 1, '["USD/CAD", "USD/MXN"]', 33.7405, -118.2720),
('NLROT', 'Rotterdam', 1, '["EUR/USD", "GBP/USD"]', 51.9244, 4.4777),
('DEHAM', 'Hamburg', 1, '["EUR/USD", "EUR/GBP"]', 53.5511, 9.9937),
('SCS', 'South China Sea', 2, '["USD/CNY", "USD/JPY"]', 20.0, 115.0),
('MED', 'Mediterranean', 2, '["EUR/TRY", "EUR/GBP"]', 35.0, 18.0),
('ATL', 'Atlantic', 2, '["GBP/USD", "EUR/USD"]', 40.0, -40.0),
('PAC', 'Pacific', 2, '["USD/JPY", "AUD/USD"]', 0.0, -150.0),
('USHU', 'Houston', 3, '["USD/CAD", "USD/MXN"]', 29.7604, -95.3698),
('AEFJR', 'Fujairah', 3, '["USD/AED", "EUR/USD"]', 25.1288, 56.3265),
('USMW', 'US Midwest', 4, '["USD/CAD", "USD/MXN"]', 40.0, -90.0),
('BRSAO', 'Brazil', 4, '["USD/BRL"]', -23.5505, -46.6333),
('CNEC', 'China East Coast', 5, '["USD/CNY", "USD/JPY"]', 30.0, 120.0),
('DE', 'Germany', 5, '["EUR/USD", "EUR/GBP"]', 51.1657, 10.4515),
('USGC', 'US Gulf Coast', 5, '["USD/CAD", "USD/MXN"]', 25.0, -90.0),
('JP', 'Japan', 5, '["USD/JPY", "AUD/USD"]', 36.2048, 138.2529);

-- ============================================================================
-- Satellite Raw Data
-- ============================================================================
CREATE TABLE IF NOT EXISTS satellite_data (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    region_id INT NOT NULL,
    satellite_type_id INT NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    indicator_value DECIMAL(20, 4) NOT NULL,
    baseline_value DECIMAL(20, 4),
    change_from_baseline DECIMAL(10, 4),
    unit VARCHAR(50),
    image_timestamp TIMESTAMP NOT NULL,
    processing_status ENUM('raw', 'processed', 'analyzed') DEFAULT 'raw',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (region_id) REFERENCES satellite_regions(id) ON DELETE CASCADE,
    FOREIGN KEY (satellite_type_id) REFERENCES satellite_data_types(id) ON DELETE CASCADE,
    INDEX idx_region_timestamp (region_id, image_timestamp),
    INDEX idx_type_timestamp (satellite_type_id, image_timestamp),
    INDEX idx_indicator (indicator_name)
);

-- ============================================================================
-- Forex Signals Table
-- ============================================================================
CREATE TABLE IF NOT EXISTS forex_signals (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    signal_id VARCHAR(50) NOT NULL UNIQUE,
    forex_pair VARCHAR(20) NOT NULL,
    signal_type ENUM('STRONG_BUY', 'BUY', 'WATCH', 'SELL', 'STRONG_SELL') NOT NULL,
    
    -- Price levels
    entry_price DECIMAL(15, 6) NOT NULL,
    take_profit DECIMAL(15, 6),
    stop_loss DECIMAL(15, 6),
    
    -- Signal metadata
    confidence DECIMAL(5, 2) NOT NULL,
    lead_time_minutes INT NOT NULL,
    risk_level ENUM('low', 'medium', 'high') DEFAULT 'medium',
    
    -- Satellite source information
    satellite_type_id INT NOT NULL,
    region_id INT NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    indicator_value DECIMAL(20, 4),
    indicator_change DECIMAL(10, 4),
    
    -- AI Analysis
    reasoning TEXT,
    market_reaction_expected VARCHAR(255),
    
    -- Status
    status ENUM('active', 'triggered', 'closed', 'expired') DEFAULT 'active',
    
    -- Outcome tracking
    actual_entry_price DECIMAL(15, 6),
    actual_exit_price DECIMAL(15, 6),
    pnl_pips DECIMAL(10, 4),
    closed_at TIMESTAMP NULL,
    
    -- Timestamps
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (satellite_type_id) REFERENCES satellite_data_types(id) ON DELETE RESTRICT,
    FOREIGN KEY (region_id) REFERENCES satellite_regions(id) ON DELETE RESTRICT,
    
    INDEX idx_forex_pair (forex_pair),
    INDEX idx_signal_type (signal_type),
    INDEX idx_status (status),
    INDEX idx_generated (generated_at),
    INDEX idx_confidence (confidence)
);

-- ============================================================================
-- Signal Performance Tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS signal_performance (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    signal_id VARCHAR(50) NOT NULL,
    forex_pair VARCHAR(20) NOT NULL,
    signal_type VARCHAR(20) NOT NULL,
    entry_price DECIMAL(15, 6) NOT NULL,
    exit_price DECIMAL(15, 6),
    pnl_pips DECIMAL(10, 4),
    holding_time_minutes INT,
    was_successful BOOLEAN,
    accuracy_score DECIMAL(5, 2),
    closed_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_signal (signal_id),
    INDEX idx_pair (forex_pair),
    INDEX idx_closed (closed_at)
);

-- ============================================================================
-- Satellite-Market Correlation
-- ============================================================================
CREATE TABLE IF NOT EXISTS satellite_market_correlations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    satellite_type_id INT NOT NULL,
    region_id INT NOT NULL,
    forex_pair VARCHAR(20) NOT NULL,
    correlation_strength DECIMAL(5, 4),
    lead_time_minutes INT,
    success_rate DECIMAL(5, 4),
    average_move_pips DECIMAL(10, 4),
    sample_size INT,
    lookback_period_days INT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (satellite_type_id) REFERENCES satellite_data_types(id) ON DELETE CASCADE,
    FOREIGN KEY (region_id) REFERENCES satellite_regions(id) ON DELETE CASCADE,
    
    UNIQUE KEY unique_correlation (satellite_type_id, region_id, forex_pair)
);

-- ============================================================================
-- Signal Alerts
-- ============================================================================
CREATE TABLE IF NOT EXISTS signal_alerts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    signal_id VARCHAR(50) NOT NULL,
    user_id INT,
    alert_type ENUM('new_signal', 'signal_triggered', 'signal_closed', 'take_profit_hit', 'stop_loss_hit') NOT NULL,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_user_alerts (user_id, is_read, created_at)
);

-- ============================================================================
-- Views
-- ============================================================================

-- View: Active Forex Signals
CREATE OR REPLACE VIEW v_active_forex_signals AS
SELECT 
    fs.*,
    sdt.type_name as satellite_source,
    sr.region_name,
    sr.region_code
FROM forex_signals fs
JOIN satellite_data_types sdt ON fs.satellite_type_id = sdt.id
JOIN satellite_regions sr ON fs.region_id = sr.id
WHERE fs.status = 'active'
AND fs.expires_at > NOW();

-- View: Signal Performance Summary
CREATE OR REPLACE VIEW v_signal_performance_summary AS
SELECT 
    fs.forex_pair,
    fs.signal_type,
    COUNT(*) as total_signals,
    SUM(CASE WHEN sp.was_successful = 1 THEN 1 ELSE 0 END) as winning_signals,
    SUM(CASE WHEN sp.was_successful = 0 THEN 1 ELSE 0 END) as losing_signals,
    AVG(sp.pnl_pips) as avg_pnl_pips,
    AVG(sp.accuracy_score) as avg_accuracy,
    AVG(sp.holding_time_minutes) as avg_holding_time
FROM forex_signals fs
JOIN signal_performance sp ON fs.signal_id = sp.signal_id
WHERE sp.closed_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY fs.forex_pair, fs.signal_type;

-- View: Satellite Source Performance
CREATE OR REPLACE VIEW v_satellite_source_performance AS
SELECT 
    sdt.type_name as satellite_source,
    COUNT(fs.id) as total_signals,
    AVG(fs.confidence) as avg_confidence,
    SUM(CASE WHEN sp.was_successful = 1 THEN 1 ELSE 0 END) / COUNT(*) * 100 as win_rate,
    AVG(sp.pnl_pips) as avg_pnl_pips,
    AVG(fs.lead_time_minutes) as avg_lead_time
FROM satellite_data_types sdt
LEFT JOIN forex_signals fs ON sdt.id = fs.satellite_type_id
LEFT JOIN signal_performance sp ON fs.signal_id = sp.signal_id
GROUP BY sdt.id, sdt.type_name;

