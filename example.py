import asyncio
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import uuid

from fastapi_progress import init_progress, track_progress, progress

app = FastAPI()

# 1. Initialize the library (auto-injects /ws/progress/{task_id})
init_progress(app)

# 2. Decorate a function
@track_progress(task_id_param="task_id")
async def heavy_work(task_id: str):
    # Do some work and update progress
    await progress.update(10, "Starting work...")
    await asyncio.sleep(1)
    
    await progress.update(50, "Processing data...")
    await asyncio.sleep(2)
    
    await progress.update(90, "Wrapping up...")
    await asyncio.sleep(1)

@app.post("/do-work")
async def start_work(tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks.add_task(heavy_work, task_id=task_id)
    return {"task_id": task_id}

@app.get("/")
async def get_html():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>FastAPI Progress Test</title>
        </head>
        <body>
            <h1>FastAPI Progress Tracker</h1>
            <button onclick="startTask()">Start Task</button>
            
            <div style="margin-top: 20px;">
                <progress id="progressBar" value="0" max="100" style="width: 300px; display: none;"></progress>
                <div id="status" style="margin-top: 10px; font-family: monospace;"></div>
            </div>
            
            <script>
                async function startTask() {
                    document.getElementById('progressBar').style.display = 'block';
                    document.getElementById('progressBar').value = 0;
                    document.getElementById('status').innerText = 'Starting...';
                    
                    const res = await fetch('/do-work', { method: 'POST' });
                    const data = await res.json();
                    const taskId = data.task_id;
                    
                    const ws = new WebSocket(`ws://${location.host}/ws/progress/${taskId}`);
                    
                    ws.onmessage = function(event) {
                        const state = JSON.parse(event.data);
                        document.getElementById('progressBar').value = state.progress;
                        document.getElementById('status').innerText = `[${state.progress}%] ${state.message}`;
                    };
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(html)
