---
layer: change
artifact_type: plan
status: proposed
template_id: implementation-plan
contract_version: "1"
name: general-os-validated-review-findings-remediation
targets:
  - src/general_os/acceptance.py
  - src/general_os/cli.py
  - src/general_os/git.py
  - src/general_os/orca.py
  - src/general_os/policy.py
  - src/general_os/state.py
  - docs/contracts.md
  - docs/recovery.md
  - docs/migration/project-os-starter.md
  - docs/rules/publication-boundary.md
  - .agents/skills/finishing-development-work/SKILL.md
  - tests/
---

# general-os Validated Review Findings Remediation Plan

## Goal

Remediate the findings that were both visible in completed, revision-pinned
GitHub review responses and reproducible from the source tree at
`longdang193/general-os@d32cd2c9adc9f3d9ccbe2c7914669b71caefaff8`.

Preserve the intended design: Git remains repository and recovery truth;
general-os remains a small durable semantic layer; Codex remains the normal
execution harness; native subagents remain Codex-owned; Orca remains optional
independent orchestration; and no runtime ledger, worker registry, scheduler,
second profile registry, or mirrored lifecycle state is introduced.

## Review Evidence Gate

- Repository: `longdang193/general-os`
- Branch: `main`
- Reviewed commit: `d32cd2c9adc9f3d9ccbe2c7914669b71caefaff8`
- Review context: `longdang193-general-os-d32cd2c9-ssot-migration-review`
- Profile marker: repository `longdang193/general-os`, project key
  `longdang193-general-os`
- Publication: no publication required; the reviewed full SHA was already
  reachable from `origin/main`.

Both bounded runner results were terminal and complete:

| Model | Effort | Runner result | Chat identity | Completion evidence |
| --- | --- | --- | --- | --- |
| `GPT-5.6-Sol` | `High` | `run-KMLVN7`, `completed`, `acknowledged`, `confirmed`, cleanup completed | `6af5906d-db04-83eb-8b09-bc6430997af2` | Visible response cited revision `d32cd2c9adc9f3d9ccbe2c7914669b71caefaff8`, plan heading `# Goal`, migration source SHA `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`, and plan blob `cc826f8242f7d3a27b654234e39aa78453f16372` |
| `GPT-6` | `High` | `run-Idc3UE`, `completed`, `acknowledged`, `confirmed`, cleanup completed | `6af591e1-c6b4-83ed-a724-e78e45e1984b` | Visible response cited repository/commit `longdang193/general-os@d32cd2c9adc9f3d9ccbe2c7914669b71caefaff8`, branch `main`, plan headings, and the same plan blob |

The existing chats were re-opened read-only in the same repository-bound
profile through the loopback TCP-CDP endpoint. `/json/version` and
`/json/list` were verified; the authenticated ChatGPT tab, requested model,
`High` effort, commit-pinned prompt, and final visible response were present
for both chats. No run was incomplete or ambiguous, so no finding was excluded
because of missing review evidence.

Runner artifacts are retained outside the repository at:

- `C:\tmp\general-os-review-d32cd2c9-ssot-migration\run-KMLVN7\result.json`
- `C:\tmp\general-os-review-d32cd2c9-ssot-migration\run-KMLVN7\response.md`
- `C:\tmp\general-os-review-d32cd2c9-ssot-migration\run-Idc3UE\result.json`
- `C:\tmp\general-os-review-d32cd2c9-ssot-migration\run-Idc3UE\response.md`

## Validated Findings

The following findings are included because the completed review responses
identify the pinned source and the current checkout contains the cited
behavior or missing proof:

1. `src/general_os/cli.py:run_accept` constructs a passing
   `VerificationResult` directly from caller-controlled status, check names,
   revision, and snapshot identity. The CLI does not prove that checks ran or
   that the result came from a verifier.
2. `src/general_os/policy.py:resolve_policy` turns a durable allow exception
   with a declared scope into global `RuntimeConfig(remote_side_effects="allow")`
   without matching the requested operation to that scope.
3. `src/general_os/state.py:CoordinationState.__post_init__` rejects an
   expired durable allow exception, making an otherwise valid coordination
   file unloadable after expiry.
4. `src/general_os/acceptance.py:BoundaryEvidence` checks only non-empty shape,
   supported kind, and snapshot identity. It does not establish task binding,
   worker provenance, or replay resistance, and `run_accept` has no supported
   successful independent-boundary evidence path.
5. `src/general_os/git.py:GitRepository._identity` omits canonical repository
   and worktree identity, so clean clones at the same branch and revision can
   collide.
