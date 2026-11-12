import subprocess

import pytest

from general_os.git import GitError, GitRepository, GitSnapshot


def run_git(root, *args):
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )


def test_inspect_git_observes_branch_revision_and_changes(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    (tmp_path / "README.md").write_text("draft\n", encoding="utf-8")

    snapshot = GitRepository(tmp_path).inspect()

    assert isinstance(snapshot, GitSnapshot)
    assert snapshot.branch == "main"
    assert snapshot.revision is None
    assert snapshot.changed_files == ("README.md",)
    assert snapshot.conflicts == ()
    assert snapshot.clean is False


def test_inspect_git_reports_conflicting_index_status(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    (tmp_path / "file.txt").write_text("content\n", encoding="utf-8")
    run_git(tmp_path, "add", "file.txt")
    run_git(
        tmp_path,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "initial",
    )
    run_git(tmp_path, "checkout", "-b", "feature")
    (tmp_path / "file.txt").write_text("feature\n", encoding="utf-8")
    run_git(tmp_path, "add", "file.txt")
    run_git(
        tmp_path,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "feature",
    )
    run_git(tmp_path, "checkout", "main")
    (tmp_path / "file.txt").write_text("main\n", encoding="utf-8")
    run_git(tmp_path, "add", "file.txt")
    run_git(
        tmp_path,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "main",
    )
    subprocess.run(
        ["git", "merge", "feature"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )

    snapshot = GitRepository(tmp_path).inspect()

    assert snapshot.conflicts == ("file.txt",)
    assert snapshot.clean is False


def test_snapshot_identity_changes_with_tracked_and_untracked_content(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    (tmp_path / "file.txt").write_text("initial\n", encoding="utf-8")
    run_git(tmp_path, "add", "file.txt")
    run_git(
        tmp_path,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "initial",
    )

    first = GitRepository(tmp_path).inspect()
    (tmp_path / "file.txt").write_text("changed\n", encoding="utf-8")
    second = GitRepository(tmp_path).inspect()
    (tmp_path / "untracked.txt").write_text("untracked\n", encoding="utf-8")
    third = GitRepository(tmp_path).inspect()

    assert first.identity != second.identity
    assert second.identity != third.identity


def test_snapshot_identity_hashes_quoted_untracked_paths(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    path = tmp_path / "new file.txt"
    path.write_text("first\n", encoding="utf-8")

    first = GitRepository(tmp_path).inspect()
    path.write_text("second\n", encoding="utf-8")
    second = GitRepository(tmp_path).inspect()

    assert first.identity != second.identity


def test_snapshot_identity_hashes_staged_content_in_unborn_repository(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    path = tmp_path / "staged.txt"
    path.write_text("first\n", encoding="utf-8")
    run_git(tmp_path, "add", "staged.txt")

    first = GitRepository(tmp_path).inspect()
    path.write_text("second\n", encoding="utf-8")
    run_git(tmp_path, "add", "staged.txt")
    second = GitRepository(tmp_path).inspect()

    assert first.identity != second.identity


def test_snapshot_identity_handles_utf8_tracked_diff(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    path = tmp_path / "file.txt"
    path.write_text("initial\n", encoding="utf-8")
    run_git(tmp_path, "add", "file.txt")
    run_git(
        tmp_path,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "initial",
    )
    path.write_text("ā\n", encoding="utf-8")

    snapshot = GitRepository(tmp_path).inspect()

    assert snapshot.clean is False


def test_snapshot_identity_distinguishes_clean_clones(tmp_path):
    source = tmp_path / "source"
    clone = tmp_path / "clone"
    source.mkdir()
    run_git(source, "init", "--initial-branch", "main")
    (source / "file.txt").write_text("content\n", encoding="utf-8")
    run_git(source, "add", "file.txt")
    run_git(
        source,
        "-c",
        "user.name=Test User",
        "-c",
        "user.email=test@example.com",
        "commit",
        "-m",
        "initial",
    )
    run_git(tmp_path, "clone", str(source), str(clone))

    assert GitRepository(source).inspect().identity != GitRepository(clone).inspect().identity


def test_snapshot_identity_hashes_symlink_target_when_supported(tmp_path):
    run_git(tmp_path, "init", "--initial-branch", "main")
    target = tmp_path / "target.txt"
    link = tmp_path / "link.txt"
    target.write_text("content\n", encoding="utf-8")
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symlinks unavailable")

    first = GitRepository(tmp_path).inspect()
    link.unlink()
    link.symlink_to(tmp_path / "other.txt")
    second = GitRepository(tmp_path).inspect()

    assert first.identity != second.identity


def test_snapshot_identity_reports_unreadable_untracked_file(tmp_path, monkeypatch):
    run_git(tmp_path, "init", "--initial-branch", "main")
    path = tmp_path / "untracked.txt"
    path.write_text("content\n", encoding="utf-8")
    original_open = type(path).open

    def fail_open(self, *args, **kwargs):
        if self == path:
            raise OSError("unreadable")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(type(path), "open", fail_open)
    with pytest.raises(GitError, match="Unable to hash untracked path"):
        GitRepository(tmp_path).inspect()
