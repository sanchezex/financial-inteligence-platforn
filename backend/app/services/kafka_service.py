"""
Financial Intelligence Platform - Kafka Service

Kafka connection management and streaming operations.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class KafkaManager:
    """
    Kafka connection and streaming manager.
    
    Provides methods for:
    - Topic management
    - Producer operations
    - Consumer operations
    - Message serialization
    """
    
    def __init__(self):
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self._connected = False
        self._topics = set()
    
    @property
    def connected(self) -> bool:
        """Check if connected to Kafka."""
        return self._connected
    
    async def connect(self) -> None:
        """
        Establish connection to Kafka.
        """
        try:
            logger.info("Connecting to Kafka...")
            
            # Create producer
            self.producer = AIOKafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                max_batch_size=16384,
                linger_ms=10
            )
            
            await self.producer.start()
            logger.info("Kafka producer connected")
            
            # Create consumer (will be configured when starting)
            self.consumer = AIOKafkaConsumer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                auto_offset_reset='latest',
                enable_auto_commit=True,
                max_poll_records=500
            )
            
            self._connected = True
            logger.info("Kafka connection established successfully")
            
        except KafkaConnectionError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            self._connected = False
            raise
    
    async def disconnect(self) -> None:
        """
        Close Kafka connection.
        """
        try:
            if self.producer:
                await self.producer.stop()
                logger.info("Kafka producer stopped")
            
            if self.consumer:
                await self.consumer.stop()
                logger.info("Kafka consumer stopped")
            
            self._connected = False
            logger.info("Kafka connections closed")
            
        except Exception as e:
            logger.error(f"Error closing Kafka connections: {e}")
    
async def create_topics(self, topics: List[str], num_partitions: int = 6, replication_factor: int = 1) -> None:
        """
        Create Kafka topics for realtime trading.
        
        Args:
            topics: List of topic names to create
            num_partitions: Number of partitions (6 for forex/commodities)
            replication_factor: Replication factor
        """
        from aiokafka.admin import AIOKafkaAdminClient, NewTopic
        
        # Realtime trading topics (high-throughput)
        realtime_topics = topics + [
            # Forex majors
            'market.forex.eurusd', 'market.forex.gbpusd', 'market.forex.usdjpy',
            'market.forex.audusd', 'market.forex.usdcad', 'market.forex.nzdusd',
            # Commodities
            'market.commodities.xauusd', 'market.commodities.xagusd', 
            'market.commodities.cl', 'market.commodities.gc',
            'market.commodities.si', 'market.commodities.ng',
            # AI Signals
            'ai.trading.signals', 'ai.risk.alerts',
            # Order flow
            'trading.orders', 'trading.executions'
        ]
        
        try:
            admin = AIOKafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
            )
            
            await admin.start()
            
            new_topics = [NewTopic(name=t, num_partitions=num_partitions, replication_factor=replication_factor) 
                         for t in realtime_topics]
            
            await admin.create_topics(new_topics)
            logger.info(f"Created realtime topics: {realtime_topics}")
            
            await admin.close()
            
        except Exception as e:
            if 'TopicAlreadyExistsError' not in str(e):
                logger.error(f"Error creating realtime topics: {e}")
                raise
    
    async def delete_topics(self, topics: List[str]) -> None:
        """
        Delete Kafka topics.
        
        Args:
            topics: List of topic names to delete
        """
        from aiokafka.admin import AIOKafkaAdminClient
        
        try:
            admin = AIOKafkaAdminClient(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
            )
            
            await admin.start()
            await admin.delete_topics(topics)
            logger.info(f"Deleted topics: {topics}")
            
            await admin.close()
            
        except Exception as e:
            logger.error(f"Error deleting topics {topics}: {e}")
            raise
    
    # =========================================================================
    # Producer Operations
    # =========================================================================
    
    async def send(
        self,
        topic: str,
        value: Dict[str, Any],
        key: Optional[str] = None,
        partition: Optional[int] = None,
        timestamp_ms: Optional[int] = None
    ) -> None:
        """
        Send message to Kafka topic.
        
        Args:
            topic: Topic name
            value: Message value (dict will be JSON serialized)
            key: Optional message key for partitioning
            partition: Optional partition number
            timestamp_ms: Optional timestamp in milliseconds
        """
        if not self._connected or not self.producer:
            raise RuntimeError("Kafka producer not connected")
        
        try:
            await self.producer.send(
                topic=topic,
                value=value,
                key=key,
                partition=partition,
                timestamp_ms=timestamp_ms
            )
            
            logger.debug(f"Sent message to topic {topic}, key={key}")
            
        except Exception as e:
            logger.error(f"Error sending message to topic {topic}: {e}")
            raise
    
    async def send_market_data(
        self,
        symbol: str,
        data: Dict[str, Any],
        source: str = "internal"
    ) -> None:
        """
        Send market data to Kafka.
        
        Args:
            symbol: Asset symbol
            data: Market data dict
            source: Data source identifier
        """
        message = {
            "type": "market_data",
            "symbol": symbol,
            "source": source,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send(topic=f"market.{symbol.lower()}", value=message, key=symbol)
    
    async def send_news(self, article: Dict[str, Any]) -> None:
        """
        Send news article to Kafka.
        
        Args:
            article: News article dict
        """
        message = {
            "type": "news",
            "data": article,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send(topic="news.articles", value=message, key=article.get("id"))
    
    async def send_alert(self, alert: Dict[str, Any]) -> None:
        """
        Send alert notification to Kafka.
        
        Args:
            alert: Alert dict
        """
        message = {
            "type": "alert",
            "data": alert,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send(topic="alerts.notifications", value=message, key=alert.get("id"))
    
    async def send_heartbeat(self, service_name: str) -> None:
        """
        Send service heartbeat to Kafka.
        
        Args:
            service_name: Name of the service
        """
        message = {
            "type": "heartbeat",
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send(topic="system.heartbeats", value=message, key=service_name)
    
    async def flush(self, timeout: float = 10.0) -> None:
        """
        Flush pending messages.
        
        Args:
            timeout: Timeout in seconds
        """
        if self.producer:
            await self.producer.flush(timeout=timeout)
    
    # =========================================================================
    # Consumer Operations
    # =========================================================================
    
    async def subscribe(self, topics: List[str]) -> None:
        """
        Subscribe to Kafka topics.
        
        Args:
            topics: List of topic names to subscribe to
        """
        if not self._connected or not self.consumer:
            raise RuntimeError("Kafka consumer not connected")
        
        try:
            await self.consumer.subscribe(topics=topics)
            self._topics.update(topics)
            logger.info(f"Subscribed to topics: {topics}")
            
        except Exception as e:
            logger.error(f"Error subscribing to topics {topics}: {e}")
            raise
    
    async def unsubscribe(self) -> None:
        """
        Unsubscribe from all topics.
        """
        if self.consumer:
            await self.consumer.unsubscribe()
            self._topics.clear()
            logger.info("Unsubscribed from all topics")
    
    async def get_messages(
        self,
        timeout_ms: int = 1000,
        max_records: int = 100
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Get messages from subscribed topics.
        
        Args:
            timeout_ms: Timeout in milliseconds
            max_records: Maximum number of records to return
        
        Yields:
            Message dict with topic, partition, offset, key, value
        """
        if not self._connected or not self.consumer:
            raise RuntimeError("Kafka consumer not connected")
        
        try:
            messages = await self.consumer.getmany(
                timeout_ms=timeout_ms,
                max_records=max_records
            )
            
            for topic_partition, msgs in messages.items():
                for msg in msgs:
                    yield {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key.decode('utf-8') if msg.key else None,
                        "value": msg.value,
                        "timestamp": msg.timestamp
                    }
                    
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            raise
    
    async def consume(
        self,
        topics: List[str],
        handler: Callable[[Dict[str, Any]], None],
        error_handler: Optional[Callable[[Exception], None]] = None
    ) -> None:
        """
        Consume messages with a handler function.
        
        Args:
            topics: List of topics to subscribe to
            handler: Async function to process each message
            error_handler: Optional function to handle errors
        """
        await self.subscribe(topics)
        
        try:
            async for message in self.get_messages():
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    if error_handler:
                        await error_handler(e)
                        
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
            raise
    
    async def start_consumer(
        self,
        topics: List[str],
        group_id: str,
        handler: Callable[[Dict[str, Any]], None]
    ) -> None:
        """
        Start a consumer in a consumer group.
        
        Args:
            topics: Topics to consume
            group_id: Consumer group ID
            handler: Message handler function
        """
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=group_id,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            max_poll_records=500
        )
        
        await consumer.start()
        
        try:
            logger.info(f"Starting consumer for topics {topics} with group {group_id}")
            
            async for msg in consumer:
                try:
                    message = {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "key": msg.key.decode('utf-8') if msg.key else None,
                        "value": msg.value,
                        "timestamp": msg.timestamp
                    }
                    
                    await handler(message)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Consumer cancelled")
        finally:
            await consumer.stop()
    
    # =========================================================================
    # Topic Configuration
    # =========================================================================
    
    # Default topic names
    TOPICS = {
        "market_data": "market.data",
        "quotes": "market.quotes",
        "news": "news.articles",
        "alerts": "alerts.notifications",
        "analytics": "analytics.results",
        "heartbeats": "system.heartbeats",
        "logs": "system.logs",
        "metrics": "system.metrics"
    }
    
    def get_topic_name(self, topic_key: str) -> str:
        """
        Get topic name from predefined topics.
        
        Args:
            topic_key: Key from TOPICS dict
        
        Returns:
            Full topic name
        """
        return self.TOPICS.get(topic_key, topic_key)


