---
layer: change
artifact_type: plan
contract_version: "1"
status: proposed
template_id: implementation-plan
name: general-os-vnext-coordination-layer
targets:
  - pyproject.toml
  - README.md
  - src/general_os
  - agents
  - repo_config
  - state/coordination.json
  - docs/architecture.md
  - docs/contracts.md
  - docs/runtime-adapters.md
  - docs/recovery.md
  - docs/migration/project-os-starter.md
  - tests
  - docs/superpowers/plans/2026-11-11-16-40-general-os-vnext-coordination-layer-plan.md
---

# General OS vNext Coordination Layer

## Goal

Build `general-os` as a small, provider-neutral semantic coordination layer
above Git, native Codex execution, and optional Orca orchestration. It stores
only durable project intent and task facts that cannot be reconstructed
cheaply, derives current runtime and repository facts at the point of use,
and keeps acceptance separate from runtime completion.

`general-os` decides and remembers. Codex reasons and executes, including any
native subagent delegation inside its assignment. Orca is an optional
independent execution boundary. Git proves repository state and enables
recovery. CoS connects those systems without becoming an agent runtime,
scheduler, or second task ledger.

The target repository currently has no source files, Git history, or remote
refs. This is a greenfield successor implementation for
`https://github.com/longdang193/general-os`. The
`https://github.com/longdang193/project-OS-starter` checkout is strictly
read-only reference input for migration candidates and validated behavior.
No task in this plan modifies, commits to, or otherwise changes
`project-OS-starter`.

The architectural filter is:

- Store only durable facts that cannot be reconstructed cheaply and reliably.
- Derive current Git, Codex, and Orca facts from their native sources.
- Keep one owner for each fact and one explicit projection at runtime.
- Fail closed only for real safety, authority, dependency, or correctness
  boundaries.
- Recover from the durable coordination object plus Git, not lost runtime
  history.

## Implementation Outcomes

### One minimal durable coordination object

`general-os` owns one small structured state object at
`state/coordination.json`. It contains a goal, an optional small task graph,
task dependencies, one durable task state, acceptance criteria, optional
profile selection, and exceptional constraints that materially change what may
happen. Detailed Markdown implementation plans may remain useful supporting
artifacts, but they are not required input and are not parsed as the runtime
state machine.

The only durable task states are `pending`, `active`, `blocked`, and
`completed`. Dispatch outcomes, runtime observations, verification results,
and acceptance decisions are transient results. Codex thread IDs, Goal state,
Orca dispatch IDs, worker heartbeats, subagent counts, temporary checklist state,
runtime progress, write scopes, command ACLs, and cached parity state are not
persisted.

### Native-first execution

CoS chooses between one Codex assignment and an independent Orca workstream.
Native Codex subagents remain Codex-owned behavior controlled by the resolved
Codex configuration; CoS does not choose or track them as a project-level
strategy.

Profiles remain in `general-os` as capability and cost policy. Runtime toggles
such as `native_subagents_enabled` and `orca_enabled` are configuration, not
authority escalations. Authority is reserved for material side effects such
as remote writes, deployment, publication, destructive actions, or explicit
user prohibitions.

### Git-based restartability and current-fact acceptance

When a runtime disappears, CoS rereads the durable state and current Git
snapshot, finds unfinished tasks, and starts a fresh assignment. There is no
`recovery-required` task state or runtime reconstruction protocol.

Acceptance evaluates the current task, current Git facts, and fresh required
verification. Evidence that no longer matches the current repository is
rejected or rerun; acceptance is not bound to a copied plan revision or cached
runtime identity.

### Thin runtime boundaries

The Codex integration is a direct native adapter with only the operations
needed by the current workflow. The Orca integration is an experimental,
optional, best-effort wrapper around a configured local/API transport. No
generic runtime registry, normalized event framework, scheduler, or Orca
protocol is invented before a real third runtime or transport proves that the
abstraction is needed.

### Portable successor, not a Project OS dependency

