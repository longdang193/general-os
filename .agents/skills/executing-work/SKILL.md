---
name: executing-work
description: Use when a general-os task is ready for native Codex execution, bounded native delegation, verification, or optional independent Orca handoff.
---

# Executing Work

## Overview

Execute the assigned objective in the native Codex runtime. `general-os`
provides semantic context and acceptance boundaries when a coordinated
assignment exists; ordinary authorized work may execute directly. It does not
recreate the Codex agent loop.

## Normal Codex Path

1. Read the assigned goal or task objective, dependencies, acceptance, and
   exceptional authority.
2. For repository changes, inspect current Git before changing files; for
   external-only work, inspect the authoritative project or service source
   instead.
3. Use native Codex Goal Mode, `update_plan`, context, approvals, tools, and
   repository instructions.
4. Keep the assignment bounded by its objective and acceptance criteria.
5. Run focused verification, inspect the resulting Git state for repository
   changes, and return evidence to the owning native assignment or project
   workflow. Return it to CoS only when the work belongs to a durable General
   OS commitment.

The current Codex runtime is the normal interactive execution path. General-os
does not maintain a second Python interactive runtime; compatibility proof must
not be presented as native Codex execution evidence.
Use the native mechanisms opportunistically; the assignment does not prescribe
Goal Mode versus direct work, plan shape, or native subagent count.

For an OpenSpec-enabled project, execute against the project's native change
artifacts and reconcile its maintained specs through the native project
workflow. The controlling Codex agent owns the native OpenSpec `apply` path for
the active change; bounded Codex subagents may implement assigned code but must
not independently run the full apply workflow or edit shared change checklists
concurrently. Use the project's native `openspec-update-change` workflow before
continuing when requirements or design need a material change. Native
OpenSpec checklist completion is task evidence, not implementation verification
or durable General OS acceptance. Do not create a duplicate general-os
specification or task ledger.

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
- A material repository Git, authority, dependency, credential, user-decision, or
  required-runtime failure is reported as `BLOCKED`.
- Repository-bound runtime loss is recovered by rereading durable state and Git
  and starting a fresh assignment. For OpenSpec-enabled work, resume from the
  existing active change artifacts and pending checklist entries; do not
  recreate tasks already represented there. External-only work is recovered
  from its owning project record and authoritative source. Runtime history is
  not the recovery source of truth.

## Common Mistakes

- Rebuilding Codex Goal Mode or `update_plan` as a general-os ledger.
- Treating a native child as a peer coordinator.
- Persisting thread IDs, progress, or temporary plans.
- Assuming runtime completion proves repository-bound acceptance without fresh
  Git verification.
