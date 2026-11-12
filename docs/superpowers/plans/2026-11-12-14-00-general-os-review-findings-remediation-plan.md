---
layer: change
artifact_type: plan
status: completed
template_id: implementation-plan
contract_version: "1"
name: general-os-review-findings-remediation
targets:
  - src/general_os/git.py
  - src/general_os/acceptance.py
  - src/general_os/orca.py
  - src/general_os/cli.py
  - docs/contracts.md
  - docs/recovery.md
  - .agents/skills/github-browser-reviews/SKILL.md
  - .agents/skills/chief-of-staff/SKILL.md
  - .agents/skills/orca-orchestration/SKILL.md
  - .agents/skills/dashboard-reporting/SKILL.md
  - .agents/skills/requesting-code-review/SKILL.md
  - .agents/skills/reviewing-pull-requests/SKILL.md
  - .agents/skills/wayfinding/SKILL.md
  - .agents/skills/receiving-code-review/SKILL.md
  - docs/templates/coordination-state.json
  - tests/
---

# General-OS Review Findings Remediation Plan

## Goal

Correct the findings independently validated against
`longdang193/general-os@1a33fddbfb058ccfdc4f244c2fb10aa8bae2e702` while
preserving the small, native-first, fact-derived design. Do not add a runtime
ledger, scheduler, profile registry, worker registry, or publication authority.

## Implementation Outcomes

### Git-bound acceptance evidence

`GitSnapshot.identity` distinguishes staged and unstaged tracked contents,
reports status paths without losing porcelain columns, and ignores the tracked
coordination-state file when hashing work identity so saving durable semantic
state does not invalidate the work it records.

### Trusted task-bound acceptance

Verifier-produced PASS evidence is task-bound to both the current Git work
identity and a deterministic fingerprint of the acceptance-relevant task
contract. Successful reverification updates both accepted identities rather
than retaining stale evidence.

### Native boundary and documentation alignment

Orca receives the ephemeral assignment separately from profile projection,
smoke output names reachability precisely, CoS applies `orca_enabled`, and
maintained guidance no longer requires publication or points at predecessor-only
owners. The state template emits schema version `1`.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `git-tracked`
- Required skills: `skill-writing-plans`, `skill-backend-verification`, `skill-verification-before-completion`
- Isolation: `current workspace`
- Commit policy: `no commits during execution`
- Preauthorized local actions: edit listed files, run declared tests and read-only Git/status/probe commands, and update this plan with evidence
- User-approval actions: commit, push, merge, publication, destructive cleanup, or external runtime mutation
- Parallel ownership: none
- Sequential fallback: complete source/test fixes before documentation reconciliation, then run final verification

## Coordination State

- Coordination owner: `single lead controller`
- Coordination schema: `2`
- Branch: `main`
- Base commit: `1a33fddbfb058ccfdc4f244c2fb10aa8bae2e702`
- Expected workspace: `published HEAD with unrelated .serena/ preserved`
- Next action: `none; implementation and exact-SHA verification complete`
- Blockers: `none`

## Review Evidence

Two sequential, same-profile GitHub reviews completed at the pinned commit:

- `GPT-5.6-Sol`, `High`, run `run-QTiht4`, chat `6af5a66a-3cec-83ed-8775-7620679a9905`.
- `GPT-6`, `High`, run `run-VvW1qR`, chat `6af5a760-3218-83eb-9ff1-a37725f4e9e0`.

Both final visible responses cited the requested full SHA. Findings below are
included only where source inspection or a local reproduction confirms them.
The disagreement about conservative whole-snapshot invalidation is resolved by
the direct reproduction: saving tracked `state/coordination.json` changes the
identity immediately, so that path must not participate in work identity.

The suggestion to change `plan-document-reviewer` was not included: its
repository-memory reference resolves through the current `AGENTS.md`, so source
evidence does not establish a broken owner.

A follow-up GPT-5.6-Sol review of this plan at
`general-os@1a33fddbfb058ccfdc4f244c2fb10aa8bae2e702` found two high-severity
issues and one low-severity audit issue. Source inspection and a targeted
acceptance probe confirmed all three. The review completed in chat
`6af5b190-1990-83ed-8681-0161a7680002` with run `run-QjOLiW`.

