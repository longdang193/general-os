"""Central General OS installation and seed-only project adoption."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = 1
SUPPORTED_ADAPTERS = frozenset({"codex"})
CENTRAL_DIRNAME = "general-os"
PACKAGE_ASSETS = Path(__file__).resolve().parent / "assets"
SKILL_SOURCE = Path(".agents") / "skills"
CENTRAL_DOCS = Path("docs")
CENTRAL_LOCK = Path("managed.json")
PROJECT_LOCK = Path("repo_config") / "general-os.lock.json"
PROJECT_SEEDS = (
    Path("AGENTS.md"),
    Path("agents") / "high.toml",
    Path("agents") / "low.toml",
    Path("agents") / "normal.toml",
    Path("agents") / "xhigh.toml",
    Path("repo_config") / "runtime-policy.toml",
)


class DeploymentError(ValueError):
    """Raised when a deployment contract is invalid or cannot be applied."""


@dataclass(frozen=True)
class Action:
    kind: str
    path: str
    reason: str

    def as_dict(self) -> dict[str, str]:
        return {"kind": self.kind, "path": self.path, "reason": self.reason}


@dataclass(frozen=True)
class DeploymentPlan:
    source_root: Path
    repo_root: Path | None
    central_root: Path
    adapter: str
    actions: tuple[Action, ...]
    warnings: tuple[str, ...]
    residue: tuple[str, ...]
    source_revision: str
    manifest_digest: str
    central_lock: dict[str, object]
    project_lock: dict[str, object]

    @property
    def pending(self) -> bool:
        return any(action.kind in {"create", "update", "adopt", "remove"} for action in self.actions)

    @property
    def conflicts(self) -> bool:
        return any(
            action.kind in {"preserve", "invalid"}
            and action.path.startswith(("skills/", "docs/"))
            for action in self.actions
        )

    def as_dict(self, *, status: str) -> dict[str, object]:
        return {
            "status": status,
            "adapter": self.adapter,
            "source_root": str(self.source_root),
            "repo_root": str(self.repo_root) if self.repo_root is not None else None,
            "central_root": str(self.central_root),
            "source_revision": self.source_revision,
            "manifest_digest": self.manifest_digest,
            "actions": [action.as_dict() for action in self.actions],
            "warnings": list(self.warnings),
            "residue": list(self.residue),
            "managed_files": self.central_lock["managed_files"],
            "seeded_paths": self.project_lock.get("seeded_paths", []),
        }


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _safe_relative(path: str, root: Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise DeploymentError(f"unsafe managed path: {path}")
    resolved_root = root.resolve()
    resolved_candidate = (root / candidate).resolve()
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise DeploymentError(f"unsafe managed path: {path}") from exc
    return candidate


def _read_json(path: Path, *, label: str) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentError(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise DeploymentError(f"invalid {label}: {path}")
    return value


def _load_central_lock(path: Path) -> dict[str, object]:
    if not path.exists():
        return {
            "schema_version": SCHEMA_VERSION,
            "source": "general-os",
            "source_revision": "",
            "manifest_digest": "",
            "adapters": [],
            "managed_files": {},
        }
    value = _read_json(path, label="central deployment lock")
    if value.get("schema_version") != SCHEMA_VERSION:
        raise DeploymentError(f"unsupported central lock schema: {path}")
    managed = value.get("managed_files")
    if not isinstance(managed, dict) or not all(
        isinstance(key, str) and isinstance(digest, str) and len(digest) == 64
        for key, digest in managed.items()
    ):
        raise DeploymentError(f"invalid managed_files in central lock: {path}")
    for key in managed:
        _safe_relative(key, path.parent)
    return value


def _load_project_lock(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    value = _read_json(path, label="project adoption record")
    expected = {"schema_version", "adopted_from", "adopted_revision", "seeded_paths"}
    if set(value) != expected or value.get("schema_version") != SCHEMA_VERSION:
        raise DeploymentError(f"invalid project adoption record: {path}")
    if value.get("adopted_from") != "general-os" or not isinstance(
        value.get("adopted_revision"), str
    ):
        raise DeploymentError(f"invalid project adoption record: {path}")
    paths = value.get("seeded_paths")
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        raise DeploymentError(f"invalid project adoption record: {path}")
    return value


def _source_revision(source_root: Path) -> str:
    if source_root.resolve() == PACKAGE_ASSETS.resolve():
        from general_os import __version__

        return f"package-{__version__}"
    try:
        return subprocess.run(
            ["git", "-C", str(source_root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "working-tree"


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return ()
    return (path for path in sorted(root.rglob("*")) if path.is_file())


def _skill_root(source_root: Path) -> Path:
    packaged = source_root / "skills"
    if packaged.is_dir():
        return packaged
    return source_root / SKILL_SOURCE


def _project_root(source_root: Path) -> Path:
    packaged = source_root / "project-kit"
    if packaged.is_dir():
        return packaged
    return source_root


def _central_sources(source_root: Path) -> dict[str, bytes]:
    sources: dict[str, bytes] = {}
    skill_root = _skill_root(source_root)
    for path in _iter_files(skill_root):
        relative = path.relative_to(skill_root).as_posix()
        sources[f"skills/{relative}"] = path.read_bytes()
    for relative_root in (Path("docs") / "rules", Path("docs") / "templates"):
        for path in _iter_files(source_root / relative_root):
            relative = path.relative_to(source_root).as_posix()
            sources[relative] = path.read_bytes()
    adapters = source_root / "docs" / "runtime-adapters.md"
    if adapters.is_file():
        sources["docs/runtime-adapters.md"] = adapters.read_bytes()
    if not sources:
        raise DeploymentError(f"central source tree is empty: {source_root}")
    return sources


def _rewrite_skill_references(data: bytes, central_root: Path) -> bytes:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    docs_root = (central_root / CENTRAL_DOCS).as_posix()
    for old, new in (
        ("docs/runtime-adapters.md", f"{docs_root}/runtime-adapters.md"),
        ("docs/rules/", f"{docs_root}/rules/"),
    ):
        text = text.replace(old, new)
    return text.encode("utf-8")


def _staged_sources(source_root: Path, central_root: Path) -> dict[str, bytes]:
    sources = _central_sources(source_root)
    return {
        relative: (
            _rewrite_skill_references(data, central_root)
            if relative.startswith("skills/")
            else data
        )
        for relative, data in sources.items()
    }


def _manifest_digest(sources: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(sources):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sources[relative])
        digest.update(b"\0")
    return digest.hexdigest()


def _residue(repo_root: Path) -> tuple[str, ...]:
    found: list[str] = []
    legacy_rules = repo_root / ".agents" / "rules"
    if legacy_rules.exists():
        found.append(legacy_rules.relative_to(repo_root).as_posix())
    skill_root = repo_root / ".agents" / "skills"
    if skill_root.is_dir():
        found.extend(
            path.relative_to(repo_root).as_posix()
            for path in sorted(skill_root.iterdir())
            if path.name.startswith("skill-")
        )
    return tuple(found)


def _project_sources(source_root: Path) -> dict[Path, bytes]:
    sources: dict[Path, bytes] = {}
    project_root = _project_root(source_root)
    for relative in PROJECT_SEEDS:
        source = project_root / relative
        if source.is_file():
            sources[relative] = source.read_bytes()
    return sources


def _project_lock_value(
    existing: dict[str, object] | None,
    source_revision: str,
    seeded_paths: Iterable[str],
) -> dict[str, object]:
    if existing is not None:
        return existing
    return {
        "schema_version": SCHEMA_VERSION,
        "adopted_from": "general-os",
        "adopted_revision": source_revision,
        "seeded_paths": sorted(set(seeded_paths)),
    }


def _action_for_current(
    relative: str,
    destination: Path,
    desired: bytes,
    prior_digest: str | None,
) -> Action:
    if not destination.exists():
        return Action("create", relative, "destination absent")
    current = destination.read_bytes()
    current_digest = _digest(current)
    desired_digest = _digest(desired)
    if current_digest == desired_digest:
        if prior_digest is None:
            return Action("adopt", relative, "byte-identical unmarked file adopted")
        return Action("unchanged", relative, "already matches desired content")
    if prior_digest and current_digest == prior_digest:
        return Action("update", relative, "centrally managed content changed upstream")
    return Action(
        "preserve",
        relative,
        "existing content is not centrally owned or was locally modified",
    )


def build_plan(
    repo_root: str | Path | None = None,
    *,
    adapter: str = "codex",
    home: str | Path | None = None,
    source_root: str | Path | None = None,
    prune: bool = False,
    adopt: bool = False,
) -> DeploymentPlan:
    if adapter not in SUPPORTED_ADAPTERS:
        raise DeploymentError(f"unsupported adapter: {adapter}")
    if adopt and repo_root is None:
        raise DeploymentError("project adoption requires --repo")
    if repo_root is not None and not adopt:
        raise DeploymentError("project adoption requires adopt=True")
    repo = Path(repo_root).resolve() if repo_root is not None else None
    source = Path(source_root).resolve() if source_root else PACKAGE_ASSETS.resolve()
    central = (Path(home).expanduser() if home is not None else Path.home()) / ".agents" / CENTRAL_DIRNAME
    central = central.resolve()
    central_sources = _staged_sources(source, central)
    source_revision = _source_revision(source)
    manifest_digest = _manifest_digest(central_sources)
    old_lock = _load_central_lock(central / CENTRAL_LOCK)
    old_managed = old_lock["managed_files"]
    assert isinstance(old_managed, dict)
    actions: list[Action] = []
    next_managed: dict[str, str] = {}
    for relative, desired in sorted(central_sources.items()):
        destination = central / relative
        prior = old_managed.get(relative)
        action = _action_for_current(relative, destination, desired, prior)
        actions.append(action)
        if action.kind in {"create", "update", "adopt", "unchanged"}:
            next_managed[relative] = _digest(desired)
        elif isinstance(prior, str):
            next_managed[relative] = prior

    desired_paths = set(central_sources)
    for relative, prior in sorted(old_managed.items()):
        if relative in desired_paths or not prune:
            continue
        destination = central / _safe_relative(relative, central)
        if not destination.exists():
            actions.append(Action("remove", relative, "owned file is already absent"))
            continue
        if destination.is_file() and _digest(destination.read_bytes()) == prior:
            actions.append(Action("remove", relative, "owned file is no longer in source manifest"))
            continue
        actions.append(Action("preserve", relative, "prune skipped modified or missing file"))
        next_managed[relative] = prior

    project_lock: dict[str, object] = {"seeded_paths": []}
    if adopt:
        assert repo is not None
        existing_project_lock = _load_project_lock(repo / PROJECT_LOCK)
        project_sources = _project_sources(source)
        seeded_paths: set[str] = set()
        if existing_project_lock is None:
            for relative, desired in sorted(project_sources.items()):
                destination = repo / relative
                if not destination.exists():
                    actions.append(Action("create", relative.as_posix(), "project semantic seed absent"))
                    seeded_paths.add(relative.as_posix())
                elif destination.read_bytes() == desired:
                    actions.append(Action("unchanged", relative.as_posix(), "project semantic already present"))
                else:
                    actions.append(Action("preserve", relative.as_posix(), "existing project semantic preserved"))
            project_lock = _project_lock_value(existing_project_lock, source_revision, seeded_paths)
            project_lock_path = repo / PROJECT_LOCK
            project_lock_bytes = _json_bytes(project_lock)
            if not project_lock_path.exists():
                actions.append(Action("create", PROJECT_LOCK.as_posix(), "project adoption record absent"))
            elif project_lock_path.read_bytes() != project_lock_bytes:
                actions.append(Action("update", PROJECT_LOCK.as_posix(), "adoption record gains seed provenance"))
            else:
                actions.append(Action("unchanged", PROJECT_LOCK.as_posix(), "adoption record already matches"))
        else:
            project_lock = existing_project_lock

    central_lock = {
        "schema_version": SCHEMA_VERSION,
        "source": "general-os",
        "source_revision": source_revision,
        "manifest_digest": manifest_digest,
        "adapters": [adapter],
        "managed_files": dict(sorted(next_managed.items())),
    }
    central_lock_path = central / CENTRAL_LOCK
    central_lock_bytes = _json_bytes(central_lock)
    if not central_lock_path.exists():
        actions.append(Action("create", str(CENTRAL_LOCK), "central deployment lock absent"))
    elif central_lock_path.read_bytes() != central_lock_bytes:
        actions.append(Action("update", str(CENTRAL_LOCK), "central provenance changed"))
    else:
        actions.append(Action("unchanged", str(CENTRAL_LOCK), "central provenance already matches"))

    residue = _residue(repo) if repo is not None else ()
    warnings = tuple(
        [f"predecessor residue: {item}" for item in residue]
        + [
            f"preserved existing project file: {action.path}"
            for action in actions
            if action.kind == "preserve" and action.path in {item.as_posix() for item in PROJECT_SEEDS}
        ]
    )
    return DeploymentPlan(
        source_root=source,
        repo_root=repo,
        central_root=central,
        adapter=adapter,
        actions=tuple(actions),
        warnings=warnings,
        residue=residue,
        source_revision=source_revision,
        manifest_digest=manifest_digest,
        central_lock=central_lock,
        project_lock=project_lock,
    )


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temporary = handle.name
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass


def _restore(path: Path, data: bytes | None) -> None:
    if data is None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    else:
        _atomic_write(path, data)


def apply_plan(plan: DeploymentPlan) -> None:
    central_sources = _staged_sources(plan.source_root, plan.central_root)
    project_sources = _project_sources(plan.source_root) if plan.repo_root is not None else {}
    central_paths = set(central_sources) | set(plan.central_lock["managed_files"])
    targets: dict[Path, bytes | None] = {}
    for action in plan.actions:
        if action.kind not in {"create", "update", "remove"}:
            continue
        if action.path in central_paths or action.path.startswith(("skills/", "docs/")):
            target = plan.central_root / _safe_relative(action.path, plan.central_root)
            data = central_sources.get(action.path)
        elif action.path == str(CENTRAL_LOCK):
            target = plan.central_root / CENTRAL_LOCK
            data = _json_bytes(plan.central_lock)
        elif action.path == PROJECT_LOCK.as_posix():
            assert plan.repo_root is not None
            target = plan.repo_root / PROJECT_LOCK
            data = _json_bytes(plan.project_lock)
        else:
            relative = _safe_relative(action.path, plan.repo_root)
            assert plan.repo_root is not None
            target = plan.repo_root / relative
            data = project_sources.get(relative)
            if action.kind != "remove" and data is None:
                raise DeploymentError(f"missing project seed source: {relative}")
        targets[target] = None if action.kind == "remove" else data

    backups = {target: target.read_bytes() if target.is_file() else None for target in targets}
    lock_target = plan.central_root / CENTRAL_LOCK
    ordered = [target for target in targets if target != lock_target]
    if lock_target in targets:
        ordered.append(lock_target)
    try:
        for target in ordered:
            _restore(target, targets[target])
    except (OSError, ValueError) as exc:
        try:
            for target, data in backups.items():
                _restore(target, data)
        except OSError as rollback_error:
            raise DeploymentError(f"deployment failed and rollback failed: {rollback_error}") from exc
        raise DeploymentError(f"deployment rolled back: {exc}") from exc


def deploy(
    repo_root: str | Path | None = None,
    *,
    adapter: str = "codex",
    home: str | Path | None = None,
    source_root: str | Path | None = None,
    dry_run: bool = False,
    check: bool = False,
    prune: bool = False,
    strict_migration: bool = False,
    adopt: bool = False,
) -> tuple[int, dict[str, object]]:
    if dry_run and check:
        raise DeploymentError("--dry-run and --check are mutually exclusive")
    plan = build_plan(
        repo_root,
        adapter=adapter,
        home=home,
        source_root=source_root,
        prune=prune,
        adopt=adopt,
    )
    if dry_run:
        return (1 if strict_migration and plan.residue else 0, plan.as_dict(status="dry-run"))
    if check:
        healthy = not plan.pending and not plan.conflicts
        if strict_migration and plan.residue:
            healthy = False
        return (0 if healthy else 1, plan.as_dict(status="healthy" if healthy else "drift"))
    apply_plan(plan)
    status = "applied" if plan.pending else "unchanged"
    return (1 if strict_migration and plan.residue else 0, plan.as_dict(status=status))
