# Runtime Adapters

The Codex adapter is a direct native boundary with `run`, `inspect`, and
`cancel` operations. Codex receives the resolved profile and the
`native_subagents_enabled` toggle; native subagent choice remains inside
Codex.

The Orca adapter is experimental and optional. `orca_enabled` is configuration,
not an authority escalation. The wrapper reports unavailable when no transport
is configured and reports live verification only after a real local smoke.

Neither adapter writes runtime IDs, heartbeats, or lifecycle mirrors into
`state/coordination.json`.