## Task Breakdown

| Task | State | Workspace | Executor | Depends On | Required Proof | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Task 1 | `completed` | current | `lead` | none | Git regression tests | `12 passed` |
| Task 2 | `completed` | current | `lead` | Task 1 | acceptance regression tests | `22 passed` |
| Task 3 | `completed` | current | `lead` | Task 2 | Orca/CLI tests and smoke | `33 passed; ready/reachable` |
| Task 4 | `completed` | current | `lead` | Task 3 | documentation and template tests | `28 passed; 44 manifest rows valid` |
| Task 5 | `completed` | current | `lead` | Task 4 | full verification commands | `112 passed; state valid` |
| Task 6 | `completed` | current | `lead` | Task 5 | acceptance-contract regression tests | `41 passed` |
| Task 7 | `completed` | current | `lead` | Task 6 | exact-SHA clean-checkout verification and plan reconciliation | `115 passed; state/migration valid; Orca ready` |

### Follow-up findings

- `state/coordination.json` must remain outside Git work identity while its
  acceptance-relevant task semantics receive their own durable fingerprint.
- Final verification must be rerun against the exact published remediation SHA,
  not the pre-publication base SHA recorded by the earlier execution.
- Completed inline tasks must not retain unresolved executor or validator
  profile placeholders; mark those roles not applicable when no delegation was
  used.

### Task 1: Repair Git snapshot identity and status parsing

**Purpose:** Make repository evidence complete for staged changes, accurate for
status paths, and stable across durable coordination-state saves.

**Task Function:** Git evidence correction.

**Template Profile:**
- Not applicable: inline lead; no delegated executor.
- Selection basis: resolve from implementation risk before activation.

**Validator Profile:**
- Not applicable: inline lead; no delegated validator.
- Selection basis: independently exercise isolated Git repositories.

**Specification Coverage:** Git owns repository truth; accepted evidence must
be bound to the complete work snapshot without self-invalidating state writes.

**Required Skills:** `skill-backend-verification`

**Files And Symbols:**
- Modify: `src/general_os/git.py:GitRepository.inspect`, `_identity`, status parsing.
- Verify: `tests/test_git.py`.
- Document: `docs/contracts.md` and `docs/recovery.md`.

**Dependencies:** direct reproduction above; no external runtime.

**Authority:**
- Preauthorized local actions: edit Git adapter/tests/docs and run focused tests.
- Stop for: Git mutation outside disposable test repositories, publication, or a changed base.

**Steps:**
- [x] Preserve leading porcelain columns with NUL-delimited status parsing.
- [x] Hash staged and unstaged tracked diffs separately for born and existing repositories.
- [x] Exclude only `state/coordination.json` from the work identity hash and document why.
- [x] Add regressions for staged-content collision, first-entry unstaged path, and tracked-state save stability.

**Verification:**
- [x] `python -m pytest -q tests/test_git.py`
- Expected: all Git tests pass and the new identity/path regressions pass.

**Exit Criteria:** Git identity and changed-file evidence satisfy the stated
ownership boundary without changing ordinary `changed_files` visibility.

### Task 2: Harden task-bound verifier acceptance

**Purpose:** Prevent cross-task evidence replay, expose one small supported
verifier handoff, and keep completed-task evidence current.

**Task Function:** Acceptance boundary correction.

**Template Profile:**
- Not applicable: inline lead; no delegated executor.
- Selection basis: resolve from trust-boundary scope and test complexity.

**Validator Profile:**
- Not applicable: inline lead; no delegated validator.
- Selection basis: independently exercise success, stale, replay, and idempotency paths.

**Specification Coverage:** Acceptance remains outside workers; only current,
task-bound verifier evidence may produce durable PASS.

**Required Skills:** `skill-backend-verification`

**Files And Symbols:**
- Modify: `src/general_os/acceptance.py:VerificationResult`, `evaluate_acceptance`, `apply_task_transition`.
- Verify: `tests/test_acceptance.py`, `tests/test_cli.py`.
- Document: `docs/contracts.md` and `docs/recovery.md`.

