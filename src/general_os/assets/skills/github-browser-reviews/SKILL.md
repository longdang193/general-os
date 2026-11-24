---
name: github-browser-reviews
description: Use when a GitHub pull request needs browser-based inspection, review, or evidence through the supported GitHub browser flow.
---

# GitHub Browser Reviews

## Role

Use this skill only after the user explicitly invokes it by name or explicitly
requests the GitHub Browser Reviews workflow. It defines the preparation, request, and evidence
rules for a read-only review; it does not modify files, merge changes, or
replace repository ownership and branch controls.

## When to Use

Use only when the user explicitly requests this skill or workflow, for example:

- `$github-browser-reviews`;
- "Use the GitHub Browser Reviews skill";
- an equivalent explicit request naming this skill and asking for a GitHub browser-tab review.

Do not activate this skill merely because:

- a plan, code change, or pull request needs review;
- the task mentions GitHub or asks to open, review, or merge a pull request;
- the review can read a committed revision from GitHub.

Use the applicable review or pull-request skill instead when this skill was not
explicitly requested.

Do not use a local Windows path as the only review source. If the requested revision is
not available on GitHub, report `incomplete` or `blocked` instead of claiming
that the review inspected local state.

## Non-Negotiable Invariants

1. **Explicit-invocation invariant:** Do not use this skill unless the user
   explicitly requested it by name or explicitly requested its workflow.
2. **Publication invariant:** Review an exact revision already reachable from
   GitHub without mutation. If publication is needed, commit or push only
   after the owning Git disposition workflow establishes separate explicit
   authority; this review skill never grants publication authority.
3. **Revision invariant:** Give the reviewer an exact branch or commit and an
   exact file URL. The review request must include the file path or GitHub file URL.
   Pin URLs to a commit when reproducibility matters.
4. **Browser invariant:** Prefer the standalone automatic dedicated TCP-CDP
   runner as the primary execution path. It launches only the repository-bound
   Chrome profile, attaches over TCP CDP, and invokes `@GitHub` through the
   visible UI. Owned Playwright profile mode is the secondary fallback. A
   pipe-backed Playwright MCP browser has no TCP CDP endpoint; do not attempt
   to attach the standalone CLI to it. Use ChromeDev only for session
   attachment or low-level diagnostics when the primary runner cannot operate.
5. **Model invariant:** Let the user select one of `GPT-5.6-Sol`, `GPT-6`, or `GPT-6.2`.
6. **Reasoning invariant:** Let the user select `Instant`, `Medium`, or `High`
   and preserve that choice in the review request.
7. **Scope invariant:** Keep the request read-only and identify the stable
   context, repository, revision, file path, and review question.
8. **Evidence invariant:** Require the reviewer to cite a known heading, hash,
   or other file marker from the requested revision.
9. **Privacy invariant:** Do not include credentials, environment values,
   private instructions, or unrelated repository contents in the request.
10. **Rerun-authorization invariant:** Do not rerun, retry, resubmit, or open a
    replacement for a requested GitHub review unless the user explicitly orders
    that review to be rerun. An incomplete, stale, interrupted, or inconclusive
    review is not permission to start another one.

### ChatGPT Web selector semantics

ChatGPT Web exposes a `Select ChatGPT model` button. Open it to reveal model
radio items and a `Power` thinking-effort control. The effort is displayed as
`Instant`, `Medium`, or `High`; use the control's left/right keys rather than
dragging the overlapping visual thumb. Record the selected model and effort
exactly as displayed.

Use the visible selected state as the authority. Treat model selection and
thinking effort as separate controls and verify them separately. A generic
`Locked`, `Usage limit reached`, or similar banner is unscoped evidence unless
the visible UI attaches it to a specific model item or the specific effort
control. Never attribute that banner to a model merely because it appears
near the model list, and never treat it as account-wide model unavailability.

For the requested model, verify the visible radio item's checked/selected
state and inspect only the same item's visible disabled, locked, or error
state. A click timeout, pointer interception, unchanged page, or failure to
click an overlapping control does not prove that the model is locked. If the
requested model remains visibly selectable but an unscoped banner is present,
record the banner as an unscoped selector warning and continue only when the
requested model and effort are both visibly verified. If either value is not
verified, report it as unverified or incomplete rather than guessing the
cause.

