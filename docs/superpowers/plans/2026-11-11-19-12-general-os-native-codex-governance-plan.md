---
layer: change
artifact_type: plan
contract_version: "1"
status: completed
template_id: implementation-plan
name: general-os-native-codex-governance
targets:
  - AGENTS.md
  - src/general_os/state.py
  - src/general_os/cos.py
  - src/general_os/acceptance.py
  - src/general_os/cli.py
  - tests/test_state.py
  - tests/test_cos.py
  - tests/test_acceptance.py
  - tests/test_cli.py
  - tests/test_documentation_contracts.py
  - docs/templates/coordination-state.json
  - docs/templates/detailed-plan.md
  - docs/architecture.md
  - docs/contracts.md
  - docs/recovery.md
  - docs/runtime-adapters.md
  - README.md
  - .agents/skills/chief-of-staff/SKILL.md
  - .agents/skills/defining-work/SKILL.md
  - .agents/skills/executing-work/SKILL.md
  - .agents/skills/verification-before-completion/SKILL.md
  - .agents/skills/orca-orchestration/SKILL.md
  - docs/superpowers/plans/2026-11-11-19-12-general-os-native-codex-governance-plan.md
---

# General OS Native Codex Governance

## Goal

Add the smallest native-first governance layer that makes `general-os` a
durable semantic coordination layer above Codex and optional Orca. The slice
must keep Git as repository and recovery truth, keep Codex as the default
execution harness, keep native Codex subagents subordinate to their parent
assignment, and use Orca only for materially independent work.

This plan follows the governing rule:

> Store only durable facts that cannot be reconstructed cheaply and reliably;
> derive runtime facts from Git, Codex, or Orca at the point of use.

The existing Orca implementation at commit `94aaa7be29ce36d533cf8ba6bf6b8d5e7513d65f`
is the baseline and remains the only Orca infrastructure in scope. Do not add
another Orca abstraction, runtime registry, scheduler, worker ledger, profile
parity system, or recovery mirror. Do not modify `project-OS-starter`; use it
only as a read-only reference.

The named Project OS skills in this plan are implementation-time aids for
building and verifying this repository. They are not runtime dependencies or
required installed skills of `general-os`.

## Implementation Outcomes

### Durable task assignments are semantic and retryable

`Task` gains one optional durable `objective` field. New task records can carry
their bounded assignment, while old records without the field remain valid and
fall back to the global goal when dispatched. Codex and Orca dispatch requests
use the task objective for task execution and the global goal only for goal-only
execution.

Acceptance transitions become semantically correct: `PASS` completes the task,
failed, stale, incomplete, or unknown verification leaves the task unfinished
so Codex can fix or reverify, and `BLOCKED` persists only a real material
blocker. The CLI persists `PASS` and genuine `BLOCKED` changes but does not
convert retryable evidence problems into a durable blocker.

### Native Codex governance is explicit and small

The repository has concise guidance for CoS, work definition, native Codex
execution, and verification, alongside the existing Orca skill. The native CoS
skill is the canonical coordination intelligence. Python CoS, Codex, and
dispatch modules remain factual/headless compatibility helpers and must not
become a second routing policy engine or the normal interactive launch path.
The guidance delegates Goal Mode, `update_plan`, context, approvals, tools, and
native subagents to Codex rather than rebuilding them in `general-os`. Runtime
IDs, heartbeats, progress mirrors, and temporary runtime plans remain
non-durable.

### Canonical state and planning examples are usable

The repository includes two minimal templates: a coordination-state JSON
example with goal, optional tasks, objectives, dependencies, acceptance, and
optional profile; and a detailed-plan Markdown example for complex ordering or
shared-ownership cases. Goal-only state with an empty task list remains a valid
first-class path.

### Documentation and proof match ownership boundaries

Architecture, contract, recovery, adapter, and README documentation describe
one owner per fact and the shallow routing decision: the native CoS selects a
Codex assignment, Codex may use native subagents internally, Orca is selected
when independent ownership is required or materially useful, and only real
dependency or authority failures block. Tests prove the durable schema,
routing helper behavior, acceptance, CLI persistence, and skill contracts.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `git-tracked`
- Required skills: `skill-code-standards`, `skill-test-driven-development`, `skill-backend-verification`, `skill-writing-skills`, `skill-executing-plans`, `skill-verification-before-completion`
- Isolation: `current workspace`
- Commit policy: `no commits during execution`
- Preauthorized local actions: make changes within the approved semantic scope, including directly affected source, tests, documentation, templates, skills, and small adjacent files discovered during proof; run declared local Python checks and read-only Git inspections.
- User-approval actions: push, merge, publication, destructive recovery, discard, cleanup, new dependencies, new durable state, new runtime ownership, and material scope expansion.
- Parallel ownership: `none`
- Sequential fallback: complete Tasks 1 through 4 in order, then run final verification; do not activate a later task when an earlier task has failed proof or changed scope.

