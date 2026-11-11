from general_os.acceptance import (
    AcceptanceDecision,
    VerificationResult,
    apply_task_transition,
    evaluate_acceptance,
)
from general_os.git import GitSnapshot
from general_os.state import CoordinationState, Task


def snapshot(revision="abc123"):
    return GitSnapshot("main", revision, (), (), True)


def test_acceptance_passes_fresh_required_proof():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot(),
        VerificationResult("pass", ("tests pass",), "abc123"),
    )

    assert decision == AcceptanceDecision("PASS", "required proof is current")


def test_acceptance_rejects_stale_proof_against_current_git():
    task = Task(id="work", acceptance=("tests pass",))

    decision = evaluate_acceptance(
        task,
        snapshot("new-revision"),
        VerificationResult("pass", ("tests pass",), "old-revision"),
    )

    assert decision.status == "BLOCKED"
    assert "stale" in decision.reason


def test_acceptance_updates_only_durable_task_state_idempotently():
    state = CoordinationState(goal="goal", tasks=(Task(id="work", state="active"),))
    decision = AcceptanceDecision("PASS", "required proof is current")

    completed = apply_task_transition(state, "work", decision)
    repeated = apply_task_transition(completed, "work", decision)

    assert completed.tasks[0].state == "completed"
    assert repeated == completed
