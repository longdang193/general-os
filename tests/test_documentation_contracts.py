import json
import re
from pathlib import Path


def test_documentation_explains_fact_ownership_and_boundaries():
    root = Path(__file__).parents[1]
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    migration = (root / "docs" / "migration" / "project-os-starter.md").read_text(
        encoding="utf-8"
    )
    deployment = (root / "docs" / "deployment.md").read_text(encoding="utf-8")

    for text in (architecture, migration):
        assert "state/coordination.json" in text
        assert "Codex" in text
        assert "Orca" in text
        assert "Git" in text
    for term in ("Codex", "Git", "managed.json", "seed-only", "--strict-migration"):
        assert term in deployment
    assert "read-only" in migration
    assert "managed.json" in deployment
    assert "seed-only" in deployment
    assert "--strict-migration" in deployment


def test_documentation_keeps_native_specification_and_direct_work_native():
    root = Path(__file__).parents[1]
    texts = [
        (root / "README.md").read_text(encoding="utf-8"),
        (root / "docs" / "architecture.md").read_text(encoding="utf-8"),
        (root / "docs" / "contracts.md").read_text(encoding="utf-8"),
        (root / ".agents" / "skills" / "spec-drafting" / "SKILL.md").read_text(
            encoding="utf-8"
        ),
        (root / ".agents" / "skills" / "executing-work" / "SKILL.md").read_text(
            encoding="utf-8"
        ),
        (root / ".agents" / "skills" / "defining-work" / "SKILL.md").read_text(
            encoding="utf-8"
        ),
    ]
    contents = "\n".join(texts)
    assert "OpenSpec" in contents
    assert "tasks.md" in contents
    assert "Do not copy" in contents or "Do not mirror" in contents
    assert "ordinary authorized work" in contents


def test_external_review_does_not_bypass_git_bound_acceptance():
    root = Path(__file__).parents[1]
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")
    verification = (
        root / ".agents" / "skills" / "verification-before-completion" / "SKILL.md"
    ).read_text(encoding="utf-8")
    contents = f"{contracts}\n{verification}"
    assert "Source-specific review" in contents
    assert "external-only" in contents
    assert "does not produce the machine-readable" in contents
    assert "existing Git-bound acceptance path" in contents


