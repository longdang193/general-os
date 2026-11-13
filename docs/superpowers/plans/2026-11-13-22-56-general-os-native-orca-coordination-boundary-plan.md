---
layer: change
artifact_type: plan
template_id: implementation-plan
contract_version: "1"
status: completed
name: general-os-native-orca-coordination-boundary
targets:
  - docs/architecture.md
  - docs/contracts.md
  - docs/runtime-adapters.md
  - docs/deployment.md
  - .agents/skills/orca-orchestration/SKILL.md
  - src/general_os/assets/skills/orca-orchestration/SKILL.md
  - tests/test_documentation_contracts.py
  - tests/test_acceptance.py
  - tests/test_state.py
  - tests/test_git.py
  - tests/test_orca.py
---

# General OS Native Orca Coordination Boundary Plan

## Goal

Align the repository's architecture, contracts, runtime guidance, packaged skill
surface, and regression proof around one ownership invariant:

> **Project-level CoS chooses the execution boundary; the selected native runtime
> chooses execution topology.**

When CoS selects Orca, general-os hands over one independently owned semantic
workstream. The native Orca coordinator owns runtime decomposition, Runs, Tasks,
Dispatches, worker selection, supervision, retries, nested helpers, fan-in, and
cleanup. Orca returns a semantic outcome/evidence bundle for the delegated
assignment; it may represent success, partial progress, failure, or a material
blocker. General-os verifies current Git and project-level CoS performs durable
acceptance. No Python Orca scheduler,
worker registry, runtime ledger, or second coordination authority is added.

## Implementation Outcomes

### Native ownership contract is consistent across maintained documentation

`docs/architecture.md`, `docs/contracts.md`, and `docs/runtime-adapters.md`
state the same authority split for durable project semantics, coordination
judgment, boundary choice, native execution, runtime topology, Git truth,
transient evidence, and durable
acceptance. The documentation also covers qualitative Codex-versus-Orca
selection, workstream-level handoff, native fan-out/fan-in, nested workers,
execution-level failure handling, partial semantic success, and the explicit
Git/worktree result boundary. Deployment wording remains accurate: central
assets live under `~/.agents/general-os/`, project adoption is one-shot
seed-only behavior, and deployment never seeds `state/coordination.json` or
owns runtime coordination.

### Orca guidance and packaged assets describe a native coordinator handoff

`.agents/skills/orca-orchestration/SKILL.md` no longer presents
`build_orca_launch()` as the conceptual Orca orchestration boundary. It directs
the selected native coordinator to load version-matched Orca guidance and
receive a semantic workstream contract, while explicitly forbidding worker-level
topology, polling, retry, heartbeat, or runtime-ledger instructions from
general-os. `build_orca_launch()` remains a low-level one-way leaf/compatibility
helper, and the packaged mirror at
`src/general_os/assets/skills/orca-orchestration/SKILL.md` remains byte-identical
to the canonical skill.

### Regression proof protects the boundary without creating new orchestration code

Documentation contract tests assert the authority split, workstream handoff,
prohibited runtime mirrors, deployment ownership, and native coordinator
language. Existing Orca launch, state, Git snapshot, and acceptance tests remain
passing and are extended only where a direct assertion is needed to prove that
runtime completion/evidence cannot by itself complete a durable task. No new
runtime coordinator API, scheduler, registry, or durable state field is added.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `none`
- Required skills: `skill-writing-plans`, `skill-writing-skills`, `skill-code-standards`, `skill-plan-document-reviewer`, `skill-executing-plans`, `skill-verification-before-completion`
- Isolation: `current workspace`
- Commit policy: `no commits during execution`
- Preauthorized local actions: edit the named documentation, canonical skill, packaged skill mirror, and named tests; run the declared local validators and test commands; preserve unrelated workspace state
- User-approval actions: commit, push, merge, publication, destructive cleanup, or changes outside the named targets
- Parallel ownership: `none`; shared architecture and skill terms require ordered edits
- Sequential fallback: keep the same task order in one executor; do not split documentation and mirror updates because the packaged asset must follow the canonical skill

## Task Breakdown

### Task 1: Establish the current baseline and ownership map

**Purpose:**
- Capture the starting revision, overlapping target-file changes, current focused proof, and existing canonical-versus-packaged skill relationship before editing.

**Task Function:**
- Baseline and scope reconciliation.

