# Architecture

`general-os` is a thin semantic coordination and governance layer above Git,
native Codex, and optional Orca. It is not an agent runtime and does not
reimplement Codex turns, Goal Mode, context, tools, approvals, or native
subagent scheduling.

## Fact ownership

`state/coordination.json` is the durable source for goal, optional task
objectives, dependencies, durable task state, acceptance criteria, and material
exceptions. Git owns repository and recovery facts. Codex owns its native
execution loop, Goal Mode, context, tools, approvals, and subordinate native
subagents. Orca owns independently managed worker lifecycle after CoS selects
that boundary.

`agents/*.toml` is the only profile registry. A profile name is semantic
selection, not a guessed model or effort setting. General-os may project
explicit profile facts one way to a selected native runtime; omitted facts
inherit that runtime's defaults. There is no second Orca profile registry.
The read-only `general-os profile resolve` command exposes only the explicit
`harness`, `model`, `effort`, and `instructions` facts; rank, name, and provider
never synthesize runtime settings.
The selected Orca worker is harness-neutral: its resolved runtime may be Codex,
Claude, or another explicitly supported harness without changing durable state.

Do not mirror runtime IDs, progress, heartbeats, worker registries, or
temporary plans into general-os. If a fact can be read reliably from Git,
Codex, or Orca at the point of use, derive it instead of persisting a copy.

## Shallow routing

The native CoS skill reads durable state and current Git, selects the first
dependency-ready assignment, resolves the semantic profile, and chooses the
smallest safe execution boundary:

1. Codex handles ordinary work directly.
2. Codex may use native subagents when that helps its bounded assignment; those
   children remain subordinate and do not become peer project coordinators.
3. Orca is selected when independent ownership is required or materially
   useful, and only when the configured Orca boundary is available.
4. A real Git, authority, dependency, or required-boundary failure blocks;
   missing optional runtime bookkeeping does not.

The current Codex runtime is the normal interactive execution path. General-os
does not maintain a Python Codex/CoS/dispatch runtime or a second interactive
scheduler. Its Orca surface is limited to optional native orchestration guidance
and read-only health observation; worker lifecycle remains native Orca.
