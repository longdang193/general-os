---
layer: change
artifact_type: plan
template_id: implementation-plan
contract_version: "1"
status: proposed
name: general-os-native-openspec-ownership-boundaries
targets:
  - README.md
  - AGENTS.md
  - docs/architecture.md
  - docs/contracts.md
  - docs/recovery.md
  - docs/runtime-adapters.md
  - .agents/skills/chief-of-staff/SKILL.md
  - .agents/skills/spec-drafting/SKILL.md
  - .agents/skills/defining-work/SKILL.md
  - .agents/skills/executing-work/SKILL.md
  - .agents/skills/orca-orchestration/SKILL.md
  - .agents/skills/verification-before-completion/SKILL.md
  - src/general_os/assets/skills/chief-of-staff/SKILL.md
  - src/general_os/assets/skills/spec-drafting/SKILL.md
  - src/general_os/assets/skills/defining-work/SKILL.md
  - src/general_os/assets/skills/executing-work/SKILL.md
  - src/general_os/assets/skills/orca-orchestration/SKILL.md
  - src/general_os/assets/skills/verification-before-completion/SKILL.md
  - src/general_os/assets/docs/runtime-adapters.md
  - src/general_os/assets/project-kit/AGENTS.md
  - tests/test_documentation_contracts.py
  - tests/test_deployment.py
  - tests/test_orca.py
  - tests/test_acceptance.py
  - tests/test_state.py
  - tests/test_git.py
---

# General OS Native OpenSpec Ownership Boundaries Plan

## Goal

Align general-os with the proposed decision-first, native-first architecture:
General OS retains durable high-level decisions and exceptional commitments;
adopted projects use native OpenSpec for change specifications; Codex remains
the default execution harness; Orca remains optional native orchestration; and
verification stays with the authoritative source for each claim.

## Outcomes

- Ordinary authorized repository work can proceed through native Codex and
  project tools without creating General OS coordination state or invoking CoS.
- OpenSpec-enabled projects use native specs, changes, design notes, and task
  checklists without copying them into `state/coordination.json` or a new
  general-os registry.
- Projects without OpenSpec, and small/reversible changes where OpenSpec is not
  appropriate, retain the existing specification route.
- Within already authorized scope, native work may select Orca when independent
  orchestration materially improves the assignment, while native Orca
  preflight and hard-boundary checks remain intact.
- Repository verification remains Git- and test-grounded where Git is the
  relevant evidence source. Strategic or external findings use source-specific
  evidence without claiming unsupported durable PASS transitions.
- Maintained guidance and checked-in packaged counterparts remain consistent.
- A separately authorized pilot may validate the workflow, but its absence does
  not block completion of the local general-os changes.

## Constraints / decisions

- The core architecture is a proposed target, not current implementation
  truth. Implementation must distinguish verified current behavior from target
  behavior and preserve existing functionality until each boundary is proven.
- General OS is not a mandatory front door, scheduler, specification database,
  universal router, or second acceptance authority.
- OpenSpec integration is conditional on project adoption and task suitability.
  This repository is not OpenSpec-enabled by this plan; do not add an
  `openspec/` tree here merely to demonstrate integration.
- OpenSpec owns change-local requirements, proposal, technical design notes,
  changed specs, and tasks when adopted. Figma/OpenDesign or project code may
  own visual design, prototypes, tokens, or interfaces; link those sources
  rather than copying them into OpenSpec or general-os.
- An active OpenSpec change is a proposal until native reconciliation updates
  maintained specs. It must not silently override existing requirements.
- `tasks.md` is a local change checklist, not a durable general-os dependency
  graph. Do not mirror OpenSpec tasks, runtime IDs, progress, heartbeats, or
  worker topology into durable state.
- Native Codex owns direct execution, planning, approvals, and subordinate
  agents. Native Orca owns internal decomposition, workers, supervision,
  retries, synthesis, and cleanup when selected.
- Orca may be selected without a new high-level General OS task only within
  already authorized scope. A hard independence requirement that cannot be
  satisfied remains a blocker; optional independence may fall back to Codex.
- Source-specific review of strategic or external findings is distinct from
  repository-bound task acceptance. Do not represent an external-only review as
  a successful durable task transition unless its evidence can be validated by
  a supported acceptance contract.
- Preserve the current `acceptance.py` and durable-state contract initially.
  Do not add external-evidence acceptance APIs unless a pilot demonstrates a
  concrete requirement that existing source-specific evidence cannot satisfy.
- Modify maintained files and their checked-in packaged counterparts in the
  same change where a counterpart exists. Preserve equality with existing
  tests; do not assume or introduce a source-to-package generator.
