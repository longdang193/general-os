from general_os.codex import CodexClient
from general_os.cos import ChiefOfStaff, CoSDecision
from general_os.git import GitSnapshot
from general_os.orca import OrcaClient
from general_os.policy import RuntimeConfig
from general_os.profiles import ProfileSpec
from general_os.state import CoordinationState, Task


def snapshot(revision="abc123", conflicts=()):
    return GitSnapshot(
        branch="main",
        revision=revision,
        changed_files=(),
        conflicts=tuple(conflicts),
        clean=not conflicts,
    )


def make_cos(state, *, orca_enabled=False):
    return ChiefOfStaff(
        state=state,
        policy=RuntimeConfig(orca_enabled=orca_enabled),
        profiles={"normal": ProfileSpec("normal")},
        codex=CodexClient(),
        orca=OrcaClient(enabled=orca_enabled),
    )


def test_cos_chooses_codex_and_leaves_native_children_to_codex():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))

    decision = make_cos(state).choose_strategy(state.tasks[0], snapshot())

    assert decision == CoSDecision("codex", "work", "normal", "single assignment")


def test_cos_chooses_codex_goal_only_when_task_graph_is_empty():
    state = CoordinationState(goal="goal")

    decision = make_cos(state).next_decision(snapshot())

    assert decision == CoSDecision("codex", None, "normal", "goal-only assignment")


def test_cos_reports_done_when_all_declared_tasks_are_completed():
    state = CoordinationState(
        goal="goal", tasks=(Task(id="work", state="completed"),)
    )

    decision = make_cos(state).next_decision(snapshot())

    assert decision == CoSDecision(
        "done", None, "normal", "all declared tasks completed"
    )


def test_cos_blocks_when_unfinished_tasks_have_no_ready_dependency():
    state = CoordinationState(
        goal="goal",
        tasks=(
            Task(id="dependency", state="blocked"),
            Task(id="work", depends_on=("dependency",)),
        ),
    )

    decision = make_cos(state).next_decision(snapshot())

    assert decision == CoSDecision(
        "blocked", None, "normal", "no dependency-ready task"
    )


def test_cos_chooses_orca_only_for_independent_enabled_work():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="work", requires_independent_boundary=True),),
    )

    decision = make_cos(state, orca_enabled=True).choose_strategy(
        state.tasks[0], snapshot()
    )

    assert decision.strategy == "orca"


def test_cos_blocks_independent_work_when_orca_is_disabled():
    state = CoordinationState(
        goal="goal",
        tasks=(Task(id="work", requires_independent_boundary=True),),
    )

    decision = make_cos(state).choose_strategy(state.tasks[0], snapshot())

    assert decision.strategy == "blocked"
    assert "Orca" in decision.reason


def test_cos_blocks_on_git_conflict():
    state = CoordinationState(goal="goal", tasks=(Task(id="work"),))

    decision = make_cos(state).choose_strategy(state.tasks[0], snapshot(conflicts=("x",)))

    assert decision.strategy == "blocked"
