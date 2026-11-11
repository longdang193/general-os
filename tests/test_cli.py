import json

from general_os import cli
from general_os.cli import main
from general_os.orca import OrcaStatusObservation


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
