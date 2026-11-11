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

The Python CoS and dispatch modules are factual/headless compatibility helpers.
They do not become a second interactive scheduler or a second owner of task
state.
