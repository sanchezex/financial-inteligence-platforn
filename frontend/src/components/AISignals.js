
import React, { useState, useEffect } from 'react';
import './AISignals.css';

function AISignals() {
  const [signals, setSignals] = useState([
    { id: 1, symbol: 'NVDA', signal: 'BUY', confidence: 87, reason: 'Strong momentum breakout with volume spike', timestamp: '2024-01-15 14:30', target: 520, current: 495 },
    { id: 2, symbol: 'AAPL', signal: 'HOLD', confidence: 65, reason: 'Consolidating near resistance', timestamp: '2024-01-15 12:15', target: 185, current: 178 },
    { id: 3, symbol: 'TSLA', signal: 'WATCH', confidence: 72, reason: 'Approaching key support level', timestamp: '2024-01-15 10:45', target: 260, current: 245 },
    { id: 4, symbol: 'MSFT', signal: 'BUY', confidence: 81, reason: 'AI-driven earnings beat expectations', timestamp: '2024-01-15 09:30', target: 400, current: 379 },
    { id: 5, symbol: 'GOOGL', signal: 'NEUTRAL', confidence: 58, reason: 'Mixed technical indicators', timestamp: '2024-01-14 16:20', target: 150, current: 142 },
  ]);

  const [filter, setFilter] = useState('all');
  const [selectedSignal, setSelectedSignal] = useState(null);

  useEffect(() => {
    // Simulate real-time signal updates
    const timer = setInterval(() => {
      setSignals(prev => prev.map(signal => ({
        ...signal,
        confidence: Math.min(100, Math.max(30, signal.confidence + (Math.random() - 0.5) * 5)),
        current: signal.current + (Math.random() - 0.5) * 2
      })));
    }, 10000);

    return () => clearInterval(timer);
  }, []);

  const getSignalColor = (signal) => {
    switch (signal) {
      case 'BUY': return '#22c55e';
      case 'SELL': return '#ef4444';
      case 'HOLD': return '#f59e0b';
      case 'WATCH': return '#3b82f6';
      default: return '#8b98a5';
    }
  };

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 80) return 'high';
    if (confidence >= 60) return 'medium';
    return 'low';
  };

  const filteredSignals = filter === 'all'
    ? signals
    : signals.filter(s => s.signal === filter);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  return (
    <div className="ai-signals">
      <div className="signals-header">
        <div>
          <h2>AI Trading Signals</h2>
          <p>Machine learning-powered trade recommendations</p>
        </div>
        <div className="signal-summary">
          <span className="summary-item buy">{signals.filter(s => s.signal === 'BUY').length} Buy</span>
          <span className="summary-item hold">{signals.filter(s => s.signal === 'HOLD').length} Hold</span>
          <span className="summary-item watch">{signals.filter(s => s.signal === 'WATCH').length} Watch</span>
        </div>
      </div>

      {/* Filter */}
      <div className="signal-filters">
        {['all', 'BUY', 'HOLD', 'WATCH', 'NEUTRAL', 'SELL'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Signals Grid */}
      <div className="signals-grid">
        {filteredSignals.map(signal => (
          <div
            key={signal.id}
            className={`signal-card ${getConfidenceLevel(signal.confidence)}`}
            onClick={() => setSelectedSignal(signal)}
          >
            <div className="signal-header">
              <div className="symbol-section">
                <span className="symbol">{signal.symbol}</span>
                <span
                  className="signal-badge"
                  style={{ background: getSignalColor(signal.signal) }}
                >
                  {signal.signal}
                </span>
              </div>
              <div className="confidence-section">
                <span className="confidence-label">Confidence</span>
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
            </div>

            <div className="signal-footer">
              <span className="timestamp">{signal.timestamp}</span>
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
                <h2>{selectedSignal.symbol}</h2>
                <span
                  className="signal-badge large"
                  style={{ background: getSignalColor(selectedSignal.signal) }}
                >
                  {selectedSignal.signal}
                </span>
              </div>
              <div className="modal-confidence">
                <span className="confidence-label">AI Confidence</span>
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

              <div className="factors-section">
                <h3>Contributing Factors</h3>
                <div className="factors-list">
                  {[
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
                  ))}
                </div>
              </div>

              <div className="prediction-section">
                <h3>Price Prediction</h3>
                <div className="prediction-chart">
                  <svg viewBox="0 0 200 60" className="prediction-svg">
                    <path
                      d="M0,50 Q30,45 60,35 T120,25 T200,15"
                      fill="none"
                      stroke="#22c55e"
                      strokeWidth="2"
                    />
                    <circle cx="0" cy="50" r="3" fill="#22c55e" />
                    <circle cx="200" cy="15" r="4" fill="#1d9bf0" />
                  </svg>
                  <div className="prediction-labels">
                    <span>Current: {formatPrice(selectedSignal.current)}</span>
                    <span>Target: {formatPrice(selectedSignal.target)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button className="action-btn primary">Add to Watchlist</button>
              <button className="action-btn secondary">Set Price Alert</button>
              <button className="action-btn secondary">View Full Report</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AISignals;

