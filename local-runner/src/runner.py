"""Executes browser-use Agent tasks in the background."""

import json
import logging
from datetime import datetime, timezone

from browser_use import Agent, Browser

from src.config import settings
from src.llm_factory import create_llm
from src.models import TaskState
from src.task_store import store

logger = logging.getLogger(__name__)


async def execute_task(task_state: TaskState) -> None:
    """Run a browser-use agent for the given task. Updates store in-place."""
    await store.update(task_state.id, status="running")

    browser = Browser(headless=settings.browser_headless, viewport={"width": 1280, "height": 800})

    try:
        print("TESTANDO SEM VISION")
        llm = create_llm()
        agent = Agent(
            task=task_state.task_prompt,
            llm=llm,
            browser=browser,
            max_actions_per_step=5,
            llm_timeout=300,
            step_timeout=300,
            llm_screenshot_size=(1280, 800),
        )

        result = await agent.run(max_steps=settings.max_agent_steps)

        # Extract the final output from the agent result
        output = _extract_output(result)

        await store.update(
            task_state.id,
            status="finished",
            output=output,
            finished_at=datetime.now(timezone.utc),
        )
    except Exception:
        logger.exception("Task %s failed", task_state.id)
        # Return structured error so QAUse can parse it
        error_output = json.dumps(
            {
                "status": "failing",
                "steps": [],
                "error": "Local runner encountered an internal error during execution.",
            }
        )
        await store.update(
            task_state.id,
            status="failed",
            output=error_output,
            finished_at=datetime.now(timezone.utc),
        )
    finally:
        await browser.close()


def _extract_output(result: object) -> str:
    """Pull the final text output from a browser-use AgentHistoryList result."""
    # browser-use Agent.run() returns an AgentHistoryList
    # The final_result() method returns the last extracted content
    final = result.final_result()  # type: ignore[union-attr]
    if final is not None:
        return final if isinstance(final, str) else json.dumps(final)

    # Fallback: return a failing response
    return json.dumps(
        {
            "status": "failing",
            "steps": [],
            "error": "Agent completed but produced no output.",
        }
    )