## Review Procedure

### 1. Prepare the revision

Inspect the selected changes locally. If the exact revision is already
reachable from GitHub, record it and do not mutate Git. If publication is
needed, stop until the owning Git disposition workflow grants separate commit
and push authority; then record the repository, branch, commit, and file paths
used for review. The review request must identify the repository and exact
branch or commit, and the reviewed revision must be reachable from GitHub.

### 2. Select the model and reasoning level

Before opening the review, let the user choose one model and one reasoning
level. The supported choices are:

- `GPT-5.6-Sol`, `GPT-6`, or `GPT-6.2`;
- `Instant`, `Medium`, or `High` response mode.

Use the bounded page helper to select the requested visible model and effort,
then verify both visible values before submission. A failed click, pointer
interception, unchanged page, or unscoped usage banner is not proof that a
model is locked. Do not use force-click loops, hidden DOM state, repeated
resubmissions, or automatic retries; stop as `incomplete` or `blocked` when
visible verification cannot be completed.

For repeatable browser automation, use the page-bound helper at
`scripts/select-review-model.mjs`:

```js
import { selectReviewModel } from "./scripts/select-review-model.mjs";

await selectReviewModel(page, {
  model: "GPT-6",
  effort: "High"
});
```

The helper accepts an existing authenticated Playwright `page`; it does not
launch a browser, authenticate, submit a review, inspect hidden state, or retry
indefinitely. If it cannot visibly confirm the requested model and effort, stop
the review as `incomplete` or `blocked`.

The helper owns the bounded navigation between the model and effort controls,
uses real Playwright hit-testing, and verifies the visible selected state. Keep
model labels separate from nearby status or usage-banner text.

For an explicitly authorized end-to-end prompt submission, use
`scripts/run-review-prompt.mjs`. It navigates an existing authenticated page
to ChatGPT, selects and verifies the model and effort, fills the prompt, and
submits it once. `openReviewTab(context)` and
`runReviewPromptInNewTab(context, options)` can create or reuse a review page
from an existing authenticated Playwright context; they do not launch a browser or
authenticate. The submission helper never retries or reruns a review request;
the completion helper only observes visible completion signals and returns the
  final visible assistant turn for the caller to record. When
  `existingConversationUrl` is supplied, the helper opens that conversation
  in the supplied/reused review page and runs the read-only observer instead; it never calls the
  submission path.

### Helper execution boundary

These `.mjs` helpers run in the Node/Playwright runner, not in the ChatGPT page
context. Do not import them from `page.evaluate` or another inline browser
snippet; page evaluation cannot resolve workspace modules. Load them through
the runner's file-backed entry point instead:

```js
import { runReviewPromptInNewTab } from "./.agents/skills/github-browser-reviews/scripts/run-review-prompt.mjs";

const { page } = await runReviewPromptInNewTab(context, {
  model: "GPT-6",
  effort: "High",
  prompt: reviewPrompt
});
```

The runner must either launch the dedicated project profile directly with
visible Chrome, launch it over TCP CDP, or receive an already authenticated
Playwright `context`. The CLI's `--launch-cdp` mode launches Chrome with the
repository-bound profile and attaches to its endpoint. The CLI's
`--user-data-dir` mode launches the installed Chrome executable directly with
Playwright and does not use TCP CDP. Use one dedicated project profile such as
`~/.codex/profiles/github-review/<project>` and never the normal Chrome `User
Data` directory. The library helpers and `--cdp-endpoint` mode require the
caller to provide an existing context or endpoint.
Use a browser tool's `filename` or `sourcePath` option only when it supports
file-backed Node execution. If the helper cannot be loaded or the authenticated
context cannot be created or attached, report `incomplete` or `blocked`; do not
replace the helper with hidden DOM or network-state inspection. Prompt submission remains gated by the explicit user authorization required by this
skill.

For a standalone, repeatable Node invocation, use the ESM CLI entrypoint rather
than evaluating the `.mjs` module as a browser VM script. The primary mode
launches visible Chrome with TCP CDP and a dedicated authenticated profile:

```bash
node .agents/skills/github-browser-reviews/scripts/run-review-prompt-cli.mjs \
  --launch-cdp \
  --user-data-dir ~/.codex/profiles/github-review/<project> \
  --project-key <owner-repository> \
  --model GPT-6 \
  --effort High \
  --prompt-file <review-prompt.txt> \
  --repository <owner/repository> \
  --commit-sha <full-40-character-sha> \
  --review-url https://github.com/<owner>/<repo>/blob/<full-sha>/<path> \
  --output-dir <review-output-directory>
```

One normal invocation is one bounded review transaction. Single-review mode
requires `--repository`, `--commit-sha`, and at least one repeatable
`--review-url`. Every declared URL must be an HTTPS GitHub `/blob/` URL pinned
to the same full SHA and repository, and every GitHub blob URL in the prompt
must match that declared set. The CLI rejects unknown flags, missing
provenance, and invalid/default profile paths before browser setup.

For read-only verification of an already completed review, add
`--existing-conversation-url https://chatgpt.com/c/<id>`. The runner navigates
only to that conversation, observes the stable visible response, and never
selects a model, fills a prompt, or submits a message. Its result records
`submission: "not_attempted"` and keeps the supplied conversation URL in
request provenance. Batch entries may use the equivalent
`existing_conversation_url` field.

The owned profile must end in the canonical, case-normalized project key
derived from the repository (`owner-repository`), and `--project-key` must
match that derived value. Use one dedicated profile per project, for example
`~/.codex/profiles/github-review/owner-repository`; never use the
normal Chrome `User Data` directory. This same repository/profile binding is
checked by direct library callers, not only by CLI parsing. Profile validation,
lease naming, and persistent-browser launch use the same physical filesystem
identity; existing symlink/junction aliases and aliases through the nearest
existing parent do not create a second lease identity.
The runner records the canonical repository and project key in
`.codex-review-profile.json` inside a newly created or empty dedicated profile.
An existing profile without that marker is treated as ambiguous and blocks with
operator-directed migration instructions; the runner never copies credentials,
renames profiles, or silently binds a legacy directory. A marker for another
repository also blocks, which prevents collisions such as `foo-bar/baz` and
`foo/bar-baz` from sharing one profile.

When the derived profile path does not exist, create the directory and verify
that it is empty before launching the runner. The runner may then create
`.codex-review-profile.json` with the repository and project-key binding. If
the path exists and is non-empty without a matching marker, stop as `blocked`;
do not delete contents, clear cookies, copy credentials, or adopt the profile
implicitly.

The runner performs one non-submitting visible authentication preflight for the
owned context. It reuses the bootstrap ChatGPT tab instead of opening a
temporary second tab. An explicit login wall blocks the
batch before review pages are opened. It selects and visibly verifies the requested model and effort,
submits at most once, waits for a new stable visible assistant turn, checkpoints
interim text to `response.partial.md`, writes the complete final answer to
`response.md`, and writes a small `result.json` before it closes the owned browser
context. While the response is visibly generating, completion observation polls
cheap visible state and defers full assistant-text extraction until generation
stops and stability can be checked.

After dispatch, the runner checkpoints the current conversation URL, ID,
assistant message, and response text while the page is still available. Only
identity-accepted snapshots become checkpoints; rejected route/conversation
snapshots remain diagnostic-only. If the page or context closes during cleanup,
the final result uses that last durable checkpoint instead of querying the
closed page. `response.partial.md` is checkpoint evidence only; `response.md` is
written after structural final-response observation, even when review-content
evidence is still unconfirmed. A complete `response.md` does not prove that
revision evidence was accepted; `result.json` remains the lifecycle authority. Current visible completion markers include `Response complete` and
`Feedback`. When those controls are unavailable, repeated stable assistant
text can confirm completion after the new-turn, identity, interruption,
submitted-turn, and composer-readiness checks pass. If structural completion is observed but revision evidence is
rejected, the bounded observer carries `content_evidence_unconfirmed: true`
into the terminal `result.json` and settles the transaction as `incomplete`
with a specific reason rather than a generic association timeout.

