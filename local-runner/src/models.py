"""Pydantic models matching the BrowserUse Cloud API response shapes exactly."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel


class RunTaskRequestBody(BaseModel):
    """Matches the Cloud API RunTaskRequest. Only fields QAUse actually sends."""

    task: str
    highlight_elements: bool = True
    enable_public_share: bool = False
    save_browser_data: bool = False
    llm_model: str | None = None
    use_adblock: bool | None = None
    use_proxy: bool | None = None
    max_agent_steps: int = 75
    structured_output_json: str | None = None


class TaskCreatedResponse(BaseModel):
    """POST /api/v1/run-task response."""

    id: str


class TaskStepResponse(BaseModel):
    """Individual step in the task response."""

    id: str
    step: int
    evaluation_previous_goal: str
    next_goal: str
    url: str


class TaskResponse(BaseModel):
    """GET /api/v1/task/{task_id} response. Matches Cloud API TaskResponse."""

    id: str
    task: str
    live_url: str | None = None
    output: str | None = None
    status: Literal["created", "running", "finished", "stopped", "paused", "failed"]
    created_at: datetime
    finished_at: datetime | None = None
    steps: list[TaskStepResponse] = []
    browser_data: None = None
    user_uploaded_files: list[str] | None = None
    output_files: list[str] | None = None
    public_share_url: str | None = None


class TaskState(BaseModel):
    """Internal state for an in-flight task."""

    id: str
    task_prompt: str
    status: Literal["created", "running", "finished", "failed"]
    output: str | None = None
    created_at: datetime
    finished_at: datetime | None = None
    steps: list[TaskStepResponse] = []

    def to_response(self) -> TaskResponse:
        return TaskResponse(
            id=self.id,
            task=self.task_prompt,
            output=self.output,
            status=self.status,
            created_at=self.created_at,
            finished_at=self.finished_at,
            steps=self.steps,
        )

    @staticmethod
    def new(task_id: str, task_prompt: str) -> "TaskState":
        return TaskState(
            id=task_id,
            task_prompt=task_prompt,
            status="created",
            created_at=datetime.now(timezone.utc),
        )
