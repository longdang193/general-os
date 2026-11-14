# Recovery

Runtime loss is intentionally boring. Recover from durable intent plus current
Git, not from Codex or Orca session history:

1. Read `state/coordination.json`.
2. Inspect the current branch, revision, worktree, conflicts, and changed
   files directly from Git.
3. Determine unfinished dependency-ready semantic work, or redispatch the global
   goal when the task graph is empty. Goal-only state is intent-only and has no
   durable completion record; use a task graph when completion must be retained.
4. Revalidate every completed task's accepted task-contract fingerprint and
   dependency closure. The accepted `GitSnapshot.identity` remains historical
   evidence of where acceptance occurred; later commits or unrelated Git changes
   do not automatically demote completed tasks. A fresh current Git snapshot is
   still required before relying on the result for new acceptance or publication.
   When accepted and current identities differ, treat the affected completed
   tasks as ephemeral re-verification candidates. This is a signal for a
   decision that relies on their evidence, not a mandate for a global sweep;
   run task-level verification against current Git only before relying on the
   affected result, and do not persist a candidate list.
5. Reuse required evidence only after checking that it is fresh and applies to
   the current task and complete current Git snapshot identity.
6. Start a fresh native assignment. Use the current Codex runtime by default;
   use Orca only when the unfinished work needs an independent workstream and
   the configured boundary is available.

If Git has a material conflict, a required dependency is unfinished, authority
is insufficient, or a required independent boundary is unavailable, block and
preserve the workspace. Missing optional runtime metadata lowers confidence but
does not create a new recovery ledger or automatically stop safe work.

There is no separate recovery runtime or recovery ledger. Do not reconstruct
lost runtime sessions, persist runtime IDs, or copy runtime progress into
`state/coordination.json`.

Central deployment recovery is similarly Git- and lock-bound. Read
`~/.agents/general-os/managed.json` and rerun `general-os deploy --check`; do
not reconstruct a runtime session or infer ownership from timestamps. Use
`general-os deploy --repo . --check` only when explicitly inspecting the
one-shot adoption boundary; an existing adoption record does not make project
semantics deployment-owned. A failed
deployment restores the files changed by that attempt and writes provenance
last. Locally modified or conflicting central files remain preserved for
manual resolution.
