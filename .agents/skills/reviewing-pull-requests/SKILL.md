---
name: reviewing-pull-requests
description: Use when an independent agent must inspect a pull request and return head-bound technical review evidence.
---

# Reviewing Pull Requests

## Role

Inspect one pull request independently and return a technical verdict bound to
the exact reviewed head. This skill owns PR inspection and review evidence. It
does not implement fixes, merge, delete branches, remove worktrees, or decide
task acceptance.

## Inputs

Require repository, PR number, approved scope, preserved invariants, and
required checks. Read the PR base, head, and SHA from GitHub; a caller-supplied
expected SHA may additionally pin the review. If GitHub identity or access is
missing or ambiguous, return `BLOCKED`.

## Review Contract

Before inspection, verify repository identity, PR number, base ref and SHA when
material, head ref and SHA, and current PR head. If a supplied expected head
differs from the observed head, or the head moves during review, return `FAIL`
with a rerun condition; do not treat a retryable stale head as `BLOCKED`.

Inspect the exact diff, changed-file scope, tests, required checks, security or
data-loss risks, and approved deviations. Do not infer approval from CI alone.
Record known limits and unverified claims.

Return one review-local verdict:

- `PASS`: no blocking finding within approved scope
- `FAIL`: finding requires correction or rerun
- `BLOCKED`: identity, access, required proof, or review prerequisite is unavailable

Evidence must include repository, PR number, base ref and SHA when material,
head ref and SHA, verdict, checks inspected, findings, approved deviations,
and known limits. New commits invalidate prior review evidence.

OpenCodeReview may provide optional native specialist findings; PR review does
not own OCR invocation or installation. Verify the OCR output's repository,
revision, approved scope, and provenance against current Git before consuming
it. Preserve caller-owned Git inventory and apply repository content policy
before OCR; protected content is never review input, including both old and new
rename/copy paths. Treat OCR findings as advisory and reconcile them with
requirements, source, tests, and inspection. For committed review, use exact
base/head identity. For working-tree review, use scoped native
`review-package` with package SHA-256 and Git-inventory digest.

## GitHub Review State

Review-local status is separate from GitHub review state. Submit GitHub
`APPROVE` only when reviewer identity is eligible, differs from PR author when
required, and repository rules allow the approval to count. Otherwise submit
`COMMENT` or no GitHub action. Required distinct-identity approval returns
`BLOCKED`; do not create another account to satisfy this skill.

## Boundaries

Use `requesting-code-review` for dispatch and
`receiving-code-review` for feedback evaluation. Do not mutate the PR
branch, push commits, merge, delete branches, or remove worktrees. A review
does not complete a task or update durable coordination state.

## Output

Return the structured review evidence, exact reviewed head SHA, review-local
verdict, optional GitHub review action result, and rerun condition when head
changes. A stale head is a retryable review failure; it is not durable task
acceptance or a permanent project blocker.
