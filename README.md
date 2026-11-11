# general-os

`general-os` is a small durable semantic coordination layer above Git, native
Codex execution, and optional Orca orchestration.

The durable coordination object is `state/coordination.json`. Runtime session
facts remain in their native systems and are observed at the point of use.
`project-OS-starter` is a read-only migration reference, not a runtime or
schema dependency.
