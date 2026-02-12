import React, { useState, useEffect } from 'react';
import './InstitutionalHoldings.css';

function InstitutionalHoldings({ symbol = 'AAPL' }) {
  const [activeTab, setActiveTab] = useState('ownership');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Generate institutional holdings data
    const generateData = () => {
      return {
        companyInfo: {
          symbol,
          name: 'Apple Inc.',
          totalShares: 15550000000,
          publicFloat: 15420000000,
          insiderOwnership: 0.07,
          institutionalOwnership: 59.8,
        },
        ownershipSummary: {
          totalInstitutions: 4892,
          totalSharesHeld: 9310000000,
          totalValue: 1660000000000,
          change: 2.3,
          newPositions: 234,
          soldOut: 156,
        },
        topHolders: [
          { rank: 1, name: 'Vanguard Group', shares: 1312000000, percent: 8.44, change: 1.2, value: 234500000000 },
          { rank: 2, name: 'BlackRock Inc', shares: 1145000000, percent: 7.36, change: 0.8, value: 204600000000 },
          { rank: 3, name: 'State Street Corp', shares: 786000000, percent: 5.05, change: -0.3, value: 140500000000 },
          { rank: 4, name: 'FMR LLC', shares: 478000000, percent: 3.07, change: 2.1, value: 85400000000 },
          { rank: 5, name: 'Geode Capital Mgmt', shares: 356000000, percent: 2.29, change: 0.5, value: 63600000000 },
          { rank: 6, name: 'Morgan Stanley', shares: 298000000, percent: 1.92, change: -1.2, value: 53200000000 },
          { rank: 7, name: 'Bank of America', shares: 267000000, percent: 1.72, change: 0.9, value: 47700000000 },
          { rank: 8, name: 'JPMorgan Chase', shares: 245000000, percent: 1.58, change: 1.5, value: 43800000000 },
          { rank: 9, name: 'Goldman Sachs', shares: 212000000, percent: 1.36, change: -0.7, value: 37900000000 },
          { rank: 10, name: 'Charles Schwab', shares: 198000000, percent: 1.27, change: 0.3, value: 35400000000 },
        ],
        recentFilings: [
          { id: 1, date: '2024-01-15', type: '13F', institution: 'Vanguard Group', shares: 1312000000, action: 'Increased', percent: 8.44 },
          { id: 2, date: '2024-01-12', type: '13F', institution: 'BlackRock Inc', shares: 1145000000, action: 'Increased', percent: 7.36 },
          { id: 3, date: '2024-01-11', type: '4', institution: 'Insider', shares: 50000, action: 'Sold', percent: 0.00 },
          { id: 4, date: '2024-01-10', type: '13F', institution: 'State Street', shares: 786000000, action: 'Decreased', percent: 5.05 },
          { id: 5, date: '2024-01-08', type: '13D', institution: 'ValueAct', shares: 45000000, action: 'Increased', percent: 0.29 },
        ],
        ownershipHistory: [
          { period: 'Q4 2023', institutional: 59.8, insider: 0.07, retail: 40.13 },
          { period: 'Q3 2023', institutional: 58.2, insider: 0.08, retail: 41.72 },
          { period: 'Q2 2023', institutional: 57.5, insider: 0.09, retail: 42.41 },
          { period: 'Q1 2023', institutional: 56.8, insider: 0.10, retail: 43.10 },
          { period: 'Q4 2022', institutional: 55.2, insider: 0.11, retail: 44.69 },
        ],
        sectorAllocation: [
          { sector: 'Technology', percent: 45.2 },
          { sector: 'Financial', percent: 18.5 },
          { sector: 'Healthcare', percent: 12.3 },
          { sector: 'Consumer', percent: 10.8 },
          { sector: 'Industrial', percent: 5.2 },
          { sector: 'Energy', percent: 3.1 },
          { sector: 'Other', percent: 4.9 },
        ],
        etfHoldings: [
          { symbol: 'SPY', name: 'SPDR S&P 500 ETF', shares: 245000000, value: 112000000000 },
          { symbol: 'QQQ', name: 'Invesco QQQ Trust', shares: 78000000, value: 35800000000 },
          { symbol: 'VTI', name: 'Vanguard Total Stock Mkt', shares: 67000000, value: 15600000000 },
          { symbol: 'VOO', name: 'Vanguard S&P 500 ETF', shares: 45000000, value: 19800000000 },
          { symbol: 'IVV', name: 'iShares Core S&P 500', shares: 38000000, value: 16700000000 },
        ],
      };
    };

    const timer = setTimeout(() => {
      setData(generateData());
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [symbol]);

  const formatNumber = (num) => {
    if (num >= 1000000000000) return `$${(num / 1000000000000).toFixed(2)}T`;
    if (num >= 1000000000) return `$${(num / 1000000000).toFixed(2)}B`;
    if (num >= 1000000) return `$${(num / 1000000).toFixed(2)}M`;
    if (num >= 1000) return `$${(num / 1000).toFixed(2)}K`;
    return num.toString();
  };

  const formatPercent = (num) => {
    return `${num.toFixed(2)}%`;
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="institutional-holdings loading">
        <div className="loading-spinner"></div>
        <p>Loading institutional data...</p>
      </div>
    );
  }

  return (
    <div className="institutional-holdings">
      {/* Header */}
      <div className="holdings-header">
        <div className="header-left">
          <h2>Institutional Holdings</h2>
          <p>{data.companyInfo.symbol} - SEC filings and institutional ownership</p>
        </div>
        <div className="header-right">
          <div className="quick-stats">
            <div className="stat-item">
              <span className="stat-value">{formatNumber(data.ownershipSummary.totalValue)}</span>
              <span className="stat-label">Total Value</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{data.ownershipSummary.totalInstitutions}</span>
              <span className="stat-label">Institutions</span>
            </div>
            <div className="stat-item">
              <span className={`stat-value ${data.ownershipSummary.change >= 0 ? 'positive' : 'negative'}`}>
                {data.ownershipSummary.change >= 0 ? '+' : ''}{data.ownershipSummary.change}%
              </span>
              <span className="stat-label">Change</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="holdings-tabs">
        {['ownership', 'filings', 'history', 'etfs'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'ownership' && 'Ownership'}
            {tab === 'filings' && 'SEC Filings'}
            {tab === 'history' && 'History'}
            {tab === 'etfs' && 'ETF Holdings'}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="holdings-content">
        {activeTab === 'ownership' && (
          <div className="ownership-section">
            {/* Ownership Breakdown */}
            <div className="ownership-breakdown">
              <div className="breakdown-chart">
                <svg viewBox="0 0 200 200">
                  <circle cx="100" cy="100" r="80" fill="none" stroke="#2f3336" strokeWidth="30" />
                  <circle
                    cx="100" cy="100" r="80"
                    fill="none"
                    stroke="#22c55e"
                    strokeWidth="30"
                    strokeDasharray={`${data.companyInfo.institutionalOwnership * 5.02} 502`}
                    transform="rotate(-90 100 100)"
                  />
                  <circle
                    cx="100" cy="100" r="80"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="30"
                    strokeDasharray={`${data.companyInfo.insiderOwnership * 5.02} 502`}
                    strokeDashoffset={`${-data.companyInfo.institutionalOwnership * 5.02}`}
                    transform="rotate(-90 100 100)"
                  />
                </svg>
                <div className="chart-center">
                  <span className="center-value">{data.companyInfo.institutionalOwnership + data.companyInfo.insiderOwnership}%</span>
                  <span className="center-label">Institutional</span>
                </div>
              </div>
              <div className="breakdown-legend">
                <div className="legend-item">
                  <span className="legend-color institutional"></span>
                  <span className="legend-text">Institutional Ownership</span>
                  <span className="legend-value">{data.companyInfo.institutionalOwnership}%</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color insider"></span>
                  <span className="legend-text">Insider Ownership</span>
                  <span className="legend-value">{data.companyInfo.insiderOwnership}%</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color retail"></span>
                  <span className="legend-text">Retail / Other</span>
                  <span className="legend-value">{(100 - data.companyInfo.institutionalOwnership - data.companyInfo.insiderOwnership).toFixed(2)}%</span>
                </div>
              </div>
            </div>

            {/* Activity Summary */}
            <div className="activity-summary">
              <div className="activity-item">
                <span className="activity-icon new">New</span>
                <div className="activity-info">
                  <span className="activity-value">{data.ownershipSummary.newPositions}</span>
                  <span className="activity-label">New Positions</span>
                </div>
              </div>
              <div className="activity-item">
                <span className="activity-icon sold">Sold</span>
                <div className="activity-info">
                  <span className="activity-value">{data.ownershipSummary.soldOut}</span>
                  <span className="activity-label">Sold Out</span>
                </div>
              </div>
              <div className="activity-item">
                <span className="activity-icon increased">Changed</span>
                <div className="activity-info">
                  <span className="activity-value">{data.ownershipSummary.totalInstitutions - data.ownershipSummary.newPositions - data.ownershipSummary.soldOut}</span>
                  <span className="activity-label">Increased/Decreased</span>
                </div>
              </div>
            </div>

            {/* Top Holders Table */}
            <div className="holders-table-section">
              <h3>Top Institutional Holders</h3>
              <div className="holders-table">
                <div className="table-row header">
                  <span className="rank">#</span>
                  <span className="institution">Institution</span>
                  <span className="shares">Shares</span>
                  <span className="percent">% Owned</span>
                  <span className="change">Change</span>
                  <span className="value">Value</span>
                </div>
                {data.topHolders.map(holder => (
                  <div key={holder.rank} className="table-row">
                    <span className="rank">{holder.rank}</span>
                    <span className="institution">{holder.name}</span>
                    <span className="shares">{formatNumber(holder.shares)}</span>
                    <span className="percent">{holder.percent}%</span>
                    <span className={`change ${holder.change >= 0 ? 'positive' : 'negative'}`}>
                      {holder.change >= 0 ? '+' : ''}{holder.change}%
                    </span>
                    <span className="value">{formatNumber(holder.value)}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'filings' && (
          <div className="filings-section">
            <div className="filings-header">
              <h3>Recent SEC Filings</h3>
              <div className="filings-legend">
                <span className="legend-item"><span className="dot type-13f"></span> 13F (Quarterly)</span>
                <span className="legend-item"><span className="dot type-4"></span> 4 (Insider)</span>
                <span className="legend-item"><span className="dot type-13d"></span> 13D (5%+ Owner)</span>
              </div>
            </div>

            <div className="filings-list">
              {data.recentFilings.map(filing => (
                <div key={filing.id} className={`filing-card type-${filing.type.toLowerCase()}`}>
                  <div className="filing-main">
                    <div className="filing-type">
                      <span className="type-badge">{filing.type}</span>
                      <span className="filing-date">{formatDate(filing.date)}</span>
                    </div>
                    <div className="filing-institution">
                      <span className="institution-name">{filing.institution}</span>
                      <span className="institution-action">{filing.action}</span>
                    </div>
                  </div>
                  <div className="filing-details">
                    <div className="detail-item">
                      <span className="detail-label">Shares</span>
                      <span className="detail-value">{formatNumber(filing.shares)}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Ownership</span>
                      <span className="detail-value">{filing.percent}%</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Action</span>
                      <span className={`detail-value ${filing.action === 'Increased' ? 'positive' : filing.action === 'Sold' ? 'negative' : ''}`}>
                        {filing.action}
                      </span>
                    </div>
                  </div>
                  <button className="view-filing-btn">View Filing</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="history-section">
            <h3>Ownership History</h3>
            <div className="history-chart">
              <svg viewBox="0 0 600 200" className="ownership-svg">
                {data.ownershipHistory.map((period, i) => {
                  const x = (i / (data.ownershipHistory.length - 1)) * 550;
                  const institutionalY = 180 - (period.institutional / 70) * 150;
                  const insiderY = 180 - (period.insider / 70) * 150;
                  const retailY = 180 - (period.retail / 70) * 150;
                  
                  return (
                    <g key={i}>
                      {/* Bars */}
                      <rect x={x - 30} y={institutionalY} width="25" height={180 - institutionalY} fill="#22c55e" opacity="0.8" />
                      <rect x={x - 5} y={retailY} width="25" height={180 - retailY} fill="#8b98a5" opacity="0.5" />
                      
                      {/* Labels */}
                      <text x={x} y="195" textAnchor="middle" fill="#8b98a5" fontSize="11">{period.period}</text>
                    </g>
                  );
                })}
                
                {/* Legend */}
                <rect x="480" y="10" width="12" height="12" fill="#22c55e" opacity="0.8" />
                <text x="495" y="20" fill="#8b98a5" fontSize="11">Institutional</text>
                <rect x="480" y="28" width="12" height="12" fill="#8b98a5" opacity="0.5" />
                <text x="495" y="38" fill="#8b98a5" fontSize="11">Retail</text>
              </svg>
            </div>

            <div className="history-table">
              <div className="table-row header">
                <span>Period</span>
                <span>Institutional</span>
                <span>Insider</span>
                <span>Retail</span>
              </div>
              {data.ownershipHistory.map((period, i) => (
                <div key={i} className="table-row">
                  <span>{period.period}</span>
                  <span className="positive">{period.institutional}%</span>
                  <span>{period.insider}%</span>
                  <span>{period.retail}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'etfs' && (
          <div className="etfs-section">
            <h3>ETF Holdings</h3>
            <p className="section-description">ETFs that hold {data.companyInfo.symbol}</p>
            
            <div className="etfs-grid">
              {data.etfHoldings.map(etf => (
                <div key={etf.symbol} className="etf-card">
                  <div className="etf-header">
                    <span className="etf-symbol">{etf.symbol}</span>
                    <span className="etf-name">{etf.name}</span>
                  </div>
                  <div className="etf-details">
                    <div className="etf-stat">
                      <span className="stat-label">Shares</span>
                      <span className="stat-value">{formatNumber(etf.shares)}</span>
                    </div>
                    <div className="etf-stat">
                      <span className="stat-label">Value</span>
                      <span className="stat-value">{formatNumber(etf.value)}</span>
                    </div>
                    <div className="etf-stat">
                      <span className="stat-label">% of ETF</span>
                      <span className="stat-value">{(Math.random() * 10 + 2).toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default InstitutionalHoldings;

