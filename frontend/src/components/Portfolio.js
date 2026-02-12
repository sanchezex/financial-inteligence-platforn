
import React, { useState, useEffect } from 'react';
import './Portfolio.css';

function Portfolio({ isOpen, onClose }) {
  const [holdings, setHoldings] = useState([
    { symbol: 'AAPL', shares: 50, avgCost: 145.20, currentPrice: 178.50 },
    { symbol: 'MSFT', shares: 30, avgCost: 280.50, currentPrice: 378.90 },
    { symbol: 'GOOGL', shares: 20, avgCost: 120.00, currentPrice: 141.80 },
    { symbol: 'NVDA', shares: 15, avgCost: 450.00, currentPrice: 495.20 },
    { symbol: 'AMZN', shares: 25, avgCost: 135.00, currentPrice: 178.25 },
  ]);

  const [allocation, setAllocation] = useState([]);

  useEffect(() => {
    if (holdings.length > 0) {
      const totalValue = holdings.reduce((sum, h) => sum + (h.shares * h.currentPrice), 0);
      const alloc = holdings.map(h => ({
        ...h,
        value: h.shares * h.currentPrice,
        gain: (h.currentPrice - h.avgCost) * h.shares,
        gainPercent: ((h.currentPrice - h.avgCost) / h.avgCost * 100),
        allocationPercent: (h.shares * h.currentPrice) / totalValue * 100
      }));
      setAllocation(alloc);
    }
  }, [holdings]);

  const totalValue = allocation.reduce((sum, h) => sum + h.value, 0);
  const totalCost = allocation.reduce((sum, h) => sum + (h.shares * h.avgCost), 0);
  const totalGain = totalValue - totalCost;
  const totalGainPercent = (totalGain / totalCost) * 100;

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatPercent = (percent) => {
    const isPositive = percent >= 0;
    return `${isPositive ? '+' : ''}${percent.toFixed(2)}%`;
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="portfolio-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>&times;</button>

        <div className="portfolio-header">
          <h2>Portfolio</h2>
          <span className="portfolio-value">
            {formatPrice(totalValue)}
          </span>
          <div className={`total-change ${totalGain >= 0 ? 'positive' : 'negative'}`}>
            {formatPrice(totalGain)} ({formatPercent(totalGainPercent)})
          </div>
        </div>

        {/* Asset Allocation */}
        <div className="allocation-section">
          <h3>Asset Allocation</h3>
          <div className="allocation-bars">
            {allocation.map((item, i) => (
              <div key={item.symbol} className="allocation-bar-container">
                <div className="allocation-label">
                  <span className="symbol">{item.symbol}</span>
                  <span className="percent">{item.allocationPercent.toFixed(1)}%</span>
                </div>
                <div className="bar-track">
                  <div
                    className={`bar-fill ${item.gain >= 0 ? 'positive' : 'negative'}`}
                    style={{ width: `${item.allocationPercent}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Holdings Table */}
        <div className="holdings-section">
          <h3>Holdings</h3>
          <div className="holdings-table">
            <div className="table-header">
              <span>Symbol</span>
              <span>Shares</span>
              <span>Avg Cost</span>
              <span>Price</span>
              <span>Value</span>
              <span>Gain/Loss</span>
            </div>
            {allocation.map((holding, i) => (
              <div key={i} className="table-row">
                <span className="symbol">{holding.symbol}</span>
                <span>{holding.shares}</span>
                <span>{formatPrice(holding.avgCost)}</span>
                <span>{formatPrice(holding.currentPrice)}</span>
                <span>{formatPrice(holding.value)}</span>
                <span className={holding.gain >= 0 ? 'positive' : 'negative'}>
                  {formatPrice(holding.gain)} ({formatPercent(holding.gainPercent)})
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Chart Placeholder */}
        <div className="performance-section">
          <h3>Performance</h3>
          <div className="performance-chart">
            <svg viewBox="0 0 300 100" className="chart-svg">
              <defs>
                <linearGradient id="portfolioGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" stopColor="#22c55e20" />
                  <stop offset="100%" stopColor="#22c55e00" />
                </linearGradient>
              </defs>
              <path
                d="M0,80 Q50,70 100,60 T200,40 T300,30 L300,100 L0,100 Z"
                fill="url(#portfolioGradient)"
              />
              <path
                d="M0,80 Q50,70 100,60 T200,40 T300,30"
                fill="none"
                stroke="#22c55e"
                strokeWidth="2"
              />
            </svg>
            <div className="chart-legend">
              <span>1D</span>
              <span>1W</span>
              <span>1M</span>
              <span>3M</span>
              <span>1Y</span>
              <span>ALL</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="portfolio-actions">
          <button className="action-btn primary">Add Position</button>
          <button className="action-btn secondary">Rebalance</button>
          <button className="action-btn secondary">Export</button>
        </div>
      </div>
    </div>
  );
}

export default Portfolio;

