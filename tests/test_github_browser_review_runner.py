import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).parents[1]
RUNNER = ROOT / "src/general_os/assets/skills/github-browser-reviews/scripts/run-review-prompt.mjs"
CLI_RUNNER = ROOT / "src/general_os/assets/skills/github-browser-reviews/scripts/run-review-prompt-cli.mjs"


def run_node_assertion(source: str) -> None:
    node = shutil.which("node")
    assert node, "Node.js is required for the GitHub browser review runner tests"
    result = subprocess.run(
        [node, "--input-type=module", "-e", source],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_stable_new_assistant_turn_confirms_without_transient_ui_signal():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-2",
  assistantText: "## Review\\n\\nNo findings.",
  assistantTurnCount: 2,
  baselineAssistantTurnCount: 1,
  composerReady: true,
  conversationId: "conversation-2",
  expectedConversationId: "conversation-2",
  generationObserved: false,
  generating: false,
  interrupted: false,
  responseActionsReady: false,
  stableSampleCount: 2,
  allowStableTextFallback: true,
}}), true);
'''
    )


def test_completion_still_requires_a_new_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-1",
  assistantText: "Older response.",
  assistantTurnCount: 1,
  baselineAssistantTurnCount: 1,
  composerReady: true,
  conversationId: "conversation-1",
  expectedConversationId: "conversation-1",
  generationObserved: false,
  generating: false,
  interrupted: false,
  responseActionsReady: false,
  stableSampleCount: 2,
}}), false);
'''
    )


def test_completion_waits_for_accepted_review_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("data-response-body")
        ? callback([{{ innerText: "I will inspect the pinned files and report findings.", getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}], includeText)
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: () => null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole(role) {{
    return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
let acceptanceChecks = 0;
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
  acceptSnapshot: () => {{ acceptanceChecks += 1; return false; }},
}});
assert.equal(result.status, "incomplete");
assert.ok(acceptanceChecks > 0);
'''
    )


def test_planning_only_response_does_not_count_as_review_completion():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ hasRevisionEvidence }} from {CLI_RUNNER.as_uri()!r};

const provenance = {{
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
}};
assert.equal(hasRevisionEvidence("I will inspect the pull request and report findings.", provenance), false);
assert.equal(hasRevisionEvidence("I will inspect commit 0123456789abcdef0123456789abcdef01234567 and report findings.", provenance), false);
assert.equal(hasRevisionEvidence("I will inspect file.md and report findings.", provenance), false);
assert.equal(hasRevisionEvidence("I will review https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md.", provenance), false);
assert.equal(hasRevisionEvidence("Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", provenance), true);
assert.equal(hasRevisionEvidence("Reviewed file.md; no findings.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n## Summary\\nI will inspect file.md next.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings yet; I will inspect file.md next.", provenance), false);
assert.equal(hasRevisionEvidence("https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md\\nSeverity: pending until I inspect it.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nSeverity: High; reviewed the pinned file.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n1. High — reviewed the pinned file.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nSeverity: High\\nI will inspect the pinned file and report findings next.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nCould not access the pinned file; this review is not approved yet.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nI don't have access to the pinned file, so I found no issues.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nI will report no findings if the review is clean.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nSeverity: High if the suspected issue is confirmed; I will inspect it next.", provenance), false);
'''
    )


def test_completion_accepts_terminal_response_marker_without_composer_visibility():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-new",
  assistantText: "Reviewed the pinned revision; no findings.",
  assistantTurnCount: 1,
  baselineAssistantTurnCount: 0,
  composerReady: false,
  conversationId: "review",
  expectedConversationId: "review",
  generationObserved: true,
  generating: false,
  interrupted: false,
  responseActionsReady: true,
  stableSampleCount: 2,
  submittedTurnObserved: true,
}}), true);
'''
    )


def test_completion_accepts_terminal_response_marker_before_two_stable_samples():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-new",
  assistantText: "Reviewed the pinned revision; findings follow.",
  assistantTurnCount: 1,
  baselineAssistantTurnCount: 0,
  composerReady: true,
  conversationId: "review",
  expectedConversationId: "review",
  generationObserved: true,
  generating: false,
  interrupted: false,
  responseActionsReady: true,
  stableSampleCount: 1,
  submittedTurnObserved: true,
}}), true);
'''
    )


