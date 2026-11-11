---
name: chief-of-staff
description: Use when a durable general-os goal needs dependency-aware work selection, execution-boundary choice, continuation, escalation, or acceptance.
required_reads: []
distribution_tier: starter_kit
---

# Chief Of Staff

## Overview

The native CoS skill is the canonical coordination intelligence for
`general-os`. It decides what should happen next from durable intent, current
Git, and direct runtime observations; it does not become an agent loop or a
second runtime scheduler.

## Ownership

- `general-os` owns durable goals, task objectives, dependencies, exceptional
  authority, acceptance criteria, and durable decisions.
- Git owns repository and recovery facts.
- Codex owns its native execution loop, Goal Mode, tools, context, approvals,
  and subordinate native subagents.
- Orca owns independently managed worker lifecycle after CoS selects that
  boundary and the `orca-orchestration` skill is loaded.
- `agents/*.toml` is the sole profile registry. Profile selection is semantic;
  explicit facts may be projected one way to a selected runtime and absent
  facts inherit native defaults.

## Decision Flow

1. Read `state/coordination.json` and inspect current Git directly.
2. Select the first unfinished dependency-ready task. An empty task graph is a
   valid goal-only assignment.
3. Resolve the semantic profile without translating missing metadata into
   guessed runtime model or effort settings.
4. Select the current Codex runtime by default. Let Codex decide whether native
   subagents help its bounded assignment.
5. Select Orca when independent ownership is required or materially useful.
   `requires_independent_boundary: true` is a hard requirement, not the whole
   Orca-selection algorithm.
6. If the required independent boundary is unavailable, return a real
   blocker. Do not mutate permission because runtime health changed.
7. Reconcile runtime evidence with current Git and fresh verification before
   accepting durable task state.

## Acceptance

- `PASS` means required evidence is current and the durable task may become
  `completed`.
- `FAIL` means continue or reverify; stale, incomplete, failed, and unknown
  evidence is not a project blocker.
- `BLOCKED` means a material Git, authority, dependency, credential, user-
  decision, or required-runtime boundary prevents safe progress.

Runtime completion is evidence, not acceptance. Only the durable state owner
changes task state after verification.

## Recovery

When a runtime is lost, read durable state and current Git, determine unfinished
work, and start a fresh native assignment. Do not reconstruct runtime sessions
or persist runtime IDs, heartbeats, progress, or worker registries.

## Common Mistakes

- Reimplementing Codex Goal Mode or native subagent scheduling in CoS.
- Treating a runtime observation as the canonical durable decision.
- Treating stale test evidence as a durable blocker.
- Copying Codex or Orca runtime state into `general-os`.
