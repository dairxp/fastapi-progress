import uuid
from functools import wraps
from typing import Callable, Any, Coroutine, TypeVar, ParamSpec

from .context import current_task_id
from .globals import get_backend

P = ParamSpec("P")
R = TypeVar("R")

def track_progress(task_id_param: str | None = None) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    # Tracks background task progress
    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            task_id = None
            if task_id_param and task_id_param in kwargs:
                task_id = str(kwargs[task_id_param])
            else:
                task_id = str(uuid.uuid4())

            token = current_task_id.set(task_id)
            backend = get_backend()

            await backend.update(task_id, 0, "Task started")

            try:
                result = await func(*args, **kwargs)
                await backend.update(task_id, 100, "Task completed")
                return result
            except Exception as e:
                await backend.update(task_id, 0, f"Error: {str(e)}")
                raise e
            finally:
                current_task_id.reset(token)

        return wrapper
    return decorator
