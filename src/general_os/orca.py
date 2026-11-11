"""Thin optional Orca boundary for independently managed work."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


@dataclass(frozen=True)
class OrcaRequest:
    task_id: str
    prompt: str
    workspace: str
    profile: str


@dataclass(frozen=True)
class OrcaObservation:
    status: str
    worker_id: str | None = None
    message: str = ""


class OrcaTransport(Protocol):
    def dispatch(self, request: OrcaRequest) -> Mapping[str, Any]: ...

    def inspect(self, worker_id: str) -> Mapping[str, Any]: ...

    def cancel(self, worker_id: str) -> Mapping[str, Any]: ...


class OrcaClient:
    def __init__(
        self,
        transport: OrcaTransport | None = None,
        *,
        enabled: bool = False,
    ):
        self.transport = transport
        self.enabled = enabled

    def dispatch(self, request: OrcaRequest) -> OrcaObservation:
        if not self.enabled or self.transport is None:
            return OrcaObservation(
                "unavailable", message="Orca transport unavailable or disabled"
            )
        try:
            raw = self.transport.dispatch(request)
        except Exception as exc:
            return OrcaObservation("failed", message=f"Orca dispatch failed: {exc}")
        return self._map(raw, default_status="running")

    def inspect(self, worker_id: str) -> OrcaObservation:
        if not self.enabled or self.transport is None:
            return OrcaObservation(
                "unavailable",
                worker_id=worker_id,
                message="Orca transport unavailable or disabled",
            )
        try:
            raw = self.transport.inspect(worker_id)
        except Exception as exc:
            return OrcaObservation(
                "failed", worker_id=worker_id, message=f"Orca inspect failed: {exc}"
            )
        return self._map(raw, default_status="unknown", fallback_id=worker_id)

    def cancel(self, worker_id: str) -> OrcaObservation:
        if not self.enabled or self.transport is None:
            return OrcaObservation(
                "unavailable",
                worker_id=worker_id,
                message="Orca transport unavailable or disabled",
            )
        try:
            raw = self.transport.cancel(worker_id)
        except Exception as exc:
            return OrcaObservation(
                "failed", worker_id=worker_id, message=f"Orca cancel failed: {exc}"
            )
        return self._map(raw, default_status="cancelled", fallback_id=worker_id)

    @staticmethod
    def _map(
        raw: Mapping[str, Any],
        *,
        default_status: str,
        fallback_id: str | None = None,
    ) -> OrcaObservation:
        if not isinstance(raw, Mapping):
            return OrcaObservation("failed", message="Orca response was not an object")
        worker_id = raw.get("id", raw.get("worker_id", fallback_id))
        if worker_id is None:
            return OrcaObservation("failed", message="Orca response lacked a worker id")
        status = raw.get("status", default_status)
        message = raw.get("message", "")
        return OrcaObservation(str(status), str(worker_id), str(message))
