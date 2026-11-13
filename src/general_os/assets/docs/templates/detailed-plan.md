# Goal

Describe the desired outcome in one sentence.

# Outcomes

- Name the observable results that must exist when the work is accepted.

# Constraints / decisions

- Record only material constraints, invariants, or decisions that a fresh
  executor could not safely reconstruct.
- Do not duplicate repository guidance or native runtime planning.

# Task graph

## Task A

**Objective:**

Describe the bounded semantic outcome owned by this task.

**Scope:**

Name only material system, component, interface, or ownership boundaries when
they constrain execution. Do not enumerate expected file edits unless those
files themselves form a durable scope boundary.

**Dependencies:**

None.

**Durable sequencing:** <!-- optional -->

Record only ordering that another fresh executor must preserve. Do not write a
normal implementation checklist.

**Constraints / decisions:** <!-- optional -->

Record task-specific invariants or decisions that must survive runtime loss.

**Acceptance:**

Name observable evidence proving the task outcome.

**Verification:**

- Name fresh checks required to establish acceptance.
- Prefer intent and required evidence over prescribing every temporary command.

**Stop / escalation conditions:** <!-- optional -->

Identify material conditions where the executor must stop and return for a
decision instead of improvising.

## Task B

Repeat the fields above for the next bounded semantic assignment when needed.

# Final verification

- List the fresh end-to-end evidence needed to prove the complete goal against
  current Git and relevant external state.

This template describes durable coordination. Concrete files, symbols, commands,
and implementation steps belong to native runtime planning; include them here
only when they are themselves non-derivable durable boundaries or an explicitly
requested handoff contract.
