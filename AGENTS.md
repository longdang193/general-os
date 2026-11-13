# general-os Repository Guidance

`general-os` is the durable semantic coordination layer above native agent
runtimes. It owns durable intent, task boundaries, dependencies, exceptional
authority constraints, acceptance criteria, and non-derivable decisions.

## Fact Ownership

- Git owns repository state, branches, revisions, worktrees, commits, and
  recovery facts.
- Codex is the default execution harness and owns Goal Mode, `update_plan`,
  context, approvals, tools, and native subagents.
- Native subagents remain subordinate to their parent Codex assignment and do
  not become peer project coordinators.
- Orca owns independently managed worker lifecycle when CoS selects an
  independent boundary.
- CoS reads durable state plus current Git and native runtime observations,
  then coordinates assignment, continuation, escalation, and acceptance.

## Durable State

Store only facts that cannot be reconstructed cheaply and reliably. Do not
persist runtime IDs, heartbeats, temporary progress, native plans, worker
registries, or mirrored lifecycle state. Runtime completion is evidence, not
acceptance.

Use the native Orca skill before any Orca mutation. Do not recreate Orca worker
lifecycle or Codex execution loops in Python. Python adapters may provide
headless facts and compatibility seams, but they are not a second coordination
authority.

## Agent Memory

Use memory only for verified, reusable project facts, workflows, invariants,
or recurring failures. Never store secrets, credentials, private governance,
personal data, transient progress, runtime IDs, or facts already recoverable
from source, tests, Git, or current runtime state. Memory informs work but does
not override current source, tests, repository guidance, or user constraints.

## Command Safety

Prefer read-only inspection before mutation and use native repository tools when
available. Before recursive delete or move, resolve and verify the absolute
target remains inside the intended workspace or explicitly named directory.
When using a shell for destructive mutation, resolve and validate the target in
the same command or transaction immediately before mutation; never pass an
unverified computed path to destructive commands. Do not expose credentials in commands,
logs, patches, or generated artifacts.

## Execution And Recovery

Prefer the current Codex runtime. Let Codex use native subagents when useful
and allowed. Use Orca only when independent ownership is required or
materially useful. `requires_independent_boundary` is a hard requirement, not
the complete Orca selection algorithm.

Recover from durable `general-os` state plus current Git. Do not reconstruct
lost runtime sessions unless a concrete operational reason makes that safer
than starting fresh.

Block only for material authority, dependency, Git, or external-state risks.
Missing optional runtime evidence lowers confidence; it does not by itself
stop ordinary work. Acceptance requires fresh verification against current
Git. Failed or stale evidence remains retryable; `BLOCKED` means progress
cannot safely continue.
