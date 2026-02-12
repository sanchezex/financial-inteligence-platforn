
// Real-time price streaming service using WebSocket
class PriceStreamService {
  constructor() {
    this.subscribers = new Map();
    this.prices = new Map();
    this.isConnected = false;
    this.updateInterval = null;
    this.ws = null;
  }

  // Initialize connection (simulated for demo)
  connect() {
    if (this.isConnected) return;

    // Simulate WebSocket connection
    this.isConnected = true;
    console.log('PriceStreamService: Connected');

    // Start simulated price updates
    this.startSimulatedUpdates();
  }

  disconnect() {
    this.isConnected = false;
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
    console.log('PriceStreamService: Disconnected');
  }

  // Simulate real-time price updates
  startSimulatedUpdates() {
    const symbols = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AMZN', 'TSLA', 'JPM', 'S&P 500', 'DJIA', 'NASDAQ'];

    // Initialize prices
    symbols.forEach(symbol => {
      this.prices.set(symbol, {
        symbol,
        price: 100 + Math.random() * 400,
        change: (Math.random() - 0.5) * 10,
        changePercent: (Math.random() - 0.5) * 5,
        volume: Math.floor(Math.random() * 10000000),
        timestamp: Date.now()
      });
    });

    // Update every 2 seconds
    this.updateInterval = setInterval(() => {
      symbols.forEach(symbol => {
        const current = this.prices.get(symbol);
        if (current) {
          // Random walk price movement
          const change = (Math.random() - 0.5) * 2;
          const newPrice = Math.max(1, current.price + change);
          const priceChange = newPrice - current.price;
          const newChange = current.change + priceChange;
          const newChangePercent = (newChange / (newPrice - newChange)) * 100;

          const updated = {
            ...current,
            price: newPrice,
            change: newChange,
            changePercent: newChangePercent,
            volume: current.volume + Math.floor(Math.random() * 10000),
            timestamp: Date.now()
          };

          this.prices.set(symbol, updated);
          this.notifySubscribers(symbol, updated);
        }
      });
    }, 2000);
  }

  // Subscribe to price updates for a symbol
  subscribe(symbol, callback) {
    if (!this.subscribers.has(symbol)) {
      this.subscribers.set(symbol, new Set());
    }
    this.subscribers.get(symbol).add(callback);

    // Immediately send current price if available
    const currentPrice = this.prices.get(symbol);
    if (currentPrice) {
      callback(currentPrice);
    }

    // Return unsubscribe function
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

  // Subscribe to all price updates
  subscribeAll(callback) {
    return this.subscribe('*ALL*', callback);
  }

  // Notify subscribers of price update
  notifySubscribers(symbol, data) {
    // Notify symbol-specific subscribers
    const symbolSubscribers = this.subscribers.get(symbol);
    if (symbolSubscribers) {
      symbolSubscribers.forEach(callback => callback(data));
    }

    // Notify all-subscribers
    const allSubscribers = this.subscribers.get('*ALL*');
    if (allSubscribers) {
      allSubscribers.forEach(callback => callback(data));
    }
  }

  // Get current price for symbol
  getPrice(symbol) {
    return this.prices.get(symbol) || null;
  }

  // Get all prices
  getAllPrices() {
    return Object.fromEntries(this.prices);
  }
}

// Singleton instance
const priceStreamService = new PriceStreamService();

export default priceStreamService;