The migration preserves useful concepts from Project OS Starter while
implementing them in repository-owned code. `general-os` has no runtime,
schema, or required-installed-skill dependency on Project OS Starter or a
user-local Project OS installation.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `git-tracked`
- Required skills: `skill-code-standards`, `skill-test-driven-development`, `skill-backend-verification`, `skill-executing-plans`, and `skill-verification-before-completion`; these are build-time aids, not runtime dependencies of `general-os`
- Isolation: `current workspace`; use a task-specific worktree only if implementation begins while another checkout owns the same repository
- Dependency policy: use the Python standard library where it is sufficient, but do not impose a zero-dependency rule; add a small mature dependency only when it materially reduces parser or transport risk
- Commit policy: `verified per-task checkpoint commits preauthorized`; the lead creates a checkpoint only after task-local proof and ledger update
- Preauthorized local actions: create and edit listed `general-os` files, inspect the read-only Project OS Starter reference checkout, run local tests and fake-runtime checks, and run optional configured smoke checks without publishing or external writes
- Reference boundary: `project-OS-starter` is read-only input; all implementation, tests, configuration, documentation, and Git history created by this plan belong to `general-os`
- User-approval actions: push, merge, publication, live external writes, deployment, external authentication, destructive cleanup, or changes to the approved architecture
- Parallel ownership: `none`; the five tasks share the durable state contract and remain serialized
- Sequential fallback: if a runtime or optional transport is unavailable, preserve the core implementation and record unavailable evidence rather than adding a mirror or blocking unrelated work

## Coordination State

- Coordination owner: `single lead controller`
- Coordination schema: `2`
- Branch: `main (to be created by Task 1)`
- Base commit: `none; the GitHub remote had zero refs on 2026-11-11`
- Expected workspace: `empty general-os checkout plus this proposed plan`
- Next action: `initialize the repository and create the package/test skeleton`
- Blockers: `none for the approved scope; live Codex or Orca evidence is optional and must be reported honestly`

| Task | State | Workspace | Executor | Depends On | Required Proof | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Task 1 | `completed` | current | `codex` | none | `python -m pytest -q tests/test_state.py tests/test_profiles.py tests/test_policy.py` | `17 passed` with Task 2 focused proof on 2026-11-11 |
| Task 2 | `completed` | current | `codex` | Task 1 | `python -m pytest -q tests/test_git.py tests/test_recovery.py` | `17 passed` combined Task 1–2 proof on 2026-11-11 |
| Task 3 | `pending` | current | `unresolved` | Task 1 | `python -m pytest -q tests/test_codex.py` | pending |
| Task 4 | `pending` | current | `unresolved` | Task 1 | `python -m pytest -q tests/test_orca.py` | pending |
| Task 5 | `pending` | current | `unresolved` | Task 2, Task 3, Task 4 | `python -m pytest -q` and `python -m general_os state validate state/coordination.json` | pending |

## Task Breakdown

Implementation plans in this document are the handoff artifact for this
greenfield build. They are not the input format that ordinary future
`general-os` work must use.

### Task 1: Bootstrap the minimal durable state and policy

**Purpose:**
- Create the package, test layout, configuration, and one small durable state
  object without importing the Project OS plan schema or runtime ledgers.

**Task Function:**
- Establish the canonical state, profile, configuration, and exceptional
  authority contracts that later tasks consume.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: bounded bootstrap and contract design with low repository
  risk but unresolved implementation details.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently validate state serialization, defaults, and
  schema rejection behavior.

**Specification Coverage:**
- One durable coordination object owns goal, optional tasks, dependencies,
  task state, acceptance criteria, optional profile, and exceptional
  constraints.
