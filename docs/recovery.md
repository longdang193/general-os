# Recovery

Runtime loss is intentionally boring. Recover from durable intent plus current
Git, not from Codex or Orca session history:

1. Read `state/coordination.json`.
2. Inspect the current branch, revision, worktree, conflicts, and changed
   files directly from Git.
3. Determine the unfinished dependency-ready task, or use the global goal when
   the task graph is empty.
4. Reuse required evidence only after checking that it is fresh and applies to
   the current Git revision.
5. Start a fresh native assignment. Use the current Codex runtime by default;
   use Orca only when the unfinished work needs an independent workstream and
   the configured boundary is available.

If Git has a material conflict, a required dependency is unfinished, authority
is insufficient, or a required independent boundary is unavailable, block and
preserve the workspace. Missing optional runtime metadata lowers confidence but
does not create a new recovery ledger or automatically stop safe work.

There is no separate recovery runtime or recovery ledger. Do not reconstruct
lost runtime sessions, persist runtime IDs, or copy runtime progress into
`state/coordination.json`.
