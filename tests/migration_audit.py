import subprocess
import sys
from pathlib import Path


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


def test_migration_manifest_validator_checks_manifest_destinations():
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


def test_migration_manifest_current_tree_check_is_opt_in(tmp_path):
    root = tmp_path / "repository"
    rules = root / "docs" / "rules"
    rules.mkdir(parents=True)
    (rules / "old.md").write_text("old\n", encoding="utf-8")
    (rules / "new.md").write_text("new\n", encoding="utf-8")
    manifest = tmp_path / "manifest.md"
    manifest.write_text(
        "## Rule disposition\n\n"
        "| `old-rule.md` | migrate to `docs/rules/old.md` |\n",
        encoding="utf-8",
    )
    command = [
        sys.executable,
        str(Path(__file__).parents[1] / "scripts" / "validate_migration_manifest.py"),
        "--manifest",
        str(manifest),
        "--repository-root",
        str(root),
    ]

    normal = subprocess.run(command, check=False, capture_output=True, text=True)
    strict = subprocess.run(
        [*command, "--check-current-tree"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert normal.returncode == 0, normal.stderr
    assert strict.returncode == 1
    assert "active rule set mismatch" in strict.stderr
