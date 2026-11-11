import json
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


def test_root_guidance_and_templates_define_durable_ownership():
    root = Path(__file__).parents[1]
    guidance = (root / "AGENTS.md").read_text(encoding="utf-8")
    template_path = root / "docs" / "templates" / "coordination-state.json"
    template = json.loads(template_path.read_text(encoding="utf-8"))
    detailed_plan = (root / "docs" / "templates" / "detailed-plan.md").read_text(
        encoding="utf-8"
    )

    for term in ("Git", "Codex", "Orca", "acceptance"):
        assert term.lower() in guidance.lower()
    for heading in (
        "# Goal",
        "# Outcomes",
        "# Constraints / decisions",
        "# Task graph",
        "# Final verification",
    ):
        assert heading in detailed_plan

    assert template["goal"]
    assert isinstance(template["tasks"], list)
    task = template["tasks"][0]
    assert {
        "id",
        "objective",
        "state",
        "depends_on",
        "acceptance",
    } <= set(task)
    assert set(task) <= {
        "id",
        "objective",
        "state",
        "depends_on",
        "acceptance",
        "profile",
        "requires_independent_boundary",
    }


def test_core_governance_skills_define_native_ownership():
    root = Path(__file__).parents[1]
    skill_paths = {
        "chief-of-staff": root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md",
        "defining-work": root / ".agents" / "skills" / "defining-work" / "SKILL.md",
        "executing-work": root / ".agents" / "skills" / "executing-work" / "SKILL.md",
        "verification-before-completion": root
        / ".agents"
        / "skills"
        / "verification-before-completion"
        / "SKILL.md",
        "orca-orchestration": root
        / ".agents"
        / "skills"
        / "orca-orchestration"
        / "SKILL.md",
    }

    contents = {name: path.read_text(encoding="utf-8") for name, path in skill_paths.items()}
    assert all("Use when" in text for text in contents.values())
    assert "canonical coordination intelligence" in contents["chief-of-staff"]
    assert '"tasks": []' in contents["defining-work"]
    assert "update_plan" in contents["executing-work"]
    assert "PASS" in contents["verification-before-completion"]
    assert "orca skills get orchestration --full" in contents["orca-orchestration"]


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
    assert "harness-neutral" in skill
    assert "model" in skill
    assert "native defaults" in skill


def test_native_cos_keeps_orca_optional_but_allows_material_independence():
    root = Path(__file__).parents[1]
    chief = (root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    runtime = (root / "docs" / "runtime-adapters.md").read_text(encoding="utf-8")

    assert "materially useful" in chief
    assert "hard requirement" in chief
    assert "primary execution path" in runtime
    assert "required independent" in runtime
    assert "blocks when Orca is disabled or unavailable" in runtime


def test_profile_projection_is_canonical_and_one_way():
    root = Path(__file__).parents[1]
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    runtime = (root / "docs" / "runtime-adapters.md").read_text(encoding="utf-8")
    skill = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    for text in (architecture, runtime, skill):
        assert "agents/*.toml" in text
        assert "project" in text.lower() or "projected" in text.lower()
        assert "defaults" in text
    assert "no second Orca profile registry" in architecture