## Coordination State

- Coordination owner: `single lead controller`
- Coordination schema: `2`
- Branch: `main`
- Base commit: `94aaa7be29ce36d533cf8ba6bf6b8d5e7513d65f`
- Expected workspace: `clean at the base commit; this proposed plan is the only current change`
- Next action: `none; implementation and verification complete`
- Blockers: `none`

| Task | State | Workspace | Executor | Depends On | Required Proof | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Task 1 | `completed` | current | `unresolved` | none | focused state, dispatch, acceptance, and CLI tests | `28 passed`; compileall and diff check passed |
| Task 2 | `completed` | current | `unresolved` | Task 1 | template and root-guidance contract checks | `3 passed`; JSON parse passed |
| Task 3 | `completed` | current | `unresolved` | Task 2 | skill contract checks and manual ownership review | `4 passed`; native ownership review passed |
| Task 4 | `completed` | current | `unresolved` | Tasks 1–3 | full test, compile, state, CLI, and Git checks | `58 passed`; compile, CLI, diff, and scope checks passed |

## Task Breakdown

### Task 1: Make task objectives durable and acceptance retryable

**Purpose:**
- Preserve the current durable schema while adding the missing bounded task objective and correcting retryable versus materially blocked verification behavior.

**Task Function:**
- Schema and acceptance contract maintenance.

**Template Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: resolve from reasoning depth, ambiguity, scope, risk, and cost immediately before activation; do not infer runtime settings from the profile name.

**Validator Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: independently select the lowest discovered profile that can verify schema compatibility, dispatch prompts, and transition persistence.

**Specification Coverage:**
- Durable `Task.objective` is the task boundary; missing objectives remain backward-compatible.
- Task dispatch uses `task.objective` for both Codex and Orca requests and uses `state.goal` only for goal-only dispatch.
- `PASS` maps to `completed`; failed, stale, incomplete, or unknown verification leaves the existing task state unchanged; only a genuine `BLOCKED` result maps to `blocked`.
- Runtime IDs and progress remain rejected or absent from serialized state.

**Required Skills:**
- `skill-code-standards`
- `skill-test-driven-development`
- `skill-backend-verification`

**Files And Symbols:**
- Inspect: `src/general_os/state.py:Task`, `src/general_os/cos.py:ChiefOfStaff.dispatch_task`, `src/general_os/acceptance.py:evaluate_acceptance`, `src/general_os/acceptance.py:apply_task_transition`, `src/general_os/cli.py:run_accept`
- Modify: `src/general_os/state.py:Task`, `src/general_os/cos.py:ChiefOfStaff.dispatch_task`, `src/general_os/acceptance.py:evaluate_acceptance`, `src/general_os/acceptance.py:apply_task_transition`, `src/general_os/cli.py:run_accept`
- Verify: `tests/test_state.py`, `tests/test_cos.py`, `tests/test_acceptance.py`, `tests/test_cli.py`

**Dependencies:**
- Baseline commit `94aaa7be29ce36d533cf8ba6bf6b8d5e7513d65f` is clean and remains the comparison base.

**Authority:**
- Preauthorized local actions: change the declared state, acceptance, dispatch, CLI, and directly affected test surfaces within this semantic scope; run focused `pytest`, `compileall`, and read-only Git checks.
- Stop for: any schema change that adds runtime identity/progress fields, any change to Orca lifecycle ownership, any new dependency or durable state, or material scope expansion.

**Steps:**
- [x] Step 1: Extend `Task` with `objective: str | None = None`; validate a provided objective as a non-empty string, accept omission in `from_dict`, include it in `to_dict` only when provided, and preserve old task JSON round trips.
- [x] Step 2: In `ChiefOfStaff.dispatch_task`, compute one prompt from `task.objective` when a task exists and has an objective, otherwise from `state.goal`; pass that prompt unchanged to the selected Codex or Orca dispatch request.
- [x] Step 3: Change `evaluate_acceptance` so Git conflicts and explicit verification blockers remain `BLOCKED`, while stale evidence, missing required proof, failed verification, and unknown verification results return retryable `FAIL` decisions.
- [x] Step 4: Change `apply_task_transition` so `PASS` produces `completed`, genuine `BLOCKED` produces `blocked`, and `FAIL` returns the original state unchanged; keep repeated transitions idempotent.
- [x] Step 5: Update `run_accept` to save durable state for `PASS` and genuine `BLOCKED`, leave state unchanged for `FAIL`, and add focused tests for objective round trips, legacy fallback, both dispatch boundaries, all three transitions, retryable stale/incomplete/failed/unknown evidence, material blockers, and CLI persistence.
- [x] Step 6: Run focused proof before proceeding to governance files.

