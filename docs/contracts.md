# Contracts

## Durable state

`state/coordination.json` contains only facts needed after runtime loss:

- the goal;
- optional task IDs, bounded objectives, dependencies, and task state;
- acceptance criteria;
- optional semantic profile selection; and
- exceptional authority or boundary decisions that materially change safe
  execution.

Substantive strategic rationale belongs in an existing project-owned Markdown
decision record when it genuinely needs persistence. Keep alternatives and any
reconsideration trigger there rather than forcing them into task records.
Use this durable coordination state only when the decision also requires a
General OS assignment, acceptance boundary, or exceptional authority decision.

When OpenSpec is adopted, maintained specifications are the accepted intended
behavior and an active change is proposed behavior until reconciliation. Do not
silently treat the active change as the maintained contract or copy either
OpenSpec tasks or specifications into this state.

The task state is one of `pending`, `active`, `blocked`, or `completed`.
Dispatch requests, runtime identities, Goal Mode status, native subagent
counts, Orca lifecycle, heartbeats, temporary plans, and verification output
are observations, not another durable ledger.

## Execution boundary

An empty task list is a valid goal-only intent assignment. It has no durable
completion or acceptance record, so recovery may redispatch the goal; use a task
graph when acceptance must be persisted. When a task has an objective, that
objective is the assignment; the global goal is not copied into the task or
used as a second task assignment. Codex may use native subagents inside that
assignment. Ordinary authorized work may bypass this coordination contract and
start directly in the native runtime. Within already authorized scope, native
Orca may be selected when independent ownership is materially useful or
required; a required independent boundary cannot silently fall back to Codex
when Orca is unavailable.

When coordination is selected, `general-os` owns the durable semantic
assignment. Project-level CoS owns the coordination judgment that selects the
boundary and later decides acceptance. The selected native runtime owns
execution decomposition and execution topology inside that boundary.

Profiles are selected by name from `agents/*.toml`. Explicit profile facts may
be projected one way to the selected runtime, while absent facts inherit native
defaults. Profile selection does not create an Orca registry or a durable
runtime configuration mirror.

The projection shape is `{harness, model, effort, instructions}` plus the
resolved profile name. Missing model, harness, or effort values are `null` in
the projection; missing instructions serialize as the empty string sentinel.
`model = "codex"` is not a valid substitute for the `codex` harness. The
shipped capability profiles may carry verified Codex harness, model, and effort
preferences. These are explicit optional runtime settings where supported, not
universal routing truth; missing or unsupported settings fall back to native
behavior. Project-local profiles may provide other explicit values when a
runtime constraint is intentional. These values are owned by `agents/*.toml`,
not reconstructed from rank or profile name. The optional Orca handoff consumes
that projection once as a semantic
workstream contract containing the objective, task identity, relevant context
and constraints, acceptance/evidence requirements, explicit profile facts, and
the relevant repository or work boundary. The native Orca entrypoint provided
by the installed version decides whether and how to create internal runtime
tasks, workers, dependencies, retries, supervision, nested helpers, and
synthesis. A supervised path may return an outcome/evidence bundle; a
lightweight ownership handoff may return only a transfer acknowledgement, if
the native path reports one. Transfer or runtime completion is not durable
task acceptance. Worker count, worker roles, runtime IDs, internal DAGs,
polling, heartbeats, retry counters, and temporary plans are not general-os
contract fields.

`build_orca_launch(project_profile(profile), assignment)` remains a low-level
one-way leaf/compatibility projection for the native CLI: `harness` becomes
`--agent`, explicit `model` and `effort` become their matching flags, and the
ephemeral assignment plus explicit `instructions` become the launch prompt.
Missing fields are omitted; no Orca profile registry or runtime state is
created. A semantic profile alone is not a complete Orca launch configuration;
the low-level helper requires an explicit harness. Orca rejects an incomplete launch when the harness is absent or effort
is supplied without an explicit model. This helper does not define the
conceptual multi-agent boundary.

## Acceptance

