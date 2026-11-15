"""Central General OS installation and seed-only project adoption."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import subprocess
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCHEMA_VERSION = 1
SUPPORTED_ADAPTERS = frozenset({"codex"})
DEPLOYMENT_LOCK_TIMEOUT_SECONDS = 10.0
DEPLOYMENT_LOCK_RETRY_SECONDS = 0.05
CENTRAL_DIRNAME = "general-os"
PACKAGE_ASSETS = Path(__file__).resolve().parent / "assets"
SKILL_SOURCE = Path(".agents") / "skills"
CENTRAL_DOCS = Path("docs")
CENTRAL_LOCK = Path("managed.json")
PROJECT_LOCK = Path("repo_config") / "general-os.lock.json"
PROJECT_SEEDS = (
    Path("AGENTS.md"),
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
    skill_root: Path
    adapter: str
    actions: tuple[Action, ...]
    warnings: tuple[str, ...]
    residue: tuple[str, ...]
    source_revision: str
    manifest_digest: str
    source_snapshot_digest: str
    central_lock: dict[str, object]
    project_lock: dict[str, object]
    target_preconditions: dict[str, str | None]

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
            "skill_root": str(self.skill_root),
            "source_revision": self.source_revision,
            "manifest_digest": self.manifest_digest,
            "source_snapshot_digest": self.source_snapshot_digest,
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


def _read_json_bytes(source: bytes, path: Path, *, label: str) -> dict[str, object]:
    try:
        value = json.loads(source)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DeploymentError(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise DeploymentError(f"invalid {label}: {path}")
    return value


def _read_json(path: Path, *, label: str) -> dict[str, object]:
    try:
        source = path.read_bytes()
    except OSError as exc:
        raise DeploymentError(f"invalid {label}: {path}") from exc
    return _read_json_bytes(source, path, label=label)


def _load_central_lock(path: Path) -> tuple[dict[str, object], bytes | None]:
    if not path.exists():
        return (
            {
                "schema_version": SCHEMA_VERSION,
                "source": "general-os",
                "source_revision": "",
                "manifest_digest": "",
                "adapters": [],
                "managed_files": {},
            },
            None,
        )
    try:
        source = path.read_bytes()
    except OSError as exc:
        raise DeploymentError(f"invalid central deployment lock: {path}") from exc
    value = _read_json_bytes(source, path, label="central deployment lock")
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
    return value, source


def _load_project_lock(path: Path) -> tuple[dict[str, object] | None, bytes | None]:
    if not path.exists():
        return None, None
    try:
        source = path.read_bytes()
    except OSError as exc:
        raise DeploymentError(f"invalid project adoption record: {path}") from exc
    value = _read_json_bytes(source, path, label="project adoption record")
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
    return value, source


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


def _central_destination(relative: str, central_root: Path) -> Path:
    """Resolve managed files to the runtime discovery or provenance tree."""
    if relative == "skills" or relative.startswith("skills/"):
        return central_root.parent / _safe_relative(relative, central_root.parent)
    return central_root / _safe_relative(relative, central_root)


def _manifest_digest(sources: dict[str, bytes]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(sources):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sources[relative])
        digest.update(b"\0")
    return digest.hexdigest()


def _source_snapshot_digest(
    central_sources: dict[str, bytes], project_sources: dict[Path, bytes]
) -> str:
    sources = {f"central/{path}": data for path, data in central_sources.items()}
    sources.update({f"project/{path.as_posix()}": data for path, data in project_sources.items()})
    return _manifest_digest(sources)


def _target_bytes(path: Path) -> bytes | None:
    if not path.exists():
        return None
    if not path.is_file():
        raise DeploymentError(f"deployment target is not a file: {path}")
    return path.read_bytes()


def _target_for_action(
    action: Action,
    *,
    central_sources: dict[str, bytes],
    project_sources: dict[Path, bytes],
    central_lock: dict[str, object],
    project_lock: dict[str, object],
    central_root: Path,
    repo_root: Path | None,
) -> tuple[Path, bytes | None]:
    central_paths = set(central_sources) | set(central_lock["managed_files"])
    if action.path in central_paths or action.path.startswith(("skills/", "docs/")):
        target = _central_destination(action.path, central_root)
        data = central_sources.get(action.path)
    elif action.path == str(CENTRAL_LOCK):
        target = central_root / CENTRAL_LOCK
        data = _json_bytes(central_lock)
    elif action.path == PROJECT_LOCK.as_posix():
        if repo_root is None:
            raise DeploymentError("project adoption target has no repository root")
        target = repo_root / PROJECT_LOCK
        data = _json_bytes(project_lock)
    else:
        if repo_root is None:
            raise DeploymentError(f"project target has no repository root: {action.path}")
        relative = _safe_relative(action.path, repo_root)
        target = repo_root / relative
        data = project_sources.get(relative)
        if action.kind != "remove" and data is None:
            raise DeploymentError(f"missing project seed source: {relative}")
    return target, None if action.kind == "remove" else data


@contextmanager
def _deployment_lock(central_root: Path):
    lock_name = hashlib.sha256(str(central_root.resolve()).encode("utf-8")).hexdigest()
    lock_path = Path(tempfile.gettempdir()) / f"general-os-deployment-{lock_name}.lock"
    with lock_path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            lock = lambda: msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            lock = lambda: fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        deadline = time.monotonic() + DEPLOYMENT_LOCK_TIMEOUT_SECONDS
        while True:
            try:
                lock()
                break
            except OSError as exc:
                contention = isinstance(exc, BlockingIOError) or (
                    os.name == "nt"
                    and exc.errno in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}
                )
                if not contention:
                    raise DeploymentError(f"deployment lock failed: {lock_path}") from exc
                if time.monotonic() >= deadline:
                    raise DeploymentError(f"deployment lock unavailable: {lock_path}") from exc
                time.sleep(DEPLOYMENT_LOCK_RETRY_SECONDS)
        try:
            yield
        finally:
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


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
    seed_paths = PROJECT_SEEDS + tuple(
        path.relative_to(project_root)
        for path in sorted((project_root / "agents").glob("*.toml"))
        if path.is_file()
    )
    for relative in seed_paths:
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
) -> tuple[Action, bytes | None]:
    if not destination.exists():
        return Action("create", relative, "destination absent"), None
    current = destination.read_bytes()
    current_digest = _digest(current)
    desired_digest = _digest(desired)
    if current_digest == desired_digest:
        if prior_digest is None:
            return Action("adopt", relative, "byte-identical unmarked file adopted"), current
        return Action("unchanged", relative, "already matches desired content"), current
    if prior_digest and current_digest == prior_digest:
        return Action("update", relative, "centrally managed content changed upstream"), current
    return (
        Action(
            "preserve",
            relative,
            "existing content is not centrally owned or was locally modified",
        ),
        current,
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
    skill_root = central.parent / "skills"
    central_sources = _staged_sources(source, central)
    source_revision = _source_revision(source)
    manifest_digest = _manifest_digest(central_sources)
    central_lock_path = central / CENTRAL_LOCK
    old_lock, old_lock_bytes = _load_central_lock(central_lock_path)
    old_managed = old_lock["managed_files"]
    assert isinstance(old_managed, dict)
    actions: list[Action] = []
    next_managed: dict[str, str] = {}
    target_preconditions: dict[str, str | None] = {}
    for relative, desired in sorted(central_sources.items()):
        destination = _central_destination(relative, central)
        prior = old_managed.get(relative)
        action, current = _action_for_current(relative, destination, desired, prior)
        actions.append(action)
        if action.kind in {"create", "update"}:
            target_preconditions[str(destination)] = _digest(current) if current is not None else None
        if action.kind in {"create", "update", "adopt", "unchanged"}:
            next_managed[relative] = _digest(desired)
        elif isinstance(prior, str):
            next_managed[relative] = prior

    desired_paths = set(central_sources)
    for relative, prior in sorted(old_managed.items()):
        if relative in desired_paths or not prune:
            continue
        destination = _central_destination(relative, central)
        if not destination.exists():
            actions.append(Action("remove", relative, "owned file is already absent"))
            target_preconditions[str(destination)] = None
            continue
        if destination.is_file():
            current = destination.read_bytes()
        else:
            current = None
        if current is not None and _digest(current) == prior:
            actions.append(Action("remove", relative, "owned file is no longer in source manifest"))
            target_preconditions[str(destination)] = _digest(current)
            continue
        actions.append(Action("preserve", relative, "prune skipped modified or missing file"))
        next_managed[relative] = prior

    project_lock: dict[str, object] = {"seeded_paths": []}
    project_sources: dict[Path, bytes] = {}
    project_seed_paths: set[Path] = set()
    if adopt:
        assert repo is not None
        project_lock_path = repo / PROJECT_LOCK
        existing_project_lock, existing_project_lock_bytes = _load_project_lock(project_lock_path)
        project_sources = _project_sources(source)
        project_seed_paths = set(project_sources)
        seeded_paths: set[str] = set()
        if existing_project_lock is None:
            for relative, desired in sorted(project_sources.items()):
                destination = repo / relative
                if not destination.exists():
                    actions.append(Action("create", relative.as_posix(), "project semantic seed absent"))
                    target_preconditions[str(destination)] = None
                    seeded_paths.add(relative.as_posix())
                else:
                    current = destination.read_bytes()
                    if current == desired:
                        actions.append(Action("unchanged", relative.as_posix(), "project semantic already present"))
                    else:
                        actions.append(Action("preserve", relative.as_posix(), "existing project semantic preserved"))
            project_lock = _project_lock_value(existing_project_lock, source_revision, seeded_paths)
            project_lock_bytes = _json_bytes(project_lock)
            if existing_project_lock_bytes is None:
                actions.append(Action("create", PROJECT_LOCK.as_posix(), "project adoption record absent"))
            else:
                if existing_project_lock_bytes != project_lock_bytes:
                    actions.append(Action("update", PROJECT_LOCK.as_posix(), "adoption record gains seed provenance"))
                else:
                    actions.append(Action("unchanged", PROJECT_LOCK.as_posix(), "adoption record already matches"))
            if actions[-1].kind in {"create", "update"}:
                target_preconditions[str(project_lock_path)] = (
                    _digest(existing_project_lock_bytes)
                    if existing_project_lock_bytes is not None
                    else None
                )
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
    central_lock_bytes = _json_bytes(central_lock)
    if old_lock_bytes is None:
        actions.append(Action("create", str(CENTRAL_LOCK), "central deployment lock absent"))
    else:
        if old_lock_bytes != central_lock_bytes:
            actions.append(Action("update", str(CENTRAL_LOCK), "central provenance changed"))
        else:
            actions.append(Action("unchanged", str(CENTRAL_LOCK), "central provenance already matches"))
    if actions[-1].kind in {"create", "update"}:
        target_preconditions[str(central_lock_path)] = (
            _digest(old_lock_bytes) if old_lock_bytes is not None else None
        )

    residue = _residue(repo) if repo is not None else ()
    warnings = tuple(
        [f"predecessor residue: {item}" for item in residue]
        + [
            f"preserved existing project file: {action.path}"
            for action in actions
            if action.kind == "preserve" and action.path in {item.as_posix() for item in project_seed_paths}
        ]
    )
    return DeploymentPlan(
        source_root=source,
        repo_root=repo,
        central_root=central,
        skill_root=skill_root,
        adapter=adapter,
        actions=tuple(actions),
        warnings=warnings,
        residue=residue,
        source_revision=source_revision,
        manifest_digest=manifest_digest,
        source_snapshot_digest=_source_snapshot_digest(central_sources, project_sources),
        central_lock=central_lock,
        project_lock=project_lock,
        target_preconditions=target_preconditions,
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
    with _deployment_lock(plan.central_root):
        central_sources = _staged_sources(plan.source_root, plan.central_root)
        project_sources = _project_sources(plan.source_root) if plan.repo_root is not None else {}
        if _source_snapshot_digest(central_sources, project_sources) != plan.source_snapshot_digest:
            raise DeploymentError("stale deployment plan: source changed")

        targets: dict[Path, bytes | None] = {}
        for action in plan.actions:
            if action.kind not in {"create", "update", "remove"}:
                continue
            target, data = _target_for_action(
                action,
                central_sources=central_sources,
                project_sources=project_sources,
                central_lock=plan.central_lock,
                project_lock=plan.project_lock,
                central_root=plan.central_root,
                repo_root=plan.repo_root,
            )
            targets[target] = data

        for target, expected_digest in plan.target_preconditions.items():
            current = _target_bytes(Path(target))
            current_digest = _digest(current) if current is not None else None
            if current_digest != expected_digest:
                raise DeploymentError(f"stale deployment plan: target changed: {target}")

        backups = {target: _target_bytes(target) for target in targets}
        lock_target = plan.central_root / CENTRAL_LOCK
        ordered = [target for target in targets if target != lock_target]
        if lock_target in targets:
            ordered.append(lock_target)
        written: set[Path] = set()
        try:
            for target in ordered:
                expected_digest = plan.target_preconditions.get(str(target))
                current = _target_bytes(target)
                current_digest = _digest(current) if current is not None else None
                if current_digest != expected_digest:
                    raise DeploymentError(f"stale deployment plan: target changed: {target}")
                _restore(target, targets[target])
                written.add(target)
        except (OSError, ValueError) as exc:
            conflicts: list[str] = []
            try:
                for target in reversed(ordered):
                    if target not in written:
                        continue
                    try:
                        current = _target_bytes(target)
                    except (OSError, DeploymentError):
                        conflicts.append(str(target))
                        continue
                    if current != targets[target]:
                        conflicts.append(str(target))
                        continue
                    _restore(target, backups[target])
            except OSError as rollback_error:
                raise DeploymentError(f"deployment failed and rollback failed: {rollback_error}") from exc
            if conflicts:
                raise DeploymentError(
                    "deployment rolled back with rollback conflicts: "
                    + ", ".join(conflicts)
                ) from exc
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
