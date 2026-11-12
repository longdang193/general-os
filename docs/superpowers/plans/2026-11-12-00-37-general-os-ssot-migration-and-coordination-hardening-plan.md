---
layer: change
artifact_type: plan
template_id: implementation-plan
contract_version: "1"
status: completed
name: general-os-ssot-migration-and-coordination-hardening
targets:
  - AGENTS.md
  - .agents/skills/
  - docs/migration/project-os-starter.md
  - docs/templates/
  - docs/rules/
  - src/general_os/acceptance.py
  - src/general_os/git.py
  - src/general_os/state.py
  - src/general_os/policy.py
  - src/general_os/profiles.py
  - src/general_os/orca.py
  - src/general_os/cli.py
  - tests/
---

# Goal

Make `general-os` the semantic SSOT for reusable skills and active shared
rules, while preserving its native-first Codex/Orca architecture and fixing
the validated durable-coordination failure modes found at implementation
baseline `450b51ed4626ec67ffd420807b416c9500102ace`. Execution is reconciled
against current HEAD `ea2a07cee21d3502b0e097bf950dd3b215091327`.

The migration is semantic, not a 1:1 copy: migrate methods and domain
knowledge, retire duplicated orchestration, and keep `project-OS-starter` as
read-only historical evidence.

## Review Evidence And Scope

- The single requested review run is complete: `GPT-5.6-Sol`, `High`, run
  `run-BFYn7y`, conversation
  `6af4f97f-2014-83eb-b14e-28869dd05502`, repository
  `longdang193/general-os`, commit
  `450b51ed4626ec67ffd420807b416c9500102ace`.
- The repository-bound review profile marker was verified as
  `longdang193/general-os`; the existing chat showed the pinned commit,
  requested model/effort, and a final actionable response. No run is
  incomplete or ambiguous.
- The attached verdict was compared with source at the same commit and the
  current `project-OS-starter` committed head
  `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`. That source contains 33 skill
  directories and 11 rule files; its uncommitted changes are not migration
  input.
- Review findings were reconciled against execution HEAD before acceptance;
  plan/state bookkeeping is coordination scope, not product behavior.
- Existing `general-os` tests pass: `53 passed`. Focused probes reproduce:
  missing acceptance evidence can pass, required boundaries are unenforced,
  dependencies do not gate completion, blocked `FAIL` is sticky, a durable
  policy exception can override `deny`, missing profiles synthesize `normal`,
  and unknown profile keys are ignored.
- Validated implementation scope includes: acceptance freshness, required
  boundary enforcement, dependency-state consistency, blocked-task recovery,
  lost-update protection, profile fail-closed behavior, policy-exception
  authority, durable-state versioning, bounded Orca observation, migration
  completeness, and weak prose-only contract tests.
- Excluded from implementation: copying generated `.agents/rules/`, copying
  Herdr/Runtime Grant/DeepAgents control-plane machinery, adding Project
  Secretary, rewriting historical completed plans, and treating uncommitted
  `project-OS-starter` edits as authoritative.

## Implementation Outcomes

### Canonical SSOT migration

`general-os` owns the maintained reusable skill source and active shared rules.
The migration document contains an explicit source-to-destination inventory,
retained/retired decisions, source commit, cutover criteria, and a one-way
verification procedure. No generated `.agents/rules/` tree or second rule
registry is introduced.

### Small native-first operating kernel

`AGENTS.md` and the five existing core skills remain concise and own only
global coordination, planning, execution, verification, and independent Orca
boundary guidance. Specialist skills are optional procedures; they do not
create schedulers, profile registries, runtime ledgers, or peer coordination
owners. The default coordination template demonstrates a goal-only state.

### Durable coordination correctness

Acceptance is bound to the exact observed repository/worktree identity,
required independent boundaries are evidenced, dependencies gate completion,
blocked work can return to retryable state, concurrent state updates cannot
silently overwrite one another, and the durable state format has an explicit
compatibility/version policy.

### Bounded runtime and authority behavior

Profiles fail closed when the declared registry is missing or malformed;
durable policy exceptions cannot silently widen a safer local denial; Orca
health observation has a finite default timeout and actionable schema-failure
behavior. Focused regression tests and documentation prove the contracts.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `git-tracked`
- Required skills: `skill-executing-plans`, `skill-code-standards`,
  `skill-writing-skills`, `skill-backend-verification`,
  `skill-plan-document-reviewer`, `skill-verification-before-completion`
