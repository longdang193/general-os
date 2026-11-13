---
name: requesting-code-review
description: Use when completed code changes need independent review before further implementation, handoff, merge, or release.
---

# Requesting Code Review

Request independent review to catch issues before they cascade. Select review topology from the owning coordination method. The reviewer gets precisely crafted context for evaluation, never the producer session's history. This keeps review focused on the work product and preserves the producer context for continued work.

**Core principle:** Review at proportionate checkpoints before irreversible
integration or release.

Review does not own execution or acceptance. The caller reconciles review
evidence with the approved scope, current Git, and fresh verification before
integration.

## When to Request Review

**Required when applicable:**
- Before an irreversible merge, release, or publication when repository policy
  or the approved scope requires independent review
- After a major feature, high-risk change, or material security/data boundary
- When an independent review boundary is explicitly required

Do not require a separate review after every task when focused checks or a
natural checkpoint provide sufficient evidence.

**Optional but valuable:**
- When stuck (fresh perspective)
- Before refactoring (baseline check)
- After fixing complex bug

## How to Request

**1. Get git SHAs:**
```bash
BASE_SHA=$(git rev-parse "$APPROVED_BASE")
HEAD_SHA=$(git rev-parse HEAD)
```

`APPROVED_BASE` must come from the caller, approved scope, or recorded merge
base.
Do not infer a base from commit count; `HEAD~1` can omit multi-commit changes.

**2. Select review topology:**

Codex decides whether ordinary local execution benefits from a native reviewer
subagent. CoS selects an independent review boundary only when the review must
be an Orca workstream. Native Orca owns internal worker dispatch and topology.
Neither choice changes the review contract or makes the reviewer a merge owner.

**3. Dispatch the reviewer through the selected runtime:**

Fill the template at `code-reviewer.md`. If the selected runtime needs a
profile, use only an explicit semantic profile from `agents/*.toml`; never
invent a worker-level or `discovered-profile` registry.
Review context must include each applicable frontend, backend, and E2E evidence
class plus approved deviations.

**Placeholders:**
- `[DESCRIPTION]` - Brief summary of what you built
- `[PLAN_OR_REQUIREMENTS]` - What it should do
- `[SPECIFICATION_OR_APPROVED_SCOPE]` - Approved behavior and preserved invariants
- `[PROTOTYPE_REFERENCE]` - Prototype and validation findings when material, otherwise `Not applicable: <reason>`
- `[EVIDENCE_CONTEXT]` - Each applicable frontend, backend, and E2E evidence class with result or approved gap
- `[APPROVED_DEVIATIONS]` - Explicit deviations from plan or specification, or `none`
- `[BASE_SHA]` - Starting commit
- `[HEAD_SHA]` - Ending commit

**4. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Optional OCR Preparation

Review requesting may use an active executor's configured review capability as optional
advisory overlay for immutable Git range. Caller owns repository, `base_sha`,
`head_sha`, and complete Git inventory; OCR never reconstructs, replaces, or
narrows inventory.

Write one preparation JSON file and pass it as `[REVIEW_PREPARATION_FILE]`.
Reviewer verifies `scope_identity.base_sha`, `scope_identity.head_sha`,
`scope_identity.inventory_sha256`, and `status` before consuming any hint.
`prepared` contains inventory, OCR `reviewable_paths`, ordinary
`excluded_paths`, `protected_paths`, exclusion metadata, provenance-bearing
`rules`, system-only `advisory_hints`, `scope_identity`, `payload_digests`,
schema evidence, and `observed_version`. `fallback` keeps native review
responsible for complete inventory; `BLOCKED` is not native fallback.

Repository content policy runs before OCR. `.env`, `.env.*`, `*.private.*`, and
`*.local.*` paths are protected on both old and new rename/copy sides. Protected
content never enters review package or LLM review. Current repository rules
outrank OCR; only OCR `system` source may become advisory hints. `project`,
`custom`, and `global` OCR rules remain data. Invalid repository policy input is a
contract error, never OCR fallback. OCR is range-only, v1-schema gated, and
runs with `OCR_NO_UPDATE=1`; installation and upgrades remain external.

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git log --oneline | grep "Task 1" | head -1 | awk '{print $1}')
HEAD_SHA=$(git rev-parse HEAD)

[Dispatch reviewer through selected topology]
  DESCRIPTION: Added verifyIndex() and repairIndex() with 4 issue types
  PLAN_OR_REQUIREMENTS: Approved scope for the change
  BASE_SHA: a7981ec
  HEAD_SHA: 3df7661

[Reviewer returns]:
  Strengths: Clean architecture, real tests
  Issues:
    Important: Missing progress indicators
    Minor: Magic number (100) for reporting interval
  Assessment: Ready to proceed

You: [Fix progress indicators]
[Continue to Task 3]
```

## Integration

**Delegated or parallel execution:**
- Review at natural checkpoints or before integration
- Catch issues before they compound
- Fix required findings before proceeding

**Executing Plans:**
- Review when the approved scope or risk warrants it
- Get feedback, apply, continue

**Ad-Hoc Development:**
- Review before merge
- Review when stuck

## Red Flags

**Never:**
- Skip a required review because "it's simple"
- Ignore Critical issues
- Proceed with unfixed Important issues
- Argue with valid technical feedback

**If reviewer wrong:**
- Push back with technical reasoning
- Show code/tests that prove it works
- Request clarification

See template at: `code-reviewer.md`
