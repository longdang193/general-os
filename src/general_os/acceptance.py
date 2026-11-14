"""Current-fact verification and durable task transitions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from general_os.git import GitSnapshot
from general_os.state import BLOCKER_CATEGORIES, CoordinationState

SUPPORTED_INDEPENDENT_BOUNDARIES = frozenset({"orca"})
_VERIFIER_TOKEN = object()
_DECISION_TOKEN = object()


@dataclass(frozen=True)
class BoundaryEvidence:
    kind: str
    snapshot_identity: str
    evidence: str
    task_id: str | None = None

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value.strip() for value in (self.kind, self.snapshot_identity, self.evidence)):
            raise ValueError("boundary evidence requires kind, snapshot identity, and evidence")
        if self.task_id is not None and (
            not isinstance(self.task_id, str) or not self.task_id.strip()
        ):
            raise ValueError("boundary evidence task id must be non-empty when provided")


@dataclass(frozen=True)
class VerificationResult:
    status: str
    passed: tuple[str, ...] = ()
    evidence_revision: str | None = None
    message: str = ""
    task_id: str | None = None
    snapshot_identity: str | None = None
    task_contract_identity: str | None = None
    boundary_evidence: BoundaryEvidence | None = None
    blocker_category: str | None = None
    blocker_reason: str | None = None
    _verifier_token: object | None = field(default=None, repr=False, compare=False)

    @classmethod
    def _from_verifier(cls, **values) -> "VerificationResult":
        return cls(**values, _verifier_token=_VERIFIER_TOKEN)


def create_verification_result(
    task,
    snapshot: GitSnapshot,
    *,
    passed: tuple[str, ...] = (),
    boundary_evidence: BoundaryEvidence | None = None,
) -> VerificationResult:
    """Create trusted evidence from a task and current Git observation."""

    return VerificationResult._from_verifier(
        status="pass",
        passed=tuple(passed),
        evidence_revision=snapshot.revision,
        task_id=task.id,
        snapshot_identity=snapshot.identity,
        task_contract_identity=task.contract_identity(),
        boundary_evidence=boundary_evidence,
    )


@dataclass(frozen=True)
class AcceptanceDecision:
    status: str
    reason: str
    blocker_category: str | None = None
    blocker_reason: str | None = None
    accepted_snapshot_identity: str | None = None
    accepted_task_contract_identity: str | None = None
    task_id: str | None = field(default=None, compare=False, repr=False)
    _decision_token: object | None = field(default=None, compare=False, repr=False)


def evaluate_acceptance(
    task,
    snapshot: GitSnapshot,
    verification: VerificationResult,
) -> AcceptanceDecision:
    if snapshot.conflicts:
        return AcceptanceDecision(
            "BLOCKED",
            "Git conflict prevents acceptance",
            "git",
            "Git conflict prevents acceptance",
        )
    if (
        verification.evidence_revision is not None
        and verification.evidence_revision != snapshot.revision
    ):
        return AcceptanceDecision("FAIL", "verification evidence is stale")
    if verification.status == "blocked":
        return AcceptanceDecision(
            "BLOCKED",
            verification.message or verification.blocker_reason or "verification blocked",
            verification.blocker_category,
            verification.blocker_reason or verification.message,
        )
    if verification.status == "fail":
        return AcceptanceDecision("FAIL", verification.message or "verification failed")
    if verification.status != "pass":
        return AcceptanceDecision("FAIL", "verification result is unknown")
    if verification._verifier_token is not _VERIFIER_TOKEN:
        return AcceptanceDecision("FAIL", "verification result is not verifier-produced")
    if verification.task_id != task.id:
        return AcceptanceDecision("FAIL", "verification result is bound to another task")
    if verification.task_contract_identity != task.contract_identity():
        return AcceptanceDecision("FAIL", "task contract evidence is missing or stale")
    if snapshot.identity is None:
        return AcceptanceDecision("FAIL", "verification worktree identity is missing")
    if verification.snapshot_identity != snapshot.identity:
        return AcceptanceDecision("FAIL", "verification worktree evidence is missing or stale")
    missing = set(task.acceptance) - set(verification.passed)
    if missing:
        return AcceptanceDecision(
            "FAIL", f"required proof is missing: {', '.join(sorted(missing))}"
        )
    if task.requires_independent_boundary:
        boundary = verification.boundary_evidence
        if (
            boundary is None
            or boundary.kind not in SUPPORTED_INDEPENDENT_BOUNDARIES
            or boundary.snapshot_identity != snapshot.identity
            or boundary.task_id != task.id
        ):
            return AcceptanceDecision("FAIL", "required independent boundary evidence is missing or stale")
    return AcceptanceDecision(
        "PASS",
        "required proof is current",
        accepted_snapshot_identity=snapshot.identity,
        accepted_task_contract_identity=task.contract_identity(),
        task_id=task.id,
        _decision_token=_DECISION_TOKEN,
    )


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
                    replace(
                        task,
                        state="pending",
                        blocker_category=None,
                        blocker_reason=None,
                    )
                    if task.id == task_id
                    else task
                    for task in state.tasks
                ),
            )
        return state
    if decision.status == "BLOCKED":
        if decision.blocker_category not in BLOCKER_CATEGORIES:
            raise ValueError("BLOCKED requires a valid blocker category")
        if not isinstance(decision.blocker_reason, str) or not decision.blocker_reason.strip():
            raise ValueError("BLOCKED requires a non-empty blocker reason")
    new_state = "completed" if decision.status == "PASS" else "blocked"
    if decision.status == "PASS":
        if decision.task_id != task_id or decision._decision_token is not _DECISION_TOKEN:
            raise ValueError("PASS requires verifier-produced task-bound evidence")
        if not decision.accepted_snapshot_identity:
            raise ValueError("PASS requires verifier snapshot identity")
        if not decision.accepted_task_contract_identity:
            raise ValueError("PASS requires verifier task contract identity")
        if decision.accepted_task_contract_identity != target.contract_identity():
            raise ValueError("PASS requires current task contract evidence")
        incomplete = [dependency for dependency in target.depends_on if next(task for task in state.tasks if task.id == dependency).state != "completed"]
        if incomplete:
            raise ValueError(f"task dependencies are incomplete: {', '.join(incomplete)}")
    if target.state == new_state and (
        decision.status != "BLOCKED"
        or (
            target.blocker_category == decision.blocker_category
            and target.blocker_reason == decision.blocker_reason
        )
    ) and (
        decision.status != "PASS"
        or target.accepted_snapshot_identity == decision.accepted_snapshot_identity
        and target.accepted_task_contract_identity == decision.accepted_task_contract_identity
    ):
        return state
    updated = replace(
        target,
        state=new_state,
        accepted_snapshot_identity=(
            decision.accepted_snapshot_identity if new_state == "completed" else None
        ),
        accepted_task_contract_identity=(
            decision.accepted_task_contract_identity if new_state == "completed" else None
        ),
        blocker_category=decision.blocker_category if new_state == "blocked" else None,
        blocker_reason=decision.blocker_reason if new_state == "blocked" else None,
    )
    tasks = tuple(updated if task.id == task_id else task for task in state.tasks)
    return replace(state, tasks=tasks)


def completed_tasks_requiring_reverification(
    state: CoordinationState,
    snapshot: GitSnapshot,
) -> tuple[str, ...]:
    """Signal completed tasks for targeted re-verification when Git evidence differs."""

    return tuple(
        task.id
        for task in state.tasks
        if task.state == "completed"
        and (
            snapshot.identity is None
            or task.accepted_snapshot_identity != snapshot.identity
        )
    )


def revalidate_completed_tasks(
    state: CoordinationState,
    snapshot: GitSnapshot,
) -> CoordinationState:
    """Revalidate durable task semantics after any needed fresh Git verification."""
    stale: set[str] = set()
    for task in state.tasks:
        if task.state == "completed" and (
            task.accepted_task_contract_identity != task.contract_identity()
        ):
            stale.add(task.id)

    changed = True
    while changed:
        changed = False
        for task in state.tasks:
            if (
                task.state == "completed"
                and task.id not in stale
                and any(dependency in stale for dependency in task.depends_on)
            ):
                stale.add(task.id)
                changed = True

    if not stale:
        return state
    return replace(
        state,
        tasks=tuple(
            replace(
                task,
                state="pending",
                accepted_snapshot_identity=None,
                accepted_task_contract_identity=None,
                blocker_category=None,
                blocker_reason=None,
            )
            if task.id in stale
            else task
            for task in state.tasks
        ),
    )
