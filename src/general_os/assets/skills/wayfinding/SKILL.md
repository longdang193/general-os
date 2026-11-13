---
name: wayfinding
description: Use when the user explicitly invokes wayfinding for a known destination with materially unresolved dependent decisions expected to span sessions.
---

# Wayfinding Through Unresolved Decisions

Use only when the user explicitly invokes wayfinding, the destination is known,
the route contains materially unresolved dependent decisions, and the work is
expected to span multiple sessions (multi-session work). These are an AND gate. Missing any one
condition routes to the existing planning method instead.

## Role

Wayfinding coordinates provisional decision discovery. It never writes code,
creates implementation tasks, assigns builders, estimates work, or replaces
canonical specifications and plans.

## Entry Gate

Before opening a map, record evidence for all conditions:

- explicit user invocation of wayfinding;
- one bounded destination;
- dependent decisions whose answers affect later questions;
- expected work beyond one focused session.

If destination or problem framing is unknown, use `brainstorming`.
If behavior and design are settled, use `spec-drafting`. If approved
behavior needs implementation sequencing, use `defining-work`. Local,
reversible, design-clear work uses the existing direct execution route.

## Map Ownership

Create one task-owned design map at
`docs/wayfinding/<YYYY-MM-DD-HH-MM-topic>/map.md`. This is a
non-authoritative design artifact, not current governance or durable
coordination state; `state/coordination.json` remains the only durable
coordination ledger.

The current author is the sole writer. Other sessions return read-only findings
to that author. This is artifact ownership, not a second
coordination authority. Do not allow concurrent map edits, merge competing
maps, or copy settled decisions into the map, specification, and plan. Each
artifact keeps one owner and links to the others.

Use a concise task-owned map in the current response or plan. Keep entries
short and provisional. Record unresolved questions, evidence, alternatives,
and links only. Do not persist task states, owners, handoff status, stale or
reopen transitions, supersession state, dependencies, schedules, or runtime
identities in the map.

## Decision Frontier

Open items are precise questions, not build tasks. Give items short local labels
only when needed for discussion; they are not durable task IDs. Do not add code
slices, implementation acceptance tests, workflow state, owners, dependencies,
estimates, schedules, tracker IDs, or builder assignments.

Record evidence and alternatives needed to answer a question. Keep approved
behavior, interfaces, invariants, and design decisions out of the map's
canonical truth; promote them once through `spec-drafting`.

When an upstream decision changes, record the affected question and evidence in
the non-authoritative artifact, then promote the settled result once through
the specification path. Do not close the map, create implementation tickets,
or encode workflow transitions in it.

## Code Pressure

If the user asks for code while the decision frontier is unresolved, refuse the
code request and record it as out of scope. Do not skip the map, author control,
decision questions, promotion checks, or links to the owning planning flow.
Continue only with
decision discovery; implementation begins later through the approved durable
scope or specification and the planning tier selected by `defining-work`.

## Completion And Promotion

Finish the design exploration only when all conditions hold:

- destination remains valid;
- no material dependent decision or relevant fog remains;
- approved behavior has been promoted once through `spec-drafting`;
- the resulting specification or decision link is available to the owning
  planning flow.

After promotion, return to durable coordination state and use the chief-of-staff
decision flow and `defining-work` when implementation sequencing is needed.
Apply the next applicable gate from current `AGENTS.md` guidance. Wayfinding
does not pre-author plan tasks,
dependency order, write ownership, executor choice, or verification commands.

## Verification

Before promotion, verify that the map has one author, decision questions only, no
workflow ledger fields, no duplicated canonical prose, and clear evidence or
specification links. Verify that rejected entry cases route without opening a
map and that settled decisions are promoted through the specification path.

## Explicit Deferrals

Do not add or invoke separate `grilling`, `domain-modeling`, `research`, or
`prototyping` methods from this skill. Use existing source-first research,
brainstorming, and specification mechanisms. Do not add speculative template
changes, custom orchestration, runtime/session systems, tracker
adapters, CLIs, ticket generation, estimation, scheduling, or code execution.
