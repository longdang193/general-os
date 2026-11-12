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
    _COORDINATION_STATE = "state/coordination.json"

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
        status_bytes = self._run_bytes(
            "status", "--porcelain=v1", "--untracked-files=all", "-z"
        )
        changed_files: list[str] = []
        conflicts: list[str] = []
        conflict_codes = {"AA", "AU", "DD", "DU", "UA", "UD", "UU"}
        records = self._status_records(status_bytes)
        for code, path in records:
            changed_files.append(path)
            if code in conflict_codes:
                conflicts.append(path)
        try:
            revision = self._run("rev-parse", "--verify", "HEAD")
        except GitError:
            revision = None
        changed = tuple(dict.fromkeys(changed_files))
        conflict_paths = tuple(dict.fromkeys(conflicts))
        identity = self._identity(branch, revision, records)
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
        status: tuple[tuple[str, str], ...],
    ) -> str:
        digest = hashlib.sha256()
        repository_root = self._run("rev-parse", "--show-toplevel")
        common_dir = self._run("rev-parse", "--git-common-dir")
        for value in (
            str(Path(repository_root).resolve()),
            str((self.root / common_dir).resolve()),
            branch,
            revision or "",
        ):
            digest.update(value.encode("utf-8"))
            digest.update(b"\0")
        for code, path in status:
            if self._is_coordination_state(path):
                continue
            digest.update(code.encode("ascii"))
            digest.update(b"\0")
            digest.update(os.fsencode(path))
            digest.update(b"\0")
        pathspec = (".", f":(exclude){self._COORDINATION_STATE}")
        if revision is None:
            staged_diff = self._run_bytes("diff", "--cached", "--binary", "--", *pathspec)
            unstaged_diff = self._run_bytes("diff", "--binary", "--", *pathspec)
        else:
            staged_diff = self._run_bytes("diff", "HEAD", "--cached", "--binary", "--", *pathspec)
            unstaged_diff = self._run_bytes("diff", "HEAD", "--binary", "--", *pathspec)
        for label, diff in ((b"staged", staged_diff), (b"unstaged", unstaged_diff)):
            digest.update(label)
            digest.update(b"\0")
            digest.update(diff)
            digest.update(b"\0")
        untracked_status = self._run_bytes(
            "status", "--porcelain=v1", "--untracked-files=all", "-z"
        )
        untracked = [
            os.fsdecode(record[3:])
            for record in untracked_status.split(b"\0")
            if record.startswith(b"?? ")
            and not self._is_coordination_state(os.fsdecode(record[3:]))
        ]
        for path in sorted(untracked):
            candidate = self.root / path
            digest.update(os.fsencode(path))
            digest.update(b"\0")
            try:
                if candidate.is_symlink():
                    digest.update(b"symlink\0")
                    digest.update(os.fsencode(os.readlink(candidate)))
                elif candidate.is_file():
                    digest.update(b"file\0")
                    with candidate.open("rb") as handle:
                        while chunk := handle.read(1024 * 1024):
                            digest.update(chunk)
                else:
                    digest.update(b"non-regular\0")
            except OSError as exc:
                raise GitError(f"Unable to hash untracked path {path}") from exc
            digest.update(b"\0")
        return digest.hexdigest()

    @classmethod
    def _is_coordination_state(cls, path: str) -> bool:
        return path.replace("\\", "/") == cls._COORDINATION_STATE

    @staticmethod
    def _status_records(status: bytes) -> tuple[tuple[str, str], ...]:
        records: list[tuple[str, str]] = []
        parts = status.split(b"\0")
        index = 0
        while index < len(parts):
            record = parts[index]
            index += 1
            if not record or len(record) < 3:
                continue
            code = record[:2].decode("ascii")
            path = os.fsdecode(record[3:])
            records.append((code, path))
            if code[0] in {"R", "C"} and index < len(parts):
                index += 1
        return tuple(records)


def inspect_git(root: str | Path) -> GitSnapshot:
    return GitRepository(root).inspect()