- Isolation: `current workspace`; read `project-OS-starter` from committed
  revision `00b825ba95af4a44f0a33d528ea42593f3fc1dc1` and do not copy its dirty
  working-tree changes
- Commit policy: `no commits during execution`; checkpoint commits, push, and
  branch disposition require explicit user authorization
- Preauthorized local actions: inspect committed source, edit declared
  `general-os` files, add focused tests/docs, update the active plan/state,
  and run the declared local verification commands
- User-approval actions: publish or clean `project-OS-starter`, push/merge,
  delete source material, discard unrelated changes, or perform destructive
  recovery
- Parallel ownership: none; `AGENTS.md`, migration docs, and contract tests
  are shared surfaces that make parallel writers unsafe
- Sequential fallback: execute Tasks 1–7 in order in the current workspace

## Coordination State

- Coordination owner: `single lead controller`
- Coordination schema: `2`
- Branch: `main`
- Review baseline: `450b51ed4626ec67ffd420807b416c9500102ace`
- Execution HEAD: `ea2a07cee21d3502b0e097bf950dd3b215091327`
- Expected workspace: preserve unrelated untracked `.serena/`; preserve all
  existing `general-os` changes if they appear; treat the dirty
  `project-OS-starter` checkout as read-only source context
- Next action: none; final verification complete
- Blockers: none for plan execution; publication of source changes is outside
  this plan's authority
- Publication: no publication required; commit/push was not authorized during
  execution.

| Task | State | Workspace | Executor | Depends On | Required Proof | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Task 1 | `completed` | current | `codex` | none | committed source inventory and migration manifest tests | `8 passed`; source inventory `33` skills / `11` rules |
| Task 2 | `completed` | current | `codex` | Task 1 | core/docs/template contract tests | `8 passed`; goal-only template validated |
| Task 3 | `completed` | current | `codex` | Task 1, Task 2 | skill/rule inventory and forbidden-reference checks | `29` maintained skill directories; no `.agents/rules/`; scans clean |
| Task 4 | `completed` | current | `codex` | Task 2 | acceptance/state regression tests | `28 passed`; Git/acceptance/state/CLI checks |
| Task 5 | `completed` | current | `codex` | Task 2 | policy/profile/Orca regression tests | `44 passed`; concurrency, ceiling, fail-closed, timeout checks |
| Task 6 | `completed` | current | `codex` | Tasks 3–5 | docs, CLI, and migration acceptance checks | `63 passed`; CLI valid; active scan clean |
| Task 7 | `completed` | current | `codex` | Task 6 | full suite and final reconciliation | `70 passed`; diff/status reconciliation complete |

## Final Reconciliation

- Verification result: `verified` at execution HEAD
  `ea2a07cee21d3502b0e097bf950dd3b215091327` on `main`.
- Review baseline remains `450b51ed4626ec67ffd420807b416c9500102ace`; the
  implementation was validated against the newer execution HEAD.
- The policy contract is explicit: durable exceptions are narrowly scoped,
  carry provenance and expiry when supported, and cannot widen configured
  local `remote_side_effects="deny"`.
- All changed files are within declared plan targets. Untracked `.serena/` is
  unrelated preserved workspace state; no generated/runtime artifact was
  added. No publication was performed.

## Task Breakdown

### Task 1: Freeze ownership and record the committed migration inventory

**Purpose:**
- Establish one authoritative source revision and a reviewable mapping before
  importing any content.

**Task Function:**
- Reconcile the attached verdict with the committed source tree and define
  what is retained, merged, renamed, retired, or intentionally omitted.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- `general-os` becomes the maintained SSOT; `project-OS-starter` becomes
  historical/read-only evidence; migration is semantic, not 1:1.

**Required Skills:**
- `skill-writing-skills`, `skill-code-standards`

**Files And Symbols:**
- Inspect the predecessor only at commit
  `00b825ba95af4a44f0a33d528ea42593f3fc1dc1` using `git show` or `git archive`;
  never read its dirty working tree as migration input.
