import json

import pytest

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
    assert output["probe_ok"] is True
    assert "verified" not in output


def test_accept_persists_material_blocker_but_not_retryable_failure(
    tmp_path, monkeypatch, capsys
):
    inspect_calls = []
    state_path = tmp_path / "coordination.json"
    save_state(
        state_path,
        CoordinationState(goal="goal", tasks=(Task(id="work", state="active"),)),
    )
    monkeypatch.setattr(
        cli,
        "inspect_git",
        lambda _, **kwargs: (
            inspect_calls.append(kwargs) or GitSnapshot("main", "abc123", (), (), True)
        ),
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
                "--blocker-category",
                "dependency",
                "--blocker-reason",
                "waiting on prerequisite",
            ]
        )
        == 0
    )
    capsys.readouterr()
    assert load_state(state_path).tasks[0].state == "blocked"
    assert inspect_calls == [{"include_identity": False}, {"include_identity": False}]
    assert load_state(state_path).tasks[0].blocker_category == "dependency"


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
        lambda _, **kwargs: GitSnapshot("main", "abc123", (), (), True, "current"),
    )

    with pytest.raises(SystemExit):
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
            ]
        )
    assert load_state(state_path).tasks[0].state == "active"


def test_orca_smoke_returns_nonzero_for_unavailable(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "OrcaCliStatusObserver",
        lambda: type(
            "FakeObserver",
            (),
            {"observe": lambda self: OrcaStatusObservation("unavailable")},
        )(),
    )

    assert main(["orca", "smoke", "--json"]) == 1
    output = json.loads(capsys.readouterr().out)

    assert output["status"] == "unavailable"


def test_orca_smoke_returns_nonzero_for_failed_probe(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "OrcaCliStatusObserver",
        lambda: type(
            "FakeObserver",
            (),
            {"observe": lambda self: OrcaStatusObservation("failed", message="bad")},
        )(),
    )

    assert main(["orca", "smoke", "--json"]) == 1
    output = json.loads(capsys.readouterr().out)

    assert output["status"] == "failed"
    assert output["message"] == "bad"


def test_deploy_cli_emits_json_and_passes_boundary_options(monkeypatch, capsys):
    calls = []

    def fake_deploy(repo, **kwargs):
        calls.append((repo, kwargs))
        return (
            0,
            {"status": "dry-run", "repo_root": repo, "adapter": kwargs["adapter"]},
        )

    monkeypatch.setattr(
        cli,
        "deploy",
        fake_deploy,
    )

    assert main(["deploy", "--repo", "project", "--adapter", "codex", "--dry-run"]) == 0

    assert json.loads(capsys.readouterr().out) == {
        "adapter": "codex",
        "repo_root": "project",
        "status": "dry-run",
    }
    assert calls[0][0] == "project"
    assert calls[0][1]["adopt"] is True


def test_deploy_cli_defaults_to_central_only(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        cli,
        "deploy",
        lambda repo, **kwargs: (calls.append((repo, kwargs)) or (0, {"repo_root": repo})),
    )

    assert main(["deploy", "--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out) == {"repo_root": None}
    assert calls[0][0] is None
    assert calls[0][1]["adopt"] is False


def test_deploy_rejects_unsupported_adapter(capsys):
    with pytest.raises(SystemExit):
        main(["deploy", "--adapter", "claude", "--dry-run"])
    assert "unsupported adapter" in capsys.readouterr().err


def test_accept_cli_does_not_accept_free_form_boundary_evidence():
    with pytest.raises(SystemExit):
        main(["accept", "--boundary-evidence", '{"kind":"orca"}'])


def test_accept_persists_blocked_retry_recovery(tmp_path, monkeypatch, capsys):
    state_path = tmp_path / "coordination.json"
    save_state(
        state_path,
        CoordinationState(
            goal="goal",
            tasks=(Task(id="work", state="blocked", blocker_category="external", blocker_reason="offline"),),
        ),
    )
    monkeypatch.setattr(
        cli,
        "inspect_git",
        lambda _, **kwargs: GitSnapshot("main", "abc123", (), (), True),
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


def test_accept_rejects_blocked_without_category_or_reason(tmp_path, monkeypatch):
    state_path = tmp_path / "coordination.json"
    save_state(state_path, CoordinationState(goal="goal", tasks=(Task(id="work"),)))
    monkeypatch.setattr(
        cli,
        "inspect_git",
        lambda _, **kwargs: GitSnapshot("main", "abc123", (), (), True),
    )

    with pytest.raises(SystemExit):
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