- Omitted configuration uses standard defaults.
- Detailed Markdown plans and Project OS installation files are not runtime
  dependencies.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`

**Files And Symbols:**
- Inspect: `project-OS-starter/repo_config/planning_artifact_schema.yaml` and
  `project-OS-starter/scripts/project_os_runtime/plan_preparation.py:PlanGraph`
  for migration facts only
- Modify: `pyproject.toml`, `.gitignore`, `README.md`
- Modify: `src/general_os/state.py:CoordinationState, Task, load_state, save_state, validate_state`
- Modify: `src/general_os/profiles.py:ProfileSpec, load_profiles, resolve_profile`
- Modify: `src/general_os/policy.py:PolicyDefaults, AuthorityExceptions, resolve_policy`
- Modify: `agents/low.toml`, `agents/normal.toml`, `agents/high.toml`, `agents/xhigh.toml`
- Modify: `repo_config/runtime-policy.toml`
- Verify: `state/coordination.json`, `tests/test_state.py`, `tests/test_profiles.py`, `tests/test_policy.py`

**Dependencies:**
- None; the repository is an empty successor checkout.

**Authority:**
- Preauthorized local actions: initialize Git, create package/test/config directories, implement JSON state and profile loading, and run local tests.
- Stop for: modifying `project-OS-starter`, adding a second durable ledger, importing the Project OS plan schema as a runtime requirement, or adding an exhaustive permission matrix.

**Steps:**
- [ ] Step 1: Create the package metadata, source tree, test tree, and repository-owned configuration directories.
- [ ] Step 2: Define `CoordinationState` with one task state enum (`pending`, `active`, `blocked`, `completed`) and JSON serialization that rejects runtime identities and progress mirrors.
- [ ] Step 3: Define the minimal state shape: goal, optional task list, dependencies, acceptance criteria, optional profile, and exceptional constraints.
- [ ] Step 4: Implement profile resolution and defaults: `native_subagents_enabled = true`, `orca_enabled = false` until a local transport is configured, and `remote_side_effects = ask`. Keep the runtime toggles as configuration and reserve authority exceptions for material side effects.
- [ ] Step 5: Add focused tests for round-trip state, dependency references, duplicate task IDs, invalid states, omitted defaults, and forbidden runtime fields in serialized task/state objects.

**Verification:**
- [ ] `python -m pytest -q tests/test_state.py tests/test_profiles.py tests/test_policy.py`
- Expected: the minimal state round-trips, invalid state is rejected, defaults resolve without optional metadata, and runtime identity/progress fields cannot enter the durable object.

**Exit Criteria:**
- A fresh checkout can load and validate one small coordination object without Project OS files, YAML frontmatter, runtime IDs, or a second task database.

### Task 2: Add direct Git observation and restartable recovery

**Purpose:**
- Make Git the direct repository and recovery source without persisting a
  recovery state machine or cached repository mirror.

**Task Function:**
- Implement stateless Git inspection and the simplest runtime-loss restart
  path.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: filesystem/process-boundary behavior and recovery edge cases.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: verify clean, changed, conflicting, and missing-workspace
  outcomes independently.

**Specification Coverage:**
- Current branch, revision, changed files, commits, and worktree status are
  observed from Git at invocation time.
- Runtime loss means reread durable tasks plus Git, verify existing evidence,
  or rerun unfinished work; no `recovery-required` state is added.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`

**Files And Symbols:**
- Inspect: `project-OS-starter/scripts/project_os_runtime/reconciliation.py`,
  `project-OS-starter/scripts/project_os_runtime/attempt.py`, and
  `project-OS-starter/scripts/project_os_runtime/lane.py` for useful Git and
  recovery behavior only
- Modify: `src/general_os/git.py:GitRepository, GitSnapshot, inspect_git`
- Modify: `src/general_os/recovery.py:find_unfinished_tasks, restart_unfinished`
- Modify: `src/general_os/workspaces.py:WorkspaceBinding, inspect_workspace`
- Verify: `tests/test_git.py`, `tests/test_recovery.py`, `tests/fixtures/git/`

**Dependencies:**
- Task 1 state and task contracts.

**Authority:**
- Preauthorized local actions: run read-only Git commands, create isolated test repositories, inspect worktrees, and implement fresh-runtime restart behavior.
- Stop for: destructive cleanup, branch deletion, push/merge, overwriting unrelated changes, or persisting a Git/runtime mirror that Git can provide directly.

**Steps:**
- [ ] Step 1: Implement `GitRepository` methods for current branch, revision, status, changed files, and conflict detection using direct Git observations.
- [ ] Step 2: Implement `find_unfinished_tasks` from durable task state and current Git facts only.
- [ ] Step 3: Implement `restart_unfinished` so missing runtime context causes a fresh assignment, not session reconstruction.
- [ ] Step 4: Add tests for clean state, unrelated changes, conflicting changes, completed evidence, unfinished tasks, and missing runtime/workspace conditions.