- Modify: `docs/migration/project-os-starter.md`
- Verify: `tests/test_documentation_contracts.py`

**Dependencies:**
- None; use only the committed source tree, not the dirty source checkout.

**Authority:**
- Preauthorized local actions: read both repositories, update the migration document and its focused tests, and run inventory checks.
- Stop for: a request to publish/clean source changes or a source revision different from `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`.

**Steps:**
- [x] Step 1: Record the source commit, count 33 committed skill directories
  and 11 committed rule files, and preserve the source worktree's unrelated
  modifications.
- [x] Step 2: Add a migration manifest to
  `docs/migration/project-os-starter.md` mapping all 11 rules and 33 skills to
  an existing core skill, a new specialist skill, a small shared rule, or an
  explicit retirement decision.
- [x] Step 3: Record the cutover criteria: no maintained runtime dependency
  on `project-OS-starter`, no maintained skill reference to
  `docs/operating_system/*`, no generated `.agents/rules/`, native Codex
  default, Codex-owned native children, Orca-only independent orchestration,
  `agents/*.toml` profile SSOT, and Git recovery truth.

**Verification:**
- [x] `git -C "C:/Users/HOANG PHI LONG DANG/repos/project-OS-starter" ls-tree -r --name-only 00b825ba95af4a44f0a33d528ea42593f3fc1dc1 -- .agents/skills | Select-String '/SKILL.md$' | Measure-Object -Line`
- Expected: 33 committed skill directories are represented by the inventory.
- [x] `pytest -q tests/test_documentation_contracts.py`
- Expected: migration ownership and acceptance assertions pass.

**Exit Criteria:**
- The migration document is an executable, source-pinned manifest with no
  unexplained predecessor skill/rule.

### Task 2: Normalize the core SSOT surfaces and goal-only defaults

**Purpose:**
- Make the always-on kernel small before specialist material is imported.

**Task Function:**
- Fold only global ownership/safety rules into `AGENTS.md`, simplify the five
  core skills, normalize their frontmatter, and prevent the template from
  implying a task graph for every request.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- Root guidance owns global facts only; skills own procedures; native runtimes
  own execution; no generated adapter mirror; goal-only work remains default.

**Required Skills:**
- `skill-writing-skills`, `skill-code-standards`

**Files And Symbols:**
- Inspect/modify: `AGENTS.md`
- Inspect/modify: `.agents/skills/chief-of-staff/SKILL.md`
- Inspect/modify: `.agents/skills/defining-work/SKILL.md`
- Inspect/modify: `.agents/skills/executing-work/SKILL.md`
- Inspect/modify: `.agents/skills/verification-before-completion/SKILL.md`
- Inspect/modify: `.agents/skills/orca-orchestration/SKILL.md`
- Modify: `docs/templates/coordination-state.json`
- Modify: `docs/templates/detailed-plan.md`
- Verify: `tests/test_documentation_contracts.py`

**Dependencies:**
- Task 1 migration manifest and ownership decisions.

**Authority:**
- Preauthorized local actions: edit the declared core guidance, skills, templates, and focused tests; run frontmatter and documentation checks.
- Stop for: a proposal to add a second registry, generated rule tree, scheduler, runtime ledger, or mandatory meta-skill.

**Steps:**
- [x] Step 1: Keep `AGENTS.md` limited to Git ownership, durable general-os
  facts, native Codex default, Codex child ownership, Orca independence,
  profile SSOT, runtime-state boundaries, fresh verification, and authority.
- [x] Step 2: Merge useful planning, execution, verification, and CoS
  guidance into the existing five core skills; remove Project-OS-only
  metadata such as `required_reads` and `distribution_tier` unless a current
  general-os consumer proves it is needed.
- [x] Step 3: Keep Orca selection optional unless independence is required or
  materially useful, and state that required independence blocks rather than
  silently falling back.
- [x] Step 4: Change `docs/templates/coordination-state.json` to a goal-only
  example with `"tasks": []`; keep task-graph examples inside
  `defining-work`.

**Verification:**
- [x] `pytest -q tests/test_documentation_contracts.py`
- Expected: core ownership, native execution, Orca boundary, and goal-only
  template contracts pass.
