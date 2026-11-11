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

## Dispatch

An empty task list is a valid goal-only assignment. Its headless decision is
Codex with `task_id = null`, and the global goal is the prompt. When a task has
an objective, that objective is the prompt; the global goal is not copied into
the task or used as a second task assignment. A required independent boundary
cannot silently fall back to Codex when Orca is unavailable.

## Acceptance

Acceptance uses the current task, current Git snapshot, and fresh verification:

- `PASS` completes the task;
- `FAIL` leaves the task unfinished so the work can continue or be reverified;
- `BLOCKED` persists only a material Git, authority, dependency, credential,
  user-decision, or required-runtime-boundary blocker.

Runtime completion never changes durable acceptance by itself. Repeated
successful transitions are idempotent.
