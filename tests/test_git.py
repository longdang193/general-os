import subprocess

from general_os.git import GitRepository, GitSnapshot


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
