import pytest

from general_os.git import GitSnapshot
from general_os.recovery import RecoveryError, next_unfinished_task
from general_os.state import CoordinationState, Task


def test_recovery_selects_first_unfinished_task_from_current_facts():
    state = CoordinationState(
        goal="goal",
        tasks=(
            Task(id="done", state="completed"),
            Task(id="blocked-by-done", depends_on=("done",)),
            Task(id="ready", state="active", depends_on=("done",)),
        ),
    )
    snapshot = GitSnapshot(
        branch="main",
        revision="abc123",
        changed_files=(),
        conflicts=(),
        clean=True,
    )

    assert next_unfinished_task(state, snapshot).id == "blocked-by-done"


def test_recovery_blocks_on_material_git_conflict():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))
    snapshot = GitSnapshot(
        branch="main",
        revision="abc123",
        changed_files=("file.txt",),
        conflicts=("file.txt",),
        clean=False,
    )

    with pytest.raises(RecoveryError, match="Git conflict"):
        next_unfinished_task(state, snapshot)


def test_recovery_returns_none_when_all_tasks_are_complete():
    state = CoordinationState(
        goal="goal", tasks=(Task(id="done", state="completed"),)
    )
    snapshot = GitSnapshot(
        branch="main",
        revision="abc123",
        changed_files=(),
        conflicts=(),
        clean=True,
    )

    assert next_unfinished_task(state, snapshot) is None
