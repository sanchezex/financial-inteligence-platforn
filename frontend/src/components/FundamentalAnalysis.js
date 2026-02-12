import React, { useState, useEffect } from 'react';
import './FundamentalAnalysis.css';

function FundamentalAnalysis({ symbol = 'AAPL' }) {
  const [activeTab, setActiveTab] = useState('income');
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    // Generate fundamental data
    const generateData = () => {
      try {
        return {
          companyInfo: {
            name: 'Apple Inc.',
            sector: 'Technology',
            industry: 'Consumer Electronics',
            employees: '164,000',
            headquarters: 'Cupertino, CA',
            website: 'www.apple.com',
            ceo: 'Tim Cook',
            founded: '1976'
          },
          incomeStatement: {
            periods: ['2023', '2022', '2021', '2020', '2019'],
            revenue: [383.29, 394.33, 365.81, 274.51, 260.17],
            costOfRevenue: [214.13, 227.85, 212.98, 169.15, 162.17],
            grossProfit: [169.16, 166.48, 152.83, 105.36, 98.00],
            operatingExpenses: [49.82, 47.29, 43.72, 38.92, 34.66],
            operatingIncome: [119.34, 119.19, 109.10, 66.44, 63.34],
            netIncome: [97.00, 99.80, 94.68, 57.41, 55.26],
            eps: [6.13, 6.16, 5.92, 3.69, 2.97]
          },
          balanceSheet: {
            periods: ['2023', '2022', '2021', '2020', '2019'],
            totalAssets: [352.77, 352.58, 351.00, 323.89, 338.52],
            totalLiabilities: [290.44, 287.91, 287.91, 287.91, 250.27],
            shareholdersEquity: [62.33, 64.67, 63.09, 35.98, 88.25],
            cashAndEquivalents: [62.15, 63.73, 35.93, 38.16, 48.84],
            shortTermInvestments: [31.59, 31.59, 27.69, 52.88, 51.71],
            longTermDebt: [109.11, 111.04, 107.82, 98.07, 91.81]
          },
          cashFlow: {
            periods: ['2023', '2022', '2021', '2020', '2019'],
            operatingCashFlow: [124.42, 122.15, 111.44, 80.67, 69.39],
            capitalExpenditures: [10.96, 10.70, 10.82, 7.31, 7.61],
            freeCashFlow: [113.46, 111.45, 100.62, 73.36, 61.78],
            dividendPayments: [14.93, 14.81, 14.67, 14.08, 13.73],
            shareRepurchases: [77.32, 89.73, 88.29, 72.36, 66.91]
          },
          ratios: {
            pe: [29.1, 28.5, 26.2, 37.8, 28.5],
            pb: [47.2, 45.8, 42.3, 68.4, 52.1],
            ps: [7.6, 7.2, 6.8, 10.2, 8.4],
            roe: [155.6, 154.3, 150.1, 159.5, 134.2],
            roa: [27.5, 28.3, 27.0, 17.7, 16.3],
            currentRatio: [0.99, 0.88, 1.07, 1.23, 1.13],
            debtToEquity: [180.2, 185.3, 182.4, 253.5, 197.5],
            profitMargin: [25.3, 25.3, 25.9, 20.9, 21.2]
          },
          growth: {
            revenueGrowth: [-2.8, 7.8, 33.3, 5.5, -2.0],
            epsGrowth: [-0.5, 4.1, 60.4, 24.2, 7.0],
            revenueCAGR: 10.2,
            epsCAGR: 15.7
          }
        };
      } catch (error) {
        console.error('Error generating fundamental data:', error);
        return null;
      }
    };

    const timer = setTimeout(() => {
      const data = generateData();
      if (data) {
        setData(data);
      }
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [symbol]);

  const formatNumber = (num, type = 'billions') => {
    if (Array.isArray(num)) return num;
    if (type === 'billions') return `$${num.toFixed(2)}B`;
    if (type === 'millions') return `$${(num / 1000).toFixed(2)}M`;
    if (type === 'ratio') return num.toFixed(2);
    if (type === 'percent') return `${num.toFixed(1)}%`;
    return num;
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num);
  };

  if (loading) {
    return (
      <div className="fundamental-analysis loading">
        <div className="loading-spinner"></div>
        <p>Loading fundamental data...</p>
      </div>
    );
  }

  return (
    <div className="fundamental-analysis">
      {/* Header */}
      <div className="fundamental-header">
        <div className="company-info">
          <h2>{data.companyInfo.name} ({symbol})</h2>
          <div className="company-meta">
            <span className="meta-item">{data.companyInfo.sector}</span>
            <span className="meta-item">{data.companyInfo.industry}</span>
            <span className="meta-item">{data.companyInfo.employees}</span>
            <span className="meta-item">{data.companyInfo.headquarters}</span>
          </div>
        </div>
        <div className="quick-stats">
          <div className="stat-item">
            <span className="stat-label">P/E Ratio</span>
            <span className="stat-value">{data.ratios.pe[0]}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">ROE</span>
            <span className="stat-value positive">{data.ratios.roe[0]}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Profit Margin</span>
            <span className="stat-value positive">{data.ratios.profitMargin[0]}%</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Debt/Equity</span>
            <span className="stat-value">{data.ratios.debtToEquity}</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="fundamental-tabs">
        {['income', 'balance', 'cashflow', 'ratios', 'growth'].map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab === 'income' && 'Income Statement'}
            {tab === 'balance' && 'Balance Sheet'}
            {tab === 'cashflow' && 'Cash Flow'}
            {tab === 'ratios' && 'Ratios'}
            {tab === 'growth' && 'Growth'}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="fundamental-content">
        {activeTab === 'income' && (
          <div className="statement-section">
            <h3>Income Statement</h3>
            <div className="statement-table">
              <div className="table-row header">
                <span className="metric">Metric</span>
                {data.incomeStatement.periods.map((period, i) => (
                  <span key={period} className="period">{period}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Revenue</span>
                {data.incomeStatement.revenue.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Cost of Revenue</span>
                {data.incomeStatement.costOfRevenue.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">Gross Profit</span>
                {data.incomeStatement.grossProfit.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Operating Expenses</span>
                {data.incomeStatement.operatingExpenses.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">Operating Income</span>
                {data.incomeStatement.operatingIncome.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Net Income</span>
                {data.incomeStatement.netIncome.map((val, i) => (
                  <span key={i} className="period positive">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">EPS</span>
                {data.incomeStatement.eps.map((val, i) => (
                  <span key={i} className="period">{formatCurrency(val)}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'balance' && (
          <div className="statement-section">
            <h3>Balance Sheet</h3>
            <div className="statement-table">
              <div className="table-row header">
                <span className="metric">Metric</span>
                {data.balanceSheet.periods.map((period, i) => (
                  <span key={period} className="period">{period}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Total Assets</span>
                {data.balanceSheet.totalAssets.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Cash & Equivalents</span>
                {data.balanceSheet.cashAndEquivalents.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Short-term Investments</span>
                {data.balanceSheet.shortTermInvestments.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Total Liabilities</span>
                {data.balanceSheet.totalLiabilities.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Long-term Debt</span>
                {data.balanceSheet.longTermDebt.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">Shareholders' Equity</span>
                {data.balanceSheet.shareholdersEquity.map((val, i) => (
                  <span key={i} className="period">{formatNumber(val)}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'cashflow' && (
          <div className="statement-section">
            <h3>Cash Flow Statement</h3>
            <div className="statement-table">
              <div className="table-row header">
                <span className="metric">Metric</span>
                {data.cashFlow.periods.map((period, i) => (
                  <span key={period} className="period">{period}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">Operating Cash Flow</span>
                {data.cashFlow.operatingCashFlow.map((val, i) => (
                  <span key={i} className="period positive">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Capital Expenditures</span>
                {data.cashFlow.capitalExpenditures.map((val, i) => (
                  <span key={i} className="period negative">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row highlight">
                <span className="metric">Free Cash Flow</span>
                {data.cashFlow.freeCashFlow.map((val, i) => (
                  <span key={i} className="period positive">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Dividend Payments</span>
                {data.cashFlow.dividendPayments.map((val, i) => (
                  <span key={i} className="period negative">{formatNumber(val)}</span>
                ))}
              </div>
              <div className="table-row">
                <span className="metric">Share Repurchases</span>
                {data.cashFlow.shareRepurchases.map((val, i) => (
                  <span key={i} className="period negative">{formatNumber(val)}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ratios' && (
          <div className="ratios-section">
            <h3>Financial Ratios</h3>
            <div className="ratios-grid">
              <div className="ratio-category">
                <h4>Valuation</h4>
                <div className="ratio-item">
                  <span className="ratio-name">P/E Ratio</span>
                  <span className="ratio-value">{data.ratios.pe[0]}</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill" style={{ width: `${Math.min(100, data.ratios.pe[0] / 50 * 100)}%` }}></span>
                  </span>
                </div>
                <div className="ratio-item">
                  <span className="ratio-name">P/B Ratio</span>
                  <span className="ratio-value">{data.ratios.pb[0]}</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill" style={{ width: `${Math.min(100, data.ratios.pb[0] / 80 * 100)}%` }}></span>
                  </span>
                </div>
                <div className="ratio-item">
                  <span className="ratio-name">P/S Ratio</span>
                  <span className="ratio-value">{data.ratios.ps[0]}</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill" style={{ width: `${Math.min(100, data.ratios.ps[0] / 15 * 100)}%` }}></span>
                  </span>
                </div>
              </div>

              <div className="ratio-category">
                <h4>Profitability</h4>
                <div className="ratio-item">
                  <span className="ratio-name">ROE</span>
                  <span className="ratio-value positive">{data.ratios.roe[0]}%</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill positive" style={{ width: `${Math.min(100, data.ratios.roe[0])}%` }}></span>
                  </span>
                </div>
                <div className="ratio-item">
                  <span className="ratio-name">ROA</span>
                  <span className="ratio-value positive">{data.ratios.roa[0]}%</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill positive" style={{ width: `${Math.min(100, data.ratios.roa[0])}%` }}></span>
                  </span>
                </div>
                <div className="ratio-item">
                  <span className="ratio-name">Profit Margin</span>
                  <span className="ratio-value positive">{data.ratios.profitMargin[0]}%</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill positive" style={{ width: `${Math.min(100, data.ratios.profitMargin[0])}%` }}></span>
                  </span>
                </div>
              </div>

              <div className="ratio-category">
                <h4>Liquidity</h4>
                <div className="ratio-item">
                  <span className="ratio-name">Current Ratio</span>
                  <span className="ratio-value">{data.ratios.currentRatio}</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill" style={{ width: `${Math.min(100, data.ratios.currentRatio * 33)}%` }}></span>
                  </span>
                </div>
                <div className="ratio-item">
                  <span className="ratio-name">Debt/Equity</span>
                  <span className="ratio-value negative">{data.ratios.debtToEquity}</span>
                  <span className="ratio-bar">
                    <span className="ratio-fill negative" style={{ width: `${Math.min(100, data.ratios.debtToEquity / 3)}%` }}></span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'growth' && (
          <div className="growth-section">
            <h3>Growth Analysis</h3>
            <div className="growth-cards">
              <div className="growth-card">
                <div className="growth-header">
                  <h4>Revenue Growth</h4>
                  <span className={`growth-value ${data.growth.revenueGrowth[0] >= 0 ? 'positive' : 'negative'}`}>
                    {data.growth.revenueGrowth[0] >= 0 ? '+' : ''}{data.growth.revenueGrowth[0]}%
                  </span>
                </div>
                <div className="growth-chart">
                  <svg viewBox="0 0 200 60">
                    <defs>
                      <linearGradient id="revenueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor={data.growth.revenueGrowth[0] >= 0 ? '#22c55e' : '#ef4444'} stopOpacity="0.3"/>
                        <stop offset="100%" stopColor={data.growth.revenueGrowth[0] >= 0 ? '#22c55e' : '#ef4444'} stopOpacity="0"/>
                      </linearGradient>
                    </defs>
                    <path
                      d={`M0,${50 - (data.growth.revenueGrowth[1] / 50) * 40} Q50,${50 - (data.growth.revenueGrowth[2] / 50) * 40} 100,${50 - (data.growth.revenueGrowth[0] / 50) * 40}`}
                      fill="none"
                      stroke={data.growth.revenueGrowth[0] >= 0 ? '#22c55e' : '#ef4444'}
                      strokeWidth="2"
                    />
                  </svg>
                </div>
                <div className="growth-cagr">
                  <span>CAGR (5Y):</span>
                  <span className="cagr-value positive">{data.growth.revenueCAGR}%</span>
                </div>
              </div>

              <div className="growth-card">
                <div className="growth-header">
                  <h4>EPS Growth</h4>
                  <span className={`growth-value ${data.growth.epsGrowth[0] >= 0 ? 'positive' : 'negative'}`}>
                    {data.growth.epsGrowth[0] >= 0 ? '+' : ''}{data.growth.epsGrowth[0]}%
                  </span>
                </div>
                <div className="growth-chart">
                  <svg viewBox="0 0 200 60">
                    <path
                      d={`M0,${50 - (data.growth.epsGrowth[1] / 80) * 40} Q50,${50 - (data.growth.epsGrowth[2] / 80) * 40} 100,${50 - (data.growth.epsGrowth[0] / 80) * 40}`}
                      fill="none"
                      stroke={data.growth.epsGrowth[0] >= 0 ? '#22c55e' : '#ef4444'}
                      strokeWidth="2"
                    />
                  </svg>
                </div>
                <div className="growth-cagr">
                  <span>CAGR (5Y):</span>
                  <span className="cagr-value positive">{data.growth.epsCAGR}%</span>
                </div>
              </div>
            </div>

            <div className="peer-comparison">
              <h4>Peer Comparison</h4>
              <div className="peer-table">
                <div className="peer-row header">
                  <span>Metric</span>
                  <span>{symbol}</span>
                  <span>Industry Avg</span>
                  <span>S&P 500</span>
                </div>
                <div className="peer-row">
                  <span>P/E Ratio</span>
                  <span>{data.ratios.pe[0]}</span>
                  <span>24.5</span>
                  <span>21.3</span>
                </div>
                <div className="peer-row">
                  <span>ROE</span>
                  <span className="positive">{data.ratios.roe[0]}%</span>
                  <span>28.5%</span>
                  <span>18.2%</span>
                </div>
                <div className="peer-row">
                  <span>Profit Margin</span>
                  <span className="positive">{data.ratios.profitMargin[0]}%</span>
                  <span>22.1%</span>
                  <span>12.8%</span>
                </div>
                <div className="peer-row">
                  <span>Debt/Equity</span>
                  <span className="negative">{data.ratios.debtToEquity}</span>
                  <span>156.3</span>
                  <span>89.5</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default FundamentalAnalysis;

