import json
import multiprocessing
from dataclasses import replace

import pytest

from general_os.state import CoordinationState, StateError, Task, load_state, save_state


def _concurrent_save(path, goal, barrier, results):
    try:
        state = load_state(path)
        barrier.wait()
        state = replace(state, goal=goal)
        save_state(path, state)
    except StateError as exc:
        results.put(f"error:{exc}")
    else:
        results.put("saved")


def test_state_round_trips_goal_tasks_and_acceptance(tmp_path):
    state = CoordinationState(
        goal="Ship the admission fix",
        tasks=(
            Task(
                id="fix-admission",
                objective="Implement the admission fix",
                acceptance=("regression passes", "existing tests pass"),
                profile="high",
            ),
        ),
        policy_exceptions={"remote_side_effects": "ask"},
    )

    path = tmp_path / "coordination.json"
    save_state(path, state)

    assert load_state(path) == state


def test_task_rejects_invalid_state():
    with pytest.raises(StateError, match="invalid task state"):
        Task(id="work", state="running")


def test_task_rejects_blank_objective():
    with pytest.raises(StateError, match="objective must be a non-empty string"):
        Task(id="work", objective=" ")


def test_state_rejects_unknown_dependency_and_cycles():
    with pytest.raises(StateError, match="unknown dependency"):
        CoordinationState(
            goal="goal",
            tasks=(Task(id="a", depends_on=("missing",)),),
        )

    with pytest.raises(StateError, match="cyclic dependency"):
        CoordinationState(
            goal="goal",
            tasks=(
                Task(id="a", depends_on=("b",)),
                Task(id="b", depends_on=("a",)),
            ),
        )


def test_state_rejects_runtime_identity_and_progress_fields(tmp_path):
    path = tmp_path / "coordination.json"
    path.write_text(
        json.dumps(
            {
                "goal": "goal",
                "codex_thread_id": "thread-1",
                "tasks": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(StateError, match="unknown state field"):
        load_state(path)


def test_state_serialization_does_not_add_runtime_fields():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))

    payload = state.to_dict()

    assert payload == {
        "version": 1,
        "goal": "goal",
        "tasks": [
            {
                "id": "work",
                "state": "pending",
                "depends_on": [],
                "acceptance": [],
            }
        ],
    }


def test_legacy_state_reads_and_future_versions_fail(tmp_path):
    path = tmp_path / "coordination.json"
    path.write_text(json.dumps({"goal": "legacy", "tasks": []}), encoding="utf-8")

    state = load_state(path)
    assert state.version == 1
    save_state(path, state)
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == 1

    path.write_text(json.dumps({"version": 2, "goal": "future", "tasks": []}), encoding="utf-8")
    with pytest.raises(StateError, match="unsupported state version"):
        load_state(path)


def test_stale_loaded_state_is_rejected(tmp_path):
    path = tmp_path / "coordination.json"
    save_state(path, CoordinationState(goal="initial"))
    first = load_state(path)
    second = load_state(path)
    save_state(path, CoordinationState(goal="first", tasks=first.tasks, version=first.version, _source_digest=first._source_digest))

    with pytest.raises(StateError, match="changed since it was loaded"):
        save_state(path, CoordinationState(goal="second", tasks=second.tasks, version=second.version, _source_digest=second._source_digest))


def test_fresh_state_cannot_overwrite_existing_state(tmp_path):
    path = tmp_path / "coordination.json"
    save_state(path, CoordinationState(goal="initial"))

    with pytest.raises(StateError, match="loaded source provenance"):
        save_state(path, CoordinationState(goal="replacement"))


def test_two_process_writers_accept_one_update_and_reject_one_stale_writer(tmp_path):
    path = tmp_path / "coordination.json"
    save_state(path, CoordinationState(goal="initial"))
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    results = context.Queue()
    processes = [
        context.Process(target=_concurrent_save, args=(path, goal, barrier, results))
        for goal in ("first", "second")
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(10)
        assert process.exitcode == 0

    outcomes = sorted(results.get(timeout=2) for _ in processes)
    assert outcomes[0].startswith("error:state changed since it was loaded")
    assert outcomes[1] == "saved"


def test_task_without_objective_remains_backward_compatible():
    task = Task.from_dict({"id": "work"})

    assert task.objective is None
    assert task.to_dict() == {
        "id": "work",
        "state": "pending",
        "depends_on": [],
        "acceptance": [],
    }


def test_blocker_context_round_trips():
    state = CoordinationState(
        goal="goal",
        tasks=(
            Task(
                id="work",
                state="blocked",
                blocker_category="external",
                blocker_reason="service unavailable",
            ),
        ),
    )

    restored = CoordinationState.from_dict(state.to_dict())

    assert restored.tasks[0].blocker_category == "external"
    assert restored.tasks[0].blocker_reason == "service unavailable"


def test_state_rejects_malformed_policy_expiry():
    with pytest.raises(StateError, match="ISO-8601"):
        CoordinationState(
            goal="goal",
            policy_exceptions={
                "remote_side_effects": "allow",
                "scope": "github:general-os",
                "provenance": "user-approval",
                "expires_at": "not-a-date",
            },
        )
