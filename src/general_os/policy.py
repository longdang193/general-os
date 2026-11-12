"""Small runtime configuration and material-side-effect policy."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from datetime import datetime, timezone
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
    scope: str | None = None
    provenance: str | None = None
    expires_at: str | None = None


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
    requested_scope: str | None = None,
) -> RuntimeConfig:
    resolved = config or RuntimeConfig()
    if isinstance(exceptions, AuthorityExceptions):
        values = {
            "remote_side_effects": exceptions.remote_side_effects,
            "scope": exceptions.scope,
            "provenance": exceptions.provenance,
            "expires_at": exceptions.expires_at,
        }
        values = {key: value for key, value in values.items() if value is not None}
    else:
        values = dict(exceptions or {})
    unknown = set(values) - {
        "remote_side_effects",
        "scope",
        "provenance",
        "expires_at",
    }
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
    if values.get("remote_side_effects") == "allow" and remote_side_effects == "allow":
        missing = {"scope", "provenance", "expires_at"} - set(values)
        if missing:
            raise PolicyError(
                "allow policy exception requires requested scope, provenance, and expiry"
            )
        metadata_keys = {"scope", "provenance", "expires_at"}
        if not all(
            isinstance(values[key], str) and values[key].strip()
            for key in metadata_keys
        ):
            raise PolicyError("allow policy exception metadata must be non-empty strings")
        if requested_scope is None:
            raise PolicyError("allow policy exception requires a requested scope")
        if values["scope"] != requested_scope:
            raise PolicyError("allow policy exception scope does not match requested scope")
        try:
            expires_at = values["expires_at"].replace("Z", "+00:00")
            expiry = datetime.fromisoformat(expires_at)
        except (AttributeError, TypeError, ValueError) as exc:
            raise PolicyError("allow policy exception expiry must be ISO-8601") from exc
        if expiry.tzinfo is None:
            raise PolicyError("allow policy exception expiry must include a timezone")
        if expiry.astimezone(timezone.utc) <= datetime.now(timezone.utc):
            remote_side_effects = resolved.remote_side_effects
    if not isinstance(resolved.native_subagents_enabled, bool):
        raise PolicyError("native_subagents_enabled must be boolean")
    if not isinstance(resolved.orca_enabled, bool):
        raise PolicyError("orca_enabled must be boolean")
    return RuntimeConfig(
        native_subagents_enabled=resolved.native_subagents_enabled,
        orca_enabled=resolved.orca_enabled,
        remote_side_effects=remote_side_effects,
    )