**Template Profile:**
- Controller-selected: `none (lead controller)`
- Selection basis: deterministic local inspection with no ambiguity or implementation risk.

**Validator Profile:**
- Controller-selected: `none`
- Selection basis: no independent validator is needed for read-only baseline capture.

**Specification Coverage:**
- Preserve Git as the repository truth and preserve unrelated workspace state, including the untracked `.serena/` directory.
- Confirm `build_orca_launch()` remains a low-level compatibility helper rather than a new orchestration owner.
- Confirm the current focused tests already cover acceptance, state, Git snapshot, and Orca projection behavior.

**Required Skills:**
- `skill-code-standards`

**Files And Symbols:**
- Inspect: `docs/architecture.md`
- Inspect: `docs/contracts.md`
- Inspect: `docs/runtime-adapters.md`
- Inspect: `docs/deployment.md`
- Inspect: `.agents/skills/orca-orchestration/SKILL.md`
- Inspect: `src/general_os/assets/skills/orca-orchestration/SKILL.md`
- Inspect: `src/general_os/orca.py:build_orca_launch`
- Inspect: `tests/test_documentation_contracts.py`, `tests/test_acceptance.py`, `tests/test_state.py`, `tests/test_git.py`, `tests/test_orca.py`

**Dependencies:**
- None.

**Authority:**
- Preauthorized local actions: run read-only Git, file, hash, and focused-test commands; do not edit files in this task.
- Stop for: overlapping changes in a named target, a missing named target, a changed `HEAD` that invalidates the baseline, or a focused baseline failure that cannot be attributed to the pre-existing repository state.

**Steps:**
- [ ] Step 1: Run `git status --short --branch`, `git diff --name-only`, and `git rev-parse HEAD`; record the current revision and identify only overlapping changes in named target files as blockers. Preserve unrelated changes, including `.serena/`.
- [ ] Step 2: Compare the canonical and packaged Orca skill hashes with `Get-FileHash` and confirm they are currently identical.
- [ ] Step 3: Inspect the named docs, skill, helper, and tests; identify stale one-agent boundary language and missing native-topology prohibitions without changing source.
- [ ] Step 4: Run `python -m pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py` as the pre-edit baseline.

**Verification:**
- [ ] `git status --short --branch` and `git rev-parse HEAD`
- Expected: only the known `.serena/` untracked directory is unrelated to this plan; no tracked edits exist before execution.
- [ ] Canonical/package hash comparison
- Expected: the two Orca skill files have the same SHA-256 before the planned wording change.
- [ ] Focused pytest command
- Expected: the baseline passes, or a pre-existing failure is recorded before Task 2 begins.

**Exit Criteria:**
- The lead has a current Git baseline, confirmed target ownership, and a recorded focused-test result; no source changes were made.

### Task 2: Update the canonical architecture and contracts

**Purpose:**
- Make the durable ownership model executable and unambiguous across architecture, contracts, runtime adapters, and deployment documentation.

**Task Function:**
- Canonical contract normalization.

**Template Profile:**
- Controller-selected: `none (lead controller)`
- Selection basis: cross-document contract editing is low-risk but requires precise SSOT consistency.

**Validator Profile:**
- Controller-selected: `none`
- Selection basis: the repository documentation-contract suite is the authoritative validator.

**Specification Coverage:**
- General-os owns durable project semantics. Project-level CoS owns coordination judgment, readiness, profile selection, execution-boundary choice, and acceptance decisions; native runtimes own execution topology.
- Orca handoff is workstream-level, not worker-level.
- Runtime fan-out/fan-in, nested workers, retries, questions, supervision, and cleanup remain Orca-owned.
- Runtime completion is evidence only; Git verification remains the repository truth and project-level CoS owns durable acceptance decisions over general-os semantics.
- Runtime IDs, worker state, DAGs, heartbeats, retry counters, temporary plans, and coordinator state never enter durable general-os state.
- Git/worktree result integration is explicit; general-os does not silently merge, publish, push, or treat a runtime report as acceptance.
- Optional Orca degradation and required independent-boundary failure retain their existing semantics.
- Deployment remains central-only by default, seed-only with explicit `--repo`, and outside runtime coordination ownership.

**Required Skills:**
- `skill-code-standards`
- `skill-plan-document-reviewer`

