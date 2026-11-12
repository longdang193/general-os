"""Current-fact verification and durable task transitions."""

from __future__ import annotations

from dataclasses import dataclass, replace

from general_os.git import GitSnapshot
from general_os.state import CoordinationState


@dataclass(frozen=True)
class BoundaryEvidence:
    kind: str
    snapshot_identity: str
    evidence: str

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.kind, self.snapshot_identity, self.evidence)):
            raise ValueError("boundary evidence requires kind, snapshot identity, and evidence")


@dataclass(frozen=True)
class VerificationResult:
    status: str
    passed: tuple[str, ...] = ()
    evidence_revision: str | None = None
    message: str = ""
    snapshot_identity: str | None = None
    boundary_evidence: BoundaryEvidence | None = None


@dataclass(frozen=True)
class AcceptanceDecision:
    status: str
    reason: str


def evaluate_acceptance(
    task,
    snapshot: GitSnapshot,
    verification: VerificationResult,
) -> AcceptanceDecision:
    if snapshot.conflicts:
        return AcceptanceDecision("BLOCKED", "Git conflict prevents acceptance")
    if (
        verification.evidence_revision is not None
        and verification.evidence_revision != snapshot.revision
    ):
        return AcceptanceDecision("FAIL", "verification evidence is stale")
    if snapshot.identity is not None and verification.snapshot_identity != snapshot.identity:
        return AcceptanceDecision("FAIL", "verification worktree evidence is missing or stale")
    if verification.status == "blocked":
        return AcceptanceDecision("BLOCKED", verification.message or "verification blocked")
    if verification.status == "fail":
        return AcceptanceDecision("FAIL", verification.message or "verification failed")
    if verification.status != "pass":
        return AcceptanceDecision("FAIL", "verification result is unknown")
    missing = set(task.acceptance) - set(verification.passed)
    if missing:
        return AcceptanceDecision(
            "FAIL", f"required proof is missing: {', '.join(sorted(missing))}"
        )
    if task.requires_independent_boundary:
        boundary = verification.boundary_evidence
        if boundary is None or boundary.snapshot_identity != snapshot.identity:
            return AcceptanceDecision("FAIL", "required independent boundary evidence is missing or stale")
    return AcceptanceDecision("PASS", "required proof is current")


def apply_task_transition(
    state: CoordinationState,
    task_id: str,
    decision: AcceptanceDecision,
) -> CoordinationState:
    if decision.status not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError(f"unknown acceptance status: {decision.status}")
    target = next((task for task in state.tasks if task.id == task_id), None)
    if target is None:
        raise ValueError(f"unknown task: {task_id}")
    if decision.status == "FAIL":
        if target.state == "blocked":
            return replace(
                state,
                tasks=tuple(
                    replace(task, state="pending") if task.id == task_id else task
                    for task in state.tasks
                ),
            )
        return state
    new_state = "completed" if decision.status == "PASS" else "blocked"
    if decision.status == "PASS":
        incomplete = [dependency for dependency in target.depends_on if next(task for task in state.tasks if task.id == dependency).state != "completed"]
        if incomplete:
            raise ValueError(f"task dependencies are incomplete: {', '.join(incomplete)}")
    if target.state == new_state:
        return state
    updated = replace(target, state=new_state)
    tasks = tuple(updated if task.id == task_id else task for task in state.tasks)
    return replace(state, tasks=tasks)
