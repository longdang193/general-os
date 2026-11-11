# Project OS Starter Migration

`project-OS-starter` is a strictly read-only reference for this successor.
`general-os` retains useful ideas such as profile selection, Git observation,
acceptance, and recovery-by-restart, but implements them in repository-owned
code.

`general-os` does not require the Project OS installation, plan schema,
generated agent trees, Herdr launchers, Project Secretary state, runtime
session mirrors, or a second task ledger. Its durable source is
`state/coordination.json`; current Codex, Orca, and Git facts remain in their
native systems.
