# Architecture

`general-os` is a thin semantic layer above Git, native Codex, and optional
Orca. Its durable source is `state/coordination.json`, which stores goal,
optional tasks, dependencies, one task state, acceptance criteria, optional
profile selection, and material exceptions.

Git owns repository state and recovery facts. Codex owns its own loop, native
Goal behavior, context, tools, and native subagents. Orca owns independent
worker execution when explicitly configured. CoS reads current facts and
chooses `Codex` or `Orca`; it does not schedule native Codex children.
