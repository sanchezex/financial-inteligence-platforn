import React, { useState, useEffect } from 'react';
import './ExpertFollow.css';

function ExpertFollow() {
  const [experts, setExperts] = useState([]);
  const [followed, setFollowed] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [selectedExpert, setSelectedExpert] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate expert data
    const generateExperts = () => {
      return [
        {
          id: 1,
          name: 'Cathie Wood',
          alias: 'ARK Invest',
          avatar: '',
          specialty: 'Technology & Innovation',
          followers: 1250000,
          following: 45,
          reputation: 4.8,
          performance: { ytd: 28.5, oneYear: 42.3, threeYear: 156.2 },
          winRate: 72,
          totalPicks: 892,
          recentPicks: [
            { symbol: 'TSLA', action: 'BUY', date: '2024-01-12', return: 12.5 },
            { symbol: 'COIN', action: 'BUY', date: '2024-01-10', return: 28.3 },
            { symbol: 'PLTR', action: 'BUY', date: '2024-01-08', return: -5.2 },
          ],
          bio: 'Founder & CEO of ARK Investment Management. Focused on disruptive innovation including genomics, automation, and fintech.',
          tags: ['Innovation', 'Growth', 'Disruptive'],
          verified: true,
          twitter: '@CathieDWood',
          newsletter: 'ARK Invest Newsletter'
        },
        {
          id: 2,
          name: 'Warren Buffett',
          alias: 'Berkshire Hathaway',
          avatar: '',
          specialty: 'Value Investing',
          followers: 2100000,
          following: 12,
          reputation: 4.9,
          performance: { ytd: 12.4, oneYear: 18.7, threeYear: 45.8 },
          winRate: 85,
          totalPicks: 156,
          recentPicks: [
            { symbol: 'AAPL', action: 'HOLD', date: '2024-01-14', return: 8.2 },
            { symbol: 'OXY', action: 'BUY', date: '2024-01-11', return: 15.6 },
          ],
          bio: 'Chairman & CEO of Berkshire Hathaway. Legendary value investor known as the "Oracle of Omaha".',
          tags: ['Value', 'Blue Chip', 'Long-term'],
          verified: true,
          twitter: '@WarrenBuffett',
          newsletter: 'Berkshire Annual Letter'
        },
        {
          id: 3,
          name: 'Jim Cramer',
          alias: 'TheStreet',
          avatar: '',
          specialty: 'Active Trading',
          followers: 890000,
          following: 234,
          reputation: 4.2,
          performance: { ytd: 22.1, oneYear: 35.4, threeYear: 89.3 },
          winRate: 65,
          totalPicks: 2341,
          recentPicks: [
            { symbol: 'NVDA', action: 'BUY', date: '2024-01-15', return: 15.2 },
            { symbol: 'AMD', action: 'BUY', date: '2024-01-13', return: 8.7 },
          ],
          bio: 'Host of Mad Money on CNBC. Known for actionable stock picks and market analysis.',
          tags: ['Trading', 'Momentum', 'Tech'],
          verified: true,
          twitter: '@jimcramer',
          newsletter: 'Action Alerts PLUS'
        },
        {
          id: 4,
          name: 'Michael Burry',
          alias: 'Scion Capital',
          avatar: '',
          specialty: 'Short Selling',
          followers: 650000,
          following: 8,
          reputation: 4.5,
          performance: { ytd: 15.8, oneYear: 28.9, threeYear: 78.4 },
          winRate: 68,
          totalPicks: 145,
          recentPicks: [
            { symbol: 'TSLA', action: 'SHORT', date: '2024-01-10', return: -12.3 },
            { symbol: 'ARKK', action: 'SHORT', date: '2024-01-08', return: -8.5 },
          ],
          bio: 'Founder of Scion Capital. Famous for predicting 2008 mortgage crisis. Known for contrarian bets.',
          tags: ['Contrarian', 'Short', 'Macro'],
          verified: true,
          twitter: '@michaeljburry',
          newsletter: 'Scion Capital Letters'
        },
        {
          id: 5,
          name: 'Catherine Wood',
          alias: 'ARK Invest',
          avatar: '',
          specialty: 'AI & Robotics',
          followers: 780000,
          following: 67,
          reputation: 4.3,
          performance: { ytd: 32.1, oneYear: 48.7, threeYear: 134.2 },
          winRate: 58,
          totalPicks: 456,
          recentPicks: [
            { symbol: 'NVDA', action: 'BUY', date: '2024-01-14', return: 18.5 },
            { symbol: 'GOOGL', action: 'BUY', date: '2024-01-12', return: 6.2 },
          ],
          bio: 'Leading voice in AI and robotics investing. Focus on companies enabling productivity improvements.',
          tags: ['AI', 'Robotics', 'Productivity'],
          verified: true,
          twitter: '@CathieDWood',
          newsletter: 'ARK Innovation Report'
        },
        {
          id: 6,
          name: 'David Tepper',
          alias: 'Appaloosa Management',
          avatar: '',
          specialty: 'Hedge Fund',
          followers: 420000,
          following: 23,
          reputation: 4.6,
          performance: { ytd: 18.2, oneYear: 25.4, threeYear: 62.8 },
          winRate: 74,
          totalPicks: 234,
          recentPicks: [
            { symbol: 'META', action: 'BUY', date: '2024-01-13', return: 22.4 },
            { symbol: 'GOOGL', action: 'BUY', date: '2024-01-11', return: 9.8 },
          ],
          bio: 'Founder of Appaloosa Management. Billionaire hedge fund manager known for tech investments.',
          tags: ['Hedge Fund', 'Tech', 'Large Cap'],
          verified: true,
          twitter: '@DavidTepper',
          newsletter: 'Appaloosa Quarterly Letters'
        },
        {
          id: 7,
          name: 'ARK Invest Team',
          alias: 'ARK Invest',
          avatar: '',
          specialty: 'Thematic Investing',
          followers: 560000,
          following: 89,
          reputation: 4.1,
          performance: { ytd: 25.3, oneYear: 38.9, threeYear: 112.4 },
          winRate: 62,
          totalPicks: 678,
          recentPicks: [
            { symbol: 'TSLA', action: 'BUY', date: '2024-01-15', return: 10.5 },
            { symbol: 'ROKU', action: 'BUY', date: '2024-01-14', return: -3.2 },
          ],
          bio: 'Research team at ARK Invest providing daily trade ideas and thematic analysis.',
          tags: ['Thematic', 'Research', 'Daily Picks'],
          verified: true,
          twitter: '@ARKInvest',
          newsletter: 'ARK Daily'
        },
        {
          id: 8,
          name: 'Mosaic Asset',
          alias: 'Mosaic Partners',
          avatar: '',
          specialty: 'Small Cap Value',
          followers: 234000,
          following: 45,
          reputation: 4.4,
          performance: { ytd: 14.7, oneYear: 22.3, threeYear: 56.8 },
          winRate: 71,
          totalPicks: 345,
          recentPicks: [
            { symbol: 'SMLR', action: 'BUY', date: '2024-01-12', return: 8.9 },
            { symbol: 'LTHM', action: 'BUY', date: '2024-01-10', return: 15.2 },
          ],
          bio: 'Small cap value specialist focusing on underfollowed companies with hidden upside.',
          tags: ['Small Cap', 'Value', 'Underfollowed'],
          verified: false,
          twitter: '@MosaicAsset',
          newsletter: 'Small Cap Insider'
        }
      ];
    };

    const timer = setTimeout(() => {
      const data = generateExperts();
      setExperts(data);
      setFollowed([1, 2]); // Follow first two experts
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, []);

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const toggleFollow = (id) => {
    if (followed.includes(id)) {
      setFollowed(followed.filter(f => f !== id));
    } else {
      setFollowed([...followed, id]);
    }
  };

  const getPerformanceColor = (perf) => {
    if (perf >= 0) return 'positive';
    return 'negative';
  };

  const filteredExperts = experts.filter(expert => {
    if (activeTab === 'following') return followed.includes(expert.id);
    if (activeTab === 'verified') return expert.verified;
    return true;
  });

  if (loading) {
    return (
      <div className="expert-follow loading">
        <div className="loading-spinner"></div>
        <p>Loading experts...</p>
      </div>
    );
  }

  return (
    <div className="expert-follow">
      {/* Header */}
      <div className="expert-header">
        <div className="header-left">
          <h2>Follow Analysts & Traders</h2>
          <p>Learn from top-performing experts and get their latest picks</p>
        </div>
        <div className="header-stats">
          <div className="stat-item">
            <span className="stat-value">{experts.length}</span>
            <span className="stat-label">Experts</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">{formatNumber(experts.reduce((sum, e) => sum + e.followers, 0))}</span>
            <span className="stat-label">Total Followers</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="expert-tabs">
        {[
          { key: 'all', label: 'All Experts' },
          { key: 'following', label: 'Following' },
          { key: 'verified', label: 'Verified' },
          { key: 'trending', label: 'Trending' },
        ].map(tab => (
          <button
            key={tab.key}
            className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Experts Grid */}
      <div className="experts-grid">
        {filteredExperts.map(expert => (
          <div key={expert.id} className="expert-card">
            <div className="card-header">
              <div className="expert-info">
                <span className="expert-avatar">{expert.avatar}</span>
                <div className="expert-details">
                  <div className="expert-name">
                    {expert.name}
                    {expert.verified && <span className="verified-badge">✓</span>}
                  </div>
                  <span className="expert-alias">{expert.alias}</span>
                </div>
              </div>
              <div className="expert-reputation">
                <span className="reputation-score">{expert.reputation}</span>
              </div>
            </div>

            <div className="specialty">
              <span className="specialty-tag">{expert.specialty}</span>
            </div>

            <div className="stats-row">
              <div className="stat">
                <span className="stat-value">{formatNumber(expert.followers)}</span>
                <span className="stat-label">Followers</span>
              </div>
              <div className="stat">
                <span className="stat-value">{expert.winRate}%</span>
                <span className="stat-label">Win Rate</span>
              </div>
              <div className="stat">
                <span className="stat-value">{expert.totalPicks}</span>
                <span className="stat-label">Picks</span>
              </div>
            </div>

            <div className="performance-row">
              <div className="perf-item">
                <span className="perf-label">YTD</span>
                <span className={`perf-value ${getPerformanceColor(expert.performance.ytd)}`}>
                  {expert.performance.ytd >= 0 ? '+' : ''}{expert.performance.ytd}%
                </span>
              </div>
              <div className="perf-item">
                <span className="perf-label">1Y</span>
                <span className={`perf-value ${getPerformanceColor(expert.performance.oneYear)}`}>
                  {expert.performance.oneYear >= 0 ? '+' : ''}{expert.performance.oneYear}%
                </span>
              </div>
              <div className="perf-item">
                <span className="perf-label">3Y</span>
                <span className={`perf-value ${getPerformanceColor(expert.performance.threeYear)}`}>
                  {expert.performance.threeYear >= 0 ? '+' : ''}{expert.performance.threeYear}%
                </span>
              </div>
            </div>

            <div className="recent-picks">
              <h4>Recent Picks</h4>
              <div className="picks-list">
                {expert.recentPicks.map((pick, i) => (
                  <div key={i} className="pick-item">
                    <span className={`pick-action ${pick.action.toLowerCase()}`}>{pick.action}</span>
                    <span className="pick-symbol">{pick.symbol}</span>
                    <span className={`pick-return ${pick.return >= 0 ? 'positive' : 'negative'}`}>
                      {pick.return >= 0 ? '+' : ''}{pick.return.toFixed(1)}%
                    </span>
                    <span className="pick-date">{formatDate(pick.date)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="tags-row">
              {expert.tags.map((tag, i) => (
                <span key={i} className="tag">{tag}</span>
              ))}
            </div>

            <div className="card-actions">
              <button
                className={`follow-btn ${followed.includes(expert.id) ? 'following' : ''}`}
                onClick={() => toggleFollow(expert.id)}
              >
                {followed.includes(expert.id) ? '✓ Following' : '+ Follow'}
              </button>
              <button
                className="view-btn"
                onClick={() => setSelectedExpert(expert)}
              >
                View Profile
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Expert Detail Modal */}
      {selectedExpert && (
        <div className="modal-overlay" onClick={() => setSelectedExpert(null)}>
          <div className="expert-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedExpert(null)}>×</button>
            
            <div className="modal-header">
              <span className="expert-avatar large">{selectedExpert.avatar}</span>
              <div className="modal-info">
                <h2>{selectedExpert.name}</h2>
                <span className="alias">{selectedExpert.alias}</span>
                <div className="modal-meta">
                  <span className="reputation">{selectedExpert.reputation}</span>
                  {selectedExpert.verified && <span className="verified">Verified</span>}
                </div>
              </div>
              <button
                className={`follow-btn large ${followed.includes(selectedExpert.id) ? 'following' : ''}`}
                onClick={() => toggleFollow(selectedExpert.id)}
              >
                {followed.includes(selectedExpert.id) ? 'Following' : '+ Follow'}
              </button>
            </div>

            <div className="modal-body">
              <div className="about-section">
                <h3>About</h3>
                <p>{selectedExpert.bio}</p>
              </div>

              <div className="performance-section">
                <h3>Performance</h3>
                <div className="perf-grid">
                  <div className="perf-card">
                    <span className="perf-label">YTD Return</span>
                    <span className={`perf-value ${getPerformanceColor(selectedExpert.performance.ytd)}`}>
                      {selectedExpert.performance.ytd >= 0 ? '+' : ''}{selectedExpert.performance.ytd}%
                    </span>
                  </div>
                  <div className="perf-card">
                    <span className="perf-label">1 Year</span>
                    <span className={`perf-value ${getPerformanceColor(selectedExpert.performance.oneYear)}`}>
                      {selectedExpert.performance.oneYear >= 0 ? '+' : ''}{selectedExpert.performance.oneYear}%
                    </span>
                  </div>
                  <div className="perf-card">
                    <span className="perf-label">3 Year</span>
                    <span className={`perf-value ${getPerformanceColor(selectedExpert.performance.threeYear)}`}>
                      {selectedExpert.performance.threeYear >= 0 ? '+' : ''}{selectedExpert.performance.threeYear}%
                    </span>
                  </div>
                  <div className="perf-card">
                    <span className="perf-label">Win Rate</span>
                    <span className="perf-value">{selectedExpert.winRate}%</span>
                  </div>
                </div>
              </div>

              <div className="picks-section">
                <h3>Recent Picks</h3>
                <div className="picks-table">
                  <div className="table-row header">
                    <span>Symbol</span>
                    <span>Action</span>
                    <span>Date</span>
                    <span>Return</span>
                  </div>
                  {selectedExpert.recentPicks.map((pick, i) => (
                    <div key={i} className="table-row">
                      <span className="symbol">{pick.symbol}</span>
                      <span className={`action ${pick.action.toLowerCase()}`}>{pick.action}</span>
                      <span>{formatDate(pick.date)}</span>
                      <span className={`return ${pick.return >= 0 ? 'positive' : 'negative'}`}>
                        {pick.return >= 0 ? '+' : ''}{pick.return.toFixed(1)}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="social-section">
                <h3>Connect</h3>
                <div className="social-links">
                  <a href="#" className="social-link twitter">
                    <span>X</span> {selectedExpert.twitter}
                  </a>
                  <button className="social-link newsletter">
                    Subscribe to Newsletter
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ExpertFollow;

