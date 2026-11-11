# Contracts

## Durable state

`state/coordination.json` contains only facts needed after runtime loss:

- the goal;
- optional task IDs, bounded objectives, dependencies, and task state;
- acceptance criteria;
- optional semantic profile selection; and
- exceptional authority or boundary decisions that materially change safe
  execution.

The task state is one of `pending`, `active`, `blocked`, or `completed`.
Dispatch requests, runtime identities, Goal Mode status, native subagent
counts, Orca lifecycle, heartbeats, temporary plans, and verification output
are observations, not another durable ledger.

## Execution boundary

An empty task list is a valid goal-only assignment for the current Codex
runtime. When a task has an objective, that objective is the assignment; the
global goal is not copied into the task or used as a second task assignment.
Codex may use native subagents inside that assignment. CoS selects Orca only
when independent ownership is materially useful or required; a required
independent boundary cannot silently fall back to Codex when Orca is
unavailable.

Profiles are selected by name from `agents/*.toml`. Explicit profile facts may
be projected one way to the selected runtime, while absent facts inherit native
defaults. Profile selection does not create an Orca registry or a durable
runtime configuration mirror.

The projection shape is `{harness, model, effort, instructions}` plus the
resolved profile name. Each runtime field is either explicitly configured or
`null`; `model = "codex"` is not a valid substitute for the `codex` harness.
The supplied capability profiles explicitly configure the Claude gateway
combos `combo-low`, `combo-normal`, `combo-high`, and `combo-xhigh` with their
corresponding effort levels; these values are owned by `agents/*.toml`, not
reconstructed from rank or profile name.

The optional Orca handoff consumes that projection once and maps it to native
`orca agent launch` arguments: `harness` becomes `--agent`, explicit `model`
and `effort` become their matching flags, and `instructions` becomes the
launch prompt. Missing fields are omitted; no Orca profile registry or runtime
state is created. Orca rejects an incomplete launch when the harness is absent
or effort is supplied without an explicit model.

## Acceptance

Acceptance uses the current task, current Git snapshot, and fresh verification:

- `PASS` completes the task;
- `FAIL` leaves the task unfinished so the work can continue or be reverified;
- `BLOCKED` persists only a material Git, authority, dependency, credential,
  user-decision, or required-runtime-boundary blocker.

Runtime completion never changes durable acceptance by itself. Repeated
successful transitions are idempotent.
