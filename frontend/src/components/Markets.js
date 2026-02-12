import React, { useState, useEffect, useCallback } from 'react';
import './Markets.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

function Markets() {
  const [activeExchange, setActiveExchange] = useState('NASDAQ');
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const exchanges = ['NYSE', 'NASDAQ', 'AMEX'];

  // Fetch stocks by exchange
  const fetchStocks = useCallback(async (exchange) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/stocks/by-exchange/${exchange}`);
      const data = await response.json();
      if (data.stocks) {
        setStocks(data.stocks);
      }
    } catch (error) {
      console.error('Error fetching stocks:', error);
      // Fallback data
      setStocks([]);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchStocks(activeExchange);
  }, [activeExchange, fetchStocks]);

  // Search stocks
  useEffect(() => {
    const searchStocks = async () => {
      if (searchQuery.length < 1) {
        setSearchResults([]);
        setShowSearchResults(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/stocks/search?q=${searchQuery}`);
        const data = await response.json();
        if (data.results) {
          setSearchResults(data.results);
          setShowSearchResults(true);
        }
      } catch (error) {
        console.error('Error searching stocks:', error);
      }
    };

    const debounce = setTimeout(searchStocks, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatChange = (change) => {
    const isPositive = change >= 0;
    return (
      <span className={isPositive ? 'change-positive' : 'change-negative'}>
        {isPositive ? '+' : ''}{change.toFixed(2)}%
      </span>
    );
  };

  const formatMarketCap = (cap) => {
    if (cap >= 1e12) return `$${(cap / 1e12).toFixed(2)}T`;
    if (cap >= 1e9) return `$${(cap / 1e9).toFixed(2)}B`;
    if (cap >= 1e6) return `$${(cap / 1e6).toFixed(2)}M`;
    return `$${cap}`;
  };

  const getExchangeColor = (exchange) => {
    switch (exchange) {
      case 'NYSE': return '#1a73e8';
      case 'NASDAQ': return '#ff6b00';
      case 'AMEX': return '#34a853';
      default: return '#666';
    }
  };

  return (
    <div className="markets-container">
      {/* Search Bar */}
      <div className="markets-search-section">
        <div className="search-wrapper">
          <input
            type="text"
            className="stock-search-input"
            placeholder="Search stocks by symbol or name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onFocus={() => searchQuery.length > 0 && setShowSearchResults(true)}
          />
          {showSearchResults && searchResults.length > 0 && (
            <div className="search-results-dropdown">
              {searchResults.map((stock) => (
                <div
                  key={stock.symbol}
                  className="search-result-item"
                  onClick={() => {
                    setSearchQuery('');
                    setShowSearchResults(false);
                    setActiveExchange(stock.exchange);
                  }}
                >
                  <div className="result-main">
                    <span className="result-symbol">{stock.symbol}</span>
                    <span className="result-name">{stock.name}</span>
                  </div>
                  <div className="result-secondary">
                    <span
                      className="result-exchange"
                      style={{ backgroundColor: getExchangeColor(stock.exchange) }}
                    >
                      {stock.exchange}
                    </span>
                    <span className="result-price">{formatPrice(stock.price)}</span>
                    {formatChange(stock.change_percent)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Exchange Tabs */}
      <div className="exchange-tabs">
        {exchanges.map((exchange) => (
          <button
            key={exchange}
            className={`exchange-tab ${activeExchange === exchange ? 'active' : ''}`}
            onClick={() => setActiveExchange(exchange)}
          >
            <span className="tab-name">{exchange}</span>
            <span className="tab-indicator" style={{ backgroundColor: getExchangeColor(exchange) }}></span>
          </button>
        ))}
      </div>

      {/* Exchange Info */}
      <div className="exchange-info">
        <h2>{activeExchange} Exchange</h2>
        <div className="exchange-stats">
          <div className="stat">
            <span className="stat-value">{stocks.length}</span>
            <span className="stat-label">Listed Stocks</span>
          </div>
          <div className="stat">
            <span className="stat-value">$28.5T</span>
            <span className="stat-label">Market Cap</span>
          </div>
          <div className="stat">
            <span className="stat-value">~2,400</span>
            <span className="stat-label">Companies</span>
          </div>
        </div>
      </div>

      {/* Stocks Grid */}
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading {activeExchange} stocks...</p>
        </div>
      ) : (
        <div className="stocks-grid">
          {stocks.map((stock) => (
            <div key={stock.symbol} className="stock-card">
              <div className="stock-card-header">
                <div className="stock-symbol-info">
                  <span className="stock-symbol">{stock.symbol}</span>
                  <span
                    className="stock-exchange-badge"
                    style={{ backgroundColor: getExchangeColor(stock.exchange) }}
                  >
                    {stock.exchange}
                  </span>
                </div>
                <span className="stock-sector">{stock.sector}</span>
              </div>
              <div className="stock-card-body">
                <span className="stock-name">{stock.name}</span>
                <div className="stock-price-section">
                  <span className="stock-price">{formatPrice(stock.price)}</span>
                  {formatChange(stock.change_percent)}
                </div>
              </div>
              <div className="stock-card-footer">
                <span className="market-cap">Cap: {formatMarketCap(stock.market_cap)}</span>
                <button className="add-watchlist-btn">+ Watchlist</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Markets;

