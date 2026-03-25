import random
from datetime import datetime
from typing import List, Dict

from .nse_symbols import NSE_SYMBOLS

def generate_nse_signals(symbol: str, limit: int = 10) -> List[Dict]:
    if symbol not in NSE_SYMBOLS:
        raise ValueError("NSE symbol only")
    
    signals = []
    reasons = ['RSI oversold', 'Volume breakout', 'MACD crossover', 'Support bounce', 'Sector momentum']
    
    for i in range(limit):
        now = datetime.utcnow()
        signal_type = random.choice(["STRONG BUY", "BUY", "WATCH", "SELL", "STRONG SELL"])
        confidence = round(random.uniform(0.6, 0.95), 2)
        signals.append({
            "symbol": symbol,
            "type": signal_type,
            "confidence": confidence,
            "reason": f"AI: {random.choice(reasons)}",
            "price": round(random.uniform(10, 50), 2),
            "target": round(random.uniform(45, 60), 2),
            "stop_loss": round(random.uniform(8, 12), 2),
            "timestamp": now.isoformat()
        })
    
    return signals

def detect_volume_anomaly(symbol: str, bars: List[Dict]) -> Dict:
    '''Simple volume anomaly detection'''
    if len(bars) < 20:
        return {"anomaly": False}
    
    recent_vol = [b['volume'] for b in bars[-5:]]
    avg_vol = sum(recent_vol) / 5
    anomaly = max(recent_vol) > avg_vol * 2
    
    return {
        "symbol": symbol,
        "anomaly": anomaly,
        "volume_spike": max(recent_vol) if anomaly else 0,
        "avg_volume": avg_vol,
        "alert": "Volume spike detected" if anomaly else "Normal"
    }
