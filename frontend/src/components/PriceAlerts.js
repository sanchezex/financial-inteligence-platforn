
import React, { useState, useEffect } from 'react';
import './PriceAlerts.css';

function PriceAlerts() {
  const [alerts, setAlerts] = useState([
    { id: 1, symbol: 'AAPL', type: 'above', price: 185.00, currentPrice: 178.50, active: true, created: '2024-01-10' },
    { id: 2, symbol: 'NVDA', type: 'below', price: 480.00, currentPrice: 495.20, active: true, created: '2024-01-08' },
    { id: 3, symbol: 'MSFT', type: 'change', price: 5, currentPrice: 378.90, active: false, created: '2024-01-05' },
    { id: 4, symbol: 'GOOGL', type: 'above', price: 150.00, currentPrice: 141.80, active: true, created: '2024-01-12' },
  ]);

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAlert, setNewAlert] = useState({ symbol: '', type: 'above', price: '', percentChange: '' });

  useEffect(() => {
    const timer = setInterval(() => {
      setAlerts(prev => prev.map(alert => ({
        ...alert,
        currentPrice: alert.currentPrice + (Math.random() - 0.5) * 2
      })));
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getAlertStatus = (alert) => {
    if (!alert.active) return 'paused';
    if (alert.type === 'above' && alert.currentPrice >= alert.price) return 'triggered';
    if (alert.type === 'below' && alert.currentPrice <= alert.price) return 'triggered';
    return 'active';
  };

  const toggleAlert = (id) => {
    setAlerts(prev => prev.map(alert =>
      alert.id === id ? { ...alert, active: !alert.active } : alert
    ));
  };

  const deleteAlert = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const createAlert = () => {
    if (newAlert.symbol && newAlert.price) {
      const alert = {
        id: Date.now(),
        symbol: newAlert.symbol.toUpperCase(),
        type: newAlert.type,
        price: parseFloat(newAlert.type === 'change' ? newAlert.percentChange : newAlert.price),
        currentPrice: { 'AAPL': 178, 'MSFT': 378, 'GOOGL': 141, 'NVDA': 495, 'AMZN': 178, 'TSLA': 245 }[newAlert.symbol.toUpperCase()] || 100,
        active: true,
        created: new Date().toISOString().split('T')[0]
      };
      setAlerts([...alerts, alert]);
      setNewAlert({ symbol: '', type: 'above', price: '', percentChange: '' });
      setShowCreateModal(false);
    }
  };

  const triggeredCount = alerts.filter(a => getAlertStatus(a) === 'triggered').length;
  const activeCount = alerts.filter(a => getAlertStatus(a) === 'active').length;

  return (
    <div className="price-alerts">
      <div className="alerts-header">
        <div>
          <h2>Price Alerts</h2>
          <p>Get notified when stocks reach your target prices</p>
        </div>
        <button className="create-btn" onClick={() => setShowCreateModal(true)}>
          + New Alert
        </button>
      </div>

      <div className="alerts-stats">
        <div className="stat-item">
          <span className="stat-value">{activeCount}</span>
          <span className="stat-label">Active</span>
        </div>
        <div className="stat-item triggered">
          <span className="stat-value">{triggeredCount}</span>
          <span className="stat-label">Triggered</span>
        </div>
        <div className="stat-item">
          <span className="stat-value">{alerts.length}</span>
          <span className="stat-label">Total</span>
        </div>
      </div>

      <div className="alerts-list">
        {alerts.map(alert => {
          const status = getAlertStatus(alert);
          const progress = Math.min(100, Math.abs((alert.currentPrice - alert.price) / (alert.price || 1)) * 100);

          return (
            <div key={alert.id} className={`alert-card ${status}`}>
              <div className="alert-main">
                <div className="alert-symbol">
                  <span className="symbol">{alert.symbol}</span>
                  <span className="current-price">{formatPrice(alert.currentPrice)}</span>
                </div>
                <div className="alert-condition">
                  {alert.type === 'above' && (
                    <>
                      <span className="condition-icon">⬆</span>
                      <span>Price goes above {formatPrice(alert.price)}</span>
                    </>
                  )}
                  {alert.type === 'below' && (
                    <>
                      <span className="condition-icon">⬇</span>
                      <span>Price goes below {formatPrice(alert.price)}</span>
                    </>
                  )}
                  {alert.type === 'change' && (
                    <>
                      <span className="condition-icon">%</span>
                      <span>Change by {alert.price}%</span>
                    </>
                  )}
                </div>
              </div>

              <div className="alert-progress">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${progress}%`,
                      background: alert.type === 'above'
                        ? (alert.currentPrice >= alert.price ? '#22c55e' : '#1d9bf0')
                        : (alert.currentPrice <= alert.price ? '#22c55e' : '#1d9bf0')
                    }}
                  ></div>
                </div>
                <span className="progress-target">
                  Target: {formatPrice(alert.price)}
                </span>
              </div>

              <div className="alert-actions">
                <button
                  className={`toggle-btn ${alert.active ? 'active' : 'paused'}`}
                  onClick={() => toggleAlert(alert.id)}
                >
                  {alert.active ? 'Active' : 'Paused'}
                </button>
                <button className="delete-btn" onClick={() => deleteAlert(alert.id)}>
                  Delete
                </button>
              </div>

              {status === 'triggered' && (
                <div className="triggered-badge">
                  <span>Triggered!</span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="create-alert-modal" onClick={e => e.stopPropagation()}>
            <h3>Create Price Alert</h3>

            <div className="form-group">
              <label>Symbol</label>
              <input
                type="text"
                placeholder="e.g., AAPL"
                value={newAlert.symbol}
                onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Condition</label>
              <select
                value={newAlert.type}
                onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value })}
              >
                <option value="above">Price goes above</option>
                <option value="below">Price goes below</option>
                <option value="change">Percent change</option>
              </select>
            </div>

            <div className="form-group">
              <label>{newAlert.type === 'change' ? 'Percentage' : 'Target Price'}</label>
              <input
                type="number"
                placeholder={newAlert.type === 'change' ? 'e.g., 5' : 'e.g., 185.00'}
                value={newAlert.type === 'change' ? newAlert.percentChange : newAlert.price}
                onChange={(e) => setNewAlert({
                  ...newAlert,
                  [newAlert.type === 'change' ? 'percentChange' : 'price']: e.target.value
                })}
              />
            </div>

            <div className="modal-actions">
              <button className="cancel-btn" onClick={() => setShowCreateModal(false)}>
                Cancel
              </button>
              <button className="submit-btn" onClick={createAlert}>
                Create Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PriceAlerts;