- [x] `rg -n "required_reads|distribution_tier|generated_agents|Herdr|Runtime Grant|DeepAgents" AGENTS.md .agents/skills`
- Expected: no forbidden Project-OS control-plane dependency remains in the
  maintained core surfaces.

**Exit Criteria:**
- The core kernel and default template express the intended architecture
  without duplicating Project-OS control-plane machinery.

### Task 3: Fold rules and migrate reusable specialist skills

**Purpose:**
- Bring over reusable methods while retiring duplicate orchestration and
  preventing a second rule source.

**Task Function:**
- Port and adapt specialist skills from the source manifest into
  `.agents/skills/`, create only genuinely shared `docs/rules/` files, and
  preserve native ownership.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- Retain reusable expertise; retire `skill-deepagents-executing-plans`,
  `skill-project-secretary`, `skill-using-superpowers`, custom scheduling,
  lane ledgers, runtime grants, generated rules, and mandatory meta-routing.

**Required Skills:**
- `skill-writing-skills`, `skill-executing-plans`, `skill-plan-document-reviewer`

**Files And Symbols:**
- Inspect: source `.agents/skills/skill-*/SKILL.md` at commit `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`
- Inspect: source `docs/operating_system/rules/*.md` at commit `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`
- Create/modify: `.agents/skills/backend-verification/`
- Create/modify: `.agents/skills/brainstorming/`
- Create/modify: `.agents/skills/central-config-layer/`
- Create/modify: `.agents/skills/code-standards/`
- Create/modify: `.agents/skills/creating-learning-materials/`
- Create/modify: `.agents/skills/dashboard-reporting/`
- Create/modify: `.agents/skills/disposable-artifact-cleanup/`
- Create/modify: `.agents/skills/distinctive-frontend-design/`
- Create/modify: `.agents/skills/finishing-development-work/`
- Create/modify: `.agents/skills/frontend-component-engineering/`
- Create/modify: `.agents/skills/full-stack-integration/`
- Create/modify: `.agents/skills/github-browser-reviews/`
- Create/modify: `.agents/skills/performance-optimization/`
- Create/modify: `.agents/skills/plan-document-reviewer/`
- Create/modify: `.agents/skills/receiving-code-review/`
- Create/modify: `.agents/skills/refactoring-assessment/`
- Create/modify: `.agents/skills/requesting-code-review/`
- Create/modify: `.agents/skills/reviewing-pull-requests/`
- Create/modify: `.agents/skills/spec-drafting/`
- Create/modify: `.agents/skills/systematic-debugging/`
- Create/modify: `.agents/skills/test-driven-development/`
- Create/modify: `.agents/skills/workspace-isolation/`
- Create/modify: `.agents/skills/wayfinding/`
- Create/modify: `.agents/skills/writing-skills/`
- Create only when multiple skills need the same rule: `docs/rules/frontend-ui.md`, `docs/rules/prompt-cache.md`, `docs/rules/publication-boundary.md`
- Verify: `tests/test_documentation_contracts.py` and a maintained-surface reference scan

**Dependencies:**
- Tasks 1 and 2; no specialist skill is copied before its source mapping and
  target ownership are recorded.

**Authority:**
- Preauthorized local actions: add/adapt only the declared skill and shared-rule files, update inventory tests, and run forbidden-reference scans.
- Stop for: copying generated adapters, importing source runtime machinery, or changing the source repository.

**Steps:**
- [x] Step 1: Merge the five old core skills into their existing general-os
  owners instead of creating duplicate names.
- [x] Step 2: Port the 24 reusable specialist capabilities under the target
  names above; soften absolute gates so they apply only when the task has the
  stated material risk or unresolved design.
- [x] Step 3: Fold backend, full-stack, Python, documentation-contract,
  review, and coordination guidance into owning skills; create a shared rule
  file only when at least two maintained skills need the same rule.
- [x] Step 4: Retire the three explicitly excluded control-plane skills and do
  not create `.agents/rules/`, `generated_agents/`, or a sync generator in
  `general-os`.
- [x] Step 5: Keep Git worktree guidance native-first: current checkout for
  small reversible work, native worktrees for useful isolation, and Orca-owned
  independent worker worktrees.

