import json
import subprocess

from general_os.orca import OrcaCliStatusObserver


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


def test_orca_status_observer_maps_ready_and_optional_diagnostics():
    observer = OrcaCliStatusObserver(
        executable="orca",
        runner=lambda command, timeout: completed(
            {"ok": True, "result": {"runtime": {"reachable": True}}}
        ),
    )

    observation = observer.observe()

    assert observation.status == "ready"
    assert observation.reachable is True
    assert observation.state is None
    assert observation.app_version is None


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