**Verification:**
- [ ] `python -m pytest -q tests/test_state.py tests/test_cos.py tests/test_acceptance.py tests/test_cli.py`
- Expected: all focused tests pass; task-specific prompts reach the native request seam; retryable evidence never creates `blocked`; genuine `BLOCKED` persists when accepted by the CLI.
- [ ] `python -m compileall -q src`
- Expected: source compiles without errors.

**Exit Criteria:**
- Task objectives are durable but optional for backward compatibility, dispatch no longer sends the global goal for bounded tasks, and acceptance distinguishes retryable failure from material blocking.

### Task 2: Add the canonical root governance and minimal templates

**Purpose:**
- Give the repository one concise ownership contract and two practical examples without importing Project OS Starter’s full governance graph.

**Task Function:**
- Repository contract and artifact-template authoring.

**Template Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: select for precise cross-surface documentation work, not for a runtime capability mapping.

**Validator Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: independently select a profile able to check ownership language, omissions, and template validity.

**Specification Coverage:**
- `general-os` owns durable semantic coordination; Git owns repository/recovery facts; Codex owns native execution; Orca owns independent worker lifecycle.
- Native subagents remain subordinate; runtime completion is evidence, not acceptance; recovery uses durable state plus Git.
- Defaults are native-first and authority stores exceptional material boundaries only.

**Required Skills:**
- `skill-code-standards`
- `skill-writing-skills`

**Files And Symbols:**
- Inspect: `README.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/recovery.md`, `.agents/skills/orca-orchestration/SKILL.md`
- Modify: `AGENTS.md`, `docs/templates/coordination-state.json`, `docs/templates/detailed-plan.md`
- Verify: `tests/test_documentation_contracts.py`

**Dependencies:**
- Task 1 complete and focused tests pass.

**Authority:**
- Preauthorized local actions: create the declared root guidance and template files and directly affected documentation tests; run JSON parsing, Markdown/text contract checks, and read-only Git inspections.
- Stop for: any generated-surface sync requirement not present in this repository, any attempt to add runtime IDs/progress to templates, any new runtime dependency, or any edit to `project-OS-starter`.

