---
layer: change
artifact_type: plan
template_id: implementation-plan
contract_version: "1"
status: proposed
name: general-os-acceptance-recovery-git-deployment-boundaries
targets:
  - src/general_os/state.py
  - src/general_os/acceptance.py
  - src/general_os/cli.py
  - src/general_os/git.py
  - src/general_os/deployment.py
  - src/general_os/profiles.py
  - .agents/skills/chief-of-staff/SKILL.md
  - src/general_os/assets/skills/chief-of-staff/SKILL.md
  - tests/test_state.py
  - tests/test_acceptance.py
  - tests/test_cli.py
  - tests/test_git.py
  - tests/test_deployment.py
  - tests/test_profiles.py
  - tests/test_documentation_contracts.py
  - docs/architecture.md
  - docs/contracts.md
  - docs/recovery.md
---

# General OS Acceptance, Recovery, Git, And Deployment Boundaries Plan

## Goal

Make durable completion, recovery, Git snapshot identity, deployment
application, and profile documentation agree with the thin native-first
general-os architecture, without adding another runtime coordinator or
changing Codex/Orca ownership.

## Review basis

The approved scope comes from two completed, revision-pinned read-only reviews
of `longdang193/general-os` at commit
`34a4e96fc1905242b5f3ae113b51747f0d2abc0b` using `GPT-5.6-Sol` and `GPT-6`,
both at `High` effort. The reviews agreed that native execution ownership is
intact and identified boundary weaknesses in completion/recovery, Git snapshot
identity, deployment application, and profile documentation.

## Outcomes

- A completed task cannot be accepted as durable state without the acceptance
  identities required by the existing contract, and recovery uses the existing
  task-contract/dependency revalidation semantics before relying on completed
  work.
- Git snapshot identity is independent of the directory from which the
  repository is inspected and continues to exclude only the documented
  coordination-state content.
- Deployment application does not overwrite a target changed after planning;
  concurrent-change handling remains local, bounded, and recoverable.
- Profile documentation matches the existing intentional behavior: explicit
  missing profiles fail clearly, while implicit profile selection may inherit
  native defaults.
- Existing Codex, native-subagent, Orca, Git, acceptance, recovery, and
  deployment ownership boundaries remain intact.

## Constraints / decisions

- Keep `state/coordination.json` as the only durable coordination state and
  `agents/*.toml` as the only profile registry.
- Reuse `revalidate_completed_tasks`, existing acceptance tokens, existing
  state compare-and-save behavior, existing deployment ownership metadata, and
  existing native runtime boundaries before adding new mechanisms.
- Preserve historical acceptance across unrelated Git changes. Do not turn
  snapshot divergence alone into a durable failure or global revalidation
  sweep.
- Do not persist revalidation candidate lists, runtime IDs, verifier sessions,
  deployment sessions, worker registries, retry counters, or lifecycle mirrors.
- If an existing historical state contains a completed task without acceptance
  identities, do not silently rewrite, discard, or auto-migrate it. Preserve
  the file, report a deterministic compatibility condition, and stop for an
  explicit migration decision; newly created or normalized completed records
  must satisfy the invariant.
- Deployment concurrency protection must be a narrow local coordination
  mechanism. Do not add a deployment daemon, service, or durable deployment
  ledger.
- Do not add verifier command receipts or a persistent verifier service. The
  in-process verification handoff remains the trust boundary unless concrete
  untrusted callers are discovered.
- Do not expand this change into packaged-skill synchronization machinery. If
  the canonical CoS recovery contract changes, update only its required
  packaged mirror and verify equality; the current trees have matching file
  inventories and no observed content drift.

## Exclusions

- No Python Codex scheduler, Orca scheduler, worker registry, runtime ledger,
  second profile registry, or replacement orchestration layer.
- No change to Codex native delegation, Orca internal topology, or runtime
  fallback policy.
- No redesign of verification provenance beyond preserving the existing
  explicit in-process boundary.
