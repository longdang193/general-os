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
boundary. The repository `orca-orchestration` skill loads the installed,
version-matched guidance for the selected native Orca path before mutation;
simple independent assignments use lightweight handoff guidance, while
supervised assignments use the native orchestration guidance. worker lifecycle,
inspection, retry, release, and cleanup remain inside native Orca.

After CoS selects Orca, native guidance chooses the smallest useful execution
path. That topology choice is not a durable general-os routing field.

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

When project-level CoS selects Orca, general-os hands the native Orca
coordinator/coordinating agent provided by the installed version a semantic
workstream contract: objective, task identity, relevant context and
constraints, acceptance/evidence requirements, explicit profile facts, and the
relevant repository or work boundary. Orca owns internal orchestration and
execution topology, including decomposition, workers, supervision, retries,
nested helpers, fan-in, and cleanup. Its returned outcome/evidence bundle may
report success, partial progress, failure, or a material blocker.

`build_orca_launch(project_profile(profile), assignment)` remains a low-level
one-way leaf/compatibility projection into the native CLI. Orca requires an explicit
`harness`; `model`, `effort`, and `instructions` may be omitted and
then retain their native defaults subject to launch validation. Explicit values
map to `--agent`, `--model`, `--effort`, and `--prompt`. The helper is not the
conceptual multi-agent boundary and the handoff remains an ephemeral command
description, not a second profile registry or a durable runtime record.

The maintained Python Orca surface only observes `orca status --json` for
read-only smoke evidence. It does not dispatch, inspect, cancel, or mirror
workers. Transient Orca failure does not mutate policy.

Orca status observation uses a 30-second default timeout unless the caller
supplies another timeout. Malformed or unsupported status envelopes return a
bounded failed observation with an actionable message.

Acceptance does not infer independent execution from Orca reachability or
runtime completion. Project-level CoS must inspect current Git and the native
verifier or controller must provide ephemeral typed boundary evidence bound to
the current Git snapshot identity; no worker or runtime identifier is
persisted.

Neither adapter writes runtime IDs, heartbeats, progress, or lifecycle mirrors
into `state/coordination.json`.

## Deployment adapter

The `codex` deployment adapter is intentionally near-no-op: it activates the
central shared skill discovery path and does not generate a `~/.codex` tree,
credential projection, runtime registry, or execution loop. Other adapter
projections require a separate approved contract.
