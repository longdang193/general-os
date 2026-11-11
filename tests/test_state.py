import json

import pytest

from general_os.state import CoordinationState, StateError, Task, load_state, save_state


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


def test_task_without_objective_remains_backward_compatible():
    task = Task.from_dict({"id": "work"})

    assert task.objective is None
    assert task.to_dict() == {
        "id": "work",
        "state": "pending",
        "depends_on": [],
        "acceptance": [],
    }