**Verification:**
- [x] `rg -n "project-OS-starter|docs/operating_system|generated_agents|Herdr|Runtime Grant|DeepAgents|Project Secretary|lane ledger|MAIN AGENT" .agents/skills docs/rules AGENTS.md`
- Expected: only explicitly historical migration references remain; no
  maintained skill depends on the retired control plane.
- [x] `Get-ChildItem .agents/rules -ErrorAction SilentlyContinue`
- Expected: no generated `.agents/rules/` directory exists.
- [x] Parse every maintained `SKILL.md` frontmatter and assert each target has
  exactly `name` and `description` unless a current general-os consumer proves
  another field is required.

**Exit Criteria:**
- The target skill set is source-mapped, semantically adapted, and free of a
  second orchestration or generated-rule authority.

### Task 4: Enforce acceptance freshness, boundaries, dependencies, and recovery

**Purpose:**
- Prevent false completion, impossible dependency states, and permanently
  stranded blocked tasks.

**Task Function:**
- Add the smallest typed evidence and transition checks that make the
  documented acceptance contract executable.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- Fresh verification precedes acceptance; required independent work cannot
  fall back; dependencies gate completion; `FAIL` remains retryable; runtime
  completion is not acceptance.

**Required Skills:**
- `skill-backend-verification`, `skill-code-standards`,
  `skill-systematic-debugging`

**Files And Symbols:**
- Modify: `src/general_os/git.py:GitSnapshot`, `GitRepository.inspect`
- Modify: `src/general_os/acceptance.py:VerificationResult`,
  `evaluate_acceptance`, `apply_task_transition`
- Modify: `src/general_os/state.py:CoordinationState.validate`
- Modify: `src/general_os/cli.py:run_accept`, `build_parser`
- Verify/extend: `tests/test_git.py`, `tests/test_acceptance.py`,
  `tests/test_state.py`, `tests/test_cli.py`

**Dependencies:**
- Task 2; preserve the current public status names and idempotent transitions.

**Authority:**
- Preauthorized local actions: modify the declared acceptance/state/Git/CLI symbols and focused regression tests; run direct boundary and failure-path checks.
- Stop for: changing task-state names, silently deleting existing state fields, or introducing a runtime scheduler.

**Steps:**
- [x] Step 1: Add one canonical repository/worktree identity to
  `GitSnapshot`, derived from `HEAD`, status, tracked diff, and untracked-file
  content; require `VerificationResult` to carry the matching evidence for a
  repository-bound `PASS`. Do not require a clean tree when the verified
  worktree is intentionally dirty; require identity equality instead.
- [x] Step 2: Add typed independent-boundary evidence to verification and
  reject or block `PASS` for `requires_independent_boundary=True` when the
  evidence is absent or does not identify the selected boundary. Keep the
  library fail-closed; do not add an unchecked boolean escape hatch.
- [x] Step 3: In `apply_task_transition` and `CoordinationState.validate`,
  require every dependency of a completing task to be `completed` and reject
  persisted completed tasks whose prerequisites are not complete.
- [x] Step 4: Make a retryable `FAIL` move a previously `blocked` task back to
  `pending`; keep `BLOCKED` reserved for the current material blocker and
  preserve idempotency for repeated transitions.
- [x] Step 5: Update the CLI to produce the same snapshot identity used by
  the library and to refuse acceptance of required-boundary tasks without
  runtime-produced boundary evidence.

**Verification:**
- [x] Add tests for missing/stale worktree evidence, dirty-tree identity
  changes, missing/valid required-boundary evidence, incomplete dependencies,
  blocked-to-pending recovery, and repeated transitions.
- Expected: every false-positive scenario reproduced by the review fails or
  blocks, while valid dirty-tree verification with matching identity passes.
- [x] `pytest -q tests/test_git.py tests/test_acceptance.py tests/test_state.py tests/test_cli.py`
- Expected: focused acceptance and state tests pass.

**Exit Criteria:**
- A task cannot be falsely accepted from stale evidence, an unfinished
  prerequisite, or an unproven required boundary, and blocker removal leaves
  work retryable.

### Task 5: Add durable-state concurrency/versioning and runtime safety guards

**Purpose:**
- Protect the SSOT file and runtime boundary from silent overwrite, unsafe
  authority widening, profile drift, and indefinite Orca hangs.

