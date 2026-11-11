"""Thin native Codex app-server boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class CodexRequest:
    task_id: str
    prompt: str
    workspace: str
    profile: str
    native_subagents_enabled: bool


@dataclass(frozen=True)
class CodexObservation:
    status: str
    runtime_id: str | None = None
    message: str = ""


class CodexTransport(Protocol):
    def start(self, request: CodexRequest) -> Mapping[str, Any]: ...

    def inspect(self, runtime_id: str) -> Mapping[str, Any]: ...

    def cancel(self, runtime_id: str) -> Mapping[str, Any]: ...


class CodexClient:
    def __init__(self, transport: CodexTransport | None = None):
        self.transport = transport

    def run(self, request: CodexRequest) -> CodexObservation:
        if self.transport is None:
            return CodexObservation("unavailable", message="Codex transport unavailable")
        try:
            raw = self.transport.start(request)
        except Exception as exc:
            return CodexObservation("failed", message=f"Codex start failed: {exc}")
        return self._map(raw, default_status="running")

    def inspect(self, runtime_id: str) -> CodexObservation:
        if self.transport is None:
            return CodexObservation(
                "unavailable",
                runtime_id=runtime_id,
                message="Codex transport unavailable",
            )
        try:
            raw = self.transport.inspect(runtime_id)
        except Exception as exc:
            return CodexObservation(
                "failed", runtime_id=runtime_id, message=f"Codex inspect failed: {exc}"
            )
        return self._map(raw, default_status="unknown", fallback_id=runtime_id)

    def cancel(self, runtime_id: str) -> CodexObservation:
        if self.transport is None:
            return CodexObservation(
                "unavailable",
                runtime_id=runtime_id,
                message="Codex transport unavailable",
            )
        try:
            raw = self.transport.cancel(runtime_id)
        except Exception as exc:
            return CodexObservation(
                "failed", runtime_id=runtime_id, message=f"Codex cancel failed: {exc}"
            )
        return self._map(raw, default_status="cancelled", fallback_id=runtime_id)

    @staticmethod
    def _map(
        raw: Mapping[str, Any],
        *,
        default_status: str,
        fallback_id: str | None = None,
    ) -> CodexObservation:
        if not isinstance(raw, Mapping):
            return CodexObservation("failed", message="Codex response was not an object")
        runtime_id = raw.get("id", raw.get("runtime_id", fallback_id))
        if runtime_id is None:
            return CodexObservation("failed", message="Codex response lacked a runtime id")
        status = raw.get("status", default_status)
        message = raw.get("message", "")
        return CodexObservation(str(status), str(runtime_id), str(message))
