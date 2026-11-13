---
name: systematic-debugging
description: Use when diagnosing a bug, failure, or unexpected behavior before proposing a fix.
---
# Systematic Debugging

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** Establish root cause before a permanent corrective fix.
Reversible containment may precede full diagnosis when needed to limit impact,
but it is not a root-cause resolution.

**Violating the letter of this process is violating the spirit of debugging.**

<EXTREMELY-IMPORTANT>
## The Iron Law

```
NO PERMANENT CORRECTIVE FIX WITHOUT ROOT-CAUSE EVIDENCE
```

If you haven't completed Phase 1, do not propose a permanent corrective fix.
Containment is allowed when necessary to limit active impact.
</EXTREMELY-IMPORTANT>

## When to Use

Use for ANY technical issue:

- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**Use this ESPECIALLY when:**

- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

**Don't skip when:**

- Issue seems simple (simple bugs have root causes too)
- You're in a hurry (rushing guarantees rework)
- Manager wants it fixed NOW (containment may be needed before diagnosis)

## Related Skills

- Use `performance-optimization` when the defect is a measured latency, throughput, memory, query, bundle, rendering, or Core Web Vitals problem requiring comparable before/after proof.
- Use `full-stack-integration` when the failure crosses frontend behavior, typed clients, API contracts, route handling, authorization, or backend responses.
- Use `executing-work` only after evidence separates failures into independent problem domains.
- Each dispatched investigator follows this debugging method inside its assigned domain.
- Keep possibly shared-cause failures together until root-cause evidence proves independence.

## Evidence Capability

State minimum tracing capability and required evidence before selecting a tool.
Prefer native source, tests, and reproduction evidence; resolve unmet
capabilities through the active runtime's configured/native tooling. Read
`docs/runtime-adapters.md` only for runtime-boundary questions.
Source, tests, and reproduction evidence remain authoritative.

## The Four Phases

Complete the phases in order for permanent corrective fixes. Containment may
interrupt the sequence when needed to limit active impact.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess
   - For browser-visible failures, use available browser-interaction capability when available to reproduce repeatable flows and capture semantic state
   - If no suitable browser-diagnostic capability is currently available, use existing browser evidence and native logs before adding a new diagnostic path; otherwise select the needed capability through the active runtime's configured/native tooling
   - Browser replay is diagnostic evidence, not committed regression coverage; preserve the failure in the existing browser test suite before fixing when practical

3. **Check Failure Memory When The Issue Looks Familiar**
   - If the failure appears repeated, method-related, or suspiciously similar to a previous repo-operating issue, search configured MCP memory when active executor exposes it; under external worker runtime, request validated Codex handoff facts
   - Use it to recognize known failure modes earlier
   - Do not skip direct investigation just because something looks familiar

4. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

5. **Gather Evidence in Multi-Component Systems**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**

   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Audit gate (mandatory):**
   - if the current task explicitly requires audit evidence and no active audit exists, create or update the task-owned audit report
   - use the approved task or plan format; do not assume an external audit template
   - add evidence or reproduction files only when they contain real artifacts needed by report


   **Example (multi-layer system):**

   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

6. **Trace Data Flow**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Reproducible Proof**
   - Simplest possible reproduction
   - Automated failing test when practical
   - One-off test script, log, trace, or other reproducible evidence when an automated test cannot represent the failure
   - Preserve the proof before fixing when practical
   - Use `test-driven-development` for writing proper failing tests

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Record the failed hypothesis and return to Phase 1 with new evidence
   - If repeated failures reveal shared coupling, state problems, or no credible
     root-cause hypothesis remains, stop and question the architecture

5. **If Evidence Indicates Architectural Risk: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

    **Discuss with the request owner before attempting more fixes**

    Do not label architecture wrong without evidence; record the observed
    coupling or repeated failed hypotheses first.

## Red Flags - STOP and Follow Process

If you catch yourself thinking:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**ALL of these mean: STOP. Return to Phase 1.**

**If repeated failures reveal shared coupling or leave no credible root-cause
hypothesis:** Question the architecture before attempting another fix.

## your human partner's Signals You're Doing It Wrong

**Watch for these redirections:**

- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultrathink this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**When you see these:** STOP. Return to Phase 1.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Contain active impact first when needed, then return to root-cause investigation. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" after repeated failures | Record evidence and reassess the hypothesis before trying another fix. |

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, gather evidence | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify | Bug resolved, tests pass, audit linkage complete when required |

## When Process Reveals "No Root Cause"

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

## Supporting Techniques

These techniques are part of systematic debugging and available in this directory:

<LINK>
- **`root-cause-tracing.md`** - Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** - Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** - Replace arbitrary timeouts with condition polling
</LINK>

**Related skills:**

- **test-driven-development** - For creating failing test case (Phase 4, Step 1)
- **performance-optimization** - Define representative workloads, metrics, targets, and comparable performance proof
- **full-stack-integration** - Reconcile frontend intent, transport contracts, API impact, and browser evidence
- **verification-before-completion** - Verify fix worked before claiming success
