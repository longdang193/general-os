import json

from general_os.cli import main


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
    assert output["strategy"] == "blocked"
    assert "task" in output["reason"].lower()


def test_orca_smoke_reports_unavailable_without_claiming_verified(capsys):
    assert main(["orca", "smoke", "--json"]) == 0

    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "unavailable"
    assert output["verified"] is False
