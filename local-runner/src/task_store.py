"""Thread-safe in-memory store for task states."""

import asyncio

from src.models import TaskState


class TaskStore:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskState] = {}
        self._lock = asyncio.Lock()

    async def get(self, task_id: str) -> TaskState | None:
        async with self._lock:
            return self._tasks.get(task_id)

    async def set(self, task: TaskState) -> None:
        async with self._lock:
            self._tasks[task.id] = task

    async def update(self, task_id: str, **kwargs: object) -> TaskState | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            updated = task.model_copy(update=kwargs)
            self._tasks[task_id] = updated
            return updated


store = TaskStore()
