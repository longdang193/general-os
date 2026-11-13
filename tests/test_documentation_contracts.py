import json
import re
import subprocess
import sys
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
    state = json.loads((root / "state" / "coordination.json").read_text(encoding="utf-8"))
    detailed_plan = (root / "docs" / "templates" / "detailed-plan.md").read_text(
        encoding="utf-8"
    )

    for term in ("Git", "Codex", "Orca", "acceptance"):
        assert term.lower() in guidance.lower()
    assert template["version"] == 1
    assert state["version"] == 1
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
    assert template["tasks"] == []
    for term in (
        "Durable sequencing",
        "Constraints / decisions",
        "Verification",
        "Stop / escalation conditions",
        "durable coordination",
        "native runtime planning",
    ):
        assert term in detailed_plan
    assert "## Agent Memory" in guidance
    assert "## Command Safety" in guidance


def test_maintained_skill_descriptions_are_actionable():
    root = Path(__file__).parents[1]
    skill_root = root / ".agents" / "skills"

    for path in sorted(skill_root.glob("*/SKILL.md")):
        frontmatter = path.read_text(encoding="utf-8").split("---\n", 2)[1]
        description = next(
            line.split(":", 1)[1].strip()
            for line in frontmatter.splitlines()
            if line.startswith("description:")
        )
        assert description.startswith("Use when"), path
        assert "migrated specialist procedure" not in description, path


def test_planning_and_review_guidance_do_not_create_a_second_authority():
    root = Path(__file__).parents[1]
    paths = (
        root / ".agents" / "skills" / "plan-document-reviewer" / "SKILL.md",
        root / ".agents" / "skills" / "workspace-isolation" / "SKILL.md",
        root / ".agents" / "skills" / "finishing-development-work" / "SKILL.md",
        root / ".agents" / "skills" / "reviewing-pull-requests" / "SKILL.md",
    )
    contents = "\n".join(path.read_text(encoding="utf-8") for path in paths)

    assert "state/coordination.json" in contents
    assert "lifecycle authority" in contents
    assert "implementation plan does not grant Git or publication authority" in contents
    for forbidden in (
        "active-plan lane authority",
        "approved-plan lane authority",
        "active plan ledger",
    ):
        assert forbidden not in contents


def test_migrated_guidance_uses_current_owners_and_review_statuses():
    root = Path(__file__).parents[1]
    skill_paths = [
        root / ".agents" / "skills" / name / "SKILL.md"
        for name in (
            "dashboard-reporting",
            "requesting-code-review",
            "reviewing-pull-requests",
            "wayfinding",
            "receiving-code-review",
        )
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in skill_paths)

    assert "Project OS" not in contents
    assert "CLAUDE.md" not in contents
    assert "routing rules" not in contents
    assert "review-local verdict" in contents


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
    defining_work = contents["defining-work"]
    for term in (
        '"tasks": []',
        "Direct execution",
        "fresh capable executor",
        "native runtime",
        "update_plan",
        "runtime IDs",
    ):
        assert term in defining_work
    assert "update_plan" in contents["executing-work"]
    assert "PASS" in contents["verification-before-completion"]
    assert "orca skills get orchestration --full" in contents["orca-orchestration"]


def test_goal_only_and_reusable_skill_boundaries_are_explicit():
    root = Path(__file__).parents[1]
    defining_work = (root / ".agents" / "skills" / "defining-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")
    recovery = (root / "docs" / "recovery.md").read_text(encoding="utf-8")
    learning = (
        root / ".agents" / "skills" / "creating-learning-materials" / "SKILL.md"
    ).read_text(encoding="utf-8")
    historical_plans = (root / "docs" / "superpowers" / "plans" / "README.md").read_text(
        encoding="utf-8"
    )

    for text in (defining_work, contracts, recovery):
        normalized = " ".join(text.split())
        assert "no durable completion" in normalized
        assert "task graph" in normalized
    assert "user-supplied output location" in learning
    assert "OneDrive" not in learning
    assert "never override" in historical_plans


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
    assert "requires an explicit" in runtime
    assert "native defaults" in runtime
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


def test_readme_has_stable_verification_commands():
    root = Path(__file__).parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")

    assert "pytest -q" in readme
    assert "python -m general_os state validate state/coordination.json" in readme
    assert "active implementation plan" not in readme


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