def test_existing_conversation_interruption_returns_without_waiting_for_timeout():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/existing",
  waitForTimeout: async () => {{ throw new Error("should not wait"); }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") ? 1 : 0,
      isVisible: async () => selector.includes("conversation-turn-error"),
      innerText: async () => "Response interrupted",
      evaluateAll: async (callback) => selector.includes("data-message-author-role=assistant")
        ? callback([{{ innerText: "Partial response", getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null }}])
        : callback([]),
    }};
  }},
  getByRole: () => ({{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => false }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForExistingReviewCompletion(page, {{ conversationUrl: "https://chatgpt.com/c/existing", timeoutMs: 900000 }});
assert.equal(result.status, "interrupted");
assert.equal(result.checkpointAccepted, true);
'''
    )


def test_preflight_reuses_launch_owned_review_page_without_opening_second_tab():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ preflightAuthenticatedContext }} from {RUNNER.as_uri()!r};

const page = {{
  closeCount: 0,
  close: async () => {{ page.closeCount += 1; }},
  url: () => "https://chatgpt.com/",
  getByRole: () => ({{
    first() {{ return this; }},
    waitFor: async () => {{}},
    isVisible: async () => true,
  }}),
}};
const context = {{
  newPage: async () => {{ throw new Error("unexpected second tab"); }},
}};
await preflightAuthenticatedContext(context, page);
assert.equal(page.closeCount, 0);
'''
    )


def test_owned_profile_context_reuses_bootstrap_page_for_review():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ openContext, closeContext }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-profile-"));
const profile = join(root, "github-review", "owner-repo");
const page = {{}};
const context = {{ pages: () => [page], close: async () => {{}} }};
const chromium = {{
  launchPersistentContext: async () => context,
}};
const attached = await openContext(chromium, {{
  userDataDir: profile,
  projectKey: "owner-repo",
  repository: "owner/repo",
}});
assert.equal(attached.reviewPage, page);
await closeContext(attached);
'''
    )


def test_attached_cdp_context_does_not_adopt_existing_pages():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ openContext }} from {CLI_RUNNER.as_uri()!r};

const context = {{ pages: () => [{{}}, {{}}] }};
const browser = {{ contexts: () => [context] }};
const chromium = {{ connectOverCDP: async () => browser }};
const attached = await openContext(chromium, {{
  cdpEndpoint: "http://127.0.0.1:9222",
  contextIndex: 0,
  contextIndexProvided: true,
}});
assert.equal(attached.reviewPage, undefined);
'''
    )


def test_existing_conversation_aliases_reject_empty_or_conflicting_values():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ validateReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const base = {{
  model: "GPT-6",
  effort: "High",
  prompt: "Review https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
}};
assert.throws(() => validateReviewBatch([{{ ...base, existing_conversation_url: "" }}], {{ projectKey: "owner-repo" }}), /non-empty/);
assert.throws(() => validateReviewBatch([{{ ...base, existing_conversation_url: "https://chatgpt.com/c/one", existingConversationUrl: "https://chatgpt.com/c/two" }}], {{ projectKey: "owner-repo" }}), /conflicting/);
'''
    )


def test_conversation_identity_normalizes_encoded_route_segments():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ normalizeExistingConversationUrl, waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(
  normalizeExistingConversationUrl("https://chatgpt.com/c/local-chatgpt%3Aabc"),
  "https://chatgpt.com/c/local-chatgpt%3Aabc",
);

const page = {{
  url: () => "https://chatgpt.com/c/local-chatgpt:abc",
  waitForTimeout: async () => {{}},
  locator: () => ({{
    first() {{ return this; }},
    last() {{ return this; }},
    count: async () => 1,
    isVisible: async () => false,
    evaluateAll: async (callback, includeText) => callback([
      {{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null }},
    ], includeText),
  }}),
  getByRole: (role) => ({{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => true }}),
}};
const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/local-chatgpt%3Aabc",
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "local-chatgpt:abc");
'''
    )


def test_direct_library_read_only_values_are_validated_before_browser_interaction():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewPromptInNewTab }} from {RUNNER.as_uri()!r};
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