- No behavior change to implicit native-default profile inheritance.
- No publication, push, merge, commit, or cleanup of unrelated `.serena/`
  workspace state as part of plan execution.

## Execution approach

- **Mode:** inline sequential; one lead executor owns the ordered changes.
- **Coordination:** no durable worker or runtime registry; native Codex planning
  and optional subordinate delegation remain runtime-local.
- **Ordering:** normalize Git identity before finalizing completion/recovery
  integration evidence; settle completion/recovery behavior before updating
  the canonical and packaged CoS guidance; deployment protection is
  independently bounded.
- **Shared-write control:** tasks touch shared acceptance/state and test
  surfaces, so execute them serially in one checkout unless a fresh executor
  establishes a safe isolated workspace.
- **Stop conditions:** stop before changing persisted historical state when
  legacy completed records lack acceptance identities; stop before broadening
  deployment locking if the required lock scope cannot remain local and
  bounded; return for a decision if current tests contradict the approved
  contracts.
- **Authority:** this plan authorizes source, test, and documentation changes
  only. Git disposition and any publication remain separate explicit actions.

## Task graph

## Task A — Canonicalize Git snapshot identity

**Objective:**

Ensure all Git status, diff, and untracked-file reads use one canonical
repository root so `GitSnapshot.identity` represents the same worktree whether
inspection begins at the repository root or a nested directory.

**Scope:**

The `GitRepository` observation boundary and its focused regression tests.
Preserve branch, revision, conflict, changed-file, coordination-state
exclusion, symlink, and bounded untracked-file behavior.

**Dependencies:**

None.

**Durable sequencing:**

Complete before final acceptance/recovery verification because acceptance
evidence binds to `GitSnapshot.identity`.

**Acceptance:**

- Root and nested-directory inspection of the same repository state produce
  equivalent identity inputs.
- Root-level tracked changes and root-relative untracked files are included
  when inspection starts below the repository root.
- Existing coordination-state exclusion and current Git snapshot semantics are
  unchanged.

**Verification:**

- Add a focused regression covering nested inspection with a root-level tracked
  change and an untracked path.
- Run the Git-focused tests and the existing acceptance tests that consume
  snapshot identity.

**Stop / escalation conditions:**

Stop if canonical-root handling changes the documented identity inputs or
causes the coordination-state exclusion to broaden.

## Task B — Enforce durable completion and recovery semantics

**Objective:**

Close the gap between the documented acceptance contract and the durable state
and recovery paths: completed tasks must carry valid acceptance identities, and
recovery must use the existing revalidation semantics before relying on them.

**Scope:**

The state validation boundary, a single thin `state revalidate` recovery entry
point through the existing CLI/library surface, the canonical native CoS
recovery contract and its required packaged mirror, and focused tests and
contract documentation. Keep historical snapshot identity as evidence of
where acceptance occurred; do not demote completed tasks merely because
unrelated Git state changed.

**Dependencies:**

Task A.

**Durable sequencing:**

Resolve compatibility for any legacy completed records before applying a
stricter persisted-state invariant. Do not silently rewrite such records.

**Constraints / decisions:**

- Reuse `revalidate_completed_tasks` and existing compare-and-save semantics.
- Revalidation must remain task-contract/dependency based and must not persist a
  global candidate list.
- The recovery entry point may inspect current Git, invoke the existing
  revalidation helper, and compare-and-save only changed durable state. It must
  not select work, manufacture `PASS` evidence, or become a second coordinator.
- The canonical CoS recovery guidance must require this revalidation boundary
  before dependency-ready selection; update only the matching packaged mirror
  and verify it remains identical.
- The CLI and recovery guidance must not manufacture `PASS` evidence or add a
  second verifier/runtime boundary.

**Acceptance:**

- A completed task missing required acceptance identities is rejected as an
  impossible new/normalized durable record. A historical record with missing
  identities remains preserved but produces the explicit compatibility
  condition; it is not silently accepted, demoted, or rewritten.
