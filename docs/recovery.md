# Recovery

Runtime loss is intentionally boring. Recover from durable intent plus current
Git, not from Codex or Orca session history:

1. Read `state/coordination.json`.
2. Inspect the current branch, revision, worktree, conflicts, and changed
   files directly from Git.
3. Determine the unfinished dependency-ready task, or redispatch the global
   goal when the task graph is empty. Goal-only state is intent-only and has no
   durable completion record; use a task graph when completion must be retained.
4. Revalidate every completed task against its accepted `GitSnapshot.identity`
   and the current work snapshot identity. The identity includes implementation
   changes and untracked content but excludes `state/coordination.json`, which
   is the durable semantic state written by acceptance itself. If evidence is missing or
   mismatched after checkout, reset, or other material Git divergence, move the
   task to `pending` and invalidate completed dependents transitively.
5. Reuse required evidence only after checking that it is fresh and applies to
   the current task and complete Git snapshot identity.
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
not reconstruct a runtime session or infer ownership from timestamps. A failed
deployment restores the files changed by that attempt and writes provenance
last. Locally modified or conflicting central files remain preserved for
manual resolution.