let newPageCalls = 0;
const context = {{ newPage: async () => {{ newPageCalls += 1; throw new Error("browser interaction should not start"); }} }};
for (const existingConversationUrl of ["", null, "https://example.com/c/not-chatgpt"]) {{
  await assert.rejects(
    runReviewPromptInNewTab(context, {{ existingConversationUrl }}),
    /existing conversation URL/i,
  );
}}
assert.equal(newPageCalls, 0);
await assert.rejects(
  runReviewTransaction({{}}, {{ existingConversationUrl: "" }}),
  /existing conversation URL/i,
);
'''
    )


def test_completion_requires_continuity_with_submitted_user_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/unrelated",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("data-message-author-role=assistant")
        ? callback([{{ innerText: "Older", getAttribute: (name) => name === "data-message-id" ? "old" : null }}, {{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "new" : null }}], includeText)
        : callback([], includeText),
    }};
  }},
  getByRole(role) {{
    return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "old", assistantTurnCount: 1, conversationId: null, submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /association|submitted user turn/i);
'''
    )


def test_submitted_user_turn_id_is_polled_through_spa_route_transition():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ readSubmittedUserTurnId }} from {RUNNER.as_uri()!r};

let reads = 0;
const page = {{
  locator: () => ({{
    evaluateAll: async (callback) => callback(reads++ === 0
      ? [{{ innerText: "Review the pinned change.", getAttribute: () => null }}]
      : [{{ innerText: "Review the pinned change.", getAttribute: (name) => name === "data-message-id" ? "submitted-user" : null }}]),
  }}),
  waitForTimeout: async () => {{}},
}};

assert.equal(await readSubmittedUserTurnId(page, "Review the pinned change.", {{ timeoutMs: 50 }}), "submitted-user");
assert.equal(reads, 2);
'''
    )


def test_completion_rejects_stale_same_prompt_conversation():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/stale",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("data-message-author-role=assistant")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }}], includeText)
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: (name) => name === "data-message-id" ? "user-old" : null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-base", assistantTurnCount: 1, conversationId: null, submittedPrompt: "Review the pinned change.", submittedUserTurnId: "user-new" }},
  timeoutMs: 20,
}});
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /association|submitted user turn/i);
'''
    )


def test_completion_allows_normal_route_handoff_after_new_turn_anchor_is_visible():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/new-route",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("assistant")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-new" : null }}], includeText)
          : selector.includes("data-user-message-bubble")
            ? callback([{{ innerText: "Review the pinned change.", getAttribute: () => null }}])
            : callback([]),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-base", assistantTurnCount: 0, conversationId: "bootstrap-route", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "new-route");
'''
    )


def test_completion_allows_local_route_handoff_when_user_turn_appears_after_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
    url() {{ return this.current().url; }},
    waitForTimeout() {{ this.index += 1; }},
    locator(selector) {{
      const current = () => this.current();
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        evaluateAll: async (callback, includeText) => callback(
          selector.includes("assistant")
            ? current().assistant.map(([id, text]) => ({{ innerText: text, getAttribute: (name) => name === "data-message-id" ? id : null }}))
            : selector.includes("data-user-message-bubble") && current().user
              ? [{{ innerText: current().user, getAttribute: () => null }}]
              : [],
          includeText,
        ),
      }};
    }},
    getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
    getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
  }};
  return page;
}}

const response = "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.";
const result = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/local-chatgpt:abc", assistant: [], user: null }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: [["assistant-new", response]], user: null }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: [["assistant-new", response]], user: "Review the pinned change." }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: [["assistant-new", response]], user: "Review the pinned change." }},
]), {{
  baseline: {{ assistantMessageId: null, assistantTurnCount: 0, conversationId: "local-chatgpt:abc", submissionConversationId: "local-chatgpt:abc", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "real-route");
'''
    )


def test_completion_allows_route_handoff_when_bootstrap_has_one_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/real-route",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => callback(
        selector.includes("assistant")
          ? [{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-new" : null }}]
          : selector.includes("data-user-message-bubble")
            ? [{{ innerText: "Review the pinned change.", getAttribute: () => null }}]
            : [],
        includeText,
      ),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-bootstrap", assistantTurnCount: 1, conversationId: "local-chatgpt:abc", submissionConversationId: "local-chatgpt:abc", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "real-route");
'''
    )


def test_completion_allows_synthetic_route_handoff_after_response_progress():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
    url() {{ return this.current().url; }},
    waitForTimeout() {{ this.index += 1; }},
    locator(selector) {{
      const current = () => this.current();
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        evaluateAll: async (callback, includeText) => callback(
          selector.includes("assistant")
            ? current().assistant.map((text) => ({{ innerText: text, getAttribute: () => null }}))
            : [],
          includeText,
        ),
      }};
    }},
    getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
    getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
  }};
  return page;
}}

const result = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/local-chatgpt:abc", assistant: ["Bootstrap"] }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: ["Partial response"] }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: ["Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."] }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: ["Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."] }},
  {{ url: "https://chatgpt.com/c/real-route", assistant: ["Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."] }},
]), {{
  baseline: {{ assistantMessageId: "visible-assistant-turn-0", assistantTurnCount: 1, conversationId: "local-chatgpt:abc", submissionConversationId: "local-chatgpt:abc", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "real-route");
'''
    )


