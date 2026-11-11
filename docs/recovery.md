# Recovery

Runtime loss is intentionally boring:

1. Read `state/coordination.json`.
2. Inspect current Git directly.
3. If Git has a material conflict, block and preserve the workspace.
4. If required evidence already exists, verify it against current Git.
5. Otherwise start a fresh Codex assignment, or an optional Orca assignment
   when independent ownership is required and configured.

No runtime session reconstruction or recovery ledger is required.