**Files And Symbols:**
- Modify: `docs/architecture.md` sections `Fact ownership`, `Shallow routing`, and `Central deployment ownership`; add the authority split and native Orca workstream sections.
- Modify: `docs/contracts.md` sections `Execution boundary`, `Acceptance`, `Verification evidence`, and `Deployment`; define the semantic workstream handoff and evidence boundary without adding a new schema.
- Modify: `docs/runtime-adapters.md` the Orca handoff section; describe the native coordinator path before the retained `build_orca_launch()` leaf helper.
- Verify: `docs/deployment.md` commands and project-adoption wording against the actual central paths and seed-only contract; keep already-correct wording unchanged.
- Verify only: `README.md` deployment/verification references remain consistent with the corrected docs; do not modify it unless the baseline finds a stale statement in the approved scope.

**Dependencies:**
- Task 1 complete with a usable baseline.

**Authority:**
- Preauthorized local actions: edit only the named documentation sections and run documentation-focused tests; do not change Python behavior, durable state schema, deployment implementation, or Git disposition.
- Stop for: a proposed new runtime ledger, worker registry, scheduler, scoring engine, durable Orca identifier, silent Git merge/publish behavior, or a documentation requirement that conflicts with current source/tests.

**Steps:**
- [ ] Step 1: Add one concise authority table or equivalent structured section to `docs/architecture.md` covering project goal/task/dependency/constraint/acceptance ownership, Codex execution, Orca coordinator topology, Git truth, and CoS acceptance.
- [ ] Step 2: Define the Orca workstream contract in `docs/architecture.md` and `docs/contracts.md` using only objective, semantic task identity, relevant context/constraints, acceptance/evidence requirements, resolved explicit profile facts, and repository/work boundary information.
- [ ] Step 3: Explicitly list worker-level topology that must not cross the boundary: worker count/roles/IDs, Run/Task/Dispatch IDs, runtime DAG, polling/heartbeat state, retry counters, temporary plans, nested helper identities, and runtime progress.
- [ ] Step 4: Document that the native Orca coordinator absorbs runtime chatter and returns one semantic outcome/evidence bundle per delegated assignment; the bundle may represent success, partial progress, failure, or a material blocker. Document upward escalation only for material authority, dependency, user, credential, Git, boundary, or acceptance blockers.
- [ ] Step 5: Document partial semantic success and recovery from runtime loss: verify useful outcomes independently, derive remaining work from durable state and current Git, and start a fresh native runtime instead of reconstructing a lost Orca episode.
- [ ] Step 6: Replace the one-agent conceptual framing in `docs/runtime-adapters.md` while preserving the existing one-way profile projection, native-default inheritance, status observation, and required-boundary degradation rules.
- [ ] Step 7: Recheck `docs/deployment.md` and `README.md` for the actual `~/.agents/general-os/` path, absence of `state/coordination.json` from the project kit, explicit one-shot adoption, and no generated runtime tree; keep both unchanged when their current wording already satisfies the contract.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py tests/test_deployment.py tests/test_cli.py`
- Expected: current documentation ownership tests pass after the canonical wording changes.
- [ ] `rg -n "worker registry|Run registry|Task registry|Dispatch registry|heartbeat|runtime DAG|worker count|fan-out strategy|polling interval|coordinator state" docs/architecture.md docs/contracts.md docs/runtime-adapters.md`
- Expected: these terms appear only in explicit prohibition/ownership statements, never as general-os-owned durable mechanisms.
- [ ] `rg -n "~/.agents/general-os|state/coordination.json|seed-only|--repo|runtime registry|generated.*runtime" docs/deployment.md README.md docs/architecture.md docs/contracts.md`
- Expected: deployment ownership and no-runtime-state wording point to the actual central paths and explicit adoption boundary.

**Exit Criteria:**
- The four maintained docs express one consistent architecture without introducing implementation machinery or contradicting existing source/test contracts.

### Task 3: Revise the Orca orchestration skill and packaged mirror

**Purpose:**
- Make native Orca internal orchestration/execution-topology ownership the operational guidance while retaining the existing low-level launch helper for compatibility.

**Task Function:**
- Canonical skill maintenance and package-surface synchronization.

**Template Profile:**
- Controller-selected: `none (lead controller)`
- Selection basis: the task is a bounded documentation/skill edit with an exact canonical-to-package mirror requirement.

**Validator Profile:**
- Controller-selected: `none`
- Selection basis: byte comparison plus the documentation contract suite directly validates the mirror.

**Specification Coverage:**
- CoS chooses Orca only for an independently owned semantic workstream.
- The selected native Orca coordinator decides decomposition and topology.
- `build_orca_launch()` remains a low-level leaf/compatibility helper and is not the conceptual orchestration boundary.
- Native Orca guidance owns the installed version's internal orchestration lifecycle, worker topology, nested helpers, retries, questions, fan-in, release, and cleanup.
- General-os receives evidence, verifies current Git, and owns acceptance; runtime IDs and lifecycle facts remain transient.

**Required Skills:**
- `skill-writing-skills`
- `skill-code-standards`

**Files And Symbols:**
- Modify: `.agents/skills/orca-orchestration/SKILL.md`
- Modify mirror: `src/general_os/assets/skills/orca-orchestration/SKILL.md`
- Preserve: `src/general_os/orca.py:OrcaLaunch`, `src/general_os/orca.py:build_orca_launch`, and `src/general_os/orca.py:OrcaCliStatusObserver`
- Verify: `.agents/skills/orca-orchestration/SKILL.md` and `src/general_os/assets/skills/orca-orchestration/SKILL.md` have identical content after the edit.

**Dependencies:**
- Task 2 complete; the skill must use the final contract vocabulary.

**Authority:**
- Preauthorized local actions: edit the canonical Orca skill and its tracked packaged mirror; run skill-maintenance and mirror-validation commands; do not add or alter runtime code, CLI commands, or Orca lifecycle APIs.
- Stop for: a request to implement a Python Orca coordinator, a new durable runtime identifier, a new worker/Run/Task registry, a new general-os topology limit, or a mismatch between canonical and packaged skill ownership.

**Steps:**
- [ ] Step 1: Replace the handoff instructions that make `build_orca_launch(project_profile(profile), assignment)` the canonical path with a workstream-level handoff to the native Orca coordinator/coordinating agent provided by the installed version after loading `orca skills get orchestration --full`.
- [ ] Step 2: State the allowed handoff fields and the forbidden worker/topology fields using the contract in Task 2.
- [ ] Step 3: State that Orca handles internal decomposition, fan-out/fan-in, supervision, retries, bounded worker questions, nested helpers, and cleanup, then returns one semantic outcome/evidence bundle that may report success, partial progress, failure, or a material blocker.
- [ ] Step 4: State that general-os owns durable project semantics, project-level CoS performs fresh Git inspection, verification, and acceptance decisions, and Orca completion cannot transition a general-os task by itself.
- [ ] Step 5: Keep `build_orca_launch()` documented as a low-level compatibility/leaf projection only, with no new call path or runtime behavior.
- [ ] Step 6: Treat `.agents/skills/orca-orchestration/SKILL.md` as the SSOT and copy its final content to the derived package asset at `src/general_os/assets/skills/orca-orchestration/SKILL.md`; do not build a synchronization framework.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py tests/test_orca.py`
- Expected: skill wording and existing launch projection tests pass.
- [ ] `if ((Get-FileHash '.agents/skills/orca-orchestration/SKILL.md').Hash -ne (Get-FileHash 'src/general_os/assets/skills/orca-orchestration/SKILL.md').Hash) { throw 'Orca skill mirror drift' }`
- Expected: the canonical and packaged skill hashes match exactly.
- [ ] `rg -n "build_orca_launch|Run|Task|Dispatch|worker|fan-in|runtime IDs|acceptance|Git" .agents/skills/orca-orchestration/SKILL.md src/general_os/assets/skills/orca-orchestration/SKILL.md`
- Expected: `build_orca_launch` is described as a leaf/compatibility helper, while native coordinator ownership and CoS acceptance are explicit.

