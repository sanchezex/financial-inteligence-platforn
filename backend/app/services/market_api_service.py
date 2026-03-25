'''Real-Time Market Data APIs Service
Aggregates multiple providers:
- Polygon.io: Stocks/Commodities/Options (US markets)
- OANDA: Forex (majors + exotics, 24/7)
- CCXT/Binance: Crypto + Commodity Futures (global)

Async tick streaming, OHLCV, quotes. Rate-limit safe. Free-tier compatible.
'''

import asyncio
import logging
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
import ccxt.async_support as ccxt
import yfinance as yf
from polygon import RESTClient, WebSocketClient
import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import pricing as pricing_http
from oandapyV20.contrib.requests import MarketOrderRequest

from app.core.config import settings
from app.core.logging import get_logger
from .nse_symbols import NSE_SYMBOLS
from app.core.config import settings
from app.core.logging import get_logger
logger = get_logger(__name__)

logger = get_logger(__name__)

class MarketAPIService:
    def __init__(self):
        self.polygon_client = None
        self.oanda_client = None
        self.binance_client = None
        self.session = None
        self._initialized = False
        
    async def init(self):
        '''Initialize all API clients'''
        if self._initialized:
            return
            
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=20)
        )
        
        # NSE-ONLY: No other providers
        logger.info("NSE MarketAPI initialized (Yahoo Finance .KN only)")
        
    async def close(self):
        '''Cleanup clients'''
        logger.info("NSE Market API service closed")
    
    # =========================================================================
    # QUOTES (Latest bid/ask/last)
    # =========================================================================
    def validate_nse_symbol(self, symbol: str) -> bool:
        '''Validate symbol is NSE Kenya stock'''
        if symbol not in NSE_SYMBOLS:
            logger.warning(f"Non-NSE symbol requested: {symbol}")
            return False
        return True
    
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        '''Get NSE quote ONLY via Yahoo Finance (.KN tickers)'''
        if not self.validate_nse_symbol(symbol):
            return None
        
        try:
            yahoo_ticker = f"{symbol}.KN"  # Kenyan NSE format
            ticker = yf.Ticker(yahoo_ticker)
            info = ticker.info or {}
            hist = ticker.history(period="1d")
            if hist.empty:
                logger.debug(f"No data for {yahoo_ticker}")
                return None
            
            last_price = float(hist['Close'].iloc[-1])
            return {
                'provider': 'yahoo_nse',
                'symbol': symbol,
                'bid': round(last_price * 0.999, 2),
                'ask': round(last_price * 1.001, 2),
                'last': round(last_price, 2),
                'volume': int(info.get('volume', 0)),
                'timestamp': datetime.now().timestamp() * 1000,
                'currency': 'KES'
            }
        except Exception as e:
            logger.debug(f"NSE quote {symbol} failed: {e}")
            return None
        # OLD CODE REMOVED - NSE-only handled above
    
    # =========================================================================
    # TICK STREAM (Realtime quotes)
    # =========================================================================  
    async def stream_ticks(self, symbols: List[str]) -> AsyncGenerator[Dict, None]:
        '''NSE tick polling (yfinance no WS, poll every 5s) - yields for ClickHouse'''
        validated = [s for s in symbols if self.validate_nse_symbol(s)]
        if not validated:
            logger.warning("No valid NSE symbols for streaming")
            return
        
        while True:  # Infinite stream
            for symbol in validated:
                quote = await self.get_quote(symbol)
                if quote:
                    quote['type'] = 'tick'
                    yield quote
            await asyncio.sleep(5)  # Poll interval
        '''Realtime tick stream - yields dicts for ClickHouse insert'''
        # Polygon WebSocket for stocks/commodities  
        # NSE streaming only via polling (no WS providers for NSE)
            async for message in self._polygon_stream(symbols):
                yield message
                
        # NSE-only polling above - no other streams
    
    # DISABLED non-NSE streams
    async def _polygon_stream(self, symbols): raise NotImplementedError("NSE only")
    async def _oanda_stream(self, symbols): raise NotImplementedError("NSE only")
    async def _binance_stream(self, symbols): raise NotImplementedError("NSE only")
    
    # =========================================================================
    # BARS (OHLCV)
    # =========================================================================
    async def get_bars(self, symbol: str, timeframe: str = 'minute', 
                      from_ts: datetime = None, to_ts: datetime = None, 
                      limit: int = 1000) -> List[Dict]:
        '''NSE OHLCV via yfinance'''
        if not self.validate_nse_symbol(symbol):
            return []
        try:
            yahoo_ticker = f"{symbol}.KN"
            ticker = yf.Ticker(yahoo_ticker)
            period_map = {'1d': '1d', '5d': '5d', '1mo': '1mo', '3mo': '3mo', '6mo': '6mo', '1y': '1y', '2y': '2y', '5y': '5y', '10y': '10y', 'ytd': 'ytd', 'max': 'max'}
            hist = ticker.history(period=period_map.get(timeframe, '1mo'), interval=timeframe)
            return hist.reset_index().to_dict('records')
        except:
            return []
        '''Get OHLCV bars'''
        if self.polygon_client:
            try:
                bars = self.polygon_client.list_aggs(
                    symbol, 1, 'minute', 
                    from_=from_ts, to=to_ts, limit=limit
                )
                return [b.__dict__ for b in bars]
            except:
                pass
        
        if self.binance_client:
            try:
                ohlcv = await self.binance_client.fetch_ohlcv(symbol, timeframe, limit=limit)
                return [{
                    'timestamp': datetime.fromtimestamp(candle[0]/1000),
                    'open': candle[1], 'high': candle[2], 
                    'low': candle[3], 'close': candle[4], 'volume': candle[5]
                } for candle in ohlcv]
            except:
                pass
        return []
    
    # =========================================================================
    # SYMBOL SEARCH & METADATA
    # =========================================================================
    async def search_symbols(self, query: str, asset_class: str = 'all') -> List[Dict]:
        '''Search forex/commodities/stocks'''
        results = []
        
        if self.polygon_client and asset_class != 'forex':
            try:
                results.extend(self.polygon_client.list_tickers(market='stocks', 
                    ticker=query+'*', active=True, limit=20))
            except:
                pass
        
        # Add forex/commodity search via OANDA/Binance
        return results
    
    # ============================================================================
    # ORDER EXECUTION (Paper trading first)
    # ============================================================================
    async def place_order(self, symbol: str, side: str, quantity: float, 
                         order_type: str = 'market', price: float = None,
                         account_id: str = None) -> Dict:
        '''Place trade order (paper/demo first)'''
        if not account_id:
            # Paper trading
            return {
                'status': 'filled_paper',
                'order_id': f'PAPER_{int(datetime.now().timestamp())}',
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price or 100.0,  # mock fill
                'timestamp': datetime.now()
            }
        
        # Live execution via broker
        pass  # TODO: implement live brokers

# Global singleton
market_api_service = MarketAPIService()

__all__ = ['market_api_service']

