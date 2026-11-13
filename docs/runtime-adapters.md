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
The provided profiles carry explicit `combo-*` model and effort values; the
runtime adapter passes them through without maintaining another combo or model
registry.
Use `general-os profile resolve --name <name> --directory agents` to inspect
the deterministic projection without launching a runtime. The command never
infers model or effort from rank or profile name.

When CoS selects Orca, `build_orca_launch(project_profile(profile))` performs
the one-way handoff into the native CLI contract. Orca requires an explicit
`harness`; `model`, `effort`, and `instructions` may be omitted and then retain
their native defaults subject to launch validation. Explicit values map to
`--agent`, `--model`, `--effort`, and `--prompt`. The handoff is an ephemeral
command description, not a second profile registry or a durable runtime
record.

The maintained Python Orca surface only observes `orca status --json` for
read-only smoke evidence. It does not dispatch, inspect, cancel, or mirror
workers. Transient Orca failure does not mutate policy.

Orca status observation uses a 30-second default timeout unless the caller
supplies another timeout. Malformed or unsupported status envelopes return a
bounded failed observation with an actionable message.

Acceptance does not infer independent execution from Orca reachability. The
native verifier or controller must provide ephemeral typed boundary evidence
bound to the current Git snapshot identity; no worker or runtime identifier is
persisted.

Neither adapter writes runtime IDs, heartbeats, progress, or lifecycle mirrors
into `state/coordination.json`.
