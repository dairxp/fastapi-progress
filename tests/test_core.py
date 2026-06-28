import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_progress import init_progress, track_progress, progress

app = FastAPI()
init_progress(app)

@track_progress(task_id_param="task_id")
async def dummy_task(task_id: str):
    await progress.update(50, "Working")
    return "OK"

@app.post("/test/{task_id}")
async def run_task(task_id: str):
    # Running synchronously for testing
    await dummy_task(task_id=task_id)
    return {"status": "started"}

client = TestClient(app)

def test_websocket_progress():
    # 1. Run the task
    response = client.post("/test/task-999")
    assert response.status_code == 200
    
    # 2. Check websocket. Since the task is done, the MemoryBackend should yield 
    # the last known state (100% Task completed from the decorator).
    with client.websocket_connect("/ws/progress/task-999") as websocket:
        data = websocket.receive_json()
        assert data["progress"] == 100
        assert data["message"] == "Task completed"
