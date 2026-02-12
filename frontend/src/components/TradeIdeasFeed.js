import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import PriceStreamService from '../services/PriceStreamService';
import AdvancedChart from './AdvancedChart';
import StockCompare from './StockCompare';
import PriceAlerts from './PriceAlerts';
import './TradeIdeasFeed.css';

// Multi-language support
const translations = {
  en: {
    tradeIdeas: 'Trade Ideas',
    communityShared: 'Community-shared investment ideas and strategies',
    newTradeIdea: '+ New Trade Idea',
    allIdeas: 'All Ideas',
    long: 'Long',
    short: 'Short',
    following: 'Following',
    trending: 'Trending',
    newest: 'Newest',
    confidence: 'Confidence',
    comments: 'comments',
    share: 'Share',
    save: 'Save',
    copyTrade: 'Copy Trade',
    addToWatchlist: 'Add to Watchlist',
    setAlert: 'Set Alert',
    exportPDF: 'Export PDF',
    exportExcel: 'Export Excel',
    keyboardShortcuts: 'Keyboard Shortcuts',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    compareStocks: 'Compare Stocks',
    chartAnalysis: 'Chart Analysis',
    aiSignals: 'AI Signals',
    anomalyDetection: 'Anomaly Detection',
    portfolio: 'Portfolio',
    searchIdeas: 'Search ideas...',
    filterByTag: 'Filter by tag',
    loading: 'Loading trade ideas...',
    noIdeas: 'No trade ideas found',
    signInRequired: 'Sign in to create and share trade ideas',
    upvotes: 'upvotes',
    downvotes: 'downvotes',
  },
  es: {
    tradeIdeas: 'Ideas de Trading',
    communityShared: 'Ideas y estrategias de inversión compartidas por la comunidad',
    newTradeIdea: '+ Nueva Idea',
    allIdeas: 'Todas',
    long: 'Largo',
    short: 'Corto',
    following: 'Siguiendo',
    trending: 'Tendencias',
    newest: 'Más Reciente',
    confidence: 'Confianza',
    comments: 'comentarios',
    share: 'Compartir',
    save: 'Guardar',
    copyTrade: 'Copiar Trade',
    addToWatchlist: 'Añadir a Lista',
    setAlert: 'Establecer Alerta',
    exportPDF: 'Exportar PDF',
    exportExcel: 'Exportar Excel',
    keyboardShortcuts: 'Atajos de Teclado',
    darkMode: 'Modo Oscuro',
    lightMode: 'Modo Claro',
    compareStocks: 'Comparar Acciones',
    chartAnalysis: 'Análisis Gráfico',
    aiSignals: 'Señales IA',
    anomalyDetection: 'Detección Anomalías',
    portfolio: 'Portafolio',
    searchIdeas: 'Buscar ideas...',
    filterByTag: 'Filtrar por etiqueta',
    loading: 'Cargando ideas...',
    noIdeas: 'No se encontraron ideas',
    signInRequired: 'Inicia sesión para crear y compartir ideas',
    upvotes: 'votos a favor',
    downvotes: 'votos en contra',
  },
  zh: {
    tradeIdeas: '交易思路',
    communityShared: '社区分享的投资策略和想法',
    newTradeIdea: '+ 新交易思路',
    allIdeas: '全部',
    long: '做多',
    short: '做空',
    following: '关注',
    trending: '热门',
    newest: '最新',
    confidence: '置信度',
    comments: '评论',
    share: '分享',
    save: '保存',
    copyTrade: '复制交易',
    addToWatchlist: '添加到关注列表',
    setAlert: '设置提醒',
    exportPDF: '导出PDF',
    exportExcel: '导出Excel',
    keyboardShortcuts: '键盘快捷键',
    darkMode: '深色模式',
    lightMode: '浅色模式',
    compareStocks: '股票对比',
    chartAnalysis: '图表分析',
    aiSignals: 'AI信号',
    anomalyDetection: '异常检测',
    portfolio: '投资组合',
    searchIdeas: '搜索思路...',
    filterByTag: '按标签筛选',
    loading: '正在加载交易思路...',
    noIdeas: '未找到交易思路',
    signInRequired: '登录以创建和分享交易思路',
    upvotes: '点赞',
    downvotes: '点踩',
  }
};