**Verification:**
- [ ] `python -m pytest -q tests/test_git.py tests/test_recovery.py`
- Expected: Git observations are fresh, conflicts fail closed only when material, and runtime loss can restart unfinished work without a recovery ledger.

**Exit Criteria:**
- CoS can recover from durable state plus Git alone and does not require Codex, Orca, or cached session metadata to identify unfinished work.

### Task 3: Implement the thin native Codex boundary

**Purpose:**
- Integrate Codex directly without creating a generic runtime framework or
  reimplementing native agent behavior.

**Task Function:**
- Provide the smallest Codex client needed to start, inspect, and optionally
  cancel one assignment while preserving native Goal, context, tools, and
  subagent ownership.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: native app-server boundary and failure handling.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: fake transport contract tests plus optional local boundary
  smoke evidence.

**Specification Coverage:**
- CoS chooses a Codex assignment, not direct versus native subagent execution.
- Codex receives task facts, workspace, resolved profile, and runtime toggles.
- Runtime observations remain transient and are never copied into durable
  state.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`

**Files And Symbols:**
- Inspect: `project-OS-starter/scripts/project_os_runtime/codex_app_server.py:CodexAppServerClient` and `project-OS-starter/tests/test_codex_app_server.py` for native boundary facts only
- Modify: `src/general_os/codex.py:CodexClient, CodexRequest, CodexObservation, run, inspect, cancel`
- Modify: `src/general_os/dispatch.py:CodexDispatchRequest, dispatch_codex`
- Modify: `repo_config/runtime-policy.toml:[codex]`
- Verify: `tests/test_codex.py`, `tests/fixtures/codex/`

**Dependencies:**
- Task 1 state, profiles, and configuration.

**Authority:**
- Preauthorized local actions: implement the injected/fake Codex boundary, map native responses, and run offline adapter tests.
- Stop for: live authentication, model/provider changes outside resolved policy, reimplementing Codex turns/context/tool behavior, or persisting Codex session state.

**Steps:**
- [ ] Step 1: Define only the Codex request and transient observation needed by the current workflow.
- [ ] Step 2: Implement `CodexClient.run` against the native app-server seam and return `unavailable` when the executable or boundary is absent.
- [ ] Step 3: Keep native subagents inside the Codex request/configuration; do not expose them as a CoS strategy or durable task state.
- [ ] Step 4: Add fake transport tests for success, unavailable runtime, malformed response, cancellation if implemented, and repeated observation.
- [ ] Step 5: Add serialization tests proving Codex thread/Goal/subagent facts do not enter `state/coordination.json`.

**Verification:**
- [ ] `python -m pytest -q tests/test_codex.py`
- Expected: the adapter maps the native boundary without a runtime registry, and unavailable live Codex evidence is reported without blocking the core package tests.

**Exit Criteria:**
- One Codex assignment can be requested, observed, and settled through a thin adapter while Codex remains the owner of its own agent loop.

### Task 4: Add the optional experimental Orca boundary

**Purpose:**
- Support independently managed work only when configured, without inventing
  an Orca protocol or treating local Orca use as an authority escalation.

**Task Function:**
- Implement a thin configurable Orca wrapper with fake-transport coverage and
  honest unavailable/live evidence handling.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: independent-work boundary, transport uncertainty, and
  bounded failure handling.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: fake transport lifecycle tests and one real local smoke when
  a configured Orca transport is available.

**Specification Coverage:**
- `orca_enabled` is configuration, not an `orca` authority state.
- Orca is selected only when work needs independent worktree/runtime ownership,
  retry, or parallel top-level execution.
- Remote or externally visible effects still require the material side-effect
  policy; local worker selection alone does not require approval.
- Missing live Orca evidence does not block the Codex-first implementation and
  must not be reported as verified.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`