**Task Function:**
- Extend existing persistence and adapter code without creating another state
  or profile registry.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- Git/state recovery remains durable; profiles stay in `agents/*.toml`;
  durable exceptions do not bypass safer local policy; optional/required Orca
  observation is bounded and actionable.

**Required Skills:**
- `skill-backend-verification`, `skill-code-standards`

**Files And Symbols:**
- Modify: `src/general_os/state.py:CoordinationState.from_dict`,
  `CoordinationState.to_dict`, `load_state`, `save_state`
- Modify: `src/general_os/policy.py:resolve_policy`
- Modify: `src/general_os/profiles.py:load_profiles`, `resolve_profile`
- Modify: `src/general_os/orca.py:OrcaCliStatusObserver.observe`, `_run`
- Verify/extend: `tests/test_state.py`, `tests/test_policy.py`,
  `tests/test_profiles.py`, `tests/test_orca.py`

**Dependencies:**
- Task 4; state identity/version changes must not invalidate the acceptance
  evidence contract.

**Authority:**
- Preauthorized local actions: modify only the declared persistence/policy/profile/Orca symbols and focused tests; run concurrent-write and timeout simulations.
- Stop for: adding a second durable ledger, persisting runtime IDs, or widening remote-side-effect authority beyond the declared policy contract.

**Steps:**
- [x] Step 1: Add a schema version with an explicit legacy-read path for the
  current unversioned `state/coordination.json`, reject unsupported future
  versions, and write the current version on save.
- [x] Step 2: Add optimistic concurrency to `save_state` using the loaded
  state generation/digest; reject a save when the on-disk generation moved
  instead of silently replacing a newer update. Keep atomic temp-file replace
  for partial-write protection.
- [x] Step 3: Treat configured local `remote_side_effects="deny"` as a hard
  ceiling. If durable exceptions remain supported, require a narrow scope,
  explicit provenance, and expiry; otherwise reject the exception rather than
  silently upgrading `deny` to `allow`.
- [x] Step 4: Fail profile loading when the configured directory or default
  profile is absent; validate `rank`, `provider`, and `instructions`; reject
  unknown TOML keys and whitespace-only values. Keep `agents/*.toml` as the
  only registry and preserve one-way projection.
- [x] Step 5: Give `OrcaCliStatusObserver.observe` a finite default timeout,
  preserve caller overrides, and return a bounded actionable observation for
  malformed/unsupported status envelopes.

**Verification:**
- [x] `pytest -q tests/test_state.py tests/test_policy.py tests/test_profiles.py tests/test_orca.py`
- Expected: version migration, stale-save rejection, policy ceiling,
  fail-closed profile loading, and timeout/schema failure tests pass.
- [x] Run two read-modify-write processes against one temporary state file.
- Expected: exactly one stale writer is rejected and no accepted update is
  lost.

**Exit Criteria:**
- Durable state upgrades and concurrent writes are explicit and recoverable;
  local policy cannot be widened by stale state; profile and Orca failures are
  bounded and visible.

### Task 6: Align docs, migration acceptance, and executable contract tests

**Purpose:**
- Make the documented SSOT and the implementation/test contracts agree.

**Task Function:**
- Replace prose-only assertions with behavioral and inventory checks while
  documenting the final migration boundaries.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- Source/test/docs agreement, explicit migration acceptance, native ownership,
  profile projection, acceptance freshness, and recovery behavior.

**Required Skills:**
- `skill-plan-document-reviewer`, `skill-verification-before-completion`,
  `skill-code-standards`

**Files And Symbols:**
- Modify: `docs/architecture.md`, `docs/contracts.md`,
  `docs/runtime-adapters.md`, `README.md`
- Modify: `tests/test_documentation_contracts.py`
- Verify: `docs/migration/project-os-starter.md`, all maintained
  `.agents/skills/*/SKILL.md`

**Dependencies:**
- Tasks 3–5; documentation must describe the implemented contracts, not
  planned behavior.

**Authority:**
- Preauthorized local actions: update declared docs/tests to match accepted code and run inventory, CLI, and behavioral checks.
- Stop for: documenting a behavior not proven by source/tests or changing historical plan content solely to remove old references.

**Steps:**
- [x] Step 1: Document the exact state identity/version, dependency,
  required-boundary, blocked-recovery, policy-ceiling, profile, and Orca
  semantics in the owning docs.
