---
layer: change
artifact_type: plan
contract_version: "1"
status: completed
template_id: implementation-plan
name: general-os-verified-orca-transport
targets:
  - src/general_os/orca.py
  - src/general_os/cos.py
  - src/general_os/cli.py
  - repo_config/runtime-policy.toml
  - docs/runtime-adapters.md
  - .agents/skills/orca-orchestration/SKILL.md
  - tests/test_orca.py
  - tests/test_cos.py
  - tests/test_cli.py
  - tests/test_documentation_contracts.py
  - docs/superpowers/plans/2026-11-11-18-26-general-os-verified-orca-transport-plan.md
---

# General OS Verified Orca Transport

## Goal

Add the smallest useful Orca integration to `general-os` without making
`general-os` an Orca runtime, orchestration protocol owner, readiness registry,
worker scheduler, or second task ledger.

The implementation filter is:

> Before adding behavior to `general-os`, ask whether Codex or Orca already
> owns it natively. Use the native capability and project only the minimum
> semantic assignment and current observation across the boundary.

`general-os` owns durable intent, task dependencies, exceptional authority,
profiles, acceptance criteria, and recovery decisions. Git owns repository
truth. Codex owns its Goal, `update_plan`, tools, context, and native
subagents. Orca owns independent worker, Run, Task, Dispatch, worktree, wait,
retry, message, and cleanup lifecycle. CoS selects whether an independent
boundary is warranted; the native Orca skill performs Orca orchestration. When
the durable task graph is empty, CoS may dispatch the goal directly to Codex;
an empty graph is not itself a blocked state.

The installed Orca runtime was observed at version `1.4.256`. Its local
runtime reaches `ready` through `orca status --json` after the app is started.
A bounded worker-start attempt reached the real Orca boundary but failed at
`agent_readiness` with `agent-hooks-review-prompt`; the returned terminal was
released through the receipt-directed cleanup command. That is operational
evidence, not a reason to encode readiness into durable policy or block this
implementation plan.

## Review Findings And Decisions

1. **Separate permission, availability, and worker health.**
   `orca_enabled = true` means CoS may select Orca. It does not mean Orca is
   installed, reachable, or currently able to start a Codex worker. Availability
   and worker health are observed at use time.
2. **Do not hardcode Orca's orchestration protocol in Python.** Python owns
   discovery, `status --json`, and a small JSON execution helper. The
   version-matched Orca orchestration skill owns mutation commands and their
   current flags.
3. **Do not guess runtime profile values.** The current `agents/*.toml`
   `model = "codex"`, `provider = "native"`, name, and rank fields are
   general-os profile metadata, not proven native model/effort values. This
   slice passes the resolved profile name as semantic context only. Orca/Codex
   inherit native defaults until a separate profile slice defines explicitly
   runtime-native fields. No profile parity validator or guessed mapping is
   added.
4. **Use portable executable discovery.** Discovery checks
   `GENERAL_OS_ORCA_CLI`, `PATH` entries for `orca`/`orca.exe`, and a derived
   `%LOCALAPPDATA%\Programs\orca\resources\bin\orca.exe` path. No username or
   machine-specific absolute path is embedded.
5. **Do not set a semantic five-second timeout.** Orca's native lifecycle and
   defaults govern worker startup. The Python status helper may accept an
   optional test timeout, but production behavior does not treat a fixed
   startup duration as semantic correctness.
6. **Live smoke is evidence, not plan completion.** A failed local worker
   start records the observed cause and leaves implementation completion
   separate from current environment health. A task that does not require an
   independent boundary remains on Codex. A task whose durable contract
   requires independence is blocked when the native Orca skill reports Orca
   unavailable.
7. **Keep cleanup receipt-directed and bounded.** The skill follows Orca's
   current recovery instructions for the exact returned identity. `general-os`
   does not create a cleanup state machine or persist residual-resource state.
8. **No new third-party dependency is required by this slice.** The current
   implementation can use Python standard-library subprocess and JSON support,
   but stdlib-only is not a permanent architecture invariant.