**Files And Symbols:**
- Inspect: `project-OS-starter` only for runtime-neutral lane/admission concepts; it contains no Orca protocol source
- Modify: `src/general_os/orca.py:OrcaClient, OrcaRequest, OrcaObservation, dispatch, inspect, cancel`
- Modify: `src/general_os/dispatch.py:dispatch_orca`
- Modify: `src/general_os/cli.py:run_orca_smoke`
- Modify: `repo_config/runtime-policy.toml:[orca]`
- Modify: `docs/runtime-adapters.md`
- Verify: `tests/test_orca.py`, `tests/fixtures/orca/`

**Dependencies:**
- Task 1 state and configuration.

**Authority:**
- Preauthorized local actions: implement the disabled-or-enabled-by-config thin wrapper, fake transport, unavailable result, and optional local smoke command.
- Stop for: inventing a production protocol, remote authentication, external writes, deployment, publication, or adding an Orca lifecycle/worker registry.

**Steps:**
- [ ] Step 1: Define the smallest injected transport seam needed to dispatch, inspect, and cancel an independently managed worker.
- [ ] Step 2: Implement `OrcaClient` as an optional wrapper; return `unavailable` when no configured transport exists.
- [ ] Step 3: Keep worker IDs and lifecycle observations transient; do not write them into the durable state object.
- [ ] Step 4: Add fake transport tests for dispatch, observation, cancellation, malformed responses, unavailable transport, and repeated observation.
- [ ] Step 5: Add `python -m general_os orca smoke --json` as an opt-in local boundary check. Record `unavailable` evidence when no transport is configured and report `verified` only after a real local smoke succeeds.

**Verification:**
- [ ] `python -m pytest -q tests/test_orca.py`
- Expected: fake transport behavior is covered, disabled/unconfigured Orca is non-blocking, and no generic runtime registry or durable lifecycle mirror exists.
- [ ] `python -m general_os orca smoke --json` when a configured local Orca transport is available
- Expected: either a real local smoke result is recorded as evidence or the command reports unavailable without claiming integration verification.

**Exit Criteria:**
- `general-os` can optionally delegate an independent workstream through a thin configured boundary without requiring Orca for core execution.

### Task 5: Implement CoS, current-fact acceptance, CLI, and documentation

**Purpose:**
- Connect the minimal state, Git, Codex, and Orca surfaces into one shallow
  coordination path and document the successor boundary.

**Task Function:**
- Implement bounded coordination, verification, acceptance, CLI commands, and
  migration documentation without creating another lifecycle engine.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: cross-component integration, acceptance semantics, and final
  offline proof.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: end-to-end fake-runtime tests, direct Git evidence, and
  independent acceptance checks.

**Specification Coverage:**
- CoS strategy is `Codex | Orca`; native Codex subagents remain Codex-owned.
- CoS decisions are grounded, traceable, bounded by current facts and policy;
  mathematical determinism is not a required contract.
