'''NSE Realtime AI Analysis Service
Integrates ClickHouse ticks for ML signals/anomalies.
'''

from typing import List, Dict
import numpy as np
from app.services.clickhouse_service import clickhouse_service
from app.services.nse_symbols import NSE_SYMBOLS

class NSEAI:
    @staticmethod
    async def rsi(symbol: str, period: int = 14) -> float:
        '''Calculate RSI from recent ticks'''
        bars = await clickhouse_service.get_ohlcv(symbol, '1m', limit=period+1)
        if len(bars) < period:
            return 50.0
        deltas = np.diff([b['close'] for b in bars])
        gain = np.mean(deltas[deltas > 0])
        loss = -np.mean(deltas[deltas < 0])
        rs = gain / loss if loss else 100
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    async def volume_anomaly(symbol: str) -> Dict:
        '''Detect volume spike'''
        ticks = await clickhouse_service.get_latest_quote(symbol)
        if not ticks:
            return {"anomaly": False}
        avg_vol = await clickhouse_service.get_features(symbol)['avg_volume_20']
        anomaly = ticks['volume'] > avg_vol * 2
        return {"symbol": symbol, "anomaly": anomaly, "score": ticks['volume'] / avg_vol if avg_vol else 1}
    
    @staticmethod
    async def generate_signal(symbol: str) -> Dict:
        rsi_val = await NSEAI.rsi(symbol)
        vol = await NSEAI.volume_anomaly(symbol)
        if rsi_val < 30 and vol['anomaly']:
            signal = "STRONG BUY"
        elif rsi_val > 70:
            signal = "STRONG SELL"
        else:
            signal = "HOLD"
        return {"symbol": symbol, "signal": signal, "rsi": rsi_val, "volume_anomaly": vol['anomaly']}

ai_nse = NSEAI()