# Global Kafka manager instance
kafka_manager = KafkaManager()


# ============================================================================
# Kafka Message Types
# ============================================================================

class MarketDataMessage:
    """Market data message factory."""
    
    @staticmethod
    def create(
        symbol: str,
        price: float,
        volume: int,
        bid: Optional[float] = None,
        ask: Optional[float] = None,
        source: str = "internal"
    ) -> Dict[str, Any]:
        """
        Create market data message.
        
        Args:
            symbol: Asset symbol
            price: Current price
            volume: Trading volume
            bid: Bid price
            ask: Ask price
            source: Data source
        
        Returns:
            Market data message dict
        """
        return {
            "type": "market_data",
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "bid": bid,
            "ask": ask,
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def create_quote(
        symbol: str,
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        source: str = "internal"
    ) -> Dict[str, Any]:
        """
        Create quote message.
        
        Args:
            symbol: Asset symbol
            open_price: Opening price
            high: High price
            low: Low price
            close: Closing/last price
            volume: Trading volume
            source: Data source
        
        Returns:
            Quote message dict
        """
        spread = ask - bid if bid and ask else 0
        
        return {
            "type": "quote",
            "symbol": symbol,
            "data": {
                "open": open_price,
                "high": high,
                "low": low,
                "close": close,
                "volume": volume,
                "spread": spread
            },
            "source": source,
            "timestamp": datetime.utcnow().isoformat()
        }


class NewsMessage:
    """News message factory."""
    
    @staticmethod
    def create(
        article_id: str,
        title: str,
        summary: str,
        source: str,
        categories: List[str],
        sentiment: Optional[str] = None,
        sentiment_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Create news message.
        
        Args:
            article_id: Unique article ID
            title: Article title
            summary: Article summary
            source: News source
            categories: Article categories
            sentiment: Sentiment label
            sentiment_score: Sentiment score (-1 to 1)
        
        Returns:
            News message dict
        """
        return {
            "type": "news",
            "id": article_id,
            "title": title,
            "summary": summary,
            "source": source,
            "categories": categories,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "timestamp": datetime.utcnow().isoformat()
        }


class AlertMessage:
    """Alert message factory."""
    
    @staticmethod
    def create(
        alert_id: str,
        alert_type: str,
        title: str,
        message: str,
        symbols: List[str],
        severity: str = "info"
    ) -> Dict[str, Any]:
        """
        Create alert message.
        
        Args:
            alert_id: Unique alert ID
            alert_type: Type of alert
            title: Alert title
            message: Alert message
            symbols: Affected symbols
            severity: Alert severity (info, warning, critical)
        
        Returns:
            Alert message dict
        """
        return {
            "type": "alert",
            "id": alert_id,
            "alert_type": alert_type,
            "title": title,
            "message": message,
            "symbols": symbols,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }

