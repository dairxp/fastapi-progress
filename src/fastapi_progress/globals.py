from .state.base import StateBackend
from .state.memory import MemoryBackend

_active_backend: StateBackend = MemoryBackend()

def set_backend(backend: StateBackend) -> None:
    global _active_backend
    _active_backend = backend

def get_backend() -> StateBackend:
    return _active_backend
