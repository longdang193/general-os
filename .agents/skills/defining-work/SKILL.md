---
name: defining-work
description: Use when a general-os request needs a durable goal, a small dependency graph, or a detailed plan before execution.
required_reads: []
distribution_tier: starter_kit
---

# Defining Work

## Overview

Choose the smallest durable representation that makes the work safe to
execute and recover. Planning depth is a semantic decision, not a requirement
to create a full project-management ledger.

## Planning Depths

### Level 1: Goal only

Use when the work is clear, bounded, and locally reversible.

```json
{
  "goal": "Fix duplicate admission",
  "tasks": []
}
```

The empty task list is valid. Native Codex owns its temporary execution plan.

### Level 2: Small task graph

Use when there are multiple meaningful dependencies or acceptance boundaries.
Persist only task facts that survive runtime loss:

```json
{
  "goal": "Ship the admission change",
  "tasks": [
    {
      "id": "implementation",
      "objective": "Implement the bounded change",
      "state": "pending",
      "depends_on": [],
      "acceptance": ["focused tests pass"]
    }
  ]
}
```

### Level 3: Detailed plan

Use only when ordering, migration, shared ownership, or verification risk
needs durable explanation. Use the repository detailed-plan template. Keep
executor sessions, runtime IDs, temporary checklists, and progress out of it.

## Rules

- Define a bounded objective for every durable task when the graph is used.
- Keep dependencies explicit and acyclic.
- Keep acceptance observable and tied to fresh evidence.
- Persist exceptional authority constraints only when they materially change
  what may happen.
- Select profiles by name from `agents/*.toml`; do not persist runtime-specific
  model, effort, worker, or lifecycle mirrors.
- Do not add an execution strategy, worker registry, runtime grant, heartbeat,
  or mirror of native runtime state.
- Prefer defaults and omission over repeated configuration.

## Escalation

Start at Level 1. Move to Level 2 only when dependency ordering or separate
acceptance matters. Move to Level 3 only when a detailed durable handoff or
complex verification path is necessary.

## Common Mistakes

- Turning every goal into a multi-task plan.
- Copying Codex or Orca progress into durable state.
- Using a task ID without a meaningful objective.
- Treating a temporary Codex `update_plan` as project truth.