- [x] Step 2: Replace substring-only migration assertions with checks that
  enumerate maintained skills, validate the migration manifest, reject
  forbidden active references, and cover critical acceptance/state behavior.
- [x] Step 3: Update README and migration acceptance criteria to distinguish
  active SSOT sources from historical references.

**Verification:**
- [x] `pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_profiles.py tests/test_policy.py tests/test_orca.py`
- Expected: documentation and behavior tests agree with the canonical source.
- [x] `rg -n "project-OS-starter|Herdr|Runtime Grant|DeepAgents|docs/operating_system|generated_agents" .agents/skills docs/rules AGENTS.md`
- Expected: no forbidden active dependency; historical migration references
  are limited to the migration documentation.

**Exit Criteria:**
- A fresh checkout can identify the SSOT, migration status, and safety
  invariants from maintained docs and executable tests without relying on the
  attached verdict.

### Task 7: Run final verification and reconcile the plan

**Purpose:**
- Confirm the complete migration/hardening outcome against current Git and
  record any deviation before execution is accepted.

**Task Function:**
- Perform final source, test, inventory, and recovery verification.

**Template Profile:**
- Controller-selected: `unresolved while pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and
  cost when execution begins.

**Specification Coverage:**
- All implementation outcomes and migration acceptance criteria.

**Required Skills:**
- `skill-verification-before-completion`

**Files And Symbols:**
- Inspect: all files listed in `targets`
- Verify: `state/coordination.json`, `docs/migration/project-os-starter.md`,
  `.agents/skills/`, `docs/rules/`, `tests/`

**Dependencies:**
- Task 6 complete and all required task-local proof accepted.

**Authority:**
- Preauthorized local actions: run final verification, reconcile plan/task evidence, and record blockers or deviations.
- Stop for: failed required proof, unreviewed scope expansion, stale Git/base identity, or any request to publish without explicit authorization.

**Steps:**
- [x] Step 1: Run the full test suite and CLI validation against the current
  state file.
- [x] Step 2: Re-run the source-pinned inventory and forbidden-reference scans;
  confirm no generated rule mirror or retired control-plane dependency exists.
- [x] Step 3: Compare changed files with the plan targets, record deviations,
  and leave plan status `proposed` or `active` until
  `skill-verification-before-completion` returns `verified`.

**Verification:**
- [x] `pytest -q`
- Expected: all tests pass with no unrelated failures.
- [x] `python -m general_os state validate state/coordination.json`
- Expected: JSON output reports `"status": "valid"`.
- [x] `git status --short --branch`
- Expected: only declared plan/migration implementation changes plus preserved
  unrelated work are present; no generated or runtime artifact is silently
  added.

**Exit Criteria:**
- Every task has accepted proof, the migration is source-pinned and one-way,
  validated risks are addressed or explicitly deferred, and the final plan
  reconciliation is complete.

## Verification

- `pytest -q`
- `python -m general_os state validate state/coordination.json`
- `pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_profiles.py tests/test_policy.py tests/test_orca.py`
- `rg -n "project-OS-starter|Herdr|Runtime Grant|DeepAgents|docs/operating_system|generated_agents" .agents/skills docs/rules AGENTS.md README.md`
- Source-pinned inventory against `project-OS-starter@00b825ba95af4a44f0a33d528ea42593f3fc1dc1`.
- Fresh `git status --short --branch` and changed-file reconciliation against
  this plan.

## Completion Criteria

The plan is ready for completion verification when:

1. `general-os` owns the maintained skill/rule sources and the migration
   manifest proves every predecessor item was merged, retained, or retired.
2. No generated `.agents/rules/` tree, second profile registry, runtime
   ledger, Project Secretary, DeepAgents execution layer, or custom scheduler
   has been introduced.
3. Acceptance freshness, required boundaries, dependency state, blocked-task
   recovery, concurrent state writes, schema compatibility, policy ceilings,
   profile loading, and Orca observation have focused executable proof.
4. Maintained docs and tests agree with the implementation and historical
   references are not mistaken for active dependencies.
5. Final verification returns clean required results, deviations are recorded,
   and `skill-verification-before-completion` returns `verified` before the
   plan status changes from `proposed`.
