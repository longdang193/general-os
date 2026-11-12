---
layer: change
artifact_type: plan
status: completed
template_id: implementation-plan
name: general-os-review-findings-remediation
targets:
  - .agents/skills/
  - docs/migration/project-os-starter.md
  - docs/contracts.md
  - src/general_os/acceptance.py
  - src/general_os/cli.py
  - src/general_os/git.py
  - src/general_os/policy.py
  - src/general_os/state.py
  - tests/test_acceptance.py
  - tests/test_cli.py
  - tests/test_documentation_contracts.py
  - tests/test_policy.py
  - tests/test_state.py
---

# general-os Review Findings Remediation Plan

## Outcome

Bring the committed `general-os` SSOT migration and durable coordination
contracts into agreement with the reviewed design at
`8dc83c5e96a37ea98e0c718fda809ae3e871b802`.

The implementation will:

- remove active predecessor-only skill, rule, template, and adapter references;
- make required independent-boundary acceptance reject caller-forged evidence;
- make repository-bound acceptance fail closed when Git identity is missing;
- preserve compare-and-write protection for every update to existing state;
- prevent durable authority exceptions from widening policy without provenance
  and expiry, or reject durable allow overrides when those fields are absent;
- require a typed, durable reason for material `BLOCKED` state; and
- expand documentation and migration tests so the maintained surface cannot
  silently regress.

## Preserved Behavior

- Git remains the repository and recovery truth.
- `general-os` remains a durable semantic layer, not a Codex or Orca scheduler.
- Codex remains the default execution harness; native delegation remains
  internal to Codex; Orca remains optional independent orchestration.
- The existing state file remains the single durable coordination object.
- Atomic state replacement, loaded-state digest checks, local policy deny
  ceilings, profile projection, and retryable `FAIL` transitions remain.
- No new runtime ledger, worker registry, scheduler, profile registry, or
  orchestration authority is introduced.

## Exclusions

- No production deployment hardening or live Orca worker execution proof.
- No redesign of the Codex, native-subagent, or Orca lifecycle.
- No cleanup of unrelated untracked `.serena/` workspace state.
- No changes to historical migration tables except correcting their active
  disposition claims.

## Execution Approach

- **Mode:** inline sequential.
- **Coordination:** none; one lead executor owns the ordered changes.
- **Isolation:** current checkout; preserve unrelated `.serena/` state.
- **Commit policy:** implementation commits are created only after task-local
  proof; no commit is required while this plan remains proposed.
- **Shared-write control:** Tasks 2–4 share acceptance, state, policy, CLI, and
  test surfaces and therefore run serially. Documentation inventory changes
  precede all behavior changes because they establish the active owner names.
- **Fallback:** if a required runtime capability is unavailable, use source,
  unit, and contract probes; do not claim live Orca evidence.

## Task 1: Complete the active SSOT migration surface

**Purpose:** Remove operational dead ends and make the migration manifest agree
with the committed tree.

**Task Function:** Migration/reference-integrity remediation.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Single-source-of-truth migration, native-first
execution, retired peer orchestration, and no predecessor runtime dependency.

**Required Skills:** `skill-code-standards`, `skill-writing-skills`,
`skill-verification-before-completion`.

**Files And Symbols:**

- Every active `.agents/skills/*/SKILL.md` and supporting Markdown resource.
- `docs/migration/project-os-starter.md` rule disposition table.
- `docs/runtime-adapters.md` and `AGENTS.md` as existing runtime/ownership
  owners.
- `tests/test_documentation_contracts.py` maintained-surface tests.

**Dependencies:** None.

**Authority:** Edit maintained skills, migration documentation, and their tests.
Stop if a proposed replacement would create a new runtime authority or require
an unresolved product decision.

**Steps:**

1. Enumerate every active skill Markdown file and collect references to local
   paths, retired skill names, predecessor rule names, and predecessor adapter
   scripts. Exclude only the historical migration table and historical plan
   prose from active-reference enforcement.
2. Replace predecessor coordination names by owner-aligned maintained skills:
   use `executing-work` for bounded native execution, `orca-orchestration` for
   independently managed Orca work, and `verification-before-completion` for
   final verification.