Submitted-review completion evidence stays bound to the same review page,
requires a new stable assistant turn, and must remain continuous with the
submitted user turn. Read-only existing-conversation
verification instead requires a stable current assistant turn. Conversation
identity is a continuity signal rather
than an immutable SPA invariant: the runner tolerates route transitions before
response evidence appears, then binds the conversation identity when the new
response is first observed. A later transition, missing new turn, interruption,
or unstable response returns `incomplete`. If the baseline conversation is
unknown, the first post-dispatch conversation identity is bound. An ambiguous send
acknowledgement uses a short bounded observation window, preserves
`possibly_dispatched`, and never resubmits; confirmed or visibly active
generations retain the normal completion window.

Terminal runner results are `completed`, `incomplete`, or `blocked`; a failed
owned-context cleanup preserves the review artifacts but makes the invocation
nonzero and records the cleanup failure. Internal dispatch states distinguish
`not_dispatched`, `possibly_dispatched`, and `acknowledged`: once the send
action begins, an uncertain click or Enter failure is never retried and is
treated as possibly dispatched until visible acknowledgement proves otherwise.
Only a definitely pre-dispatch failure skips the long completion observer. A
visible terminal interruption returns immediately with partial evidence. If the
final result artifact cannot be persisted, the runner reports `incomplete` and
returns nonzero even when the response itself completed. A technically complete
  response must cite the requested full SHA or a pinned file marker and contain
  a review outcome (for example, a no-findings conclusion or structured
  findings). Missing revision evidence records `incomplete` but does not discard
  a structurally final response from `response.md`; planning-only text remains
  incomplete until structural completion is observed. The controller still owns
  the final `verified` classification. The runner never retries or silently recovers a failed
submission. In a sequential batch, a confirmed response that only lacks
revision text evidence may proceed to the next model when dispatch was
acknowledged and cleanup completed without warning; that review remains
`incomplete` and is not treated as `verified`.

For a multi-model review driven by a Node controller, validate the complete
review list against one repository-derived project key before opening the
browser. Then keep the same transaction boundary: call the CLI module's
`openReviewContext(options)` once, and call
`runReviewBatch({ attached, reviews, outputDir, projectKey, repository })` from
the Node controller. The Node controller must supply validated `projectKey` and
`repository`; the attached browser context cannot establish repository identity
safely. The standalone CLI validates each review's repository, full commit SHA,
and pinned URLs. The standalone CLI derives the project key from each validated
review's repository provenance. In standalone CLI mode, pass the canonical `--project-key` whenever using `--user-data-dir` (with or without `--launch-cdp`); omit it only when attaching through `--cdp-endpoint`. The CLI reserves that flag for owned-profile mode.
The standalone CLI also
accepts a manifest:

```json
{
  "reviews": [
    {
      "model": "GPT-5.6-Sol",
      "effort": "High",
      "prompt_file": "review-sol.txt",
      "repository": "<owner>/<repo>",
      "commit_sha": "<full-40-character-sha>",
      "review_urls": ["https://github.com/<owner>/<repo>/blob/<full-sha>/<path>"]
    },
    {
      "model": "GPT-6",
      "effort": "High",
      "prompt_file": "review-gpt6.txt",
      "repository": "<owner>/<repo>",
      "commit_sha": "<full-40-character-sha>",
      "review_urls": ["https://github.com/<owner>/<repo>/blob/<full-sha>/<path>"]
    }
  ]
}
```

Pass it as `--batch-file <reviews.json>` instead of the single-review flags.
For the two-model batch described here, process the manifest in this exact order:

1. Open one fresh tab in the already authenticated context, select
   `GPT-5.6-Sol` at `High`, submit once, wait for its terminal result, and close
   that tab.
2. Only after step 1 settles, open one different fresh tab in the same
   authenticated context, select the requested second model (`GPT-6` or
   `GPT-6.2`) at `High`, submit once, wait for its terminal result, and close
   that tab.

