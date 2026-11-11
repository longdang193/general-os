from general_os.codex import CodexClient
from general_os.cos import ChiefOfStaff, CoSDecision
from general_os.git import GitSnapshot
from general_os.orca import OrcaClient
from general_os.policy import RuntimeConfig
from general_os.profiles import ProfileSpec
from general_os.state import CoordinationState, Task


class RecordingCodexTransport:
    def __init__(self):
        self.requests = []

    def start(self, request):
        self.requests.append(request)
        return {"id": "thread-1", "status": "running"}


class RecordingOrcaTransport:
    def __init__(self):
        self.requests = []

    def dispatch(self, request):
        self.requests.append(request)
        return {"id": "worker-1", "status": "running"}


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


def test_dispatch_task_uses_task_objective_for_codex():
    state = CoordinationState(
        goal="overall goal",
        tasks=(Task(id="work", objective="bounded objective"),),
    )
    transport = RecordingCodexTransport()
    chief = ChiefOfStaff(
        state=state,
        policy=RuntimeConfig(),
        profiles={"normal": ProfileSpec("normal")},
        codex=CodexClient(transport),
        orca=OrcaClient(),
    )

    chief.dispatch_task(
        CoSDecision("codex", "work", "normal", "single assignment"),
        state.tasks[0],
        "C:/work/general-os",
    )

    assert transport.requests[0].prompt == "bounded objective"


def test_dispatch_goal_only_uses_global_goal_for_codex():
    state = CoordinationState(goal="overall goal")
    transport = RecordingCodexTransport()
    chief = ChiefOfStaff(
        state=state,
        policy=RuntimeConfig(),
        profiles={"normal": ProfileSpec("normal")},
        codex=CodexClient(transport),
        orca=OrcaClient(),
    )

    chief.dispatch_task(
        CoSDecision("codex", None, "normal", "goal-only assignment"),
        None,
        "C:/work/general-os",
    )

    assert transport.requests[0].prompt == "overall goal"


def test_dispatch_task_uses_task_objective_for_orca():
    state = CoordinationState(
        goal="overall goal",
        tasks=(
            Task(
                id="work",
                objective="independent bounded objective",
                requires_independent_boundary=True,
            ),
        ),
    )
    transport = RecordingOrcaTransport()
    chief = ChiefOfStaff(
        state=state,
        policy=RuntimeConfig(orca_enabled=True),
        profiles={"normal": ProfileSpec("normal")},
        codex=CodexClient(),
        orca=OrcaClient(transport, enabled=True),
    )

    chief.dispatch_task(
        CoSDecision("orca", "work", "normal", "independent boundary required"),
        state.tasks[0],
        "C:/work/general-os",
    )

    assert transport.requests[0].prompt == "independent bounded objective"


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
