import React, { useState, useEffect, Suspense, lazy } from 'react';
import './App.css';

// Lazy loaded components
const ShippingMap = lazy(() => import('./components/ShippingMap'));
const StockDetailModal = lazy(() => import('./components/StockDetailModal'));
const AuthModal = lazy(() => import('./components/AuthModal'));
const Portfolio = lazy(() => import('./components/Portfolio'));
const AdvancedChart = lazy(() => import('./components/AdvancedChart'));
const StockCompare = lazy(() => import('./components/StockCompare'));
const OptionsChain = lazy(() => import('./components/OptionsChain'));
const PriceAlerts = lazy(() => import('./components/PriceAlerts'));
const AISignals = lazy(() => import('./components/AISignals'));
const NaturalLanguageSearch = lazy(() => import('./components/NaturalLanguageSearch'));
const AnomalyDetection = lazy(() => import('./components/AnomalyDetection'));
const TradeIdeasFeed = lazy(() => import('./components/TradeIdeasFeed'));
const Markets = lazy(() => import('./components/Markets'));

// Context
import { AuthProvider, useAuth } from './context/AuthContext';

// Services
import PriceStreamService from './services/PriceStreamService'; 

function AppContent() {
  const { user, isAuthenticated, login, register, logout } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [watchlist, setWatchlist] = useState([
    'NSE20', 'NBK', 'KCB', 'SCOM', 'EABL', 'BAT', 'GLD', 'ICDC', 'KQ', 'ORCH'
  ]); // Nairobi Stock Exchange stocks
  const [selectedStock, setSelectedStock] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [showPortfolio, setShowPortfolio] = useState(false);
  const [realtimePrices, setRealtimePrices] = useState({});
  const [isConnected, setIsConnected] = useState(false);

  // Initialize real-time price streaming
  useEffect(() => {
    try {
      PriceStreamService.connect();
      setIsConnected(true);

      const unsubscribe = PriceStreamService.subscribeAll((data) => {
        setRealtimePrices(prev => ({
          ...prev,
          [data.symbol]: data
        }));
      });

      return () => {
        unsubscribe();
        PriceStreamService.disconnect();
      };
    } catch (error) {
      console.error('Failed to connect to price stream:', error);
      setIsConnected(false);
    }
  }, []);

  // Loading simulation
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES'
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

  const handleStockClick = (symbol) => {
    setSelectedStock(symbol);
  };

  const handleLogin = async (email, password) => {
    await login(email, password);
    setShowAuthModal(false);
  };

  const handleRegister = async (name, email, password) => {
    await register(name, email, password);
    setShowAuthModal(false);
  };

const navItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'markets', label: 'Markets' },
    { id: 'stocks', label: 'Stocks' },
    { id: 'trade_ideas', label: 'Trade Ideas' },
    { id: 'portfolio', label: 'Portfolio', requiresAuth: true },
    { id: 'compare', label: 'Compare' },
    { id: 'options', label: 'Options' },
    { id: 'alerts', label: 'Alerts' },
    { id: 'ai_signals', label: 'AI Signals' },
    { id: 'anomaly', label: 'Anomalies' },
    { id: 'search', label: 'Search' },
    { id: 'macro', label: 'Macro' },
    { id: 'shipping', label: 'Shipping' },
    { id: 'news', label: 'News' },
    { id: 'analytics', label: 'Analytics' },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'shipping':
        return (
          <div style={{ height: 'calc(100vh - 200px)', minHeight: '600px' }}>
            <ShippingMap />
          </div>
        );

      case 'portfolio':
        if (!isAuthenticated) {
          return (
            <div className="auth-required">
              <div className="auth-message">
                <span className="auth-icon"></span>
                <h2>Sign In Required</h2>
                <p>Please sign in to view your portfolio</p>
                <button className="auth-btn" onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}>
                  Sign In
                </button>
              </div>
            </div>
          );
        }
        return <Suspense fallback={<div>Loading Portfolio...</div>}>
          <Portfolio isOpen={showPortfolio} onClose={() => setShowPortfolio(false)} />
        </Suspense>; 

      case 'compare':
        return <StockCompare />;

      case 'options':
        return <OptionsChain symbol="AAPL" />;

      case 'alerts':
        return <PriceAlerts />;

      case 'ai_signals':
        return <AISignals />;

      case 'search':
        return <NaturalLanguageSearch />;

