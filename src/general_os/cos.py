"""Chief of Staff coordination over durable state and current observations."""

from __future__ import annotations

from dataclasses import dataclass

from general_os.codex import CodexClient, CodexObservation
from general_os.dispatch import (
    CodexDispatchRequest,
    OrcaDispatchRequest,
    dispatch_codex,
    dispatch_orca,
)
from general_os.git import GitSnapshot
from general_os.orca import OrcaClient, OrcaObservation
from general_os.policy import RuntimeConfig
from general_os.profiles import ProfileSpec, resolve_profile
from general_os.recovery import RecoveryError, next_unfinished_task
from general_os.state import CoordinationState, Task


@dataclass(frozen=True)
class CoSDecision:
    strategy: str
    task_id: str | None
    profile: str
    reason: str


class ChiefOfStaff:
    def __init__(
        self,
        *,
        state: CoordinationState,
        policy: RuntimeConfig,
        profiles: dict[str, ProfileSpec],
        codex: CodexClient,
        orca: OrcaClient,
    ):
        self.state = state
        self.policy = policy
        self.profiles = profiles
        self.codex = codex
        self.orca = orca

    def select_next_task(self, snapshot: GitSnapshot) -> Task | None:
        return next_unfinished_task(self.state, snapshot)

    def choose_strategy(self, task: Task, snapshot: GitSnapshot) -> CoSDecision:
        profile = resolve_profile(task.profile, self.profiles).name
        if snapshot.conflicts:
            return CoSDecision("blocked", task.id, profile, "Git conflict blocks execution")
        if task.requires_independent_boundary:
            if not self.policy.orca_enabled:
                return CoSDecision(
                    "blocked",
                    task.id,
                    profile,
                    "Orca is disabled for independent work",
                )
            return CoSDecision("orca", task.id, profile, "independent boundary required")
        return CoSDecision("codex", task.id, profile, "single assignment")

    def next_decision(self, snapshot: GitSnapshot) -> CoSDecision:
        if not self.state.tasks:
            if snapshot.conflicts:
                return CoSDecision(
                    "blocked", None, "normal", "Git conflict blocks goal-only execution"
                )
            return CoSDecision("codex", None, "normal", "goal-only assignment")
        try:
            task = self.select_next_task(snapshot)
        except RecoveryError as exc:
            return CoSDecision("blocked", None, "normal", str(exc))
        if task is None:
            if all(item.state == "completed" for item in self.state.tasks):
                return CoSDecision("done", None, "normal", "all declared tasks completed")
            return CoSDecision("blocked", None, "normal", "no dependency-ready task")
        return self.choose_strategy(task, snapshot)

    def dispatch_task(
        self,
        decision: CoSDecision,
        task: Task | None,
        workspace: str,
    ) -> CodexObservation | OrcaObservation:
        prompt = task.objective if task is not None and task.objective else self.state.goal
        if decision.strategy == "codex":
            return dispatch_codex(
                self.codex,
                CodexDispatchRequest(
                    task_id=task.id if task is not None else "goal-only",
                    prompt=prompt,
                    workspace=workspace,
                    profile=decision.profile,
                    native_subagents_enabled=self.policy.native_subagents_enabled,
                ),
            )
        if decision.strategy == "orca":
            return dispatch_orca(
                self.orca,
                OrcaDispatchRequest(
                    task_id=task.id,
                    prompt=prompt,
                    workspace=workspace,
                    profile=decision.profile,
                ),
            )
        raise ValueError(f"cannot dispatch strategy: {decision.strategy}")

    @staticmethod
    def reconcile_observation(observation: CodexObservation | OrcaObservation) -> str:
        return observation.status
