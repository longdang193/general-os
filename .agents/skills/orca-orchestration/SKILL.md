---
name: orca-orchestration
description: Use when an authorized native controller selects Orca for an independently managed top-level workstream.
---

# Orca Orchestration

Use this skill when an authorized native controller selects Orca for one
independently owned semantic workstream. Selection may be required or
opportunistic; it is not limited to a predefined task category or to a
`requires_independent_boundary` flag. Ordinary work stays in the current Codex
runtime, and native Codex subagents remain subordinate to that assignment.

Orca may be useful for investigation, independent hypothesis testing, parallel
research, debugging, implementation, reviews, synthesis, or other work where
its native orchestration materially helps. These are examples, not mandatory
workflows or a routing table; the installed native guidance chooses the worker
count, roles, dependencies, and execution topology.

## Native Instructions

Before the first Orca mutation in the current agent session/version context,
load the installed, version-matched guidance for the selected native path.
Use lightweight handoff guidance for simple independent assignments and full
orchestration guidance only when supervised coordination is needed. Reuse the
loaded guidance for subsequent mutations in the same session. Reload it only
after context loss, an Orca runtime/version change, or unavailable guidance.
Use the installed guidance for all worker lifecycle, inspection, wait, retry,
messaging, release, and cleanup operations. Do not recreate those commands in
`general-os` code or this skill.

## Repository-bound preflight

Before the first native worker dispatch for repository-bound work:

1. Resolve the intended repository from the task boundary and current Git as an
   absolute, normalized path.
2. Load the installed, version-matched native Orca guidance.
3. Ask that native guidance to validate the repository boundary, worktree
   selector, runtime capability, and reachability using its installed contract.
4. If native guidance reports that the target is unavailable or requires
   registration, authority, or another precondition, stop before dispatch and
   report that result. Register or open it only with explicit authority.
5. Re-resolve the repository boundary if the target repository, Orca runtime, or
   session context changes before dispatch.

## Handoff

The active native controller chooses this boundary within already authorized
scope. CoS may require an independent boundary as a durable constraint, but it
does not select Orca, a reviewer, or the execution topology. When a durable
assignment exists, general-os owns its semantic contract and passes it to the
native Orca entrypoint selected by the installed version:

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

After an authorized native controller selects Orca, let the installed native
guidance choose the smallest useful path—lightweight handoff, independent
workspace, or supervised orchestration. Do not add that topology choice to
durable general-os state.

`build_orca_launch(project_profile(profile), assignment)` remains a low-level
leaf/compatibility projection for simple native CLI launch paths. It maps only
explicit `harness`, `model`, `effort`, and `instructions` values plus the
ephemeral assignment to Orca launch flags; it does not define the conceptual
multi-agent boundary, create a second profile registry, or persist runtime
configuration.

The selected native path determines what is returned. Supervised orchestration
may return one semantic outcome/evidence bundle reporting success, partial
progress, failure, or a material blocker. A lightweight ownership handoff may
return only a transfer acknowledgement, if the native path reports one; the
handoff is not semantic task completion. Never persist or mirror Run IDs, Task
IDs, Dispatch IDs, worker IDs, heartbeats, progress, or other Orca runtime
 state in `general-os` durable state. For repository-bound work, the owning
 verifier must inspect current Git; for external-only work, it must inspect the
 owning project record and authoritative source. In either case, evaluate fresh
 evidence; neither a native outcome nor a successful handoff completes a
 general-os task by itself.

## Degradation

If Orca is unavailable, continue with Codex when independent ownership is not
required. If the durable task contract requires an independent boundary, report
the current Orca observation as a blocker. Do not mutate `orca_enabled` in
response to transient runtime health.

General-os does not provide a Python dispatch, inspection, cancellation, or
 worker registry seam. The native Orca skill owns real worker inspection and
 lifecycle; general-os may retain only read-only CLI health observation.
