import React, { useState, useEffect } from 'react';
import './ShareWatchlists.css';

function ShareWatchlists({ watchlistId = null }) {
  const [watchlists, setWatchlists] = useState([]);
  const [sharedLists, setSharedLists] = useState([]);
  const [selectedList, setSelectedList] = useState(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareLink, setShareLink] = useState('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate sample data
    const generateData = () => {
      return {
        myWatchlists: [
          { id: 1, name: 'Tech Giants', symbolCount: 8, isPublic: true, sharedCount: 45 },
          { id: 2, name: 'Healthcare', symbolCount: 6, isPublic: false, sharedCount: 0 },
          { id: 3, name: 'Dividend Kings', symbolCount: 5, isPublic: true, sharedCount: 128 },
          { id: 4, name: 'EV & Clean Energy', symbolCount: 7, isPublic: false, sharedCount: 0 },
        ],
        sharedWatchlists: [
          { id: 101, name: 'Cathie Wood Picks', owner: 'ARK Invest', symbolCount: 6, followers: 12500, avatar: '' },
          { id: 102, name: 'Warren Buffett Portfolio', owner: 'Berkshire Hathaway', symbolCount: 10, followers: 8900, avatar: '' },
          { id: 103, name: 'Top AI Stocks 2024', owner: 'Tech Analyst', symbolCount: 12, followers: 5600, avatar: '' },
          { id: 104, name: 'Meme Stock Watch', owner: 'Retail Traders', symbolCount: 8, followers: 23000, avatar: '' },
          { id: 105, name: 'ESG Leaders', owner: 'Green Investing', symbolCount: 15, followers: 3400, avatar: '' },
        ]
      };
    };

    const timer = setTimeout(() => {
      const data = generateData();
      setWatchlists(data.myWatchlists);
      setSharedLists(data.sharedWatchlists);
      setLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  const generateShareLink = (list) => {
    const baseUrl = window.location.origin;
    const link = `${baseUrl}/watchlist/shared/${list.id}?name=${encodeURIComponent(list.name)}`;
    setShareLink(link);
    setSelectedList(list);
    setShowShareModal(true);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const togglePublic = (id) => {
    setWatchlists(watchlists.map(w =>
      w.id === id ? { ...w, isPublic: !w.isPublic } : w
    ));
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  if (loading) {
    return (
      <div className="share-watchlists loading">
        <div className="loading-spinner"></div>
        <p>Loading shared watchlists...</p>
      </div>
    );
  }

  return (
    <div className="share-watchlists">
      {/* Header */}
      <div className="share-header">
        <div className="header-left">
          <h2>Shared Watchlists</h2>
          <p>Share your watchlists and discover curated lists from the community</p>
        </div>
      </div>

      {/* My Watchlists Section */}
      <section className="section">
        <div className="section-header">
          <h3>My Watchlists</h3>
          <span className="section-count">{watchlists.filter(w => w.isPublic).length} public</span>
        </div>
        <div className="watchlists-grid">
          {watchlists.map(list => (
            <div key={list.id} className="watchlist-card">
              <div className="card-header">
                <span className="card-icon"></span>
                <span className="card-name">{list.name}</span>
              </div>
              <div className="card-stats">
                <span className="stat">
                  <span className="stat-value">{list.symbolCount}</span>
                  <span className="stat-label">stocks</span>
                </span>
                {list.isPublic && (
                  <span className="stat">
                    <span className="stat-value">{list.sharedCount}</span>
                    <span className="stat-label">shares</span>
                  </span>
                )}
              </div>
              <div className="card-actions">
                <button
                  className={`toggle-btn ${list.isPublic ? 'active' : ''}`}
                  onClick={() => togglePublic(list.id)}
                >
                  {list.isPublic ? 'Public' : 'Private'}
                </button>
                {list.isPublic && (
                  <button
                    className="share-btn"
                    onClick={() => generateShareLink(list)}
                  >
                    Share
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Community Watchlists Section */}
      <section className="section">
        <div className="section-header">
          <h3>Community Watchlists</h3>
          <div className="search-filter">
            <input type="text" placeholder="Search watchlists..." />
          </div>
        </div>
        <div className="community-grid">
          {sharedLists.map(list => (
            <div key={list.id} className="community-card">
              <div className="card-top">
                <span className="card-avatar"></span>
                <div className="card-info">
                  <span className="card-name">{list.name}</span>
                  <span className="card-owner">by {list.owner}</span>
                </div>
                <button className="follow-btn">+ Follow</button>
              </div>
              <div className="card-meta">
                <span className="meta-item">
                  {list.symbolCount} stocks
                </span>
                <span className="meta-item">
                  {formatNumber(list.followers)} followers
                </span>
              </div>
              <div className="card-preview">
                <span className="preview-label">Preview:</span>
                <div className="preview-symbols">
                  {['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN'].slice(0, Math.min(5, list.symbolCount)).map(s => (
                    <span key={s} className="symbol-chip">{s}</span>
                  ))}
                </div>
              </div>
              <div className="card-footer">
                <button className="view-btn">View Watchlist</button>
                <button className="copy-btn">Copy</button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Collaboration Section */}
      <section className="section">
        <div className="section-header">
          <h3>Collaboration</h3>
        </div>
        <div className="collab-options">
          <div className="collab-card">
            <div className="collab-icon"></div>
            <h4>Invite Collaborators</h4>
            <p>Allow specific users to edit your watchlists</p>
            <button className="invite-btn">Send Invites</button>
          </div>
          <div className="collab-card">
            <div className="collab-icon"></div>
            <h4>Embed Widget</h4>
            <p>Add your watchlist to your website</p>
            <button className="embed-btn">Get Embed Code</button>
          </div>
          <div className="collab-card">
            <div className="collab-icon"></div>
            <h4>Export as Report</h4>
            <p>Download as PDF or Excel report</p>
            <button className="export-btn">Export</button>
          </div>
        </div>
      </section>

      {/* Share Modal */}
      {showShareModal && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="share-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setShowShareModal(false)}>×</button>
            
            <div className="modal-header">
              <span className="modal-icon"></span>
              <div>
                <h3>Share "{selectedList.name}"</h3>
                <p>This watchlist is public</p>
              </div>
            </div>

            <div className="share-options">
              <div className="share-link-section">
                <label>Share Link</label>
                <div className="link-input">
                  <input type="text" value={shareLink} readOnly />
                  <button className="copy-btn" onClick={copyToClipboard}>
                    {copied ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>

              <div className="social-share">
                <span className="share-label">Share on:</span>
                <div className="social-buttons">
                  <button className="social-btn twitter">
                    <span>X</span> Twitter
                  </button>
                  <button className="social-btn facebook">
                    <span>f</span> Facebook
                  </button>
                  <button className="social-btn linkedin">
                    <span>in</span> LinkedIn
                  </button>
                  <button className="social-btn email">
                    Email
                  </button>
                </div>
              </div>

              <div className="embed-section">
                <label>Embed Widget</label>
                <textarea readOnly value={`<iframe src="${shareLink}/embed" width="100%" height="300"></iframe>`} />
                <button className="copy-btn">Copy Code</button>
              </div>
            </div>

            <div className="share-stats">
              <div className="stat-item">
                <span className="stat-value">{selectedList.symbolCount}</span>
                <span className="stat-label">Stocks</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{selectedList.sharedCount}</span>
                <span className="stat-label">Total Shares</span>
              </div>
              <div className="stat-item">
                <span className="stat-value">{Math.floor(Math.random() * 100 + 10)}</span>
                <span className="stat-label">Views Today</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ShareWatchlists;

