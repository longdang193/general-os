---
name: verification-before-completion
description: Use when a Codex or Orca assignment reports completion and fresh Git, acceptance, and failure evidence must determine whether a durable General OS commitment is accepted.
---

# Verification Before Completion

## Overview

Verify a durable General OS commitment against current Git and fresh evidence
before CoS changes durable task state. Runtime completion is only an
observation. Ordinary direct work uses the owning project's native verification
and does not require this skill merely to produce a General OS result.

## Procedure

For task-bound work:

1. Read the task objective and acceptance criteria from durable state.
2. Inspect current branch, revision, conflicts, changed files, and worktree
   state directly through Git.
3. Run the smallest relevant automated checks, then broader required checks.
4. Compare evidence revision with the current Git revision.
5. Report one result with the exact checks, results, revision, and remaining
   work.

For ordinary direct execution or Level 1 work without a durable acceptance
boundary, use the owning project's native verification and current Git facts.
Invoke this skill only when the approved scope explicitly requires a Git-bound
General OS evidence handoff; do not invent durable goal acceptance or write a
completion record to `state/coordination.json`.

Profile names and runtime observations are context, not acceptance evidence.
Use fresh Git and verification output; do not require optional runtime
bookkeeping when current source and tests establish the result.

Source-specific review of strategic or external findings is separate from
repository-bound durable task acceptance. Do not record an external-only review
as a durable `PASS` unless its evidence satisfies a supported acceptance
contract; the existing Git-bound acceptance path remains authoritative for
repository tasks.

## Result Contract

### `PASS`

Use only when required checks pass, evidence is current, the durable commitment
criteria are satisfied, and no material Git conflict remains. CoS may persist a
task as `completed` only for task-bound work. Native verification remains
authoritative for ordinary direct and Level 1 work.

### `FAIL`

Use when work can continue or verification can be rerun: failed tests,
stale evidence, missing proof, incomplete output, or an unknown current
verification result. Leave the durable task unfinished.

### `BLOCKED`

Use only when progress cannot safely continue because of a material Git
conflict, authority prohibition, required user decision, unavailable mandatory
dependency or credential, or a required independent runtime boundary that is
unavailable. Record the concrete reason.

## Boundaries

- Do not accept work because Codex Goal Mode or an Orca worker reports done.
- Do not require this General OS proof when the approved work is direct or
  Level 1 goal-only intent; use the owning project's native verification and
  current Git-bound evidence instead.
- Do not write runtime IDs, progress, heartbeats, or verifier state into
  `general-os` durable state.
- Do not own branch merge, publication, worktree cleanup, Orca cleanup, or
  runtime lifecycle; return evidence to CoS and the applicable Git owner.
- Do not turn optional evidence loss into a blocker when current Git and fresh
  checks can establish the result.

## Evidence Shape

Return the status, exact commands or checks, observed Git revision, important
failures, durable-state consequence, and remaining work. Preserve failed
evidence for the current controller; do not create a second ledger.

## Common Mistakes

- Reusing an old successful check after Git changed.
- Calling missing proof a permanent blocker.
- Treating a worker receipt as acceptance.
- Performing cleanup or branch disposition from the verifier.