def test_migration_manifest_accounts_for_every_predecessor_surface():
    root = Path(__file__).parents[1]
    migration = (root / "docs" / "migration" / "project-os-starter.md").read_text(
        encoding="utf-8"
    )
    skills = {
        "skill-backend-verification",
        "skill-brainstorming",
        "skill-central-config-layer",
        "skill-chief-of-staff",
        "skill-code-standards",
        "skill-creating-learning-materials",
        "skill-dashboard-reporting",
        "skill-deepagents-executing-plans",
        "skill-dispatching-parallel-agents",
        "skill-disposable-artifact-cleanup",
        "skill-distinctive-frontend-design",
        "skill-executing-plans",
        "skill-finishing-a-development-branch",
        "skill-frontend-component-engineering",
        "skill-full-stack-integration",
        "skill-github-browser-reviews",
        "skill-performance-optimization",
        "skill-plan-document-reviewer",
        "skill-project-secretary",
        "skill-receiving-code-review",
        "skill-refactoring-assessment",
        "skill-requesting-code-review",
        "skill-reviewing-pull-requests",
        "skill-spec-drafting",
        "skill-subagent-driven-development",
        "skill-systematic-debugging",
        "skill-test-driven-development",
        "skill-using-git-worktrees",
        "skill-using-superpowers",
        "skill-verification-before-completion",
        "skill-wayfinding",
        "skill-writing-plans",
        "skill-writing-skills",
    }
    rules = {
        "agent-memory-rule.md",
        "audit-evidence-mandate-rule.md",
        "backend-verification-rule.md",
        "command-execution-rule.md",
        "doc-contracts-rule.md",
        "frontend-backend-integration-rule.md",
        "frontend-ui-rule.md",
        "git-tracked-coordination-rule.md",
        "prompt-cache-contract-rule.md",
        "publication-boundary-rule.md",
        "python-contracts-rule.md",
    }

    assert len(skills) == 33
    assert len(rules) == 11
    assert "00b825ba95af4a44f0a33d528ea42593f3fc1dc1" in migration
    assert all(skill in migration for skill in skills)
    assert all(rule in migration for rule in rules)
    assert migration.count("| `skill-") == 33
    assert migration.count("| `") >= 44


def test_migration_manifest_validator_checks_current_tree():
    root = Path(__file__).parents[1]
    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "validate_migration_manifest.py"),
            "--manifest",
            str(root / "docs" / "migration" / "project-os-starter.md"),
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "valid:" in result.stdout


def test_publication_boundary_has_one_maintained_skill_owner():
    root = Path(__file__).parents[1]
    owners = [
        path
        for path in (root / ".agents" / "skills").glob("*/SKILL.md")
        if "docs/rules/publication-boundary.md"
        in path.read_text(encoding="utf-8")
    ]

    assert [path.parent.name for path in owners] == ["finishing-development-work"]


def test_maintained_skills_use_minimal_frontmatter_and_no_generated_rules():
    root = Path(__file__).parents[1]
    skill_root = root / ".agents" / "skills"
    skills = sorted(path.parent.name for path in skill_root.glob("*/SKILL.md"))

    assert len(skills) == 29
    assert not (skill_root.parent / "rules").exists()
    for path in sorted(skill_root.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        frontmatter = text.split("---\n", 2)[1]
        fields = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if ":" in line
        }
        assert fields == {"name", "description"}, path


def test_migrated_skills_use_current_owners_and_available_resources():
    root = Path(__file__).parents[1]
    skill_root = root / ".agents" / "skills"
    active_paths = sorted(skill_root.rglob("*.md"))
    all_skills = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
    forbidden = (
        "repository operating guidance",
        "scripts/ocr_delegate_adapter.py",
        "skill-dispatching-parallel-agents",
        "skill-subagent-driven-development",
        "skill-verification-before-completion",
    )
    assert not any(value in all_skills for value in forbidden)

    reference_pattern = re.compile(r"`([^`\n]*(?:/|\\|\.md|\.py|\.toml)[^`\n]*)`")
    for path in active_paths:
        for reference in reference_pattern.findall(path.read_text(encoding="utf-8")):
            if (
                reference.startswith(("http://", "https://", "~/", "$", "<"))
                or "*" in reference
                or reference.endswith("/")
                or "<" in reference
            ):
                continue
            if reference.startswith((".agents/", "docs/", "src/", "tests/", "state/", "repo_config/", "AGENTS.md", "README")):
                target = root / reference
            elif reference.startswith("scripts/"):
                target = path.parent / reference
            else:
                continue
            assert target.exists(), f"missing active skill reference: {path} -> {reference}"

    assert (root / "docs" / "runtime-adapters.md").exists()
    assert not (root / "docs" / "rules" / "backend-verification.md").exists()
