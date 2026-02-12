import React, { useState, useEffect } from 'react';
import './EarningsCalendar.css';

function EarningsCalendar() {
  const [viewMode, setViewMode] = useState('upcoming');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(true);
  const [earningsData, setEarningsData] = useState([]);

  useEffect(() => {
    // Generate earnings calendar data
    const generateData = () => {
      const today = new Date();
      const earnings = [];
      
      // Generate data for next 30 days
      for (let i = 0; i < 30; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() + i);
        
        if (date.getDay() !== 0 && date.getDay() !== 6) {
          // Add 2-4 companies per trading day
          const numCompanies = Math.floor(Math.random() * 3) + 2;
          const companies = getCompaniesForDate();
          
          for (let j = 0; j < numCompanies; j++) {
            const company = companies[Math.floor(Math.random() * companies.length)];
            const epsEstimate = (Math.random() * 5 + 0.5).toFixed(2);
            const epsActual = i < 7 ? null : (parseFloat(epsEstimate) + (Math.random() - 0.5) * 0.5).toFixed(2);
            const revEstimate = (Math.random() * 50 + 5).toFixed(1);
            const surprise = epsActual ? ((parseFloat(epsActual) - parseFloat(epsEstimate)) / parseFloat(epsEstimate) * 100).toFixed(1) : null;
            
            earnings.push({
              id: `${date.toISOString().split('T')[0]}-${company.symbol}`,
              symbol: company.symbol,
              name: company.name,
              date: date.toISOString().split('T')[0],
              time: Math.random() > 0.5 ? 'Before Market' : 'After Market',
              epsEstimate: parseFloat(epsEstimate),
              epsActual: epsActual ? parseFloat(epsActual) : null,
              revEstimate: parseFloat(revEstimate),
              revActual: i < 7 ? null : parseFloat(revEstimate) * (1 + (Math.random() - 0.5) * 0.1),
              surprise: surprise ? parseFloat(surprise) : null,
              sector: company.sector,
              marketCap: company.marketCap,
              importance: Math.random() > 0.7 ? 'high' : Math.random() > 0.4 ? 'medium' : 'low'
            });
          }
        }
      }
      
      return earnings.sort((a, b) => new Date(a.date) - new Date(b.date));
    };

    const getCompaniesForDate = () => {
      return [
        { symbol: 'AAPL', name: 'Apple Inc.', sector: 'Technology', marketCap: '2.8T' },
        { symbol: 'MSFT', name: 'Microsoft Corp.', sector: 'Technology', marketCap: '2.5T' },
        { symbol: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology', marketCap: '1.7T' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer', marketCap: '1.5T' },
        { symbol: 'NVDA', name: 'NVIDIA Corp.', sector: 'Technology', marketCap: '1.2T' },
        { symbol: 'META', name: 'Meta Platforms', sector: 'Technology', marketCap: '800B' },
        { symbol: 'TSLA', name: 'Tesla Inc.', sector: 'Automotive', marketCap: '750B' },
        { symbol: 'BRK.B', name: 'Berkshire Hathaway', sector: 'Financial', marketCap: '780B' },
        { symbol: 'JPM', name: 'JPMorgan Chase', sector: 'Financial', marketCap: '490B' },
        { symbol: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare', marketCap: '380B' },
        { symbol: 'V', name: 'Visa Inc.', sector: 'Financial', marketCap: '520B' },
        { symbol: 'PG', name: 'Procter & Gamble', sector: 'Consumer', marketCap: '360B' },
        { symbol: 'UNH', name: 'UnitedHealth', sector: 'Healthcare', marketCap: '480B' },
        { symbol: 'HD', name: 'Home Depot', sector: 'Retail', marketCap: '340B' },
        { symbol: 'BAC', name: 'Bank of America', sector: 'Financial', marketCap: '270B' },
      ];
    };

    const timer = setTimeout(() => {
      setEarningsData(generateData());
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, []);

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const getDaysUntil = (dateStr) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const target = new Date(dateStr);
    const diff = Math.ceil((target - today) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(num);
  };

  const formatNumber = (num) => {
    if (num >= 1000000000000) return `$${(num / 1000000000000).toFixed(1)}T`;
    if (num >= 1000000000) return `$${(num / 1000000000).toFixed(1)}B`;
    if (num >= 1000000) return `$${(num / 1000000).toFixed(1)}M`;
    return `$${num}`;
  };

  const filteredData = earningsData.filter(item => {
    if (viewMode === 'upcoming') {
      return getDaysUntil(item.date) >= 0;
    } else if (viewMode === 'past') {
      return getDaysUntil(item.date) < 0;
    }
    return true;
  });

  const groupedData = filteredData.reduce((acc, item) => {
    if (!acc[item.date]) {
      acc[item.date] = [];
    }
    acc[item.date].push(item);
    return acc;
  }, {});

  const upcomingCount = earningsData.filter(e => getDaysUntil(e.date) >= 0 && getDaysUntil(e.date) <= 7).length;
  const highImpactCount = earningsData.filter(e => e.importance === 'high' && getDaysUntil(e.date) >= 0).length;

  if (loading) {
    return (
      <div className="earnings-calendar loading">
        <div className="loading-spinner"></div>
        <p>Loading earnings calendar...</p>
      </div>
    );
  }

  return (
    <div className="earnings-calendar">
      {/* Header */}
      <div className="earnings-header">
        <div className="header-left">
          <h2>Earnings Calendar</h2>
          <p>Upcoming earnings dates and analyst estimates</p>
        </div>
        <div className="header-right">
          <div className="header-stats">
            <div className="stat-item">
              <span className="stat-value">{upcomingCount}</span>
              <span className="stat-label">This Week</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{highImpactCount}</span>
              <span className="stat-label">High Impact</span>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="earnings-filters">
        <div className="view-toggle">
          {['upcoming', 'past', 'all'].map(mode => (
            <button
              key={mode}
              className={`filter-btn ${viewMode === mode ? 'active' : ''}`}
              onClick={() => setViewMode(mode)}
            >
              {mode.charAt(0).toUpperCase() + mode.slice(1)}
            </button>
          ))}
        </div>
        <div className="date-filter">
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="calendar-grid">
        {Object.entries(groupedData)
          .sort(([a], [b]) => new Date(a) - new Date(b))
          .map(([date, items]) => (
            <div key={date} className="calendar-day">
              <div className="day-header">
                <span className="day-date">{formatDate(date)}</span>
                <span className="day-count">{items.length} companies</span>
              </div>
              <div className="day-content">
                {items.map(item => {
                  const daysUntil = getDaysUntil(item.date);
                  return (
                    <div key={item.id} className={`earnings-card ${item.importance}`}>
                      <div className="card-main">
                        <div className="card-header">
                          <span className="symbol">{item.symbol}</span>
                          <span className="time-badge">{item.time}</span>
                        </div>
                        <span className="company-name">{item.name}</span>
                        <div className="company-meta">
                          <span className="sector">{item.sector}</span>
                          <span className="market-cap">{item.marketCap}</span>
                        </div>
                      </div>

                      <div className="estimates">
                        <div className="estimate-row">
                          <span className="estimate-label">EPS Estimate</span>
                          <span className="estimate-value">
                            {item.epsActual !== null ? (
                              <span className={item.surprise > 0 ? 'positive' : item.surprise < 0 ? 'negative' : ''}>
                                {formatCurrency(item.epsActual)}
                                {item.surprise !== null && (
                                  <span className="surprise-badge">
                                    {item.surprise > 0 ? '+' : ''}{item.surprise}%
                                  </span>
                                )}
                              </span>
                            ) : (
                              formatCurrency(item.epsEstimate)
                            )}
                          </span>
                        </div>
                        <div className="estimate-row">
                          <span className="estimate-label">Revenue Estimate</span>
                          <span className="estimate-value">
                            {formatNumber(item.revEstimate)}B
                          </span>
                        </div>
                      </div>

                      <div className="card-footer">
                        {daysUntil === 0 && (
                          <span className="today-badge">Today</span>
                        )}
                        {daysUntil === 1 && (
                          <span className="tomorrow-badge">Tomorrow</span>
                        )}
                        {daysUntil > 1 && daysUntil <= 7 && (
                          <span className="week-badge">In {daysUntil} days</span>
                        )}
                        {item.importance === 'high' && (
                          <span className="importance-badge high">High Impact</span>
                        )}
                        {item.importance === 'medium' && (
                          <span className="importance-badge medium">Medium</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
      </div>

      {/* Earnings Summary */}
      <div className="earnings-summary">
        <h3>Market-Wide Earnings Expectations</h3>
        <div className="summary-grid">
          <div className="summary-card">
            <h4>Average EPS Growth</h4>
            <span className="summary-value positive">+8.2%</span>
            <span className="summary-trend">vs last quarter</span>
          </div>
          <div className="summary-card">
            <h4>Expected Revenue Growth</h4>
            <span className="summary-value">+5.7%</span>
            <span className="summary-trend">YoY</span>
          </div>
          <div className="summary-card">
            <h4>Positive Surprise Rate</h4>
            <span className="summary-value">68%</span>
            <span className="summary-trend">historical avg</span>
          </div>
          <div className="summary-card">
            <h4>Most Active Sector</h4>
            <span className="summary-value">Technology</span>
            <span className="summary-trend">42 reports</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default EarningsCalendar;

