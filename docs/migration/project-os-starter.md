# Project OS Starter Migration

`project-OS-starter` is a strictly read-only reference for this successor.
The migration source is commit `00b825ba95af4a44f0a33d528ea42593f3fc1dc1`;
dirty working-tree changes in that checkout are never migration input.

## Ownership

`general-os` owns the maintained semantic skills and active shared rules.
Git owns repository truth; Codex owns ordinary execution and subordinate native
children; Orca owns only independently managed worker lifecycle; `agents/*.toml`
is the only profile registry; `state/coordination.json` is the only durable
coordination state. Generated adapter trees, runtime ledgers, Herdr, Project
Secretary, and DeepAgents control-plane machinery are not migrated.

## Skill disposition

Every committed predecessor skill has one explicit disposition. Core material is
folded into existing general-os owners; specialist material is adapted under
the unprefixed target name; excluded control-plane material is retired.

| Predecessor skill | Disposition |
| --- | --- |
| `skill-backend-verification` | migrate to `.agents/skills/backend-verification/` |
| `skill-brainstorming` | migrate to `.agents/skills/brainstorming/` |
| `skill-central-config-layer` | migrate to `.agents/skills/central-config-layer/` |
| `skill-chief-of-staff` | fold into `.agents/skills/chief-of-staff/` |
| `skill-code-standards` | migrate to `.agents/skills/code-standards/` |
| `skill-creating-learning-materials` | migrate to `.agents/skills/creating-learning-materials/` |
| `skill-dashboard-reporting` | migrate to `.agents/skills/dashboard-reporting/` |
| `skill-deepagents-executing-plans` | retire; no second execution authority |
| `skill-dispatching-parallel-agents` | fold native bounded delegation into `.agents/skills/executing-work/`; retire peer scheduling |
| `skill-disposable-artifact-cleanup` | migrate to `.agents/skills/disposable-artifact-cleanup/` |
| `skill-distinctive-frontend-design` | migrate to `.agents/skills/distinctive-frontend-design/` |
| `skill-executing-plans` | fold into `.agents/skills/executing-work/` |
| `skill-finishing-a-development-branch` | migrate to `.agents/skills/finishing-development-work/` |
| `skill-frontend-component-engineering` | migrate to `.agents/skills/frontend-component-engineering/` |
| `skill-full-stack-integration` | migrate to `.agents/skills/full-stack-integration/` |
| `skill-github-browser-reviews` | migrate to `.agents/skills/github-browser-reviews/` |
| `skill-performance-optimization` | migrate to `.agents/skills/performance-optimization/` |
| `skill-plan-document-reviewer` | migrate to `.agents/skills/plan-document-reviewer/` |
| `skill-project-secretary` | retire; CoS owns durable routing |
| `skill-receiving-code-review` | migrate to `.agents/skills/receiving-code-review/` |
| `skill-refactoring-assessment` | migrate to `.agents/skills/refactoring-assessment/` |
| `skill-requesting-code-review` | migrate to `.agents/skills/requesting-code-review/` |
| `skill-reviewing-pull-requests` | migrate to `.agents/skills/reviewing-pull-requests/` |
| `skill-spec-drafting` | migrate to `.agents/skills/spec-drafting/` |
| `skill-subagent-driven-development` | fold bounded sequential child work into `.agents/skills/executing-work/`; retire peer orchestration |
| `skill-systematic-debugging` | migrate to `.agents/skills/systematic-debugging/` |
| `skill-test-driven-development` | migrate to `.agents/skills/test-driven-development/` |
| `skill-using-git-worktrees` | migrate to `.agents/skills/workspace-isolation/` |
| `skill-using-superpowers` | retire; selection remains explicit and native |
| `skill-verification-before-completion` | fold into `.agents/skills/verification-before-completion/` |
| `skill-wayfinding` | migrate to `.agents/skills/wayfinding/` |
| `skill-writing-plans` | fold into `.agents/skills/defining-work/` |
| `skill-writing-skills` | migrate to `.agents/skills/writing-skills/` |

## Rule disposition

| Predecessor rule | Disposition |
| --- | --- |
| `agent-memory-rule.md` | fold durable-memory boundary into `AGENTS.md` |
| `audit-evidence-mandate-rule.md` | fold evidence ownership into `.agents/skills/verification-before-completion/` |
| `backend-verification-rule.md` | fold semantic contract into `.agents/skills/backend-verification/` |
| `command-execution-rule.md` | fold native command safety into `AGENTS.md` |
| `doc-contracts-rule.md` | fold documentation contract checks into `.agents/skills/writing-skills/` and `tests/test_documentation_contracts.py` |
| `frontend-backend-integration-rule.md` | fold contract boundary into `.agents/skills/full-stack-integration/` |
| `frontend-ui-rule.md` | migrate shared rule to `docs/rules/frontend-ui.md` |
| `git-tracked-coordination-rule.md` | fold Git/plan ownership into `AGENTS.md` |
| `prompt-cache-contract-rule.md` | migrate shared rule to `docs/rules/prompt-cache.md` |
| `publication-boundary-rule.md` | migrate shared rule to `docs/rules/publication-boundary.md` |
| `python-contracts-rule.md` | fold Python boundary guidance into `.agents/skills/code-standards/` |

## Cutover acceptance

- No maintained skill or runtime code depends on `project-OS-starter`.
- No generated `.agents/rules/` tree, second profile registry, runtime ledger,
  scheduler, or independent Python orchestration layer exists.
- The maintained skill inventory contains the 24 specialist targets above and
  the five existing core skills; all 33 predecessor skills are accounted for.
- The three shared rules are the only new rule files; all other predecessor
  rules are folded into their owning source.
- Migration reads use `git show` or an equivalent commit-pinned materialization,
  never the dirty predecessor checkout.

## Deployment cutover

The maintained tree is the canonical source for central deployment. The
deployment command copies complete runtime-clean skill directories and shared
docs into `~/.agents/general-os/`, while `repo_config/general-os.lock.json`
records only seed provenance for an adopting project. Existing project
semantics and predecessor residue are preserved; normal checks report residue,
and `--strict-migration` is the explicit failure mode.
