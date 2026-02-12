
import React, { useState, useEffect, useRef } from 'react';
import './AdvancedChart.css';

function AdvancedChart({ symbol, period = '1M' }) {
  const [chartData, setChartData] = useState([]);
  const [indicators, setIndicators] = useState({
    rsi: true,
    macd: true,
    bollinger: false
  });
  const [loading, setLoading] = useState(true);
  const [hoveredData, setHoveredData] = useState(null);

  useEffect(() => {
    // Generate candlestick data
    const generateCandles = () => {
      const candles = [];
      let price = 150 + Math.random() * 50;
      const numDays = period === '1D' ? 24 : period === '1W' ? 7 : period === '1M' ? 30 : period === '3M' ? 90 : period === '1Y' ? 365 : 500;

      for (let i = 0; i < numDays; i++) {
        const volatility = 0.02;
        const change = price * volatility * (Math.random() - 0.5) * 2;
        const open = price;
        const close = price + change;
        const high = Math.max(open, close) + Math.abs(change) * Math.random();
        const low = Math.min(open, close) - Math.abs(change) * Math.random();
        const volume = Math.floor(Math.random() * 50000000) + 10000000;

        candles.push({
          date: new Date(Date.now() - (numDays - i) * 24 * 60 * 60 * 1000),
          open,
          high,
          low,
          close,
          volume
        });

        price = close;
      }
      return candles;
    };

    const timer = setTimeout(() => {
      setChartData(generateCandles());
      setLoading(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [symbol, period]);

  // Calculate technical indicators
  const calculateRSI = (data, period = 14) => {
    if (data.length < period) return null;
    const gains = [];
    const losses = [];

    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close;
      gains.push(change > 0 ? change : 0);
      losses.push(change < 0 ? Math.abs(change) : 0);
    }

    const avgGain = gains.slice(-period).reduce((a, b) => a + b, 0) / period;
    const avgLoss = losses.slice(-period).reduce((a, b) => a + b, 0) / period;

    if (avgLoss === 0) return 100;
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  };

  const calculateMACD = (data) => {
    if (data.length < 26) return null;

    const ema12 = calculateEMA(data, 12);
    const ema26 = calculateEMA(data, 26);

    if (!ema12 || !ema26) return null;

    const macdLine = ema12 - ema26;
    const signalLine = calculateSignalLine(data, macdLine);
    const histogram = macdLine - signalLine;

    return { macdLine, signalLine, histogram };
  };

  const calculateEMA = (data, period) => {
    if (data.length < period) return null;
    const k = 2 / (period + 1);
    let ema = data[0].close;

    for (let i = 1; i < data.length; i++) {
      ema = data[i].close * k + ema * (1 - k);
    }

    return ema;
  };

  const calculateSignalLine = (data, initialMacd) => {
    const period = 9;
    if (data.length < 26 + period) return null;

    const k = 2 / (period + 1);
    let signal = initialMacd;

    for (let i = 0; i < period; i++) {
      const idx = data.length - period + i;
      if (idx > 0) {
        const macd = data[idx].close - data[idx - 1].close;
        signal = macd * k + signal * (1 - k);
      }
    }

    return signal;
  };

  const calculateBollingerBands = (data, period = 20) => {
    if (data.length < period) return null;

    const prices = data.slice(-period).map(d => d.close);
    const sma = prices.reduce((a, b) => a + b, 0) / period;
    const stdDev = Math.sqrt(prices.reduce((sum, p) => sum + Math.pow(p - sma, 2), 0) / period);

    return {
      upper: sma + 2 * stdDev,
      middle: sma,
      lower: sma - 2 * stdDev
    };
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(price);
  };

  const rsi = chartData.length > 0 ? calculateRSI(chartData) : null;
  const macd = chartData.length > 0 ? calculateMACD(chartData) : null;
  const bollinger = chartData.length > 0 ? calculateBollingerBands(chartData) : null;

  const getChartPath = (key = 'close') => {
    if (chartData.length === 0) return '';
    const prices = chartData.map(d => d[key]);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min || 1;

    return chartData.map((d, i) => {
      const x = (i / (chartData.length - 1)) * 280;
      const y = 80 - ((d[key] - min) / range) * 70;
      return `${x},${y}`;
    }).join(' ');
  };

  if (loading) {
    return (
      <div className="advanced-chart loading">
        <div className="chart-loading">
          <div className="loading-spinner"></div>
          <p>Loading {symbol} chart...</p>
        </div>
      </div>
    );
  }

  const currentPrice = chartData.length > 0 ? chartData[chartData.length - 1].close : 0;
  const priceChange = chartData.length > 1
    ? chartData[chartData.length - 1].close - chartData[0].close
    : 0;
  const isPositive = priceChange >= 0;

  return (
    <div className="advanced-chart">
      {/* Header */}
      <div className="chart-header">
        <div className="symbol-info">
          <h3>{symbol}</h3>
          <span className="current-price">{formatPrice(currentPrice)}</span>
          <span className={`price-change ${isPositive ? 'positive' : 'negative'}`}>
            {isPositive ? '+' : ''}{formatPrice(priceChange)}
          </span>
        </div>
        <div className="indicator-toggles">
          <button
            className={`indicator-btn ${indicators.rsi ? 'active' : ''}`}
            onClick={() => setIndicators({ ...indicators, rsi: !indicators.rsi })}
          >
            RSI
          </button>
          <button
            className={`indicator-btn ${indicators.macd ? 'active' : ''}`}
            onClick={() => setIndicators({ ...indicators, macd: !indicators.macd })}
          >
            MACD
          </button>
          <button
            className={`indicator-btn ${indicators.bollinger ? 'active' : ''}`}
            onClick={() => setIndicators({ ...indicators, bollinger: !indicators.bollinger })}
          >
            BB
          </button>
        </div>
      </div>

      {/* Main Chart */}
      <div className="chart-container">
        <svg viewBox="0 0 300 100" className="main-chart">
          <defs>
            <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={isPositive ? '#22c55e20' : '#ef444420'} />
              <stop offset="100%" stopColor={isPositive ? '#22c55e00' : '#ef444400'} />
            </linearGradient>
          </defs>

          {/* Bollinger Bands */}
          {indicators.bollinger && bollinger && (
            <>
              <path
                d={`M0,${80 - ((bollinger.upper - chartData[0].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70} L300,${80 - ((bollinger.upper - chartData[chartData.length - 1].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70}`}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="1"
                strokeDasharray="4,2"
                opacity="0.5"
              />
              <path
                d={`M0,${80 - ((bollinger.middle - chartData[0].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70} L300,${80 - ((bollinger.middle - chartData[chartData.length - 1].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70}`}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="1"
                opacity="0.7"
              />
              <path
                d={`M0,${80 - ((bollinger.lower - chartData[0].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70} L300,${80 - ((bollinger.lower - chartData[chartData.length - 1].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70}`}
                fill="none"
                stroke="#3b82f6"
                strokeWidth="1"
                strokeDasharray="4,2"
                opacity="0.5"
              />
            </>
          )}

          {/* Price Line */}
          <path
            d={`M0,${getChartPath('close').split(' ')[0].split(',')[1]} ${chartData.map((d, i) => `L${(i / (chartData.length - 1)) * 280},${80 - ((d.close - chartData[0].close) / (chartData[chartData.length - 1].close - chartData[0].close || 1)) * 70}`).join(' ')}`}
            fill="none"
            stroke={isPositive ? '#22c55e' : '#ef4444'}
            strokeWidth="2"
          />

          {/* Area fill */}
          <path
            d={`M0,100 ${getChartPath('close').split(' ').map(p => `L${p}`).join(' ')} L300,100 Z`}
            fill="url(#chartGradient)"
          />
        </svg>
      </div>

      {/* Technical Indicators Summary */}
      <div className="indicators-summary">
        {indicators.rsi && rsi !== null && (
          <div className="indicator-card">
            <span className="indicator-label">RSI (14)</span>
            <span className={`indicator-value ${rsi > 70 ? 'overbought' : rsi < 30 ? 'oversold' : ''}`}>
              {rsi.toFixed(1)}
            </span>
          </div>
        )}
        {indicators.macd && macd !== null && (
          <div className="indicator-card">
            <span className="indicator-label">MACD</span>
            <span className={`indicator-value ${macd.macdLine > 0 ? 'positive' : 'negative'}`}>
              {macd.macdLine.toFixed(2)}
            </span>
          </div>
        )}
        {indicators.bollinger && bollinger && (
          <div className="indicator-card">
            <span className="indicator-label">BB Range</span>
            <span className="indicator-value">
              {formatPrice(bollinger.lower)} - {formatPrice(bollinger.upper)}
            </span>
          </div>
        )}
      </div>

      {/* Period Selector */}
      <div className="period-selector">
        {['1D', '1W', '1M', '3M', '1Y', 'ALL'].map(p => (
          <button
            key={p}
            className={`period-btn ${period === p ? 'active' : ''}`}
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}

export default AdvancedChart;

