
import React, { useState, useEffect, useRef } from 'react';
import './NaturalLanguageSearch.css';

function NaturalLanguageSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [recentSearches, setRecentSearches] = useState([
    'NVDA earnings date',
    'Apple stock forecast',
    'Tech sector performance',
    'Best performing ETFs',
    'Fed meeting date'
  ]);
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const inputRef = useRef(null);

  const processQuery = (input) => {
    const keywords = {
      'earnings': { type: 'event', label: 'Earnings' },
      'forecast': { type: 'prediction', label: 'Forecast' },
      'price': { type: 'price', label: 'Price' },
      'volume': { type: 'volume', label: 'Volume' },
      'dividend': { type: 'dividend', label: 'Dividend' },
      'news': { type: 'news', label: 'News' },
      'performance': { type: 'performance', label: 'Performance' },
      'aapl': { type: 'stock', label: 'Apple Inc.' },
      'msft': { type: 'stock', label: 'Microsoft' },
      'nvda': { type: 'stock', label: 'NVIDIA' },
      'googl': { type: 'stock', label: 'Alphabet' },
      'amzn': { type: 'stock', label: 'Amazon' },
      'tsla': { type: 'stock', label: 'Tesla' },
    };

    const words = input.toLowerCase().split(' ');
    const detected = [];

    words.forEach(word => {
      Object.entries(keywords).forEach(([key, value]) => {
        if (word.includes(key) || key.includes(word)) {
          detected.push(value);
        }
      });
    });

    return detected;
  };

  const generateResults = (input) => {
    const detected = processQuery(input);
    const results = [];

    if (detected.some(d => d.type === 'stock')) {
      const stocks = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'];
      detected.filter(d => d.type === 'stock').forEach(d => {
        stocks.forEach(s => {
          results.push({
            type: 'stock',
            symbol: s,
            title: `${s} - ${getCompanyName(s)}`,
            subtitle: `$${(100 + Math.random() * 400).toFixed(2)}`,
          });
        });
      });
    }

    if (detected.some(d => d.type === 'event')) {
      results.push({
        type: 'event',
        title: 'Upcoming Earnings',
        subtitle: 'AAPL, MSFT, GOOGL reporting this week',
      });
    }

    if (results.length === 0 && input.length > 2) {
      results.push(
        { type: 'chart', title: `Chart: ${input}`, subtitle: 'View price chart' },
        { type: 'news', title: `News about ${input}`, subtitle: 'Latest headlines' },
        { type: 'analysis', title: `Analysis: ${input}`, subtitle: 'AI-powered analysis' }
      );
    }

    return results;
  };

  const getCompanyName = (symbol) => {
    const names = {
      'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation',
      'NVDA': 'NVIDIA Corporation', 'GOOGL': 'Alphabet Inc.',
      'AMZN': 'Amazon.com Inc.', 'TSLA': 'Tesla Inc.',
    };
    return names[symbol] || symbol;
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    setQuery(value);

    if (value.length > 1) {
      const detected = processQuery(value);
      setSuggestions(detected);
      setShowResults(true);
    } else {
      setSuggestions([]);
      setShowResults(false);
    }
  };

  const handleSearch = (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);

    setTimeout(() => {
      const searchResults = generateResults(searchQuery);
      setResults(searchResults);
      setIsSearching(false);

      if (!recentSearches.includes(searchQuery)) {
        setRecentSearches(prev => [searchQuery, ...prev.slice(0, 4)]);
      }

      setShowResults(true);
    }, 500);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(query + ' ' + suggestion.label);
    inputRef.current?.focus();
  };

  const handleRecentClick = (search) => {
    setQuery(search);
    handleSearch(search);
  };

  const clearSearch = () => {
    setQuery('');
    setResults([]);
    setSuggestions([]);
    setShowResults(false);
  };

  return (
    <div className="natural-search">
      <div className="search-header">
        <h2>Natural Language Search</h2>
        <p>Ask questions in plain English</p>
      </div>

      <div className="search-container">
        <div className="search-input-wrapper">
          <span className="search-icon"></span>
          <input
            ref={inputRef}
            type="text"
            placeholder="Try: 'NVDA earnings date' or 'Apple stock forecast'"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="search-input"
          />
          {query && (
            <button className="clear-btn" onClick={clearSearch}>×</button>
          )}
          <button
            className="search-btn"
            onClick={() => handleSearch()}
            disabled={isSearching || !query.trim()}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>

        {suggestions.length > 0 && (
          <div className="suggestions-bar">
            <span className="suggestions-label">Detected:</span>
            {suggestions.map((suggestion, i) => (
              <button
                key={i}
                className="suggestion-chip"
                onClick={() => handleSuggestionClick(suggestion)}
              >
                {suggestion.label}
              </button>
            ))}
          </div>
        )}

        <div className="search-templates">
          <span className="templates-label">Try asking:</span>
          <div className="template-chips">
            {[
              { text: 'NVDA earnings' },
              { text: 'Tech stocks' },
              { text: 'Best dividend stocks' },
              { text: 'Market outlook' }
            ].map((template, i) => (
              <button
                key={i}
                className="template-chip"
                onClick={() => {
                  setQuery(template.text);
                  handleSearch(template.text);
                }}
              >
                {template.text}
              </button>
            ))}
          </div>
        </div>
      </div>

      {showResults ? (
        <div className="search-results">
          <h3>Search Results for "{query}"</h3>

          {results.length > 0 ? (
            <div className="results-list">
              {results.map((result, i) => (
                <div key={i} className="result-item" onClick={() => setQuery('')}>
                  <div className="result-content">
                    <span className="result-title">{result.title}</span>
                    <span className="result-subtitle">{result.subtitle}</span>
                  </div>
                  <span className="result-arrow"></span>
                </div>
              ))}
            </div>
          ) : (
            <div className="no-results">
              <p>No results found. Try rephrasing your query.</p>
            </div>
          )}
        </div>
      ) : (
        <div className="recent-searches">
          <h3>Recent Searches</h3>
          <div className="recent-list">
            {recentSearches.map((search, i) => (
              <div
                key={i}
                className="recent-item"
                onClick={() => handleRecentClick(search)}
              >
                <span className="recent-text">{search}</span>
                <span className="recent-arrow"></span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default NaturalLanguageSearch;

