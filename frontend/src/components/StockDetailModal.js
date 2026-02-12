import React, { useState, useEffect } from 'react';
import './StockDetailModal.css';

function StockDetailModal({ symbol, onClose }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activePeriod, setActivePeriod] = useState('1D');

  useEffect(() => {
    // Simulate loading detailed data
    const timer = setTimeout(() => {
      setData({
        symbol,
        companyName: getCompanyName(symbol),
        currentPrice: 100 + Math.random() * 400,
        previousClose: 100 + Math.random() * 400,
        dayHigh: 100 + Math.random() * 400,
        dayLow: 100 + Math.random() * 400,
        volume: Math.floor(Math.random() * 50000000),
        avgVolume: Math.floor(Math.random() * 50000000),
        marketCap: Math.floor(Math.random() * 2000000000000),
        pe: (Math.random() * 50).toFixed(2),
        eps: (Math.random() * 10).toFixed(2),
        week52High: 100 + Math.random() * 500,
        week52Low: 50 + Math.random() * 200,
        hourlyData: generateHourlyData(),
        news: generateNews(symbol),
      });
      setLoading(false);
    }, 500);
    return () => clearTimeout(timer);
  }, [symbol]);

  const generateHourlyData = () => {
    const hours = [];
    const now = new Date();
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      hours.push({
        time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        price: 100 + Math.random() * 400 + Math.sin(i) * 20,
        volume: Math.floor(Math.random() * 1000000),
      });
    }
    return hours;
  };

  const generateNews = (symbol) => {
    return [
      { title: `${symbol} Announces Q4 Earnings Results`, time: '2 hours ago', source: 'Bloomberg' },
      { title: `Analysts Upgrade ${symbol} Price Target`, time: '4 hours ago', source: 'Reuters' },
      { title: `Institutional Investors Increase ${symbol} Holdings`, time: '6 hours ago', source: 'CNBC' },
    ];
  };

  const getCompanyName = (sym) => {
    const names = {
      'AAPL': 'Apple Inc.',
      'MSFT': 'Microsoft Corporation',
      'GOOGL': 'Alphabet Inc.',
      'NVDA': 'NVIDIA Corporation',
      'META': 'Meta Platforms Inc.',
      'AMZN': 'Amazon.com Inc.',
      'TSLA': 'Tesla Inc.',
      'JPM': 'JPMorgan Chase & Co.',
      'S&P 500': 'S&P 500 Index',
      'DJIA': 'Dow Jones Industrial Average',
      'NASDAQ': 'NASDAQ Composite',
      'RUT': 'Russell 2000 Index',
    };
    return names[sym] || sym;
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatVolume = (volume) => {
    if (volume >= 1000000) return `${(volume / 1000000).toFixed(2)}M`;
    if (volume >= 1000) return `${(volume / 1000).toFixed(2)}K`;
    return volume.toString();
  };

  const formatMarketCap = (cap) => {
    if (cap >= 1000000000000) return `$${(cap / 1000000000000).toFixed(2)}T`;
    if (cap >= 1000000000) return `$${(cap / 1000000000).toFixed(2)}B`;
    return `$${(cap / 1000000).toFixed(2)}M`;
  };

  const calculateChange = () => {
    if (!data) return 0;
    return ((data.currentPrice - data.previousClose) / data.previousClose * 100).toFixed(2);
  };

  const getChartPath = () => {
    if (!data) return '';
    const points = data.hourlyData.map((d, i) => {
      const x = (i / (data.hourlyData.length - 1)) * 280;
      const minPrice = Math.min(...data.hourlyData.map(d => d.price));
      const maxPrice = Math.max(...data.hourlyData.map(d => d.price));
      const y = 80 - ((d.price - minPrice) / (maxPrice - minPrice)) * 70;
      return `${x},${y}`;
    });
    return `M0,${points[0].split(',')[1]} ${points.map(p => `L${p}`).join(' ')}`;
  };

  if (loading) {
    return (
      <div className="modal-overlay" onClick={onClose}>
        <div className="modal-content" onClick={e => e.stopPropagation()}>
          <div className="loading-spinner"></div>
          <p>Loading {symbol} data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content stock-detail-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        
        {/* Header */}
        <div className="stock-header">
          <div className="stock-title">
            <h2>{symbol}</h2>
            <span className="company-name">{data.companyName}</span>
          </div>
          <div className="stock-price-section">
            <span className="current-price">{formatPrice(data.currentPrice)}</span>
            <span className={`price-change ${parseFloat(calculateChange()) >= 0 ? 'positive' : 'negative'}`}>
              {parseFloat(calculateChange()) >= 0 ? '+' : ''}{calculateChange()}%
            </span>
          </div>
        </div>

        {/* Period Tabs */}
        <div className="period-tabs">
          {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map(period => (
            <button
              key={period}
              className={`period-tab ${activePeriod === period ? 'active' : ''}`}
              onClick={() => setActivePeriod(period)}
            >
              {period}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div className="chart-section">
          <svg viewBox="0 0 300 100" className="price-chart">
            <defs>
              <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stopColor={parseFloat(calculateChange()) >= 0 ? '#22c55e20' : '#ef444420'} />
                <stop offset="100%" stopColor={parseFloat(calculateChange()) >= 0 ? '#22c55e00' : '#ef444400'} />
              </linearGradient>
            </defs>
            <path
              d={`${getChartPath()} L300,100 L0,100 Z`}
              fill="url(#chartGradient)"
            />
            <path
              d={getChartPath()}
              fill="none"
              stroke={parseFloat(calculateChange()) >= 0 ? '#22c55e' : '#ef4444'}
              strokeWidth="2"
            />
          </svg>
        </div>

        {/* Key Statistics */}
        <div className="stats-section">
          <h3>Key Statistics</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Day High</span>
              <span className="stat-value">{formatPrice(data.dayHigh)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Day Low</span>
              <span className="stat-value">{formatPrice(data.dayLow)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Volume</span>
              <span className="stat-value">{formatVolume(data.volume)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Volume</span>
              <span className="stat-value">{formatVolume(data.avgVolume)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Market Cap</span>
              <span className="stat-value">{formatMarketCap(data.marketCap)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">P/E Ratio</span>
              <span className="stat-value">{data.pe}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">EPS</span>
              <span className="stat-value">{formatPrice(data.eps)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">52W Range</span>
              <span className="stat-value">{formatPrice(data.week52Low)} - {formatPrice(data.week52High)}</span>
            </div>
          </div>
        </div>

        {/* Hourly Data Table */}
        <div className="hourly-section">
          <h3>24-Hour Trading Activity</h3>
          <div className="hourly-table">
            <div className="table-header">
              <span>Time</span>
              <span>Price</span>
              <span>Change</span>
              <span>Volume</span>
            </div>
            {data.hourlyData.slice(0, 12).map((hour, i) => {
              const prevPrice = i < data.hourlyData.length - 1 ? data.hourlyData[i + 1].price : hour.price;
              const change = ((hour.price - prevPrice) / prevPrice * 100).toFixed(2);
              return (
                <div key={i} className="table-row">
                  <span>{hour.time}</span>
                  <span>{formatPrice(hour.price)}</span>
                  <span className={parseFloat(change) >= 0 ? 'positive' : 'negative'}>
                    {parseFloat(change) >= 0 ? '+' : ''}{change}%
                  </span>
                  <span>{formatVolume(hour.volume)}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* News */}
        <div className="news-section">
          <h3>Latest News</h3>
          <div className="news-list">
            {data.news.map((item, i) => (
              <div key={i} className="news-item">
                <span className="news-title">{item.title}</span>
                <div className="news-meta">
                  <span>{item.source}</span>
                  <span>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="modal-actions">
          <button className="action-btn primary">Add to Watchlist</button>
          <button className="action-btn secondary">Set Alert</button>
          <button className="action-btn secondary">View Full Analysis</button>
        </div>
      </div>
    </div>
  );
}

export default StockDetailModal;

