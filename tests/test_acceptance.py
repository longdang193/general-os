import pytest

from general_os.acceptance import (
    AcceptanceDecision,
    BoundaryEvidence,
    VerificationResult,
    apply_task_transition,
    create_verification_result,
    evaluate_acceptance,
    revalidate_completed_tasks,
)
from general_os.git import GitSnapshot
from general_os.state import CoordinationState, Task


def snapshot(revision="abc123", identity=None):
    return GitSnapshot("main", revision, (), (), True, identity)


def verified(*, task=None, **values):
    if task is not None:
        values.setdefault("task_contract_identity", task.contract_identity())
    return VerificationResult._from_verifier(**values)


def test_acceptance_passes_fresh_required_proof():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        verified(
            task=task,
            status="pass",
            passed=("tests pass",),
            evidence_revision="abc123",
            task_id="work",
            snapshot_identity="snapshot-id",
        ),
    )

    assert decision == AcceptanceDecision(
        "PASS",
        "required proof is current",
        accepted_snapshot_identity="snapshot-id",
        accepted_task_contract_identity=task.contract_identity(),
    )


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
        verified(
            task=task,
            status="pass",
            task_id="work",
            evidence_revision="abc123",
            snapshot_identity="snapshot-id",
        ),
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
        verified(status="pass", task_id="work"),
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
    decision = evaluate_acceptance(
        Task(id="work"),
        snapshot(identity="snapshot-id"),
        verified(task=Task(id="work"), status="pass", task_id="work", snapshot_identity="snapshot-id"),
    )

    completed = apply_task_transition(state, "work", decision)
    repeated = apply_task_transition(completed, "work", decision)

    assert completed.tasks[0].state == "completed"
    assert completed.tasks[0].accepted_snapshot_identity == "snapshot-id"
    assert repeated == completed


def test_acceptance_requires_matching_worktree_identity():
    task = Task(id="work")

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        verified(task=task, status="pass", task_id="work", snapshot_identity="other"),
    )

    assert decision.status == "FAIL"
    assert "worktree evidence" in decision.reason


def test_acceptance_requires_worktree_identity_for_pass():
    task = Task(id="work")

    decision = evaluate_acceptance(
        task,
        snapshot(),
        verified(task=task, status="pass", task_id="work"),
    )

    assert decision.status == "FAIL"
    assert "identity" in decision.reason


def test_required_boundary_needs_typed_matching_evidence():
    task = Task(id="work", requires_independent_boundary=True)
    evidence = BoundaryEvidence("orca", "snapshot-id", "worker receipt", "work")

    assert evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        verified(
            task=task,
            status="pass",
            task_id="work",
            snapshot_identity="snapshot-id",
            boundary_evidence=evidence,
        ),
    ).status == "PASS"
    assert evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="snapshot-id"),
    ).status == "FAIL"


@pytest.mark.parametrize("kind", ("codex", "unknown"))
def test_required_boundary_rejects_unsupported_evidence(kind):
    task = Task(id="work", requires_independent_boundary=True)
    evidence = BoundaryEvidence(kind, "snapshot-id", "caller supplied", "work")

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        verified(
            task=task,
            status="pass",
            task_id="work",
            snapshot_identity="snapshot-id",
            boundary_evidence=evidence,
        ),
    )

    assert decision.status == "FAIL"
    assert "boundary" in decision.reason


def test_pass_cannot_complete_before_dependencies():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="dependency"), Task(id="work", depends_on=("dependency",))),
    )

    with pytest.raises(ValueError, match="dependencies are incomplete"):
        apply_task_transition(
            state,
            "work",
            evaluate_acceptance(
                Task(id="work", depends_on=("dependency",)),
                snapshot(identity="snapshot-id"),
                verified(
                    task=Task(id="work", depends_on=("dependency",)),
                    status="pass",
                    task_id="work",
                    snapshot_identity="snapshot-id",
                ),
            ),
        )


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


