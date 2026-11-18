---
name: chief-of-staff
description: Use when a durable general-os goal needs dependency-aware work selection, continuation, escalation, or acceptance.
---

# Chief Of Staff

## Overview

The native CoS skill is the canonical coordination intelligence for
`general-os` when durable coordination is selected. It decides what should
happen next from durable intent, current Git, and direct runtime observations;
ordinary authorized work may bypass it. It does not become an agent loop or a
second runtime scheduler.

## Ownership

- `general-os` owns durable goals, task objectives, dependencies, exceptional
  authority, acceptance criteria, and durable decisions.
- Git owns repository and recovery facts.
- Codex owns its native execution loop, Goal Mode, tools, context, approvals,
  and subordinate native subagents.
- Orca owns internal runtime orchestration and execution topology after an
  authorized native controller selects that boundary and the
  `orca-orchestration` skill is loaded.
- `agents/*.toml` is the sole profile registry. Profile selection is semantic;
  explicit facts may be projected one way to a selected runtime and absent
  facts inherit native defaults.

## Decision Flow

1. Read `state/coordination.json` and inspect current Git directly.
2. Determine unfinished dependency-ready semantic work and choose the smallest
   useful assignment boundary. An empty task graph is a valid goal-only intent
   assignment with no durable completion record; use a task graph when
   acceptance must be persisted for a material high-level commitment that
   cannot be reconstructed from native evidence.
3. Resolve effective runtime policy, including `orca_enabled`, before handing
   off any explicit independence constraint. A disabled Orca capability keeps
   ordinary work on Codex and blocks only work whose durable contract requires
   independence.
4. Resolve the semantic profile without translating missing metadata into
   guessed runtime model or effort settings. Treat explicit harness, model,
   and effort values as optional preferences only where the selected runtime
   supports them; they do not prescribe Orca topology or replace native
   runtime decisions.
5. Confirm only the material outcome, authority, and independence constraints
   that must survive runtime loss. The active native controller chooses Codex
   direct, native subagents, or Orca within that authorized scope and owns the
   execution topology.
6. If independent ownership is required or materially useful, make that
   constraint explicit and allow the active native controller to select Orca
   when `orca_enabled` permits it. Predefined use cases are examples, not
   restrictions. `requires_independent_boundary: true` is a hard requirement,
   not the whole Orca-selection algorithm; `false` does not prohibit selecting
   Orca when its native orchestration offers material benefit.
7. If the required independent boundary is unavailable, return a real
   blocker. Do not mutate permission because runtime health changed.
8. Reconcile repository-bound runtime evidence with current Git and fresh
   verification before accepting durable task state. For an external-only
   commitment, use the designated project decision record and fresh
   source-specific evidence instead; do not invent a Git requirement when no
   repository state is in scope.

## Acceptance

- `PASS` means required evidence is current and the durable task may become
  `completed`.
- `FAIL` means continue or reverify; stale, incomplete, failed, and unknown
  evidence is not a project blocker.
- `BLOCKED` means a material Git, authority, dependency, credential, user-
  decision, or required-runtime boundary prevents safe progress.

Runtime completion is evidence, not acceptance. CoS decides acceptance after
verification; general-os persists the resulting durable task state.

Repository-bound `PASS` requires current Git-bound evidence. External-only
`PASS` requires a supported project-specific acceptance contract identifying the
designated decision record and fresh source-specific evidence; it must not be
represented as repository acceptance without that contract.

## Recovery

When a runtime is lost, read durable state and current Git. If a completed task
is needed for continuation, acceptance, or publication, run
`python -m general_os state revalidate --state state/coordination.json [--task-id TASK_ID]`
as a targeted check. It reuses task-contract and dependency revalidation only;
legacy completed tasks without current acceptance identities load as pending and
need fresh verification before completion. Determine unfinished work and start
a fresh native assignment. Do not reconstruct runtime sessions or persist
runtime IDs, heartbeats, progress, or worker registries.

## Common Mistakes

- Reimplementing Codex Goal Mode or native subagent scheduling in CoS.
- Treating a runtime observation as the canonical durable decision.
- Treating stale test evidence as a durable blocker.
- Copying Codex or Orca runtime state into `general-os`.