Do not open both review tabs in advance, run the reviews concurrently, reuse the
first review tab, or switch profiles or browser contexts between models.
The runner validates every entry before opening the browser, reuses one
  authenticated context for strictly sequential review-page transactions:
  settle the first review before starting the next, open exactly one fresh tab
  for each model, close that review tab before opening the next, and never run
  the model reviews concurrently or reuse a prior review tab. The shared
  authenticated browser context remains open across the sequence. Allocate a
  separate `run-*` directory per review, persist response and result artifacts
  before page cleanup, close the shared context once through the batch owner,
  print a JSON summary, and return nonzero if any review is not `completed` or
  the shared context cannot be closed. Repeated reviews with the same model use
  the same authenticated context; persistent-profile mode holds an exclusive
  profile lease for the lifetime of the owned context, so overlapping launches
  fail before opening a second browser. Malformed, live, stale, or ambiguous
 ownership stays blocked for operator-confirmed recovery; the runner never
 deletes a stale lock based only on a PID, timestamp, or profile path, and
  release removes only the current lease token. Normal SIGINT/SIGTERM cleanup
 makes a best-effort release when ownership remains provable. Selection and page-local failures carry an explicit scope. A clean,
 definitely pre-dispatch review-scoped failure may let the batch continue to
 the next already-authorized model; a closed/disconnected page or browser,
 missing or unknown dispatch evidence, or any cleanup warning stops the shared
 batch. A missing or transient model option is not proof of unavailability,
 and the failed review is never silently switched to another model.
 A confirmed response that only lacks revision-evidence validation may proceed
 to the next already-authorized model when dispatch is acknowledged and cleanup
 is clean; it remains `incomplete` and is never resubmitted. The failed review
 is never silently switched to another model. Do not add a keep-open flag
 or a second browser lifecycle owner. A newly created tab that does not reach the
composer readiness state is page-local and review-scoped; failure to create a
 page or loss of the shared browser context remains shared-context scoped. If a
 send acknowledgement is ambiguous, preserve the owned page and any visible
 conversation/completion evidence before cleanup. A read-only existing-conversation
 verification that remains incomplete stops the batch: `not_dispatched` means
 that invocation sent nothing, not that the existing conversation is settled.
 If that evidence confirms a new stable response, promote the transaction to the normal acknowledged,
 completed state; otherwise mark `submission` as `ambiguous`. Never send the
 prompt again. Batch summaries include requested,
transaction-started, submission-attempted, acknowledged, completed, failed, and
skipped entries. `attempted_count` means a review transaction allocated its run
and started; it does not count a partially allocated review that never reached
dispatch. Each result retains sanitized prompt hash, repository, full commit
SHA, and pinned review URL provenance.
  A failure writing the aggregate `batch-result.json` is recorded as an
  artifact-stage incomplete result without rewriting already-settled per-review
  artifacts.
  Batch validation completes before browser setup, so a malformed entry cannot
  consume a profile lease or open a partial batch. If run-directory allocation
  fails partway through a batch, every created run is finalized as blocked with
  `dispatch_state: not_dispatched` and the batch stops before browser setup. If
  an explicit CDP endpoint
  exposes multiple browser contexts, `--context-index` is required; the runner
  never silently chooses context `0`.
  Launch-owned TCP-CDP mode waits for exactly one bootstrap page; zero pages
  time out and multiple pages fail closed as ambiguous instead of opening a
  second review tab.

Model-menu interaction uses a five-second UI action/transition timeout. Initial
model-menu opening remains ten seconds, completion observation remains bounded
by its separate long timeout, and polling backoff values are not changed to
compensate for slow clicks.

An ambiguous dispatch starts with the short acknowledgement/evidence window.
Once generation, a new assistant turn, or equivalent response controls are
visible, completion observation promotes to the normal long deadline without
resubmitting. A review is not durably marked `completed` until its owned page
cleanup and final result persistence succeed; if final persistence fails, the
last durable checkpoint remains non-terminal and the returned result is
`incomplete`.

When a TCP CDP endpoint is explicitly available, `--cdp-endpoint` remains an
exceptional attach mode and `--context-index` selects its browser context. The
normal personal submission path uses the dedicated project profile instead.
Before attaching, verify the endpoint and its targets explicitly:

```powershell
$cdpPort = 9222  # Example only; replace with an available explicit TCP port.
Invoke-RestMethod "http://localhost:$cdpPort/json/version"
Invoke-RestMethod "http://localhost:$cdpPort/json/list"
```

