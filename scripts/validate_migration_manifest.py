#!/usr/bin/env python3
"""Validate the executable parts of the predecessor migration manifest."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROW_PATTERN = re.compile(r"^\| `([^`]+)` \| (.+) \|$")
DESTINATION_PATTERN = re.compile(r"`([^`]+)`")
VALID_ACTIONS = ("migrate", "fold", "retire")


@dataclass(frozen=True)
class ManifestRow:
    section: str
    source: str
    disposition: str

    @property
    def destinations(self) -> tuple[str, ...]:
        return tuple(DESTINATION_PATTERN.findall(self.disposition))


def parse_manifest(path: Path) -> tuple[ManifestRow, ...]:
    section = ""
    rows: list[ManifestRow] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Skill disposition":
            section = "skills"
        elif line == "## Rule disposition":
            section = "rules"
        elif line.startswith("## "):
            section = ""
        match = ROW_PATTERN.match(line)
        if match and section in {"skills", "rules"}:
            rows.append(ManifestRow(section, match.group(1), match.group(2)))
    return tuple(rows)


def validate_manifest(
    manifest: Path,
    repository_root: Path,
    predecessor_root: Path | None = None,
    predecessor_sha: str | None = None,
) -> tuple[ManifestRow, ...]:
    rows = parse_manifest(manifest)
    errors: list[str] = []
    if len({(row.section, row.source) for row in rows}) != len(rows):
        errors.append("manifest contains duplicate source rows")
    for row in rows:
        if not row.disposition.startswith(VALID_ACTIONS):
            errors.append(f"invalid disposition for {row.source}: {row.disposition}")
        for destination in row.destinations:
            target = repository_root / destination.rstrip("/")
            if not target.exists():
                errors.append(f"missing destination for {row.source}: {destination}")
        if row.disposition.startswith("retire") and row.destinations:
            errors.append(f"retired row has an active destination: {row.source}")

    active_rules = {
        destination.rstrip("/")
        for row in rows
        if row.section == "rules" and row.disposition.startswith("migrate")
        for destination in row.destinations
        if destination.startswith("docs/rules/")
    }
    actual_rules = {
        path.relative_to(repository_root).as_posix()
        for path in (repository_root / "docs" / "rules").glob("*")
        if path.is_file()
    }
    if active_rules != actual_rules:
        errors.append(
            f"active rule set mismatch: manifest={sorted(active_rules)} "
            f"tree={sorted(actual_rules)}"
        )

    if predecessor_root is not None:
        if not predecessor_sha or not re.fullmatch(r"[0-9a-f]{40}", predecessor_sha):
            errors.append("predecessor SHA must be a full 40-character lowercase SHA")
        else:
            try:
                actual_sha = subprocess.run(
                    ["git", "-C", str(predecessor_root), "rev-parse", "HEAD"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
            except (OSError, subprocess.CalledProcessError) as exc:
                errors.append(f"cannot resolve predecessor HEAD: {exc}")
            else:
                if actual_sha != predecessor_sha:
                    errors.append(
                        f"predecessor HEAD mismatch: expected {predecessor_sha}, got {actual_sha}"
                    )
            dirty = subprocess.run(
                ["git", "-C", str(predecessor_root), "status", "--porcelain"],
                check=False,
                capture_output=True,
                text=True,
            ).stdout.strip()
            if dirty:
                errors.append("predecessor checkout is dirty")
        for row in rows:
            source_path = (
                predecessor_root
                / ".agents"
                / ("skills" if row.section == "skills" else "rules")
                / row.source
                / "SKILL.md"
                if row.section == "skills"
                else predecessor_root / ".agents" / "rules" / row.source
            )
            if not source_path.is_file():
                errors.append(f"missing predecessor source: {source_path}")

    if errors:
        raise ValueError("\n".join(errors))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--predecessor-root", type=Path)
    parser.add_argument("--predecessor-sha")
    parser.add_argument("--repository-root", type=Path)
    args = parser.parse_args(argv)
    manifest = args.manifest.resolve()
    repository_root = (args.repository_root or manifest.parents[2]).resolve()
    try:
        rows = validate_manifest(
            manifest,
            repository_root,
            args.predecessor_root.resolve() if args.predecessor_root else None,
            args.predecessor_sha,
        )
    except (OSError, ValueError) as exc:
        print(f"migration manifest invalid: {exc}", file=sys.stderr)
        return 1
    print(f"valid: {len(rows)} manifest rows; repository={repository_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
