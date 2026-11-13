---
layer: change
artifact_type: plan
status: complete
name: general-os-central-deployment-and-ownership
targets:
  - src/general_os/deployment.py
  - src/general_os/cli.py
  - tests/test_deployment.py
  - tests/test_cli.py
  - tests/test_documentation_contracts.py
  - docs/deployment.md
  - docs/architecture.md
  - docs/contracts.md
  - docs/recovery.md
  - docs/runtime-adapters.md
  - docs/migration/project-os-starter.md
  - README.md
  - .agents/skills/
---

# General OS Central Deployment And Ownership Plan

## Goal

Install reusable General OS implementation once per user, seed only absent
project semantics, and preserve Git, Codex, Orca, and CoS ownership boundaries.

## Outcomes

- A single `general-os deploy` command supports deterministic planning,
  read-only `--dry-run` and `--check`, safe application, explicit `--prune`,
  and optional `--strict-migration` residue failure.
- The central installation owns complete runtime-clean skill directories,
  shared rules/templates, and deployment metadata under paths derived from
  `Path.home()`; it does not create generated agent trees or runtime state.
- Staged central skills resolve shared references through the installed
  `~/.agents/general-os/docs/` tree without changing canonical source files.
- Codex activation is the shared skill discovery path. Existing project
  `AGENTS.md` files remain untouched; an absent one may be seeded with the
  minimal project guidance template.
- Central provenance owns managed-file digests. The project adoption record
  records only seed history and source revision; it does not own project-file
  drift or synchronize project profiles, policy, AGENTS guidance, or durable
  coordination state.
- Governance normalization is completed as a separate patch from deployment:
  Direct/Level 1 verification can feed authorized Git publication ephemerally,
  while task-bound durable acceptance remains for Level 2/3 work.

## Constraints / decisions

- Use the existing stdlib-only package and existing loaders. Do not add a
  scheduler, runtime/session/worker registry, second profile registry, recovery
  database, generated coordination state, or provider credential projection.
- Use current unprefixed skill names: `plan-document-reviewer`,
  `defining-work`, `central-config-layer`, `code-standards`,
  `backend-verification`, `writing-skills`, and
  `verification-before-completion`.
- Use `docs/templates/detailed-plan.md` as the durable-plan structure. This
  document is durable semantics, not a task-state ledger: it contains no
  coordination schema, executor/profile fields, progress evidence table, or
  runtime task checkboxes.
- The first adapter is `codex`. It is a central compatibility declaration and
  shared-skill activation path, not a generated `~/.codex` tree. Claude/Gemini
  projections remain future approved scope.
- Central installation copies entire runtime-clean skill directories, not only
  `SKILL.md`. Move or classify development-only material before deployment:
  `CREATION-LOG.md`, `test-academic.md`, and `test-pressure-*.md` must not stay
  inside runtime skill directories.
- The installed skill projection rewrites only staged references to shared
  paths such as `docs/rules/...` and `docs/runtime-adapters.md`; canonical
  source files remain unchanged. Relative references to files inside one skill
  directory remain intact.
- `~/.agents/general-os/managed.json` is the central managed-file lock and may
  contain `schema_version`, source, source revision, manifest digest, managed
  paths/digests, and adapter names. `repo_config/general-os.lock.json` is a
  project adoption record with `schema_version`, `adopted_from`,
  `adopted_revision`, and `seeded_paths`; it contains no ongoing project drift
  ownership or runtime facts.
- Existing project semantics are seed-only. A project file is created only
  when absent; a present file is preserved and reported. Project adoption does
  not require modifying an existing `AGENTS.md`; shared skill discovery is the
  activation mechanism.
- Normal `--check` reports predecessor residue as a warning and still checks
  deployment health. `--strict-migration` makes residue a nonzero result. No
  deployment command deletes predecessor files.
- Central updates are allowed only for unchanged files previously owned by the
  central lock or unmarked byte-identical files adopted by the lock. Conflicts
  and local modifications are preserved. Staged replacement writes provenance
  last and restores prior files if application fails.
- Do not modify `project-OS-starter`, publish, commit, or stage the unrelated
  untracked `.serena/` directory during implementation.

## Task graph

### Task A — Governance normalization

**Objective:** Apply the previously justified Direct/Level 1 closure fix and
the independent skill cleanup without coupling it to deployment behavior.

**Scope:** Maintained verification, finishing, specification, plan-review,
debugging, cleanup, review-reception, brainstorming, and learning-material
guidance plus their documentation contract assertions.

**Dependencies:** None.

**Durable sequencing:** Complete this patch before deployment implementation so
the deployment work starts from settled ownership and planning guidance.

**Acceptance:** Direct and Level 1 work has an ephemeral current-Git proof path
to explicitly authorized publication; task-bound durable acceptance remains the
only persisted completion record. The targeted cleanup terms are removed
without changing historical plans or introducing another owner.

**Verification:** Run the documentation contract tests and focused searches for
the removed social, validator-specific, and obsolete planning terms.

**Stop / escalation conditions:** Stop if the change requires a durable goal
acceptance field, another publication owner, a new runtime ledger, or a change
to the durable state schema.

### Task B — Deployment contract and runtime-clean asset boundary

**Objective:** Define the central installation, thin project kit, activation,
provenance, adapter, reference-resolution, collision, rollback, prune, and
residue contracts.

**Scope:** `docs/deployment.md`, architecture/contracts/recovery/runtime-adapter
guidance, README usage, migration exclusions, and the canonical skill tree.

**Dependencies:** Task A.

