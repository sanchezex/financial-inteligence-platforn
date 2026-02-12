
import React, { useState, useEffect } from 'react';
import './OptionsChain.css';

function OptionsChain({ symbol = 'AAPL', expiryDate = null }) {
  const [optionsData, setOptionsData] = useState({ calls: [], puts: [] });
  const [selectedExpiry, setSelectedExpiry] = useState('Jan 19 2024');
  const [strikeRange, setStrikeRange] = useState({ min: null, max: null });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate options chain data
    const generateOptionsChain = () => {
      const basePrice = { 'AAPL': 178, 'MSFT': 378, 'GOOGL': 141, 'NVDA': 495 }[symbol] || 100;
      const strikes = [];
      const numStrikes = 15;

      for (let i = 0; i < numStrikes; i++) {
        strikes.push(basePrice - (numStrikes / 2 - i) * 5);
      }

      const calls = strikes.map(strike => ({
        strike,
        bid: Math.max(0, strike < basePrice ? (basePrice - strike) * 0.5 + Math.random() * 5 : Math.random() * 3),
        ask: Math.max(0.1, (strike < basePrice ? (basePrice - strike) * 0.5 : Math.random() * 3) + 0.5),
        last: Math.max(0.1, (strike < basePrice ? (basePrice - strike) * 0.5 : Math.random() * 3) + Math.random()),
        volume: Math.floor(Math.random() * 10000),
        openInterest: Math.floor(Math.random() * 50000),
        impliedVol: (Math.random() * 0.3 + 0.2).toFixed(2),
        delta: strike < basePrice ? (0.5 + (basePrice - strike) / basePrice).toFixed(2) : (0.5 - (strike - basePrice) / basePrice).toFixed(2),
        gamma: (Math.random() * 0.1).toFixed(3),
        theta: (-Math.random() * 0.5).toFixed(3),
      }));

      const puts = strikes.map(strike => ({
        strike,
        bid: Math.max(0, strike > basePrice ? (strike - basePrice) * 0.5 + Math.random() * 5 : Math.random() * 3),
        ask: Math.max(0.1, (strike > basePrice ? (strike - basePrice) * 0.5 : Math.random() * 3) + 0.5),
        last: Math.max(0.1, (strike > basePrice ? (strike - basePrice) * 0.5 : Math.random() * 3) + Math.random()),
        volume: Math.floor(Math.random() * 10000),
        openInterest: Math.floor(Math.random() * 50000),
        impliedVol: (Math.random() * 0.3 + 0.2).toFixed(2),
        delta: strike > basePrice ? (-0.5 - (strike - basePrice) / basePrice).toFixed(2) : (-0.5 + (basePrice - strike) / basePrice).toFixed(2),
        gamma: (Math.random() * 0.1).toFixed(3),
        theta: (-Math.random() * 0.5).toFixed(3),
      }));

      return { calls, puts };
    };

    const timer = setTimeout(() => {
      setOptionsData(generateOptionsChain());
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [symbol, selectedExpiry]);

  const formatPrice = (price) => {
    return price.toFixed(2);
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const calculateGreeks = (strike, type, spot) => {
    if (type === 'call') {
      const moneyness = (spot - strike) / strike;
      return {
        delta: moneyness > 0 ? Math.min(1, 0.5 + moneyness) : Math.max(0, 0.5 + moneyness),
        gamma: Math.random() * 0.05,
        theta: -Math.random() * 0.3,
        vega: Math.random() * 0.5
      };
    } else {
      const moneyness = (strike - spot) / strike;
      return {
        delta: moneyness > 0 ? -Math.min(1, 0.5 + moneyness) : -Math.max(0, 0.5 + moneyness),
        gamma: Math.random() * 0.05,
        theta: -Math.random() * 0.3,
        vega: Math.random() * 0.5
      };
    }
  };

  const expirations = ['Jan 19 2024', 'Feb 16 2024', 'Mar 15 2024', 'Jun 21 2024', 'Jan 17 2025'];
  const basePrice = { 'AAPL': 178, 'MSFT': 378, 'GOOGL': 141, 'NVDA': 495 }[symbol] || 100;

  if (loading) {
    return (
      <div className="options-chain loading">
        <div className="loading-spinner"></div>
        <p>Loading options data...</p>
      </div>
    );
  }

  return (
    <div className="options-chain">
      {/* Header */}
      <div className="options-header">
        <div className="symbol-info">
          <h2>{symbol} Options</h2>
          <span className="spot-price">Spot: ${formatPrice(basePrice)}</span>
        </div>
        <div className="expiry-selector">
          {expirations.map(exp => (
            <button
              key={exp}
              className={`expiry-btn ${selectedExpiry === exp ? 'active' : ''}`}
              onClick={() => setSelectedExpiry(exp)}
            >
              {exp}
            </button>
          ))}
        </div>
      </div>

      {/* Key Stats */}
      <div className="options-stats">
        <div className="stat-card">
          <span className="stat-label">IV (30d)</span>
          <span className="stat-value">{(Math.random() * 30 + 20).toFixed(1)}%</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Volume</span>
          <span className="stat-value">{formatNumber(Math.floor(Math.random() * 1000000))}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Put/Call Ratio</span>
          <span className="stat-value">{(Math.random() * 0.5 + 0.3).toFixed(2)}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Max Pain</span>
          <span className="stat-value">${formatPrice(basePrice + Math.random() * 20 - 10)}</span>
        </div>
      </div>

      {/* Options Table */}
      <div className="options-table-container">
        <div className="options-section">
          <h3>PUTS</h3>
          <div className="options-table">
            <div className="table-header">
              <span>Last</span>
              <span>Bid</span>
              <span>Ask</span>
              <span>Strike</span>
            </div>
            {optionsData.puts.reverse().map((option, i) => (
              <div
                key={i}
                className={`table-row ${Math.abs(option.strike - basePrice) < 5 ? 'at-the-money' : ''}`}
              >
                <span className="last">{formatPrice(option.last)}</span>
                <span className="bid">{formatPrice(option.bid)}</span>
                <span className="ask">{formatPrice(option.ask)}</span>
                <span className="strike">{formatPrice(option.strike)}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="options-section">
          <h3>CALLS</h3>
          <div className="options-table">
            <div className="table-header">
              <span>Strike</span>
              <span>Bid</span>
              <span>Ask</span>
              <span>Last</span>
            </div>
            {optionsData.calls.map((option, i) => (
              <div
                key={i}
                className={`table-row ${Math.abs(option.strike - basePrice) < 5 ? 'at-the-money' : ''}`}
              >
                <span className="strike">{formatPrice(option.strike)}</span>
                <span className="bid">{formatPrice(option.bid)}</span>
                <span className="ask">{formatPrice(option.ask)}</span>
                <span className="last">{formatPrice(option.last)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Greeks Panel */}
      <div className="greeks-panel">
        <h3>Greeks Analysis</h3>
        <div className="greeks-table">
          <div className="greeks-row header">
            <span>Strike</span>
            <span>Delta</span>
            <span>Gamma</span>
            <span>Theta</span>
            <span>Vega</span>
            <span>IV</span>
          </div>
          {optionsData.calls.slice(5, 10).map((option, i) => {
            const greeks = calculateGreeks(option.strike, 'call', basePrice);
            return (
              <div key={i} className="greeks-row">
                <span>{formatPrice(option.strike)}</span>
                <span className={greeks.delta > 0 ? 'positive' : 'negative'}>{greeks.delta.toFixed(3)}</span>
                <span>{greeks.gamma.toFixed(3)}</span>
                <span className="negative">{greeks.theta.toFixed(3)}</span>
                <span>{greeks.vega.toFixed(3)}</span>
                <span>{option.impliedVol}%</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Volume/Interest Chart */}
      <div className="volume-section">
        <h3>Volume & Open Interest</h3>
        <div className="volume-chart">
          <svg viewBox="0 0 600 100" className="volume-svg">
            {optionsData.calls.map((option, i) => {
              const x = (i / optionsData.calls.length) * 600;
              const barHeight = (option.volume / 10000) * 80;
              return (
                <g key={i}>
                  <rect
                    x={x}
                    y={100 - barHeight}
                    width={20}
                    height={barHeight}
                    fill="#22c55e"
                    opacity={Math.abs(option.strike - basePrice) < 5 ? 1 : 0.3}
                  />
                  <rect
                    x={x + 10}
                    y={100 - (option.openInterest / 50000) * 80}
                    width={20}
                    height={(option.openInterest / 50000) * 80}
                    fill="#3b82f6"
                    opacity={Math.abs(option.strike - basePrice) < 5 ? 1 : 0.3}
                  />
                </g>
              );
            })}
          </svg>
          <div className="chart-legend">
            <span><span className="legend-dot volume"></span> Volume</span>
            <span><span className="legend-dot oi"></span> Open Interest</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default OptionsChain;

