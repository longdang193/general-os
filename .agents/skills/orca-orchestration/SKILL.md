---
name: orca-orchestration
description: Use when CoS selects Orca for an independently managed top-level workstream.
---

# Orca Orchestration

Use this skill only when CoS has selected an independent execution boundary.
Ordinary work stays in the current Codex runtime, and native Codex subagents
remain subordinate to that assignment.

## Native Instructions

Before the first Orca orchestration mutation in the current agent
session/version context, load the installed guidance:

```text
orca skills get orchestration --full
```

Reuse that guidance for subsequent mutations in the same session. Reload it
only after context loss, an Orca runtime/version change, or unavailable
guidance. Use the installed guidance for all worker lifecycle, inspection,
wait, retry, messaging, release, and cleanup operations. Do not recreate those
commands in `general-os` code or this skill.

## Handoff

Project only the semantic assignment:

- task objective and relevant context
- acceptance criteria when useful
- resolved general-os profile name as context

Do not translate current profile `model`, `provider`, `rank`, or name fields
into native model or effort settings. Orca and Codex inherit their native
defaults until a separate profile slice defines explicitly runtime-native
fields.

Never persist or mirror Run IDs, Task IDs, Dispatch IDs, worker IDs,
heartbeats, progress, or other Orca runtime state in `general-os` durable
state. Return native runtime outcome and evidence to CoS instead.

Orca completion is not general-os acceptance. CoS must verify Git, required
evidence, and acceptance criteria before changing durable task state.

## Degradation

If Orca is unavailable, continue with Codex when independent ownership is not
required. If the durable task contract requires an independent boundary, report
the current Orca observation as a blocker. Do not mutate `orca_enabled` in
response to transient runtime health.

The injected Python `OrcaTransport`/`OrcaClient` lifecycle seam is a
compatibility/test seam during migration, not the canonical orchestration path.
The native Orca skill owns real worker inspection and lifecycle.
