# fastapi-progress

A zero-config library to track the progress of FastAPI background tasks and stream it to the frontend via WebSockets in real-time.

## Features

- **Zero-config WebSockets:** Automatically injects a `/ws/progress/{task_id}` endpoint.
- **Elegant Decorator:** Use `@track_progress` on your background tasks.
- **Context-aware Updates:** Simply call `await progress.update(50, "Processing")` from anywhere in your task without passing task IDs around.
- **Hybrid State Backend:** Includes an in-memory backend for simple deployments, and a Redis backend for distributed setups (e.g., Celery, multiple Uvicorn workers).

## Installation

Using `uv` (recommended):
```bash
uv add fastapi-progress
```
Or pip:
```bash
pip install fastapi-progress
```

## Quick Start

```python
import asyncio
import uuid
from fastapi import FastAPI, BackgroundTasks
from fastapi_progress import init_progress, track_progress, progress

app = FastAPI()

# 1. Initialize to inject the websocket route
init_progress(app)

# 2. Decorate your background task
@track_progress(task_id_param="task_id")
async def heavy_work(task_id: str):
    await progress.update(10, "Starting work...")
    await asyncio.sleep(1)
    
    await progress.update(50, "Processing data...")
    await asyncio.sleep(2)
    
    await progress.update(100, "Done!")

# 3. Trigger the task
@app.post("/do-work")
async def start_work(tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks.add_task(heavy_work, task_id=task_id)
    return {"task_id": task_id}
```

## Using Redis (For Production)

If you are running multiple Gunicorn/Uvicorn workers, you must use Redis to share the state across processes.

```python
from redis.asyncio import Redis
from fastapi_progress import init_progress, RedisBackend

redis_client = Redis(host="localhost", port=6379)
backend = RedisBackend(redis_client)

init_progress(app, backend=backend)
```
