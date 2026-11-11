import json

from general_os import cli
from general_os.cli import main
from general_os.git import GitSnapshot
from general_os.orca import OrcaStatusObservation
from general_os.state import CoordinationState, Task, load_state, save_state


def test_state_validate_returns_json(capsys):
    assert main(["state", "validate", "state/coordination.json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "valid"


def test_cos_next_returns_codex_decision_json(capsys):
    assert (
        main(
            [
                "cos",
                "next",
                "--state",
                "state/coordination.json",
                "--repo",
                ".",
                "--json",
            ]
        )
        == 0
    )

    output = json.loads(capsys.readouterr().out)
    assert output["strategy"] == "codex"
    assert output["task_id"] is None
    assert output["reason"] == "goal-only assignment"


def test_orca_smoke_reports_observed_status_without_claiming_worker_completion(
    monkeypatch, capsys
):
    monkeypatch.setattr(
        cli,
        "OrcaCliStatusObserver",
        lambda: type(
            "FakeObserver",
            (),
            {
                "observe": lambda self: OrcaStatusObservation(
                    "ready",
                    reachable=True,
                    state="ready",
                    app_version="test",
                    executable="orca",
                )
            },
        )(),
    )

    assert main(["orca", "smoke", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "ready"
    assert output["reachable"] is True
    assert output["verified"] is True


def test_accept_persists_material_blocker_but_not_retryable_failure(
    tmp_path, monkeypatch, capsys
):
    state_path = tmp_path / "coordination.json"
    save_state(
        state_path,
        CoordinationState(goal="goal", tasks=(Task(id="work", state="active"),)),
    )
    monkeypatch.setattr(
        cli,
        "inspect_git",
        lambda _: GitSnapshot("main", "abc123", (), (), True),
    )

    assert (
        main(
            [
                "accept",
                "--state",
                str(state_path),
                "--repo",
                ".",
                "--task-id",
                "work",
                "--status",
                "fail",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert load_state(state_path).tasks[0].state == "active"

    assert (
        main(
            [
                "accept",
                "--state",
                str(state_path),
                "--repo",
                ".",
                "--task-id",
                "work",
                "--status",
                "blocked",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert load_state(state_path).tasks[0].state == "blocked"