**Dependencies:** Task 1 identity contract.

**Authority:**
- Preauthorized local actions: edit acceptance code/tests/docs and run focused tests.
- Stop for: new scheduler/worker state, external side effects, or publication.

**Steps:**
- [x] Add verifier task identity and require it for PASS evaluation.
- [x] Add a public, narrow in-process verifier-result builder that accepts current Git evidence and does not persist runtime state.
- [x] Update already-completed tasks only when a PASS carries a different accepted identity; preserve same-identity idempotency.
- [x] Add cross-task replay, public-handoff, fresh-reverification, and tracked-state recovery tests.

**Verification:**
- [x] `python -m pytest -q tests/test_acceptance.py tests/test_cli.py`
- Expected: valid current evidence completes the intended task only; free-form CLI PASS remains rejected.

**Exit Criteria:** No caller can reuse a verifier result across task IDs, and a
supported native/CoS handoff is exercised without making workers acceptance
owners.

### Task 3: Align native boundary adapters

**Purpose:** Preserve one-way profile projection while giving independent Orca
work its actual ephemeral assignment and precise diagnostics.

**Task Function:** Runtime-boundary contract correction.

**Template Profile:**
- Not applicable: inline lead; no delegated executor.
- Selection basis: resolve from adapter scope and optional-runtime risk.

**Validator Profile:**
- Not applicable: inline lead; no delegated validator.
- Selection basis: verify command projection and graceful degradation.

**Specification Coverage:** Codex remains default; Orca is optional and never a
second durable coordinator.

**Required Skills:** `skill-backend-verification`

**Files And Symbols:**
- Modify: `src/general_os/orca.py:build_orca_launch`, `src/general_os/cli.py:run_orca_smoke`.
- Modify: `.agents/skills/chief-of-staff/SKILL.md`, `.agents/skills/orca-orchestration/SKILL.md`.
- Verify: `tests/test_orca.py`, `tests/test_cli.py`, `tests/test_policy.py`.

**Dependencies:** Task 2 acceptance boundary.

**Authority:**
- Preauthorized local actions: edit adapter/docs/tests and run simulated probes.
- Stop for: live Orca mutation or worker lifecycle operation.

**Steps:**
- [x] Add an optional ephemeral assignment argument to Orca launch construction.
- [x] Keep profile instructions separate and preserve explicit-only projection.
- [x] Rename smoke `verified` output to a reachability/probe fact.
- [x] Make CoS explicitly read effective `orca_enabled` before selecting Orca.

**Verification:**
- [x] `python -m pytest -q tests/test_orca.py tests/test_cli.py tests/test_policy.py`
- Expected: empty profile instructions still produce an assignment prompt when supplied; optional Orca failure degrades without policy mutation.

**Exit Criteria:** Independent work receives enough context to execute, while
general-os owns no Orca lifecycle or second profile registry.

### Task 4: Reconcile migrated guidance and templates

**Purpose:** Remove predecessor-only authorities and align docs with serialized
profiles and the current publication boundary.

**Task Function:** Documentation contract reconciliation.

**Template Profile:**
- Not applicable: inline lead; no delegated executor.
- Selection basis: resolve from cross-surface documentation risk.

**Validator Profile:**
- Not applicable: inline lead; no delegated validator.
- Selection basis: inspect references and run documentation contracts.

**Specification Coverage:** general-os is the SSOT; no maintained skill points
to unavailable predecessor governance or requires unauthorized publication.

**Required Skills:** `skill-writing-plans`

**Files And Symbols:**
- Modify: browser review, dashboard, review, wayfinding, plan-review, and review-reception skills listed in `targets`.
- Modify: `docs/templates/coordination-state.json`, `docs/contracts.md`.
- Verify: `tests/test_documentation_contracts.py`, `tests/test_state.py`.

**Dependencies:** Tasks 1–3.

**Authority:**
- Preauthorized local actions: edit maintained docs/templates/tests and run validators.
- Stop for: generated-surface edits without canonical-source changes or publication.

