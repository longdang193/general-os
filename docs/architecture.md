# Architecture

`general-os` is a thin semantic coordination and governance layer above Git,
native Codex, and optional Orca. It is used when durable coordination is
needed; ordinary authorized work may remain direct in the native runtime. It
is not an agent runtime and does not reimplement Codex turns, Goal Mode,
context, tools, approvals, or native subagent scheduling.

## Fact ownership

When durable coordination is selected for a material high-level commitment that
cannot be safely or economically reconstructed from Git, project records, or
native runtime evidence, `general-os` owns the durable project semantics in
`state/coordination.json`: goals, meaningful task objectives, dependencies,
durable task state, acceptance criteria, and material exceptions. Project-level
CoS owns coordination judgment for that path: readiness, material outcome and
authority constraints, and acceptance decisions. Git owns repository and
recovery facts. Codex owns its native execution loop, Goal Mode, context,
tools, approvals, and subordinate native subagents. Orca owns internal
orchestration and execution topology after an authorized native controller
selects that boundary.

Projects that adopt OpenSpec keep change-local requirements, proposals, design
notes, changed specs, and task checklists in OpenSpec. Those artifacts are not
copied into general-os state. Projects without OpenSpec and small or reversible
changes retain their existing native specification route.

The specification SSOT is explicit: maintained OpenSpec specifications define
accepted intended behavior when OpenSpec is adopted; an authorized active
OpenSpec change defines the implementation target for its scope while remaining
a proposal against the maintained contract until native reconciliation updates
those specifications; it does not globally replace the maintained contract.
Current code and runtime evidence describe
implementation reality; and an approved Figma, OpenDesign, or code-first design
authority defines visual design. A project-owned Markdown decision record may preserve
substantive strategic rationale, alternatives, and reconsideration triggers
when that rationale genuinely needs persistence. Use `state/coordination.json`
only when the decision also requires durable coordination or an exceptional
authority boundary. No mandatory decision template or decision database is
created. When explicitly requested, a project-owned Concept Brief may preserve
concise problem, value, concept, uncertainty, and decision discovery context;
it is not an implementation specification or a General OS task record.

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
| Durable goals, semantic task boundaries, dependencies, profiles, constraints, and acceptance criteria for material high-level commitments | general-os |
| Readiness, material authority constraints, and acceptance decisions for coordinated work | project-level CoS |
| Direct execution, native planning, execution-mechanism selection, and subordinate Codex delegation | active native controller |
| Orca internal orchestration and execution topology | native Orca coordinator/coordinating agent provided by the installed version |
| Runtime decomposition, workers, internal dependencies, retries, questions, supervision, fan-in, and cleanup | selected native runtime |
| Repository state, worktrees, commits, diffs, and recovery evidence | Git |
| Durable completion after fresh verification for coordinated work | project-level CoS over general-os state |
| Accepted intended behavior when OpenSpec is adopted | maintained OpenSpec specifications |
| Authorized scoped implementation target before OpenSpec reconciliation | active OpenSpec change |
| Implementation reality | current code and runtime evidence |
| Approved visual design | selected design authority |
| Strategic decision rationale | project-owned General OS decision context |
| Project-owned concept discovery context | project-owned Concept Brief |

The durable invariant is that coordinated work has one semantic owner and the
selected native runtime chooses execution topology. General-os must not become
a second Orca coordinator, scheduler, worker registry, runtime ledger, or
result aggregator.

## Orca workstream boundary

When an authorized native controller selects Orca, it hands over one semantic workstream
containing the
objective, task identity, relevant context and constraints, acceptance/evidence
requirements, explicit resolved profile facts, and the relevant repository or
work boundary. It does not prescribe worker count or roles, runtime IDs,
internal DAGs, polling, heartbeats, retry counters, nested helper identities,
or temporary runtime plans.

The selected native Orca path owns internal decomposition, fan-out,
supervision, retries, bounded worker questions, nested helpers, fan-in, and
cleanup when those capabilities are used. A supervised path may return a
semantic outcome/evidence bundle representing success, partial progress,
failure, or a material blocker. A lightweight ownership handoff may return
only a transfer acknowledgement, if the native path reports one; transfer is
not durable general-os acceptance. For repository-bound coordinated work,
project-level CoS inspects current Git, runs or evaluates fresh verification,
and decides `PASS`, `FAIL`, or `BLOCKED` for the durable task. External-only
strategic evidence remains in the designated project decision record and does
not produce a General OS task-state transition.

General-os does not silently merge runtime worktrees, publish, or push. Git
integration and any later repository disposition remain explicit operations
outside the native runtime outcome.

Repository-bound runtime loss is recovered from durable general-os semantics and
current Git. External-only work is recovered from its designated project
decision record and authoritative source evidence. Useful independent outcomes
may be accepted separately, while remaining work is derived again and a fresh
native runtime is started. The previous Orca episode is not reconstructed.

## Shallow routing

When durable coordination is selected, the native CoS skill reads durable state
and, for repository-bound work, current Git; it determines dependency-ready
semantic work, resolves the semantic profile, and confirms material outcome,
authority, or independence constraints. External-only work uses the designated
project decision record and authoritative source evidence instead. The active
native controller chooses the execution mechanism based on task requirements,
available capabilities, expected benefit, cost, and coordination overhead; it
also owns internal planning, delegation, execution topology, and worker
lifecycle. CoS owns acceptance requirements only for the durable commitment.
Otherwise, authorized work starts in
the native runtime directly:

1. Codex handles ordinary work directly without creating general-os state.
2. Codex may use native subagents when that helps its bounded assignment; those
   children remain subordinate and do not become peer project coordinators.
3. Native Orca is selected within authorized scope when independent ownership
   is required or materially useful, and only when the configured boundary is
   available.
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

Machine-readable General OS task acceptance uses the current Git snapshot
identity and records that identity as historical evidence for the accepted
result. Required independent work also needs typed ephemeral boundary evidence
tied to that identity; a runtime completion report alone is not acceptance.
External-only strategic evidence does not produce a General OS task `PASS` and
belongs in the designated project decision record. Later Git changes do not by
themselves erase completed task results, while fresh current verification is
still required before new repository-bound acceptance or publication.
Explicitly requested missing profiles fail clearly; implicit profile selection
may use the neutral profile and inherit native runtime defaults. Local `deny` is
a hard ceiling for durable policy exceptions.

Execution-level failures stay inside the selected runtime when they can be
resolved there. Only material authority, dependency, user, credential, Git,
required-boundary, or acceptance blockers need to cross back to CoS when a
coordinated assignment exists. This keeps
runtime chatter and internal fan-in out of the project coordination layer.

## Central deployment ownership

`general-os deploy` installs complete runtime-clean skill directories under
`~/.agents/skills/` and shared docs under `~/.agents/general-os/docs/`. Its
`managed.json` lock under `~/.agents/general-os/` owns only central
installation provenance and managed-file digests. Canonical repository skills
remain the source of truth; staged copies rewrite shared-doc references to the
installed central docs tree. Unrelated existing skill directories are
preserved.

Project adoption is seed-only. `repo_config/general-os.lock.json` records the
source revision and paths that were seeded, but it does not own project-file
drift, existing `AGENTS.md`, profiles, runtime policy, or coordination state.
Codex activation is shared skill discovery, not a generated `~/.codex` tree or
runtime registry. Existing project guidance is preserved.