3. Replace the nonexistent `repository operating guidance/tooling/runtime-tool-resolution.md`
   references with the existing `docs/runtime-adapters.md` owner where runtime
   capability resolution is actually required. Remove optional references to
   nonexistent audit templates, OCR adapters, and predecessor-only tooling
   instead of recreating those resources.
4. Replace predecessor backend/frontend rule references with their maintained
   owning skills (`backend-verification` and `full-stack-integration`) or with
   `AGENTS.md` when the rule is repository-wide ownership guidance.
5. Change the migration manifest disposition for `backend-verification-rule.md`
   from the absent `docs/rules/backend-verification.md` destination to the
   maintained `backend-verification` skill owner.
6. Extend `test_migrated_skills_use_current_owners_and_available_resources` or
   add adjacent helpers in `tests/test_documentation_contracts.py` to scan all
   maintained skills, reject retired names, and verify every referenced local
   destination exists.

**Verification:**

- `rg -n -i "repository operating guidance|scripts/ocr_delegate_adapter|skill-dispatching-parallel-agents|skill-subagent-driven-development|skill-verification-before-completion" .agents/skills`
  returns no active matches.
- The manifest destination check passes for every disposition that claims a
  committed file.
- `python -m pytest -q tests/test_documentation_contracts.py` passes.

**Exit Criteria:** All maintained skill references resolve to current owners or
explicitly optional existing capabilities; no active predecessor dependency or
missing manifest destination remains.

## Task 2: Make acceptance evidence fail closed

**Purpose:** Prevent a caller from satisfying a required independent boundary
or repository-bound `PASS` with fabricated or incomplete evidence.

**Task Function:** Acceptance-contract hardening.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Acceptance outside workers, current Git evidence,
selected execution boundary, and runtime state recovery.

**Required Skills:** `skill-backend-verification`, `skill-code-standards`,
`skill-test-driven-development`.

**Files And Symbols:**

- `src/general_os/acceptance.py`: `BoundaryEvidence`, `VerificationResult`,
  `evaluate_acceptance`, and `apply_task_transition`.
- `src/general_os/cli.py`: `run_accept` and `build_parser`.
- `src/general_os/git.py`: `GitSnapshot` identity contract.
- `tests/test_acceptance.py` and `tests/test_cli.py`.
- `docs/contracts.md` acceptance wording.

**Dependencies:** Task 1.

**Authority:** Change acceptance semantics and focused regression tests only.
Stop if trusted runtime evidence cannot be distinguished from caller-provided
text without introducing a new runtime ledger or scheduler.

**Steps:**

1. Define the currently supported independent boundary as `orca` in the
   acceptance contract. Reject unknown and `codex` boundary kinds for tasks
   that require an independent boundary.
2. Require a non-null Git snapshot identity for repository-bound `PASS`; reject
   missing verification identity rather than making the comparison conditional.
3. Remove free-form `--boundary-evidence` parsing from `general_os accept`.
   The CLI must reject acceptance of a required-boundary task unless a trusted
   runtime integration supplies typed evidence through the library boundary;
   arbitrary JSON must never become proof by being caller-declared.
4. Keep a positive library path for matching `orca` evidence and a negative
   path for missing, stale, unknown, and caller-forged evidence. Preserve
   normal acceptance for tasks that do not require an independent boundary.
5. Update `docs/contracts.md` to state the supported boundary kind, mandatory
   snapshot identity, and the CLI restriction without claiming live Orca proof.

**Verification:**

- Add tests for `kind="codex"`, unknown kinds, missing identity, stale identity,
  and matching `kind="orca"` evidence.
- Add a CLI test proving free-form boundary JSON cannot produce `PASS`.
- `python -m pytest -q tests/test_acceptance.py tests/test_cli.py` passes.
- Direct probe result for fabricated evidence is `FAIL`, never `PASS`.

**Exit Criteria:** Required-boundary and repository-bound `PASS` decisions are
only possible with supported, matching evidence; no CLI argument can forge
independent-boundary proof.

## Task 3: Restore strict compare-and-write updates

**Purpose:** Prevent a fresh in-memory state object from silently replacing an
existing durable coordination state file.

