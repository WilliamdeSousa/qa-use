"""FastAPI app that mirrors the BrowserUse Cloud API endpoints used by QAUse."""

import asyncio
import uuid

from fastapi import FastAPI, HTTPException

from src.models import RunTaskRequestBody, TaskCreatedResponse, TaskResponse, TaskState
from src.runner import execute_task
from src.task_store import store

app = FastAPI(title="QAUse Local Runner", version="0.1.0")


@app.get("/api/v1/ping")
async def ping() -> dict[str, str]:
    return {"status": "ok", "mode": "local"}


@app.post("/api/v1/run-task", response_model=TaskCreatedResponse)
async def run_task(body: RunTaskRequestBody) -> TaskCreatedResponse:
    task_id = str(uuid.uuid4())
    task_state = TaskState.new(task_id=task_id, task_prompt=body.task)
    await store.set(task_state)

    # Fire and forget - runs in background
    asyncio.create_task(execute_task(task_state))

    return TaskCreatedResponse(id=task_id)


@app.get("/api/v1/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    task_state = await store.get(task_id)
    print(task_state)
    if task_state is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task_state.to_response()


# Stubs for endpoints QAUse doesn't use but exist in the OpenAPI spec.
# Returning 501 so callers know local mode doesn't support these.

@app.put("/api/v1/stop-task")
async def stop_task(task_id: str) -> None:
    raise HTTPException(status_code=501, detail="stop-task not supported in local mode")


@app.put("/api/v1/pause-task")
async def pause_task(task_id: str) -> None:
    raise HTTPException(status_code=501, detail="pause-task not supported in local mode")


@app.put("/api/v1/resume-task")
async def resume_task(task_id: str) -> None:
    raise HTTPException(status_code=501, detail="resume-task not supported in local mode")


@app.get("/api/v1/me")
async def me() -> bool:
    """Always authenticated in local mode."""
    return True


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