9. **Defer broader governance templates.** A repository-local Orca skill is in
   scope because it is the native execution boundary. A complete `AGENTS.md`
   hierarchy and broader general-os skills for defining, executing, and
   verifying work are intentionally deferred to a separate general-os slice.
10. **Keep the old Python lifecycle seam transitional.** The injected
    `OrcaTransport`/`OrcaClient` worker methods remain compatibility/test seams
    for this migration, not the canonical general-os orchestration path. The
    native Orca skill owns real worker inspection and lifecycle; deletion of the
    legacy seam is deferred until native-skill coverage replaces its consumers.
11. **Load native orchestration guidance once per session.** The repository
    skill loads `orca skills get orchestration --full` before the first Orca
    mutation in an active agent session/version context, and reloads only after
    context loss, runtime/version change, or unavailable guidance.

## Implementation Outcomes

### Minimal Orca discovery and observation

`src/general_os/orca.py` gains a concrete local CLI observation boundary that
discovers Orca, runs `status --json`, validates the JSON object/envelope, and
maps current runtime readiness into a new transient status observation. The
existing injected `OrcaTransport`/`OrcaClient` worker lifecycle seam remains
available for current tests and embedders; the status observer is separate and
does not reinterpret worker IDs as runtime health. It does not run
`worker-start`, `worker-show`, `worker-stop`, retry, wait, message, or cleanup
commands.

### Goal-only CoS execution

`ChiefOfStaff.next_decision` treats an empty task graph as a direct Codex goal
assignment with `task_id = null`, rather than as a blocked dependency state.
Declared unfinished tasks with no dependency-ready item remain blocked; a graph
whose declared tasks are all completed returns a terminal `done` observation.
These are transient decisions derived from durable state and do not add a new
state ledger.

### Version-matched native orchestration skill

`.agents/skills/orca-orchestration/SKILL.md` becomes the repository-owned thin
instruction layer for using Orca. It instructs the executing Codex agent to
load `orca skills get orchestration --full`, follow that installed version's
commands, project only semantic assignment facts, return runtime evidence to
CoS, and never persist Orca runtime identities or progress.

### Permission-only policy and graceful runtime behavior

`repo_config/runtime-policy.toml` sets `orca_enabled = true` as an allowed
capability. Runtime health is derived at point of use. Ordinary tasks remain
Codex-first. Required independent work uses the native Orca skill and reports
an explicit blocker when Orca is unavailable; transient worker failure does
not mutate the policy or corrupt durable state.

### Profile projection without guessed runtime values

The native skill receives the resolved profile name as semantic task context.
The current profile `model`, `provider`, `rank`, and name fields are not
projected as native model or effort settings. Orca/Codex inherit native
defaults. No copied Orca profile, synchronization loop, equality check, or
profile validator is introduced; explicitly runtime-native profile fields are
deferred to a separate profile slice.

### Direct proof and documentation alignment

Focused tests prove discovery, status success/failure, malformed responses,
missing executable behavior, and honest smoke output. Skill/documentation
tests prove the fact boundary and native-command ownership. Direct local Orca
status evidence and one receipt-directed worker observation are recorded as
runtime evidence, not as durable coordination state.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `git-tracked`
- Required skills: `skill-code-standards`, `skill-test-driven-development`, `skill-backend-verification`, `skill-verification-before-completion`
- Isolation: `current workspace`
- Commit policy: `no commits during execution`
- Preauthorized local actions: edit the listed source, test, configuration, documentation, and skill files; run declared local Python checks; run read-only Orca status and skill commands; run one bounded local worker observation only through the native Orca skill and receipt-directed cleanup.
- User-approval actions: push, merge, publication, remote or paired Orca execution, remote side effects, destructive Orca reset, deletion outside receipt-directed cleanup, and changing scope or base commit.
- Parallel ownership: `none`
- Sequential fallback: complete goal-only CoS behavior, discovery/observation,
  and offline proof first; native worker health remains an evidence result and
  does not change the policy toggle.