`/json/list` confirms the endpoint's tabs/targets; it is not a browser-context
index. Do not assume `--context-index 0`: use `0` only after verifying that the
endpoint exposes exactly one browser context, otherwise identify the intended
context and pass its actual index. The runner requires an explicit index when
multiple contexts are exposed. Do not launch a second Chrome process against
the same profile. Close the owned-profile process before the manual CDP launch,
or reuse the already-running process only when it was launched with the
verified endpoint.
CLI imports `run-review-prompt.mjs` through Node's ESM loader and submits
exactly once. It never authenticates
a profile for the user. A pipe-backed Playwright MCP browser cannot be used
with `--cdp-endpoint`; use the owned-profile mode or MCP directly.
`browser_run_code_unsafe` is not an ESM module runner; do not pass this CLI or
either `.mjs` helper to that VM as a raw file.

### Cloudflare or human-verification handoff

If the automatic dedicated TCP-CDP attempt encounters a Cloudflare or
human-verification loop, an HTML challenge page, or a pre-submission
`Invalid content type: text/html` diagnostic, stop the attempt. Do not retry,
refresh, resubmit, clear cookies or site data, switch profiles, use Incognito,
or solve/bypass a CAPTCHA. The runner records challenge evidence (including
page title and challenge iframe URLs) and fails before any refresh or submit
attempt when that evidence is visible.

Use the no-CDP recovery below only as an operator handoff. Completing the
challenge in ordinary Chrome does not turn that browser into a runner session:
the CLI's direct `--user-data-dir` mode still launches a Playwright-controlled
persistent context without TCP CDP, and Cloudflare may assess that automated
context differently. Manual clearance may carry over through the profile's
cookies, but it is not guaranteed and is not a bypass. If the challenge returns
in the runner, report `blocked` or `incomplete`; do not keep retrying.

After manual recovery, explicitly confirm `logged in` and the normal composer,
then verify the exact profile path, repository/profile binding, requested model,
and reasoning effort. A `logged in` message or visible composer alone is
insufficient: the requested model and effort must be visibly confirmed,
separately, before submission.

#### No-CDP recovery

Prefer the direct visible-Chrome path when Cloudflare or Turnstile blocks the
TCP-CDP attempt. Stop the runner, close any Chrome process using the dedicated
profile, and launch the same profile without remote-debugging flags:

```powershell
$projectKey = "<owner-repository>"
$profile = "$env:USERPROFILE\.codex\profiles\github-review\$projectKey"

& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" `
  "--user-data-dir=$profile" `
  "https://chatgpt.com/"
```

Complete the human-verification check there and wait until the normal composer
is visible. Close that Chrome window before restarting the review with the same
review arguments, using `--user-data-dir $profile --project-key $projectKey` and
omitting both `--launch-cdp` and `--cdp-endpoint`. This is a bounded
pre-dispatch recovery attempt, not ordinary-Chrome control: the runner must
still acquire the profile lease and launch its own visible Playwright context,
and it must not run concurrently with another process using the same profile.
If the challenge loops in ordinary Chrome or returns in the runner, return
`blocked` or `incomplete` rather than retrying automatically.

Cloudflare documents that Turnstile and challenge behavior depends on browser,
network, and client-side signals; keep the dedicated profile on a stable,
non-VPN/non-proxy connection, allow JavaScript and cookies, and remove only
known extensions that interfere with challenge scripts. Do not repeatedly
reload or submit automated attempts to force a challenge through. These
operational mitigations reduce session churn but cannot guarantee acceptance.
Reference: <https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/> and
<https://developers.cloudflare.com/turnstile/troubleshooting/testing/>.

#### Manual CDP recovery

If automatic launch fails, an operator may start the same derived dedicated
Chrome profile directly and attach through TCP CDP. Never reuse the normal
Chrome `User Data` directory or a different repository's profile. Use this
only after the automatic path fails and never attach to an unknown endpoint:

```powershell
$ownerRepo = "<owner>/<repo>"
$projectKey = $ownerRepo.ToLowerInvariant().Replace("/", "-")
$profile = "$env:USERPROFILE\.codex\profiles\github-review\$projectKey"

& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" `
  --user-data-dir="$profile" `
  --remote-debugging-port=0 `
  --remote-debugging-address=127.0.0.1 `
  https://chatgpt.com/
```

Read the profile-owned port and verify the same endpoint that will be passed to
the CLI before attaching:

