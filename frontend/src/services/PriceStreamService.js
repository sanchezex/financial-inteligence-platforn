// Real-time price streaming service using Socket.io with axios polling fallback
import io from 'socket.io-client';
import axios from 'axios';

class PriceStreamService {
  constructor() {
    this.subscribers = new Map();
    this.prices = new Map();
    this.isConnected = false;
    this.ws = null;
    this.pollInterval = null;
this.baseUrl = process.env.REACT_APP_WS_URL || 'http://localhost:8000'; // Backend NSE proxy
  }

  connect() {
    if (this.isConnected) return;

    // Try Socket.io connection first
    try {
      this.ws = io(this.baseUrl, {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        timeout: 20000
      });

      this.ws.on('connect', () => {
        this.isConnected = true;
        console.log('PriceStreamService: Socket.io Connected');
        this.startSocketUpdates();
      });

      this.ws.on('disconnect', () => {
        this.isConnected = false;
        console.log('PriceStreamService: Socket.io Disconnected');
        this.startPollingFallback();
      });

  this.ws.on('nse_price_update', (data) => {
        // Ensure timestamp format: YYYY-MM-DD HH:MM:SS
        if (data.timestamp) {
          data.timestamp = new Date(data.timestamp).toISOString().slice(0, 19).replace('T', ' ');
        }
        this.updatePrice(data.symbol, data);
      });

      this.ws.on('connect_error', (error) => {
        console.warn('Socket.io connect error, falling back to polling:', error);
        this.startPollingFallback();
      });

    } catch (error) {
      console.error('Socket.io init failed:', error);
      this.startPollingFallback();
    }
  }

  disconnect() {
    this.isConnected = false;
    if (this.ws) {
      this.ws.disconnect();
      this.ws = null;
    }
    if (this.pollInterval) {
      clearInterval(this.pollInterval);
      this.pollInterval = null;
    }
    console.log('PriceStreamService: Disconnected');
  }

  startSocketUpdates() {
    // Request initial prices
    if (this.ws) {
    this.ws.emit('subscribe_nse_all');
    }
  }

  startPollingFallback() {
    // Axios polling every 5 seconds as fallback (per task example)
    this.pollInterval = setInterval(async () => {
      try {
      const response = await axios.get(`${this.baseUrl}/api/nse-realtime-data`, {
          timeout: 5000
        });
        response.data.forEach(data => {
          this.updatePrice(data.symbol, data);
        });
      } catch (error) {
        console.warn('Polling failed:', error.message);
      }
    }, 5000);
  }

  updatePrice(symbol, data) {
    this.prices.set(symbol, { ...data, symbol, timestamp: Date.now() });
    this.notifySubscribers(symbol, this.prices.get(symbol));
  }

  // Subscribe to price updates for a symbol (backward compatible)
  subscribe(symbol, callback) {
    if (!this.subscribers.has(symbol)) {
      this.subscribers.set(symbol, new Set());
    }
    this.subscribers.get(symbol).add(callback);

    // Send current price immediately
    const currentPrice = this.prices.get(symbol);
    if (currentPrice) {
      callback(currentPrice);
    }

    return () => {
      const symbolSubscribers = this.subscribers.get(symbol);
      if (symbolSubscribers) {
        symbolSubscribers.delete(callback);
        if (symbolSubscribers.size === 0) {
          this.subscribers.delete(symbol);
        }
      }
    };
  }

  // Subscribe to all updates (backward compatible)
  subscribeAll(callback) {
    return this.subscribe('*ALL*', callback);
  }

  notifySubscribers(symbol, data) {
    const symbolSubscribers = this.subscribers.get(symbol);
    if (symbolSubscribers) {
      symbolSubscribers.forEach(callback => callback(data));
    }
    const allSubscribers = this.subscribers.get('*ALL*');
    if (allSubscribers) {
      allSubscribers.forEach(callback => callback(data));
    }
  }

  getPrice(symbol) {
    return this.prices.get(symbol) || null;
  }

  getAllPrices() {
    return Object.fromEntries(this.prices);
  }
}

// Singleton
const priceStreamService = new PriceStreamService();
export default priceStreamService;

