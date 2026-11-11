import json
import subprocess

from general_os.dispatch import OrcaDispatchRequest, dispatch_orca
from general_os.orca import (
    OrcaCliStatusObserver,
    OrcaClient,
    OrcaObservation,
    OrcaRequest,
)


class FakeOrcaTransport:
    def __init__(self, dispatch_result=None):
        self.dispatch_result = dispatch_result or {
            "id": "worker-1",
            "status": "running",
        }
        self.dispatched = []
        self.inspected = []
        self.cancelled = []

    def dispatch(self, request):
        self.dispatched.append(request)
        return self.dispatch_result

    def inspect(self, worker_id):
        self.inspected.append(worker_id)
        return {"id": worker_id, "status": "finished", "message": "done"}

    def cancel(self, worker_id):
        self.cancelled.append(worker_id)
        return {"id": worker_id, "status": "cancelled"}


def request():
    return OrcaRequest(
        task_id="task-1",
        prompt="Run an independent workstream",
        workspace="C:/work/general-os",
        profile="high",
    )


def test_orca_client_maps_fake_transport_lifecycle():
    transport = FakeOrcaTransport()
    client = OrcaClient(transport=transport, enabled=True)

    started = client.dispatch(request())
    observed = client.inspect(started.worker_id)
    cancelled = client.cancel(started.worker_id)

    assert started == OrcaObservation("running", "worker-1")
    assert observed == OrcaObservation("finished", "worker-1", "done")
    assert cancelled == OrcaObservation("cancelled", "worker-1")


def test_orca_disabled_or_unconfigured_is_non_blocking():
    assert OrcaClient().dispatch(request()).status == "unavailable"
    assert OrcaClient(FakeOrcaTransport(), enabled=False).dispatch(request()).status == (
        "unavailable"
    )


def test_orca_client_reports_malformed_dispatch_response():
    client = OrcaClient(
        FakeOrcaTransport(dispatch_result={"status": "running"}),
        enabled=True,
    )

    observation = client.dispatch(request())

    assert observation.status == "failed"
    assert "worker id" in observation.message


def test_dispatch_keeps_orca_request_independent_from_codex_children():
    transport = FakeOrcaTransport()
    dispatch_request = OrcaDispatchRequest(
        task_id="task-1",
        prompt="Run an independent workstream",
        workspace="C:/work/general-os",
        profile="high",
    )

    observation = dispatch_orca(
        OrcaClient(transport=transport, enabled=True), dispatch_request
    )

    assert observation.status == "running"
    assert transport.dispatched[0].task_id == "task-1"


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