## Coordination State

- Coordination owner: `single lead controller`
- Coordination schema: `2`
- Branch: `main`
- Base commit: `a5bb85396aaa16fe38cd55fc3d9655da12ce6364`
- Expected workspace: `clean`
- Next action: hand off the verified workspace to branch-disposition review; no commit, push, merge, or publication is authorized by this plan.
- Blockers: none; the observed `agent-hooks-review-prompt` worker-start failure was released successfully and remains runtime evidence only.

| Task | State | Workspace | Executor | Depends On | Required Proof | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Task 1 | `completed` | current | `unresolved` | none | focused observation and CoS goal-only tests | `24 passed` |
| Task 2 | `completed` | current | `unresolved` | Task 1 | skill/config/docs tests | `24 passed`; native skill/status verified |
| Task 3 | `completed` | current | `unresolved` | Task 2 | full suite plus direct runtime evidence | `45 passed`; Orca status ready; worker readiness failure released; no state mirror |
| Task 3 | `pending` | current | `unresolved` | Task 2 | full suite plus direct runtime evidence | pending |

## Task Breakdown

### Task 1: Implement minimal Orca discovery and status observation

**Purpose:**
- Add only the Python capability that `general-os` must own: discovering the
  local Orca executable and observing current runtime readiness.

**Task Function:**
- Establish a small, version-tolerant status boundary with explicit failure
  behavior and no Orca lifecycle ownership.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: bounded local subprocess and JSON boundary with moderate
  failure-handling risk.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently validate discovery precedence, response
  validation, and unavailable behavior.

**Specification Coverage:**
- Native-first implementation filter.
- One owner per fact.
- Runtime readiness is derived and transient.
- No Python-owned Orca orchestration protocol.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`

**Files And Symbols:**
- Inspect: `src/general_os/orca.py:OrcaObservation`, `OrcaClient`,
  `OrcaTransport`
- Add: `src/general_os/orca.py:OrcaStatusObservation`,
  `OrcaCliStatusObserver`, and the injectable subprocess runner
- Modify: `src/general_os/cli.py:run_orca_smoke` to consume the status observer;
  keep `run_runtime_inspect` unchanged and transitional/test-only
- Modify: `src/general_os/cos.py:ChiefOfStaff.next_decision` for goal-only,
  blocked, and done observations
- Verify: `tests/test_orca.py`, `tests/test_cos.py`

**Dependencies:**
- None; the installed Orca executable and `status --json` boundary are known.

**Authority:**
- Preauthorized local actions: implement and unit-test discovery/status observation without starting a worker, mutating a repository, or writing durable runtime state.
- Stop for: a request to encode worker lifecycle commands in Python, a second runtime registry, a new persisted health field, or a change to `project-OS-starter`.

**Steps:**
- [x] Step 1: Discover the executable in this order:
  `GENERAL_OS_ORCA_CLI`, `orca` on `PATH`, `orca.exe` on `PATH`, and the
  derived path `Path(os.environ["LOCALAPPDATA"]) / "Programs" / "orca" /
  "resources" / "bin" / "orca.exe"`. Return unavailable when no candidate
  exists.
- [x] Step 2: Add a small JSON subprocess helper that executes an argument
  array without a shell, captures stdout/stderr, accepts an optional injected
  timeout for tests, rejects process errors, timeout, malformed JSON, and
  non-object responses, and never retries or launches Orca automatically.
- [x] Step 3: Implement only `status --json` through the helper. Unwrap the
  result object and expose reachability as the required transient status fact.
  Report `runtime.state` and `runtime.appVersion` when present, but treat those
  fields as optional diagnostics. Keep runtime status separate from
  `OrcaObservation.worker_id` and the existing worker lifecycle methods.
- [x] Step 4: Preserve the existing injected `OrcaTransport` lifecycle seam for
  tests/embedders; do not add a concrete Python implementation for dispatch,
  worker inspection, cancel, wait, retry, messaging, or cleanup.
- [x] Step 5: Add an injectable subprocess runner and focused tests for
  discovery precedence, ready status, unavailable status, non-zero exit,
  `ok: false`, malformed JSON, timeout, and no state-file mutation. CLI tests
  must inject or monkeypatch the observer boundary so they do not depend on
  whether Orca is installed or running on the test machine.
- [x] Step 6: Update `ChiefOfStaff.next_decision` so an empty task graph returns
  a Codex goal-only decision with `task_id = null`, unfinished tasks with no
  ready dependency return `blocked`, and all declared completed tasks return
  `done`. Keep these decisions transient; do not add durable runtime state.

**Verification:**
- [x] `python -m pytest -q tests/test_orca.py`
- Expected: status observations are mapped correctly, failures remain honest,
  and no worker identity or runtime progress enters durable state.
- [x] `python -m compileall -q src`
- Expected: the observation boundary compiles without a new third-party
  dependency.

**Exit Criteria:**
- Python can discover Orca and observe its current status, while all Orca
  orchestration lifecycle remains owned by the native skill/runtime.

### Task 2: Add the native Orca orchestration skill and permission semantics

**Purpose:**
- Make Orca usable through its own version-matched orchestration guidance and
  express `orca_enabled` as permission rather than health.

**Task Function:**
- Connect CoS decisions to the native Orca execution boundary without copying
  Orca's lifecycle model into Python.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: cross-surface integration across one repository skill,
  policy configuration, CLI observation, and maintained documentation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: validate profile projection, graceful degradation, and
  absence of runtime mirrors.

**Specification Coverage:**
- `orca_enabled = true` means CoS may use Orca, not that Orca is healthy.
- Native Orca skill owns Run, Task, Dispatch, worker, retry, wait, message,
  release, and cleanup behavior.
- Current profile metadata is not guessed into native runtime configuration;
  Orca/Codex inherit native defaults until a separate profile slice defines
  runtime-native fields.
- Ordinary Codex work remains unaffected by Orca availability.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`