- The `state revalidate` recovery entry point and canonical CoS guidance
  revalidate completed task-contract fingerprints and dependency closure before
  relying on them.
- A changed task contract invalidates that task and affected completed
  dependents through the existing semantics.
- Unrelated Git changes preserve historical completion and do not trigger a
  global sweep.

**Verification:**

- Add negative state-validation coverage for completed tasks without acceptance
  identities.
- Add CLI/integration coverage proving the recovery entry point invokes the
  existing revalidation behavior and preserves compare-and-save semantics.
- Add documentation-contract coverage for the canonical and packaged CoS
  recovery guidance.
- Run focused state, acceptance, recovery/documentation-contract, and Git tests.

**Stop / escalation conditions:**

Stop if compatibility requires changing existing persisted user state without
an explicit migration decision, if the recovery boundary would need to select
work or own runtime lifecycle, or if enforcing the invariant would make
historical acceptance disappear for unrelated Git changes.

## Task C — Protect deployment application from stale plans

**Objective:**

Prevent `apply_plan` from overwriting or removing a target that changed after
the plan was built, while keeping deployment a simple local installation
operation.

**Scope:**

Deployment plan/application ownership checks, narrow concurrency protection,
rollback behavior, and focused deployment tests. Preserve dry-run, check,
prune, central lock, project adoption, and existing preservation behavior.

**Dependencies:**

None; integrate before final verification.

**Constraints / decisions:**

- Revalidate expected target ownership/content immediately before mutation.
- On an intervening change, abort with a deterministic stale-plan report;
  require a fresh deployment invocation to replan, without overwriting the
  newer content.
- Roll back only changes made by the current deployment attempt; never erase an
  intervening user change.
- Do not add a daemon, service, or durable deployment session state.

**Acceptance:**

- A target modified between planning and application is detected and preserved.
- A successful application still updates owned unchanged targets and writes
  managed metadata in the existing order.
- Injected application failures retain current rollback guarantees.
- Concurrent or stale-plan handling has a deterministic failure report and no
  silent overwrite.

**Verification:**

- Add a focused stale-plan/concurrent-change regression.
- Run deployment and CLI tests, including dry-run, check, prune, adoption, and
  rollback coverage.

**Stop / escalation conditions:**

Stop if safe protection requires a lock scope wider than the local deployment
  targets or would make ordinary read-only checks block on unrelated work.

## Task D — Align profile-default contract documentation

**Objective:**

Make architecture and contract documentation accurately describe the existing
profile resolution behavior without changing native-default inheritance.

**Scope:**

Profile documentation and documentation-contract tests only, unless current
source evidence reveals an actual behavior mismatch.

**Dependencies:**

None for implementation. Complete after Tasks A–C so the final wording and
generated mirror reflect settled behavior contracts.

**Acceptance:**

- Documentation states that explicitly requested missing profiles fail clearly.
- Documentation states that implicit profile selection may return the neutral
  profile and inherit native runtime defaults.
- Documentation tests prevent the two interpretations from diverging again.

**Verification:**

- Run focused profile and documentation-contract tests.
- Confirm no profile registry, runtime model, effort, or provider behavior was
  changed.

## Final verification

- Re-read the final diff against this plan and current `AGENTS.md`; confirm no
  runtime coordinator, worker registry, verifier service, or durable lifecycle
  mirror was introduced.
- Run `pytest -q tests/test_state.py tests/test_acceptance.py tests/test_cli.py tests/test_git.py tests/test_deployment.py tests/test_profiles.py tests/test_documentation_contracts.py`.
- Run the full `pytest -q` suite.
- Run `python -m general_os state validate state/coordination.json`.
- Run `git diff --check` and verify the working tree contains only intended
  source, test, and documentation changes; preserve unrelated `.serena/` state.
- Confirm fresh evidence for each outcome: completed-state rejection or
  compatibility handling, recovery revalidation, nested Git identity, stale
  deployment-plan protection, profile contract wording, and all existing
  native ownership boundaries.

