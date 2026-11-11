# Runtime Adapters

Runtime boundaries are thin observations and handoffs to native runtimes, not
alternate owners of coordination policy.

The current Codex runtime is the primary execution path. It owns Goal Mode,
`update_plan`, context, approvals, tools, native subagents, and execution
lifecycle. General-os supplies durable intent, acceptance boundaries, and
exceptional authority; it does not reimplement a Codex transport or runtime
registry.

The Orca capability is optional. `orca_enabled` is permission/configuration,
not runtime health and not an authority escalation. CoS may select Orca when
independent ownership is required or materially useful; required independent
work blocks when Orca is disabled or unavailable rather than falling back to
Codex. Ordinary work remains Codex-first.

`general-os` observes current Orca availability through the CLI `status --json`
boundary. The repository `orca-orchestration` skill loads Orca's
version-matched guidance with `orca skills get orchestration --full` before
mutation and leaves worker lifecycle, inspection, retry, release, and cleanup
inside native Orca.

`agents/*.toml` is the sole profile registry. Profile names do not imply
runtime model or effort values. Explicit facts may be projected one way to the
selected native runtime; missing facts inherit native defaults. Orca remains
harness-neutral and may run Codex, Claude, or another explicitly supported
harness according to the resolved runtime configuration.

The maintained Python Orca surface only observes `orca status --json` for
read-only smoke evidence. It does not dispatch, inspect, cancel, or mirror
workers. Transient Orca failure does not mutate policy.

Neither adapter writes runtime IDs, heartbeats, progress, or lifecycle mirrors
into `state/coordination.json`.