def test_completion_rejects_static_same_count_synthetic_route_handoff_without_user_anchor():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/stale-route",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("assistant")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: () => null }}], includeText)
        : callback([], includeText),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "visible-assistant-turn-0", assistantTurnCount: 1, conversationId: "local-chatgpt:abc", submissionConversationId: "local-chatgpt:abc", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "incomplete");
assert.equal(result.checkpointAccepted, false);
'''
    )


def test_completion_rejects_unanchored_zero_baseline_route_handoff():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/new-route",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("assistant")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-new" : null }}], includeText)
        : callback([]),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-base", assistantTurnCount: 0, conversationId: "bootstrap-route", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "incomplete");
assert.equal(result.checkpointAccepted, false);
'''
    )


def test_acknowledged_empty_baseline_allows_route_handoff_without_user_dom_anchor():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
    url() {{ return this.current().url; }},
    waitForTimeout() {{ this.index += 1; }},
    locator(selector) {{
      const current = () => this.current();
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        evaluateAll: async (callback, includeText) => callback(
          selector.includes("assistant")
            ? current().assistant.map(([id, text]) => ({{
                innerText: text,
                getAttribute: (name) => name === "data-message-id" ? id : null,
              }}))
            : [],
          includeText,
        ),
      }};
    }},
    getByRole(role) {{
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        isVisible: async () => role === "textbox",
      }};
    }},
    getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
  }};
  return page;
}}

const result = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/", assistant: [] }},
  {{ url: "https://chatgpt.com/c/new-route", assistant: [] }},
  {{ url: "https://chatgpt.com/c/new-route", assistant: [["assistant-new", "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."]] }},
  {{ url: "https://chatgpt.com/c/new-route", assistant: [["assistant-new", "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."]] }},
  {{ url: "https://chatgpt.com/c/new-route", assistant: [["assistant-new", "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings."]] }},
]), {{
  baseline: {{ assistantMessageId: null, assistantTurnCount: 0, conversationId: null, submissionConversationId: "new-route", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "new-route");
'''
    )


def test_acknowledged_empty_baseline_rejects_unattributed_conversation():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/stale-route",
  waitForTimeout: async () => {{ }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("assistant")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-message-id" ? "assistant-stale" : null }}], includeText)
        : callback([]),
    }};
  }},
  getByRole(role) {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: null, assistantTurnCount: 0, conversationId: null, submissionConversationId: "submitted-route", dispatchState: "acknowledged", submission: "acknowledged", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "incomplete");
assert.equal(result.checkpointAccepted, false);
'''
    )


def test_interrupted_unrelated_conversation_checkpoint_is_rejected():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/unrelated",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") ? 1 : 0,
      isVisible: async () => selector.includes("conversation-turn-error"),
      innerText: async () => "Response interrupted",
      evaluateAll: async (callback) => selector.includes("data-message-author-role=assistant")
        ? callback([{{ innerText: "Unrelated response", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }}])
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: (name) => name === "data-message-id" ? "user-old" : null }}])
          : callback([]),
    }};
  }},
  getByRole: () => ({{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => false }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
let checkpoints = 0;
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: null, assistantTurnCount: 0, conversationId: null, submittedPrompt: "Review the pinned change.", submittedUserTurnId: "user-new" }},
  timeoutMs: 20,
  onSnapshot: async () => {{ checkpoints += 1; }},
}});
assert.equal(result.status, "interrupted");
assert.equal(result.checkpointAccepted, false);
assert.equal(checkpoints, 0);
'''
    )


def test_current_chatgpt_message_markers_are_read_as_assistant_and_user_turns():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/current-markers",
  waitForTimeout: async () => {{}},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("data-response-body")
        ? callback([{{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", getAttribute: (name) => name === "data-response-body" ? "assistant-current" : null }}], includeText)
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: () => null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole(role) {{
    return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => role === "textbox" }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "old", assistantTurnCount: 0, conversationId: "current-markers", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 20,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.assistantMessageId, "assistant-current");
'''
    )