**Task Function:** Durable state concurrency hardening.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Git-backed recovery truth, optimistic concurrency,
atomic persistence, and one durable state owner.

**Required Skills:** `skill-backend-verification`, `skill-code-standards`,
`skill-test-driven-development`.

**Files And Symbols:**

- `src/general_os/state.py`: `save_state` and `_source_digest` handling.
- `tests/test_state.py`: loaded-writer and concurrent-writer coverage.

**Dependencies:** Task 2.

**Authority:** Change state persistence and tests only. Preserve unrelated
untracked files and do not add a second state store.

**Steps:**

1. In `save_state`, distinguish creation from update under the existing state
   lock. Allow a digest-less state only when the destination does not exist.
2. Raise `StateError` when an existing destination is updated without a loaded
   source digest. Keep the existing digest mismatch error for stale loaded
   writers and retain atomic temporary-file replacement.
3. Add a regression test that creates a state file, attempts to save a fresh
   replacement without loading it, and asserts rejection.
4. Retain and rerun the existing stale-loaded-state and two-process writer
   tests to prove the concurrency contract remains intact.

**Verification:**

- `python -m pytest -q tests/test_state.py` passes.
- A digest-free overwrite probe raises `StateError`.
- Existing creation and loaded-update round trips still pass.

**Exit Criteria:** Every update to an existing state file carries loaded-state
provenance or is explicitly rejected; no stale writer can replace newer state.

## Task 4: Bound durable authority exceptions and blocked state

**Purpose:** Prevent durable policy widening and preserve the cause of material
blockers through runtime loss.

**Task Function:** Policy and recovery-contract hardening.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Lightweight exceptional authority, local deny
ceiling, durable recovery context, and retryable versus material failure.

**Required Skills:** `skill-backend-verification`, `skill-code-standards`,
`skill-test-driven-development`.

**Files And Symbols:**

- `src/general_os/policy.py`: `AuthorityExceptions` and `resolve_policy`.
- `src/general_os/state.py`: `Task`, `CoordinationState`, and serialization.
- `src/general_os/acceptance.py`: `VerificationResult`,
  `AcceptanceDecision`, and `apply_task_transition`.
- `src/general_os/cli.py`: `run_accept` and acceptance arguments.
- `tests/test_policy.py`, `tests/test_state.py`, `tests/test_acceptance.py`, and
  `tests/test_cli.py`.
- `docs/contracts.md` and the reviewed implementation plan’s policy section.

**Dependencies:** Task 3.

**Authority:** Preserve the hard local `deny` ceiling. Do not add a new
permission system. Stop if policy provenance requires an external identity or
service unavailable in this personal-local repository.

**Steps:**

1. Keep transient runtime policy resolution available for the existing native
  execution path, but reject durable `remote_side_effects="allow"` exceptions
   unless the durable representation carries explicit scope, provenance, and
   expiry. Prefer the existing safe default and fail closed when metadata is
   absent.
2. Add a minimal durable blocker representation to `Task` containing a fixed
   category (`authority`, `dependency`, `git`, or `external`) and a non-empty
   reason. Validate that only blocked tasks carry blocker data and serialize it
   as durable recovery context.
3. Require category and reason for `BLOCKED` transitions. Clear blocker data
   when a blocked task returns to `pending` after retryable `FAIL`, and preserve
   idempotency for repeated transitions.
4. Expose the category and reason through the CLI only for the `blocked` status;
   reject missing or unknown values. Keep retryable `FAIL` separate from a
   material blocker.
5. Add policy, state, acceptance, and CLI tests for unscoped allow, deny-to-allow
   attempts, expired metadata, invalid blocker categories, missing reasons, and
   blocked-to-pending recovery.

**Verification:**

- `python -m pytest -q tests/test_policy.py tests/test_state.py tests/test_acceptance.py tests/test_cli.py` passes.
- A durable allow without scope, provenance, and expiry is rejected or remains
  at the configured ceiling.
- A blocked task round-trips its category and reason; retryable failure clears
  the blocker and returns the task to `pending`.

**Exit Criteria:** Durable authority cannot be widened by unscoped data, local
deny remains absolute, and recovery can distinguish material blockers from
retryable verification failures.

## Task 5: Reconcile documentation and migration contracts

