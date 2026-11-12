"""The single durable coordination state object."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


TASK_STATES = frozenset({"pending", "active", "blocked", "completed"})
BLOCKER_CATEGORIES = frozenset({"authority", "dependency", "git", "external"})
POLICY_EXCEPTION_KEYS = frozenset(
    {"remote_side_effects", "scope", "provenance", "expires_at"}
)
SIDE_EFFECT_POLICIES = frozenset({"ask", "allow", "deny"})
STATE_VERSION = 1


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
    objective: str | None = None
    state: str = "pending"
    depends_on: tuple[str, ...] = ()
    acceptance: tuple[str, ...] = ()
    profile: str | None = None
    requires_independent_boundary: bool = False
    blocker_category: str | None = None
    blocker_reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.id, str) or not self.id.strip():
            raise StateError("task id must be a non-empty string")
        if self.objective is not None and (
            not isinstance(self.objective, str) or not self.objective.strip()
        ):
            raise StateError("objective must be a non-empty string when provided")
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
        if self.state == "blocked":
            if self.blocker_category not in BLOCKER_CATEGORIES:
                raise StateError("blocked tasks require a valid blocker category")
            if (
                not isinstance(self.blocker_reason, str)
                or not self.blocker_reason.strip()
            ):
                raise StateError("blocked tasks require a non-empty blocker reason")
        elif self.blocker_category is not None or self.blocker_reason is not None:
            raise StateError("only blocked tasks may carry blocker data")
        object.__setattr__(self, "depends_on", depends_on)
        object.__setattr__(self, "acceptance", acceptance)

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Task":
        allowed = {
            "id",
            "objective",
            "state",
            "depends_on",
            "acceptance",
            "profile",
            "requires_independent_boundary",
            "blocker_category",
            "blocker_reason",
        }
        unknown = set(value) - allowed
        if unknown:
            raise StateError(f"unknown task field: {sorted(unknown)[0]}")
        return cls(
            id=value.get("id", ""),
            objective=value.get("objective"),
            state=value.get("state", "pending"),
            depends_on=value.get("depends_on", ()),
            acceptance=value.get("acceptance", ()),
            profile=value.get("profile"),
            requires_independent_boundary=value.get(
                "requires_independent_boundary", False
            ),
            blocker_category=value.get("blocker_category"),
            blocker_reason=value.get("blocker_reason"),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "state": self.state,
            "depends_on": list(self.depends_on),
            "acceptance": list(self.acceptance),
        }
        if self.objective is not None:
            result["objective"] = self.objective
        if self.profile is not None:
            result["profile"] = self.profile
        if self.requires_independent_boundary:
            result["requires_independent_boundary"] = True
        if self.blocker_category is not None:
            result["blocker_category"] = self.blocker_category
            result["blocker_reason"] = self.blocker_reason
        return result


@dataclass(frozen=True)
class CoordinationState:
    goal: str
    tasks: tuple[Task, ...] = ()
    policy_exceptions: dict[str, str] = field(default_factory=dict)
    version: int = STATE_VERSION
    _source_digest: str | None = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.goal, str) or not self.goal.strip():
            raise StateError("goal must be a non-empty string")
        if self.version != STATE_VERSION:
            raise StateError(f"unsupported state version: {self.version}")
        tasks = tuple(self.tasks)
        task_ids = [task.id for task in tasks]
        if len(set(task_ids)) != len(task_ids):
            raise StateError("duplicate task id")
        exceptions = dict(self.policy_exceptions)
        unknown = set(exceptions) - POLICY_EXCEPTION_KEYS
        if unknown:
            raise StateError(f"unknown policy exception: {sorted(unknown)[0]}")
        for key, value in exceptions.items():
            if not isinstance(value, str) or not value.strip():
                raise StateError(
                    f"policy exception values must be non-empty strings: {key}"
                )
        if exceptions.get("remote_side_effects") == "allow":
            missing = {"scope", "provenance", "expires_at"} - set(exceptions)
            if missing:
                raise StateError(
                    "allow policy exception requires scope, provenance, and expiry"
                )
            try:
                expiry = datetime.fromisoformat(
                    exceptions["expires_at"].replace("Z", "+00:00")
                )
            except ValueError as exc:
                raise StateError("policy exception expiry must be ISO-8601") from exc
            if expiry.tzinfo is None or expiry.astimezone(timezone.utc) <= datetime.now(timezone.utc):
                raise StateError("policy exception expiry must be in the future")
        elif any(key in exceptions for key in ("scope", "provenance", "expires_at")):
            raise StateError("policy metadata requires remote_side_effects=allow")
        if (
            "remote_side_effects" in exceptions
            and exceptions["remote_side_effects"] not in SIDE_EFFECT_POLICIES
        ):
            raise StateError(
                f"invalid policy value for remote_side_effects: {exceptions['remote_side_effects']}"
            )
        object.__setattr__(self, "tasks", tasks)
        object.__setattr__(self, "policy_exceptions", exceptions)
        self.validate()

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "CoordinationState":
        allowed = {"version", "goal", "tasks", "policy_exceptions"}
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
        version = value.get("version", STATE_VERSION)
        if version != STATE_VERSION:
            raise StateError(f"unsupported state version: {version}")
        return cls(
            goal=value.get("goal", ""),
            tasks=tuple(Task.from_dict(task) for task in raw_tasks),
            policy_exceptions=dict(exceptions),
            version=version,
        )

    def validate(self) -> None:
        tasks_by_id = {task.id: task for task in self.tasks}
        for task in self.tasks:
            for dependency in task.depends_on:
                if dependency not in tasks_by_id:
                    raise StateError(
                        f"unknown dependency {dependency} for task {task.id}"
                    )
            if task.state == "completed":
                incomplete = [
                    dependency
                    for dependency in task.depends_on
                    if tasks_by_id[dependency].state != "completed"
                ]
                if incomplete:
                    raise StateError(
                        f"completed task has incomplete dependencies: {task.id}"
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
            "version": self.version,
            "goal": self.goal,
            "tasks": [task.to_dict() for task in self.tasks],
        }
        if self.policy_exceptions:
            result["policy_exceptions"] = dict(self.policy_exceptions)
        return result


def load_state(path: str | os.PathLike[str]) -> CoordinationState:
    state_path = Path(path)
    try:
        source = state_path.read_bytes()
        raw = json.loads(source)
    except FileNotFoundError as exc:
        raise StateError(f"state file not found: {state_path}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"invalid JSON state: {state_path}") from exc
    if not isinstance(raw, Mapping):
        raise StateError("state root must be an object")
    state = CoordinationState.from_dict(raw)
    object.__setattr__(state, "_source_digest", _digest(source))
    return state


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


@contextmanager
def _state_lock(destination: Path):
    lock_name = hashlib.sha256(str(destination.resolve()).encode("utf-8")).hexdigest()
    lock_path = Path(tempfile.gettempdir()) / f"general-os-state-{lock_name}.lock"
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def save_state(path: str | os.PathLike[str], state: CoordinationState) -> None:
    state.validate()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with _state_lock(destination):
        current = destination.read_bytes() if destination.exists() else None
        expected = state._source_digest
        if expected is None and current is not None:
            raise StateError("existing state requires loaded source provenance")
        if expected is not None and _digest(current or b"") != expected:
            raise StateError("state changed since it was loaded")
        serialized = (json.dumps(state.to_dict(), indent=2) + "\n").encode("utf-8")
        temporary_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=destination.parent,
                prefix=f".{destination.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary_path = handle.name
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, destination)
            temporary_path = None
            object.__setattr__(state, "_source_digest", _digest(serialized))
        finally:
            if temporary_path:
                try:
                    os.unlink(temporary_path)
                except FileNotFoundError:
                    pass