6. `CoordinationState` is frozen but `policy_exceptions` remains a mutable
   dictionary, while `save_state` calls a `validate` method that does not
   re-check the policy-exception schema.
7. `docs/recovery.md` does not specify revalidation of completed tasks after a
   checkout, reset, or other material Git divergence.
8. `tests/test_documentation_contracts.py` proves counts and selected names but
   not every manifest disposition, destination, active rule owner, retired
   control-plane reference, or migrated executable skill behavior.
9. `src/general_os/cli.py:run_orca_smoke` returns exit code `0` for unavailable,
   timed-out, and malformed Orca observations.
10. `src/general_os/git.py:GitRepository._identity` reads every untracked file
    with `read_bytes`, creating an unbounded-memory and weak I/O-failure path.
11. `docs/rules/publication-boundary.md` has no active maintained-skill owner;
    publication safeguards are duplicated elsewhere instead of being
    discoverable through one canonical owner.
12. `docs/recovery.md` says reused evidence must match the current Git
    revision, while the executable acceptance contract requires the complete
    `GitSnapshot.identity`.
13. `src/general_os/orca.py:discover_executable` silently falls through to
    PATH when `GENERAL_OS_ORCA_CLI` is set to an invalid explicit path.
14. The migration plan records verification against an earlier HEAD rather
    than the reviewed SHA; this is a provenance gap, not proof that the final
    tree fails.
15. `src/general_os/state.py` uses equality checks for schema version `1`, so
    JSON boolean `true` is accepted because Python treats `True == 1`.

Excluded from implementation scope: claims requiring live Orca worker
execution, production-load behavior, or external-service behavior that the
reviews did not directly establish. The lack of a GitHub CI run is recorded as
verification provenance, not converted into a requirement to add CI.

## Implementation Outcomes

### Trustworthy acceptance and boundary evidence

Passing acceptance requires verifier-produced, task-bound evidence tied to the
current repository/worktree snapshot. Free-form CLI assertions cannot create a
passing result. Independent-boundary evidence remains ephemeral and must not
create a worker ledger or persist runtime identifiers.

### Safe, scoped durable authority

Durable policy exceptions match the requested operation scope, expire by
falling back to the safer local policy instead of invalidating the state file,
and are fully revalidated before persistence. Schema version types are strict.

### Repository-bound, bounded recovery evidence

Snapshot identity includes canonical repository/worktree provenance, hashes
untracked content with bounded memory and explicit I/O behavior, and the
recovery contract requires completed-task revalidation after Git divergence.

### Fail-visible optional Orca diagnostics

An invalid explicit Orca executable is reported as configuration failure rather
than silently replaced. Smoke probes expose failure through their exit status
while ordinary Codex work still degrades gracefully when Orca is optional.

### Executable migration proof and one publication owner

The migration manifest is checked against exact source-to-disposition and
destination invariants, the publication rule has one discoverable maintained
owner, and historical verification claims identify the exact revision they
prove.

## Execution Approach

- Mode: `inline sequential`
- Coordination: `none`
- Required skills: `skill-code-standards`, `skill-backend-verification`,
  `skill-verification-before-completion`
- Isolation: `current workspace`; preserve unrelated untracked `.serena/`
- Commit policy: `no commits during execution`; commit, push, merge, and branch
  disposition require separate explicit authorization
- Preauthorized local actions: edit the listed source, test, and documentation
  files; run declared local tests and read-only inventory probes; preserve
  unrelated workspace state
- User-approval actions: push, merge, publication, destructive cleanup,
  discard, or changes to the approved architecture
- Parallel ownership: none; acceptance, policy, state, Git identity, and
  documentation contracts share verification boundaries and run serially
- Sequential fallback: execute Tasks 1–5 in order, then run Task 6 as the sole
  final verification gate

## Task Breakdown

### Task 1: Make acceptance results verifier-produced and boundary-bound

**Purpose:** Prevent caller-controlled assertions and weak independent-boundary
receipts from producing durable `PASS` transitions.

**Task Function:** Acceptance trust-boundary remediation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from the required reasoning depth and security risk before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently validate forged, stale, replayed, and valid evidence.

**Specification Coverage:** Acceptance outside the worker; no runtime ledger;
current Git remains the evidence authority; native Codex remains the default.

**Required Skills:** `skill-code-standards`, `skill-backend-verification`.

**Files And Symbols:**
- Inspect and modify `src/general_os/acceptance.py:BoundaryEvidence`,
  `VerificationResult`, `evaluate_acceptance`, and `apply_task_transition`.
