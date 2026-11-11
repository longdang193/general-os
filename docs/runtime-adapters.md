# Runtime Adapters

The Codex adapter is a direct native boundary with `run`, `inspect`, and
`cancel` operations. Codex receives the resolved profile and the
`native_subagents_enabled` toggle; native subagent choice remains inside
Codex.

The Orca capability is optional. `orca_enabled` is permission/configuration,
not runtime health or an authority escalation. `general-os` observes current
Orca availability through the CLI `status --json` boundary. The repository
`orca-orchestration` skill loads Orca's version-matched orchestration guidance
once per active session and leaves worker lifecycle, inspection, and cleanup
inside native Orca.

The existing injected Python `OrcaTransport`/`OrcaClient` worker lifecycle is a
transitional compatibility/test seam, not the canonical general-os path.
Transient Orca failure does not mutate policy. Ordinary work remains Codex-first;
only work that requires independent ownership blocks when Orca is unavailable.

Neither adapter writes runtime IDs, heartbeats, or lifecycle mirrors into
`state/coordination.json`.
