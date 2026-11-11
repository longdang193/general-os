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

Project only the semantic assignment and resolved profile context:

- task objective and relevant context
- acceptance criteria when useful
- resolved general-os profile name as context

Resolve profile names from the sole `agents/*.toml` registry. Do not create an
Orca-specific profile registry.

Do not translate missing profile facts or profile names into guessed native
model or effort settings. Explicit profile facts may be projected one way;
otherwise the selected worker inherits native defaults. Orca is harness-neutral:
the resolved worker may use Codex, Claude, or another explicitly supported
harness.

For the native CLI handoff, use the resolved projection through
`build_orca_launch(project_profile(profile))`. This maps only explicit
`harness`, `model`, `effort`, and `instructions` values to Orca launch flags;
it does not create a second profile registry or persist runtime configuration.

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

General-os does not provide a Python dispatch, inspection, cancellation, or
worker registry seam. The native Orca skill owns real worker inspection and
lifecycle; general-os may retain only read-only CLI health observation.
