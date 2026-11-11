"""The single durable coordination state object."""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


TASK_STATES = frozenset({"pending", "active", "blocked", "completed"})
POLICY_EXCEPTION_KEYS = frozenset({"remote_side_effects"})
SIDE_EFFECT_POLICIES = frozenset({"ask", "allow", "deny"})


class StateError(ValueError):
    """Raised when durable coordination state is invalid."""


def _tuple_of_strings(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise StateError(f"{field_name} must be a list of non-empty strings")
    return tuple(value)


@dataclass(frozen=True)
class Task:
    id: str
    state: str = "pending"
    depends_on: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()
    profile: str | None = None
    requires_independent_boundary: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise StateError("task id must be a non-empty string")
        if self.state not in TASK_STATES:
            raise StateError(f"invalid task state: {self.state}")
        depends_on = _tuple_of_strings(self.depends_on, "depends_on")
        acceptance = _tuple_of_strings(self.acceptance, "acceptance")
        if len(set(depends_on)) != len(depends_on):
            raise StateError(f"duplicate dependency in task: {self.id}")
        if self.id in depends_on:
            raise StateError(f"task cannot depend on itself: {self.id}")
        if self.profile is not None and (
            not isinstance(self.profile, str) or not self.profile
        ):
            raise StateError("profile must be a non-empty string when provided")
        if not isinstance(self.requires_independent_boundary, bool):
            raise StateError("requires_independent_boundary must be boolean")
        object.__setattr__(self, "depends_on", depends_on)
        object.__setattr__(self, "acceptance", acceptance)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Task":
        allowed = {
            "id",
            "state",
            "depends_on",
            "acceptance",
            "profile",
            "requires_independent_boundary",
        }
        unknown = set(value) - allowed
        if unknown:
            raise StateError(f"unknown task field: {sorted(unknown)[0]}")
        return cls(
            id=value.get("id", ""),
            state=value.get("state", "pending"),
            depends_on=value.get("depends_on", ()),
            acceptance=value.get("acceptance", ()),
            profile=value.get("profile"),
            requires_independent_boundary=value.get(
                "requires_independent_boundary", False
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "state": self.state,
            "depends_on": list(self.depends_on),
            "acceptance": list(self.acceptance),
        }
        if self.profile is not None:
            result["profile"] = self.profile
        if self.requires_independent_boundary:
            result["requires_independent_boundary"] = True
        return result


@dataclass(frozen=True)
class CoordinationState:
    goal: str
    tasks: tuple[Task, ...] = ()
    policy_exceptions: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise StateError("goal must be a non-empty string")
        tasks = tuple(self.tasks)
        task_ids = [task.id for task in tasks]
        if len(set(task_ids)) != len(task_ids):
            raise StateError("duplicate task id")
        exceptions = dict(self.policy_exceptions)
        unknown = set(exceptions) - POLICY_EXCEPTION_KEYS
        if unknown:
            raise StateError(f"unknown policy exception: {sorted(unknown)[0]}")
        for key, value in exceptions.items():
            if value not in SIDE_EFFECT_POLICIES:
                raise StateError(f"invalid policy value for {key}: {value}")
        object.__setattr__(self, "tasks", tasks)
        object.__setattr__(self, "policy_exceptions", exceptions)
        self.validate()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CoordinationState":
        allowed = {"goal", "tasks", "policy_exceptions"}
        unknown = set(value) - allowed
        if unknown:
            raise StateError(f"unknown state field: {sorted(unknown)[0]}")
        raw_tasks = value.get("tasks", ())
        if not isinstance(raw_tasks, list):
            raise StateError("tasks must be a list")
        if not all(isinstance(task, Mapping) for task in raw_tasks):
            raise StateError("each task must be an object")
        exceptions = value.get("policy_exceptions", {})
        if not isinstance(exceptions, Mapping):
            raise StateError("policy_exceptions must be an object")
        return cls(
            goal=value.get("goal", ""),
            tasks=tuple(Task.from_dict(task) for task in raw_tasks),
            policy_exceptions=dict(exceptions),
        )

    def validate(self) -> None:
        tasks_by_id = {task.id: task for task in self.tasks}
        for task in self.tasks:
            for dependency in task.depends_on:
                if dependency not in tasks_by_id:
                    raise StateError(
                        f"unknown dependency {dependency} for task {task.id}"
                    )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> None:
            if task_id in visiting:
                raise StateError("cyclic dependency")
            if task_id in visited:
                return
            visiting.add(task_id)
            for dependency in tasks_by_id[task_id].depends_on:
                visit(dependency)
            visiting.remove(task_id)
            visited.add(task_id)

        for task_id in tasks_by_id:
            visit(task_id)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }
        if self.policy_exceptions:
            result["policy_exceptions"] = dict(self.policy_exceptions)
        return result


def load_state(path: str | os.PathLike[str]) -> CoordinationState:
    state_path = Path(path)
    try:
        raw = json.loads(state_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise StateError(f"state file not found: {state_path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"invalid JSON state: {state_path}") from exc
    if not isinstance(raw, Mapping):
        raise StateError("state root must be an object")
    return CoordinationState.from_dict(raw)


def save_state(path: str | os.PathLike[str], state: CoordinationState) -> None:
    state.validate()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = handle.name
            json.dump(state.to_dict(), handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    finally:
        if temporary_path:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
