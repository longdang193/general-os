# Contracts

The durable contract has one task state: `pending`, `active`, `blocked`, or
`completed`. Dispatch, runtime, verification, and acceptance results are
transient observations. Runtime identities are never serialized into
`state/coordination.json`.

Acceptance uses the current task, current Git snapshot, and fresh verification.
Repeated successful task transitions are idempotent.