**Durable sequencing:** Classify or move development-only skill assets before
the deployer copies skill directories. Define the central and project record
semantics before implementing file mutation.

**Acceptance:** A fresh executor can identify exactly what is installed, how a
project activates the baseline, which files remain project-owned, how shared
references resolve, and which residue is warning-only versus strict failure.

**Verification:** Documentation contract tests and a source inventory prove all
runtime skill references resolve within the central installation model and no
excluded control-plane or development-only asset is part of the runtime tree.

**Stop / escalation conditions:** Stop for any proposal to deploy only
`SKILL.md`, mutate existing project semantics automatically, create generated
adapter trees, or persist runtime lifecycle facts.

### Task C — Central deployment engine

**Objective:** Implement source-driven `deploy` planning, checking, dry-run,
application, collision preservation, staged replacement, lock-last provenance,
rollback, and safe stale-file pruning using existing stdlib and loaders.

**Scope:** `src/general_os/deployment.py` and focused deployment tests. Exact
Python symbol decomposition remains an executor decision.

**Dependencies:** Task B.

**Acceptance:** Central deployment is deterministic and idempotent; complete
runtime-clean skill packages are copied; staged shared references resolve;
owned unchanged files update; identical unmarked files can be adopted;
conflicting or modified files remain untouched; `--prune` removes only owned,
unchanged central files; failed application restores prior content and lock.

**Verification:** Use temporary home/repository roots to prove first install,
repeat install, update, adoption, conflict preservation, modified-file
preservation, invalid-lock rejection, rollback, lock-last behavior, and
prune safety.

**Stop / escalation conditions:** Stop on any need for external authentication,
provider credentials, destructive deletion outside explicit `--prune`, or a
second durable authority.

### Task D — Lite project adoption

**Objective:** Add explicit one-shot project seeding and adoption provenance
without taking ownership of project semantics.

**Scope:** Project seed templates, `repo_config/general-os.lock.json`, and
deployment integration/tests.

**Dependencies:** Task C.

**Acceptance:** `general-os deploy` is central-only by default. Explicit
`--repo` adoption seeds only absent neutral `AGENTS.md`, profiles, and runtime
policy; it never seeds `state/coordination.json`. Existing versions are never
overwritten or continuously synchronized; after an adoption record exists,
project semantics—including deleted or customized seeded files—remain inert;
adoption provenance records only seeded paths and source revision; existing
AGENTS projects report shared-skill activation without requiring a file rewrite.

**Verification:** Temporary project tests cover empty adoption, partially
adopted projects, existing modified semantics, repeated adoption, malformed
adoption records, and the absence of runtime IDs or progress fields.

**Stop / escalation conditions:** Stop if project adoption needs to merge or
rewrite existing AGENTS guidance, profiles, policy, or coordination state.

### Task E — Codex adapter and CLI boundary

**Objective:** Expose the central activation and deployment behavior through
the existing `general-os` CLI while keeping Codex nearly no-op and native.

**Scope:** Existing CLI parser/handler, adapter validation, JSON report shape,
and CLI tests. Unsupported adapters fail closed.

**Dependencies:** Tasks C and D.

**Acceptance:** These commands are supported and read-only modes do not mutate:

```text
 general-os deploy --adapter codex --dry-run
 general-os deploy --repo . --adapter codex --dry-run
 general-os deploy --repo . --adapter codex
 general-os deploy --repo . --adapter codex --check
 general-os deploy --repo . --adapter codex --prune
 general-os deploy --repo . --adapter codex --strict-migration
```

The command without `--repo` is central-only. Passing `--repo` is the explicit
project-adoption opt-in.

Normal `--check` reports residue without failing solely because residue exists;
`--strict-migration` fails for residue. Reports contain deployment facts only,
not secrets, runtime IDs, or raw environment contents.

**Verification:** Focused CLI/deployment tests plus repository dry-run and
check probes prove exit codes, JSON stability, and no-write behavior.

**Stop / escalation conditions:** Stop if Codex activation requires a runtime
registry, user credential write, generated repository tree, or non-native
execution loop.

### Task F — Final verification

**Objective:** Prove the combined governance and deployment change against one
current Git revision and reconcile only durable plan semantics.

**Scope:** Source, tests, docs, skill tree, migration validator, state validator,
dry-run/check behavior, and Git diff/status.

**Dependencies:** Tasks A–E.

**Acceptance:** Full tests and validators pass; deployment tests prove the
ownership and rollback contract; the repository dry-run is read-only; no
unrelated file is staged or modified; and no required issue remains hidden in
the plan.

**Verification:** Run focused tests, the full suite, state validation, migration
manifest validation, deployment dry-run/check, `git diff --check`, and current
Git status/revision inspection. Use `verification-before-completion` for the
fresh result; use `finishing-development-work` only for a separately authorized
Git disposition.

**Stop / escalation conditions:** Stop on failed proof, stale evidence,
unexpected tracked changes, unresolved conflicts, or any attempted publication.

## Final verification

- `python -m pytest -q tests/test_deployment.py tests/test_cli.py tests/test_documentation_contracts.py`
- `python -m pytest -q`
- `python -m general_os state validate state/coordination.json`
- `python scripts/validate_migration_manifest.py --manifest docs/migration/project-os-starter.md`
- `python -m general_os deploy --repo . --adapter codex --dry-run`
- `python -m general_os deploy --repo . --adapter codex --check`
- `git diff --check`
- `git status --short --branch`
- `git rev-parse HEAD`

The plan remains `proposed` until implementation and fresh verification are
complete. It does not authorize commit, push, merge, publication, cleanup, or
changes to the architectural invariant.