**Files And Symbols:**
- Inspect: `src/general_os/cli.py:_build_cos`, `run_runtime_inspect`,
  `run_orca_smoke`
- Inspect: `src/general_os/cos.py:ChiefOfStaff.choose_strategy`
- Inspect: `agents/low.toml`, `agents/normal.toml`, `agents/high.toml`,
  `agents/xhigh.toml`
- Modify: `.agents/skills/orca-orchestration/SKILL.md`
- Modify: `src/general_os/cli.py:_build_cos`, `run_orca_smoke`; leave
  `run_runtime_inspect` unchanged and transitional/test-only
- Modify: `repo_config/runtime-policy.toml`
- Modify: `docs/runtime-adapters.md`
- Verify: `tests/test_cli.py`, `tests/test_cos.py`,
  `tests/test_documentation_contracts.py`

**Dependencies:**
- Task 1 complete.

**Authority:**
- Preauthorized local actions: add the repository-local Orca skill stub, set the single local Orca permission toggle to true, wire status observation into CLI commands, and update boundary documentation.
- Stop for: hardcoded worker lifecycle commands in Python, copied runtime IDs, a profile parity validator, a scheduler/registry, or remote execution.

**Steps:**
- [x] Step 1: Create `.agents/skills/orca-orchestration/SKILL.md` with these
  exact rules: before the first Orca orchestration mutation in the current
  agent session/version context, load `orca skills get orchestration --full`;
  reload only after context loss, runtime/version change, or unavailable
  guidance; use the installed version's instructions for worker lifecycle;
  invoke Orca only when CoS selected an independent boundary; project task
  objective, relevant context, and acceptance criteria when useful; never
  persist Run ID, Task ID, Dispatch ID, worker ID, heartbeat, or progress;
  return runtime outcome/evidence to CoS; and treat Orca completion as
  non-acceptance until CoS verifies Git and acceptance.
- [x] Step 2: State in the skill that an unavailable Orca runtime falls back
  to Codex for work that does not require independent ownership and blocks with
  an explicit runtime observation when the durable task requires that boundary.