def test_reviewed_guidance_handles_scope_specific_acceptance_and_native_ownership():
    root = Path(__file__).parents[1]
    brainstorming = (root / ".agents" / "skills" / "brainstorming" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    spec = (root / ".agents" / "skills" / "spec-drafting" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    defining = (root / ".agents" / "skills" / "defining-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")
    plan = (root / "docs" / "templates" / "detailed-plan.md").read_text(
        encoding="utf-8"
    )
    verification = (
        root / ".agents" / "skills" / "verification-before-completion" / "SKILL.md"
    ).read_text(encoding="utf-8")
    finishing = (
        root / ".agents" / "skills" / "finishing-development-work" / "SKILL.md"
    ).read_text(encoding="utf-8")
    review = (root / ".agents" / "skills" / "requesting-code-review" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    tdd = (root / ".agents" / "skills" / "test-driven-development" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    normalized_brainstorming = " ".join(brainstorming.split())
    assert "Source and tests establish observed behavior" in brainstorming
    assert "Investigate and reconcile conflicts rather than automatically favoring either" in normalized_brainstorming
    assert "After approval, return to the designated project workflow" in spec
    assert "Native OpenSpec route" in spec
    assert '"id": "policy-preservation"' in defining
    assert '"objective": "Maintain the approved admission policy' in defining
    assert "External-only strategic acceptance uses the designated" in contracts
    assert "designated project decision record" in contracts
    assert "For external-only goals" in plan
    assert "external-only review" in verification
    assert "do not turn an external-only review into a General OS task `PASS`" in verification
    normalized_finishing = " ".join(finishing.split())
    assert "already selected an eligible closure action" in normalized_finishing
    assert "Present options only when no closure choice" in normalized_finishing
    assert "uncommitted review possible" in review
    assert "staged, unstaged, and untracked inventory" in review
    assert "approved path inventory and exclusions" in review
    assert "outside that inventory are unrelated" in review
    assert "known baseline/unrelated failures" in tdd
    assert "No introduced unexpected errors or warnings" in tdd
    assert "proportional evidence" in " ".join(tdd.split())
    assert "deterministic changes prefer" in " ".join(tdd.split())


def test_reviewed_skill_mirrors_match_canonical_sources():
    root = Path(__file__).parents[1]
    for name in (
        "chief-of-staff",
        "verification-before-completion",
        "finishing-development-work",
        "requesting-code-review",
        "test-driven-development",
        "executing-work",
        "orca-orchestration",
    ):
        canonical = root / ".agents" / "skills" / name / "SKILL.md"
        packaged = root / "src" / "general_os" / "assets" / "skills" / name / "SKILL.md"
        assert canonical.read_bytes() == packaged.read_bytes(), name

    reviewer = root / ".agents" / "skills" / "requesting-code-review" / "code-reviewer.md"
    packaged_reviewer = (
        root
        / "src"
        / "general_os"
        / "assets"
        / "skills"
        / "requesting-code-review"
        / "code-reviewer.md"
    )
    assert reviewer.read_bytes() == packaged_reviewer.read_bytes()


def test_openspec_execution_and_recovery_keep_shared_artifacts_single_owned():
    root = Path(__file__).parents[1]
    executing = (root / ".agents" / "skills" / "executing-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    orca = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    verification = (
        root / ".agents" / "skills" / "verification-before-completion" / "SKILL.md"
    ).read_text(encoding="utf-8")
    recovery = (root / "docs" / "recovery.md").read_text(encoding="utf-8")
    normalized_executing = " ".join(executing.split())
    normalized_orca = " ".join(orca.split())
    normalized_verification = " ".join(verification.split())
    normalized_recovery = " ".join(recovery.split())

    assert "controlling Codex agent owns the native OpenSpec `apply` path" in normalized_executing
    assert "must not independently run the full apply workflow" in normalized_executing
    assert "`openspec-update-change`" in normalized_executing
    assert "single authoritative writer for shared change artifacts" in normalized_orca
    assert "shared checklist entries concurrently" in normalized_orca
    assert "completed `tasks.md` checkbox records native task tracking only" in normalized_verification
    assert "neither checklist completion nor native verification output alone" in normalized_verification
    assert "do not recreate" in normalized_recovery
    assert "`openspec-update-change`" in normalized_recovery


def test_native_workflows_and_strategic_decisions_keep_single_owners():
    root = Path(__file__).parents[1]
    spec = (root / ".agents" / "skills" / "spec-drafting" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    wayfinding = (root / ".agents" / "skills" / "wayfinding" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    brainstorming = (root / ".agents" / "skills" / "brainstorming" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    plan_reviewer = (root / ".agents" / "skills" / "plan-document-reviewer" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")
    frontend = (root / "docs" / "rules" / "frontend-ui.md").read_text(
        encoding="utf-8"
    )

    assert "Native OpenSpec route" in spec
    assert "Do not require this skill's separate" in spec
    assert "target project's authoritative specification workflow" in " ".join(wayfinding.split())
    assert "designated project artifact" in wayfinding
    assert "active OpenSpec change" in " ".join(brainstorming.split())
    assert "only when durable General OS coordination is actually needed" in " ".join(brainstorming.split())
    assert "owning specification workflow" in plan_reviewer
    assert "material ambiguity, risk, independent handoff" in " ".join(plan_reviewer.split())
    assert "Strategic decision rationale" in architecture
    assert "project-owned Markdown" in contracts
    assert "observed implementation behavior" in frontend


def test_templates_and_openspec_precedence_are_scoped():
    root = Path(__file__).parents[1]
    template = json.loads(
        (root / "docs" / "templates" / "coordination-state.json").read_text(
            encoding="utf-8"
        )
    )
    detailed_plan = (root / "docs" / "templates" / "detailed-plan.md").read_text(
        encoding="utf-8"
    )
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")

    assert template["goal"] == "Coordinate a material cross-session decision"
    assert "only when `defining-work` selects a durable General OS" in detailed_plan
    for text in (architecture, contracts):
        normalized = " ".join(text.split())
        assert "authorized active OpenSpec change defines the implementation target for its scope" in normalized
        assert "does not globally replace the maintained contract" in normalized


def test_debugging_and_review_guidance_preserve_qualifications():
    root = Path(__file__).parents[1]
    debugging = (root / ".agents" / "skills" / "systematic-debugging" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    review = (root / ".agents" / "skills" / "requesting-code-review" / "SKILL.md").read_text(
        encoding="utf-8"
    )

    assert "inspect existing evidence first" in debugging
    assert "Instrument only unresolved component boundaries" in debugging
    assert "hard independence or review requirement" in review


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


def test_frontend_ui_rule_matches_packaged_asset():
    root = Path(__file__).parents[1]
    canonical = (root / "docs" / "rules" / "frontend-ui.md").read_text(
        encoding="utf-8"
    )
    packaged = (
        root / "src" / "general_os" / "assets" / "docs" / "rules" / "frontend-ui.md"
    ).read_text(encoding="utf-8")

    assert canonical == packaged


def test_concept_brief_is_available_and_documents_native_boundaries():
    root = Path(__file__).parents[1]
    template = root / "docs" / "templates" / "concept-brief.md"
    packaged = root / "src" / "general_os" / "assets" / "docs" / "templates" / "concept-brief.md"
    brainstorming = (root / ".agents" / "skills" / "brainstorming" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    wayfinding = (root / ".agents" / "skills" / "wayfinding" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    readme = (root / "README.md").read_text(encoding="utf-8")
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")

    assert template.is_file()
    assert template.read_bytes() == packaged.read_bytes()
    template_text = template.read_text(encoding="utf-8")
    for section in ("## 1. Problem", "## 2. Value", "## 3. Concept", "## 4. Uncertainty", "## 5. Decision"):
        assert section in template_text
    assert "docs/templates/concept-brief.md" in brainstorming
    assert "project-owned Concept Brief" in wayfinding
    assert "wayfinding map\nprovisional" in wayfinding
    assert "Concept Brief" in readme and "OpenSpec" in readme
    assert "Concept Brief" in architecture and "General OS task record" in architecture


def test_centrally_deployed_docs_match_canonical_sources():
    root = Path(__file__).parents[1]
    canonical_root = root / "docs"
    packaged_root = root / "src" / "general_os" / "assets" / "docs"
    canonical_paths = {
        Path("runtime-adapters.md"),
        *(
            path.relative_to(canonical_root)
            for path in (canonical_root / "rules").rglob("*")
            if path.is_file()
        ),
        *(
            path.relative_to(canonical_root)
            for path in (canonical_root / "templates").rglob("*")
            if path.is_file()
        ),
    }
    packaged_paths = {
        path.relative_to(packaged_root)
        for path in packaged_root.rglob("*")
        if path.is_file()
    }

    assert packaged_paths == canonical_paths
    for relative_path in sorted(canonical_paths):
        assert (canonical_root / relative_path).read_bytes() == (
            packaged_root / relative_path
        ).read_bytes()


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
    assert "native runtime" in contents
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


def test_review_and_wayfinding_guidance_keep_topology_and_state_native():
    root = Path(__file__).parents[1]
    review = (root / ".agents" / "skills" / "requesting-code-review" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    reviewer = (
        root / ".agents" / "skills" / "requesting-code-review" / "code-reviewer.md"
    ).read_text(encoding="utf-8")
    wayfinding = (root / ".agents" / "skills" / "wayfinding" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    derived_wayfinding = (
        root / "src" / "general_os" / "assets" / "skills" / "wayfinding" / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "active native controller chooses whether review" in review
    normalized_review = " ".join(review.split())
    assert "CoS may record a hard independence or review requirement" in normalized_review
    assert "it does not select the reviewer runtime, profile, or topology" in normalized_review
    assert "Native Orca" in review
    assert "controller-selected discovered-profile reviewer" not in review
    assert "Reviewer:" in reviewer
    assert "COMMITTED_RANGE | WORKING_TREE" in reviewer
    assert "git diff --cached" in reviewer
    assert "git diff --stat [BASE_SHA] -- [APPROVED_PATHS]" in reviewer
    assert "Do not inspect unrelated paths" in reviewer
    assert "frozen review package" in reviewer
    assert "optional" in reviewer
    assert "otherwise continue native" in " ".join(reviewer.split())
    assert "````\nReviewer:" in reviewer
    assert "````\n\n**Placeholders:**" in reviewer
    assert "controller-selected profile" not in reviewer
    orca = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "Ask that native guidance to validate the repository boundary" in orca
    assert "does not select Orca, a reviewer, or the execution topology" in orca
    assert "--worktree current" not in orca
    assert "docs/wayfinding/" in wayfinding
    assert "remains the only durable" in " ".join(wayfinding.split())
    assert "workflow state" in wayfinding
    assert "docs/superpowers/plans/wayfinding/" not in wayfinding
    assert "current author" in wayfinding
    assert "no item is stale" not in wayfinding
    assert "handoff is recorded" not in wayfinding
    assert wayfinding == derived_wayfinding


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
    assert "version-matched guidance" in contents["orca-orchestration"]
    assert "lightweight handoff guidance" in contents["orca-orchestration"]
    assert "Repository-bound runtime loss" in contents["executing-work"]
    assert "owning project record and authoritative source" in contents["orca-orchestration"]


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
    brainstorming = (root / ".agents" / "skills" / "brainstorming" / "SKILL.md").read_text(
        encoding="utf-8"
    )
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
    assert "design-artifact" in brainstorming
    assert "docs/superpowers/plans/brainstorming/" not in brainstorming


def test_orca_skill_and_runtime_docs_keep_native_ownership_explicit():
    root = Path(__file__).parents[1]
    runtime = (root / "docs" / "runtime-adapters.md").read_text(encoding="utf-8")
    skill = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    derived_skill = (
        root / "src" / "general_os" / "assets" / "skills" / "orca-orchestration" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_runtime = (
        root / "src" / "general_os" / "assets" / "docs" / "runtime-adapters.md"
    ).read_text(encoding="utf-8")
    normalized_skill = " ".join(skill.split())
    normalized_runtime = " ".join(runtime.split())

    assert "orca_enabled" in runtime
    assert "native" in runtime.lower()
    assert "worker lifecycle" in runtime
    assert "runtime IDs" in runtime
    assert "requires an explicit" in runtime
    assert "native defaults" in runtime
    assert "version-matched guidance" in skill
    assert "lightweight handoff guidance" in skill
    assert "ownership handoff" in skill
    assert "not semantic task completion" in skill
    assert "orca_enabled" in skill
    assert "native" in skill.lower()
    assert "worker lifecycle" in skill
    assert "harness-neutral" in skill
    assert "model" in skill
    assert "native defaults" in skill
    assert "semantic workstream" in normalized_skill
    assert "execution topology" in normalized_skill
    assert "partial progress" in normalized_skill
    assert "ownership handoff" in normalized_skill
    assert "not semantic task completion" in normalized_skill
    assert "current Git" in normalized_skill
    assert skill == derived_skill
    assert runtime == derived_runtime
    assert "native Orca" in normalized_runtime
    assert "partial progress" in normalized_runtime
    assert "ownership handoff" in normalized_runtime
    assert "not semantic task completion" in normalized_runtime
    assert "build_orca_launch(project_profile(profile)) performs" not in normalized_runtime


def test_architecture_contract_keeps_project_and_runtime_ownership_separate():
    root = Path(__file__).parents[1]
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    contracts = (root / "docs" / "contracts.md").read_text(encoding="utf-8")
    deployment = (root / "docs" / "deployment.md").read_text(encoding="utf-8")

    for text in (architecture, contracts):
        assert "`general-os` owns" in text
        assert "coordination judgment" in text
        assert "active native controller" in text
        assert "semantic workstream" in text or "workstream contract" in text
        assert "partial progress" in text
        assert "does not silently merge" in text or "does not silently merge runtime" in text

    assert "execution topology" in architecture
    assert "lightweight ownership handoff" in architecture
    assert "not durable general-os acceptance" in architecture
    assert "Transfer or runtime completion is not durable" in contracts

    assert "~/.agents/skills/" in deployment
    assert "~/.agents/general-os/" in deployment
    assert "seed-only" in deployment
    assert "state/coordination.json` is never seeded" in deployment


def test_native_first_architecture_rejects_routine_general_os_gates():
    root = Path(__file__).parents[1]
    active_paths = [
        root / "README.md",
        root / "docs" / "architecture.md",
        root / "docs" / "contracts.md",
        root / "docs" / "runtime-adapters.md",
        root / "docs" / "migration" / "project-os-starter.md",
        root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md",
        root / ".agents" / "skills" / "verification-before-completion" / "SKILL.md",
        root / ".agents" / "skills" / "finishing-development-work" / "SKILL.md",
        root / ".agents" / "skills" / "test-driven-development" / "SKILL.md",
        root / ".agents" / "skills" / "defining-work" / "SKILL.md",
    ]
    contents = "\n".join(path.read_text(encoding="utf-8") for path in active_paths)
    normalized = " ".join(contents.split())

    for forbidden in (
        "Project-level CoS chooses the execution boundary",
        "CoS chooses the smallest effective native execution boundary",
        "inside a CoS-selected boundary",
        "CoS selects Orca",
    ):
        assert forbidden not in normalized
    assert "native project verification" in normalized
    assert "Persistence alone is insufficient" in normalized
    assert "Changed behavior requires proportional evidence" in normalized


def test_planning_and_recovery_route_external_outcomes_to_project_records():
    root = Path(__file__).parents[1]
    defining = (root / ".agents" / "skills" / "defining-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    recovery = (root / "docs" / "recovery.md").read_text(encoding="utf-8")
    normalized_defining = " ".join(defining.split())
    normalized_recovery = " ".join(recovery.split())

    assert "### Outcome ownership" in defining
    assert "Project-owned external outcome" in defining
    assert "must not be routed into a General OS task" in normalized_defining
    assert "repository-bound General OS completion" in normalized_recovery
    assert "External-only completion returns to the designated project" in normalized_recovery


def test_repository_bound_acceptance_and_recovery_are_scoped():
    root = Path(__file__).parents[1]
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    recovery = (root / "docs" / "recovery.md").read_text(encoding="utf-8")
    chief = (root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    defining = (root / ".agents" / "skills" / "defining-work" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    normalized_architecture = " ".join(architecture.split())
    normalized_recovery = " ".join(recovery.split())
    normalized_chief = " ".join(chief.split())

    assert "repository-bound coordinated work" in normalized_architecture
    assert "does not produce a General OS task-state transition" in normalized_architecture
    assert "Machine-readable General OS task acceptance uses the current Git snapshot" in normalized_architecture
    assert "External-only work recovers from its designated project decision record" in normalized_recovery
    assert "repository-bound completed task" in normalized_recovery
    assert "external-only work, inspect the designated project decision record" in normalized_chief
    assert "owning rollout records" in defining
    assert "Each phase records" not in defining


def test_native_cos_keeps_orca_optional_but_allows_material_independence():
    root = Path(__file__).parents[1]
    chief = (root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    orca = (root / ".agents" / "skills" / "orca-orchestration" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    runtime = (root / "docs" / "runtime-adapters.md").read_text(encoding="utf-8")
    derived_chief = (
        root / "src" / "general_os" / "assets" / "skills" / "chief-of-staff" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_orca = (
        root / "src" / "general_os" / "assets" / "skills" / "orca-orchestration" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_runtime = (
        root / "src" / "general_os" / "assets" / "docs" / "runtime-adapters.md"
    ).read_text(encoding="utf-8")
    normalized_chief = " ".join(chief.split())
    normalized_orca = " ".join(orca.split())
    normalized_runtime = " ".join(runtime.split())

    assert "materially useful" in chief
    assert "hard requirement" in chief
    assert "active native controller chooses Codex direct" in normalized_chief
    assert "CoS chooses the smallest effective native execution boundary" not in normalized_chief
    assert "false` does not prohibit selecting" in chief
    assert "independent hypothesis testing" in normalized_orca
    assert "examples, not mandatory workflows" in normalized_orca
    assert "primary execution path" in normalized_runtime
    assert "Required independent" in normalized_runtime
    assert "blocks when Orca is disabled or unavailable" in normalized_runtime
    assert "expected benefit, cost, and coordination overhead" in normalized_runtime
    assert "false` does not prohibit Orca selection" in normalized_runtime
    assert chief == derived_chief
    assert orca == derived_orca
    assert runtime == derived_runtime


def test_coordination_guidance_does_not_force_native_topology():
    root = Path(__file__).parents[1]
    guidance = (root / "AGENTS.md").read_text(encoding="utf-8")
    architecture = (root / "docs" / "architecture.md").read_text(encoding="utf-8")
    recovery = (root / "docs" / "recovery.md").read_text(encoding="utf-8")
    migration = (root / "docs" / "migration" / "project-os-starter.md").read_text(
        encoding="utf-8"
    )
    chief = (root / ".agents" / "skills" / "chief-of-staff" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    isolation = (root / ".agents" / "skills" / "workspace-isolation" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    writing = (root / ".agents" / "skills" / "writing-skills" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    derived_chief = (
        root / "src" / "general_os" / "assets" / "skills" / "chief-of-staff" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_isolation = (
        root / "src" / "general_os" / "assets" / "skills" / "workspace-isolation" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_writing = (
        root / "src" / "general_os" / "assets" / "skills" / "writing-skills" / "SKILL.md"
    ).read_text(encoding="utf-8")

    for text in (guidance, migration, chief):
        assert "internal runtime orchestration" in text
        assert "execution topology" in text
        assert "worker lifecycle" not in text
    for text in (architecture, recovery, chief):
        normalized_text = " ".join(text.split())
        assert "first dependency-ready" not in normalized_text
        assert "dependency-ready semantic work" in normalized_text
    assert "isolation is mandatory" not in isolation
    assert "require isolation" in isolation
    assert "Always use subagents" not in writing
    assert "50-100x context savings" not in writing
    assert "let the active runtime choose" in writing
    assert "isolated fresh context" in writing
    assert "with subagent" not in writing
    assert "CoS decides acceptance after" in chief
    assert isolation == derived_isolation
    assert writing == derived_writing
    assert chief == derived_chief


def test_publication_boundary_separates_local_git_from_external_disposition():
    root = Path(__file__).parents[1]
    publication = (root / "docs" / "rules" / "publication-boundary.md").read_text(
        encoding="utf-8"
    )
    finishing = (
        root / ".agents" / "skills" / "finishing-development-work" / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_finishing = (
        root
        / "src"
        / "general_os"
        / "assets"
        / "skills"
        / "finishing-development-work"
        / "SKILL.md"
    ).read_text(encoding="utf-8")
    derived_publication = (
        root / "src" / "general_os" / "assets" / "docs" / "rules" / "publication-boundary.md"
    ).read_text(encoding="utf-8")
    normalized_finishing = " ".join(finishing.split())

    assert "verified commits" in publication
    assert "read-only fetch" in publication
    assert "Push, merge, release, force operations" in publication
    assert "may proceed within the approved scope" in finishing
    assert "Require explicit action-specific authority for push" in normalized_finishing
    assert "Do not commit, fetch, pull" not in finishing
    assert "content-preserving local commit" in finishing
    assert finishing == derived_finishing
    assert "approved scope and repository workflow" in publication
    assert publication == derived_publication


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
    skill_dirs = sorted(path for path in skill_root.iterdir() if path.is_dir())

    assert skill_dirs
    assert not (skill_root.parent / "rules").exists()
    for skill_dir in skill_dirs:
        path = skill_dir / "SKILL.md"
        assert path.is_file()
        text = path.read_text(encoding="utf-8")
        assert text.startswith("---\n")
        frontmatter = text.split("---\n", 2)[1]
        fields = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if ":" in line
        }
        assert fields == {"name", "description"}, path
        assert next(line.split(":", 1)[1].strip() for line in frontmatter.splitlines() if line.startswith("name:")) == skill_dir.name


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


def test_deployment_sources_include_complete_runtime_skill_directories():
    root = Path(__file__).parents[1]
    skill_root = root / ".agents" / "skills"
    assert all((path / "SKILL.md").is_file() for path in skill_root.iterdir())
    development = root / "docs" / "skill-development" / "systematic-debugging"
    assert sorted(path.name for path in development.iterdir()) == [
        "CREATION-LOG.md",
        "test-academic.md",
        "test-pressure-1.md",
        "test-pressure-2.md",
        "test-pressure-3.md",
    ]
    assert not any(path.name.startswith("test-") for path in (skill_root / "systematic-debugging").iterdir())