- Acceptance reads the current task, current Git snapshot, and fresh proof.
- Only durable task state is updated by acceptance; runtime and verification
  results remain transient.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`
- `skill-verification-before-completion`

**Files And Symbols:**
- Inspect: `project-OS-starter/scripts/project_os_runtime/admission.py`, `lane.py`, and `acceptance.py` for reusable semantics only
- Modify: `src/general_os/cos.py:ChiefOfStaff, CoSDecision, select_next_task, choose_strategy, reconcile_observation`
- Modify: `src/general_os/acceptance.py:VerificationResult, evaluate_acceptance, apply_task_transition`
- Modify: `src/general_os/cli.py:build_parser, run_state_validate, run_cos_next, run_runtime_inspect, run_accept, run_recover`
- Modify: `src/general_os/__main__.py:main`
- Modify: `README.md`
- Modify: `docs/architecture.md`, `docs/contracts.md`, `docs/runtime-adapters.md`, `docs/recovery.md`, `docs/migration/project-os-starter.md`
- Verify: `tests/test_cos.py`, `tests/test_acceptance.py`, `tests/test_cli.py`, `tests/test_documentation_contracts.py`

**Dependencies:**
- Tasks 1 through 4 provide state, Git, Codex, and Orca boundaries.

**Authority:**
- Preauthorized local actions: implement CoS, current-fact acceptance, CLI commands, documentation, fake-runtime integration tests, and declared local validation.
- Stop for: executing external side effects without policy approval, changing durable state without current evidence, adding a scheduler/runtime loop, adding a second ledger, or modifying `project-OS-starter`.

**Steps:**
- [ ] Step 1: Implement `choose_strategy` with only `Codex` and `Orca` outcomes. Select Orca only when independent ownership is materially useful and `orca_enabled` is true; otherwise use Codex or return a real dependency/authority block.
- [ ] Step 2: Implement `reconcile_observation` and `evaluate_acceptance` from current Git facts, current task facts, and fresh verification. Do not require copied plan revisions, runtime IDs, heartbeats, or formal recovery states.
- [ ] Step 3: Update only the durable task state on acceptance; make repeated acceptance idempotent and reject stale or insufficient proof.
- [ ] Step 4: Add CLI commands `state validate`, `cos next`, `runtime inspect`, `accept`, and `recover` with JSON output for automation; keep the Task 4 `orca smoke` command as its own optional boundary check.
- [ ] Step 5: Document durable versus derived facts, the Codex/Orca boundary, authority defaults, recovery-by-restart behavior, optional detailed plans, and the read-only Project OS Starter migration map.
- [ ] Step 6: Add behavior/schema tests for durable-state ownership, current Git acceptance, strategy selection, unavailable runtimes, and end-to-end restartability. Do not enforce architecture through repository-wide forbidden-word searches.

**Verification:**
- [ ] `python -m pytest -q tests/test_cos.py tests/test_acceptance.py tests/test_cli.py tests/test_documentation_contracts.py`
- Expected: CoS selects only Codex or Orca, native subagents stay Codex-owned, current Git facts govern acceptance, repeated settlement is idempotent, and documentation tests assert required schema/API behavior rather than blacklist prose.
- [ ] `python -m general_os state validate state/coordination.json`
- Expected: the one durable state object validates without Project OS installation files.
- [ ] `python -m general_os cos next --state state/coordination.json --repo . --json`
- Expected: the command returns a grounded next-task decision or an explicit material block.

**Exit Criteria:**
- A new controller can read one durable state object and Git, choose a Codex or optional Orca assignment, recover after runtime loss, and accept only work supported by current facts and required proof.

## Verification

Final artifact-level verification is source-first and does not require live
runtime access for the core implementation:

- `python -m pip install -e .`
- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os cos next --state state/coordination.json --repo . --json`
- `git diff --check`

If a configured local Codex or Orca runtime is available, run its smoke check
and record the observed result. If it is unavailable, record unavailable
evidence and do not claim live integration verification. Neither missing live
runtime evidence nor absent optional metadata blocks the offline core proof.

## Completion Criteria

The plan is ready for completion verification when:

1. `general-os` persists only goal, optional task dependencies/state,
   acceptance criteria, optional profile selection, exceptional constraints,
   and other non-derivable decisions that are actually needed.
2. One durable task state exists; dispatch, runtime, verification, and
   acceptance results are transient observations or function results.
3. CoS selects only `Codex` or `Orca`; native Codex subagents remain inside
   Codex's own execution boundary.
4. Git-based recovery rereads durable state plus current Git and starts fresh;
   it does not reconstruct lost runtime sessions or maintain a recovery ledger.
5. Acceptance uses current task and Git facts plus fresh proof, with no strict
   copied-revision transaction protocol.
6. Codex integration is direct and thin; Orca integration is optional,
   experimental, best-effort, and honest about unavailable versus verified
   live evidence.
7. The package has no runtime, schema, or required-installed-skill dependency
   on Project OS Starter or a user-local Project OS installation.
8. Documentation and behavior/schema tests establish fact ownership without
   brittle repository-wide forbidden-word policing.
9. All task-local proof and final verification commands pass, deviations are
   recorded, and `skill-verification-before-completion` returns `verified`.

The plan may be marked `completed` only after fresh final verification confirms
these criteria and no required task, failed check, blocker, or scope deviation
remains unresolved.
