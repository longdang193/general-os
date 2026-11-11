"""Restartable recovery derived from durable state and current Git facts."""

from __future__ import annotations

from general_os.git import GitSnapshot
from general_os.state import CoordinationState, Task


class RecoveryError(RuntimeError):
    """Raised when current repository facts make restart unsafe."""


def next_unfinished_task(
    state: CoordinationState,
    snapshot: GitSnapshot,
) -> Task | None:
    if snapshot.conflicts:
        paths = ", ".join(snapshot.conflicts)
        raise RecoveryError(f"Git conflict prevents safe recovery: {paths}")

    completed = {task.id for task in state.tasks if task.state == "completed"}
    for task in state.tasks:
        if task.state in {"completed", "blocked"}:
            continue
        if all(dependency in completed for dependency in task.depends_on):
            return task
    return None