**Steps:**
- [x] Make browser review publication conditional on reachability and separate authority.
- [x] Replace predecessor-only Project OS/CLAUDE/routing references with current owners and statuses.
- [x] Describe Codex profile identifiers and empty instructions accurately.
- [x] Add template `version: 1` and enforce the schema in tests.

**Verification:**
- [x] `python -m pytest -q tests/test_documentation_contracts.py tests/test_state.py`
- Expected: maintained references resolve and the template round-trips as schema version `1`.

**Exit Criteria:** Documentation and templates describe actual current behavior
without creating new registries or authority layers.

### Task 5: Fresh final verification

**Purpose:** Reconcile implementation, tests, docs, plan state, and preserved
unrelated files before claiming completion.

**Task Function:** Completion verification.

**Template Profile:**
- Not applicable: inline lead; no delegated executor.
- Selection basis: final changed-surface risk.

**Validator Profile:**
- Not applicable: inline lead; no delegated validator.
- Selection basis: independent final evidence review.

**Specification Coverage:** Fresh Git-bound proof and no unverified runtime claim.

**Required Skills:** `skill-verification-before-completion`

**Files And Symbols:** all changed files from Tasks 1–4.

**Dependencies:** Tasks 1–4.

**Authority:**
- Preauthorized local actions: run final tests, validators, diff checks, and update plan evidence/status.
- Stop for: failed required proof, stale Git state, publication, or destructive cleanup.

**Steps:**
- [x] Run focused tests and the full suite.
- [x] Validate state and migration manifest.
- [x] Run `git diff --check`, inspect status, and preserve `.serena/`.
- [x] Record fresh SHA and residual unverified live-runtime limits.
- [x] Mark plan `completed` only after verification returns `verified`.

**Verification:**
- [x] `python -m pytest -q`
- [x] `python -m general_os state validate state/coordination.json`
- [x] `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`
- [x] `git diff --check; git status --short --branch; git rev-parse HEAD`
- Expected: all required checks pass; no publication or live-runtime claim is implied.

**Exit Criteria:** Every included finding is fixed or explicitly excluded with
source evidence, all required proof is fresh, and no unrelated change is made.

### Task 6: Bind acceptance to the durable task contract

**Purpose:** Prevent changes to objective, dependencies, acceptance criteria,
profile, or independent-boundary requirements from reusing old completion proof
while keeping coordination state outside the Git work identity.

**Task Function:** Acceptance invariant correction.

**Template Profile:** Not applicable: inline lead; no delegated executor.

**Validator Profile:** Not applicable: inline lead; no delegated validator.

**Specification Coverage:** Acceptance must bind both repository/work identity
and the current acceptance-relevant task contract.

**Required Skills:** `skill-backend-verification`, `skill-verification-before-completion`

**Files And Symbols:**
- Modify: `src/general_os/state.py`, `src/general_os/acceptance.py`,
  `docs/contracts.md`.
- Verify: `tests/test_acceptance.py`, `tests/test_state.py`.

**Dependencies:** Tasks 1–5.

**Authority:**
- Preauthorized local actions: edit implementation, tests, and maintained
  contract documentation; run focused and full verification.
- Stop for: schema incompatibility, failed acceptance proof, publication, or
  unrelated worktree changes.

**Steps:**
- [x] Add a deterministic task-contract fingerprint over task ID, objective,
  dependencies, acceptance criteria, profile, and independent-boundary policy.
- [x] Bind verifier evidence and durable completed-task state to that fingerprint.
- [x] Demote completed tasks when either Git work identity or task-contract
  fingerprint is missing or mismatched.
- [x] Add regression coverage for semantic task edits and persistence.

**Verification:**
- [x] `python -m pytest -q tests/test_acceptance.py tests/test_state.py`
- Expected: changed task semantics invalidate old completion evidence; unchanged
  semantics remain idempotent.

**Exit Criteria:** Durable task edits cannot bypass fresh acceptance, and no
  runtime ledger or duplicate coordination authority is introduced.

### Task 7: Verify the published revision and reconcile the plan