def test_pass_requires_verifier_produced_result():
    decision = evaluate_acceptance(
        Task(id="work"),
        snapshot(identity="snapshot-id"),
        VerificationResult("pass", snapshot_identity="snapshot-id"),
    )

    assert decision.status == "FAIL"
    assert "verifier-produced" in decision.reason


def test_boundary_evidence_is_task_bound():
    task = Task(id="work", requires_independent_boundary=True)
    evidence = BoundaryEvidence("orca", "snapshot-id", "receipt", "other")

    decision = evaluate_acceptance(
        task,
        snapshot(identity="snapshot-id"),
        verified(
            task=task,
            status="pass",
            task_id="work",
            snapshot_identity="snapshot-id",
            boundary_evidence=evidence,
        ),
    )

    assert decision.status == "FAIL"


def test_revalidate_completed_tasks_demotes_stale_dependents():
    state = CoordinationState(
        goal="goal",
        tasks=(
            Task(id="dependency", state="completed", accepted_snapshot_identity="old"),
            Task(
                id="work",
                state="completed",
                depends_on=("dependency",),
                accepted_snapshot_identity="old",
            ),
        ),
    )

    updated = revalidate_completed_tasks(state, snapshot(identity="new"))

    assert [task.state for task in updated.tasks] == ["pending", "pending"]
    assert all(task.accepted_snapshot_identity is None for task in updated.tasks)


def test_revalidate_completed_tasks_keeps_matching_evidence():
    task = Task(id="work")
    state = CoordinationState(
        goal="goal",
        tasks=(
            Task(
                id="work",
                state="completed",
                accepted_snapshot_identity="snapshot-id",
                accepted_task_contract_identity=task.contract_identity(),
            ),
        ),
    )

    assert revalidate_completed_tasks(state, snapshot(identity="snapshot-id")) == state


def test_acceptance_rejects_stale_task_contract_evidence():
    task = Task(id="work", acceptance=("new check",))
    evidence = create_verification_result(
        Task(id="work", acceptance=("old check",)),
        snapshot(identity="snapshot-id"),
        passed=("new check",),
    )

    decision = evaluate_acceptance(task, snapshot(identity="snapshot-id"), evidence)

    assert decision.status == "FAIL"
    assert "task contract" in decision.reason


def test_revalidate_completed_tasks_demotes_changed_task_contract():
    original = Task(id="work", objective="old")
    changed = Task(
        id="work",
        objective="new",
        state="completed",
        accepted_snapshot_identity="snapshot-id",
        accepted_task_contract_identity=original.contract_identity(),
    )
    state = CoordinationState(goal="goal", tasks=(changed,))

    updated = revalidate_completed_tasks(state, snapshot(identity="snapshot-id"))

    assert updated.tasks[0].state == "pending"
    assert updated.tasks[0].accepted_snapshot_identity is None
    assert updated.tasks[0].accepted_task_contract_identity is None


def test_pass_transition_rejects_caller_forged_decision():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))

    with pytest.raises(ValueError, match="verifier-produced"):
        apply_task_transition(
            state,
            "work",
            AcceptanceDecision("PASS", "ok", accepted_snapshot_identity="snapshot-id"),
        )


def test_verifier_evidence_is_bound_to_task():
    evidence = create_verification_result(
        Task(id="first"), snapshot(identity="snapshot-id"), passed=("check",)
    )

    decision = evaluate_acceptance(
        Task(id="second", acceptance=("check",)),
        snapshot(identity="snapshot-id"),
        evidence,
    )

    assert decision.status == "FAIL"
    assert "another task" in decision.reason


def test_successful_reverification_refreshes_snapshot_identity():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="work", state="completed", accepted_snapshot_identity="old"),),
    )
    decision = evaluate_acceptance(
        Task(id="work"),
        snapshot(identity="new"),
        verified(task=Task(id="work"), status="pass", task_id="work", snapshot_identity="new"),
    )

    updated = apply_task_transition(state, "work", decision)

    assert updated.tasks[0].accepted_snapshot_identity == "new"
