# Runtime Adapters

Adapters are thin boundaries to native runtimes, not alternate owners of
coordination policy.

The Codex adapter exposes the native `run`, `inspect`, and `cancel` boundary.
Codex receives the resolved semantic profile and the
`native_subagents_enabled` toggle; Codex itself decides whether native
subagents help its bounded assignment. Goal Mode, `update_plan`, context,
approvals, tools, and child lifecycle remain native Codex behavior.

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

The injected Python `OrcaTransport`/`OrcaClient` worker lifecycle is a
transitional compatibility/test seam, not a second scheduler or the canonical
interactive path. Transient Orca failure does not mutate policy.

Neither adapter writes runtime IDs, heartbeats, progress, or lifecycle mirrors
into `state/coordination.json`.