**Exit Criteria:**
- Both maintained skill surfaces teach native Orca coordination without adding a general-os execution topology or changing `src/general_os/orca.py`.

### Task 4: Add focused contract assertions and reconcile existing proof

**Purpose:**
- Turn the architecture boundary into executable regression proof while reusing existing acceptance, state, Git, and Orca tests instead of adding duplicate runtime machinery.

**Task Function:**
- Contract-test hardening and proof reconciliation.

**Template Profile:**
- Controller-selected: `none (lead controller)`
- Selection basis: focused assertions over existing test owners; no new runtime behavior is planned.

**Validator Profile:**
- Controller-selected: `none`
- Selection basis: the full repository suite and validators provide the final independent proof surface.

**Specification Coverage:**
- Workstream-level handoff and native topology ownership are tested in maintained documentation.
- Runtime evidence is transient and cannot become durable state.
- Acceptance remains verifier- and current-Git-bound, including required Orca boundary evidence.
- Existing launch projection and status observation remain compatible.
- Existing Git/worktree identity semantics remain the acceptance boundary.

**Required Skills:**
- `skill-code-standards`
- `skill-verification-before-completion`

**Files And Symbols:**
- Modify: `tests/test_documentation_contracts.py` tests `test_orca_skill_and_runtime_docs_keep_native_ownership_explicit`, `test_native_cos_keeps_orca_optional_but_allows_material_independence`, and `test_profile_projection_is_canonical_and_one_way`; add one focused architecture/deployment boundary test and one canonical-to-derived skill equality assertion in this file.
- Verify without changing: `tests/test_acceptance.py:test_required_boundary_needs_typed_matching_evidence` and `tests/test_acceptance.py:test_pass_requires_verifier_produced_result`.
- Verify without changing: `tests/test_state.py:test_state_rejects_runtime_identity_and_progress_fields` and `tests/test_state.py:test_state_serialization_does_not_add_runtime_fields`.
- Verify without changing: `tests/test_git.py:test_snapshot_identity_changes_with_tracked_and_untracked_content` and `tests/test_git.py:test_snapshot_identity_distinguishes_staged_content_with_same_worktree`.
- Preserve and run: `tests/test_orca.py` launch/status tests; no new native scheduler or topology simulation is required.