- The approved frontend design-tool rule is already present in the working
  tree. Preserve its canonical/packaged parity; do not duplicate its guidance
  in this plan's implementation.
- Do not add a capability registry, tool router, OpenSpec adapter, persistent
  worker manager, watcher, schema version, migration framework, or automated
  cross-tool synchronization.
- The pilot is validation work, not authorization for cross-repository edits,
  commits, publication, or deployment. Its target project and Git authority
  must be named explicitly before it starts.

## Task graph

The local implementation consists of three workstreams. They may remain one
native Codex assignment; this plan does not require a durable A–C task graph or
independent delegation.

## Task A — Ownership contract

**Objective:**

Make the decision-first ownership model explicit in repository documentation
and audit active guidance for obsolete mandatory handoffs.

**Scope:**

Update the architecture, contracts, recovery, runtime-boundary, and README
wording needed to distinguish General OS decisions, project specifications,
native Codex execution, native Orca topology, Git facts, and source-specific
verification.

Audit, but do not automatically rewrite, the current root `AGENTS.md`,
`requesting-code-review`, `refactoring-assessment`, `brainstorming`, and
packaged project-kit guidance. Change an audited surface only if it actually
forces routine work through CoS, duplicates a native owner, or contradicts the
approved ownership contract. Treat generated guidance as derived from its
canonical source; do not edit a generated surface directly.

**Dependencies:**

None.

**Acceptance:**

- Ordinary work is explicitly allowed to bypass General OS and CoS.
- General OS remains responsible for high-level decisions, material
  constraints, and exceptional coordination only.
- The audited active guidance either agrees with this contract or has a
  justified minimal correction.
- No new durable state, registry, or runtime ledger is introduced.

**Verification:**

- Perform a targeted phrase audit for CoS, ordinary work, execution boundaries,
  acceptance, design approval, and defining-work handoffs.
- Review changed documentation against the proposed core architecture and
  current `AGENTS.md` ownership rules.
- Run documentation-contract checks after any maintained guidance changes.

**Stop / escalation conditions:**

Stop if resolving a contradiction requires transferring Codex, Orca, Git, or
project-specification ownership to general-os, or if the canonical source for a
generated guidance file cannot be identified.

## Task B — Native skill routing

**Objective:**

Make native OpenSpec and optional native Orca routing conditional and
authority-preserving without creating wrappers or preferred-workflow gates.

**Scope:**

Update `spec-drafting` and only the related `defining-work` or `executing-work`
wording that currently imposes an obsolete handoff. Update CoS and
`orca-orchestration` guidance so that:

- OpenSpec is used when the target project adopts it and the change benefits
  from it; non-adopting projects retain the existing route.
- OpenSpec `tasks.md` remains local to the change and is never mirrored into
  General OS state.
- Within already authorized scope, the native working agent may choose Orca
  when independent orchestration materially improves the assignment.
- Existing policy, worktree, native-guidance, required-boundary, and
  unavailable-runtime safeguards remain intact.

Update checked-in packaged counterparts directly in the same change. Do not
assume a missing synchronization command or create one for this work.

**Dependencies:**

Task A.

**Acceptance:**

- OpenSpec-enabled substantive changes use native OpenSpec artifacts without
  duplicate general-os specifications or task ledgers.
- Projects without OpenSpec and small/reversible changes retain a safe native
  specification path.
- Ordinary authorized work can choose Orca without first creating a new
  high-level General OS task.
- Unauthorized or out-of-scope Orca use remains rejected or follows the
  existing authority path.
- Optional Orca outage may fall back to Codex; unavailable mandatory
  independence remains a concrete blocker.

**Verification:**

- Documentation-contract tests establish the written ownership and routing
  contract only.
- Existing policy, Orca observer, launch, state, and Git tests establish that
  current executable safeguards remain intact.
- A native Orca integration exercise is separate evidence for actual dispatch,
  authorization, and worktree behavior; do not simulate it with new mock
  orchestration infrastructure.
- Confirm equality for every changed maintained/package pair.

**Stop / escalation conditions:**

Stop if direct Orca selection would bypass a configured deny ceiling, required
worktree registration, native guidance load, explicit authority, or a hard
independence boundary.

## Task C — Verification and packaging

**Objective:**

Prove the local contract changes without claiming evidence that documentation
or unchanged executable code cannot establish.

**Scope:**

Update only the existing documentation, deployment, Orca, acceptance, state,
and Git tests required by the changed contract. Keep `acceptance.py` unchanged
unless a demonstrated failing requirement proves a minimal code change is
necessary.

Use separate evidence classes:

| Evidence | Establishes |
| --- | --- |
| Documentation-contract tests | Ownership and routing text is consistent |
| Existing policy and Orca unit tests | Current configuration, observer, launch, and safeguard behavior remains intact |
| Acceptance, state, and Git tests | Existing durable PASS/FAIL/BLOCKED and Git-bound contracts remain intact |
| Native Orca integration exercise | Actual supported dispatch, authority, and worktree behavior |
| Optional product pilot | End-to-end OpenSpec-to-Codex usability |

**Dependencies:**

Tasks A and B.

**Acceptance:**

1. Ordinary authorized repository work proceeds without creating General OS
   coordination state or invoking CoS.
2. General OS remains responsible for high-level decisions, material
   constraints, and exceptional coordination.
3. OpenSpec-enabled projects use native OpenSpec artifacts without duplicating
   specifications or implementation tasks.
4. Codex retains native planning, execution, and subagent ownership.
5. Authorized native work may use Orca when independent orchestration provides
   material benefit without requiring a newly created General OS task.
6. Existing Orca authority, worktree, and required-boundary safeguards remain
   intact.
7. Repository verification remains Git- and test-grounded. Strategic or
   external findings use source-specific evidence without claiming unsupported
   durable PASS transitions.
8. Active guidance and checked-in packaged counterparts are consistent.
9. Applicable regression tests pass, and no new registry, adapter, scheduler,
   task ledger, or state schema is added.
10. An external product pilot is optional, separately authorized, and does not
    block completion of the local general-os changes.

**Verification:**

- Run focused documentation, deployment, Orca, acceptance, state, and Git
  checks after implementation.
- Run the full test suite after focused checks pass.
- Run `git diff --check`, inspect current Git status, and verify exact equality
  for changed maintained/package pairs.
- Do not claim live Orca dispatch or end-to-end OpenSpec usability without the
  corresponding native integration exercise or pilot evidence.

**Stop / escalation conditions:**

Stop on package-copy drift, a new unowned durable field, a failed ownership
contract, a changed acceptance transition, or a full-suite regression that
cannot be shown unrelated.

## Optional pilot — separately authorized

**Objective:**

Validate one real OpenSpec-to-Codex change after the local contract is complete.

**Scope:**

Use one explicitly named product repository and bounded change. Read its native
OpenSpec configuration, maintained specs, active change, current Git, design
references when applicable, and project tests. Do not add pilot artifacts to
general-os or copy project tasks into `state/coordination.json`.

**Dependencies:**

Local Tasks A–C may complete without this pilot. The pilot starts only after a
target project and Git authority are explicitly authorized.

**Acceptance:**

- The product change uses native OpenSpec artifacts and reaches project-native
  verification without a duplicate General OS checklist or specification.
- Direct Codex execution remains available for ordinary work.
- Orca is used only when its independent value and authorization are present.
- Pilot friction is recorded as a follow-up decision, not silently encoded as a
  new registry, adapter, or coordination mechanism.

**Verification:**

Preserve the pilot project’s OpenSpec and Git evidence as the authoritative
proof. Do not treat the absence of a pilot as a local implementation failure.

**Stop / escalation conditions:**

Stop if no authorized pilot project is available, the target project’s authority
boundary conflicts with this plan, or a required independent boundary is
unavailable.

## Final verification

- Current Git contains only intended local contract, skill, packaged-copy, and
  regression-test changes; unrelated worktree changes remain untouched.
- Documentation and skills consistently state that General OS is conditional
  for ordinary work and does not mirror OpenSpec or native runtime state.
- OpenSpec fallback, Orca authorization/degradation, source-specific
  verification, and General OS acceptance boundaries each have appropriate
  evidence.
- Maintained and checked-in packaged guidance pairs are equal where applicable.
- Focused tests and the full test suite pass against the final worktree, or any
  unrelated pre-existing failure is recorded with evidence.
- No new registry, adapter, scheduler, watcher, worker ledger, synchronized
  project copy, or state schema is added.
- The optional pilot is reported separately and is not required for local
  acceptance.

## Open questions / unresolved decisions

- Which authorized product repository and bounded change will serve as the
  optional pilot? This does not block local Tasks A–C.
- Does any real pilot require external-evidence acceptance code, or are
  source-specific evidence and project-owned records sufficient? Default:
  defer code changes until demonstrated need.
- Which canonical source and sync command govern any future generated
  `AGENTS.md` wording change? Resolve before editing that generated surface.
