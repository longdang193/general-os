---
layer: change
artifact_type: plan
contract_version: "1"
status: completed
template_id: implementation-plan
name: general-os-native-first-operational-hardening
---

# Goal

Prove the native-first `general-os` architecture at its real runtime boundaries,
retire obsolete Python runtime seams, and keep the durable coordination layer
small without introducing a scheduler, runtime registry, or duplicated state.

# Implementation Outcomes

- Codex and Orca compatibility-boundary failures remain transient observations;
  they do not mutate durable state or automatically create `blocked` tasks.
- Native Codex remains the normal execution path; native subagents remain owned
  by the current Codex assignment.
- Orca remains lazy and optional: it is selected only for independent work, and
  maintained documentation defines future worker-harness resolution from the
  general-os profile rather than from an Orca-owned profile registry.
- `cos.py`, `codex.py`, `dispatch.py`, and `recovery.py` are deleted after their
  consumers and compatibility tests are removed; the injected Orca lifecycle
  seam is removed while read-only native Orca status remains available if the
  smoke command needs it.
- Maintained documentation describes profiles as canonical general-os policy:
  profile names do not imply guessed settings, explicitly declared runtime facts
  may be projected one way, and missing fields inherit native defaults.
- Orca documentation is harness-neutral: an independent worker may use Codex,
  Claude, or another explicitly supported harness later; Orca owns orchestration,
  not capability-profile selection.
- Documentation tests validate schemas, ownership, and behavior without exact
  prose blacklists, exact wording assertions, or skill-count invariants.
- Recovery remains durable semantic state plus current Git plus fresh native
  execution. No runtime IDs, worker lifecycle, progress, or profile parity state
  is persisted.

# Constraints / decisions

- Do not modify `project-OS-starter`.
- Keep task states `pending`, `active`, `blocked`, and `completed`; keep
  `Task.objective` backward-compatible.
- Do not infer `high` → effort/model or any other runtime setting from a profile
  name. Project only explicit profile facts such as `harness`, `model`, `effort`,
  or `instructions`; absent fields inherit the native runtime default.
- Keep `agents/*.toml` as the only profile registry. Do not add Orca profiles,
  provider matrices, a live model catalog, or a second capability algebra.
- Do not implement the full profile-projection schema in this hardening slice.
  Record the follow-up boundary for a small `profiles.py`/`agents/*.toml`/
  native-skill projection slice instead of encoding profiles as descriptive-only
  metadata.
- CoS selects the execution boundary (`Codex` local or `Orca` independent).
  The resolved profile selects only the compatible worker-harness configuration;
  a Claude-capable profile must not force Orca around ordinary local work.
- Python compatibility tests are headless/compatibility-contract proof only;
  they are not proof of the interactive native Codex path.
- Use native project skills for execution: `chief-of-staff`, `defining-work`
  when a durable task graph is needed, `executing-work`,
  `verification-before-completion`, and `orca-orchestration` when Orca is used.
  `skill-backend-verification` is optional specialist guidance, not a core
  Project-OS dependency.
- No live Orca worker launch, remote side effect, authentication, commit, push,
  or external publication is part of this plan.

# Task Breakdown

## Task 1 — Compatibility-boundary failure proof

Objective: Prove the existing headless Codex/Orca compatibility surfaces preserve
transient failure semantics without claiming to test the interactive native
runtime.

Files:
- Inspect `src/general_os/codex.py`, `src/general_os/orca.py`,
  `src/general_os/dispatch.py`, `src/general_os/cos.py`,
  `src/general_os/acceptance.py`, and existing focused tests.
- Extend only missing cases in `tests/test_codex.py`, `tests/test_orca.py`,
  `tests/test_cos.py`, `tests/test_acceptance.py`, and `tests/test_cli.py`.

Changes:
- Prove Codex and Orca unavailable/failed observations are transient and do not
  mutate `state/coordination.json`.
- Prove retryable `FAIL`, stale evidence, and incomplete proof leave tasks
  unfinished; only an explicit material blocker can produce durable `BLOCKED`.
- Prove ordinary work remains Codex-first and required independent work never
  silently falls back to Codex.
- Keep runtime identity and progress out of durable state.

Dependencies: none.

Acceptance:

- `python -m pytest -q tests/test_codex.py tests/test_cos.py tests/test_orca.py tests/test_acceptance.py tests/test_cli.py`
- The result is recorded as compatibility/headless boundary proof, not native
  interactive Codex proof.

## Task 2 — Retire obsolete Python runtime seams

Objective: Delete Python runtime clients and orchestration helpers that no longer
own execution, without replacing them with another coordination abstraction.

Files:
- Delete `src/general_os/cos.py`, `src/general_os/codex.py`,
  `src/general_os/dispatch.py`, and `src/general_os/recovery.py`.
- Delete `tests/test_codex.py`, `tests/test_cos.py`, and `tests/test_recovery.py`
  when their exclusive coverage is no longer applicable.
- Modify `src/general_os/cli.py` to remove `_build_cos`, `cos next`, `runtime
  inspect`, and `recover`; retain `state validate`, `accept`, and read-only
  `orca smoke`.
