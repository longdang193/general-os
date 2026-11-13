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

Project-level CoS chooses this boundary for one independently owned semantic
workstream. General-os owns the durable semantic assignment and passes the
native Orca coordinator/coordinating agent provided by the installed version:

- task objective and semantic identity;
- relevant context and material constraints;
- acceptance and evidence requirements when useful;
- resolved general-os profile name and explicit profile facts; and
- the relevant repository or work boundary.

Resolve profile names from the sole `agents/*.toml` registry. Do not create an
Orca-specific profile registry. Do not prescribe worker count or roles, runtime
IDs, internal DAGs, polling, heartbeats, retry counters, nested helper
identities, or temporary runtime plans.

Do not translate missing profile facts or profile names into guessed native
model or effort settings. Explicit profile facts may be projected one way;
otherwise the native runtime inherits its native defaults. Orca is harness-neutral and
the installed version decides its internal orchestration and execution
topology, including decomposition, workers, supervision, retries, questions,
nested helpers, synthesis, release, and cleanup.

`build_orca_launch(project_profile(profile), assignment)` remains a low-level
leaf/compatibility projection for simple native CLI launch paths. It maps only
explicit `harness`, `model`, `effort`, and `instructions` values plus the
ephemeral assignment to Orca launch flags; it does not define the conceptual
multi-agent boundary, create a second profile registry, or persist runtime
configuration.

The native coordinator returns one semantic outcome/evidence bundle for the
delegated assignment. That bundle may report success, partial progress,
failure, or a material blocker. Never persist or mirror Run IDs, Task IDs,
Dispatch IDs, worker IDs, heartbeats, progress, or other Orca runtime state in
`general-os` durable state. Project-level CoS must inspect current Git, evaluate
fresh evidence, and decide durable task acceptance; Orca completion cannot
complete a general-os task by itself.

## Degradation

If Orca is unavailable, continue with Codex when independent ownership is not
required. If the durable task contract requires an independent boundary, report
the current Orca observation as a blocker. Do not mutate `orca_enabled` in
response to transient runtime health.

General-os does not provide a Python dispatch, inspection, cancellation, or
 worker registry seam. The native Orca skill owns real worker inspection and
 lifecycle; general-os may retain only read-only CLI health observation.
