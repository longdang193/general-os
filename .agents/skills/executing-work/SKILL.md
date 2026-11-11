---
name: executing-work
description: Use when a general-os task is ready for native Codex execution, bounded native delegation, verification, or optional independent Orca handoff.
required_reads: []
distribution_tier: starter_kit
---

# Executing Work

## Overview

Execute the assigned objective in the native Codex runtime. `general-os`
provides semantic context and acceptance boundaries; it does not recreate the
Codex agent loop.

## Normal Codex Path

1. Read the assigned goal or task objective, dependencies, acceptance, and
   exceptional authority.
2. Inspect current Git before changing files.
3. Use native Codex Goal Mode, `update_plan`, context, approvals, tools, and
   repository instructions.
4. Keep the assignment bounded by its objective and acceptance criteria.
5. Run focused verification, inspect the resulting Git state, and return
   evidence to CoS.

The current Codex runtime is the normal interactive execution path. The
repository `CodexClient` and `dispatch.py` surfaces are optional headless or
compatibility helpers; they do not define a second interactive runtime.

## Native Subagents

Use native Codex subagents only when they improve the current assignment and
the assignment permits delegation. They remain subordinate to the parent
Codex task, use a narrower responsibility, and do not create peer project
coordination, activate CoS, or create independent Orca work unless the parent
assignment explicitly permits that boundary.

## Orca Boundary

Use the `orca-orchestration` skill before any Orca mutation. Orca is for an
independently managed workstream with its own ownership, worktree, retry, or
runtime lifecycle. Do not wrap ordinary Codex work in Orca merely to make it
look durable. Do not copy Orca IDs, worker progress, or lifecycle state into
`general-os`.

## Failure And Recovery

- A failed check, stale evidence, or incomplete proof means continue or
  reverify; it is not automatically a durable blocker.
- A material Git, authority, dependency, credential, user-decision, or
  required-runtime failure is reported as `BLOCKED`.
- Runtime loss is recovered by rereading durable state and Git and starting a
  fresh assignment. Runtime history is not the recovery source of truth.

## Common Mistakes

- Rebuilding Codex Goal Mode or `update_plan` as a general-os ledger.
- Treating a native child as a peer coordinator.
- Persisting thread IDs, progress, or temporary plans.
- Assuming runtime completion proves acceptance without fresh Git verification.
