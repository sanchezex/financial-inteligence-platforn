import React, { useState, useEffect } from 'react';
import './ShortInterest.css';

function ShortInterest({ symbol = 'TSLA' }) {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [viewMode, setViewMode] = useState('overview');

  useEffect(() => {
    // Generate short interest data
    const generateData = () => {
      const baseData = {
        'TSLA': { name: 'Tesla Inc.', price: 245.30, floatPercent: 19.2 },
        'AAPL': { name: 'Apple Inc.', price: 178.50, floatPercent: 0.8 },
        'NVDA': { name: 'NVIDIA Corp.', price: 495.20, floatPercent: 1.2 },
        'MSFT': { name: 'Microsoft Corp.', price: 378.90, floatPercent: 0.6 },
        'GME': { name: 'GameStop Corp.', price: 14.50, floatPercent: 28.5 },
        'AMC': { name: 'AMC Entertainment', price: 8.20, floatPercent: 22.3 },
        'BBBY': { name: 'Bed Bath & Beyond', price: 1.85, floatPercent: 45.2 },
        'META': { name: 'Meta Platforms', price: 505.75, floatPercent: 1.5 },
        'AMD': { name: 'AMD', price: 142.30, floatPercent: 4.2 },
        'PLTR': { name: 'Palantir', price: 18.45, floatPercent: 8.7 },
      };

      const company = baseData[symbol] || baseData['TSLA'];
      
      return {
        symbol,
        name: company.name,
        currentPrice: company.price,
        shortInterest: {
          sharesShort: Math.floor(Math.random() * 100000000) + 10000000,
          avgDailyVolume: Math.floor(Math.random() * 50000000) + 10000000,
          daysToCover: (Math.random() * 15 + 2).toFixed(1),
          shortPercent: Math.random() * 30 + 1,
          change: (Math.random() - 0.3) * 20,
          date: '2024-01-15',
        },
        shortInterestHistory: [
          { date: '2024-01-15', sharesShort: 45000000, percent: 15.2, daysToCover: 4.5 },
          { date: '2024-01-01', sharesShort: 42000000, percent: 14.1, daysToCover: 4.2 },
          { date: '2023-12-15', sharesShort: 38000000, percent: 12.8, daysToCover: 3.8 },
          { date: '2023-12-01', sharesShort: 41000000, percent: 13.8, daysToCover: 4.1 },
          { date: '2023-11-15', sharesShort: 35000000, percent: 11.8, daysToCover: 3.5 },
          { date: '2023-11-01', sharesShort: 32000000, percent: 10.8, daysToCover: 3.2 },
          { date: '2023-10-15', sharesShort: 28000000, percent: 9.5, daysToCover: 2.8 },
          { date: '2023-10-01', sharesShort: 30000000, percent: 10.1, daysToCover: 3.0 },
        ],
        costBasis: {
          high: company.price * (1.2 + Math.random() * 0.5),
          low: company.price * (0.5 + Math.random() * 0.3),
          average: company.price * (0.7 + Math.random() * 0.3),
        },
        squeezeMetrics: {
          shortInterestRatio: Math.random() * 10 + 2,
          utilizationPercent: Math.random() * 80 + 20,
          availableShares: Math.floor(Math.random() * 200000000) + 50000000,
          borrowRate: (Math.random() * 50 + 5).toFixed(2),
          facilityFee: (Math.random() * 2 + 0.5).toFixed(2),
        },
        competitors: [
          { symbol: 'RIVN', name: 'Rivian', shortPercent: 18.5, daysToCover: 5.2 },
          { symbol: 'LCID', name: 'Lucid', shortPercent: 22.3, daysToCover: 6.1 },
          { symbol: 'F', name: 'Ford', shortPercent: 2.8, daysToCover: 3.5 },
        ],
        sentiment: {
          redditMentions: Math.floor(Math.random() * 50000) + 10000,
          twitterMentions: Math.floor(Math.random() * 20000) + 5000,
          newsArticles: Math.floor(Math.random() * 100) + 20,
          overallSentiment: Math.random() > 0.5 ? 'Bearish' : 'Bullish',
          sentimentScore: (Math.random() * 100).toFixed(0),
        }
      };
    };

    const timer = setTimeout(() => {
      setData(generateData());
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [symbol]);

  const formatNumber = (num) => {
    if (num >= 1000000000) return `${(num / 1000000000).toFixed(2)}B`;
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(num);
  };

  const getSqueezeRisk = () => {
    const si = data.shortInterest.shortPercent;
    const dtc = parseFloat(data.shortInterest.daysToCover);
    const borrowRate = parseFloat(data.squeezeMetrics.borrowRate);
    
    let risk = 'LOW';
    let score = 0;
    
    if (si > 20 || dtc > 8 || borrowRate > 30) {
      risk = 'HIGH';
      score = 80 + Math.random() * 20;
    } else if (si > 10 || dtc > 5 || borrowRate > 15) {
      risk = 'MEDIUM';
      score = 50 + Math.random() * 30;
    } else {
      risk = 'LOW';
      score = Math.random() * 50;
    }
    
    return { risk, score: Math.round(score) };
  };

  if (loading) {
    return (
      <div className="short-interest loading">
        <div className="loading-spinner"></div>
        <p>Loading short interest data...</p>
      </div>
    );
  }

  const squeezeRisk = getSqueezeRisk();

  return (
    <div className="short-interest">
      {/* Header */}
      <div className="short-header">
        <div className="header-left">
          <h2>{data.symbol} Short Interest</h2>
          <p>{data.name} - Short squeeze potential analysis</p>
        </div>
        <div className="header-right">
          <div className={`squeeze-risk-badge ${squeezeRisk.risk.toLowerCase()}`}>
            <span className="risk-label">Squeeze Risk</span>
            <span className="risk-value">{squeezeRisk.risk}</span>
            <span className="risk-score">{squeezeRisk.score}%</span>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="quick-stats">
        <div className="stat-card">
          <span className="stat-label">Shares Short</span>
          <span className="stat-value">{formatNumber(data.shortInterest.sharesShort)}</span>
          <span className="stat-change positive">{data.shortInterest.change >= 0 ? '+' : ''}{data.shortInterest.change.toFixed(1)}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Short % of Float</span>
          <span className="stat-value">{data.shortInterest.shortPercent.toFixed(2)}%</span>
          <span className="stat-sublabel">of {data.shortInterest.avgDailyVolume} avg vol</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Days to Cover</span>
          <span className="stat-value">{data.shortInterest.daysToCover}</span>
          <span className="stat-sublabel">at current volume</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Cost Basis</span>
          <span className="stat-value">{formatCurrency(data.costBasis.average)}</span>
          <span className="stat-sublabel">avg short price</span>
        </div>
      </div>

      {/* View Tabs */}
      <div className="view-tabs">
        {['overview', 'history', 'competitors', 'sentiment'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${viewMode === tab ? 'active' : ''}`}
            onClick={() => setViewMode(tab)}
          >
            {tab === 'overview' && 'Overview'}
            {tab === 'history' && 'History'}
            {tab === 'competitors' && 'Competitors'}
            {tab === 'sentiment' && 'Sentiment'}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="short-content">
        {viewMode === 'overview' && (
          <div className="overview-section">
            {/* Cost Basis Chart */}
            <div className="cost-basis-card">
              <h3>Short Seller Cost Basis</h3>
              <p>Where short sellers are positioned</p>
              <div className="cost-chart">
                <svg viewBox="0 0 400 150">
                  <defs>
                    <linearGradient id="costGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="#ef4444" stopOpacity="0.3"/>
                      <stop offset="100%" stopColor="#ef4444" stopOpacity="0"/>
                    </linearGradient>
                  </defs>
                  {/* Cost distribution bars */}
                  {[...Array(20)].map((_, i) => {
                    const price = data.costBasis.low + (data.costBasis.high - data.costBasis.low) * (i / 19);
                    const isCurrent = Math.abs(price - data.currentPrice) < (data.costBasis.high - data.costBasis.low) * 0.05;
                    const isProfitable = price > data.currentPrice;
                    return (
                      <rect
                        key={i}
                        x={i * 20}
                        y={isProfitable ? 100 : 50}
                        width="18"
                        height={isProfitable ? 50 : 100}
                        fill={isCurrent ? '#1d9bf0' : isProfitable ? '#22c55e' : '#ef4444'}
                        opacity={isCurrent ? 1 : 0.5}
                        rx="2"
                      />
                    );
                  })}
                  {/* Current price line */}
                  <line
                    x1={(data.currentPrice - data.costBasis.low) / (data.costBasis.high - data.costBasis.low) * 400}
                    y1="0"
                    x2={(data.currentPrice - data.costBasis.low) / (data.costBasis.high - data.costBasis.low) * 400}
                    y2="150"
                    stroke="#1d9bf0"
                    strokeWidth="2"
                    strokeDasharray="4,4"
                  />
                </svg>
                <div className="cost-labels">
                  <span>{formatCurrency(data.costBasis.low)}</span>
                  <span className="current-price">Current: {formatCurrency(data.currentPrice)}</span>
                  <span>{formatCurrency(data.costBasis.high)}</span>
                </div>
              </div>
              <div className="cost-legend">
                <div className="legend-item">
                  <span className="legend-color profit"></span>
                  <span>In Profit (Short below current)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color loss"></span>
                  <span>In Loss (Short above current)</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color current"></span>
                  <span>Current Price</span>
                </div>
              </div>
            </div>

            {/* Squeeze Metrics */}
            <div className="squeeze-metrics-card">
              <h3>Short Squeeze Metrics</h3>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Short Interest Ratio</span>
                  <span className="metric-value">{data.squeezeMetrics.shortInterestRatio.toFixed(1)}x</span>
                  <span className="metric-desc">Days of trading to cover</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Utilization</span>
                  <span className="metric-value">{data.squeezeMetrics.utilizationPercent.toFixed(1)}%</span>
                  <span className="metric-desc">Shares available to borrow</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Borrow Rate</span>
                  <span className="metric-value warning">{data.squeezeMetrics.borrowRate}%</span>
                  <span className="metric-desc">Annual borrow cost</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Available Shares</span>
                  <span className="metric-value">{formatNumber(data.squeezeMetrics.availableShares)}</span>
                  <span className="metric-desc">Shares available to short</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {viewMode === 'history' && (
          <div className="history-section">
            <h3>Short Interest History</h3>
            <div className="history-table">
              <div className="table-row header">
                <span>Date</span>
                <span>Shares Short</span>
                <span>% of Float</span>
                <span>Days to Cover</span>
                <span>Trend</span>
              </div>
              {data.shortInterestHistory.map((item, i) => (
                <div key={i} className="table-row">
                  <span>{item.date}</span>
                  <span>{formatNumber(item.sharesShort)}</span>
                  <span>{item.percent}%</span>
                  <span>{item.daysToCover}</span>
                  <span className={`trend ${i === 0 ? '' : item.percent > data.shortInterestHistory[i-1].percent ? 'up' : 'down'}`}>
                    {i === 0 ? '-' : item.percent > data.shortInterestHistory[i-1].percent ? '↑' : '↓'}
                  </span>
                </div>
              ))}
            </div>
            <div className="history-chart">
              <svg viewBox="0 0 600 150">
                {data.shortInterestHistory.map((item, i) => {
                  const x = (i / (data.shortInterestHistory.length - 1)) * 550;
                  const y = 130 - (item.percent / 25) * 100;
                  const prevY = i > 0 ? 130 - (data.shortInterestHistory[i-1].percent / 25) * 100 : y;
                  
                  return (
                    <g key={i}>
                      {i > 0 && (
                        <line
                          x1={x - (550 / (data.shortInterestHistory.length - 1))}
                          y1={prevY}
                          x2={x}
                          y2={y}
                          stroke="#ef4444"
                          strokeWidth="2"
                        />
                      )}
                      <circle cx={x} cy={y} r="4" fill="#ef4444" />
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>
        )}

        {viewMode === 'competitors' && (
          <div className="competitors-section">
            <h3>Competitor Comparison</h3>
            <div className="competitors-grid">
              <div className="competitor-card current">
                <div className="card-header">
                  <span className="symbol">{data.symbol}</span>
                  <span className="label">Current</span>
                </div>
                <div className="card-stats">
                  <div className="stat">
                    <span className="stat-label">Short %</span>
                    <span className="stat-value">{data.shortInterest.shortPercent.toFixed(2)}%</span>
                  </div>
                  <div className="stat">
                    <span className="stat-label">Days to Cover</span>
                    <span className="stat-value">{data.shortInterest.daysToCover}</span>
                  </div>
                </div>
              </div>
              {data.competitors.map(comp => (
                <div key={comp.symbol} className="competitor-card">
                  <div className="card-header">
                    <span className="symbol">{comp.symbol}</span>
                    <span className="name">{comp.name}</span>
                  </div>
                  <div className="card-stats">
                    <div className="stat">
                      <span className="stat-label">Short %</span>
                      <span className={`stat-value ${comp.shortPercent > 15 ? 'high' : ''}`}>
                        {comp.shortPercent.toFixed(2)}%
                      </span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Days to Cover</span>
                      <span className="stat-value">{comp.daysToCover}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {viewMode === 'sentiment' && (
          <div className="sentiment-section">
            <h3>Social Sentiment</h3>
            <div className="sentiment-grid">
              <div className="sentiment-card">
                <h4>Reddit Activity</h4>
                <div className="sentiment-value">{formatNumber(data.sentiment.redditMentions)}</div>
                <div className="sentiment-bar">
                  <div className="sentiment-fill" style={{ width: `${Math.random() * 100}%` }}></div>
                </div>
                <span className="sentiment-label">Mentions (7d)</span>
              </div>
              <div className="sentiment-card">
                <h4>Twitter/X Activity</h4>
                <div className="sentiment-value">{formatNumber(data.sentiment.twitterMentions)}</div>
                <div className="sentiment-bar">
                  <div className="sentiment-fill" style={{ width: `${Math.random() * 100}%` }}></div>
                </div>
                <span className="sentiment-label">Mentions (7d)</span>
              </div>
              <div className="sentiment-card">
                <h4>News Coverage</h4>
                <div className="sentiment-value">{data.sentiment.newsArticles}</div>
                <div className="sentiment-bar">
                  <div className="sentiment-fill" style={{ width: `${Math.random() * 100}%` }}></div>
                </div>
                <span className="sentiment-label">Articles (7d)</span>
              </div>
              <div className="sentiment-card overall">
                <h4>Overall Sentiment</h4>
                <div className={`sentiment-bullish ${data.sentiment.overallSentiment.toLowerCase()}`}>
                  {data.sentiment.overallSentiment}
                </div>
                <div className="sentiment-score">
                  <div className="score-bar">
                    <div className="score-fill" style={{ width: `${data.sentiment.sentimentScore}%` }}></div>
                  </div>
                  <span>Score: {data.sentiment.sentimentScore}/100</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ShortInterest;

