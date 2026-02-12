
import React, { useState, useEffect } from 'react';
import './StockCompare.css';

function StockCompare({ symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA'] }) {
  const [selectedSymbols, setSelectedSymbols] = useState(symbols);
  const [comparisonData, setComparisonData] = useState([]);
  const [compareMetrics, setCompareMetrics] = useState(['price', 'change', 'marketCap']);

  useEffect(() => {
    // Generate comparison data
    const generateData = () => {
      return selectedSymbols.map(symbol => {
        const basePrice = { 'AAPL': 178, 'MSFT': 378, 'GOOGL': 141, 'NVDA': 495, 'AMZN': 178, 'TSLA': 245, 'META': 505 }[symbol] || 100;
        return {
          symbol,
          companyName: getCompanyName(symbol),
          price: basePrice + Math.random() * 20 - 10,
          change: (Math.random() - 0.5) * 10,
          changePercent: (Math.random() - 0.5) * 5,
          marketCap: Math.floor(Math.random() * 2000000000000),
          pe: (Math.random() * 50).toFixed(2),
          eps: (Math.random() * 10).toFixed(2),
          volume: Math.floor(Math.random() * 50000000),
          high52w: basePrice * 1.3,
          low52w: basePrice * 0.7,
          dividend: Math.random() * 3,
          beta: (0.8 + Math.random() * 0.8).toFixed(2)
        };
      });
    };

    const timer = setTimeout(() => {
      setComparisonData(generateData());
    }, 300);

    return () => clearTimeout(timer);
  }, [selectedSymbols]);

  const getCompanyName = (symbol) => {
    const names = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corp.',
      'GOOGL': 'Alphabet Inc.',
      'NVDA': 'NVIDIA Corp.',
      'AMZN': 'Amazon.com Inc.',
      'TSLA': 'Tesla Inc.',
      'META': 'Meta Platforms',
    };
    return names[symbol] || symbol;
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatMarketCap = (cap) => {
    if (cap >= 1000000000000) return `$${(cap / 1000000000000).toFixed(2)}T`;
    if (cap >= 1000000000) return `$${(cap / 1000000000).toFixed(2)}B`;
    return `$${(cap / 1000000).toFixed(2)}M`;
  };

  const formatPercent = (percent) => {
    const isPositive = percent >= 0;
    return (
      <span className={isPositive ? 'positive' : 'negative'}>
        {isPositive ? '+' : ''}{percent.toFixed(2)}%
      </span>
    );
  };

  const toggleSymbol = (symbol) => {
    if (selectedSymbols.includes(symbol)) {
      if (selectedSymbols.length > 2) {
        setSelectedSymbols(selectedSymbols.filter(s => s !== symbol));
      }
    } else if (selectedSymbols.length < 5) {
      setSelectedSymbols([...selectedSymbols, symbol]);
    }
  };

  const availableSymbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'AMZN', 'TSLA', 'META', 'JPM'];

  // Calculate correlation simulation (random for demo)
  const getCorrelation = (s1, s2) => {
    return (Math.random() * 0.8 + 0.1).toFixed(2);
  };

  return (
    <div className="stock-compare">
      <div className="compare-header">
        <h2>Stock Comparison</h2>
        <p>Compare multiple stocks side-by-side</p>
      </div>

      {/* Symbol Selector */}
      <div className="symbol-selector">
        <span className="selector-label">Select stocks to compare (2-5):</span>
        <div className="symbol-buttons">
          {availableSymbols.map(symbol => (
            <button
              key={symbol}
              className={`symbol-btn ${selectedSymbols.includes(symbol) ? 'active' : ''}`}
              onClick={() => toggleSymbol(symbol)}
            >
              {symbol}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Selector */}
      <div className="metrics-selector">
        <span className="selector-label">Compare by:</span>
        <div className="metric-checkboxes">
          {['price', 'change', 'marketCap', 'pe', 'volume'].map(metric => (
            <label key={metric} className="metric-checkbox">
              <input
                type="checkbox"
                checked={compareMetrics.includes(metric)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setCompareMetrics([...compareMetrics, metric]);
                  } else {
                    setCompareMetrics(compareMetrics.filter(m => m !== metric));
                  }
                }}
              />
              {metric.replace(/([A-Z])/g, ' $1').trim()}
            </label>
          ))}
        </div>
      </div>

      {/* Comparison Table */}
      <div className="comparison-table">
        <div className="table-header">
          <span className="metric-col">Metric</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {stock.symbol}
            </span>
          ))}
        </div>

        {/* Company Name */}
        <div className="table-row">
          <span className="metric-col">Company</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col company-name">
              {stock.companyName}
            </span>
          ))}
        </div>

        {/* Price */}
        <div className="table-row">
          <span className="metric-col">Price</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {formatPrice(stock.price)}
            </span>
          ))}
        </div>

        {/* Change */}
        <div className="table-row">
          <span className="metric-col">Change</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {formatPercent(stock.changePercent)}
            </span>
          ))}
        </div>

        {/* Market Cap */}
        {compareMetrics.includes('marketCap') && (
          <div className="table-row">
            <span className="metric-col">Market Cap</span>
            {comparisonData.map(stock => (
              <span key={stock.symbol} className="stock-col">
                {formatMarketCap(stock.marketCap)}
              </span>
            ))}
          </div>
        )}

        {/* P/E Ratio */}
        {compareMetrics.includes('pe') && (
          <div className="table-row">
            <span className="metric-col">P/E Ratio</span>
            {comparisonData.map(stock => (
              <span key={stock.symbol} className="stock-col">
                {stock.pe}
              </span>
            ))}
          </div>
        )}

        {/* EPS */}
        <div className="table-row">
          <span className="metric-col">EPS</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {formatPrice(stock.eps)}
            </span>
          ))}
        </div>

        {/* Volume */}
        {compareMetrics.includes('volume') && (
          <div className="table-row">
            <span className="metric-col">Volume</span>
            {comparisonData.map(stock => (
              <span key={stock.symbol} className="stock-col">
                {(stock.volume / 1000000).toFixed(2)}M
              </span>
            ))}
          </div>
        )}

        {/* 52 Week Range */}
        <div className="table-row">
          <span className="metric-col">52W Range</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col range">
              {formatPrice(stock.low52w)} - {formatPrice(stock.high52w)}
            </span>
          ))}
        </div>

        {/* Dividend */}
        <div className="table-row">
          <span className="metric-col">Dividend</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {stock.dividend.toFixed(2)}%
            </span>
          ))}
        </div>

        {/* Beta */}
        <div className="table-row">
          <span className="metric-col">Beta</span>
          {comparisonData.map(stock => (
            <span key={stock.symbol} className="stock-col">
              {stock.beta}
            </span>
          ))}
        </div>
      </div>

      {/* Correlation Matrix */}
      <div className="correlation-section">
        <h3>Correlation Matrix</h3>
        <div className="correlation-matrix">
          <div className="matrix-row">
            <span className="matrix-header"></span>
            {selectedSymbols.map(s => (
              <span key={s} className="matrix-header">{s}</span>
            ))}
          </div>
          {selectedSymbols.map(s1 => (
            <div key={s1} className="matrix-row">
              <span className="matrix-header">{s1}</span>
              {selectedSymbols.map(s2 => {
                const corr = s1 === s2 ? 1.0 : getCorrelation(s1, s2);
                return (
                  <span
                    key={s2}
                    className="matrix-cell"
                    style={{ backgroundColor: `rgba(34, 197, 94, ${corr * 0.5})` }}
                  >
                    {corr.toFixed(2)}
                  </span>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Mini Charts */}
      <div className="mini-charts-section">
        <h3>Performance Comparison</h3>
        <div className="charts-grid">
          {comparisonData.map(stock => (
            <div key={stock.symbol} className="mini-chart-card">
              <span className="chart-symbol">{stock.symbol}</span>
              <svg viewBox="0 0 100 40" className="mini-chart-svg">
                <path
                  d="M0,30 Q25,25 50,20 T100,10"
                  fill="none"
                  stroke={stock.changePercent >= 0 ? '#22c55e' : '#ef4444'}
                  strokeWidth="2"
                />
              </svg>
              <span className={stock.changePercent >= 0 ? 'positive' : 'negative'}>
                {formatPercent(stock.changePercent)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StockCompare;