case 'anomaly':
        return <AnomalyDetection />;

      case 'trade_ideas':
        return <TradeIdeasFeed />;

      case 'markets':
        return <Suspense fallback={<div>Loading Markets...</div>}>
          <Markets />
        </Suspense>; 

      case 'stocks':
        return (
          <>
            <AdvancedChart symbol="AAPL" />
            <div style={{ marginTop: '24px' }}>
              <StockCompare />
            </div>
          </>
        );

      default:
        return (
          <>
            <section className="market-overview">
              <div className="market-card indices">
                <h3>Major Indices</h3>
                <div className="indices-grid">
                  {[
                    { symbol: 'NSE20', name: 'NSE 20 Index', price: realtimePrices['NSE20']?.price || 1850.2, change: realtimePrices['NSE20']?.changePercent || 0.45 },
                    { symbol: 'NBK', name: 'NCBA Bank', price: realtimePrices['NBK']?.price || 32.5, change: realtimePrices['NBK']?.changePercent || -0.3 },
                    { symbol: 'KCB', name: 'KCB Group', price: realtimePrices['KCB']?.price || 15.8, change: realtimePrices['KCB']?.changePercent || 1.2 },
                    { symbol: 'SCOM', name: 'Safaricom', price: realtimePrices['SCOM']?.price || 13.2, change: realtimePrices['SCOM']?.changePercent || 0.8 },
                  ].map(index => (
                    <div
                      key={index.symbol}
                      className="index-item"
                      onClick={() => handleStockClick(index.symbol)}
                      style={{ cursor: 'pointer' }}
                    >
                      <span className="index-name">{index.name}</span>
                      <span className="index-price">{formatPrice(index.price)}</span>
                      <span className="index-change">{formatPercent(index.change)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </section>

            <section className="watchlist-section">
              <div className="section-header">
                <h2>Watchlist</h2>
                <button className="btn-secondary">Edit</button>
              </div>
              <div className="watchlist-grid">
                {watchlist.map(symbol => {
                  const priceData = realtimePrices[symbol] || {};
                  return (
                    <div
                      key={symbol}
                      className="watchlist-item"
                      onClick={() => handleStockClick(symbol)}
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="stock-info">
                        <span className="stock-symbol">{symbol}</span>
                        <span className="stock-price">{formatPrice(priceData.price || 100 + Math.random() * 400)}</span>
                      </div>
                      <div className="stock-change">
                        {formatPercent(priceData.changePercent || (Math.random() - 0.5) * 10)}
                      </div>
                      <div className="stock-chart">
                        <svg viewBox="0 0 100 30" className="mini-chart">
                          <path
                            d="M0,15 L10,15 L15,12 L25,18 L35,10 L45,22 L55,8 L65,20 L75,5 L85,15 L100,10"
                            fill="none"
                            stroke={Math.random() > 0.5 ? '#22c55e' : '#ef4444'}
                            strokeWidth="1.5"
                          />
                        </svg>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            <section className="quick-stats">
              <div className="stats-grid">
                <div className="stat-card">
                  <h4>Market Sentiment</h4>
                  <div className="sentiment-meter">
                    <div className="sentiment-bar">
                      <div className="sentiment-fill" style={{ width: '62%' }}></div>
                    </div>
                    <span className="sentiment-label">Bullish (62%)</span>
                  </div>
                </div>
                <div className="stat-card">
                  <h4>Top Sectors</h4>
                  <div className="sector-list">
                    {[
                      { name: 'Technology', change: '+1.8%' },
                      { name: 'Energy', change: '+1.2%' },
                      { name: 'Healthcare', change: '+0.8%' },
                    ].map((sector, i) => (
                      <div key={i} className="sector-item">
                        <span>{sector.name}</span>
                        <span className="positive">{sector.change}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="stat-card">
                  <h4>Economic Calendar</h4>
                  <div className="events-list">
                    {[
                      { event: 'FOMC Meeting', date: 'Jan 30-31' },
                      { event: 'GDP Release', date: 'Jan 25' },
                      { event: 'CPI Data', date: 'Feb 15' },
                    ].map((event, i) => (
                      <div key={i} className="event-item">
                        <span>{event.event}</span>
                        <span className="event-date">{event.date}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="stat-card">
                  <h4>AI Insights</h4>
                  <div className="insights-list">
                    <div className="insight-item" onClick={() => setActiveTab('ai_signals')} style={{ cursor: 'pointer' }}>
                      <span className="insight-icon"></span>
                      <span>Tech sector showing strong momentum</span>
                    </div>
                    <div className="insight-item">
                      <span className="insight-icon"></span>
                      <span>Monitor Fed commentary closely</span>
                    </div>
                    <div className="insight-item" onClick={() => setActiveTab('anomaly')} style={{ cursor: 'pointer' }}>
                      <span className="insight-icon"></span>
                      <span>Volume spike detected in NVDA</span>
                    </div>
                  </div>
                </div>
              </div>
            </section>
          </>
        );
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="logo">
          <div className="logo-icon">FI</div>
          <span>Financial Intel</span>
        </div>

        <nav className="nav-menu">
          {navItems.map(item => {
            if (item.requiresAuth && !isAuthenticated) return null;
            return (
              <button
                key={item.id}
                className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span className="nav-label">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="connection-status">
            <span className={`status-dot ${isConnected ? 'connected' : ''}`}></span>
            <span>{isConnected ? 'Live' : 'Offline'}</span>
          </div>
          <div className="market-status">
            <span className="status-dot open"></span>
            <span>Markets Open</span>
          </div>
          {isAuthenticated ? (
            <div className="user-menu">
              <button className="user-btn" onClick={() => setShowPortfolio(true)}>
                <span className="user-avatar">{user?.name?.[0]?.toUpperCase() || 'U'}</span>
                <span className="user-name">{user?.name || 'User'}</span>
              </button>
              <button className="logout-btn" onClick={logout}>Logout</button>
            </div>
          ) : (
            <button className="login-btn" onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}>
              Sign In
            </button>
          )}
        </div>
      </aside>

      <main className="main-content">
        <header className="header">
          <div className="header-left">
            <h1>{navItems.find(n => n.id === activeTab)?.label || activeTab}</h1>
<span className="header-subtitle">NSE Real-time Intelligence (HH:MM:SS)</span>
          </div>
          <div className="header-right">
            <div className="search-bar" onClick={() => setActiveTab('search')} style={{ cursor: 'pointer' }}>
              <input type="text" placeholder="Search symbols, news..." readOnly />
            </div>
            <button className="header-btn" onClick={() => setActiveTab('alerts')}>Alerts</button>
            <button className="header-btn" onClick={() => setActiveTab('portfolio')}>Portfolio</button>
            {isAuthenticated ? (
              <button className="header-btn user-btn-small" onClick={() => setShowPortfolio(true)}>
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </button>
            ) : (
              <button className="header-btn" onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}>
                Sign In
              </button>
            )}
          </div>
        </header>

        <div className="content">
          {renderContent()}
        </div>
      </main>

      {selectedStock && (
        <StockDetailModal
          symbol={selectedStock}
          onClose={() => setSelectedStock(null)}
        />
      )}

      {showAuthModal && (
        <AuthModal
          mode={authMode}
          onClose={() => setShowAuthModal(false)}
          onLogin={handleLogin}
          onRegister={handleRegister}
        />
      )}
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Suspense fallback={<div className="loading-screen">
        <div className="loading-spinner"></div>
        <div>Loading modules...</div>
      </div>}>
        <AppContent />
      </Suspense>
    </AuthProvider>
  ); 
}

export default App;