- Inspect and modify `src/general_os/cli.py:run_accept` and the `accept` parser.
- Verify `tests/test_acceptance.py` and `tests/test_cli.py`.

**Dependencies:** None.

**Authority:**
- Preauthorized local actions: edit acceptance/CLI code and focused tests; run local unit and contract checks.
- Stop for: a new runtime ledger, worker registry, external side effect, or unresolved change to the durable state schema.

**Steps:**
- [ ] Define the existing verifier-to-acceptance handoff so a `PASS` cannot be
  assembled from free-form CLI claims; preserve `FAIL` and `BLOCKED` semantics.
- [ ] Bind independent-boundary evidence to the task and repository/worktree
  identity without persisting worker IDs, heartbeats, or runtime lifecycle.
- [ ] Reject forged, replayed, cross-task, wrong-worktree, and unsupported
  boundary evidence before `apply_task_transition` can complete a task.
- [ ] Keep repeated successful transitions idempotent and preserve dependency
  and blocker validation.

**Verification:**
- [ ] Add tests for missing verifier output, forged check names, valid evidence,
  replayed evidence, cross-task evidence, and wrong-worktree evidence.
- Expected: only verifier-produced evidence for the current task and snapshot
  can yield `PASS`; ordinary Codex work remains usable without Orca.

**Exit Criteria:** The CLI and Python acceptance path cannot manufacture a
passing task from caller assertions, and the focused acceptance/CLI tests pass.

### Task 2: Harden scoped policy exceptions and durable state validation

**Purpose:** Keep authority exceptions scoped and expirable without making the
coordination state unrecoverable or mutable past validation.

**Task Function:** Durable authority and schema-hardening remediation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from authority scope and state-integrity risk before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: validate authorized/unauthorized scopes, expiry fallback, and persistence mutation cases.

**Specification Coverage:** Lightweight exceptional authority; safe expiry;
single durable state object; no second permission system.

**Required Skills:** `skill-code-standards`, `skill-backend-verification`.

**Files And Symbols:**
- Inspect and modify `src/general_os/policy.py:resolve_policy` and
  `AuthorityExceptions` handling.
- Inspect and modify `src/general_os/state.py:CoordinationState.__post_init__`,
  `from_dict`, `validate`, `to_dict`, `load_state`, and `save_state`.
- Verify `tests/test_policy.py` and `tests/test_state.py`.

**Dependencies:** Task 1 for the acceptance-facing authority contract.

**Authority:**
- Preauthorized local actions: edit policy/state code, schema tests, and contract documentation; run local state and policy checks.
- Stop for: a new permission registry, credential handling, external approval integration, or silent widening of local deny ceilings.

**Steps:**
- [ ] Require an operation scope when resolving a durable allow and reject an
  exception whose scope does not match the requested target.
- [ ] Treat provenance as evidence metadata rather than a free-form grant;
  preserve the local `deny` ceiling and reject incomplete authority metadata.
- [ ] Separate syntactic state validation from active-authority expiry so an
  expired exception remains loadable and resolves to the safer local policy.
- [ ] Revalidate policy-exception structure on every save or make the nested
  mapping immutable without breaking JSON serialization.
- [ ] Reject boolean and non-integer schema versions explicitly.

**Verification:**
- [ ] Test authorized and unauthorized scope resolution, expired-state loading,
  post-load mutation followed by save, malformed metadata, deny ceilings, and
  `version: true`.
- Expected: expired or invalid authority cannot block recovery or widen policy,
  and invalid mutations cannot be persisted.

**Exit Criteria:** State remains recoverable after authority expiry, policy
exceptions cannot bypass validation, and version/schema checks are strict.

### Task 3: Bind and bound Git snapshot identity

**Purpose:** Prevent clean-clone identity collisions and unbounded snapshot
work while preserving content-based freshness.

**Task Function:** Git evidence and recovery-integrity remediation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from repository identity and I/O-risk complexity before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently validate clone identity, changed content, large files, and I/O failures.

**Specification Coverage:** Git as recovery truth; repository/worktree-bound
acceptance; graceful but fail-visible diagnostics; no recovery ledger.

**Required Skills:** `skill-code-standards`, `skill-backend-verification`.

**Files And Symbols:**
- Inspect and modify `src/general_os/git.py:GitSnapshot`,
  `GitRepository.inspect`, and `GitRepository._identity`.
- Update `docs/contracts.md` and `docs/recovery.md`.
- Verify `tests/test_git.py`, `tests/test_acceptance.py`, and recovery-contract tests.

**Dependencies:** Tasks 1–2.