**Purpose:** Replace stale pre-publication evidence with fresh proof for the
exact GitHub-reachable revision and close the remaining audit inconsistency.

**Task Function:** Final verification and plan reconciliation.

**Template Profile:** Not applicable: inline lead; no delegated executor.

**Validator Profile:** Not applicable: inline lead; no delegated validator.

**Specification Coverage:** Final evidence must describe the exact revision
being claimed, and completed inline tasks must have explicit profile status.

**Required Skills:** `skill-verification-before-completion`, `skill-writing-plans`

**Files And Symbols:**
- Modify: this plan only for evidence and task-state reconciliation.
- Verify: all changed code, tests, docs, state, and published Git revision.

**Dependencies:** Task 6.

**Authority:**
- Preauthorized local actions: run clean-checkout verification and update this
  plan with exact evidence.
- Stop for: failed proof, unreachable SHA, publication, or destructive cleanup.

**Steps:**
- [x] Run the complete verification suite on a clean checkout of the exact
  published SHA.
- [x] Replace stale base-SHA evidence with the exact verified SHA and commands.
- [x] Mark prior inline task profile roles explicitly not applicable.
- [x] Mark this plan `completed` only after all required proof passes.

**Verification:**
- [x] `python -m pytest -q`
- [x] `python -m general_os state validate state/coordination.json`
- [x] `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`
- [x] `python -m general_os orca smoke --json`
- [x] `git diff --check; git status --short --branch; git rev-parse HEAD`
- Expected: all checks pass on the exact published SHA with no unrelated file
  changes.

**Exit Criteria:** Acceptance is contract-bound, verification is revision-bound,
and the plan contains no unresolved placeholders or stale revision claims.

## Verification

```powershell
python -m pytest -q
python -m general_os state validate state/coordination.json
python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md
git diff --check
git status --short --branch
git rev-parse HEAD
```

## Completion Criteria

1. Git snapshot identity distinguishes staged and unstaged tracked contents,
   reports correct status paths, and is stable across coordination-state saves.
2. PASS evidence is task-bound and produced through a documented in-process
   handoff; stale, replayed, or contract-mismatched evidence cannot complete
   work.
3. Orca assignment projection and policy boundaries match maintained guidance;
   reachability is not mislabeled as worker verification.
4. Migrated documentation and templates refer only to current owners and
   serialized behavior.
5. Focused tests, full tests, state validation, migration validation, and diff
   checks pass on the final local revision.

## Final Evidence

- Published branch `codex/general-os-acceptance-contract-fingerprint` points to
  `eb0731453e4fa3029c4aa605f6f24f9eea9978f6`; the exact SHA is reachable from
  GitHub and was verified in clean detached worktree `C:\tmp\general-os-verify-eb07314`.
- `python -m pytest -q`: `115 passed`.
- `python -m pytest -q tests/test_acceptance.py tests/test_state.py`: `41 passed`.
- `python -m general_os state validate state/coordination.json`: `valid`.
- Migration validator: `44` valid rows.
- `python -m general_os orca smoke --json`: `status=ready`,
  `state=ready`, `reachable=true`, `probe_ok=true`, Orca `1.4.256`.
- Independent Orca probe: dispatch `ctx_f7590985d8f3`, task
  `task_2c4b2f2dc016`, run `run_a7b0171d1e61`; a separate worker worktree ran
  `python -m pytest -q tests/test_orca.py` with exit `0` and `14 passed in
  0.07s`, reported `worker_done`, and made no repository changes.
- `git diff --check`: passed. Untracked `.serena/` is unrelated and preserved.
- Browser review runs were not rerun; their completed, pinned evidence remains
  the source review input for this local remediation.
- Clean-checkout verification on `eb0731453e4fa3029c4aa605f6f24f9eea9978f6`:
  `115 passed`, state `valid`, migration `44` rows valid, Orca `ready` with
  `probe_ok=true`, and clean Git status.
- No merge, CI, production-load, or external-service claim is made. The Orca
  probe covered worker dispatch and the targeted test only; it did not establish
  production-load or external-service behavior.

