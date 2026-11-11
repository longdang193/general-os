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
