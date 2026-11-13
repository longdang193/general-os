# Deployment

`general-os deploy` installs the reusable runtime surface once per user and
performs seed-only project adoption. The command is stdlib-only and supports
the Codex adapter. Git remains the source of repository state and recovery
truth.

## Central installation

The central installation lives at `~/.agents/general-os/` and contains:

- complete runtime-clean skill directories under `skills/`;
- shared rules and templates under `docs/`; and
- `managed.json`, the central provenance lock.

Skill references to repository-relative shared docs are rewritten in the
installed copy to the central `docs/` tree. Canonical repository sources are
never rewritten. The central lock stores source revision, manifest digest, and
the last centrally managed digest for each installed file.

An unchanged centrally managed file may be updated. A locally modified or
unowned file is preserved. A byte-identical unowned file may be adopted. The
lock is written last; failed application restores all files changed by that
attempt.

## Project adoption

The project receives `repo_config/general-os.lock.json` as seed provenance.
Only absent `AGENTS.md`, profiles, runtime policy, and coordination state are
seeded. Existing project files are preserved and are never synchronized by the
deployment command. The adoption record contains only its schema, source,
source revision, and seeded paths; it contains no runtime IDs, progress, or
project drift digests.

Existing `AGENTS.md` projects activate through shared skill discovery and do
not need an in-place rewrite. The Codex adapter does not generate a `~/.codex`
tree or a second runtime registry.

## Commands

```text
general-os deploy --adapter codex --dry-run
general-os deploy --repo . --adapter codex --dry-run
general-os deploy --repo . --adapter codex
general-os deploy --repo . --adapter codex --check
general-os deploy --repo . --adapter codex --prune
general-os deploy --repo . --adapter codex --strict-migration
```

`--dry-run` plans without writing. `--check` reports drift and returns
nonzero when deployment is not healthy. `--prune` removes only unchanged files
still owned by the central lock. Predecessor residue is report-only during a
normal check; `--strict-migration` makes it a nonzero result. Deployment never
deletes predecessor residue.