**Steps:**
- [x] Step 1: Add a concise root `AGENTS.md` covering SSOT, Git recovery truth, native Codex defaults, subordinate native subagents, the Orca-skill-before-mutation rule, non-persistence of runtime state, evidence-versus-acceptance, and real safety/dependency blockers.
- [x] Step 2: Add `docs/templates/coordination-state.json` with a goal-only example and a task example containing only `id`, `objective`, `state`, `depends_on`, `acceptance`, and optional `profile`; do not include runtime IDs, heartbeats, progress, or mirrored lifecycle fields.
- [x] Step 3: Add `docs/templates/detailed-plan.md` with only Goal, Outcomes, Constraints / decisions, Task graph, per-task Objective/Dependencies/Acceptance, and Final verification.
- [x] Step 4: Extend documentation contract tests to parse the JSON template and assert the root guidance and templates state the ownership boundaries, durable-field allowlist, and goal-only validity through observable content and schema assertions.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py`
- Expected: documentation and template contracts pass; the coordination template parses as JSON and contains no runtime mirror keys.
- [ ] `python -c "import json; json.load(open('docs/templates/coordination-state.json', encoding='utf-8'))"`
- Expected: command exits `0`.

**Exit Criteria:**
- Root governance and both templates are concise, canonical, native-first, and free of Project OS Starter runtime machinery.

### Task 3: Add the four native Codex governance skills

**Purpose:**
- Encode the semantic roles that remain after native Codex and Orca own their execution lifecycles, without creating a second runtime policy engine.

**Task Function:**
- Native governance skill authoring.

**Template Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: choose based on documentation complexity and contract risk; define four new core skills alongside the existing Orca skill without prohibiting future specialized skills.

**Validator Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: independently select a profile able to detect accidental reintroduction of runtime orchestration or duplicate ledgers.

**Specification Coverage:**
- `chief-of-staff` is the canonical coordination intelligence: it reads durable intent and Git, selects ready work/profile/boundary, reconciles evidence, and accepts/continues/blocks.
- `src/general_os/cos.py` remains a deterministic headless/helper surface for CLI and tests; it must not become a second authoritative routing policy engine.
- `defining-work` supports goal-only, small task graph, and detailed-plan depths.
- `executing-work` selects a Codex assignment and lets Codex use Goal Mode, `update_plan`, native tools, approvals, context, and subordinate native subagents without task-ledger choreography or a separate CoS child-runtime strategy.
- `verification-before-completion` derives fresh Git/evidence status as `PASS | FAIL | BLOCKED` and does not own branch disposition, cleanup, or runtime lifecycle.
- Existing `orca-orchestration` remains the native Orca lifecycle boundary and is not duplicated.
- `requires_independent_boundary` is a hard requirement/override, not the complete Orca selection algorithm; native CoS may choose Orca when independent ownership is materially useful even when the flag is absent.

**Required Skills:**
- `skill-writing-skills`
- `skill-chief-of-staff`
- `skill-orca-orchestration`

**Files And Symbols:**
- Inspect: `.agents/skills/orca-orchestration/SKILL.md`, `src/general_os/cos.py:ChiefOfStaff`, `src/general_os/codex.py:CodexClient`, `src/general_os/dispatch.py`, `docs/runtime-adapters.md`, `docs/architecture.md`, `docs/recovery.md`
- Modify: `.agents/skills/chief-of-staff/SKILL.md`, `.agents/skills/defining-work/SKILL.md`, `.agents/skills/executing-work/SKILL.md`, `.agents/skills/verification-before-completion/SKILL.md`
- Verify: `tests/test_documentation_contracts.py`

**Dependencies:**
- Task 2 complete and the root ownership contract is present.

**Authority:**
- Preauthorized local actions: create the four declared skill files and directly affected documentation tests; run skill contract checks and read-only inspections of the existing Orca skill and headless adapters.
- Stop for: any skill that introduces a new runtime owner, durable ledger, runtime dependency, or material scope expansion.

**Steps:**
- [x] Step 1: Create each skill with frontmatter matching the repository’s existing skill format and a short purpose statement.
- [x] Step 2: Define the native CoS skill as semantic routing and acceptance coordination, not an agent loop or runtime scheduler; document that Python `cos.py` is only a headless/helper projection and require direct Git observation and durable-state recovery.
- [x] Step 3: Define planning depth selection and the two execution templates without requiring executor/runtime metadata in ordinary goal-only work.
- [x] Step 4: Define Codex-native execution as the normal interactive path and mark `CodexClient`/`dispatch.py` as optional headless compatibility; document subordinate child delegation, explicit use of `update_plan`, native approvals, context, and tools, and require the Orca skill before any Orca mutation.
- [x] Step 5: Define verification as fresh evidence and Git comparison with `PASS`, `FAIL`, and `BLOCKED`; state that runtime completion never changes durable acceptance by itself.
- [x] Step 6: Assert the five core skill surfaces, including the existing Orca skill, while allowing future specialized skills that do not become runtime dependencies or duplicate ownership.

**Verification:**
- [ ] `python -m pytest -q tests/test_documentation_contracts.py`
- Expected: the five core skill surfaces are found; native Codex ownership, subordinate subagents, Orca boundary, headless-helper status, runtime non-persistence, and acceptance separation are explicit.

**Exit Criteria:**
- The repository has five core governance skills in scope: the four new Codex skills plus the existing `orca-orchestration` skill. Specialized skills remain possible when they do not become required runtime dependencies or duplicate a native owner.

### Task 4: Reconcile documentation and execute final semantic proof

**Purpose:**
- Align public repository documentation and prove the complete native-first routing/acceptance path without adding another runtime layer.

**Task Function:**
- Cross-surface contract reconciliation and final verification.

**Template Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: select the lowest profile that can reconcile source, tests, docs, skills, and final evidence.

**Validator Profile:**
- Controller-selected: `unresolved while task is pending`
- Selection basis: independently select a profile for fresh final verification; validator capability is not ordered relative to executor capability.

**Specification Coverage:**
- Documentation names one durable owner per fact and direct observation at point of use.
- Goal-only Codex execution remains valid; task objectives route to the right worker; optional native subagents remain Codex-owned; required independent work routes to Orca.
- Fresh Git/evidence controls acceptance, and recovery starts from durable state plus Git rather than runtime history.
- `project-OS-starter` remains unmodified.

**Required Skills:**
- `skill-backend-verification`
- `skill-verification-before-completion`

**Files And Symbols:**
- Inspect: all files declared by Tasks 1–3, `state/coordination.json`, `repo_config/runtime-policy.toml`
- Modify: `README.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/recovery.md`, `docs/runtime-adapters.md`, `tests/test_documentation_contracts.py`, and any focused test files from Task 1 when proof exposes a contract gap
- Verify: repository-wide tests, source compilation, CLI state validation, CoS next decision, Git scope, and `project-OS-starter` diff absence

**Dependencies:**
- Tasks 1–3 complete and their task-local proof accepted.

**Authority:**
- Preauthorized local actions: reconcile verified behavior across the declared documentation/test surfaces and directly affected adjacent files within this semantic scope; run the final local verification commands and read-only Git scope checks.
- Stop for: failed required proof, changed behavior not covered by Tasks 1–3, any external write, new dependency or durable/runtime owner, material scope expansion, or any path under `project-OS-starter` appearing in the diff.

**Steps:**
- [x] Step 1: Update architecture, contracts, recovery, runtime-adapter, and README text to describe task objectives, retryable failure, material blockers, native Codex ownership, optional Orca, and no runtime persistence.
- [x] Step 2: Add/adjust integration assertions so a goal-only state returns the headless helper’s `codex` observation with `task_id = null`, a task objective reaches the dispatch request, a required-independent task cannot fall back to Codex when Orca permission is unavailable, and native CoS documentation permits Orca when independent ownership is materially useful even without the hard-requirement flag.
- [x] Step 3: Run the repository-wide test and compile checks, then validate the checked-in state and goal-only CLI route.
- [x] Step 4: Inspect the diff and untracked paths against the plan; confirm no file under `project-OS-starter` changed and no runtime ID/progress mirror entered durable state or templates.
- [x] Step 5: Record fresh evidence and mark the plan complete only after final verification passes.

**Verification:**
- [x] `python -m pytest -q` — `58 passed`
- Expected: all repository tests pass.
- [x] `python -m compileall -q src` — passed
- Expected: all source compiles.
- [x] `python -m general_os state validate state/coordination.json` — `status: valid`, `task_count: 0`
- Expected: JSON reports `status` `valid` and the goal-only state remains accepted.
- [x] `python -m general_os cos next --state state/coordination.json --repo . --json` — `strategy: codex`, `task_id: null`, `reason: goal-only assignment`
- Expected: JSON reports `strategy` `codex`, `task_id` `null`, and reason `goal-only assignment`.
- [x] `git diff --check` — passed
- Expected: no whitespace errors.
- [x] `git diff --name-only 94aaa7be29ce36d533cf8ba6bf6b8d5e7513d65f --; git ls-files --others --exclude-standard` — all paths are in plan scope; no `project-OS-starter` path appears
- Expected: every changed/untracked path is declared by this plan, and no `project-OS-starter` path appears.

**Exit Criteria:**
- Source behavior, tests, docs, templates, and skills agree on native-first ownership; final proof is fresh; no duplicate coordination owner or out-of-scope repository changes remain.

## Verification

Final artifact-level verification is:

- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os cos next --state state/coordination.json --repo . --json`
- `git diff --check`
- `git diff --name-only 94aaa7be29ce36d533cf8ba6bf6b8d5e7513d65f --`
- `git ls-files --others --exclude-standard`