**Authority:**
- Preauthorized local actions: edit Git evidence and recovery documentation/tests; run disposable local repository probes.
- Stop for: destructive checkout/reset of the user workspace, persisted runtime identifiers, or weakening current content freshness checks.

**Steps:**
- [ ] Derive canonical repository/worktree provenance from Git and include a
  stable representation in snapshot identity without exposing unnecessary path
  data in durable state.
- [ ] Hash untracked files incrementally in bounded chunks and define explicit
  behavior for unreadable files, symlinks, and I/O failures.
- [ ] Update the recovery procedure to require the complete snapshot identity,
  not only `HEAD`, when reusing evidence.
- [ ] Define recovery-time revalidation for completed tasks after checkout,
  reset, or other material Git divergence without adding a task-history ledger.

**Verification:**
- [ ] Compare two clean clones at the same branch and `HEAD`; mutate tracked
  and untracked content; probe large, unreadable, and symlinked files.
- Expected: distinct worktrees cannot share acceptance identity, content
  changes remain detectable, and snapshot work stays bounded and diagnosable.

**Exit Criteria:** `GitSnapshot.identity` is repository/worktree-bound,
content-fresh, bounded in memory, and reflected accurately in recovery docs.

### Task 4: Make Orca discovery and smoke diagnostics fail-visible

**Purpose:** Prevent invalid explicit configuration from silently selecting a
different executable and prevent failed smoke probes from looking successful to
shell callers.

**Task Function:** Optional-boundary diagnostics remediation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from optional-runtime and failure-signaling risk before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: validate unavailable, malformed, timeout, process-failure, and invalid-explicit-path cases.

**Specification Coverage:** Orca optionality; fact-derived observations;
graceful degradation without false success.

**Required Skills:** `skill-code-standards`, `skill-backend-verification`.

**Files And Symbols:**
- Inspect and modify `src/general_os/orca.py:discover_executable` and
  `OrcaCliStatusObserver.observe`.
- Inspect and modify `src/general_os/cli.py:run_orca_smoke`.
- Verify `tests/test_orca.py` and `tests/test_cli.py`.

**Dependencies:** Task 3 for shared failure and repository evidence semantics.

**Authority:**
- Preauthorized local actions: edit Orca discovery/CLI code and mocked tests; run local smoke probes without launching live workers.
- Stop for: installing/authenticating Orca, launching live workers, or making optional Orca availability a normal Codex prerequisite.

**Steps:**
- [ ] Treat a set but invalid `GENERAL_OS_ORCA_CLI` as an explicit
  configuration failure instead of falling through to PATH or derived paths.
- [ ] Preserve structured JSON diagnostics and define nonzero exit behavior
  for unavailable, failed, timeout, or malformed observations.
- [ ] Keep normal Codex execution independent of optional Orca absence.

**Verification:**
- [ ] Test valid explicit path, invalid explicit path with a PATH candidate,
  missing executable, malformed JSON, process failure, timeout, and CLI exit
  codes.
- Expected: explicit misconfiguration and probe failure are visible, while
  optional absence does not block ordinary execution.

**Exit Criteria:** Orca diagnostics are truthful to configured facts and shell
consumers cannot mistake a failed smoke probe for success.

### Task 5: Strengthen migration proof, rule ownership, and revision provenance

**Purpose:** Make the SSOT migration executable to verify and keep documentation
claims aligned with the exact reviewed revision.

**Task Function:** Migration and contract reconciliation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from migration scope and documentation ownership risk before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently check source inventory, destinations, active owners, and pinned verification records.

**Specification Coverage:** Single-source-of-truth migration; active shared
rules; no predecessor runtime dependency; historical evidence bound to SHA.

**Required Skills:** `skill-code-standards`, `skill-verification-before-completion`.

**Files And Symbols:**
- Inspect and modify `docs/migration/project-os-starter.md` and
  `tests/test_documentation_contracts.py`.
- Add one explicit owner reference in
  `.agents/skills/finishing-development-work/SKILL.md` for
  `docs/rules/publication-boundary.md`, without duplicating the rule text.
- Update `docs/contracts.md`, `docs/recovery.md`, and the historical migration
  plan only where claims are false for the reviewed SHA.
- Verify every maintained `.agents/skills/*/SKILL.md` and `docs/rules/*.md`.

**Dependencies:** Tasks 1–4.

**Authority:**
- Preauthorized local actions: edit migration/docs/tests and run offline inventory/reference probes; preserve historical source entries.
- Stop for: deleting predecessor history, editing generated adapter output instead of its canonical source, or importing a second orchestration authority.

