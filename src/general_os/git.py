"""Direct observations of repository state through Git."""

from __future__ import annotations

import subprocess
import hashlib
import os
from dataclasses import dataclass
from pathlib import Path


class GitError(RuntimeError):
    """Raised when the repository cannot be inspected."""


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    revision: str | None
    changed_files: tuple[str, ...]
    conflicts: tuple[str, ...]
    clean: bool
    identity: str | None = None


class GitRepository:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _run_bytes(self, *args: str) -> bytes:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.root,
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            raise GitError(f"Git command failed in {self.root}: {' '.join(args)}") from exc
        return result.stdout

    def _run(self, *args: str) -> str:
        return self._run_bytes(*args).decode("utf-8", errors="surrogateescape").strip()

    def inspect(self) -> GitSnapshot:
        branch = self._run("branch", "--show-current") or "HEAD"
        status = self._run("status", "--porcelain=v1", "--untracked-files=all")
        changed_files: list[str] = []
        conflicts: list[str] = []
        conflict_codes = {"AA", "AU", "DD", "DU", "UA", "UD", "UU"}
        for line in status.splitlines():
            if len(line) < 3:
                continue
            code = line[:2]
            path = line[3:]
            if " -> " in path:
                path = path.rsplit(" -> ", 1)[1]
            changed_files.append(path)
            if code in conflict_codes:
                conflicts.append(path)
        try:
            revision = self._run("rev-parse", "--verify", "HEAD")
        except GitError:
            revision = None
        changed = tuple(dict.fromkeys(changed_files))
        conflict_paths = tuple(dict.fromkeys(conflicts))
        identity = self._identity(branch, revision, status)
        return GitSnapshot(
            branch=branch,
            revision=revision,
            changed_files=changed,
            conflicts=conflict_paths,
            clean=not changed and not conflict_paths,
            identity=identity,
        )

    def _identity(
        self,
        branch: str,
        revision: str | None,
        status: str,
    ) -> str:
        digest = hashlib.sha256()
        for value in (branch, revision or "", status):
            digest.update(value.encode("utf-8"))
            digest.update(b"\0")
        if revision is None:
            tracked_diff = self._run_bytes("diff", "--cached", "--binary")
            tracked_diff += b"\0" + self._run_bytes("diff", "--binary")
        else:
            tracked_diff = self._run_bytes("diff", "HEAD", "--binary")
        digest.update(tracked_diff)
        digest.update(b"\0")
        untracked_status = self._run_bytes(
            "status", "--porcelain=v1", "--untracked-files=all", "-z"
        )
        untracked = [
            os.fsdecode(record[3:])
            for record in untracked_status.split(b"\0")
            if record.startswith(b"?? ")
        ]
        for path in sorted(untracked):
            candidate = self.root / path
            if candidate.is_file():
                digest.update(os.fsencode(path))
                digest.update(b"\0")
                digest.update(candidate.read_bytes())
                digest.update(b"\0")
        return digest.hexdigest()


def inspect_git(root: str | Path) -> GitSnapshot:
    return GitRepository(root).inspect()
