"""Thread-safe in-memory store for task states with TTL-based eviction."""

import asyncio
from collections import OrderedDict

from src.models import TaskState

MAX_TASKS = 1000
EVICT_BATCH = 100


class TaskStore:
    def __init__(self) -> None:
        self._tasks: OrderedDict[str, TaskState] = OrderedDict()
        self._lock = asyncio.Lock()

    async def get(self, task_id: str) -> TaskState | None:
        async with self._lock:
            return self._tasks.get(task_id)

    async def set(self, task: TaskState) -> None:
        async with self._lock:
            self._tasks[task.id] = task
            if len(self._tasks) > MAX_TASKS:
                # Evict oldest finished/failed tasks first
                to_remove: list[str] = []
                for tid, t in self._tasks.items():
                    if t.status in ("finished", "failed"):
                        to_remove.append(tid)
                    if len(to_remove) >= EVICT_BATCH:
                        break
                # If not enough terminal tasks, evict oldest regardless
                if not to_remove:
                    to_remove = list(self._tasks.keys())[:EVICT_BATCH]
                for tid in to_remove:
                    del self._tasks[tid]

    async def update(self, task_id: str, **kwargs: object) -> TaskState | None:
        async with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return None
            updated = task.model_copy(update=kwargs)
            self._tasks[task_id] = updated
            return updated


store = TaskStore()
