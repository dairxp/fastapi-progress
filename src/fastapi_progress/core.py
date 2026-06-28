from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from .globals import set_backend, get_backend
from .state.base import StateBackend

def init_progress(app: FastAPI, backend: StateBackend | None = None, prefix: str = "/ws/progress") -> None:
    """
    Injects the progress tracking WebSocket route into the FastAPI app.
    
    Args:
        app: The FastAPI application instance.
        backend: Optional StateBackend. Defaults to MemoryBackend.
        prefix: URL prefix for the WebSocket route. Defaults to "/ws/progress".
    """
    if backend:
        set_backend(backend)

    @app.websocket(f"{prefix}/{{task_id}}")
    async def progress_websocket(websocket: WebSocket, task_id: str) -> None:
        await websocket.accept()
        state_backend = get_backend()
        
        try:
            async for data in state_backend.subscribe(task_id):
                await websocket.send_json(data)
                if data.get("progress") == 100 or data.get("message", "").startswith("Error:"):
                    break
        except WebSocketDisconnect:
            pass
        except Exception:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass
