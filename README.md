# general-os

`general-os` is a small durable semantic coordination layer above Git, native
Codex execution, and optional Orca orchestration. It is used when durable
project decisions, dependencies, authority exceptions, or acceptance records
are needed; ordinary authorized work may start directly in the native runtime.

General-os remembers durable semantics when a project chooses that coordination
path. Project-level CoS establishes material outcome, authority, and
independence constraints for that path; the active native controller chooses the
execution mechanism and owns its topology; Git proves repository state; and
CoS accepts verified results only for commitments it owns. Native Codex
subagents may decompose a bounded assignment while remaining subordinate to
that assignment. Orca may be selected by the active native controller when
independent orchestration is materially useful or required.

The durable coordination object is `state/coordination.json` when durable
coordination is selected. It stores the goal, optional task objectives and
dependencies, acceptance criteria, and only material exceptions. Current Git,
Codex, and Orca runtime facts are observed directly at the point of use; runtime
IDs, progress, heartbeats, and lifecycle mirrors are not copied into durable
state.

For durable General OS commitments, acceptance is separate from runtime
completion: fresh evidence yields `PASS`, retryable or incomplete evidence
yields `FAIL`, and only a material safety, authority, dependency, Git, or
required-runtime boundary yields `BLOCKED`. Ordinary work uses its owning
project's native verification and Git evidence instead.

Profiles are named semantic choices from `agents/*.toml`, the sole profile
registry. The four general-purpose profiles explicitly own their configured
`combo-*` model and effort values; specialized profiles intentionally inherit
native defaults. Projection passes explicit facts one way to the selected
runtime. Orca is optional and harness-neutral, while ordinary work remains in
the current Codex runtime. Inspect the explicit projection with `python -m
general_os profile resolve --name high --directory agents`; the command is
read-only and does not infer runtime model or effort values.

The predecessor repository is a read-only migration reference, not a runtime
or schema dependency. It remains unmodified.

## Native specification and direct work

Projects that adopt OpenSpec keep change-local requirements, proposals, design
notes, changed specs, and task checklists in OpenSpec. General-os does not copy
those artifacts into `state/coordination.json` or add an OpenSpec adapter.
Projects without OpenSpec, and small or reversible changes, retain their
existing native specification route. Figma, OpenDesign, and project code remain
authoritative for their own design and implementation concerns; link those
sources instead of duplicating them.

## Concept discovery

When a persistent Concept Brief is explicitly requested, projects may use
`docs/templates/concept-brief.md`. The project owns this lightweight brief for
problem, value, concept, uncertainty, and decision
context; it is not a requirements or implementation specification. OpenSpec
owns subsequent requirements, designs, specifications, and change-local tasks,
while General OS and CoS handle exceptional durable strategic coordination
rather than routine concept-document management.

## Maintained SSOT and migration evidence

Reusable skills live under `.agents/skills/`; active shared rules live under
`docs/rules/`. The source-pinned migration manifest at
`docs/migration/project-os-starter.md` is historical cutover evidence, not a
runtime SSOT or schema dependency. It records the predecessor inventory without
importing generated adapter trees or a second orchestration authority.

When durable General OS coordination is selected, run the focused tests
affected by the change and `python -m general_os state validate state/coordination.json`
before acceptance. Ordinary direct work and native
OpenSpec changes use their owning project verification instead. For shared/core
or package-wide changes, and before release, run `pytest -q`. During
documentation or governance changes, use
`pytest -q tests/test_documentation_contracts.py` as the focused check. Run the
historical migration audit explicitly with
`pytest -q tests/migration_audit.py` when migration or cutover evidence is
needed.

## Central deployment

Install the reusable runtime surface with `general-os deploy --adapter codex`.
This is central-only by default. Use `--repo .` when explicitly opting into
one-shot project adoption; it seeds only absent neutral project guidance,
profiles, and policy, never `state/coordination.json`. Use `--dry-run` to plan
without writes, `--check` to inspect central drift, and `--prune` only when
unchanged centrally owned files should be removed. See `docs/deployment.md`
for the ownership, rollback, and migration contract.
