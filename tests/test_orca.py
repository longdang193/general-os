from general_os.dispatch import OrcaDispatchRequest, dispatch_orca
from general_os.orca import OrcaClient, OrcaObservation, OrcaRequest


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
