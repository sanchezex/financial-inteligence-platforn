import React, { useState, useEffect } from 'react';
import './AISignals.css';

function AISignals() {
  const [signalType, setSignalType] = useState('all'); // 'all', 'stocks', 'forex'
  const [filter, setFilter] = useState('all');
  const [selectedSignal, setSelectedSignal] = useState(null);

  // Stock signals (original)
  const [stockSignals, setStockSignals] = useState([
    { id: 1, symbol: 'NVDA', signal: 'BUY', confidence: 87, reason: 'Strong momentum breakout with volume spike', timestamp: '2024-01-15 14:30', target: 520, current: 495, source: 'technical' },
    { id: 2, symbol: 'AAPL', signal: 'HOLD', confidence: 65, reason: 'Consolidating near resistance', timestamp: '2024-01-15 12:15', target: 185, current: 178, source: 'fundamental' },
    { id: 3, symbol: 'TSLA', signal: 'WATCH', confidence: 72, reason: 'Approaching key support level', timestamp: '2024-01-15 10:45', target: 260, current: 245, source: 'technical' },
    { id: 4, symbol: 'MSFT', signal: 'BUY', confidence: 81, reason: 'AI-driven earnings beat expectations', timestamp: '2024-01-15 09:30', target: 400, current: 379, source: 'fundamental' },
    { id: 5, symbol: 'GOOGL', signal: 'NEUTRAL', confidence: 58, reason: 'Mixed technical indicators', timestamp: '2024-01-14 16:20', target: 150, current: 142, source: 'technical' },
  ]);

  // Satellite-based forex signals (new)
  const [forexSignals, setForexSignals] = useState([
    { 
      id: 101, 
      symbol: 'EUR/USD', 
      signal: 'STRONG_BUY', 
      confidence: 92, 
      reason: 'Satellite imagery shows significant increase in Rotterdam port activity - vessel count up 35% from baseline. Historical correlation: 78% of similar signals resulted in EUR/USD movement within 20 minutes.',
      timestamp: '2024-01-15 14:45', 
      entry: 1.0850,
      takeProfit: 1.0895,
      stopLoss: 1.0810,
      source: 'satellite',
      satelliteSource: 'port_activity',
      region: 'Rotterdam',
      leadTime: 20,
      indicator: 'vessel_count',
      indicatorChange: 35.2
    },
    { 
      id: 102, 
      symbol: 'GBP/USD', 
      signal: 'BUY', 
      confidence: 78, 
      reason: 'Elevated freight rates detected in Mediterranean shipping routes. This often precedes currency appreciation due to increased trade activity.',
      timestamp: '2024-01-15 13:30', 
      entry: 1.2650,
      takeProfit: 1.2700,
      stopLoss: 1.2590,
      source: 'satellite',
      satelliteSource: 'shipping_route',
      region: 'Mediterranean',
      leadTime: 35,
      indicator: 'freight_rates',
      indicatorChange: 18.5
    },
    { 
      id: 103, 
      symbol: 'USD/JPY', 
      signal: 'SELL', 
      confidence: 85, 
      reason: 'Declining factory activity observed in China East Coast - down 22% from weekly average. This has preceded currency depreciation in 72% of historical cases.',
      timestamp: '2024-01-15 12:15', 
      entry: 149.50,
      takeProfit: 148.80,
      stopLoss: 150.20,
      source: 'satellite',
      satelliteSource: 'industrial',
      region: 'China East Coast',
      leadTime: 45,
      indicator: 'factory_activity',
      indicatorChange: -22.1
    },
    { 
      id: 104, 
      symbol: 'AUD/USD', 
      signal: 'WATCH', 
      confidence: 65, 
      reason: 'Unusual container density patterns detected at Singapore port. Monitoring for confirmation. Current deviation: 15% from baseline.',
      timestamp: '2024-01-15 11:00', 
      entry: 0.6520,
      takeProfit: 0.6580,
      stopLoss: 0.6460,
      source: 'satellite',
      satelliteSource: 'port_activity',
      region: 'Singapore',
      leadTime: 60,
      indicator: 'container_density',
      indicatorChange: 15.3
    },
    { 
      id: 105, 
      symbol: 'USD/CAD', 
      signal: 'STRONG_SELL', 
      confidence: 89, 
      reason: 'Critical decline in Houston commodity storage levels. Storage at 6-month low. Strong predictive signal for USD/CAD weakness.',
      timestamp: '2024-01-15 10:30', 
      entry: 1.3650,
      takeProfit: 1.3580,
      stopLoss: 1.3700,
      source: 'satellite',
      satelliteSource: 'commodity_storage',
      region: 'Houston',
      leadTime: 30,
      indicator: 'storage_levels',
      indicatorChange: -28.5
    },
  ]);

  // Combine signals based on filter
  const allSignals = signalType === 'all' 
    ? [...stockSignals, ...forexSignals]
    : signalType === 'stocks' 
      ? stockSignals 
      : forexSignals;

  useEffect(() => {
    // Simulate real-time signal updates
    const timer = setInterval(() => {
      setStockSignals(prev => prev.map(signal => ({
        ...signal,
        confidence: Math.min(100, Math.max(30, signal.confidence + (Math.random() - 0.5) * 5)),
        current: signal.current + (Math.random() - 0.5) * 2
      })));
      
      setForexSignals(prev => prev.map(signal => ({
        ...signal,
        confidence: Math.min(100, Math.max(30, signal.confidence + (Math.random() - 0.5) * 3)),
        entry: signal.entry + (Math.random() - 0.5) * 0.0005
      })));
    }, 10000);

    return () => clearInterval(timer);
  }, []);

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY':
      case 'STRONG_BUY':
        return '#22c55e';
      case 'SELL':
      case 'STRONG_SELL':
        return '#ef4444';
      case 'HOLD':
        return '#f59e0b';
      case 'WATCH':
        return '#3b82f6';
      default:
        return '#8b98a5';
    }
  };

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 80) return 'high';
    if (confidence >= 60) return 'medium';
    return 'low';
  };

  const filteredSignals = filter === 'all'
    ? allSignals
    : allSignals.filter(s => {
        // Map filter to signal types
        const filterMap = {
          'BUY': ['BUY', 'STRONG_BUY'],
          'SELL': ['SELL', 'STRONG_SELL'],
          'WATCH': ['WATCH'],
          'HOLD': ['HOLD'],
          'NEUTRAL': ['NEUTRAL']
        };
        return filterMap[filter]?.includes(s.signal) || s.signal === filter;
      });

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatForexPrice = (price, pair) => {
    if (pair.includes('JPY')) {
      return price.toFixed(2);
    }
    return price.toFixed(4);
  };

  const getSourceIcon = (source) => {
    if (source === 'satellite') {
      return '🛰️';
    }
    return '🤖';
  };

  const getUpside = (signal) => {
    if (signal.signalType === 'forex' || signal.source === 'satellite') {
      const tp = signal.takeProfit || signal.target;
      const entry = signal.entry || signal.current;
      return ((tp - entry) / entry * 100).toFixed(1);
    }
    return ((signal.target - signal.current) / signal.current * 100).toFixed(1);
  };

  return (
    <div className="ai-signals">
      <div className="signals-header">
        <div>
          <h2>AI Trading Signals</h2>
          <p>Machine learning-powered trade recommendations</p>
        </div>
        
        {/* Signal Type Toggle */}
        <div className="signal-type-toggle">
          <button 
            className={`type-btn ${signalType === 'all' ? 'active' : ''}`}
            onClick={() => setSignalType('all')}
          >
            All Signals
          </button>
          <button 
            className={`type-btn ${signalType === 'stocks' ? 'active' : ''}`}
            onClick={() => setSignalType('stocks')}
          >
            📈 Stocks
          </button>
          <button 
            className={`type-btn ${signalType === 'forex' ? 'active' : ''}`}
            onClick={() => setSignalType('forex')}
          >
            💱 Forex
          </button>
        </div>
        
        <div className="signal-summary">
          <span className="summary-item buy">
            {allSignals.filter(s => s.signal.includes('BUY')).length} Buy
          </span>
          <span className="summary-item hold">
            {allSignals.filter(s => s.signal === 'HOLD').length} Hold
          </span>
          <span className="summary-item watch">
            {allSignals.filter(s => s.signal === 'WATCH').length} Watch
          </span>
          {signalType === 'forex' && (
            <span className="summary-item satellite">
              🛰️ {forexSignals.length} Satellite
            </span>
          )}
        </div>
      </div>

      {/* Filter */}
      <div className="signal-filters">
        {['all', 'BUY', 'SELL', 'WATCH', 'HOLD', 'NEUTRAL'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Satellite Info Banner (only show when forex signals are visible) */}
      {signalType === 'forex' && (
        <div className="satellite-banner">
          <span className="satellite-icon">🛰️</span>
          <span className="satellite-text">
            <strong>Satellite-Based Signals:</strong> These signals are generated from satellite imagery analysis 
            and typically provide 15-60 minutes lead time before market reactions.
          </span>
          <span className="satellite-avg-lead">
            Avg Lead Time: <strong>38 min</strong>
          </span>
        </div>
      )}

      {/* Signals Grid */}
      <div className="signals-grid">
        {filteredSignals.map(signal => (
          <div
            key={signal.id}
            className={`signal-card ${getConfidenceLevel(signal.confidence)} ${signal.source === 'satellite' ? 'satellite-signal' : ''}`}
            onClick={() => setSelectedSignal(signal)}
          >
            <div className="signal-header">
              <div className="symbol-section">
                <span className="symbol">
                  {signal.symbol}
                  {signal.source === 'satellite' && (
                    <span className="source-badge" title="Satellite-based signal">
                      {getSourceIcon(signal.source)}
                    </span>
                  )}
                </span>
                <span
                  className="signal-badge"
                  style={{ background: getSignalColor(signal.signal) }}
                >
                  {signal.signal}
                </span>
              </div>
              <div className="confidence-section">
                <span className="confidence-label">
                  {signal.source === 'satellite' ? 'Prediction Confidence' : 'Confidence'}
                </span>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${signal.confidence}%`,
                      background: signal.confidence >= 80 ? '#22c55e' : signal.confidence >= 60 ? '#f59e0b' : '#ef4444'
                    }}
                  ></div>
                </div>
                <span className="confidence-value">{signal.confidence}%</span>
              </div>
            </div>

            <div className="signal-body">
              <p className="reason">{signal.reason}</p>
              
              {/* Price targets section - different for forex vs stocks */}
              {signal.source === 'satellite' ? (
                <div className="price-targets forex-targets">
                  <div className="target-item">
                    <span className="label">Entry</span>
                    <span className="value">{formatForexPrice(signal.entry, signal.symbol)}</span>
                  </div>
                  <div className="target-item">
                    <span className="label">Take Profit</span>
                    <span className="value profit">{formatForexPrice(signal.takeProfit, signal.symbol)}</span>
                  </div>
                  <div className="target-item">
                    <span className="label">Stop Loss</span>
                    <span className="value loss">{formatForexPrice(signal.stopLoss, signal.symbol)}</span>
                  </div>
                  <div className="target-item">
                    <span className="label">Upside</span>
                    <span className={`value ${parseFloat(getUpside(signal)) > 0 ? 'positive' : 'negative'}`}>
                      {getUpside(signal)}%
                    </span>
                  </div>
                </div>
              ) : (
                <div className="price-targets">
                  <div className="target-item">
                    <span className="label">Current</span>
                    <span className="value">{formatPrice(signal.current)}</span>
                  </div>
                  <div className="target-item">
                    <span className="label">Target</span>
                    <span className="value">{formatPrice(signal.target)}</span>
                  </div>
                  <div className="target-item">
                    <span className="label">Upside</span>
                    <span className={`value ${signal.target > signal.current ? 'positive' : 'negative'}`}>
                      {((signal.target - signal.current) / signal.current * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              )}
              
              {/* Satellite-specific indicators */}
              {signal.source === 'satellite' && (
                <div className="satellite-indicators">
                  <span className="sat-indicator">
                    🌍 {signal.region}
                  </span>
                  <span className="sat-indicator">
                    📊 {signal.indicator}: {signal.indicatorChange > 0 ? '+' : ''}{signal.indicatorChange}%
                  </span>
                  <span className="sat-indicator lead-time">
                    ⏱️ {signal.leadTime}min lead
                  </span>
                </div>
              )}
            </div>

            <div className="signal-footer">
              <span className="timestamp">{signal.timestamp}</span>
              {signal.source === 'satellite' && (
                <span className="satellite-source-tag">
                  🛰️ {signal.satelliteSource}
                </span>
              )}
              <button className="details-btn">View Details</button>
            </div>
          </div>
        ))}
      </div>

      {/* Signal Detail Modal */}
      {selectedSignal && (
        <div className="modal-overlay" onClick={() => setSelectedSignal(null)}>
          <div className="signal-detail-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedSignal(null)}>×</button>

            <div className="modal-header">
              <div className="modal-symbol">
                <h2>
                  {selectedSignal.symbol}
                  {selectedSignal.source === 'satellite' && (
                    <span className="satellite-badge">🛰️ Satellite</span>
                  )}
                </h2>
                <span
                  className="signal-badge large"
                  style={{ background: getSignalColor(selectedSignal.signal) }}
                >
                  {selectedSignal.signal}
                </span>
              </div>
              <div className="modal-confidence">
                <span className="confidence-label">
                  {selectedSignal.source === 'satellite' ? 'Prediction Confidence' : 'AI Confidence'}
                </span>
                <span className="confidence-percent">{selectedSignal.confidence}%</span>
                <div className="confidence-bar large">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${selectedSignal.confidence}%`,
                      background: getSignalColor(selectedSignal.signal)
                    }}
                  ></div>
                </div>
              </div>
            </div>

            <div className="modal-body">
              <div className="analysis-section">
                <h3>Analysis</h3>
                <p>{selectedSignal.reason}</p>
              </div>

              {/* Satellite-specific details */}
              {selectedSignal.source === 'satellite' && (
                <div className="satellite-details">
                  <h3>🛰️ Satellite Data Details</h3>
                  <div className="sat-detail-grid">
                    <div className="sat-detail-item">
                      <span className="label">Data Source</span>
                      <span className="value">{selectedSignal.satelliteSource}</span>
                    </div>
                    <div className="sat-detail-item">
                      <span className="label">Region</span>
                      <span className="value">{selectedSignal.region}</span>
                    </div>
                    <div className="sat-detail-item">
                      <span className="label">Lead Time</span>
                      <span className="value">{selectedSignal.leadTime} minutes</span>
                    </div>
                    <div className="sat-detail-item">
                      <span className="label">Indicator</span>
                      <span className="value">{selectedSignal.indicator}</span>
                    </div>
                    <div className="sat-detail-item">
                      <span className="label">Change from Baseline</span>
                      <span className={`value ${selectedSignal.indicatorChange > 0 ? 'positive' : 'negative'}`}>
                        {selectedSignal.indicatorChange > 0 ? '+' : ''}{selectedSignal.indicatorChange}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="trade-levels">
                    <h4>Trade Levels</h4>
                    <div className="levels-grid">
                      <div className="level-item">
                        <span className="label">Entry</span>
                        <span className="value">{formatForexPrice(selectedSignal.entry, selectedSignal.symbol)}</span>
                      </div>
                      <div className="level-item">
                        <span className="label">Take Profit</span>
                        <span className="value profit">{formatForexPrice(selectedSignal.takeProfit, selectedSignal.symbol)}</span>
                      </div>
                      <div className="level-item">
                        <span className="label">Stop Loss</span>
                        <span className="value loss">{formatForexPrice(selectedSignal.stopLoss, selectedSignal.symbol)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="factors-section">
                <h3>
                  {selectedSignal.source === 'satellite' ? 'Correlation Factors' : 'Contributing Factors'}
                </h3>
                <div className="factors-list">
                  {selectedSignal.source === 'satellite' ? (
                    [
                      { name: 'Historical Correlation', weight: 78, type: 'positive' },
                      { name: 'Lead Time Quality', weight: 85, type: 'positive' },
                      { name: 'Signal Strength', weight: selectedSignal.confidence, type: selectedSignal.confidence > 70 ? 'positive' : 'neutral' },
                      { name: 'Regional Relevance', weight: 72, type: 'positive' },
                      { name: 'Market Conditions', weight: 65, type: 'neutral' },
                    ]
                  ).map((factor, i) => (
                    <div key={i} className="factor-item">
                      <span className="factor-name">{factor.name}</span>
                      <div className="factor-bar">
                        <div
                          className="factor-fill"
                          style={{
                            width: `${factor.weight}%`,
                            background: factor.type === 'positive' ? '#22c55e' : factor.type === 'negative' ? '#ef4444' : '#f59e0b'
                          }}
                        ></div>
                      </div>
                      <span className="factor-weight">{factor.weight}%</span>
                    </div>
                  )) : (
                    [
                      { name: 'Technical Momentum', weight: 85, type: 'positive' },
                      { name: 'Volume Analysis', weight: 72, type: 'positive' },
                      { name: 'Sentiment Score', weight: 68, type: 'neutral' },
                      { name: 'Price Action', weight: 65, type: 'positive' },
                      { name: 'Volatility Index', weight: 45, type: 'negative' },
                    ].map((factor, i) => (
                      <div key={i} className="factor-item">
                        <span className="factor-name">{factor.name}</span>
                        <div className="factor-bar">
                          <div
                            className="factor-fill"
                            style={{
                              width: `${factor.weight}%`,
                              background: factor.type === 'positive' ? '#22c55e' : factor.type === 'negative' ? '#ef4444' : '#f59e0b'
                            }}
                          ></div>
                        </div>
                        <span className="factor-weight">{factor.weight}%</span>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="prediction-section">
                <h3>
                  {selectedSignal.source === 'satellite' ? 'Expected Market Reaction' : 'Price Prediction'}
                </h3>
                <div className="prediction-chart">
                  <svg viewBox="0 0 200 60" className="prediction-svg">
                    <path
                      d="M0,50 Q30,45 60,35 T120,25 T200,15"
                      fill="none"
                      stroke={getSignalColor(selectedSignal.signal)}
                      strokeWidth="2"
                    />
                    <circle cx="0" cy="50" r="3" fill={getSignalColor(selectedSignal.signal)} />
                    <circle cx="200" cy="15" r="4" fill="#1d9bf0" />
                  </svg>
                  <div className="prediction-labels">
                    {selectedSignal.source === 'satellite' ? (
                      <>
                        <span>Entry: {formatForexPrice(selectedSignal.entry, selectedSignal.symbol)}</span>
                        <span>Target: {formatForexPrice(selectedSignal.takeProfit, selectedSignal.symbol)}</span>
                      </>
                    ) : (
                      <>
                        <span>Current: {formatPrice(selectedSignal.current)}</span>
                        <span>Target: {formatPrice(selectedSignal.target)}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              {selectedSignal.source === 'satellite' ? (
                <>
                  <button className="action-btn primary">Execute Trade</button>
                  <button className="action-btn secondary">Set Alert</button>
                  <button className="action-btn secondary">View Correlation Data</button>
                </>
              ) : (
                <>
                  <button className="action-btn primary">Add to Watchlist</button>
                  <button className="action-btn secondary">Set Price Alert</button>
                  <button className="action-btn secondary">View Full Report</button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AISignals;

