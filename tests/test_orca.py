import json
import subprocess

import pytest

from general_os.orca import OrcaCliStatusObserver, build_orca_launch
from general_os.profiles import (
    ProfileProjection,
    load_profiles,
    project_profile,
    resolve_profile,
)


def completed(payload, *, returncode=0, stderr=""):
    return subprocess.CompletedProcess(
        ["orca", "status", "--json"],
        returncode,
        json.dumps(payload),
        stderr,
    )


def test_orca_status_observer_prefers_explicit_executable(tmp_path, monkeypatch):
    configured = tmp_path / "configured-orca.exe"
    configured.write_text("", encoding="utf-8")
    path_candidate = tmp_path / "path-orca.exe"
    path_candidate.write_text("", encoding="utf-8")
    monkeypatch.setattr("general_os.orca.shutil.which", lambda _: str(path_candidate))

    assert OrcaCliStatusObserver.discover_executable(
        {"GENERAL_OS_ORCA_CLI": str(configured)}
    ) == str(configured)


def test_orca_status_observer_does_not_fall_back_from_invalid_explicit_path(
    tmp_path, monkeypatch
):
    path_candidate = tmp_path / "path-orca.exe"
    path_candidate.write_text("", encoding="utf-8")
    monkeypatch.setattr("general_os.orca.shutil.which", lambda _: str(path_candidate))

    configured = tmp_path / "missing-orca.exe"
    assert OrcaCliStatusObserver.discover_executable(
        {"GENERAL_OS_ORCA_CLI": str(configured)}
    ) == str(configured)


def test_orca_status_observer_maps_ready_and_optional_diagnostics():
    observed_timeout = []
    observer = OrcaCliStatusObserver(
        executable="orca",
        runner=lambda command, timeout: observed_timeout.append(timeout)
        or completed({"ok": True, "result": {"runtime": {"reachable": True}}}),
    )

    observation = observer.observe()

    assert observation.status == "ready"
    assert observation.reachable is True
    assert observation.state is None
    assert observation.app_version is None
    assert observed_timeout == [30.0]


def test_orca_status_observer_reports_missing_executable(tmp_path, monkeypatch):
    monkeypatch.setattr("general_os.orca.shutil.which", lambda _: None)

    observation = OrcaCliStatusObserver(
        environ={"LOCALAPPDATA": str(tmp_path)}
    ).observe()

    assert observation.status == "unavailable"
    assert observation.reachable is None


def test_orca_status_observer_reports_malformed_and_process_failures():
    malformed = OrcaCliStatusObserver(
        executable="orca",
        runner=lambda command, timeout: subprocess.CompletedProcess(
            command, 0, "not-json", ""
        ),
    ).observe()
    failed = OrcaCliStatusObserver(
        executable="orca",
        runner=lambda command, timeout: completed(
            {"ok": False}, returncode=1, stderr="runtime unavailable"
        ),
    ).observe()

    assert malformed.status == "failed"
    assert "invalid Orca JSON" in malformed.message
    assert failed.status == "failed"
    assert failed.message == "runtime unavailable"


def test_orca_status_observer_reports_timeout():
    def timeout(command, limit):
        raise subprocess.TimeoutExpired(command, limit)

    observation = OrcaCliStatusObserver(executable="orca", runner=timeout).observe()

    assert observation.status == "failed"
    assert observation.message == "Orca status timed out"


def test_orca_launch_projects_only_explicit_profile_values():
    launch = build_orca_launch(
        ProfileProjection(
            harness="claude",
            model="verified-claude-model",
            effort="high",
            instructions="Review the architecture and report evidence.",
        )
    )

    assert launch.argv("orca") == (
        "orca",
        "agent",
        "launch",
        "--agent",
        "claude",
        "--model",
        "verified-claude-model",
        "--effort",
        "high",
        "--prompt",
        "Review the architecture and report evidence.",
    )


def test_orca_launch_omits_native_defaults():
    launch = build_orca_launch(
        ProfileProjection(
            harness="codex",
            model=None,
            effort=None,
            instructions="",
        )
    )

    assert launch.argv("orca") == ("orca", "agent", "launch", "--agent", "codex")


def test_orca_launch_projects_ephemeral_assignment_when_profile_is_empty():
    launch = build_orca_launch(
        ProfileProjection("codex", "combo-normal", "medium", ""),
        "Implement X and verify pytest -q.",
    )

    assert launch.argv("orca")[-2:] == ("--prompt", "Implement X and verify pytest -q.")


@pytest.mark.parametrize(
    ("name", "model", "effort"),
    [
        ("low", "combo-low", "low"),
        ("normal", "combo-normal", "medium"),
        ("high", "combo-high", "high"),
        ("xhigh", "combo-xhigh", "xhigh"),
    ],
)
def test_orca_launch_uses_only_supplied_profile_projection(name, model, effort):
    profile = resolve_profile(name, load_profiles("agents"))

    launch = build_orca_launch(project_profile(profile))

    assert launch.model == model
    assert launch.effort == effort
    assert launch.argv("orca") == (
        "orca",
        "agent",
        "launch",
        "--agent",
        "codex",
        "--model",
        model,
        "--effort",
        effort,
    )


@pytest.mark.parametrize(
    ("projection", "message"),
    [
        (
            ProfileProjection(None, "model", None, ""),
            "Orca launch requires an explicit harness",
        ),
        (
            ProfileProjection("claude", None, "high", ""),
            "Orca effort requires an explicit model",
        ),
    ],
)
def test_orca_launch_rejects_incomplete_projection(projection, message):
    launch = build_orca_launch(projection)

    with pytest.raises(ValueError, match=message):
        launch.argv("orca")
