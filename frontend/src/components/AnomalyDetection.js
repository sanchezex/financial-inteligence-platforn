
import React, { useState, useEffect } from 'react';
import './AnomalyDetection.css';

function AnomalyDetection() {
  const [anomalies, setAnomalies] = useState([
    { id: 1, type: 'volume_spike', symbol: 'NVDA', severity: 'high', description: 'Unusual volume detected: 3.5x average', timestamp: '2024-01-15 14:30', value: '45.2M', threshold: '12.8M' },
    { id: 2, type: 'price_movement', symbol: 'TSLA', severity: 'medium', description: 'Price moved 5.2% in 5 minutes', timestamp: '2024-01-15 13:45', value: '$245.30', threshold: '3%' },
    { id: 3, type: 'options_activity', symbol: 'AAPL', severity: 'high', description: 'Heavy options activity: 50k calls vs 5k puts', timestamp: '2024-01-15 12:20', value: '50:5', threshold: '3:1' },
    { id: 4, type: 'sentiment_shift', symbol: 'MSFT', severity: 'low', description: 'Social media mentions increased 150%', timestamp: '2024-01-15 11:10', value: '12.5K', threshold: '5K' },
    { id: 5, type: 'volatility_surge', symbol: 'META', severity: 'medium', description: 'IV increased 40% in 24 hours', timestamp: '2024-01-15 10:55', value: '45%', threshold: '25%' },
  ]);

  const [filters, setFilters] = useState({ type: 'all', severity: 'all' });
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);
  const [isMonitoring, setIsMonitoring] = useState(true);

  useEffect(() => {
    if (isMonitoring) {
      const timer = setInterval(() => {
        setAnomalies(prev => prev.map(a => ({
          ...a,
          value: Math.random() > 0.7 ? updateValue(a.type, a.value) : a.value
        })));
      }, 5000);

      return () => clearInterval(timer);
    }
  }, [isMonitoring]);

  const updateValue = (type, current) => {
    switch (type) {
      case 'volume_spike': return `${(12 + Math.random() * 40).toFixed(1)}M`;
      case 'price_movement': return `$${(240 + Math.random() * 20).toFixed(2)}`;
      case 'options_activity': return `${Math.floor(20 + Math.random() * 60)}:${Math.floor(3 + Math.random() * 10)}`;
      case 'sentiment_shift': return `${(3 + Math.random() * 15).toFixed(1)}K`;
      case 'volatility_surge': return `${(20 + Math.random() * 40).toFixed(0)}%`;
      default: return current;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#3b82f6';
      default: return '#8b98a5';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'volume_spike': return '';
      case 'price_movement': return '';
      case 'options_activity': return '';
      case 'sentiment_shift': return '';
      case 'volatility_surge': return '';
      default: return '';
    }
  };

  const getTypeLabel = (type) => {
    switch (type) {
      case 'volume_spike': return 'Volume Spike';
      case 'price_movement': return 'Price Movement';
      case 'options_activity': return 'Options Activity';
      case 'sentiment_shift': return 'Sentiment Shift';
      case 'volatility_surge': return 'Volatility Surge';
      default: return type;
    }
  };

  const filteredAnomalies = anomalies.filter(a => {
    if (filters.type !== 'all' && a.type !== filters.type) return false;
    if (filters.severity !== 'all' && a.severity !== filters.severity) return false;
    return true;
  });

  const severityCounts = {
    high: anomalies.filter(a => a.severity === 'high').length,
    medium: anomalies.filter(a => a.severity === 'medium').length,
    low: anomalies.filter(a => a.severity === 'low').length,
  };

  return (
    <div className="anomaly-detection">
      <div className="anomaly-header">
        <div>
          <h2>Anomaly Detection</h2>
          <p>AI-powered detection of unusual market activity</p>
        </div>
        <div className="monitoring-toggle">
          <button
            className={`monitor-btn ${isMonitoring ? 'active' : ''}`}
            onClick={() => setIsMonitoring(!isMonitoring)}
          >
            <span className={`status-dot ${isMonitoring ? 'active' : ''}`}></span>
            {isMonitoring ? 'Monitoring' : 'Paused'}
          </button>
        </div>
      </div>

      <div className="severity-stats">
        <div className="stat-card high">
          <span className="stat-value">{severityCounts.high}</span>
          <span className="stat-label">High</span>
        </div>
        <div className="stat-card medium">
          <span className="stat-value">{severityCounts.medium}</span>
          <span className="stat-label">Medium</span>
        </div>
        <div className="stat-card low">
          <span className="stat-value">{severityCounts.low}</span>
          <span className="stat-label">Low</span>
        </div>
        <div className="stat-card total">
          <span className="stat-value">{anomalies.length}</span>
          <span className="stat-label">Total</span>
        </div>
      </div>

      <div className="filter-bar">
        <div className="filter-group">
          <label>Type:</label>
          <select
            value={filters.type}
            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
          >
            <option value="all">All Types</option>
            <option value="volume_spike">Volume Spike</option>
            <option value="price_movement">Price Movement</option>
            <option value="options_activity">Options Activity</option>
            <option value="sentiment_shift">Sentiment Shift</option>
            <option value="volatility_surge">Volatility Surge</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Severity:</label>
          <select
            value={filters.severity}
            onChange={(e) => setFilters({ ...filters, severity: e.target.value })}
          >
            <option value="all">All Severities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div className="anomalies-list">
        {filteredAnomalies.map(anomaly => (
          <div
            key={anomaly.id}
            className={`anomaly-card ${anomaly.severity}`}
            onClick={() => setSelectedAnomaly(anomaly)}
          >
            <div className="anomaly-main">
              <div className="anomaly-icon">
                {getTypeIcon(anomaly.type)}
              </div>
              <div className="anomaly-info">
                <div className="anomaly-header-row">
                  <span className="symbol">{anomaly.symbol}</span>
                  <span
                    className="severity-badge"
                    style={{ background: getSeverityColor(anomaly.severity) }}
                  >
                    {anomaly.severity}
                  </span>
                </div>
                <span className="anomaly-type">{getTypeLabel(anomaly.type)}</span>
                <p className="anomaly-description">{anomaly.description}</p>
              </div>
            </div>

            <div className="anomaly-metrics">
              <div className="metric">
                <span className="metric-label">Current</span>
                <span className="metric-value current">{anomaly.value}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Threshold</span>
                <span className="metric-value threshold">{anomaly.threshold}</span>
              </div>
              <div className="metric">
                <span className="metric-label">Time</span>
                <span className="metric-value">{anomaly.timestamp.split(' ')[1]}</span>
              </div>
            </div>

            <div className="anomaly-actions">
              <button className="action-btn">View Chart</button>
              <button className="action-btn secondary">Set Alert</button>
            </div>
          </div>
        ))}
      </div>

      {selectedAnomaly && (
        <div className="modal-overlay" onClick={() => setSelectedAnomaly(null)}>
          <div className="anomaly-detail-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedAnomaly(null)}>×</button>

            <div className="modal-header">
              <span className="modal-icon">{getTypeIcon(selectedAnomaly.type)}</span>
              <div>
                <h3>{selectedAnomaly.symbol}</h3>
                <span className="modal-type">{getTypeLabel(selectedAnomaly.type)}</span>
              </div>
              <span
                className="severity-badge large"
                style={{ background: getSeverityColor(selectedAnomaly.severity) }}
              >
                {selectedAnomaly.severity}
              </span>
            </div>

            <div className="modal-body">
              <div className="detail-section">
                <h4>Description</h4>
                <p>{selectedAnomaly.description}</p>
              </div>

              <div className="detail-section">
                <h4>AI Analysis</h4>
                <div className="ai-insight">
                  <p>
                    This anomaly has a {Math.floor(75 + Math.random() * 20)}% probability of being
                    significant. Consider monitoring {selectedAnomaly.symbol} closely.
                  </p>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button className="action-btn primary">Add to Watchlist</button>
              <button className="action-btn secondary">Create Alert</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AnomalyDetection;