**Dependencies:**
- Tasks 2 and 3 complete.

**Authority:**
- Preauthorized local actions: add or adjust only focused assertions in the named test owners; run the focused and full validation commands; do not weaken an existing assertion to accommodate stale documentation.
- Stop for: a test failure requiring production runtime changes, a new durable state field, a new Orca API, or a change to acceptance semantics outside the approved ownership contract.

**Steps:**
- [ ] Step 1: Add documentation assertions for the authority table, semantic workstream handoff, native coordinator/topology ownership, fan-in, acceptance outside Orca, explicit Git result boundary, actual deployment path, and absence of `state/coordination.json` from project adoption.
- [ ] Step 2: Add negative assertions that general-os docs and skills do not prescribe worker counts, worker registries, runtime DAG ledgers, polling/heartbeat state, retry counters, or a second Orca coordinator authority.
- [ ] Step 3: Run the existing acceptance tests to prove a matching typed Orca boundary receipt is required for a required independent task and that a caller-forged/runtime-only result cannot produce `PASS`; do not alter their established semantics.
- [ ] Step 4: Run the existing state tests to prove runtime identity/progress fields remain rejected and serialized coordination state remains semantic-only; do not add a runtime field to the schema.
- [ ] Step 5: Run the existing Git tests to prove staged/unstaged/untracked repository state changes snapshot identity, preserving the handoff rule that Git integration is verified at the current boundary; do not change Git snapshot ownership.
- [ ] Step 6: Keep existing Orca projection tests green; do not add a native scheduler or simulate Orca worker topology in unit tests.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py tests/test_deployment.py tests/test_cli.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py`
- Expected: all focused contract, acceptance, state, Git, and Orca tests pass.
- [ ] `git diff --check`
- Expected: no whitespace errors.

**Exit Criteria:**
- The tests fail when the ownership boundary regresses and pass without requiring any new general-os runtime orchestration implementation.

### Task 5: Run final repository verification and reconcile the plan

**Purpose:**
- Prove the complete documentation/skill/test change against one current Git revision and leave the plan ready for a later approved execution handoff.

**Task Function:**
- Final verification and plan reconciliation.

**Template Profile:**
- Controller-selected: `none (lead controller)`
- Selection basis: deterministic repository-wide verification.

**Validator Profile:**
- Controller-selected: `none`
- Selection basis: `skill-verification-before-completion` owns fresh final evidence.

**Specification Coverage:**
- All implementation outcomes in this plan.
- Preservation of unrelated `.serena/` state and prohibition on commit/push during plan execution.

**Required Skills:**
- `skill-verification-before-completion`

**Files And Symbols:**
- Verify: all plan targets plus `state/coordination.json`, `docs/migration/project-os-starter.md`, `scripts/validate_migration_manifest.py`, and the package metadata in `pyproject.toml`.
- Preserve: unrelated `.serena/` content and any pre-existing tracked state.

**Dependencies:**
- Tasks 1–4 complete.

**Authority:**
- Preauthorized local actions: run final tests, validators, deterministic deployment tests, optional live diagnostics, diff/status inspections, and preserve unrelated workspace state.
- Stop for: an introduced regression, overlapping target-file change, package mirror drift, migration/state validation failure, or request for commit/push/publication.

**Steps:**
- [ ] Step 1: Run the focused suite again after all edits.
- [ ] Step 2: Run the full suite with `python -m pytest -q`.
- [ ] Step 3: Run `python -m general_os state validate state/coordination.json`.
- [ ] Step 4: Run `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`.
- [ ] Step 5: Run the deterministic deployment and CLI regression tests; use `python -m general_os deploy --repo . --adapter codex --dry-run` as a read-only diagnostic. A live `--check` may be collected as informational evidence but is not a completion gate because it depends on the user's central installation.
- [ ] Step 6: Run the canonical/package skill hash comparison and `git diff --check`.
- [ ] Step 7: Inspect `git diff --stat`, `git diff --name-only`, `git status --short --branch`, and `git rev-parse HEAD`; confirm only approved target files changed and unrelated workspace state remains untouched.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py tests/test_deployment.py tests/test_cli.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py`
- Expected: focused suite passes.
- [ ] `python -m pytest -q`
- Expected: full suite passes.
- [ ] `python -m general_os state validate state/coordination.json`
- Expected: state is valid.
- [ ] `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`
- Expected: migration manifest matches the maintained tree.
- [ ] `python -m general_os deploy --repo . --adapter codex --dry-run`
- Expected: dry-run succeeds without modifying the repository or user installation; this is diagnostic evidence, not the deterministic deployment gate.
- [ ] Optional diagnostic: `python -m general_os deploy --repo . --adapter codex --check`
- Expected: record the live central/adoption result when available; do not fail completion solely because the user's installation has unrelated drift.
- [ ] `git diff --check`
- Expected: no whitespace errors.
- [ ] Git status and revision inspection
- Expected: no unexpected tracked changes, `.serena/` remains unrelated and untouched, and the observed revision is recorded as evidence.

