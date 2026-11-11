"""Dispatch seams owned by the selected native runtime."""

from __future__ import annotations

from dataclasses import dataclass

from general_os.codex import CodexClient, CodexObservation, CodexRequest
from general_os.orca import OrcaClient, OrcaObservation, OrcaRequest


@dataclass(frozen=True)
class CodexDispatchRequest:
    task_id: str
    prompt: str
    workspace: str
    profile: str
    native_subagents_enabled: bool


def dispatch_codex(
    client: CodexClient,
    request: CodexDispatchRequest,
) -> CodexObservation:
    return client.run(
        CodexRequest(
            task_id=request.task_id,
            prompt=request.prompt,
            workspace=request.workspace,
            profile=request.profile,
            native_subagents_enabled=request.native_subagents_enabled,
        )
    )


@dataclass(frozen=True)
class OrcaDispatchRequest:
    task_id: str
    prompt: str
    workspace: str
    profile: str


def dispatch_orca(
    client: OrcaClient,
    request: OrcaDispatchRequest,
) -> OrcaObservation:
    return client.dispatch(
        OrcaRequest(
            task_id=request.task_id,
            prompt=request.prompt,
            workspace=request.workspace,
            profile=request.profile,
        )
    )
