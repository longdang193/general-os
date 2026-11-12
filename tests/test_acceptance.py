import pytest

from general_os.acceptance import (
    AcceptanceDecision,
    BoundaryEvidence,
    VerificationResult,
    apply_task_transition,
    evaluate_acceptance,
)
from general_os.git import GitSnapshot
from general_os.state import CoordinationState, Task


def snapshot(revision="abc123", identity=None):
    return GitSnapshot("main", revision, (), (), True, identity)


def test_acceptance_passes_fresh_required_proof():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", ("tests pass",), "abc123", snapshot_identity="snapshot-id"),
    )

    assert decision == AcceptanceDecision("PASS", "required proof is current")


def test_acceptance_treats_stale_proof_as_retryable_failure():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot("new-revision"),
        VerificationResult("pass", ("tests pass",), "old-revision"),
    )

    assert decision.status == "FAIL"
    assert "stale" in decision.reason


def test_acceptance_treats_missing_proof_as_retryable_failure():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", (), "abc123", snapshot_identity="snapshot-id"),
    )

    assert decision.status == "FAIL"
    assert "missing" in decision.reason


def test_acceptance_treats_unknown_verification_as_retryable_failure():
    task = Task(id="work")

    decision = evaluate_acceptance(task, snapshot(), VerificationResult("unknown"))

    assert decision.status == "FAIL"
    assert "unknown" in decision.reason


def test_acceptance_preserves_material_blocker():
    task = Task(id="work")

    decision = evaluate_acceptance(
        task,
        GitSnapshot("main", "abc123", (), ("conflict",), False),
        VerificationResult("pass"),
    )

    assert decision.status == "BLOCKED"


def test_failed_transition_leaves_task_unfinished_for_retry():
    state = CoordinationState(goal="goal", tasks=(Task(id="work", state="active"),))

    updated = apply_task_transition(
        state,
        "work",
        AcceptanceDecision("FAIL", "verification failed"),
    )

    assert updated == state


def test_acceptance_updates_only_durable_task_state_idempotently():
    state = CoordinationState(goal="goal", tasks=(Task(id="work", state="active"),))
    decision = AcceptanceDecision("PASS", "required proof is current")

    completed = apply_task_transition(state, "work", decision)
    repeated = apply_task_transition(completed, "work", decision)

    assert completed.tasks[0].state == "completed"
    assert repeated == completed


def test_acceptance_requires_matching_worktree_identity():
    task = Task(id="work")

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="other"),
    )

    assert decision.status == "FAIL"
    assert "worktree evidence" in decision.reason


def test_acceptance_requires_worktree_identity_for_pass():
    task = Task(id="work")

    decision = evaluate_acceptance(
        task,
        snapshot(),
        VerificationResult("pass"),
    )

    assert decision.status == "FAIL"
    assert "identity" in decision.reason


def test_required_boundary_needs_typed_matching_evidence():
    task = Task(id="work", requires_independent_boundary=True)
    evidence = BoundaryEvidence("orca", "snapshot-id", "worker receipt")

    assert evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="snapshot-id", boundary_evidence=evidence),
    ).status == "PASS"
    assert evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="snapshot-id"),
    ).status == "FAIL"


@pytest.mark.parametrize("kind", ("codex", "unknown"))
def test_required_boundary_rejects_unsupported_evidence(kind):
    task = Task(id="work", requires_independent_boundary=True)
    evidence = BoundaryEvidence(kind, "snapshot-id", "caller supplied")

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="snapshot-id", boundary_evidence=evidence),
    )

    assert decision.status == "FAIL"
    assert "boundary" in decision.reason


def test_pass_cannot_complete_before_dependencies():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="dependency"), Task(id="work", depends_on=("dependency",))),
    )

    with pytest.raises(ValueError, match="dependencies are incomplete"):
        apply_task_transition(state, "work", AcceptanceDecision("PASS", "ok"))


def test_failed_blocked_task_returns_to_pending():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="work", state="blocked", blocker_category="git", blocker_reason="conflict"),),
    )

    updated = apply_task_transition(
        state, "work", AcceptanceDecision("FAIL", "retryable failure")
    )

    assert updated.tasks[0].state == "pending"
    assert updated.tasks[0].blocker_category is None
    assert updated.tasks[0].blocker_reason is None


def test_blocked_transition_requires_typed_reason():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))

    with pytest.raises(ValueError, match="blocker category"):
        apply_task_transition(state, "work", AcceptanceDecision("BLOCKED", "blocked"))