- [x] Step 3: Pass the resolved profile name as semantic task context only.
  Do not project the current `model`, `provider`, `rank`, or profile name as a
  native model/effort setting. Orca/Codex inherit native defaults until a
  separate profile slice defines explicitly runtime-native fields. Do not add
  validation or parity machinery in this slice.
- [x] Step 4: Set `repo_config/runtime-policy.toml` to
  `orca_enabled = true`. Keep `native_subagents_enabled = true` and
  `remote_side_effects = "ask"` unchanged.
- [x] Step 5: Make `run_orca_smoke` use the Task 1 status observation only.
  Keep `run_runtime_inspect` unchanged and transitional/test-only; it must not
  become a second general-os worker lifecycle surface. Keep `cos next` grounded
  in durable state and policy; it must not claim current runtime health from the
  policy toggle.
- [x] Step 6: Document that the Python boundary observes status while the
  version-matched Orca skill owns orchestration, and state that broader
  general-os governance skills are a separate future slice.

**Verification:**
- [x] `python -m pytest -q tests/test_cli.py tests/test_cos.py tests/test_documentation_contracts.py`
- Expected: `orca_enabled` permits Orca decisions without claiming readiness,
  normal work remains Codex-first, missing runtime status is non-blocking for
  ordinary work, and the skill/documentation contracts name one owner per fact.
- [x] `python -m general_os state validate state/coordination.json`
- Expected: the policy and skill integration do not alter durable state schema
  or add runtime identities.

**Exit Criteria:**
- CoS can select Orca as an allowed independent boundary, the native skill owns
  every Orca lifecycle action, current profile metadata is not guessed into
  runtime configuration, and policy does not act as a health registry.

### Task 3: Verify graceful runtime behavior and acceptance ownership

**Purpose:**
- Prove absent, reachable, failed, and successful-runtime paths without making
  local Orca health a completion gate or changing durable project truth.

**Task Function:**
- Validate the observation boundary, native skill handoff, receipt evidence,
  Git isolation, and CoS acceptance separation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: backend boundary verification with a local external runtime
  and explicit failure evidence.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently inspect automated proof, runtime evidence,
  cleanup receipts, Git state, and durable state.

**Specification Coverage:**
- Orca absence does not affect ordinary Codex work.
- Orca reachability permits an independent dispatch attempt through the native
  skill.
- Worker failure remains an honest runtime observation.
- Worker success returns evidence to CoS; it does not settle acceptance.
- Receipt-directed cleanup does not become a general-os state machine.
- Empty task graphs produce goal-only Codex decisions; dependency-blocked and
  all-completed graphs remain distinct transient observations.

**Required Skills:**
- `skill-backend-verification`
- `skill-verification-before-completion`

**Files And Symbols:**
- Inspect: `src/general_os/orca.py:OrcaCliStatusObserver`,
  `src/general_os/cli.py:run_orca_smoke`,
  `src/general_os/acceptance.py:evaluate_acceptance`
- Verify: `.agents/skills/orca-orchestration/SKILL.md`,
  `state/coordination.json`, `repo_config/runtime-policy.toml`, tests, and
  native Orca receipts

**Dependencies:**
- Task 2 complete.

**Authority:**
- Preauthorized local actions: run local Orca status and skill commands, perform one no-write independent-worker observation through the native skill, inspect the returned receipt, and execute only the receipt-directed cleanup action.
- Stop for: remote/paired execution, a worker requesting repository changes, unknown dispatch identity, `stop_unknown`, unproven process exit, or cleanup instructions not returned by the exact receipt.

**Steps:**
- [x] Step 1: Run `orca skills get orchestration --full` using the installed
  Orca CLI before the first mutation in this active session. Reuse that
  guidance for subsequent mutations unless context or runtime/version changes
  require a reload.
- [x] Step 2: Run `python -m general_os orca smoke --json`. Record `ready`
  only when the observed runtime is reachable; record `unavailable` or
  `failed` without converting it into a policy change.
