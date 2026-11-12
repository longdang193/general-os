"""Capability and cost profiles owned by general-os."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


class ProfileError(ValueError):
    """Raised when a profile cannot be loaded or resolved."""


@dataclass(frozen=True)
class ProfileSpec:
    name: str
    rank: int | None = None
    model: str | None = None
    provider: str | None = None
    harness: str | None = None
    effort: str | None = None
    instructions: str = ""


@dataclass(frozen=True)
class ProfileProjection:
    harness: str | None
    model: str | None
    effort: str | None
    instructions: str


def _optional_text(raw: object, field: str, path: Path) -> str | None:
    if raw is None:
        return None
    if not isinstance(raw, str) or not raw.strip():
        raise ProfileError(f"{field} must be a non-empty string: {path}")
    return raw


def load_profiles(directory: str | Path) -> dict[str, ProfileSpec]:
    profile_dir = Path(directory)
    profiles: dict[str, ProfileSpec] = {}
    if not profile_dir.is_dir():
        raise ProfileError(f"profile directory not found: {profile_dir}")
    for path in sorted(profile_dir.glob("*.toml")):
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ProfileError(f"invalid profile: {path}") from exc
        name = raw.get("name", path.stem)
        if not isinstance(name, str) or not name:
            raise ProfileError(f"profile name must be non-empty: {path}")
        unknown = set(raw) - {
            "name",
            "rank",
            "model",
            "provider",
            "harness",
            "effort",
            "instructions",
        }
        if unknown:
            raise ProfileError(f"unknown profile field: {sorted(unknown)[0]}")
        rank = raw.get("rank")
        if rank is not None and (isinstance(rank, bool) or not isinstance(rank, int)):
            raise ProfileError(f"rank must be an integer: {path}")
        provider = _optional_text(raw.get("provider"), "provider", path)
        instructions = raw.get("instructions", "")
        if not isinstance(instructions, str) or (
            "instructions" in raw and not instructions.strip()
        ):
            raise ProfileError(f"instructions must be a string: {path}")
        if name in profiles:
            raise ProfileError(f"duplicate profile: {name}")
        profiles[name] = ProfileSpec(
            name=name,
            rank=rank,
            model=_optional_text(raw.get("model"), "model", path),
            provider=provider,
            harness=_optional_text(raw.get("harness"), "harness", path),
            effort=_optional_text(raw.get("effort"), "effort", path),
            instructions=instructions,
        )
    return profiles


def resolve_profile(
    name: str | None,
    profiles: dict[str, ProfileSpec],
) -> ProfileSpec:
    requested = name or "normal"
    try:
        return profiles[requested]
    except KeyError as exc:
        raise ProfileError(f"unknown profile: {requested}") from exc


def project_profile(profile: ProfileSpec) -> ProfileProjection:
    """Project only explicit runtime facts; native runtimes own all defaults."""

    return ProfileProjection(
        harness=profile.harness,
        model=profile.model,
        effort=profile.effort,
        instructions=profile.instructions,
    )
