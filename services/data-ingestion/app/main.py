"""
Financial Intelligence Platform - Data Ingestion Service

Real-time data ingestion pipeline for:
- Market data (stocks, forex, commodities)
- Macroeconomic data
- Shipping and supply chain data
- News and sentiment data
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.services.kafka_service import kafka_manager
from app.services.redis_service import redis_manager

logger = get_logger(__name__)


class DataIngestionService:
    """
    Main data ingestion service class.
    
    Manages data sources, ingestion pipelines, and data publishing.
    """
    
    def __init__(self):
        self.running = False
        self.data_sources: Dict[str, Any] = {}
        self.ingestion_tasks: List[asyncio.Task] = []
    
    async def start(self) -> None:
        """
        Start the data ingestion service.
        """
        logger.info("Starting Data Ingestion Service...")
        
        # Connect to infrastructure
        await redis_manager.connect()
        await kafka_manager.connect()
        
        # Create topics if needed
        await kafka_manager.create_topics([
            "market.data",
            "market.quotes",
            "news.articles",
            "macro.data",
            "shipping.data",
            "analytics.results"
        ])
        
        self.running = True
        
        # Start ingestion tasks
        self.ingestion_tasks = [
            asyncio.create_task(self.ingest_market_data()),
            asyncio.create_task(self.ingest_macro_data()),
            asyncio.create_task(self.ingest_shipping_data()),
            asyncio.create_task(self.ingest_news_data()),
            asyncio.create_task(self.heartbeat_loop()),
        ]
        
        logger.info(f"Started {len(self.ingestion_tasks)} ingestion tasks")
        
        # Wait for all tasks
        await asyncio.gather(*self.ingestion_tasks)
    
    async def stop(self) -> None:
        """
        Stop the data ingestion service.
        """
        logger.info("Stopping Data Ingestion Service...")
        
        self.running = False
        
        # Cancel all tasks
        for task in self.ingestion_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.ingestion_tasks, return_exceptions=True)
        
        # Disconnect from infrastructure
        await kafka_manager.disconnect()
        await redis_manager.disconnect()
        
        logger.info("Data Ingestion Service stopped")
    
    async def ingest_market_data(self) -> None:
        """
        Ingest real-time market data.
        
        Simulates market data ingestion from exchanges.
        """
        import random
        
        logger.info("Starting market data ingestion...")
        
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM"]
        
        while self.running:
            try:
                for symbol in symbols:
                    # Generate mock market data
                    data = {
                        "symbol": symbol,
                        "price": round(100 + random.random() * 400, 2),
                        "volume": int(random.randint(1000000, 10000000)),
                        "bid": round(150 + random.random() * 100, 2),
                        "ask": round(150 + random.random() * 100, 2),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Publish to Kafka
                    await kafka_manager.send_market_data(symbol, data)
                    
                    # Cache in Redis
                    await redis_manager.setex(
                        f"quote:{symbol}",
                        1,  # 1 second cache
                        data
                    )
                
                # Sleep before next iteration
                await asyncio.sleep(1)  # Ingest every second
                
            except Exception as e:
                logger.error(f"Error in market data ingestion: {e}")
                await asyncio.sleep(5)  # Back off on error
    
    async def ingest_macro_data(self) -> None:
        """
        Ingest macroeconomic data.
        
        Simulates macro data ingestion from government sources.
        """
        import random
        
        logger.info("Starting macro data ingestion...")
        
        indicators = [
            {"code": "GDP", "name": "GDP Growth", "frequency": "quarterly"},
            {"code": "CPI", "name": "Consumer Price Index", "frequency": "monthly"},
            {"code": "NFP", "name": "Non-Farm Payrolls", "frequency": "monthly"},
            {"code": "FEDRATE", "name": "Federal Funds Rate", "frequency": "daily"},
        ]
        
        while self.running:
            try:
                for indicator in indicators:
                    data = {
                        "indicator_code": indicator["code"],
                        "indicator_name": indicator["name"],
                        "value": round(2 + random.uniform(-1, 2), 2),
                        "previous_value": round(2 + random.uniform(-1, 2), 2),
                        "forecast": round(2 + random.uniform(-1, 1), 2),
                        "frequency": indicator["frequency"],
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Publish to Kafka
                    await kafka_manager.send(
                        topic="macro.data",
                        value=data,
                        key=indicator["code"]
                    )
                
                # Sleep for longer interval (hourly for demo)
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in macro data ingestion: {e}")
                await asyncio.sleep(60)
    
    async def ingest_shipping_data(self) -> None:
        """
        Ingest shipping and supply chain data.
        
        Simulates shipping data ingestion from port authorities.
        """
        import random
        
        logger.info("Starting shipping data ingestion...")
        
        routes = [
            {"code": "SHA-LAX", "origin": "Shanghai", "destination": "Los Angeles"},
            {"code": "SIN-ROT", "origin": "Singapore", "destination": "Rotterdam"},
            {"code": "BUS-LA", "origin": "Busan", "destination": "Los Angeles"},
        ]
        
        ports = [
            {"code": "CNSGH", "name": "Shanghai"},
            {"code": "SGSIN", "name": "Singapore"},
            {"code": "USLAX", "name": "Los Angeles"},
            {"code": "NLROT", "name": "Rotterdam"},
        ]
        
        while self.running:
            try:
                # Ingest freight rates
                for route in routes:
                    data = {
                        "type": "freight_rate",
                        "route_code": route["code"],
                        "origin": route["origin"],
                        "destination": route["destination"],
                        "spot_rate": round(1000 + random.random() * 2000, 2),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await kafka_manager.send(
                        topic="shipping.data",
                        value=data,
                        key=route["code"]
                    )
                
                # Ingest port activity
                for port in ports:
                    data = {
                        "type": "port_activity",
                        "port_code": port["code"],
                        "port_name": port["name"],
                        "vessels_in_port": random.randint(20, 80),
                        "avg_wait_time": round(random.uniform(1, 48), 1),
                        "utilization": round(random.uniform(60, 100), 1),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    await kafka_manager.send(
                        topic="shipping.data",
                        value=data,
                        key=port["code"]
                    )
                
                # Sleep (6 hours for demo)
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Error in shipping data ingestion: {e}")
                await asyncio.sleep(300)
    
    async def ingest_news_data(self) -> None:
        """
        Ingest news data.
        
        Simulates news ingestion from various sources.
        """
        import random
        
        logger.info("Starting news data ingestion...")
        
        sources = ["Reuters", "Bloomberg", "CNBC", "WSJ", "Financial Times"]
        categories = ["Markets", "Economy", "Technology", "Earnings", "M&A"]
        
        while self.running:
            try:
                # Generate mock news article
                article = {
                    "id": f"article_{datetime.utcnow().timestamp()}",
                    "title": f"Market Update: {random.choice(categories)} sector sees movement",
                    "summary": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "source": random.choice(sources),
                    "categories": random.sample(categories, k=random.randint(1, 3)),
                    "sentiment": random.choice(["positive", "neutral", "negative"]),
                    "mentioned_tickers": random.sample(
                        ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM"],
                        k=random.randint(1, 4)
                    ),
                    "published_at": datetime.utcnow().isoformat()
                }
                
                await kafka_manager.send_news(article)
                
                # Sleep (15 minutes for demo)
                await asyncio.sleep(900)
                
            except Exception as e:
                logger.error(f"Error in news data ingestion: {e}")
                await asyncio.sleep(60)
    
    async def heartbeat_loop(self) -> None:
        """
        Send periodic heartbeats.
        """
        while self.running:
            try:
                await kafka_manager.send_heartbeat("data-ingestion-service")
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                logger.error(f"Error in heartbeat: {e}")
                await asyncio.sleep(10)


async def main():
    """
    Main entry point for the data ingestion service.
    """
    configure_logging()
    logger.info("=" * 50)
    logger.info("Financial Intelligence Platform - Data Ingestion Service")
    logger.info("=" * 50)
    
    service = DataIngestionService()
    
    try:
        await service.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())

