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

**1. Establish review scope:**
```bash
BASE_SHA=$(git rev-parse "$APPROVED_BASE")
HEAD_SHA=$(git rev-parse HEAD)
```

`APPROVED_BASE` must come from the caller, approved scope, or recorded merge
base.
Use this immutable SHA range when the approved review requires commit-pinned
Git evidence. For a local review before commit, provide the approved base when
available plus the scoped staged, unstaged, and untracked inventory; the
reviewer may inspect the current workspace or a frozen review package. Do not
force a commit solely to make an uncommitted review possible. Never infer a
base from commit count; `HEAD~1` can omit multi-commit changes.
Record the approved path inventory and exclusions with the review request. For
working-tree review, the approved base covers committed changes in scope while
the inventory covers staged, unstaged, and relevant untracked changes; paths
outside that inventory are unrelated and must not be loaded.

**2. Select review topology:**

The active native controller chooses whether review uses the current Codex
runtime, a native reviewer, or native Orca, and chooses the useful topology.
CoS may record a hard independence or review requirement for General
OS-coordinated work or an exceptional authority boundary, but it does not
select the reviewer runtime, profile, or topology. Native Orca owns internal
worker dispatch and topology after the native controller selects it.
Neither choice changes the review contract or makes the reviewer a merge owner.
Specialized profile names such as `review` or `ui` describe optional review
emphasis; they do not require a fixed reviewer count, sequence, or topology.

**3. Dispatch the reviewer through the selected runtime:**

Use `code-reviewer.md` as a reusable fallback when the selected runtime needs a
structured review prompt. If a native review capability already captures the
approved scope and evidence, pass the minimal required context directly rather
than wrapping it in a second prompt contract. If the selected runtime needs a
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
- `[BASE_SHA]` - Starting commit when an immutable Git range is required;
  otherwise the approved base or `Not applicable: local worktree review`
- `[HEAD_SHA]` - Ending commit when an immutable Git range is required;
  otherwise `Not applicable: local worktree review`
- `[APPROVED_PATHS]` - Caller-owned files or directories in review scope
- `[EXCLUDED_PATHS]` - Unrelated or protected paths that must not be loaded

**4. Act on feedback:**
- Fix Critical issues immediately
- Fix Important issues before proceeding
- Note Minor issues for later
- Push back if reviewer is wrong (with reasoning)

## Optional OCR Review

Use the installed OpenCodeReview CLI as an optional specialist code-review
capability when diff analysis adds value. OCR may be the primary code-diff
reviewer; native Codex or Orca can investigate unresolved or higher-risk
findings without repeating the entire review. The caller owns the approved Git
scope, revision identity, and protected-path policy; OCR does not reconstruct,
replace, or narrow that scope.

Invoke OCR through its native CLI and keep output disposable unless it is
intentionally retained, for example:

```text
ocr review --format json --audience agent --output review.json
ocr review --commit <sha> --format json --audience agent --output review.json
ocr review --from <base> --to <head> --format json --audience agent --output review.json
```

Verify the reported repository, revision, scope, and provenance against current
Git before consuming findings. OCR output is advisory: the caller reconciles
findings with requirements, source, tests, and relevant inspection. OCR does
not own implementation, acceptance, durable state, or reviewer topology. Apply
repository content policy before sending private or protected content to the
configured model provider; installation and upgrades remain external.

## Example

```
[Just completed Task 2: Add verification function]

You: Let me request code review before proceeding.

BASE_SHA=$(git rev-parse "$APPROVED_BASE")
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

See reusable fallback template at: `code-reviewer.md`
