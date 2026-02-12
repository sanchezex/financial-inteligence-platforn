import React, { useState, useEffect } from 'react';
import './CustomWatchlists.css';

function CustomWatchlists({ onSelectStock }) {
  const [watchlists, setWatchlists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newWatchlist, setNewWatchlist] = useState({ name: '', theme: 'custom', isPublic: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate sample watchlists
    const generateWatchlists = () => {
      return [
        {
          id: 1,
          name: 'Tech Giants',
          theme: 'technology',
          isPublic: true,
          symbolCount: 8,
          performance: 15.2,
          stocks: [
            { symbol: 'AAPL', name: 'Apple Inc.', price: 178.50, change: 1.2 },
            { symbol: 'MSFT', name: 'Microsoft Corp.', price: 378.90, change: 0.8 },
            { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 141.80, change: -0.3 },
            { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 495.20, change: 2.5 },
            { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.25, change: 1.1 },
            { symbol: 'META', name: 'Meta Platforms', price: 505.75, change: 0.9 },
            { symbol: 'TSLA', name: 'Tesla Inc.', price: 245.30, change: -1.5 },
            { symbol: 'AMD', name: 'AMD', price: 142.30, change: 0.5 },
          ]
        },
        {
          id: 2,
          name: 'Healthcare',
          theme: 'healthcare',
          isPublic: false,
          symbolCount: 6,
          performance: 8.5,
          stocks: [
            { symbol: 'JNJ', name: 'Johnson & Johnson', price: 156.20, change: 0.3 },
            { symbol: 'UNH', name: 'UnitedHealth', price: 528.40, change: 0.7 },
            { symbol: 'PFE', name: 'Pfizer Inc.', price: 28.90, change: -0.2 },
            { symbol: 'ABBV', name: 'AbbVie Inc.', price: 162.50, change: 0.4 },
            { symbol: 'MRK', name: 'Merck & Co.', price: 115.80, change: 0.1 },
            { symbol: 'LLY', name: 'Eli Lilly', price: 612.30, change: 1.8 },
          ]
        },
        {
          id: 3,
          name: 'Dividend Kings',
          theme: 'income',
          isPublic: true,
          symbolCount: 5,
          performance: 5.2,
          stocks: [
            { symbol: 'KO', name: 'Coca-Cola Co.', price: 59.40, change: 0.2 },
            { symbol: 'PG', name: 'Procter & Gamble', price: 152.80, change: 0.1 },
            { symbol: 'JNJ', name: 'Johnson & Johnson', price: 156.20, change: 0.3 },
            { symbol: 'MCD', name: "McDonald's", price: 298.50, change: 0.4 },
            { symbol: 'WMT', name: 'Walmart Inc.', price: 165.20, change: 0.5 },
          ]
        },
        {
          id: 4,
          name: 'EV & Clean Energy',
          theme: 'energy',
          isPublic: false,
          symbolCount: 7,
          performance: -3.2,
          stocks: [
            { symbol: 'TSLA', name: 'Tesla Inc.', price: 245.30, change: -1.5 },
            { symbol: 'RIVN', name: 'Rivian', price: 18.45, change: -2.1 },
            { symbol: 'LCID', name: 'Lucid', price: 4.82, change: -3.5 },
            { symbol: 'NIO', name: 'NIO Inc.', price: 8.15, change: -1.2 },
            { symbol: 'PLUG', name: 'Plug Power', price: 4.25, change: 0.5 },
            { symbol: 'ENPH', name: 'Enphase Energy', price: 198.40, change: 1.8 },
            { symbol: 'SEDG', name: 'SolarEdge', price: 72.30, change: -0.8 },
          ]
        },
        {
          id: 5,
          name: 'Watch Later',
          theme: 'custom',
          isPublic: false,
          symbolCount: 4,
          performance: 0,
          stocks: [
            { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 495.20, change: 2.5 },
            { symbol: 'AMD', name: 'AMD', price: 142.30, change: 0.5 },
            { symbol: 'INTC', name: 'Intel Corp.', price: 47.85, change: -0.3 },
            { symbol: 'QCOM', name: 'Qualcomm', price: 142.60, change: 0.7 },
          ]
        }
      ];
    };

    const timer = setTimeout(() => {
      setWatchlists(generateWatchlists());
      setSelectedList(generateWatchlists()[0]);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const formatPercent = (percent) => {
    const isPositive = percent >= 0;
    return (
      <span className={isPositive ? 'positive' : 'negative'}>
        {isPositive ? '+' : ''}{percent.toFixed(2)}%
      </span>
    );
  };

  const createWatchlist = () => {
    if (newWatchlist.name.trim()) {
      const watchlist = {
        id: Date.now(),
        name: newWatchlist.name,
        theme: newWatchlist.theme,
        isPublic: newWatchlist.isPublic,
        symbolCount: 0,
        performance: 0,
        stocks: []
      };
      setWatchlists([...watchlists, watchlist]);
      setNewWatchlist({ name: '', theme: 'custom', isPublic: false });
      setShowCreateModal(false);
    }
  };

  const deleteWatchlist = (id) => {
    setWatchlists(watchlists.filter(w => w.id !== id));
    if (selectedList?.id === id) {
      setSelectedList(watchlists.find(w => w.id !== id) || null);
    }
  };

  const getThemeIcon = (theme) => {
    const icons = {
      technology: 'Technology',
      healthcare: 'Healthcare',
      energy: 'Energy',
      income: 'Income',
      financial: 'Financial',
      custom: 'Custom'
    };
    return icons[theme] || 'Custom';
  };

  const getPerformanceColor = (perf) => {
    if (perf > 0) return '#22c55e';
    if (perf < 0) return '#ef4444';
    return '#8b98a5';
  };

  if (loading) {
    return (
      <div className="custom-watchlists loading">
        <div className="loading-spinner"></div>
        <p>Loading watchlists...</p>
      </div>
    );
  }

  return (
    <div className="custom-watchlists">
      {/* Header */}
      <div className="watchlists-header">
        <div className="header-left">
          <h2>Watchlists</h2>
          <p>Create and manage your custom stock watchlists</p>
        </div>
        <button className="create-btn" onClick={() => setShowCreateModal(true)}>
          + New Watchlist
        </button>
      </div>

      <div className="watchlists-layout">
        {/* Sidebar */}
        <div className="watchlists-sidebar">
          <div className="sidebar-header">
            <span>My Watchlists</span>
            <span className="count">{watchlists.length}</span>
          </div>
          <div className="watchlists-list">
            {watchlists.map(list => (
              <div
                key={list.id}
                className={`watchlist-item ${selectedList?.id === list.id ? 'active' : ''}`}
                onClick={() => setSelectedList(list)}
              >
                <span className="list-icon">{getThemeIcon(list.theme)}</span>
                <div className="list-info">
                  <span className="list-name">{list.name}</span>
                  <span className="list-meta">{list.symbolCount} stocks</span>
                </div>
                {list.isPublic && <span className="public-badge">Public</span>}
                <button
                  className="delete-btn"
                  onClick={(e) => { e.stopPropagation(); deleteWatchlist(list.id); }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="watchlists-main">
          {selectedList ? (
            <>
              {/* List Header */}
              <div className="list-header">
                <div className="list-title">
                  <span className="title-icon">{getThemeIcon(selectedList.theme)}</span>
                  <div>
                    <h3>{selectedList.name}</h3>
                    <div className="list-stats">
                      <span>{selectedList.symbolCount} stocks</span>
                      <span className="divider">•</span>
                      <span style={{ color: getPerformanceColor(selectedList.performance) }}>
                        {selectedList.performance >= 0 ? '+' : ''}{selectedList.performance.toFixed(1)}% (30d)
                      </span>
                    </div>
                  </div>
                </div>
                <div className="list-actions">
                  <button className="action-btn">
                    Edit
                  </button>
                  <button className="action-btn">
                    Share
                  </button>
                  <button className="action-btn">
                    Export
                  </button>
                </div>
              </div>

              {/* Stocks Table */}
              <div className="stocks-table">
                <div className="table-row header">
                  <span className="col-symbol">Symbol</span>
                  <span className="col-name">Name</span>
                  <span className="col-price">Price</span>
                  <span className="col-change">24h Change</span>
                  <span className="col-actions"></span>
                </div>
                {selectedList.stocks.map((stock, i) => (
                  <div key={i} className="table-row" onClick={() => onSelectStock && onSelectStock(stock.symbol)}>
                    <span className="col-symbol">{stock.symbol}</span>
                    <span className="col-name">{stock.name}</span>
                    <span className="col-price">{formatPrice(stock.price)}</span>
                    <span className="col-change">{formatPercent(stock.change)}</span>
                    <span className="col-actions">
                      <button className="remove-btn">×</button>
                    </span>
                  </div>
                ))}
              </div>

              {/* Add Stock */}
              <div className="add-stock-section">
                <h4>Add Stocks</h4>
                <div className="add-stock-form">
                  <input type="text" placeholder="Enter symbol (e.g., AAPL)" />
                  <button className="add-btn">Add</button>
                </div>
                <div className="suggested-stocks">
                  <span>Suggestions:</span>
                  {['MSFT', 'GOOGL', 'AMZN', 'META'].filter(s => !selectedList.stocks.find(st => st.symbol === s)).map(s => (
                    <button key={s} className="suggestion-chip">{s}</button>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h3>No Watchlist Selected</h3>
              <p>Select a watchlist from the sidebar or create a new one</p>
              <button className="create-btn" onClick={() => setShowCreateModal(true)}>
                + Create Watchlist
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="create-modal" onClick={e => e.stopPropagation()}>
            <h3>Create New Watchlist</h3>
            
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                placeholder="e.g., Growth Stocks"
                value={newWatchlist.name}
                onChange={(e) => setNewWatchlist({ ...newWatchlist, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Theme</label>
              <div className="theme-options">
                {[
                  { value: 'technology', label: 'Technology' },
                  { value: 'healthcare', label: 'Healthcare' },
                  { value: 'energy', label: 'Energy' },
                  { value: 'income', label: 'Income' },
                  { value: 'financial', label: 'Financial' },
                  { value: 'custom', label: 'Custom' },
                ].map(theme => (
                  <button
                    key={theme.value}
                    className={`theme-btn ${newWatchlist.theme === theme.value ? 'active' : ''}`}
                    onClick={() => setNewWatchlist({ ...newWatchlist, theme: theme.value })}
                  >
                    <span className="theme-label">{theme.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={newWatchlist.isPublic}
                  onChange={(e) => setNewWatchlist({ ...newWatchlist, isPublic: e.target.checked })}
                />
                <span>Make this watchlist public</span>
              </label>
            </div>

            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setShowCreateModal(false)}>Cancel</button>
              <button className="create-btn" onClick={createWatchlist}>Create Watchlist</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CustomWatchlists;