**Steps:**
- [ ] Parse every predecessor manifest row and assert its disposition is valid,
  every migration/fold destination exists, every retire disposition has no active
  destination, and the active rule set is exactly the maintained set.
- [ ] Add an offline operator probe that compares the manifest with the pinned
  predecessor tree at `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`; keep network
  access out of unit tests.
- [ ] Scan maintained skills and docs for retired control-plane references and
  exercise the migrated executable GitHub-review runner through its existing
  bounded test surface.
- [ ] Link the publication-boundary rule from its single maintained owner and
  remove duplicated ownership claims without changing publication authority.
- [ ] Correct recovery wording to require `GitSnapshot.identity` and label
  earlier plan test counts as historical evidence rather than proof of the
  reviewed SHA.

**Verification:**
- [ ] Run manifest-to-tree, destination, active-owner, and forbidden-reference
  probes; inspect the exact plan SHA and all updated claims.
- Expected: every source surface has one explicit disposition, every active
  destination exists, shared rules have one discoverable owner, and verification
  statements identify the revision they prove.

**Exit Criteria:** Migration documentation, maintained skills, source contracts,
and tests agree on one active SSOT surface and exact revision provenance.

### Task 6: Fresh final verification and plan reconciliation

**Purpose:** Prove the integrated remediation against the final Git revision.

**Task Function:** Final verification and acceptance preparation.

**Template Profile:**
- Controller-selected: `unresolved`
- Selection basis: resolve from the complete changed-surface risk before activation.

**Validator Profile:**
- Controller-selected: `unresolved`
- Selection basis: independently confirm all task-local proof and no scope drift.

**Specification Coverage:** Fresh evidence; acceptance outside the worker; Git
truth; no unverified completion claim.

**Required Skills:** `skill-backend-verification`, `skill-verification-before-completion`.

**Files And Symbols:** All files changed by Tasks 1–5; no new owner.

**Dependencies:** Tasks 1–5.

**Authority:**
- Preauthorized local actions: run the declared test suite, state validation, inventory probes, and diff/status checks; reconcile this plan.
- Stop for: failed required proof, stale Git identity, unreviewed scope expansion, push/merge/publication, or destructive cleanup.

**Steps:**
- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m general_os state validate state/coordination.json`.
- [ ] Run the focused suites:
  `python -m pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py tests/test_policy.py tests/test_cli.py tests/test_profiles.py`.
- [ ] Run the targeted clone, expiry, mutation, scope, boundary-evidence,
  explicit-Orca-path, version-type, and large-file probes.
- [ ] Run `git diff --check` and inspect `git status --short`; preserve the
  unrelated `.serena/` entry.
- [ ] Use `skill-verification-before-completion` to reconcile every exit
  criterion before changing this plan from `proposed`.

**Verification:**
- [ ] Full and focused suites pass with fresh output.
- [ ] State validation reports `valid`.
- [ ] All targeted probes pass and the output records the final full SHA.
- [ ] No live Orca, production-load, CI, or external-service claim is made
  without separately captured evidence.

**Exit Criteria:** The implementation is ready for explicit review and Git
disposition; this plan does not authorize commit, push, merge, or publication.

## Verification

Final commands are:

```powershell
python -m pytest -q
python -m general_os state validate state/coordination.json
python -m pytest -q tests/test_documentation_contracts.py tests/test_acceptance.py tests/test_state.py tests/test_git.py tests/test_orca.py tests/test_policy.py tests/test_cli.py tests/test_profiles.py
git diff --check
git status --short --branch
git rev-parse HEAD
```

The final proof must include the exact full SHA, fresh test output, state
validation output, migration inventory results, and any documented optional
Orca non-exercise. Browser-review evidence is already complete for the source
revision and is not rerun by this implementation plan.

## Completion Criteria

The plan is ready for completion verification when:

1. acceptance cannot be completed from caller-forged assertions;
2. policy exceptions are scoped, safely expirable, and fully validated on save;
3. Git snapshot identity is repository/worktree-bound and bounded in memory;
4. recovery requires fresh snapshot evidence after Git divergence;
5. Orca diagnostics are fail-visible without becoming a normal execution gate;
6. migration destinations, active rule ownership, and historical evidence are
   executable and revision-specific;
7. every task-local proof and the final verification commands pass against the
   resulting Git revision; and
8. `skill-verification-before-completion` returns `verified` before this plan
   is marked `completed`.

No finding from an incomplete or ambiguous review run is included; both runs
for the reviewed revision were complete and visibly verified.
