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
from polygon import RESTClient, WebSocketClient
import oandapyV20
from oandapyV20 import API
from oandapyV20.endpoints import pricing as pricing_http
from oandapyV20.contrib.requests import MarketOrderRequest

from app.core.config import settings
from app.core.logging import get_logger

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
        
        # Polygon.io (Stocks/Commodities/Options)
        if settings.POLYGON_API_KEY:
            self.polygon_client = RESTClient(api_key=settings.POLYGON_API_KEY)
            logger.info("Polygon client initialized")
        
        # OANDA Forex
        if settings.OANDA_API_KEY and settings.OANDA_ACCOUNT_ID:
            self.oanda_access_token = settings.OANDA_API_KEY
            self.oanda_account_id = settings.OANDA_ACCOUNT_ID
            self.oanda_api = API(access_token=self.oanda_access_token, 
                               environment='practice' if settings.OANDA_ENV == 'practice' else 'live')
            logger.info("OANDA client initialized")
        
        # Binance/CCXT (Crypto/Commodities Futures)
        if settings.BINANCE_API_KEY:
            self.binance_client = ccxt.binance({
                'apiKey': settings.BINANCE_API_KEY,
                'secret': settings.BINANCE_SECRET,
                'sandbox': settings.BINANCE_SANDBOX or False,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            await self.binance_client.load_markets()
            logger.info("Binance client initialized")
        
        self._initialized = True
        
    async def close(self):
        '''Cleanup clients'''
        if self.session:
            await self.session.close()
        if self.binance_client:
            await self.binance_client.close()
        logger.info("Market API service closed")
    
    # =========================================================================
    # QUOTES (Latest bid/ask/last)
    # =========================================================================
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        '''Get latest quote for any symbol across providers'''
        providers = []
        
        # Try Polygon first (stocks/commodities)
        if self.polygon_client and symbol in ['AAPL', 'GC', 'CL']:  
            try:
                quote = self.polygon_client.get_last_quote(symbol)
                providers.append({
                    'provider': 'polygon',
                    'bid': float(quote.bid),
                    'ask': float(quote.ask),
                    'last': float(quote.last),
                    'size': quote.size,
                    'timestamp': quote.participant_timestamp
                })
            except Exception as e:
                logger.debug(f"Polygon quote {symbol} failed: {e}")
        
        # Forex → OANDA
        if 'USD' in symbol and self.oanda_api:
            try:
                params = {'instruments': symbol.replace('/', '_')}
                r = pricing_http.PricingInfo(self.oanda_account_id, params)
                oanda_api.request(r)
                price = r.response['prices'][0]
                providers.append({
                    'provider': 'oanda',
                    'bid': float(price['bids'][0]['price']),
                    'ask': float(price['asks'][0]['price']), 
                    'last': (float(price['bids'][0]['price']) + float(price['asks'][0]['price'])) / 2,
                    'timestamp': price['time']
                })
            except Exception as e:
                logger.debug(f"OANDA quote {symbol} failed: {e}")
        
        # Crypto/Futures → Binance
        if self.binance_client:
            try:
                ticker = await self.binance_client.fetch_ticker(symbol)
                providers.append({
                    'provider': 'binance', 
                    'bid': float(ticker['bid']),
                    'ask': float(ticker['ask']),
                    'last': float(ticker['last']),
                    'timestamp': ticker['timestamp']
                })
            except Exception as e:
                logger.debug(f"Binance quote {symbol} failed: {e}")
        
        # Return best/most recent
        if providers:
            best = max(providers, key=lambda x: x['timestamp'])
            return best
        return None
    
    # =========================================================================
    # TICK STREAM (Realtime quotes)
    # =========================================================================  
    async def stream_ticks(self, symbols: List[str]) -> AsyncGenerator[Dict, None]:
        '''Realtime tick stream - yields dicts for ClickHouse insert'''
        # Polygon WebSocket for stocks/commodities  
        if self.polygon_client and any(s in ['AAPL', 'GC'] for s in symbols):
            async for message in self._polygon_stream(symbols):
                yield message
                
        # OANDA streaming pricing
        if self.oanda_api and any('/' in s for s in symbols):
            async for message in self._oanda_stream(symbols):
                yield message
        
        # Binance WebSocket
        if self.binance_client:
            async for message in self._binance_stream(symbols):
                yield message
    
    async def _polygon_stream(self, symbols: List[str]):
        '''Polygon WebSocket tick stream'''
        ws = WebSocketClient(api_key=settings.POLYGON_API_KEY, market='stocks', 
                           feed='realtime', symbols=symbols)
        async with ws as stream:
            async for message in stream:
                tick = {
                    'timestamp': datetime.fromtimestamp(message['endtimestamp'] / 1000),
                    'symbol': message['sym'],
                    'bid': message.get('b', 0),
                    'ask': message.get('a', 0), 
                    'volume': message.get('z', 0),
                    'bid_size': message.get('S', 0),  # fixme
                    'ask_size': message.get('s', 0)
                }
                yield tick
    
    async def _oanda_stream(self, symbols: List[str]):
        '''OANDA pricing stream'''
        # OANDA streaming implementation
        pass  # TODO: implement streaming
    
    async def _binance_stream(self, symbols: List[str]):
        '''Binance WebSocket ticker stream'''
        # Multi-symbol WebSocket
        pass  # TODO: implement
    
    # =========================================================================
    # BARS (OHLCV)
    # =========================================================================
    async def get_bars(self, symbol: str, timeframe: str = 'minute', 
                      from_ts: datetime = None, to_ts: datetime = None, 
                      limit: int = 1000) -> List[Dict]:
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

