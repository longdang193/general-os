from general_os.codex import (
    CodexClient,
    CodexObservation,
    CodexRequest,
)
from general_os.dispatch import CodexDispatchRequest, dispatch_codex


class FakeCodexTransport:
    def __init__(self, start_result=None):
        self.start_result = start_result or {"id": "thread-1", "status": "running"}
        self.started = []
        self.inspected = []
        self.cancelled = []

    def start(self, request):
        self.started.append(request)
        return self.start_result

    def inspect(self, runtime_id):
        self.inspected.append(runtime_id)
        return {"id": runtime_id, "status": "finished", "message": "done"}

    def cancel(self, runtime_id):
        self.cancelled.append(runtime_id)
        return {"id": runtime_id, "status": "cancelled"}


def request():
    return CodexRequest(
        task_id="task-1",
        prompt="Implement the task",
        workspace="C:/work/general-os",
        profile="normal",
        native_subagents_enabled=True,
    )


def test_codex_client_maps_native_start_and_observe():
    transport = FakeCodexTransport()
    client = CodexClient(transport)

    started = client.run(request())
    observed = client.inspect(started.runtime_id)

    assert started == CodexObservation("running", "thread-1")
    assert observed == CodexObservation("finished", "thread-1", "done")
    assert transport.started == [request()]


def test_codex_client_cancels_through_native_boundary():
    transport = FakeCodexTransport()
    observation = CodexClient(transport).cancel("thread-1")

    assert observation == CodexObservation("cancelled", "thread-1")
    assert transport.cancelled == ["thread-1"]


def test_codex_client_reports_unavailable_without_transport():
    observation = CodexClient().run(request())

    assert observation.status == "unavailable"
    assert observation.runtime_id is None


def test_codex_client_reports_malformed_native_response():
    observation = CodexClient(FakeCodexTransport(start_result={"status": "running"})).run(
        request()
    )

    assert observation.status == "failed"
    assert "runtime id" in observation.message


def test_dispatch_keeps_native_subagents_inside_codex_request():
    transport = FakeCodexTransport()
    dispatch_request = CodexDispatchRequest(
        task_id="task-1",
        prompt="Implement the task",
        workspace="C:/work/general-os",
        profile="normal",
        native_subagents_enabled=True,
    )

    observation = dispatch_codex(CodexClient(transport), dispatch_request)

    assert observation.status == "running"
    assert transport.started[0].native_subagents_enabled is True
