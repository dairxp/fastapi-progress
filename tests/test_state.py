import pytest
import asyncio
from fastapi_progress.state.memory import MemoryBackend

@pytest.mark.asyncio
async def test_memory_backend():
    backend = MemoryBackend()
    
    # Update state
    await backend.update("task-123", 50, "Halfway", {"custom": 1})
    
    # Get state
    state = await backend.get("task-123")
    assert state is not None
    assert state["progress"] == 50
    assert state["message"] == "Halfway"
    assert state["metadata"]["custom"] == 1

@pytest.mark.asyncio
async def test_memory_backend_subscription():
    backend = MemoryBackend()
    
    async def subscriber():
        updates = []
        async for data in backend.subscribe("task-456"):
            updates.append(data)
            if data["progress"] == 100:
                break
        return updates

    # Start subscriber in background
    task = asyncio.create_task(subscriber())
    
    # Give subscriber time to setup
    await asyncio.sleep(0.1)
    
    await backend.update("task-456", 10, "Start")
    await backend.update("task-456", 100, "Done")
    
    updates = await task
    assert len(updates) == 2
    assert updates[0]["progress"] == 10
    assert updates[1]["progress"] == 100
