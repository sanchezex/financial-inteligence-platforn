from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
import pandas as pd
from scipy import stats
import uvicorn

app = FastAPI(title="Analytics Service", version="1.0.0")

class TimeSeriesData(BaseModel):
    values: List[float]
    timestamps: Optional[List[str]] = None

class StatisticalResult(BaseModel):
    mean: float
    std: float
    min: float
    max: float
    median: float
    count: int

class CorrelationResult(BaseModel):
    correlation: float
    p_value: float
    significant: bool

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "analytics"}

@app.get("/")
async def root():
    return {"service": "analytics", "version": "1.0.0"}

@app.post("/statistics/descriptive", response_model=StatisticalResult)
async def descriptive_statistics(data: TimeSeriesData):
    """Calculate descriptive statistics for a time series"""
    if len(data.values) == 0:
        raise HTTPException(status_code=400, detail="No data provided")
    
    arr = np.array(data.values)
    return StatisticalResult(
        mean=float(np.mean(arr)),
        std=float(np.std(arr)),
        min=float(np.min(arr)),
        max=float(np.max(arr)),
        median=float(np.median(arr)),
        count=len(arr)
    )

@app.post("/statistics/correlation", response_model=CorrelationResult)
async def correlation_analysis(data1: TimeSeriesData, data2: TimeSeriesData):
    """Calculate correlation between two time series"""
    if len(data1.values) != len(data2.values):
        raise HTTPException(status_code=400, detail="Time series must have same length")
    
    arr1 = np.array(data1.values)
    arr2 = np.array(data2.values)
    
    correlation, p_value = stats.pearsonr(arr1, arr2)
    
    return CorrelationResult(
        correlation=float(correlation),
        p_value=float(p_value),
        significant=p_value < 0.05
    )

@app.post("/statistics/zscore")
async def zscore_analysis(data: TimeSeriesData):
    """Calculate z-scores for a time series"""
    arr = np.array(data.values)
    z_scores = (arr - np.mean(arr)) / np.std(arr)
    return {"zscores": z_scores.tolist(), "mean": float(np.mean(arr)), "std": float(np.std(arr))}

@app.post("/statistics/returns")
async def calculate_returns(prices: TimeSeriesData):
    """Calculate returns from price series"""
    arr = np.array(prices.values)
    returns = np.diff(arr) / arr[:-1]
    return {"returns": returns.tolist()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

