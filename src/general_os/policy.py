"""Small runtime configuration and material-side-effect policy."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


SIDE_EFFECT_POLICIES = frozenset({"ask", "allow", "deny"})


class PolicyError(ValueError):
    """Raised when runtime policy is invalid."""


@dataclass(frozen=True)
class RuntimeConfig:
    native_subagents_enabled: bool = True
    orca_enabled: bool = False
    remote_side_effects: str = "ask"


@dataclass(frozen=True)
class AuthorityExceptions:
    remote_side_effects: str | None = None


def load_runtime_config(path: str | Path) -> RuntimeConfig:
    config_path = Path(path)
    if not config_path.exists():
        return RuntimeConfig()
    try:
        raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise PolicyError(f"invalid runtime policy: {config_path}") from exc
    runtime = raw.get("runtime", {})
    policy = raw.get("policy", {})
    if not isinstance(runtime, Mapping) or not isinstance(policy, Mapping):
        raise PolicyError("runtime and policy sections must be objects")
    return RuntimeConfig(
        native_subagents_enabled=runtime.get("native_subagents_enabled", True),
        orca_enabled=runtime.get("orca_enabled", False),
        remote_side_effects=policy.get("remote_side_effects", "ask"),
    )


def resolve_policy(
    exceptions: Mapping[str, str] | AuthorityExceptions | None = None,
    config: RuntimeConfig | None = None,
) -> RuntimeConfig:
    resolved = config or RuntimeConfig()
    if isinstance(exceptions, AuthorityExceptions):
        values = {
            "remote_side_effects": exceptions.remote_side_effects,
        }
    else:
        values = dict(exceptions or {})
    unknown = set(values) - {"remote_side_effects"}
    if unknown:
        raise PolicyError(f"unknown policy exception: {sorted(unknown)[0]}")
    remote_side_effects = values.get("remote_side_effects", resolved.remote_side_effects)
    if remote_side_effects is None:
        remote_side_effects = resolved.remote_side_effects
    if remote_side_effects not in SIDE_EFFECT_POLICIES:
        raise PolicyError(f"invalid remote_side_effects: {remote_side_effects}")
    if resolved.remote_side_effects not in SIDE_EFFECT_POLICIES:
        raise PolicyError(
            f"invalid remote_side_effects: {resolved.remote_side_effects}"
        )
    if resolved.remote_side_effects == "deny" and remote_side_effects != "deny":
        remote_side_effects = "deny"
    if not isinstance(resolved.native_subagents_enabled, bool):
        raise PolicyError("native_subagents_enabled must be boolean")
    if not isinstance(resolved.orca_enabled, bool):
        raise PolicyError("orca_enabled must be boolean")
    return RuntimeConfig(
        native_subagents_enabled=resolved.native_subagents_enabled,
        orca_enabled=resolved.orca_enabled,
        remote_side_effects=remote_side_effects,
    )
