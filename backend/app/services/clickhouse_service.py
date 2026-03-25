'''ClickHouse Time Series Database Service
High-performance async client for:
- Tick ingestion (100k+/sec)
- OHLCV queries
- AI feature engineering
- Real-time analytics'''

import asyncio
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

from clickhouse_connect import get_client
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class ClickHouseService:
    def __init__(self):
        self.client = None
        self._connected = False
        
    @asynccontextmanager
    async def session(self):
        '''Async context manager for high-throughput operations'''
        async with get_client(host=settings.CLICKHOUSE_HOST or 'localhost',
                            port=8123, username='intel_user',
                            password='SecurePass2024!', 
                            database='financial_intel') as conn:
            yield conn
    
    async def connect(self):
        '''Health check connection'''
        async with self.session() as conn:
            version = await conn.command('SELECT version()')
            logger.info(f"ClickHouse connected: {version}")
            self._connected = True
    
    async def insert_ticks_batch(self, ticks: List[Dict]) -> int:
        '''Bulk insert ticks - optimized for 100k+/sec'''
        if not ticks:
            return 0
            
        async with self.session() as conn:
            result = await conn.insert_df('market_ticks', self._df_from_ticks(ticks),
                                        column_types={
                                            'timestamp': 'DateTime64(3)',
                                            'symbol': 'LowCardinality(String)',
                                            'bid': 'Float64', 'ask': 'Float64',
                                            'mid': 'Float64', 'volume': 'UInt64'
                                        })
            logger.debug(f"Inserted {result} ticks")
            return result
    
    async def stream_ticks_insert(self, tick_stream: AsyncGenerator[Dict, None]) -> None:
        '''High-throughput streaming insert from API websockets'''
        buffer = []
        buffer_size = 10000  # 10k tick batch
        
        try:
            async for tick in tick_stream:
                buffer.append(tick)
                if len(buffer) >= buffer_size:
                    await self.insert_ticks_batch(buffer)
                    buffer.clear()
                    logger.info(f"Streamed {buffer_size} ticks")
            
            # Final batch
            if buffer:
                await self.insert_ticks_batch(buffer)
                
        except Exception as e:
            logger.error(f"Tick stream insert failed: {e}")
    
    async def get_latest_quote(self, symbol: str) -> Optional[Dict]:
        '''Get latest quote from TSDB'''
        query = '''
        SELECT symbol, argMax(bid, timestamp) as bid, 
               argMax(ask, timestamp) as ask,
               argMax(mid, timestamp) as last_price,
               argMax(volume, timestamp) as volume
        FROM market_ticks 
        WHERE symbol = %s 
        PREWHERE timestamp > now() - INTERVAL 1 DAY
        '''
        async with self.session() as conn:
            result = await conn.query_df(query, [symbol])
            return result.iloc[0].to_dict() if len(result) > 0 else None
    
    async def get_ohlcv(self, symbol: str, timeframe: str = '1m', 
                       limit: int = 1000) -> List[Dict]:
        '''Get OHLCV bars from materialized views'''
        table = f'market_ohlcv_{timeframe.replace("m", "")}'
        query = f'''
        SELECT timestamp, open, high, low, close, volume
        FROM {table}
        WHERE symbol = %s
        ORDER BY timestamp DESC
        LIMIT %s
        '''
        async with self.session() as conn:
            result = await conn.query_df(query, [symbol, limit])
            return result.to_dict('records')
    
    async def get_signals(self, symbol: str, limit: int = 50) -> List[Dict]:
        '''Latest AI trading signals'''
        query = '''
        SELECT * FROM ai_signals 
        WHERE symbol = %s
        ORDER BY timestamp DESC LIMIT %s
        '''
        async with self.session() as conn:
            result = await conn.query_df(query, [symbol, limit])
            return result.to_dict('records')
    
    # AI/ML Features
    async def get_features(self, symbol: str, window_hours: int = 24) -> Dict:
        '''Engineering features for ML models'''
        # RSI, volume profile, volatility, etc.
        features_query = '''
        WITH stats AS (
            SELECT 
                arrayReduce('groupBitOr', sign(diff)) as momentum,
                quantileExact(0.95)(mid) - quantileExact(0.05)(mid) as true_range,
                stddevPop(mid) as volatility,
                sum(volume) as total_volume
            FROM market_ticks 
            WHERE symbol = %s AND timestamp > now() - INTERVAL %s HOUR
        )
        SELECT * FROM stats
        '''
        async with self.session() as conn:
            result = await conn.query_df(features_query, [symbol, window_hours])
            return result.iloc[0].to_dict()
    
    def _df_from_ticks(self, ticks: List[Dict]) -> 'pd.DataFrame':
        '''Convert tick dicts to optimized pandas DF'''
        import pandas as pd
        df = pd.DataFrame(ticks)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

# Global singleton  
clickhouse_service = ClickHouseService()

__all__ = ['clickhouse_service']

