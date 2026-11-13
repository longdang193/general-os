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

Create one active map at
`docs/superpowers/plans/wayfinding/<YYYY-MM-DD-HH-MM-topic>/map.md`.

The current coordinator is the sole writer. Other sessions return read-only
findings to that coordinator. This is artifact ownership, not a second
coordination authority. Do not allow concurrent map edits, merge competing
maps, or copy settled decisions into the map, specification, and plan. Each
artifact keeps one owner and links to the others.

Use a concise task-owned map in the current response or plan. Keep map
entries short and provisional.

## Decision Frontier

Open items are precise questions, not build tasks. Every item has an ID,
question, dependencies, state, and decision-work owner. Do not add code slices,
implementation acceptance tests, estimates, schedules, tracker IDs, or builder
assignments.

Record evidence and alternatives needed to answer a question. Keep approved
behavior, interfaces, invariants, and design decisions out of the map's
canonical truth; promote them once through `spec-drafting`.

When an upstream decision changes, mark affected downstream items stale or
reopen them. Do not close the map or create implementation tickets while stale
items remain. If the whole map is replaced, mark the old map `superseded` and
link exactly one successor.

## Code Pressure

If the user asks for code while the decision frontier is unresolved, refuse the
code request and record it as out of scope. Do not skip the map, writer control,
decision questions, closure checks, or downstream handoff. Continue only with
decision discovery; implementation begins later through the approved durable
scope or specification and the planning tier selected by `defining-work`.

## Closure And Handoff

Close only when all conditions hold:

- destination remains valid;
- no material dependent decision or relevant fog remains;
- no item is stale;
- approved behavior has been promoted once through `spec-drafting`;
- handoff is recorded.

After closure, return to durable coordination state and use the chief-of-staff
decision flow and `defining-work` when implementation sequencing is needed.
Apply the next applicable gate from current `AGENTS.md` guidance. Wayfinding
does not pre-author plan tasks,
dependency order, write ownership, executor choice, or verification commands.

## Verification

Before handoff, verify that the map has one writer, decision questions only,
clear dependencies, no duplicated canonical prose, and no stale items. Verify
that rejected entry cases route without opening a map. Verify that closure,
promotion, handoff, and supersession are recorded.

## Explicit Deferrals

Do not add or invoke separate `grilling`, `domain-modeling`, `research`, or
`prototyping` methods from this skill. Use existing source-first research,
brainstorming, and specification mechanisms. Do not add speculative template
changes, custom orchestration, runtime/session systems, tracker
adapters, CLIs, ticket generation, estimation, scheduling, or code execution.
