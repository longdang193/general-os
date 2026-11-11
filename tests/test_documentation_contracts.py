from pathlib import Path


def test_documentation_explains_fact_ownership_and_boundaries():
    root = Path(__file__).parents[1]
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    migration = (root / "docs" / "migration" / "project-os-starter.md").read_text(
        encoding="utf-8"
    )

    for text in (architecture, migration):
        assert "state/coordination.json" in text
        assert "Codex" in text
        assert "Orca" in text
        assert "Git" in text
    assert "read-only" in migration


def test_orca_skill_and_runtime_docs_keep_native_ownership_explicit():
    root = Path(__file__).parents[1]
    runtime = (root / "docs" / "runtime-adapters.md").read_text(encoding="utf-8")
    skill = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "orca_enabled" in runtime
    assert "native" in runtime.lower()
    assert "worker lifecycle" in runtime
    assert "runtime IDs" in runtime
    assert "orca skills get orchestration --full" in skill
    assert "orca_enabled" in skill
    assert "native" in skill.lower()
    assert "worker lifecycle" in skill
    assert "Run ID" in skill
    assert "native" in skill.lower()
    assert "model" in skill
