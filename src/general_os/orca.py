"""Thin optional Orca boundary for independently managed work."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from general_os.profiles import ProfileProjection


@dataclass(frozen=True)
class OrcaStatusObservation:
    status: str
    reachable: bool | None = None
    state: str | None = None
    app_version: str | None = None
    executable: str | None = None
    message: str = ""


@dataclass(frozen=True)
class OrcaLaunch:
    """One-way launch configuration projected into native Orca CLI flags."""

    agent: str | None
    model: str | None
    effort: str | None
    prompt: str

    def argv(self, executable: str = "orca") -> tuple[str, ...]:
        if not self.agent:
            raise ValueError("Orca launch requires an explicit harness")
        if self.effort and not self.model:
            raise ValueError("Orca effort requires an explicit model")

        command = [executable, "agent", "launch", "--agent", self.agent]
        if self.model:
            command.extend(("--model", self.model))
        if self.effort:
            command.extend(("--effort", self.effort))
        if self.prompt:
            command.extend(("--prompt", self.prompt))
        return tuple(command)


def build_orca_launch(projection: ProfileProjection) -> OrcaLaunch:
    """Project explicit general-os profile facts into native Orca launch data."""

    return OrcaLaunch(
        agent=projection.harness,
        model=projection.model,
        effort=projection.effort,
        prompt=projection.instructions,
    )


Runner = Callable[[Sequence[str], float | None], subprocess.CompletedProcess[str]]
DEFAULT_STATUS_TIMEOUT = 30.0


class OrcaCliStatusObserver:
    """Observe the installed Orca runtime without owning its lifecycle."""

    def __init__(
        self,
        *,
        executable: str | None = None,
        runner: Runner | None = None,
        environ: Mapping[str, str] | None = None,
    ) -> None:
        self.executable = executable
        self.runner = runner or self._run
        self.environ = environ if environ is not None else os.environ

    def observe(self, *, timeout: float | None = None) -> OrcaStatusObservation:
        executable = self.executable or self.discover_executable(self.environ)
        if executable is None:
            return OrcaStatusObservation(
                "unavailable", message="Orca executable not found"
            )
        try:
            completed = self.runner(
                (executable, "status", "--json"),
                DEFAULT_STATUS_TIMEOUT if timeout is None else timeout,
            )
        except subprocess.TimeoutExpired:
            return OrcaStatusObservation(
                "failed", executable=executable, message="Orca status timed out"
            )
        except OSError as exc:
            return OrcaStatusObservation(
                "failed", executable=executable, message=f"Orca status failed: {exc}"
            )

        if completed.returncode != 0:
            message = (completed.stderr or completed.stdout).strip()
            return OrcaStatusObservation(
                "failed",
                executable=executable,
                message=message or f"Orca status exited with {completed.returncode}",
            )
        try:
            payload = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            return OrcaStatusObservation(
                "failed", executable=executable, message=f"invalid Orca JSON: {exc}"
            )
        if not isinstance(payload, Mapping) or payload.get("ok") is not True:
            return OrcaStatusObservation(
                "failed", executable=executable, message="Orca status response was not ok"
            )
        result = payload.get("result")
        runtime = result.get("runtime") if isinstance(result, Mapping) else None
        if not isinstance(runtime, Mapping) or not isinstance(
            runtime.get("reachable"), bool
        ):
            return OrcaStatusObservation(
                "failed",
                executable=executable,
                message="Orca status response lacked runtime.reachable",
            )
        reachable = runtime["reachable"]
        return OrcaStatusObservation(
            "ready" if reachable else "unavailable",
            reachable=reachable,
            state=_optional_string(runtime.get("state")),
            app_version=_optional_string(runtime.get("appVersion")),
            executable=executable,
        )

    @staticmethod
    def discover_executable(environ: Mapping[str, str] | None = None) -> str | None:
        environment = environ if environ is not None else os.environ
        configured = environment.get("GENERAL_OS_ORCA_CLI")
        if configured:
            return str(Path(configured))
        for command in ("orca", "orca.exe"):
            found = shutil.which(command)
            if found:
                return found
        local_app_data = environment.get("LOCALAPPDATA")
        if local_app_data:
            derived = (
                Path(local_app_data)
                / "Programs"
                / "orca"
                / "resources"
                / "bin"
                / "orca.exe"
            )
            if derived.is_file():
                return str(derived)
        return None

    @staticmethod
    def _run(
        command: Sequence[str], timeout: float | None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            capture_output=True,
            check=False,
            text=True,
            timeout=timeout,
        )


def _optional_string(value: Any) -> str | None:
    return value if isinstance(value, str) else None
