import json
from pathlib import Path

import pytest

from general_os import deployment
from general_os.deployment import DeploymentError, deploy


def make_source(root: Path) -> None:
    files = {
        ".agents/skills/demo/SKILL.md": "---\nname: demo\ndescription: Use when testing.\n---\nSee `docs/rules/example.md` and `docs/runtime-adapters.md`.\n",
        ".agents/skills/demo/scripts/helper.txt": "complete skill directory\n",
        "docs/rules/example.md": "shared rule\n",
        "docs/templates/example.md": "shared template\n",
        "docs/runtime-adapters.md": "adapter boundary\n",
        "AGENTS.md": "project guidance\n",
        "agents/high.toml": 'name = "high"\n',
        "agents/low.toml": 'name = "low"\n',
        "agents/normal.toml": 'name = "normal"\n',
        "agents/review.toml": 'name = "review"\ninstructions = "Review assigned work."\n',
        "agents/review-1.toml": 'name = "review-1"\ninstructions = "Review correctness and regressions."\n',
        "agents/review-2.toml": 'name = "review-2"\ninstructions = "Review contracts and risks."\n',
        "agents/review-3.toml": 'name = "review-3"\ninstructions = "Review integration and acceptance."\n',
        "agents/ui.toml": 'name = "ui"\ninstructions = "Review visual and accessibility behavior."\n',
        "agents/xhigh.toml": 'name = "xhigh"\n',
        "repo_config/runtime-policy.toml": "[runtime]\nnative_subagents_enabled = true\n",
        "state/coordination.json": '{"version": 1, "goal": "test", "tasks": []}\n',
    }
    for relative, content in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def run_apply(source: Path, project: Path, home: Path, **kwargs):
    return deploy(project, source_root=source, home=home, adopt=True, **kwargs)


def test_first_install_copies_complete_skills_and_seeds_only_absent_project_files(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)

    code, report = run_apply(source, project, home)

    assert code == 0
    assert report["status"] == "applied"
    central = home / ".agents" / "general-os"
    installed = (central / "skills/demo/SKILL.md").read_text(encoding="utf-8")
    assert "See `docs/rules/example.md`" not in installed
    assert (central / "skills/demo/scripts/helper.txt").exists()
    assert str(central / "docs" / "rules" / "example.md").replace("\\", "/") in installed
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "project guidance\n"
    assert (project / "agents/review.toml").exists()
    assert (project / "agents/ui.toml").exists()
    assert not (project / "state/coordination.json").exists()
    adoption = json.loads((project / "repo_config/general-os.lock.json").read_text())
    assert set(adoption) == {"schema_version", "adopted_from", "adopted_revision", "seeded_paths"}
    assert "runtime_ids" not in json.dumps(adoption)

    check_code, check_report = run_apply(source, project, home, check=True)
    assert check_code == 0
    assert check_report["status"] == "healthy"


def test_dry_run_does_not_write(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)

    code, report = run_apply(source, project, home, dry_run=True)

    assert code == 0
    assert report["status"] == "dry-run"
    assert not (home / ".agents" / "general-os").exists()
    assert not (project / "repo_config").exists()