**Exit Criteria:**
- Every task has fresh proof, the final diff contains only the approved architecture/contract/skill/test surfaces, no runtime topology or durable mirror was added, and the plan is ready for handoff to `skill-executing-plans` after separate user approval.

## Verification

Final artifact-level verification is the Task 5 command set:

- `python -m pytest -q tests/test_documentation_contracts.py tests/test_deployment.py tests/test_cli.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py`
- `python -m pytest -q`
- `python -m general_os state validate state/coordination.json`
- `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`
- `python -m general_os deploy --repo . --adapter codex --dry-run`
- Optional diagnostic: `python -m general_os deploy --repo . --adapter codex --check`
- `git diff --check`
- Canonical/package skill hash comparison
- `git status --short --branch`
- `git rev-parse HEAD`

The plan must not perform commit, push, merge, publication, destructive cleanup,
or changes to the unrelated `.serena/` directory. The plan file is immutable
during execution; evidence belongs in the execution/final verification report.
A later authorized execution
must use `skill-executing-plans`, then `skill-verification-before-completion`,
and a separately authorized finishing skill for any Git disposition.

## Completion Criteria

The plan is ready for completion verification when:

1. the ownership invariant is represented consistently in architecture,
   contracts, runtime adapters, deployment wording, and the Orca skill;
2. canonical and packaged skill content are identical;
3. focused contract tests prove the native-boundary and acceptance invariants;
4. existing state, Git, profile projection, and Orca leaf behavior remain intact;
5. the full suite, state validator, migration validator, deterministic deployment tests, deployment dry-run, and
   diff checks pass on the current Git revision;
6. no unexpected tracked file changes or unrelated workspace modifications are
   introduced;
7. no commit, push, merge, publication, cleanup, or new runtime authority is
   performed by this plan.

This plan remains `proposed` until implementation and fresh verification are
complete. Only `skill-verification-before-completion` may establish a verified
completion result; a later explicitly authorized finishing workflow owns commit
or push.