def test_rejected_completion_snapshot_does_not_replace_last_accepted_checkpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{ isClosed: () => false, close: async () => {{}} }};
const responses = [];
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-rejected-checkpoint",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/accepted",
      conversationId: "accepted",
    }}),
    waitForReviewCompletion: async (_page, {{ onSnapshot }}) => {{
      await onSnapshot({{ currentUrl: "https://chatgpt.com/c/accepted", conversationId: "accepted", assistantMessageId: "assistant-1", assistantTurnCount: 2, assistantText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings." }});
      await onSnapshot({{ currentUrl: "https://chatgpt.com/c/rejected", conversationId: "rejected", assistantMessageId: "assistant-2", assistantTurnCount: 2, assistantText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings." }});
      return {{ status: "incomplete", currentUrl: "https://chatgpt.com/c/rejected", conversationId: "rejected", assistantMessageId: "assistant-2", assistantTurnIndex: 1, response: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", failureReason: "conversation identity changed" }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (_filePath, content) => responses.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/accepted");
assert.equal(result.conversation_id, "accepted");
assert.equal(responses.at(-1), "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.\\n");
'''
    )


def test_accepted_route_transition_replaces_initial_transaction_checkpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{ isClosed: () => false, close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-accepted-route-transition",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/route-1",
      conversationId: "route-1",
    }}),
    waitForReviewCompletion: async (_page, {{ onSnapshot }}) => {{
      await onSnapshot({{ checkpointAccepted: true, currentUrl: "https://chatgpt.com/c/route-1", conversationId: "route-1", assistantMessageId: "assistant-1", assistantTurnCount: 2, assistantText: "Generating" }});
      await onSnapshot({{ checkpointAccepted: true, currentUrl: "https://chatgpt.com/c/route-2", conversationId: "route-2", assistantMessageId: "assistant-2", assistantTurnCount: 2, assistantText: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings." }});
      return {{ status: "incomplete", checkpointAccepted: true, currentUrl: "https://chatgpt.com/c/route-2", conversationId: "route-2", assistantMessageId: "assistant-2", assistantTurnIndex: 1, response: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", failureReason: "bounded timeout" }};
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/route-2");
assert.equal(result.conversation_id, "route-2");
'''
    )


def test_rejected_completion_without_accepted_checkpoint_preserves_submission_identity():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{ isClosed: () => false, close: async () => {{}} }};
const responses = [];
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-rejected-without-checkpoint",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/accepted",
      conversationId: "accepted",
    }}),
    waitForReviewCompletion: async () => ({{
      status: "incomplete",
      checkpointAccepted: false,
      currentUrl: "https://chatgpt.com/c/rejected",
      conversationId: "rejected",
      assistantMessageId: "assistant-rejected",
      assistantTurnIndex: 1,
      response: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.",
      failureReason: "conversation identity changed",
    }}),
    writeResult: async () => {{}},
    writeResponse: async (_filePath, content) => responses.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/accepted");
assert.equal(result.conversation_id, "accepted");
assert.equal(responses.length, 0);
'''
    )


def test_bootstrap_page_selection_fails_closed_on_zero_or_multiple_pages():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ findBootstrapReviewPage }} from {CLI_RUNNER.as_uri()!r};

const page = {{}};
assert.equal(await findBootstrapReviewPage({{ pages: () => [page] }}), page);
await assert.rejects(findBootstrapReviewPage({{ pages: () => [] }}, {{ timeoutMs: 0 }}), /bootstrap page/);
await assert.rejects(findBootstrapReviewPage({{ pages: () => [page, {{}}] }}), /Ambiguous/);
'''
    )


def test_owned_profile_context_closes_before_releasing_lease_on_bootstrap_failure():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ existsSync }} from "node:fs";
import {{ openContext }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-profile-"));
const profile = join(root, "github-review", "owner-repo");
const lockPath = join(profile, ".codex-review-profile.lock");
let closeCount = 0;
const context = {{ pages: () => [{{}}, {{}}], close: async () => {{ closeCount += 1; assert.equal(existsSync(lockPath), true); }} }};
const chromium = {{ launchPersistentContext: async () => context }};
await assert.rejects(openContext(chromium, {{ userDataDir: profile, projectKey: "owner-repo", repository: "owner/repo" }}), /Could not launch/);
assert.equal(closeCount, 1);
assert.equal(existsSync(lockPath), false);
'''
    )


def test_cleanup_waits_for_owned_chrome_process_exit_before_releasing_lease():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ EventEmitter }} from "node:events";
import {{ existsSync }} from "node:fs";
import {{ mkdtemp, writeFile, rm }} from "node:fs/promises";
import {{ closeContext }} from {CLI_RUNNER.as_uri()!r};
import {{ join }} from "node:path";

const directory = await mkdtemp("review-lease-");
const lockPath = join(directory, "profile.lock");
await writeFile(lockPath, JSON.stringify({{ token: "token" }}));
const chromeProcess = new EventEmitter();
chromeProcess.exitCode = null;
chromeProcess.signalCode = null;
chromeProcess.killed = false;
chromeProcess.kill = () => {{
  chromeProcess.killed = true;
  setTimeout(() => {{ chromeProcess.exitCode = 0; chromeProcess.emit("exit", 0, null); }}, 5);
}};
await closeContext({{
  browser: {{ close: async () => {{}} }},
  ownsContext: false,
  chromeProcess,
  profileLease: {{ lockPath, profilePath: directory, token: "token" }},
}});
assert.equal(existsSync(lockPath), false);
await rm(directory, {{ recursive: true, force: true }});
'''
    )


def test_existing_conversation_completion_reports_actual_assistant_turn_index():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor() {{
  const page = {{
    index: 0,
    url: () => "https://chatgpt.com/c/existing-review",
    waitForTimeout: async () => {{ page.index += 1; }},
    locator(selector) {{
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        evaluateAll: async (callback, includeText) => callback([
          {{ innerText: "Older", getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null }},
          {{ innerText: "Reviewed 0123456789abcdef0123456789abcdef01234567", getAttribute: (name) => name === "data-message-id" ? "assistant-2" : null }},
        ], includeText),
      }};
    }},
    getByRole(role, options) {{
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        isVisible: async () => role === "textbox" || options?.name === "Feedback",
      }};
    }},
    getByText: () => ({{ first() {{ return this; }}, isVisible: async () => true }}),
  }};
  return page;
}}