The final evidence must distinguish:

- durable task objective behavior and backward compatibility;
- `PASS`, retryable `FAIL`, and material `BLOCKED` transitions;
- goal-only Codex routing and task-specific dispatch;
- native subagent subordination and Orca-only independent ownership;
- current Git/evidence acceptance and recovery from state plus Git;
- the five-skill governance surface;
- absence of runtime IDs/progress mirrors and changes under `project-OS-starter`.

## Completion Criteria

The plan is ready for completion verification when:

1. `Task.objective` is optional, durable, validated, serialized, and used as
   the bounded dispatch prompt without breaking old state files.
2. `PASS` completes, `FAIL` remains retryable, and `BLOCKED` is reserved for a
   real material blocker and persisted by the acceptance CLI path.
3. Root guidance and templates describe one owner per fact and contain no
   runtime identity, progress, scheduler, registry, or parity mirror.
4. The repository has the four new native Codex governance skills plus the
   existing Orca skill as its core governance surface; specialized skills may
   exist without becoming runtime dependencies or duplicating native ownership.
5. Documentation and tests prove Codex-first execution, subordinate native
   subagents, optional Orca, current Git/evidence acceptance, and durable-state
   plus Git recovery.
6. All task-local and final checks pass, declared scope is clean, and
   `project-OS-starter` remains untouched.

The plan may be marked `completed` only after
`skill-verification-before-completion` returns `verified` for the implementation
and evidence. The plan remains `proposed` until an explicit approval starts
execution.
