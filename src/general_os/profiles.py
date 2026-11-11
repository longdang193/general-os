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
    instructions: str = ""


def load_profiles(directory: str | Path) -> dict[str, ProfileSpec]:
    profile_dir = Path(directory)
    profiles: dict[str, ProfileSpec] = {}
    if not profile_dir.exists():
        return profiles
    for path in sorted(profile_dir.glob("*.toml")):
        try:
            raw = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            raise ProfileError(f"invalid profile: {path}") from exc
        name = raw.get("name", path.stem)
        if not isinstance(name, str) or not name:
            raise ProfileError(f"profile name must be non-empty: {path}")
        if name in profiles:
            raise ProfileError(f"duplicate profile: {name}")
        profiles[name] = ProfileSpec(
            name=name,
            rank=raw.get("rank"),
            model=raw.get("model"),
            provider=raw.get("provider"),
            instructions=raw.get("instructions", ""),
        )
    return profiles


def resolve_profile(
    name: str | None,
    profiles: dict[str, ProfileSpec],
) -> ProfileSpec:
    requested = name or "normal"
    if not profiles and requested == "normal":
        return ProfileSpec(name="normal")
    try:
        return profiles[requested]
    except KeyError as exc:
        raise ProfileError(f"unknown profile: {requested}") from exc