**Purpose:** Make the public contract and migration tests describe the enforced
behavior rather than the reviewed-but-unimplemented claims.

**Task Function:** Contract/documentation reconciliation.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Fact ownership, acceptance boundaries, migration
cutover, and source/test authority.

**Required Skills:** `skill-code-standards`, `skill-writing-skills`,
`skill-verification-before-completion`.

**Files And Symbols:**

- `docs/contracts.md`.
- `docs/migration/project-os-starter.md`.
- `docs/superpowers/plans/2026-11-12-00-37-general-os-ssot-migration-and-coordination-hardening-plan.md`
  only where completed claims no longer match the implementation.
- `tests/test_documentation_contracts.py`.

**Dependencies:** Tasks 1–4.

**Authority:** Update only claims affected by the implemented fixes. Do not
rewrite historical review evidence or create duplicate governance documents.

**Steps:**

1. Update contracts for required snapshot identity, supported independent
   boundary evidence, strict state updates, durable blocker context, and policy
   exception limits.
2. Correct migration dispositions and active-surface inventory counts without
   deleting historical predecessor entries.
3. Extend documentation tests to validate all active references, all manifest
   destinations, and the absence of generated `.agents/rules/` or second
   registries.
4. Reconcile plan completion statements so checked items describe behavior that
   the source and tests actually prove.

**Verification:**

- `python -m pytest -q tests/test_documentation_contracts.py` passes.
- Active scans and manifest-to-tree checks are clean.
- No documentation claims a runtime capability that is not implemented or
  directly evidenced.

**Exit Criteria:** Documentation, migration manifest, tests, and source agree on
the same owners, evidence requirements, and supported boundaries.

## Task 6: Fresh final verification and handoff

**Purpose:** Prove the complete remediation against the current Git revision.

**Task Function:** Final verification and acceptance preparation.

**Template Profile:** unresolved; resolve through Planning Dispatch before
activation.

**Specification Coverage:** Fresh verification, Git evidence, and acceptance
outside the worker.

**Required Skills:** `skill-verification-before-completion` and
`skill-backend-verification`.

**Files And Symbols:** All files changed by Tasks 1–5; no additional owner.

**Dependencies:** Tasks 1–5.

**Authority:** Read-only verification and plan reconciliation. Do not merge,
push, or delete branches without separate explicit Git disposition approval.

**Steps:**

1. Run `python -m pytest -q`.
2. Run `python -m general_os state validate state/coordination.json`.
3. Run the focused suite:
   `python -m pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py tests/test_policy.py tests/test_cli.py`.
4. Run `git diff --check` and inspect `git status --short` to confirm only
   task-owned changes are present; preserve `.serena/` if still untracked.
5. Re-run the active-reference and manifest-destination probes from Task 1.
6. Reconcile every task exit criterion with fresh output and mark this plan
   `completed` only through `skill-verification-before-completion` after all
   required evidence is present.

**Verification:**

- Full suite passes with no unexpected skips.
- State validation reports `valid`.
- Focused suite passes.
- Git diff check is clean and the final revision is identifiable.
- No live Orca or production-load claim is included unless separately observed.

**Exit Criteria:** The implementation is ready for a separately authorized Git
publication and branch-disposition decision; this plan does not perform either.

## Findings Intentionally Excluded

The review runs completed with verified model, effort, authenticated context,
conversation identity, and commit-pinned evidence. No run was incomplete.
Claims requiring live Orca execution, production load, or external service
behavior were not treated as findings or completion evidence because neither
review established them.

## Execution Evidence

- Full suite: `87 passed`.
- Focused suite (`documentation_contracts`, `acceptance`, `state`, `git`,
  `orca`, `policy`, and `cli`): `70 passed`.
- State validation: `valid` for `state/coordination.json`.
- `git diff --check`: clean.
- Publication: remediation commit `21faee2dc6fe3b6789993aebfc3fa43bdc398471`
  was merged into `main` at `95b7fb5b337e78f2cdd9cb8ce71fc82df8a5462c`.
- Review: the single authorized independent `review-1` cycle inspected the
  prior PR head, found two blocking issues and one non-blocking documentation
  issue; all three were addressed before merge, with no second cycle started.