const result = await waitForExistingReviewCompletion(pageFor(), {{ conversationUrl: "https://chatgpt.com/c/existing-review", timeoutMs: 1000 }});
assert.equal(result.status, "confirmed");
assert.equal(result.assistantTurnIndex, 1);
'''
    )


def test_route_transitions_before_response_are_tolerated_but_later_change_is_not():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
    url() {{ return this.current().url; }},
    waitForTimeout() {{ this.index += 1; }},
    locator(selector) {{
      const current = () => this.current();
      const locator = {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        innerText: async () => "",
        evaluateAll: async (callback, includeText) => callback(
          selector.includes("data-user-message-bubble")
            ? [{{ innerText: "Review the pinned change.", getAttribute: (name) => name === "data-message-id" ? "submitted-user" : null }}]
            : current().assistant.map(([id, text]) => ({{
              innerText: text,
              getAttribute: (name) => name === "data-message-id" ? id : null,
            }})),
          includeText,
        ),
      }};
      return locator;
    }},
    getByRole(role, options) {{
      const locator = {{
        first() {{ return this; }},
        last() {{ return this; }},
        isVisible: async () => role === "textbox",
      }};
      return locator;
    }},
  }};
  return page;
}}

const baseline = {{
  assistantMessageId: "old",
  assistantTurnCount: 1,
  conversationId: "base",
  submittedPrompt: "Review the pinned change.",
  submittedUserTurnId: "submitted-user",
}};
const checkpoints = [];
const stable = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
]), {{ baseline, timeoutMs: 1000, onSnapshot: async (snapshot) => checkpoints.push(snapshot) }});
assert.equal(stable.status, "confirmed");
assert.equal(stable.conversationId, "route-2");

const changed = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
]), {{ baseline, timeoutMs: 1000, onSnapshot: async (snapshot) => checkpoints.push(snapshot) }});
assert.equal(changed.status, "incomplete");
assert.match(changed.failureReason, /after response evidence was bound/);
assert.equal(checkpoints.at(-1).conversationId, "route-1");
'''
    )