function TradeIdeasFeed() {
  const { user, isAuthenticated, login, register, updatePreferences } = useAuth();
  const [ideas, setIdeas] = useState([]);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('trending');
  const [selectedIdea, setSelectedIdea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('en');
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [showChart, setShowChart] = useState(false);
  const [showCompare, setShowCompare] = useState(false);
  const [showAlerts, setShowAlerts] = useState(false);
  const [realtimePrices, setRealtimePrices] = useState({});
  const [selectedSymbolForChart, setSelectedSymbolForChart] = useState(null);
  const [compareSymbols, setCompareSymbols] = useState(['AAPL', 'MSFT', 'GOOGL', 'NVDA']);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
const [showKeyboardShortcuts, setShowKeyboardShortcuts] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [viewMode, setViewMode] = useState('cards');
  const [watchlists, setWatchlists] = useState([
    { id: 1, name: 'Tech Giants', symbols: ['AAPL', 'MSFT', 'GOOGL', 'NVDA'] },
    { id: 2, name: 'Dividend Kings', symbols: ['KO', 'JNGL', 'PG'] },
    { id: 3, name: 'AI Stocks', symbols: ['NVDA', 'PLTR', 'AI'] },
  ]);
  const [followedExperts, setFollowedExperts] = useState([1, 2]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [anomalies, setAnomalies] = useState([]);
  const [aiSignals, setAiSignals] = useState([]);
  const searchInputRef = useRef(null);

// Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
      // Ctrl/Cmd + / for shortcuts
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        setShowKeyboardShortcuts(prev => !prev);
      }
      // Ctrl/Cmd + D for dark mode toggle
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        setIsDarkMode(prev => !prev);
      }
      // Escape to close modals
      if (e.key === 'Escape') {
        setSelectedIdea(null);
        setShowChart(false);
        setShowCompare(false);
        setShowAlerts(false);
        setShowKeyboardShortcuts(false);
        setShowCreateModal(false);
      }
      // N for new idea (when authenticated)
      if (e.key === 'n' && !e.ctrlKey && !e.metaKey && isAuthenticated) {
        e.preventDefault();
        setShowCreateModal(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isAuthenticated]);

  // Real-time price streaming
  useEffect(() => {
    try {
      PriceStreamService.connect();
      
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
      console.error('Price stream connection failed:', error);
    }
  }, []);

  // Generate trade ideas with enhanced data
  const generateIdeas = useCallback(() => {
    return [
      {
        id: 1,
        author: { id: 1, name: 'TechTrader', avatar: '', followers: 12500, reputation: 4.8, verified: true, specialty: 'AI & Semiconductors' },
        symbol: 'NVDA',
        type: 'LONG',
        title: 'NVIDIA: AI Boom Continues with Strong Q4 Guidance',
        summary: 'NVIDIA remains the clear leader in AI chips. With data center revenue up 200% YoY and new AI chip announcements, fundamentals remain incredibly strong.',
        analysis: `Key bullish points:
• Dominant market share in AI/ML accelerators
• Strong data center growth continuing into 2024
• Gaming segment recovering with new RTX 40 series
• Gross margins expanding due to premium pricing
• Partnership with all major cloud providers`,
        fundamentalData: {
          pe: 65.2,
          eps: 2.75,
          marketCap: '1.2T',
          revenue: '60.9B',
          netIncome: '29.8B',
          debtToEquity: 0.42,
          currentRatio: 4.2
        },
        optionsData: {
          iv: 45.5,
          putCallRatio: 0.85,
          maxPain: 490,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 2450,
          ownership: 68.5,
          topHolders: ['Vanguard', 'BlackRock', 'State Street']
        },
        shortInterest: {
          sharesShorted: '45.2M',
          daysToCover: 4.2,
          shortPercent: 1.8,
          squeezePotential: 'Medium'
        },
        earnings: {
          nextEarnings: '2024-02-21',
          estimate: 4.52,
          surprise: '+12.5%'
        },
        entryPrice: 485.50,
        currentPrice: 495.20,
        targetPrice: 550.00,
        stopLoss: 420.00,
        riskReward: '2.5:1',
        timeframe: '3-6 months',
        upvotes: 2345,
        downvotes: 156,
        comments: 89,
        tags: ['AI', 'Semiconductors', 'Growth', 'Leader'],
        timestamp: '2024-01-15T10:30:00',
        sentiment: 'bullish',
        confidence: 85,
        aiScore: 88,
        chartIndicators: { rsi: 68, macd: 'bullish', bollinger: 'upper' },
        anomalyScore: 0.15,
        volumeSpike: false,
        priceAlert: { type: 'above', price: 500 }
      },
      {
        id: 2,
        author: { id: 2, name: 'ValueInvestor', avatar: '', followers: 8900, reputation: 4.5, verified: true, specialty: 'Value Investing' },
        symbol: 'AAPL',
        type: 'LONG',
        title: 'Apple: Undervalued with Strong Services Growth',
        summary: 'AAPL trading at 25x earnings despite 15% EPS growth. Services business now 25% of revenue with 80%+ gross margins.',
        analysis: `Investment thesis:
• iPhone cycle turning positive
• Services providing strong margin expansion
• India market opportunity untapped
• Buyback and dividend growth continuing
• Warren Buffett endorsement adds credibility`,
        fundamentalData: {
          pe: 28.5,
          eps: 6.15,
          marketCap: '2.8T',
          revenue: '383.3B',
          netIncome: '97.0B',
          debtToEquity: 1.8,
          currentRatio: 0.99
        },
        optionsData: {
          iv: 22.3,
          putCallRatio: 0.92,
          maxPain: 175,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 3200,
          ownership: 58.2,
          topHolders: ['Berkshire Hathaway', 'Vanguard', 'BlackRock']
        },
        shortInterest: {
          sharesShorted: '102.4M',
          daysToCover: 5.1,
          shortPercent: 0.65,
          squeezePotential: 'Low'
        },
        earnings: {
          nextEarnings: '2024-02-01',
          estimate: 2.10,
          surprise: '+5.2%'
        },
        entryPrice: 175.00,
        currentPrice: 178.50,
        targetPrice: 210.00,
        stopLoss: 155.00,
        riskReward: '2.8:1',
        timeframe: '6-12 months',
        upvotes: 1890,
        downvotes: 234,
        comments: 156,
        tags: ['Value', 'Blue Chip', 'Dividend', 'Services'],
        timestamp: '2024-01-15T09:15:00',
        sentiment: 'bullish',
        confidence: 78,
        aiScore: 75,
        chartIndicators: { rsi: 55, macd: 'bullish', bollinger: 'middle' },
        anomalyScore: 0.08,
        volumeSpike: false,
        priceAlert: { type: 'above', price: 185 }
      },
      {
        id: 3,
        author: { id: 3, name: 'CryptoKing', avatar: '', followers: 45000, reputation: 4.2, verified: true, specialty: 'Crypto & Fintech' },
        symbol: 'COIN',
        type: 'LONG',
        title: 'Coinbase: Riding the Bitcoin ETF Wave',
        summary: 'COIN benefiting directly from SEC approval of Bitcoin ETFs. Trading volumes surging and fee revenue following suit.',
        analysis: `Catalysts ahead:
• Bitcoin ETF inflows driving volume
• SEC decision on Ethereum ETF
• Institutional adoption accelerating
• Strong balance sheet, no debt
• Strategic partnerships announced`,
        fundamentalData: {
          pe: 145.2,
          eps: 1.15,
          marketCap: '45.2B',
          revenue: '3.1B',
          netIncome: '-0.8B',
          debtToEquity: 0.15,
          currentRatio: 2.8
        },
        optionsData: {
          iv: 78.5,
          putCallRatio: 0.65,
          maxPain: 165,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 450,
          ownership: 42.5,
          topHolders: ['ARK Invest', 'Vanguard', 'Goldman Sachs']
        },
        shortInterest: {
          sharesShorted: '12.5M',
          daysToCover: 8.5,
          shortPercent: 8.2,
          squeezePotential: 'High'
        },
        earnings: {
          nextEarnings: '2024-02-15',
          estimate: 1.85,
          surprise: '+15.8%'
        },
        entryPrice: 145.00,
        currentPrice: 168.75,
        targetPrice: 200.00,
        stopLoss: 120.00,
        riskReward: '2.1:1',
        timeframe: '1-3 months',
        upvotes: 3200,
        downvotes: 450,
        comments: 234,
        tags: ['Crypto', 'Fintech', 'Momentum', 'ETF'],
        timestamp: '2024-01-14T16:45:00',
        sentiment: 'bullish',
        confidence: 72,
        aiScore: 82,
        chartIndicators: { rsi: 72, macd: 'bullish', bollinger: 'upper' },
        anomalyScore: 0.45,
        volumeSpike: true,
        priceAlert: { type: 'above', price: 175 }
      },
      {
        id: 4,
        author: { id: 4, name: 'MacroStrategist', avatar: '', followers: 23000, reputation: 4.6, verified: true, specialty: 'Macro & Bonds' },
        symbol: 'TLT',
        type: 'LONG',
        title: 'Treasury Bonds: Fed Pivot Incoming',
        summary: 'Bonds offering incredible value at these levels. Fed will likely cut rates in Q2, bond prices will rally significantly.',
        analysis: `Why bonds now:
• Yields at 15-year highs
• Fed pivot expected in coming months
• Inflation clearly trending lower
• Economic slowdown accelerating
• BlackRock, Bond King buying`,
        fundamentalData: {
          pe: 0,
          eps: 0,
          marketCap: '45.2B',
          revenue: '2.1B',
          netIncome: '1.8B',
          debtToEquity: 0,
          currentRatio: 1.0
        },
        optionsData: {
          iv: 18.5,
          putCallRatio: 1.15,
          maxPain: 95,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 890,
          ownership: 78.5,
          topHolders: ['BlackRock', 'Vanguard', 'Pimco']
        },
        shortInterest: {
          sharesShorted: '0',
          daysToCover: 0,
          shortPercent: 0,
          squeezePotential: 'N/A'
        },
        earnings: {
          nextEarnings: 'N/A',
          estimate: 0,
          surprise: 'N/A'
        },
        entryPrice: 92.50,
        currentPrice: 94.20,
        targetPrice: 105.00,
        stopLoss: 88.00,
        riskReward: '3.1:1',
        timeframe: '6-12 months',
        upvotes: 1560,
        downvotes: 320,
        comments: 98,
        tags: ['Bonds', 'Macro', 'Value', 'Fed'],
        timestamp: '2024-01-14T11:20:00',
        sentiment: 'bullish',
        confidence: 75,
        aiScore: 72,
        chartIndicators: { rsi: 35, macd: 'bullish', bollinger: 'lower' },
        anomalyScore: 0.12,
        volumeSpike: false,
        priceAlert: { type: 'above', price: 98 }
      },
      {
        id: 5,
        author: { id: 5, name: 'ShortSqueezeHunter', avatar: '', followers: 18000, reputation: 4.1, verified: false, specialty: 'Short Selling' },
        symbol: 'PLTR',
        type: 'SHORT',
        title: 'Palantir: Overvalued AI Hype Stock',
        summary: 'PLTR trading at 20x revenue with minimal growth. Commercial segment struggling to gain traction despite AI hype.',
        analysis: `Bear case:
• Valuation absurd at current levels
• Government dependency a risk
• Competition intensifying from Big Tech
• History of profitability issues
• Insider selling ongoing`,
        fundamentalData: {
          pe: 0,
          eps: -0.45,
          marketCap: '42.5B',
          revenue: '2.1B',
          netIncome: '-0.9B',
          debtToEquity: 0.25,
          currentRatio: 4.5
        },
        optionsData: {
          iv: 65.8,
          putCallRatio: 0.55,
          maxPain: 18,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 580,
          ownership: 32.5,
          topHolders: ['Morgan Stanley', 'Citadel', 'DE Shaw']
        },
        shortInterest: {
          sharesShorted: '85.2M',
          daysToCover: 12.5,
          shortPercent: 18.5,
          squeezePotential: 'Very High'
        },
        earnings: {
          nextEarnings: '2024-02-05',
          estimate: 0.08,
          surprise: '-25.2%'
        },
        entryPrice: 20.50,
        currentPrice: 18.45,
        targetPrice: 12.00,
        stopLoss: 25.00,
        riskReward: '2.4:1',
        timeframe: '1-3 months',
        upvotes: 890,
        downvotes: 1200,
        comments: 178,
        tags: ['Short', 'Overvalued', 'Short Squeeze', 'AI'],
        timestamp: '2024-01-13T14:30:00',
        sentiment: 'bearish',
        confidence: 68,
        aiScore: 55,
        chartIndicators: { rsi: 78, macd: 'bearish', bollinger: 'upper' },
        anomalyScore: 0.68,
        volumeSpike: true,
        priceAlert: { type: 'below', price: 17 }
      },
      {
        id: 6,
        author: { id: 6, name: 'DividendHunter', avatar: '', followers: 15600, reputation: 4.4, verified: true, specialty: 'Dividend Investing' },
        symbol: 'KO',
        type: 'LONG',
        title: 'Coca-Cola: Defensive Pick with 7% Yield',
        summary: 'JNGL now part of KO - incredible yield and dividend growth. Recession resistant business with pricing power.',
        analysis: `Why KO:
• 60+ year dividend growth streak
• Strong pricing power globally
• Emerging market exposure
• Portfolio of iconic brands
• Reasonable valuation at 24x earnings`,
        fundamentalData: {
          pe: 24.5,
          eps: 2.42,
          marketCap: '268.5B',
          revenue: '45.8B',
          netIncome: '10.5B',
          debtToEquity: 1.75,
          currentRatio: 1.15
        },
        optionsData: {
          iv: 15.2,
          putCallRatio: 1.05,
          maxPain: 58,
          nextExpiry: '2024-02-16'
        },
        institutionalHoldings: {
          institutions: 2100,
          ownership: 72.5,
          topHolders: ['Berkshire Hathaway', 'Vanguard', 'BlackRock']
        },
        shortInterest: {
          sharesShorted: '15.2M',
          daysToCover: 3.2,
          shortPercent: 0.35,
          squeezePotential: 'Low'
        },
        earnings: {
          nextEarnings: '2024-02-12',
          estimate: 0.48,
          surprise: '+2.1%'
        },
        entryPrice: 58.00,
        currentPrice: 59.40,
        targetPrice: 70.00,
        stopLoss: 52.00,
        riskReward: '2.2:1',
        timeframe: '12-18 months',
        upvotes: 980,
        downvotes: 120,
        comments: 67,
        tags: ['Dividend', 'Defensive', 'Blue Chip', 'Consumer'],
        timestamp: '2024-01-13T09:45:00',
        sentiment: 'bullish',
        confidence: 82,
        aiScore: 78,
        chartIndicators: { rsi: 48, macd: 'neutral', bollinger: 'middle' },
        anomalyScore: 0.05,
        volumeSpike: false,
        priceAlert: { type: 'above', price: 62 }
      }
    ];
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      const ideasData = generateIdeas();
      setIdeas(ideasData);
      
      // Generate AI signals
      setAiSignals([
        { symbol: 'NVDA', signal: 'STRONG_BUY', confidence: 88, reason: 'AI sector momentum continues' },
        { symbol: 'AAPL', signal: 'BUY', confidence: 75, reason: 'Services growth accelerating' },
        { symbol: 'COIN', signal: 'BUY', confidence: 82, reason: 'Bitcoin ETF tailwinds' },
        { symbol: 'TLT', signal: 'BUY', confidence: 72, reason: 'Fed pivot expected' },
        { symbol: 'PLTR', signal: 'HOLD', confidence: 55, reason: 'Overvalued but high short interest' },
      ]);
      
      // Generate anomalies
      setAnomalies([
        { symbol: 'COIN', type: 'VOLUME_SPIKE', severity: 'high', description: 'Volume 250% above average' },
        { symbol: 'PLTR', type: 'PRICE_MOVE', severity: 'medium', description: 'Unusual price movement detected' },
        { symbol: 'NVDA', type: 'OPTIONS_ACTIVITY', severity: 'low', description: 'Heavy call options activity' },
      ]);
      
      setLoading(false);
    }, 400);

    return () => clearTimeout(timer);
  }, [generateIdeas]);

  const t = translations[language] || translations.en;

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = (now - date) / 1000 / 60;
    
    if (diff < 60) return `${Math.floor(diff)}m ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)}h ago`;
    return `${Math.floor(diff / 1440)}d ago`;
  };

  const getScore = (idea) => {
    return idea.upvotes - idea.downvotes + (idea.comments * 2);
  };

  const sortedIdeas = [...ideas]
    .filter(idea => {
      if (filter === 'all') return true;
      if (filter === 'long') return idea.type === 'LONG';
      if (filter === 'short') return idea.type === 'SHORT';
      if (filter === 'following') return idea.author.id && followedExperts.includes(idea.author.id);
      if (filter === 'bullish') return idea.sentiment === 'bullish';
      if (filter === 'bearish') return idea.sentiment === 'bearish';
      if (filter === 'highConfidence') return idea.confidence >= 80;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          idea.symbol.toLowerCase().includes(query) ||
          idea.title.toLowerCase().includes(query) ||
          idea.tags.some(tag => tag.toLowerCase().includes(query))
        );
      }
      if (selectedTags.length > 0) {
        return selectedTags.some(tag => idea.tags.includes(tag));
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'trending') return getScore(b) - getScore(a);
      if (sortBy === 'newest') return new Date(b.timestamp) - new Date(a.timestamp);
      if (sortBy === 'confidence') return b.confidence - a.confidence;
      if (sortBy === 'aiScore') return b.aiScore - a.aiScore;
      return 0;
    });

  const formatNumber = (num) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const getPriceColor = (symbol) => {
    const priceData = realtimePrices[symbol];
    if (priceData) {
      return priceData.changePercent >= 0 ? '#22c55e' : '#ef4444';
    }
    return '#e0e0e0';
  };

  const toggleFollowExpert = (id) => {
    if (followedExperts.includes(id)) {
      setFollowedExperts(followedExperts.filter(f => f !== id));
    } else {
      setFollowedExperts([...followedExperts, id]);
    }
  };

  const addToWatchlist = (symbol) => {
    alert(`Added ${symbol} to watchlist`);
  };

  const createPriceAlert = (idea) => {
    alert(`Creating price alert for ${idea.symbol} at $${idea.priceAlert?.price || idea.targetPrice}`);
  };

  const exportToPDF = () => {
    alert('Exporting trade ideas to PDF...');
  };

  const exportToExcel = () => {
    alert('Exporting trade ideas to Excel...');
  };

  const handleLogin = async (email, password) => {
    await login(email, password);
    setShowAuthModal(false);
  };

  const handleRegister = async (name, email, password) => {
    await register(name, email, password);
    setShowAuthModal(false);
  };

  const allTags = [...new Set(ideas.flatMap(idea => idea.tags))];

  if (loading) {
    return (
      <div className={`trade-ideas-feed loading ${isDarkMode ? 'dark' : 'light'}`}>
        <div className="loading-spinner"></div>
        <p>{t.loading}</p>
      </div>
    );
  }

  return (
    <div className={`trade-ideas-feed ${isDarkMode ? 'dark' : 'light'}`}>
      {/* Enhanced Header */}
      <div className="feed-header">
        <div className="header-left">
          <h2>{t.tradeIdeas}</h2>
          <p>{t.communityShared}</p>
        </div>
        <div className="header-controls">
          <select 
            className="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="en">🇺🇸 EN</option>
            <option value="es">🇪🇸 ES</option>
            <option value="zh">🇨🇳 中文</option>
          </select>
          
          <button 
            className="theme-toggle"
            onClick={() => setIsDarkMode(!isDarkMode)}
          >
            {isDarkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          
          <button className="export-btn" onClick={exportToPDF}>
            {t.exportPDF}
          </button>
          <button className="export-btn" onClick={exportToExcel}>
            {t.exportExcel}
          </button>
          
          <button 
            className="shortcuts-btn"
            onClick={() => setShowKeyboardShortcuts(!showKeyboardShortcuts)}
          >
            Keyboard Shortcuts
          </button>
          
          {isAuthenticated ? (
            <button className="create-btn">{t.newTradeIdea}</button>
          ) : (
            <button 
              className="create-btn"
              onClick={() => { setAuthMode('login'); setShowAuthModal(true); }}
            >
              Sign In
            </button>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <div className="search-section">
        <div className="search-bar">
          <span className="search-icon"></span>
          <input
            ref={searchInputRef}
            type="text"
            placeholder={t.searchIdeas}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <span className="search-shortcut">Ctrl+K</span>
        </div>
        <div className="tag-filters">
          {allTags.slice(0, 8).map(tag => (
            <button
              key={tag}
              className={`tag-filter ${selectedTags.includes(tag) ? 'active' : ''}`}
              onClick={() => {
                if (selectedTags.includes(tag)) {
                  setSelectedTags(selectedTags.filter(t => t !== tag));
                } else {
                  setSelectedTags([...selectedTags, tag]);
                }
              }}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      {/* AI Signals Panel */}
      <div className="ai-signals-panel">
        <h3>{t.aiSignals}</h3>
        <div className="signals-grid">
          {aiSignals.map(signal => (
            <div key={signal.symbol} className={`signal-card ${signal.signal.toLowerCase()}`}>
              <span className="signal-symbol">{signal.symbol}</span>
              <span className="signal-type">{signal.signal}</span>
              <span className="signal-confidence">{signal.confidence}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Anomaly Detection Panel */}
      <div className="anomaly-panel">
        <h3>{t.anomalyDetection}</h3>
        <div className="anomaly-list">
          {anomalies.map((anomaly, i) => (
            <div key={i} className={`anomaly-item ${anomaly.severity}`}>
              <span className="anomaly-symbol">{anomaly.symbol}</span>
              <span className="anomaly-type">{anomaly.type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Real-time Prices Ticker */}
      <div className="realtime-ticker">
        {ideas.slice(0, 6).map(idea => {
          const priceData = realtimePrices[idea.symbol] || {};
          const change = priceData.changePercent || (Math.random() - 0.5) * 5;
          return (
            <div key={idea.symbol} className="ticker-item">
              <span className="ticker-symbol">{idea.symbol}</span>
              <span className="ticker-price">${idea.currentPrice}</span>
              <span className={`ticker-change ${change >= 0 ? 'positive' : 'negative'}`}>
                {change >= 0 ? '+' : ''}{change.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>

      {/* Filters */}
      <div className="feed-filters">
        <div className="filter-tabs">
          {[
            { key: 'all', label: 'All Ideas' },
            { key: 'long', label: 'Long' },
            { key: 'short', label: 'Short' },
            { key: 'following', label: 'Following' },
          ].map(tab => (
            <button
              key={tab.key}
              className={`filter-tab ${filter === tab.key ? 'active' : ''}`}
              onClick={() => setFilter(tab.key)}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <div className="sort-options">
          <label>Sort by:</label>
          {[
            { key: 'trending', label: 'Trending' },
            { key: 'newest', label: 'Newest' },
            { key: 'confidence', label: 'Confidence' },
          ].map(option => (
            <button
              key={option.key}
              className={`sort-btn ${sortBy === option.key ? 'active' : ''}`}
              onClick={() => setSortBy(option.key)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Ideas Feed */}
      <div className="ideas-feed">
        {sortedIdeas.map(idea => (
          <div key={idea.id} className={`idea-card ${idea.type.toLowerCase()}`}>
            {/* Vote Section */}
            <div className="vote-section">
              <button className="vote-btn upvote">▲</button>
              <span className="vote-count">{formatNumber(getScore(idea))}</span>
              <button className="vote-btn downvote">▼</button>
            </div>

            {/* Content Section */}
            <div className="idea-content">
              <div className="idea-header">
                <div className="author-info">
                  <span className="author-avatar">{idea.author.avatar}</span>
                  <div className="author-details">
                    <span className="author-name">{idea.author.name}</span>
                    <div className="author-meta">
                      <span className="reputation">{idea.author.reputation}</span>
                      <span className="followers">{formatNumber(idea.author.followers)} followers</span>
                    </div>
                  </div>
                </div>
                <div className="idea-meta">
                  <span className={`type-badge ${idea.type.toLowerCase()}`}>{idea.type}</span>
                  <span className="timestamp">{formatDate(idea.timestamp)}</span>
                </div>
              </div>

              <div className="idea-title" onClick={() => setSelectedIdea(idea)}>
                <span className="symbol-tag">{idea.symbol}</span>
                <h3>{idea.title}</h3>
              </div>

              <p className="idea-summary">{idea.summary}</p>

              {/* Trade Details */}
              <div className="trade-details">
                <div className="detail-grid">
                  <div className="detail-item">
                    <span className="detail-label">Entry</span>
                    <span className="detail-value">${idea.entryPrice}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Current</span>
                    <span className="detail-value">${idea.currentPrice}</span>
                  </div>
                  <div className="detail-item target">
                    <span className="detail-label">Target</span>
                    <span className="detail-value">${idea.targetPrice}</span>
                  </div>
                  <div className="detail-item stop">
                    <span className="detail-label">Stop</span>
                    <span className="detail-value">${idea.stopLoss}</span>
                  </div>
                </div>
                <div className="risk-reward">
                  <span className="rr-label">Risk/Reward</span>
                  <span className="rr-value">{idea.riskReward}</span>
                </div>
              </div>

              {/* Tags */}
              <div className="idea-tags">
                {idea.tags.map((tag, i) => (
                  <span key={i} className="tag">{tag}</span>
                ))}
              </div>

              {/* Footer */}
              <div className="idea-footer">
                <div className="footer-left">
                  <button className="footer-btn">
                    {idea.comments} comments
                  </button>
                  <button className="footer-btn">
                    Share
                  </button>
                  <button className="footer-btn">
                    Save
                  </button>
                </div>
                <div className="confidence-badge">
                  <span className="confidence-label">Confidence</span>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${idea.confidence}%` }}
                    ></div>
                  </div>
                  <span className="confidence-value">{idea.confidence}%</span>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Idea Detail Modal */}
      {selectedIdea && (
        <div className="modal-overlay" onClick={() => setSelectedIdea(null)}>
          <div className="idea-detail-modal" onClick={e => e.stopPropagation()}>
            <button className="close-btn" onClick={() => setSelectedIdea(null)}>×</button>
            
            <div className="modal-header">
              <span className={`type-badge ${selectedIdea.type.toLowerCase()}`}>
                {selectedIdea.type}
              </span>
              <span className="symbol-tag large">{selectedIdea.symbol}</span>
              <h2>{selectedIdea.title}</h2>
              <div className="author-info">
                <span className="author-avatar">{selectedIdea.author.avatar}</span>
                <span className="author-name">{selectedIdea.author.name}</span>
                <span className="timestamp">{formatDate(selectedIdea.timestamp)}</span>
              </div>
            </div>

            <div className="modal-body">
              <div className="analysis-section">
                <h3>Full Analysis</h3>
                <div className="analysis-content">
                  {selectedIdea.analysis.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </div>

              <div className="trade-setup">
                <h3>Trade Setup</h3>
                <div className="setup-grid">
                  <div className="setup-item">
                    <span className="label">Entry</span>
                    <span className="value">${selectedIdea.entryPrice}</span>
                  </div>
                  <div className="setup-item">
                    <span className="label">Target</span>
                    <span className="value">${selectedIdea.targetPrice}</span>
                  </div>
                  <div className="setup-item">
                    <span className="label">Stop Loss</span>
                    <span className="value">${selectedIdea.stopLoss}</span>
                  </div>
                  <div className="setup-item">
                    <span className="label">Risk/Reward</span>
                    <span className="value">{selectedIdea.riskReward}</span>
                  </div>
                  <div className="setup-item">
                    <span className="label">Timeframe</span>
                    <span className="value">{selectedIdea.timeframe}</span>
                  </div>
                  <div className="setup-item">
                    <span className="label">Confidence</span>
                    <span className="value">{selectedIdea.confidence}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="action-btn primary">Copy Trade</button>
              <button className="action-btn secondary">Add to Watchlist</button>
              <button className="action-btn secondary">Set Alert</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TradeIdeasFeed;

