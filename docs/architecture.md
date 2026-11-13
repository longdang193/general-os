# Architecture

`general-os` is a thin semantic coordination and governance layer above Git,
native Codex, and optional Orca. It is not an agent runtime and does not
reimplement Codex turns, Goal Mode, context, tools, approvals, or native
subagent scheduling.

## Fact ownership

`general-os` owns the durable project semantics in `state/coordination.json`:
goals, meaningful task objectives, dependencies, durable task state, acceptance
criteria, and material exceptions. Project-level CoS owns coordination
judgment: readiness, profile selection, execution-boundary choice, and
acceptance decisions. Git owns repository and recovery facts. Codex owns its
native execution loop, Goal Mode, context, tools, approvals, and subordinate
native subagents. Orca owns internal orchestration and execution topology after
CoS selects that boundary.

`agents/*.toml` is the only profile registry. A profile name is semantic
selection, not a guessed model or effort setting. General-os may project
explicit profile facts one way to a selected native runtime; omitted facts
inherit that runtime's defaults. There is no second Orca profile registry.
The read-only `general-os profile resolve` command exposes only the explicit
`harness`, `model`, `effort`, and `instructions` facts; rank, name, and provider
never synthesize runtime settings.
The Orca execution boundary is harness-neutral. Explicit general-os profile
facts provide workstream-level context; native Orca owns internal worker
specialization and topology without changing durable state.

Do not mirror runtime IDs, progress, heartbeats, worker registries, or
temporary plans into general-os. If a fact can be read reliably from Git,
Codex, or Orca at the point of use, derive it instead of persisting a copy.

## Authority split

| Decision or fact | Owner |
| --- | --- |
| Durable goals, semantic task boundaries, dependencies, profiles, constraints, and acceptance criteria | general-os |
| Readiness, profile resolution, execution-boundary selection, and acceptance decisions | project-level CoS |
| Direct execution, native planning, and subordinate Codex delegation | Codex |
| Orca internal orchestration and execution topology | native Orca coordinator/coordinating agent provided by the installed version |
| Runtime decomposition, workers, internal dependencies, retries, questions, supervision, fan-in, and cleanup | selected native runtime |
| Repository state, worktrees, commits, diffs, and recovery evidence | Git |
| Durable completion after fresh verification | project-level CoS over general-os state |

The durable invariant is that CoS chooses the boundary and the selected native
runtime chooses execution topology. General-os must not become a second Orca
coordinator, scheduler, worker registry, runtime ledger, or result aggregator.

## Orca workstream boundary

When CoS selects Orca, it hands over one semantic workstream containing the
objective, task identity, relevant context and constraints, acceptance/evidence
requirements, explicit resolved profile facts, and the relevant repository or
work boundary. It does not prescribe worker count or roles, runtime IDs,
internal DAGs, polling, heartbeats, retry counters, nested helper identities,
or temporary runtime plans.

The native Orca coordinator owns internal decomposition, fan-out, supervision,
retries, bounded worker questions, nested helpers, fan-in, and cleanup. It
returns a semantic outcome/evidence bundle for the delegated assignment. That
bundle may represent success, partial progress, failure, or a material blocker;
it is not durable general-os acceptance. Project-level CoS inspects current
Git, runs or evaluates fresh verification, and decides `PASS`, `FAIL`, or
`BLOCKED` for the durable task.

General-os does not silently merge runtime worktrees, publish, or push. Git
integration and any later repository disposition remain explicit operations
outside the native runtime outcome.

Runtime loss is recovered from durable general-os semantics and current Git.
Useful independent outcomes may be accepted separately, while remaining work
is derived again and a fresh native runtime is started. The previous Orca
episode is not reconstructed.

## Shallow routing

The native CoS skill reads durable state and current Git, determines
dependency-ready semantic work, resolves the semantic profile, and chooses the
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
and read-only health observation; internal orchestration and worker lifecycle
remain native Orca responsibilities.

Durable state is schema version `1`. Legacy unversioned state is read as version
`1` and normalized with the version on its next save; unsupported future
versions fail closed.
Loaded state carries an in-memory source digest, and saves compare that digest
under an interprocess lock before atomic replacement.

Acceptance uses the current Git snapshot identity and records that identity as
historical evidence for the accepted result. Required independent work also
needs typed ephemeral boundary evidence tied to that identity; a runtime
completion report alone is not acceptance. Later Git changes do not by
themselves erase completed task results, while fresh current verification is
still required before new acceptance or publication. Profiles fail closed when
the registry or requested default is missing, and local `deny` is a hard ceiling
for durable policy exceptions.

Execution-level failures stay inside the selected runtime when they can be
resolved there. Only material authority, dependency, user, credential, Git,
required-boundary, or acceptance blockers need to cross back to CoS. This keeps
runtime chatter and internal fan-in out of the project coordination layer.

## Central deployment ownership

`general-os deploy` installs complete runtime-clean skill directories and
shared docs under `~/.agents/general-os/`. Its `managed.json` lock owns only
central installation provenance and managed-file digests. Canonical repository
skills remain the source of truth; staged copies rewrite shared-doc references
to the installed central docs tree.

Project adoption is seed-only. `repo_config/general-os.lock.json` records the
source revision and paths that were seeded, but it does not own project-file
drift, existing `AGENTS.md`, profiles, runtime policy, or coordination state.
Codex activation is shared skill discovery, not a generated `~/.codex` tree or
runtime registry. Existing project guidance is preserved.