def test_cli_accepts_an_existing_conversation_url_for_read_only_verification():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ parseArguments }} from {CLI_RUNNER.as_uri()!r};

const options = parseArguments([
  "--cdp-endpoint", "http://127.0.0.1:9222",
  "--model", "GPT-6",
  "--effort", "High",
  "--prompt-file", "review.txt",
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
  "--existing-conversation-url", "https://chatgpt.com/c/existing-review",
]);
assert.equal(options.existingConversationUrl, "https://chatgpt.com/c/existing-review");
'''
    )


def test_main_forwards_existing_conversation_url_to_single_review_transaction():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ main }} from {CLI_RUNNER.as_uri()!r};

const outputDir = `${{process.env.TEMP}}/github-browser-review-main-forward-${{Date.now()}}`;
const promptFile = `${{outputDir}}/review.txt`;
const captured = {{}};
const {{ mkdir, writeFile }} = await import("node:fs/promises");
await mkdir(outputDir, {{ recursive: true }});
await writeFile(promptFile, "Review https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md");

const exitCode = await main([
  "--cdp-endpoint", "http://127.0.0.1:9222",
  "--model", "GPT-6",
  "--effort", "High",
  "--prompt-file", promptFile,
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
  "--existing-conversation-url", "https://chatgpt.com/c/existing-review",
  "--output-dir", outputDir,
], {{
  createRunOutputDirectory: async (parentDir) => {{
    const runOutputDir = `${{parentDir}}/run-main-forward`;
    await mkdir(runOutputDir, {{ recursive: true }});
    return {{ outputDir: runOutputDir, runId: "run-main-forward" }};
  }},
  writeResult: async () => {{}},
  openReviewContext: async () => ({{ context: {{}} }}),
  installTerminationCleanup: () => {{
    const cleanup = () => {{}};
    cleanup.getSignalCode = () => null;
    cleanup.closeOnce = async () => {{}};
    return cleanup;
  }},
  closeContext: async () => {{}},
  runReviewTransaction: async (_context, options) => {{
    captured.existingConversationUrl = options.existingConversationUrl;
    return {{
      status: "completed",
      output_dir: "review-output/run-main-forward",
    }};
  }},
}});

assert.equal(exitCode, 0);
assert.equal(captured.existingConversationUrl, "https://chatgpt.com/c/existing-review");
'''
    )


def test_batch_reviews_preserve_existing_conversation_verification_mode():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ validateReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const [review] = validateReviewBatch([{{
  model: "GPT-6",
  effort: "High",
  prompt: `Review https://github.com/owner/repo/blob/${{sha}}/file.md at ${{sha}}`,
  repository: "owner/repo",
  commit_sha: sha,
  review_urls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  existing_conversation_url: "https://chatgpt.com/c/existing-review",
}}], {{ projectKey: "owner-repo", repository: "owner/repo" }});
assert.equal(review.existingConversationUrl, "https://chatgpt.com/c/existing-review");
'''
    )


def test_read_only_transaction_never_dispatches_a_prompt():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

let sawBeforeSubmit = false;
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-read-only",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  existingConversationUrl: "https://chatgpt.com/c/existing-review",
  dependencies: {{
    runReviewPromptInNewTab: async (_context, options) => {{
      sawBeforeSubmit = Boolean(options.beforeSubmit);
      assert.equal(options.existingConversationUrl, "https://chatgpt.com/c/existing-review");
      return {{
        page,
        model: null,
        effort: null,
        promptSubmitted: false,
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
      }};
    }},
    waitForReviewCompletion: async () => ({{
      status: "confirmed",
      currentUrl: "https://chatgpt.com/c/existing-review",
      conversationId: "existing-review",
      assistantMessageId: "assistant-1",
      assistantTurnIndex: 0,
          response: "Existing review of 0123456789abcdef0123456789abcdef01234567; no findings.",
    }}),
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(sawBeforeSubmit, false);
assert.equal(result.status, "completed");
assert.equal(result.submission, "not_attempted");
assert.equal(result.submission_attempted, false);
assert.equal(result.conversation_url, "https://chatgpt.com/c/existing-review");
'''
    )