- Modify `src/general_os/orca.py` to remove `OrcaTransport`, `OrcaRequest`,
  `OrcaObservation`, and `OrcaClient`, retaining only
  `OrcaCliStatusObserver`/`OrcaStatusObservation` if the smoke command requires
  them.
- Reduce `tests/test_orca.py` to native status-observer coverage and update
  `tests/test_cli.py` for the retained command surface.

Changes:

- Inventory imports and references before deletion with `rg`.
- Remove only consumers of the obsolete seams; do not add a replacement
  scheduler, launcher, registry, retry loop, or recovery ledger.
- Make recovery documentation and native skills the source of the
  state-plus-Git-plus-fresh-runtime recovery procedure.

Dependencies: Task 1.

Acceptance:

- `python -m compileall -q src`
- `python -m pytest -q tests/test_cli.py tests/test_orca.py tests/test_acceptance.py`
- `python -m general_os --help` contains no Python runtime-dispatch or recovery
  commands.
- This reference scan returns no maintained consumers outside the plan/history
  directory:
  `rg -n "general_os\\.(cos|codex|dispatch|recovery)|ChiefOfStaff|CodexClient|OrcaClient|OrcaTransport|next_unfinished_task|cos next|runtime inspect|run_recover" src tests docs .agents/skills README.md --glob "!docs/superpowers/plans/**"`

## Task 3 — Align documentation, profiles, and harness-neutral Orca ownership

Objective: Make maintained documentation and contract tests express the actual
general-os architecture without implementing the deferred profile-projection
slice.

Files:
- Modify `README.md`, `docs/architecture.md`, `docs/contracts.md`,
  `docs/recovery.md`, and `docs/runtime-adapters.md`.
- Inspect `agents/*.toml`, `src/general_os/profiles.py`, and
  `tests/test_profiles.py`; do not add profile fields or projection code in this
  slice.
- Modify `.agents/skills/chief-of-staff/SKILL.md`,
  `.agents/skills/defining-work/SKILL.md`,
  `.agents/skills/executing-work/SKILL.md`,
  `.agents/skills/verification-before-completion/SKILL.md`, and
  `.agents/skills/orca-orchestration/SKILL.md`.
- Modify `tests/test_documentation_contracts.py`.

Changes:

- Replace descriptive-only profile wording with canonical-profile wording: names
  do not imply values; explicit fields may be projected one way; missing fields
  inherit native defaults.
- State that `agents/*.toml` is the sole profile registry and no Orca profile
  registry exists.
- State that CoS chooses Codex versus Orca independently of harness choice, and
  an Orca worker may use Codex or Claude according to the resolved profile.
- Mark the Python adapter tests as compatibility/headless contracts and keep
  native Codex execution owned by the current Codex runtime.
- Remove exact prose, blacklist, and skill-count assertions; retain stable
  schema, ownership, command-surface, and behavioral assertions.
- Keep the deferred profile-projection slice explicit so this plan does not
  silently expand into a provider matrix or runtime layer.

Dependencies: Tasks 1 and 2.

Acceptance:

- `python -m pytest -q tests/test_documentation_contracts.py tests/test_cli.py tests/test_orca.py tests/test_acceptance.py tests/test_profiles.py`
- Documentation and skills consistently describe native Codex, optional
  harness-neutral Orca, canonical profiles, one-way explicit projection, and
  recovery from durable state plus Git.

## Task 4 — Fresh repository and native runtime verification

Objective: Verify the complete slice against current source, Git, and the
installed read-only Orca boundary.

Dependencies: Tasks 1–3.

Acceptance:

- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os --help`
- `orca --version`
- `orca status --json`
- `orca skills get orchestration --full`
- `python -m general_os orca smoke --json`
- `git diff --check`
- `git status --short --branch`
- Confirm no path under `project-OS-starter` changed, no runtime IDs/progress/
  lifecycle mirror exists in durable state, and no undeclared file changed.
- Orca readiness is recorded as current transient evidence only; unavailable or
  failed status is reported honestly without changing policy or durable state.

# Verification

- `python -m pytest -q`
- `python -m compileall -q src`
- `python -m general_os state validate state/coordination.json`
- `python -m general_os --help`
- `orca --version`
- `orca status --json`
- `orca skills get orchestration --full`
- `python -m general_os orca smoke --json`
- `git diff --check`
- `git status --short --branch`
- Reference/import scan excluding `docs/superpowers/plans/**`
- Confirm `project-OS-starter` is untouched.

# Completion Criteria

- Compatibility/headless failure tests pass without being presented as native
  interactive runtime proof.
- Obsolete Python runtime seams and their exclusive tests are removed with no
  dangling maintained references.
- Documentation and native skills define canonical explicit profile projection,
  harness-neutral Orca ownership, lazy health observation, and boring recovery.
- The profile-projection implementation remains an explicit follow-up rather
  than an unplanned schema or runtime-layer expansion.
- Fresh repository, CLI, Orca, and Git checks pass; no `project-OS-starter` path
  changes.

The plan remains `proposed` until explicitly approved. It may be marked
completed only after fresh verification confirms the outcomes above. Commit,
push, live Orca worker operations, and external side effects remain separate
authorized actions.
