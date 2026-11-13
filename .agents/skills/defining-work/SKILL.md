---
name: defining-work
description: Use when a general-os request needs a durable goal, a small dependency graph, or a detailed plan before execution.
---

# Defining Work

## Overview

Choose the smallest durable representation that makes the work safe to
execute, hand off, and recover. `general-os` owns durable coordination facts;
the selected native runtime owns temporary execution planning.

Persist a planning fact only when a fresh capable executor could not safely
reconstruct it from the goal, current Git, repository guidance, and current
environment. Do not duplicate Codex Goal Mode, `update_plan`, Claude planning,
native subagent decomposition, or other runtime-local planning mechanisms.

## Planning Depths

### Direct execution

Use when the work is local, design-clear, reversible, and does not require
durable coordination state. The native runtime owns planning and execution.

Do not create a durable plan merely because the runtime internally uses a
plan.

### Level 1: Goal only

Use when the outcome must survive runtime loss, but a capable fresh executor
can safely derive the implementation approach.

```json
{
  "goal": "Fix duplicate admission",
  "tasks": []
}
```

The empty task list is valid. Persist only the durable outcome and material
constraints or acceptance facts. The native runtime owns implementation
decomposition, exploratory work, temporary steps, tools, retries, and
delegation.

### Level 2: Small task graph

Use when work has multiple meaningful durable boundaries, dependencies, or
separate acceptance conditions. Tasks describe semantic work boundaries, not
implementation checklists. The native runtime determines how each task is
executed.

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

Use only when important coordination information cannot safely be reconstructed
by a fresh executor. Typical reasons include migration or rollout ordering,
cross-task or cross-owner dependencies, decisions whose rationale must survive
runtime loss, material scope or authority boundaries, difficult-to-reverse
changes, complex verification or recovery requirements, or points where
execution must stop rather than improvise.

Use the repository detailed-plan template. A detailed plan must still leave
local implementation planning to the selected native runtime.

Do not persist exploratory steps, anticipated tool calls, temporary
checklists, runtime IDs or sessions, native subagent assignments, progress,
file-by-file edits that can be derived safely, Codex `update_plan` state, or
Claude/native planning state.

## Planning Ownership

`general-os` should answer:

- What outcome matters?
- What work boundaries must remain stable?
- What depends on what?
- What decisions or invariants must survive runtime loss?
- What evidence proves acceptance?
- When must execution stop or escalate?

The native runtime should answer:

- Which files and symbols need inspection?
- What exact implementation sequence should be used?
- Which tools should be called?
- Whether native subagents are useful?
- How to retry or adjust locally?
- How to structure temporary execution checkpoints?

## Rules

- Define a bounded objective for every durable task when the graph is used.
- Keep dependencies explicit and acyclic.
- Keep acceptance observable and tied to fresh evidence.
- Persist only material constraints and non-derivable decisions.
- Persist exceptional authority constraints only when they materially change
  what may happen.
- Select profiles by name from `agents/*.toml`; do not persist runtime-specific
  model, effort, worker, or lifecycle mirrors.
- Do not create an execution strategy, worker registry, heartbeat, authority
  mirror, or native planning ledger.
- Prefer defaults and omission over repeated configuration.

## Escalation

Prefer direct execution → Level 1 → Level 2 → Level 3. Escalate only when the
next level preserves information that would otherwise be unsafe or expensive to
reconstruct. Do not escalate because the work merely has many implementation
steps or many changed files.

Before increasing planning depth, ask:

1. Could a fresh capable executor safely derive this from the goal and current
   repository state?
2. Would runtime loss discard an important decision?
3. Does another durable task or owner depend on this ordering?
4. Could a locally reasonable implementation violate a system invariant?
5. Is there a condition where the executor must stop instead of improvising?

## Common Mistakes

- Turning every goal into a multi-task plan.
- Treating many files or many implementation steps as justification for Level 3.
- Writing implementation recipes that duplicate native Plan/Goal mode.
- Copying Codex or Orca progress into durable state.
- Copying native planning state or subagent assignments into durable state.
- Using a task ID without a meaningful objective.
- Treating a temporary Codex `update_plan` as project truth.
