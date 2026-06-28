from contextvars import ContextVar
from typing import Any
from .globals import get_backend

current_task_id: ContextVar[str | None] = ContextVar("current_task_id", default=None)

class Progress:
    async def update(self, progress: int, message: str = "", metadata: dict[str, Any] | None = None) -> None:
        """
        Updates the progress of the current background task.
        
        Args:
            progress: An integer representing the completion percentage (0-100).
            message: An optional status message.
            metadata: An optional dictionary for extra custom data.
        """
        task_id = current_task_id.get()
        if task_id:
            backend = get_backend()
            await backend.update(task_id, progress, message, metadata)

progress = Progress()
