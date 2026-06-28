import json
from typing import AsyncGenerator, Any
from .base import StateBackend

try:
    from redis.asyncio import Redis
except ImportError:
    Redis = Any

class RedisBackend(StateBackend):
    def __init__(self, redis_client: 'Redis', prefix: str = "fastapi_progress"):
        self.redis = redis_client
        self.prefix = prefix

    def _key(self, task_id: str) -> str:
        return f"{self.prefix}:state:{task_id}"

    def _channel(self, task_id: str) -> str:
        return f"{self.prefix}:channel:{task_id}"

    async def update(self, task_id: str, progress: int, message: str = "", metadata: dict[str, Any] | None = None) -> None:
        data = {
            "task_id": task_id,
            "progress": progress,
            "message": message,
            "metadata": metadata or {}
        }
        payload = json.dumps(data)
        
        await self.redis.setex(self._key(task_id), 86400, payload)
        await self.redis.publish(self._channel(task_id), payload)

    async def get(self, task_id: str) -> dict[str, Any] | None:
        payload = await self.redis.get(self._key(task_id))
        if payload:
            return json.loads(payload)
        return None

    async def subscribe(self, task_id: str) -> AsyncGenerator[dict[str, Any], None]:
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self._channel(task_id))
        
        try:
            current = await self.get(task_id)
            if current:
                yield current
                
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield data
        finally:
            await pubsub.unsubscribe(self._channel(task_id))
            await pubsub.close()
