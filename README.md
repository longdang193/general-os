# general-os

`general-os` is a small durable semantic coordination layer above Git, native
Codex execution, and optional Orca orchestration.

It decides and remembers durable intent. Codex reasons and executes. Native
Codex subagents may decompose a bounded assignment while remaining subordinate
to that assignment. Orca is used only when work needs an independently managed
workstream or that boundary is materially useful. Git proves repository state
and provides recovery truth.

The durable coordination object is `state/coordination.json`. It stores the
goal, optional task objectives and dependencies, acceptance criteria, and only
material exceptions. Current Git, Codex, and Orca runtime facts are observed
directly at the point of use; runtime IDs, progress, heartbeats, and lifecycle
mirrors are not copied into durable state.

Acceptance is separate from runtime completion: fresh evidence yields `PASS`,
retryable or incomplete evidence yields `FAIL`, and only a material safety,
authority, dependency, Git, or required-runtime boundary yields `BLOCKED`.

Profiles are named semantic choices from `agents/*.toml`, the sole profile
registry. The supplied profiles explicitly own the configured `combo-*` model
and effort values; projection passes those facts one way to the selected
runtime. Orca is optional and harness-neutral, while ordinary work remains in
the current Codex runtime. Inspect the explicit projection with `python -m
general_os profile resolve --name high --directory agents`; the command is
read-only and does not infer runtime model or effort values.

The predecessor repository is a read-only migration reference, not a runtime
or schema dependency. It remains unmodified.

## Maintained SSOT

Reusable skills live under `.agents/skills/`; active shared rules live under
`docs/rules/`; and the source-pinned migration manifest is
`docs/migration/project-os-starter.md`. The migration accounts for all 33
predecessor skills and 11 predecessor rules without importing generated adapter
trees or a second orchestration authority.

Before acceptance, run `pytest -q`,
`python -m general_os state validate state/coordination.json`, and
`pytest -q tests/test_documentation_contracts.py` when documentation or
governance contracts changed.
