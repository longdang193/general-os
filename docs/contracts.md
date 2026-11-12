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

`BLOCKED` transitions require a durable category of `authority`, `dependency`,
`git`, or `external`, plus a non-empty reason. Retryable `FAIL` clears that
context when it returns a blocked task to `pending`.

Runtime completion never changes durable acceptance by itself. Repeated
successful transitions are idempotent.

Only the in-process verifier handoff may produce a passing verification result.
The CLI accepts retryable `FAIL` and material `BLOCKED` transitions, but it
cannot manufacture `PASS` from status, check names, revision, or snapshot
arguments. Reuse of evidence is rejected across tasks or snapshot identities;
repeating the same verified task/snapshot transition remains idempotent.

## Verification evidence

`GitSnapshot.identity` binds canonical repository/worktree provenance, `HEAD`,
branch, tracked diff, status, and untracked file content. Untracked files are
hashed in bounded chunks; symlink targets and unreadable paths have explicit
diagnostics. A repository-bound `PASS` must carry the same identity. A task
with `requires_independent_boundary` must also carry ephemeral typed boundary
evidence containing the task ID, supported `orca` boundary kind, matching
snapshot identity, and non-empty evidence. These values are not persisted as
worker lifecycle state, and the CLI cannot forge them from free-form input.

Completed tasks may retain their accepted snapshot identity as durable
acceptance evidence. Recovery revalidates it against current Git; missing or
mismatched evidence makes the task and any completed dependents pending until
fresh acceptance is obtained.

Completed tasks must have completed dependencies. A retryable `FAIL` leaves an
active task unchanged and returns a blocked task to `pending`; `BLOCKED` is
reserved for a current material blocker.

State version `1` is the only supported durable schema. Saves are compare-and-
write operations guarded by an interprocess lock and atomic replacement.

Fresh in-memory state may create a missing file, but may not overwrite an
existing file without loaded-state provenance. Durable `remote_side_effects =
"allow"` exceptions require non-empty scope, provenance, and a timezone-aware
ISO-8601 expiry. Resolution requires an exact requested scope.
Expired-but-well-formed exceptions remain loadable but fall back to the safer
local policy; malformed exceptions fail closed. A configured local `deny`
ceiling remains absolute.

The configured local `remote_side_effects = "deny"` policy cannot be widened by
durable state. Missing profile directories, missing requested profiles, unknown
profile fields, invalid ranks, and invalid runtime text fail closed. Orca
status observation defaults to a finite 30-second timeout.