```powershell
$port = [int](Get-Content "$profile\DevToolsActivePort" | Select-Object -First 1)
$endpoint = "http://127.0.0.1:$port"
Invoke-RestMethod "$endpoint/json/version"
Invoke-RestMethod "$endpoint/json/list"
```

Then use `--cdp-endpoint $endpoint` with the normal repository, full-SHA, and
pinned-URL provenance arguments. Do not replace the profile-owned endpoint with
another loopback address based only on a successful CDP response: a fixed-port
collision can expose an unrelated browser. This is an operator-owned fallback,
not a second normal browser lifecycle owner; do not use it for a pipe-backed
Playwright MCP browser.

### 3. Open the review

Run the automatic dedicated TCP-CDP path first to launch or control an
authenticated ChatGPT Web tab and invoke `@GitHub` through the visible UI. Use
owned Playwright profile mode only as the secondary fallback. If neither path
can create or use the required session, report `incomplete` or `blocked`; use
ChromeDev only for low-level diagnostics. Keep the browser request compact and
provide only the exact revision, read-only scope, stable context identifier,
and one review question.
Use visible page state as the authority for model, response mode, completion,
and interruption status; do not infer these from hidden DOM or transport
metadata.

Use this shape, with every GitHub URL pinned to the expected full commit SHA:

```text
@GitHub Review this exact file revision:
https://github.com/<owner>/<repo>/blob/<full-sha>/<path>

Scope: read-only review of the selected revision.
Context: <stable review or work-item identifier>
Model: <GPT-5.6-Sol|GPT-6|GPT-6.2>
Reasoning: <instant|medium|high>
Plan/source: <exact plan file and/or commit-pinned GitHub URL>
Question: <one precise review question>

Return findings ordered by severity and do not modify files.
```

### 4. Keep the request bounded

Keep the browser-tab request compact and provide only the exact revision,
read-only scope, stable context identifier, and one review question.

Do not refer to an "above plan" without naming the exact plan file and its
commit-pinned GitHub URL. Do not paste the current chat transcript, system or developer instructions,
tool schemas, environment blocks, attachments, or transport wrappers. Do not
include credentials. Do not include unrelated repository contents. Those are
outer execution context, not review input. If the request is too large, rebuild it
with the exact GitHub URL and the smallest sufficient scope; do not blindly
retry a bloated request.

### 5. Verify review evidence

The reviewer should confirm that it read the requested revision by citing a
known heading, hash, file marker, or equivalent evidence before the review is
accepted. The runner records the completed response and conversation identity;
the caller remains responsible for judging file-specific review evidence.
The runner only treats provisional language as a failure when it describes
review state or an explicit future action; a finding about the reviewed subject
(for example, that it is not yet suitable for production) does not invalidate
revision evidence by itself.

### 6. Handle unavailable revisions

Report `incomplete` or `blocked` when:

- the selected changes cannot be committed and pushed;
- the repository or revision is inaccessible to the reviewer;
- the review requires uncommitted local state;
- the reviewer cannot confirm the requested revision.

State the exact missing condition and do not substitute a local-only claim.

### 7. Rerun only on explicit order

If the review is incomplete, interrupted, stale, inconclusive, or otherwise
missing required evidence, stop and report the exact condition. Do not
automatically rerun it, retry the same request, submit a replacement request,
or open another browser review. A sequential batch may still start a different
model that was already authorized when the prior transaction is safely settled
and the batch policy allows continuation. Continue only after the user
explicitly orders a rerun of the same review; a general request to continue,
fix, review, or implement is not sufficient unless it explicitly authorizes the
rerun.

## Evidence Checklist

Before reporting success, record:

- repository, intended branch, and exact commit;
- successful push evidence and the reviewed file URL;
- read-only scope, stable context identifier, and review question;
- the heading, hash, or file marker cited by the reviewer;
- findings ordered by severity;
- any skipped checks or unavailable review evidence.

## Completion Result

Return one of:

- **verified:** the intended GitHub revision was pushed, read, and evidenced;
- **incomplete:** the review or evidence remains unfinished within scope;
- **blocked:** access, publication, or revision evidence requires an external
  action or user decision.

State the exact failed claim and evidence for `incomplete` or `blocked`.