- [x] Step 3: If the installed runtime and native skill permit it, use the
  repository Orca skill for one no-write independent assignment. Do not copy
  its worker-start flags into Python or this plan. The skill must return the
  native receipt or explicit failure evidence to CoS. A refusal or
  `agent_readiness` failure is valid runtime evidence and does not block the
  offline implementation proof.
- [x] Step 4: For a failed worker, record `failedStage`, `lastError`,
  `residualResources`, and `recovery`; follow only the returned cleanup
  instruction. For a successful worker, record Git/result evidence and keep
  acceptance pending until `general_os.acceptance` verifies it.
- [x] Step 5: Confirm the current diff contains only declared implementation
  paths and that `state/coordination.json` contains no Run ID, Task ID,
  Dispatch ID, worker ID, heartbeat, or progress mirror.

**Verification:**
- [x] `python -m pytest -q`
- Expected: all repository tests pass with runtime-independent coverage.
- [x] `python -m compileall -q src`
- Expected: all source compiles.
- [x] `python -m general_os state validate state/coordination.json`
- Expected: durable state remains valid and runtime identities are rejected or
  absent.
- [x] `python -m general_os orca smoke --json`
- Expected: `ready` with verified current reachability, or explicit
  `unavailable`/`failed` evidence; no policy mutation follows either result.
- [x] `python -m general_os cos next --state state/coordination.json --repo . --json`
- Expected: the checked-in empty fixture reports a Codex goal-only decision
  with `task_id = null`. Focused CoS tests prove unfinished dependency-blocked
  work returns `blocked`, all-completed work returns `done`, and independent
  work selects Orca only because policy permits it.
- [x] `git diff --check`
- Expected: no whitespace errors.

**Exit Criteria:**
- The implementation is complete when offline proof passes, native skill
  ownership is verified, runtime health is honestly reported, worker failure or
  success remains transient evidence, acceptance remains CoS-owned, and Git
  plus durable state are unaffected by runtime loss.

## Verification

Final artifact-level verification is:

- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os orca smoke --json`
- `python -m general_os cos next --state state/coordination.json --repo . --json`
- `git diff --check`
- `git status --short --branch`

The final evidence report must distinguish:

- Orca package/CLI discovery.
- Current Orca runtime readiness.
- Native skill-loaded orchestration evidence.
- Successful or failed worker outcome.
- Receipt-directed cleanup result.
- Permission policy value.
- Git and acceptance evidence.
- Absence of runtime identity/progress fields in `state/coordination.json`.

## Completion Criteria

The plan is ready for completion verification when:

1. Python owns only portable Orca discovery, `status --json`, JSON validation,
   and transient observation mapping.
2. The repository-local Orca skill loads the installed version-matched
   orchestration guidance before mutation and owns the semantic handoff to
   native Orca lifecycle commands.
3. `orca_enabled = true` expresses permission only; runtime readiness and
   worker health remain current observations.
4. Current profile name/rank/provider metadata is not guessed into native
   model/effort settings; Orca/Codex use native defaults until explicitly
   defined runtime-native fields are added by a separate slice.
5. Empty task graphs execute the goal directly in Codex; unfinished blocked
   graphs block; all-completed graphs return `done`; ordinary Codex work remains
   unaffected by Orca absence or transient worker failure; required independent
   work reports a real blocker when the native skill cannot establish Orca
   availability.
6. Worker completion never bypasses Git verification or CoS acceptance.
7. Focused tests cover goal-only/blocked/done CoS decisions, discovery, status
   success/failure, malformed responses, missing executable, deferred profile
   projection, and no state mirroring.
8. Full test, compile, CLI, and Git checks pass, and no file under
   `project-OS-starter` is modified.

The plan may be marked `completed` only after
`skill-verification-before-completion` returns `verified` for the implementation
and evidence. A local `agent-hooks-review-prompt` failure is recorded as
runtime evidence and does not by itself make the implementation incomplete.
