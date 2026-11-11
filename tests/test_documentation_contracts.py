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
