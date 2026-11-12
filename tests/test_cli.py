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


def test_profile_resolve_returns_one_way_projection(capsys):
    assert main(["profile", "resolve", "--name", "high", "--directory", "agents"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output == {
        "effort": "high",
        "harness": "codex",
        "instructions": "",
        "model": "combo-high",
        "profile": "high",
    }


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


def test_accept_requires_verifier_snapshot_identity(tmp_path, monkeypatch, capsys):
    state_path = tmp_path / "coordination.json"
    save_state(
        state_path,
        CoordinationState(
            goal="goal", tasks=(Task(id="work", state="active", acceptance=("check",)),)
        ),
    )
    monkeypatch.setattr(
        cli,
        "inspect_git",
        lambda _: GitSnapshot("main", "abc123", (), (), True, "current"),
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
                "pass",
                "--check",
                "check",
                "--revision",
                "abc123",
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)

    assert output["status"] == "FAIL"
    assert load_state(state_path).tasks[0].state == "active"


def test_accept_persists_blocked_retry_recovery(tmp_path, monkeypatch, capsys):
    state_path = tmp_path / "coordination.json"
    save_state(
        state_path,
        CoordinationState(goal="goal", tasks=(Task(id="work", state="blocked"),)),
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

    assert load_state(state_path).tasks[0].state == "pending"
