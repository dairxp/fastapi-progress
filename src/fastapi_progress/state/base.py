from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any

class StateBackend(ABC):
    @abstractmethod
    async def update(self, task_id: str, progress: int, message: str = "", metadata: dict[str, Any] | None = None) -> None:
        pass

    @abstractmethod
    async def get(self, task_id: str) -> dict[str, Any] | None:
        pass

    @abstractmethod
    async def subscribe(self, task_id: str) -> AsyncGenerator[dict[str, Any], None]:
        pass
