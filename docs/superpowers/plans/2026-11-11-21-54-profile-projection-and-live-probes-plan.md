---
layer: change
artifact_type: plan
status: completed
template_id: implementation-plan
name: general-os-profile-projection-and-live-probes
targets:
  - src/general_os/profiles.py
  - src/general_os/cli.py
  - agents/*.toml
  - tests/test_profiles.py
  - tests/test_cli.py
  - tests/test_documentation_contracts.py
  - docs/architecture.md
  - docs/contracts.md
  - docs/runtime-adapters.md
  - README.md
  - docs/superpowers/plans/2026-11-11-20-38-general-os-native-first-operational-hardening-plan.md
---

# Goal

Complete the next narrow `general-os` slice: make profile projection executable and
collect controlled native/Orca probe evidence without creating a second runtime,
scheduler, runtime registry, lifecycle mirror, or durable runtime ledger.

The default execution path remains current Codex plus native capabilities. CoS
chooses whether work stays in the current runtime or crosses the independent Orca
boundary; a profile never selects that boundary by itself.

# Outcomes

- Current Git, native Codex, Goal-only, native delegation, bounded mutation, and retry/acceptance behavior are verified where the runtime is available.
- `agents/*.toml` is the only profile registry; explicit profile facts project one way into a read-only runtime specification.
- Profile projection exposes `harness`, optional real `model`, optional `effort`, and `instructions`; missing runtime facts inherit native defaults.
- Harness validation accepts any non-empty explicit harness string; runtime availability decides whether a selected harness can be exercised.
- The supplied profiles are resolved for the Orca projection, and the configured Claude gateway is probed once per supplied profile using only its explicit model/effort values. Unavailable optional capabilities are recorded as `NOT EXERCISED`, not durable blockers.
- Git and fresh verification remain acceptance truth; runtime completion alone never accepts a durable task.
- `project-OS-starter` remains untouched.

# Constraints / decisions

- Git and this plan own workflow truth; runtime IDs, heartbeats, worker registries, progress mirrors, and parity ledgers are forbidden.
- `model = "codex"` is legacy harness metadata and must be removed from built-ins, not projected as a model ID.
- Do not add `effort` without an explicitly configured compatible real model; never infer model or effort from profile name or rank.
- Profile selection and execution-boundary selection remain separate. Harness projection applies only after Orca is selected; ordinary local execution remains current Codex.
- Orca owns independent worker/worktree lifecycle. Do not create a manual worktree for Orca probes.
- Native-subagent probing requests one child only as evidence; it does not establish a normal child-count policy.
- Optional runtime absence lowers probe coverage only. It does not mutate policy or block ordinary Codex work.
- Use the current clean `HEAD` as the probe baseline; do not require a hard-coded SHA.
- One bounded authorization covers any live worker operations and task-owned cleanup. No install, authentication, commit, push, merge, publication, or external side effect is part of this plan.

# Task graph

## Task 1: Read-only preflight and native probes

**Purpose:** Establish current repository/runtime facts and prove the native-first path before changing profile code.
**Task Function:** investigation and runtime verification.
**Template Profile:** unresolved; select the lowest reliable profile at execution time.
**Specification Coverage:** Native-first default, Git acceptance truth, optional runtime evidence, no durable runtime mirror.
**Required Skills:** `chief-of-staff`, `executing-work`.
**Files And Symbols:** `src/general_os/git.py`, `src/general_os/state.py`, `src/general_os/acceptance.py`, existing tests, current Git worktree.
**Dependencies:** None.
**Authority:** Preauthorized read-only inspection, tests, version/status commands, and disposable native probe artifacts. Stop for writes outside the repository, authentication, installation, or destructive cleanup.
**Steps:**
- Require a clean worktree and record `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`, and `git status --short --branch` as the probe baseline.
- Run the existing focused tests and inspect the current `general-os` CLI help.
- Exercise available native Codex goal-only and one-child delegation paths if the current runtime exposes them; state explicitly that the one-child request is a capability probe, not policy.
- Exercise a tiny disposable mutation in a derived sibling/native worktree only if native runtime access is available; verify the diff through Git and remove only task-owned disposable artifacts.
- Record `PASS`, `FAIL`, or `NOT EXERCISED — capability unavailable` in this plan without adding runtime state to the repository.
**Verification:** `python -m pytest -q tests/test_profiles.py tests/test_cli.py`; `python -m general_os --help`; `git diff --check`; `git status --short --branch`; runtime version/probe commands when available.
**Exit Criteria:** Baseline and focused native evidence are recorded, no unexpected durable mutation exists, and the current `HEAD` is captured without a fixed-SHA gate.

## Task 2: Implement one-way profile projection

**Purpose:** Make explicit profile facts readable and projectable without launching or coordinating runtimes.
**Task Function:** implementation and focused regression testing.
**Template Profile:** unresolved; select the lowest reliable implementation profile at execution time.
**Specification Coverage:** Profile SSOT, no model/effort inference, harness-neutral validation, deterministic read-only resolution.
**Required Skills:** `executing-work`.
**Files And Symbols:** `src/general_os/profiles.py` (`ProfileSpec`, `load_profiles`, `resolve_profile`, new projection contract); `src/general_os/cli.py` (new `profile resolve` handler/parser); `agents/high.toml`, `agents/low.toml`, `agents/normal.toml`, `agents/xhigh.toml`; `tests/test_profiles.py`; `tests/test_cli.py`.
**Dependencies:** Task 1 baseline.
**Authority:** Preauthorized edits to listed files and focused tests. Stop if projection requires runtime discovery, a compatibility matrix, or a second persistent registry.
**Steps:**
- Extend `ProfileSpec` with optional `harness` and `effort`, preserving optional `model` as an explicit real model field.
- Validate explicit `harness` and `effort` values as non-empty strings when present; do not restrict harness names to `codex` or `claude`.
- Add a pure projection function that returns only explicit `harness`, `model`, `effort`, and `instructions`, with omitted values represented as `None`; never derive values from rank/name/provider.
- Add read-only `general-os profile resolve --name <name> --directory <dir>` JSON output with no runtime inspection or mutation.
- Migrate only the provided built-in profiles from `model = "codex"` to `harness = "codex"` and omit model/effort. Do not create profiles solely for optional capability probes.
- Add focused tests for explicit projection, omitted defaults, arbitrary non-empty harness names, invalid empty values, CLI JSON, and unknown profiles.
**Verification:** `python -m pytest -q tests/test_profiles.py tests/test_cli.py`; `python -m general_os profile resolve --name high --directory agents`; `python -m compileall -q src`.
**Exit Criteria:** Projection is deterministic, one-way, tested, and does not launch workers or persist runtime facts.

## Task 3: Bounded mutation, retry, and acceptance proof

**Purpose:** Prove the normal write/verify/accept boundary independently of runtime bookkeeping.
**Task Function:** integration verification.
**Template Profile:** unresolved; select the lowest reliable profile at execution time.
**Specification Coverage:** Git truth, retryable failure, acceptance outside worker completion, no duplicated task state.
**Required Skills:** `executing-work`.
**Files And Symbols:** `src/general_os/acceptance.py`, `src/general_os/state.py`, `tests/test_cli.py`, `tests/test_acceptance.py`, disposable task-owned fixture/worktree only.
**Dependencies:** Task 1; Task 2 may be complete before final integration but is not logically required for the acceptance model.
**Authority:** Preauthorized local test fixture and disposable worktree mutation. Stop for shared-worktree conflict, destructive operation, or external side effect.
**Steps:**
- Run the existing acceptance tests and inspect the failure/pass transition behavior.
- Perform one tiny isolated mutation, capture a deliberate failed verification, retry, then capture a passing verification and reconcile through the durable owner.
- Confirm failed verification remains retryable, material blockers remain blockers, and worker/runtime completion is not used as acceptance.
- Remove task-owned disposable artifacts and retain only test/source changes in the repository.
**Verification:** `python -m pytest -q tests/test_acceptance.py tests/test_cli.py`; `git diff --check`; inspect Git state and acceptance evidence.
**Exit Criteria:** The retry-to-accept cycle is proven with fresh Git/verification evidence and no runtime ledger is introduced.

## Task 4: Profile-driven Orca probes

**Purpose:** Exercise the implemented projection at the independent orchestration boundary without making Orca mandatory.
**Task Function:** optional external-runtime verification.
**Template Profile:** unresolved; select the lowest reliable profile at execution time.
**Specification Coverage:** Orca optionality, projection-after-boundary selection, harness-neutral validation, Orca-owned lifecycle.
**Required Skills:** `orca-orchestration`, `executing-work`.
**Files And Symbols:** `src/general_os/orca.py`, `src/general_os/cli.py`, `repo_config/runtime-policy.toml`, `docs/runtime-adapters.md`, provided `agents/*.toml` profiles, disposable Orca-owned worktree/worker resources only.
**Dependencies:** Task 2.
**Authority:** One bounded authorization covers live worker launch and task-owned cleanup. Stop for missing authentication, install requirements, destructive cleanup outside task-owned resources, or any requested external side effect.
**Steps:**
- Resolve the installed Orca executable and inspect `orca --version`, `orca status --json`, and `orca skills get orchestration --full` only when the executable is available.
- If Orca is available and policy permits, launch one profile-driven Codex worker and verify its result through Git and acceptance evidence; let Orca own its worktree and lifecycle.
- Resolve only the provided profiles before any runtime probe. Do not add a profile or runtime registry to make an optional harness probe possible. The built-ins select the native `codex` Orca agent; the Claude probe validates the explicitly configured `combo-*` model/effort projection through the configured Claude gateway and does not create a second profile or harness registry.
- Do not run a second pre-projection/post-projection comparison and do not add a compatibility matrix or runtime registry.
**Verification:** `python -m general_os orca smoke --json`; resolved Orca status/skill commands when available; worker result plus Git diff/tests/acceptance evidence.
**Exit Criteria:** Each available harness is probed once after projection; unavailable optional capabilities are honest non-blocking evidence; no runtime state is persisted.

## Task 5: Final verification and plan closure

**Purpose:** Reconcile source, tests, documentation, Git, and probe evidence before completion.
**Task Function:** independent verification.
**Template Profile:** unresolved; select the lowest reliable profile that can verify the complete contract.
**Specification Coverage:** All outcomes and constraints in this plan, including untouched `project-OS-starter` and obsolete-seam removal.
**Required Skills:** `verification-before-completion`.
**Files And Symbols:** all changed files, `state/coordination.json`, `repo_config/runtime-policy.toml`, plan file, repository status, and `project-OS-starter` boundary.
**Dependencies:** Tasks 1–4.
**Authority:** Preauthorized local verification and plan-status update only after fresh proof. Stop for failed required checks, unresolved scope mismatch, or any Git disposition action.
**Steps:**
- Run full tests, compile checks, state validation, CLI smoke, projection commands, Orca smoke, and `git diff --check`.
- Scan maintained source/docs/skills for references to removed `general_os.cos`, `general_os.codex`, `general_os.dispatch`, `general_os.recovery`, `cos.py`, `codex.py`, `dispatch.py`, and `recovery.py`; scan `state/` for durable runtime mirror fields.
- Confirm the changed-file list is within this plan and no path under `C:/Users/HOANG PHI LONG DANG/repos/project-OS-starter` changed.
- Invoke `verification-before-completion`; mark this plan `completed` only if it returns `verified`. Commit/push/merge/publication remain separate actions.
**Verification:** `python -m pytest -q`; `python -m compileall -q src`; `python -m general_os state validate state/coordination.json`; `python -m general_os --help`; both `profile resolve` commands; `python -m general_os orca smoke --json`; `git diff --check`; `git status --short --branch`; maintained-reference and durable-mirror scans.
**Exit Criteria:** Fresh evidence supports every required outcome or records an exact optional-capability non-exercise; plan status is completed only after independent verification; branch disposition remains unchanged.

# Verification

- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os --help`
- `python -m general_os profile resolve --name high --directory agents`
- `python -m general_os orca smoke --json`
- `git diff --check`
- `git status --short --branch`
- maintained-reference scan excluding historical plan content
- durable-runtime-mirror scan under `state/`
- no path under `C:/Users/HOANG PHI LONG DANG/repos/project-OS-starter` changed

# Completion Criteria

The plan is complete only when Tasks 1–5 have fresh evidence, required tests and
checks pass, optional runtime gaps are recorded as `NOT EXERCISED`, no obsolete
seam or durable runtime mirror remains, and `verification-before-completion`
returns `verified`. Completion does not authorize commit, push, merge, cleanup,
or publication.

# Execution Evidence

- Task 1 — verified: current `main` remained at `def3d926aaa74a958746f3df74f0277554edd684`; Codex CLI `0.162.1` completed the goal-only probe with `CODEX_GOAL_PROBE_OK`, spawned exactly one native subordinate for `CODEX_NATIVE_CHILD_PROBE_OK` under the supplied `normal` profile (`combo-normal`), and completed the disposable mutation probe under the supplied `low` profile (`combo-low`) with `NATIVE_MUTATION_PROBE_OK`. The mutation used a sibling Git worktree and was removed afterward; Codex-created `.serena/` runtime residue was task-owned and cleaned. No repository change was retained.
- Task 2 — verified: profile projection and CLI were implemented; focused tests passed, and the provided `low`, `normal`, `high`, and `xhigh` profiles resolve to `harness=codex` with explicit `combo-low`, `combo-normal`, `combo-high`, and `combo-xhigh` models and `low`, `medium`, `high`, and `xhigh` effort values.
- Task 3 — verified: acceptance/retry tests passed (`11 passed`); no runtime ledger or additional durable state was introduced.
- Task 4 — verified end to end: Orca `1.4.256` is installed and `python -m general_os orca smoke --json` reports `ready` / `reachable=true`; the supplied profiles project to the expected native Orca arguments; Claude probes resolved each supplied profile and returned `PROFILE_PROBE_OK` with exit `0`. Claude emitted only the expected non-fatal warning that the custom `combo-*` IDs are locally unrecognized while the configured gateway accepted them. Orca registered the `general-os` repository as native metadata, then a supervised worker ran in a disposable top-level worktree under the supplied `low` projection (`codex` / `combo-low` / `low`) and returned `ORCA_WORKER_PROBE_OK` in `orca-probe.txt` with no newline. The first worker start exposed two runtime blockers: the coordinator lacked an `ORCA_TERMINAL_HANDLE`, and the worker then paused on the Codex hook-review prompt; both were resolved through Orca-native terminal custody and the user-directed trust-and-continue action. The worker terminal, probe file, generated `.serena/` residue, and disposable worktree were released or removed afterward; no live worker resource or repository change was retained. Orca retains the native historical Run/Task/Dispatch records, including the failed startup attempts, as runtime history rather than general-os durable state.
- Task 5 — verified: fresh full test suite passed (`53 passed`); `python -m compileall -q src`, state validation, CLI help, all four profile projections, Orca smoke, `git diff --check`, maintained obsolete-seam scan, and durable-mirror scan passed; no maintained obsolete seam or durable runtime mirror fields were found.
- Scope note: the separate `project-OS-starter` checkout reported 79 pre-existing working-tree changes at final inspection; no command in this plan targeted that checkout, and no `project-OS-starter` path appears in the `general-os` changed-file list.
- Independent completion result: `verified`. The working tree remains on `main`; commit, push, merge, publication, and external side effects were not performed.
