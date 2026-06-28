import asyncio
from typing import AsyncGenerator, Any
from .base import StateBackend

class MemoryBackend(StateBackend):
    def __init__(self):
        self._state: dict[str, dict[str, Any]] = {}
        self._subscriptions: dict[str, list[asyncio.Queue]] = {}

    async def update(self, task_id: str, progress: int, message: str = "", metadata: dict[str, Any] | None = None) -> None:
        data = {
            "task_id": task_id,
            "progress": progress,
            "message": message,
            "metadata": metadata or {}
        }
        self._state[task_id] = data
        
        if task_id in self._subscriptions:
            for queue in self._subscriptions[task_id]:
                await queue.put(data)

    async def get(self, task_id: str) -> dict[str, Any] | None:
        return self._state.get(task_id)

    async def subscribe(self, task_id: str) -> AsyncGenerator[dict[str, Any], None]:
        queue = asyncio.Queue()
        if task_id not in self._subscriptions:
            self._subscriptions[task_id] = []
        self._subscriptions[task_id].append(queue)
        
        try:
            current = await self.get(task_id)
            if current:
                yield current
                
            while True:
                data = await queue.get()
                yield data
        finally:
            if task_id in self._subscriptions:
                try:
                    self._subscriptions[task_id].remove(queue)
                except ValueError:
                    pass
                if not self._subscriptions[task_id]:
                    del self._subscriptions[task_id]
