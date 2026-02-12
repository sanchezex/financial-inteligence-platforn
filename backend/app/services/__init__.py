"""
Financial Intelligence Platform - Services Package

Core services for data processing, caching, and messaging.
"""

try:
	from app.services.redis_service import redis_manager
except Exception:
	class _DummyRedisManager:
		async def connect(self):
			return None

		async def disconnect(self):
			return None

		async def ping(self):
			return False

	redis_manager = _DummyRedisManager()

try:
	from app.services.kafka_service import kafka_manager
except Exception:
	class _DummyKafkaManager:
		async def start(self):
			return None

		async def stop(self):
			return None

	kafka_manager = _DummyKafkaManager()

__all__ = ["redis_manager", "kafka_manager"]