def test_central_only_deploy_does_not_mutate_project(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    (project / "AGENTS.md").write_text("local project guidance\n", encoding="utf-8")

    code, report = deploy(source_root=source, home=home)

    assert code == 0
    assert report["repo_root"] is None
    assert (project / "AGENTS.md").read_text(encoding="utf-8") == "local project guidance\n"
    assert not (project / "repo_config").exists()
    assert (home / ".agents/general-os/managed.json").exists()


def test_packaged_assets_support_central_deployment(tmp_path):
    home = tmp_path / "home"

    code, report = deploy(home=home)

    assert code == 0
    assert deployment.PACKAGE_ASSETS.is_dir()
    assert (deployment.PACKAGE_ASSETS / "skills").is_dir()
    assert (deployment.PACKAGE_ASSETS / "project-kit/AGENTS.md").is_file()
    assert "Build the general-os coordination layer" not in (
        deployment.PACKAGE_ASSETS / "project-kit/AGENTS.md"
    ).read_text(encoding="utf-8")
    assert report["source_revision"].startswith("package-")


def test_project_adoption_is_inert_after_existing_lock(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    run_apply(source, project, home)

    seeded = project / "AGENTS.md"
    seeded.write_text("project choice\n", encoding="utf-8")
    (project / "custom.md").write_text("project choice\n", encoding="utf-8")
    (source / "AGENTS.md").write_text("changed package guidance\n", encoding="utf-8")

    code, report = run_apply(source, project, home, check=True)

    assert code == 0
    assert report["status"] == "healthy"
    assert seeded.read_text(encoding="utf-8") == "project choice\n"
    assert (project / "custom.md").exists()

    seeded.unlink()
    code, report = run_apply(source, project, home, check=True)

    assert code == 0
    assert report["status"] == "healthy"
    assert not seeded.exists()


def test_adoption_revision_remains_stable_after_central_source_update(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    run_apply(source, project, home)
    adoption_path = project / "repo_config/general-os.lock.json"
    first = json.loads(adoption_path.read_text(encoding="utf-8"))

    (source / ".agents/skills/demo/SKILL.md").write_text("updated\n", encoding="utf-8")
    run_apply(source, project, home)
    second = json.loads(adoption_path.read_text(encoding="utf-8"))

    assert second["adopted_revision"] == first["adopted_revision"]


def test_owned_files_update_and_unowned_conflicts_are_preserved(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    run_apply(source, project, home)

    skill = source / ".agents/skills/demo/SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "updated\n", encoding="utf-8")
    code, report = run_apply(source, project, home)
    assert code == 0
    assert "updated" in (home / ".agents/general-os/skills/demo/SKILL.md").read_text()
    assert any(item["kind"] == "update" for item in report["actions"])

    conflict = home / ".agents/general-os/skills/demo/SKILL.md"
    conflict.write_text("local change\n", encoding="utf-8")
    skill.write_text(skill.read_text(encoding="utf-8") + "again\n", encoding="utf-8")
    code, report = run_apply(source, project, home)
    assert code == 0
    assert conflict.read_text(encoding="utf-8") == "local change\n"
    assert any(item["kind"] == "preserve" for item in report["actions"])


def test_byte_identical_unmarked_file_is_adopted(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    destination = home / ".agents/general-os/skills/demo/SKILL.md"
    destination.parent.mkdir(parents=True)
    destination.write_bytes(
        deployment._rewrite_skill_references(
            (source / ".agents/skills/demo/SKILL.md").read_bytes(),
            home / ".agents" / "general-os",
        )
    )

    code, report = run_apply(source, project, home)

    assert code == 0
    assert any(item["kind"] == "adopt" for item in report["actions"])
    lock = json.loads((home / ".agents/general-os/managed.json").read_text())
    assert "skills/demo/SKILL.md" in lock["managed_files"]


def test_prune_only_removes_owned_unchanged_files(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    run_apply(source, project, home)
    removed = home / ".agents/general-os/skills/demo/scripts/helper.txt"
    modified = home / ".agents/general-os/docs/templates/example.md"
    modified.write_text("local template\n", encoding="utf-8")
    (source / ".agents/skills/demo/scripts/helper.txt").unlink()
    (source / "docs/templates/example.md").unlink()

    code, report = run_apply(source, project, home, prune=True)

    assert code == 0
    assert not removed.exists()
    assert modified.exists()
    assert any(item["kind"] == "remove" for item in report["actions"])
    assert any(item["kind"] == "preserve" and item["path"] == "docs/templates/example.md" for item in report["actions"])


def test_failed_application_rolls_back_and_writes_lock_last(tmp_path, monkeypatch):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    calls = []
    original = deployment._atomic_write

    def fail_lock(path, data):
        calls.append(path.name)
        if path.name == "managed.json":
            raise OSError("simulated lock failure")
        return original(path, data)

    monkeypatch.setattr(deployment, "_atomic_write", fail_lock)
    with pytest.raises(DeploymentError, match="rolled back"):
        run_apply(source, project, home)

    assert calls[-1] == "managed.json"
    assert not (home / ".agents/general-os/skills/demo/SKILL.md").exists()
    assert not (project / "repo_config/general-os.lock.json").exists()


def test_residue_is_report_only_unless_strict_migration(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    legacy = project / ".agents/rules"
    legacy.mkdir(parents=True)
    (project / ".agents/skills/skill-old").mkdir(parents=True)
    run_apply(source, project, home)

    code, report = run_apply(source, project, home, check=True)
    assert code == 0
    assert report["residue"]
    strict_code, _ = run_apply(source, project, home, check=True, strict_migration=True)
    assert strict_code == 1


def test_invalid_central_lock_fails_closed(tmp_path):
    source = tmp_path / "source"
    project = tmp_path / "project"
    home = tmp_path / "home"
    source.mkdir()
    project.mkdir()
    make_source(source)
    lock = home / ".agents/general-os/managed.json"
    lock.parent.mkdir(parents=True)
    lock.write_text('{"schema_version": 999}\n', encoding="utf-8")

    with pytest.raises(DeploymentError, match="unsupported central lock schema"):
        run_apply(source, project, home, dry_run=True)