Source-specific review of strategic or external findings is distinct from
repository-bound task acceptance. An external-only review may inform a decision,
but it must not be recorded as a successful durable task transition unless its
evidence satisfies a supported acceptance contract. The existing Git-bound
acceptance subsystem remains authoritative for repository tasks.

Acceptance uses the current task, current Git snapshot, and fresh verification:

- `PASS` completes the task;
- `FAIL` leaves the task unfinished so the work can continue or be reverified;
- `BLOCKED` persists only a material Git, authority, dependency, credential,
  user-decision, or required-runtime-boundary blocker.

`BLOCKED` transitions require a durable category of `authority`, `dependency`,
`git`, or `external`, plus a non-empty reason. Retryable `FAIL` clears that
context when it returns a blocked task to `pending`.

An Orca outcome/evidence bundle may report success, partial progress, failure,
or a material blocker. Runtime completion never changes durable acceptance by
itself. Repeated
successful transitions are idempotent.

Only the public in-process `create_verification_result` handoff may produce a
passing verification result. It binds evidence to the task ID, a deterministic
fingerprint of the acceptance-relevant task contract, and the current Git
observation. The CLI accepts retryable `FAIL` and material `BLOCKED` transitions,
but it cannot manufacture `PASS` from status, check names, revision, or
snapshot arguments. Reuse of evidence is rejected across tasks or snapshot
identities; repeating the same verified task/snapshot transition remains
idempotent.

## Verification evidence

`GitSnapshot.identity` binds canonical repository/worktree provenance, `HEAD`,
branch, status, separate staged and unstaged tracked diffs, and untracked file
content. The tracked `state/coordination.json` file is excluded from this work
identity because acceptance writes durable semantic state after verification.
Untracked files are hashed in bounded chunks; symlink targets and unreadable
paths have explicit diagnostics. A repository-bound `PASS` must carry the same
identity. A task
with `requires_independent_boundary` must also carry ephemeral typed boundary
evidence containing the task ID, supported `orca` boundary kind, matching
snapshot identity, and non-empty evidence. These values are not persisted as
worker lifecycle state, and the CLI cannot forge them from free-form input.

The result boundary is explicit: general-os may inspect the returned evidence
and current Git, but it does not silently merge runtime worktrees, publish,
push, or convert a runtime completion report into acceptance. Git and the
project-level CoS acceptance path remain authoritative.

Completed tasks retain their accepted snapshot identity and task-contract
fingerprint as durable acceptance evidence. The snapshot identity records where
the result was accepted; later commits or unrelated Git changes do not erase
that historical result. Recovery revalidates the task-contract fingerprint and
dependency closure. Current or final verification still uses a fresh Git
snapshot before relying on the result for new acceptance or publication.
Snapshot divergence is an ephemeral signal for selecting completed tasks for
fresh task-level verification; it is not itself a durable failure or a reason
to demote a task.

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
durable state. Missing requested profiles, unknown profile fields, invalid
ranks, and invalid runtime text fail closed. When no profile is explicitly
requested, a missing profile directory or `normal.toml` inherits native
runtime defaults. Orca status observation defaults to a finite 30-second
timeout.

## Deployment

The central installation under `~/.agents/` is governed by
`~/.agents/general-os/managed.json`, which stores only central managed-file
digests and source provenance. Runtime skill files live at
`~/.agents/skills/`; shared docs live at `~/.agents/general-os/docs/`.
Project adoption is represented by
`repo_config/general-os.lock.json`; it stores schema, source, source revision,
and seeded paths only. Deployment is central-only unless `--repo` explicitly
opts into one-shot adoption. Adoption never seeds `state/coordination.json`,
and an existing adoption record makes project semantics entirely inert.
Existing project semantics remain outside deployment ownership.

Deployment distributes reusable assets and performs explicit one-shot adoption;
it does not participate in project coordination or native runtime ownership.

`--dry-run` is read-only. `--check` reports drift without writing and treats
predecessor residue as a warning unless `--strict-migration` is supplied.
`--prune` removes only unchanged files still owned by the central lock.
