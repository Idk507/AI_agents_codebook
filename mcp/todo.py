
from __future__ import annotations

import itertools
from typing import Iterable

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("todo-mcp")


_TASKS: dict[int, str] = {}
_COUNTER = itertools.count(1)


def _format_tasks(tasks: Iterable[tuple[int, str]]) -> list[str]:
    return [f"#{task_id}: {description}" for task_id, description in tasks]


@mcp.tool()
def list_tasks() -> list[str]:
    """Return the tasks currently on the list."""

    return _format_tasks(sorted(_TASKS.items()))


@mcp.tool()
def add_task(description: str) -> str:
    """Store a task and return its identifier."""

    task_id = next(_COUNTER)
    _TASKS[task_id] = description
    return f"Added task #{task_id}: {description}"


@mcp.tool()
def complete_task(task_id: int) -> str:
    """Remove a task by ID."""

    description = _TASKS.pop(task_id, None)
    if description is None:
        return f"Task #{task_id} was not found."
    return f"Completed task #{task_id}: {description}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