def test_planning_only_transaction_remains_incomplete_after_technical_completion():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-planning-only",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/review",
      conversationId: "review",
      completion: {{
        status: "confirmed",
        currentUrl: "https://chatgpt.com/c/review",
        conversationId: "review",
        assistantMessageId: "assistant-1",
        assistantTurnIndex: 0,
        response: "I will inspect the pull request and report findings.",
      }},
    }}),
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.completion, "confirmed");
assert.equal(result.status, "incomplete");
assert.match(result.failure_reason, /without citing/);
'''
    )


def test_closed_page_preserves_last_conversation_checkpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const persisted = [];
const page = {{
  isClosed: () => true,
  url: () => {{ throw new Error("page is closed"); }},
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-checkpoint",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/created-review",
      conversationId: "created-review",
    }}),
    waitForReviewCompletion: async () => {{ throw new Error("Target page has been closed"); }},
    writeResult: async (_outputDir, value) => persisted.push(JSON.parse(JSON.stringify(value))),
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/created-review");
assert.equal(result.conversation_id, "created-review");
assert.equal(persisted.at(-1).conversation_url, "https://chatgpt.com/c/created-review");
assert.equal(persisted.at(-1).conversation_id, "created-review");
'''
    )


def test_launch_owned_review_page_is_reused_and_not_closed_per_transaction():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{
  closeCount: 0,
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/reused-review",
  close: async () => {{ page.closeCount += 1; }},
}};
let receivedPage;
const result = await runReviewTransaction({{}}, {{
  reviewPage: page,
  runOutputDir: "review-output/run-reused-page",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async (_context, options) => {{
      receivedPage = options.reviewPage;
      return {{
        page,
        model: "GPT-6",
        effort: "High",
        promptSubmitted: true,
        submission: "acknowledged",
        dispatchState: "acknowledged",
        currentUrl: page.url(),
        conversationId: "reused-review",
        completion: {{
          status: "confirmed",
          currentUrl: page.url(),
          conversationId: "reused-review",
          assistantMessageId: "assistant-1",
          assistantTurnIndex: 0,
              response: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.",
        }},
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(receivedPage, page);
assert.equal(page.closeCount, 0);
assert.equal(result.status, "completed");
'''
    )


def test_closed_shared_review_page_stops_batch_and_skips_following_review():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const page = {{ isClosed: () => true, close: async () => {{}} }};
const base = {{
  model: "GPT-6",
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  dependencies: {{
    runReviewPromptInNewTab: async () => {{
      const error = new Error("Target page has been closed");
      error.reviewPage = page;
      error.failureScope = "review";
      throw error;
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}};
const result = await runReviewBatch({{
  attached: {{ context: {{ pages: () => [] }}, projectKey: "owner-repo", repository: "owner/repo", reviewPage: page }},
  reviews: [{{ ...base, runOutputDir: "review-output/run-shared-page-first" }}, {{ ...base, runOutputDir: "review-output/run-shared-page-second" }}],
  closeContextFn: async () => {{}},
}});

assert.equal(result.length, 2);
assert.equal(result[0].failure_scope, "shared_context");
assert.equal(result[1].status, "skipped");
assert.equal(result[1].failure_scope, "shared_context");
'''
    )


def test_existing_conversation_completion_accepts_current_visible_markers():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
    url() {{ return this.current().url; }},
    waitForTimeout() {{ this.index += 1; }},
    locator(selector) {{
      const current = () => this.current();
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        innerText: async () => "",
        evaluateAll: async (callback, includeText) => callback(
          current().assistant.map(([id, text]) => ({{
            innerText: text,
            getAttribute: (name) => name === "data-message-id" ? id : null,
          }})),
          includeText,
        ),
      }};
    }},
    getByRole(role, options) {{
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        isVisible: async () => role === "textbox" || options?.name === "Feedback",
      }};
    }},
    getByText() {{
      return {{ first() {{ return this; }}, isVisible: async () => true }};
    }},
  }};
  return page;
}}

const result = await waitForExistingReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Existing review"]] }},
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Existing review"]] }},
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Existing review"]] }},
]), {{ conversationUrl: "https://chatgpt.com/c/existing-review", timeoutMs: 1000 }});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "existing-review");
assert.equal(result.response, "Existing review");
'''
    )
