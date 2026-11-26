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

def test_model_catalog_accepts_gpt_6_2_and_matches_visible_label():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ findModelOption, SUPPORTED_MODELS }} from {(ROOT / "src/general_os/assets/skills/github-browser-reviews/scripts/select-review-model.mjs").as_uri()!r};

assert.equal(SUPPORTED_MODELS.has("GPT-6.2"), true);
const option = {{ innerText: async () => "GPT-6.2" }};
const menu = {{
  locator: (selector) => {{
    assert.equal(selector, '[role="menuitemradio"]:visible');
    return {{ count: async () => 1, nth: () => option }};
  }},
}};
assert.equal(await findModelOption(menu, "GPT-6.2"), option);
'''
    )


def test_model_catalog_accepts_subscription_metadata_after_visible_label():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ findModelOption }} from {(ROOT / "src/general_os/assets/skills/github-browser-reviews/scripts/select-review-model.mjs").as_uri()!r};

const option = {{ innerText: async () => "GPT-5.6 Sol\\nLeaving on December 23" }};
const menu = {{
  locator: (selector) => {{
    assert.equal(selector, '[role="menuitemradio"]:visible');
    return {{ count: async () => 1, nth: () => option }};
  }},
}};
assert.equal(await findModelOption(menu, "GPT-5.6-Sol"), option);
'''
    )

def test_model_selection_distinguishes_missing_from_visible_unavailable_option():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ findModelOption }} from {(ROOT / "src/general_os/assets/skills/github-browser-reviews/scripts/select-review-model.mjs").as_uri()!r};

const missingMenu = {{
  locator: () => ({{ count: async () => 0, nth: () => null }}),
}};
await assert.rejects(
  findModelOption(missingMenu, "GPT-6.2"),
  (error) => error.code === "MODEL_MENU_TRANSIENT",
);

const unavailableOption = {{
  innerText: async () => "GPT-6.2 Locked",
  getAttribute: async (name) => name === "aria-disabled" ? "true" : null,
}};
const unavailableMenu = {{
  locator: () => ({{ count: async () => 1, nth: () => unavailableOption }}),
}};
await assert.rejects(
  findModelOption(unavailableMenu, "GPT-6.2"),
  (error) => error.code === "MODEL_UNAVAILABLE",
);

const disabledExactOption = {{
  innerText: async () => "GPT-6.2",
  getAttribute: async (name) => name === "data-disabled" ? "true" : null,
}};
const disabledExactMenu = {{
  locator: () => ({{ count: async () => 1, nth: () => disabledExactOption }}),
}};
await assert.rejects(
  findModelOption(disabledExactMenu, "GPT-6.2"),
  (error) => error.code === "MODEL_UNAVAILABLE",
);
''',
    )


def test_stable_text_fallback_requires_composer_readiness():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-2",
  assistantText: "## Review\\n\\nNo findings.",
  assistantTurnCount: 2,
  baselineAssistantTurnCount: 1,
  composerReady: false,
  conversationId: "conversation-2",
  expectedConversationId: "conversation-2",
  generationObserved: false,
  generating: false,
  interrupted: false,
  responseActionsReady: false,
  stableSampleCount: 2,
  allowStableTextFallback: true,
}}), false);
'''
    )

def test_stable_text_without_terminal_ui_signal_does_not_confirm():
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


def test_response_content_ready_rejects_planning_only_interim_text():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isResponseContentReady }} from {RUNNER.as_uri()!r};

assert.equal(
  isResponseContentReady("I\u2019ll inspect the commit-pinned file and report findings."),
  false,
);
assert.equal(
  isResponseContentReady("I\u2019ll review the file at the pinned commit and report only actionable findings."),
  false,
);
assert.equal(
  isResponseContentReady("The first pass already shows the key design tension. I\u2019m narrowing the review to the transaction wait/recovery path."),
  false,
);
assert.equal(
  isResponseContentReady("The pinned documentation already states the intended invariant. I\u2019m now checking whether the implementation enforces it."),
  false,
);
assert.equal(
  isResponseContentReady("A confirmed design smell is emerging: the observer's contentEvidenceUnconfirmed flag is set when a structural-response heuristic rejects text, but its failure message calls that revision evidence. That mixes two validation layers before the CLI's actual revision-evidence check even runs."),
  false,
);
assert.equal(isResponseContentReady("Reviewed completion logic"), false);
assert.equal(isResponseContentReady("No findings."), true);
assert.equal(
  isResponseContentReady("0123456789abcdef0123456789abcdef01234567\\nNo actionable findings."),
  true,
);
assert.equal(
  isResponseContentReady("792b035\\n\\n## Findings\\n\\n[P1] The completion state can remain waiting after the response is visible."),
  true,
);
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


def test_stable_text_fallback_still_requires_multiple_stable_samples():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-new",
  assistantText: "Medium — partial review text.",
  assistantTurnCount: 1,
  baselineAssistantTurnCount: 0,
  composerReady: false,
  conversationId: "review",
  expectedConversationId: "review",
  generating: false,
  interrupted: false,
  responseActionsReady: false,
  stableSampleCount: 1,
  submittedTurnObserved: true,
  allowStableTextFallback: true,
}}), false);
'''
    )


def test_checkpoint_does_not_persist_old_assistant_text_when_only_user_turn_is_visible():
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
      evaluateAll: async (callback, includeText) => selector.includes("assistant") || selector.includes("response-body")
        ? callback([{{ innerText: "Older response", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }}], includeText)
        : selector.includes("user")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: (name) => name === "data-message-id" ? "submitted-user" : null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole() {{ return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => false }}; }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const checkpoints = [];
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 1, conversationId: "review", submittedPrompt: "Review the pinned change.", submittedUserTurnId: "submitted-user" }},
  timeoutMs: 0,
  onSnapshot: async (snapshot) => checkpoints.push(snapshot),
}});
assert.equal(result.status, "incomplete");
assert.ok(checkpoints.length >= 1);
assert.equal(checkpoints.every((snapshot) => snapshot.responseTurnObserved === false), true);
assert.equal(result.checkpointAccepted, true);
'''
    )


def test_ambiguous_dispatch_keeps_its_short_initial_deadline():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

let now = 1000;
const realDateNow = Date.now;
Date.now = () => now;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async (delay) => {{ now += delay || 1; }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => callback([], includeText),
    }};
  }},
  getByRole: () => ({{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => false }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
try {{
  const result = await waitForReviewCompletion(page, {{
    baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 1, conversationId: "review", submittedPrompt: "Review the pinned change." }},
    initialTimeoutMs: 15_000,
    completionTimeoutMs: 900_000,
    deadlineAt: 901_000,
  }});
  assert.equal(result.status, "incomplete");
  assert.ok(now < 901_000);
}} finally {{
  Date.now = realDateNow;
}}
''' ,
    )


def test_structural_completion_does_not_wait_for_content_acceptance():
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
        ? callback([{{ innerText: "The response completed, but the requested revision marker is absent.", getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}], includeText)
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
assert.equal(result.status, "confirmed");
assert.ok(acceptanceChecks > 0);
assert.equal(result.contentEvidenceUnconfirmed, true);
'''
    )


def test_nested_assistant_match_does_not_replace_complete_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isResponseContentReady, waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const finalText = "Reviewed the pinned revision; no actionable findings.";
const planningText = "I am now checking the response state.";
const nestedStatus = {{
  innerText: planningText,
  getAttribute: (name) => name === "data-response-body" ? "status-fragment" : null,
  contains: () => false,
}};
const completeTurn = {{
  innerText: finalText,
  getAttribute: (name) => name === "data-message-id" ? "assistant-new" : null,
  contains: (element) => element === nestedStatus,
}};
const assistantElements = [completeTurn, nestedStatus];
const emptyLocator = {{
  first() {{ return this; }},
  last() {{ return this; }},
  nth() {{ return this; }},
  count: async () => 0,
  isVisible: async () => false,
  evaluateAll: async (callback, includeText) => callback([], includeText),
  getByRole: () => this,
  getByText: () => this,
}};
const assistantLocator = {{
  first() {{ return this; }},
  last() {{ return this; }},
  nth() {{ return this; }},
  count: async () => assistantElements.length,
  isVisible: async () => false,
  evaluateAll: async (callback, includeText) => callback(assistantElements, includeText),
  getByRole(role, options) {{
    const visible = role === "button" && options?.name?.test?.("Feedback") === true;
    return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => visible }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const userLocator = {{
  evaluateAll: async (callback, includeText) => callback([{{
    innerText: "Review the pinned change.",
    getAttribute: () => "submitted-user",
  }}], includeText),
}};
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async () => {{}},
  evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  locator(selector) {{
    if (selector.includes("data-response-body") || selector.includes('data-message-author-role="assistant"')) return assistantLocator;
    if (selector.includes("data-user-message-bubble") || selector.includes('data-message-author-role="user"')) return userLocator;
    return emptyLocator;
  }},
  getByRole(role, options) {{
    const visible = role === "textbox"
      || (role === "button" && options?.name?.test?.("Feedback") === true);
    return {{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => visible }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "Review the pinned change.", submittedUserTurnId: "submitted-user" }},
  timeoutMs: 100,
  acceptSnapshot: (snapshot) => isResponseContentReady(snapshot.assistantText),
}});
assert.equal(result.status, "confirmed");
assert.equal(result.response, finalText);
'''
    )

def test_planning_checkpoint_does_not_settle_before_final_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isResponseContentReady, waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const planningText = "I'll trace the lifecycle and report findings.";
const finalText = "Reviewed the pinned revision; no actionable findings.";
const assistantSequences = [
  [{{ innerText: planningText, getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}],
  [{{ innerText: planningText, getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}],
  [{{ innerText: finalText, getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}],
  [{{ innerText: finalText, getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}],
];
let reads = 0;
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
        ? callback(assistantSequences[Math.min(reads++, assistantSequences.length - 1)], includeText)
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: () => null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole(role, options) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      isVisible: async () => role === "textbox" || (options?.name === "Feedback" && reads >= 3),
    }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 100,
  acceptSnapshot: (snapshot) => isResponseContentReady(snapshot.assistantText),
}});
assert.equal(result.status, "confirmed");
assert.equal(result.response, finalText);
assert.equal(result.contentEvidenceUnconfirmed, false);
'''
    )


def test_structured_or_long_planning_checkpoint_stays_provisional():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isResponseContentReady }} from {RUNNER.as_uri()!r};

assert.equal(isResponseContentReady("## Plan\\nI will inspect the lifecycle in three stages:\\n\\n1. Trace completion detection.\\n2. Examine response persistence.\\n3. Identify incorrect continuation conditions."), false);
assert.equal(isResponseContentReady("I will inspect the lifecycle and report findings.\\n" + "I will check the observer and persistence path.\\n".repeat(8)), false);
assert.equal(isResponseContentReady("Plan:\\n- Inspect the pinned files\\n- Check the runner tests\\n- Report findings"), false);
assert.equal(isResponseContentReady("## Analysis\\nChecking the completion path next."), false);
assert.equal(isResponseContentReady("## Analysis\\nThe review identified a bug that can overwrite the final response."), true);
assert.equal(isResponseContentReady("I found two actionable issues in the pinned revision."), true);
assert.equal(isResponseContentReady("## Findings\\nReviewed the pinned revision; no actionable findings."), true);
'''
    )


def test_structurally_final_response_settles_without_content_acceptance():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async () => {{}} ,
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      getByRole(role, options) {{
        return {{
          first() {{ return this; }},
          last() {{ return this; }},
          isVisible: async () => options?.name instanceof RegExp ? options.name.test("Feedback") : options?.name === "Feedback",
        }};
      }},
      count: async () => 0,
      isVisible: async () => selector.includes("data-message-author-role=assistant") ? false : selector.includes("data-user-message-bubble") ? true : false,
      evaluateAll: async (callback, includeText) => selector.includes("data-response-body")
        ? callback([{{ innerText: includeText ? "I will inspect the pinned revision next." : "", getAttribute: (name) => name === "data-response-body" ? "assistant-new" : null }}], includeText)
        : selector.includes("data-user-message-bubble")
          ? callback([{{ innerText: "Review the pinned change.", getAttribute: () => null }}], includeText)
          : callback([], includeText),
    }};
  }},
  getByRole(role, options) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      isVisible: async () => role === "textbox" || (options?.name instanceof RegExp ? options.name.test("Feedback") : options?.name === "Feedback"),
    }};
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 100,
  acceptSnapshot: () => false,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.contentEvidenceUnconfirmed, true);
assert.equal(result.response, "I will inspect the pinned revision next.");
''',
    )


def test_severity_led_substantive_finding_is_content_ready():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isResponseContentReady }} from {RUNNER.as_uri()!r};

assert.equal(isResponseContentReady("High - Confirmed defect: the lifecycle can finalize a checkpoint too early."), true);
assert.equal(isResponseContentReady("High - I will inspect the remaining files next."), false);
''',
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
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nP1 - Retrying the job may duplicate the write.\\nReview complete.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n[P1] The error path failed to read a cache entry and may return stale data.\\nReview complete.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n1. High — reviewed the pinned file.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nMedium — reviewed the pinned file.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nSeverity: High\\nI will inspect the pinned file and report findings next.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nCould not access the pinned file; this review is not approved yet.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nI don't have access to the pinned file, so I found no issues.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nI will report no findings if the review is clean.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nSeverity: High if the suspected issue is confirmed; I will inspect it next.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nConfidence: High", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nRisk: Low", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nHigh — confidence in the review plan.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nHigh — possible issue; needs investigation.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nHigh — risk level only.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings expected; review has not started.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I need to inspect the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nI haven't reviewed the pinned file yet; no findings.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to read the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to examine the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to analyze the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to investigate the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to compare the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings. I still need to look at the pinned file before I can conclude.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nNo findings; I may inspect the pinned file next.", provenance), false);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nMedium — verified finding.\\nThe evidence gate was too strict.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n[P1] The workflow is not yet suitable for production; a pending external check does not change this finding. The evidence still needs verification by the operator.\\nReview complete.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n[P1] The parser drops a valid finding when a suspected issue needs verification against an external dependency.\\nReview complete.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\n[P1] Runtime behavior remains unverified until the external dependency is available.\\nReview complete.", provenance), true);
assert.equal(hasRevisionEvidence("0123456789abcdef0123456789abcdef01234567\\nHigh — parser defect.\\nI still need to analyze the remaining pinned file.", provenance), false);
'''
    )


def test_stable_text_fallback_resets_at_a_new_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const text = "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.";
const assistantSequences = [
  [{{ innerText: text, getAttribute: (name) => name === "data-message-id" ? "assistant-a" : null }}],
  [
    {{ innerText: "Earlier response", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }},
    {{ innerText: text, getAttribute: (name) => name === "data-message-id" ? "assistant-b" : null }},
  ],
  [
    {{ innerText: "Earlier response", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }},
    {{ innerText: text, getAttribute: (name) => name === "data-message-id" ? "assistant-b" : null }},
  ],
  [
    {{ innerText: "Earlier response", getAttribute: (name) => name === "data-message-id" ? "assistant-old" : null }},
    {{ innerText: text, getAttribute: (name) => name === "data-message-id" ? "assistant-b" : null }},
  ],
];
let reads = 0;
let polls = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async () => {{ polls += 1; }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => 0,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => selector.includes("data-message-author-role=\\"assistant\\"")
        ? callback(assistantSequences[Math.min(reads++, assistantSequences.length - 1)], includeText)
        : selector.includes("data-message-author-role=\\"user\\"")
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
  baseline: {{ assistantMessageId: "baseline", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 100,
}});
assert.equal(result.status, "confirmed");
assert.ok(polls >= 3);
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


def test_terminal_marker_does_not_complete_an_old_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ evaluateReviewCompletion }} from {RUNNER.as_uri()!r};

assert.equal(evaluateReviewCompletion({{
  assistantMessageId: "assistant-old",
  assistantText: "Old response still visible.",
  assistantTurnCount: 1,
  baselineAssistantTurnCount: 1,
  composerReady: false,
  conversationId: "review",
  expectedConversationId: "review",
  generationObserved: false,
  generating: false,
  interrupted: false,
  responseActionsReady: true,
  stableSampleCount: 2,
  submittedTurnObserved: true,
}}), false);
'''
    )


def test_global_response_complete_marker_confirms_scoped_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/review",
  evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  waitForTimeout: async () => {{}},
  locator(selector) {{
    const assistant = selector.includes("assistant") || selector.includes("response-body");
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => assistant ? 1 : 0,
      nth() {{
        return {{
          getByRole: () => ({{ last() {{ return this; }}, isVisible: async () => false }}),
          getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
        }};
      }},
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => assistant
        ? callback([{{ innerText: includeText ? "Reviewed commit 792b035." : "", getAttribute: (name) => name === "data-message-id" ? "assistant-new" : null }}], includeText)
        : callback([], includeText),
    }};
  }},
  getByRole: () => ({{
    first() {{ return this; }},
    last() {{ return this; }},
    isVisible: async () => false,
  }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => true }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "assistant-old", assistantTurnCount: 0, conversationId: "review", submittedPrompt: "" }},
  timeoutMs: 100,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.response, "Reviewed commit 792b035.");
'''
    )
def test_completion_action_must_be_on_the_current_assistant_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

let polls = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForTimeout: async () => {{ polls += 1; }},
  locator: () => ({{
    count: async () => 2,
    nth: () => ({{
      getByRole: () => ({{ last() {{ return this; }}, isVisible: async () => false }}),
    }}),
    first() {{ return this; }},
    last() {{ return this; }},
    isVisible: async () => false,
    evaluateAll: async () => [],
  }}),
  getByRole: (role) => ({{
    first() {{ return this; }},
    last() {{ return this; }},
    isVisible: async () => role === "button",
  }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

const result = await waitForReviewCompletion(page, {{
  baseline: {{ assistantMessageId: "baseline", assistantTurnCount: 1, conversationId: "review", submittedPrompt: "Review the pinned change." }},
  timeoutMs: 100,
}});
assert.equal(result.status, "incomplete");
assert.ok(polls > 0);
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
  evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  waitForTimeout: async () => {{ throw new Error("should not wait"); }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error")
        ? 1
        : selector.includes("data-message-author-role=\\\"user\\\"")
          || selector.includes("data-user-message-bubble")
          || selector.includes("data-message-author-role=\\\"assistant\\\"")
          ? 1
          : 0,
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

def test_capture_preflight_does_not_require_the_composer():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ preflightCaptureContext }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
  locator: () => ({{ innerText: async () => "Visible response" }}),
  getByRole: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};

await preflightCaptureContext({{ newPage: async () => page }}, page);
''',
    )


def test_missing_composer_reports_availability_without_claiming_authentication_failed():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ preflightAuthenticatedContext }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/",
  reload: async () => {{}},
  locator: () => ({{ innerText: async () => "" }}),
  getByRole: () => ({{
    first() {{ return this; }},
    waitFor: async () => {{ throw new Error("composer unavailable"); }},
    isVisible: async () => false,
  }}),
}};

await assert.rejects(
  () => preflightAuthenticatedContext({{ newPage: async () => page }}, page),
  (error) => {{
    assert.equal(error.failureScope, "shared_context");
    assert.equal(
      error.message,
      "Could not find the ChatGPT message composer in the current browser session. Verify that ChatGPT is open, fully loaded, and signed in.",
    );
    assert.equal(error.visibleEvidence.composerVisible, false);
    assert.equal(error.visibleEvidence.loginVisible, false);
    return true;
  }},
);
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
const conversationUrl = "https://chatgpt.com/c/existing-review";
let navigatedTo = null;
const page = {{
  url: () => "https://chatgpt.com/",
  goto: async (url, options) => {{ navigatedTo = {{ url, options }}; }},
}};
const context = {{ pages: () => [page], close: async () => {{}} }};
let launchOptions;
process.env.CHROME_PATH = "C:/test/chrome.exe";
const chromium = {{
  launchPersistentContext: async (_profilePath, options) => {{
    launchOptions = options;
    return context;
  }},
}};
const attached = await openContext(chromium, {{
  userDataDir: profile,
  projectKey: "owner-repo",
  repository: "owner/repo",
  initialUrl: conversationUrl,
}});
assert.equal(attached.reviewPage, page);
assert.deepEqual(launchOptions, {{ headless: false, executablePath: "C:/test/chrome.exe" }});
assert.deepEqual(navigatedTo, {{ url: conversationUrl, options: {{ timeout: 15000, waitUntil: "domcontentloaded" }} }});
await closeContext(attached);
'''
    )


def test_owned_cdp_profile_navigates_bootstrap_page_to_requested_thread():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ openContext, closeContext }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "github-review-cdp-profile-"));
const profile = join(root, "github-review", "owner-repo");
const conversationUrl = "https://chatgpt.com/c/existing-review";
let navigatedTo = null;
const page = {{
  url: () => "https://chatgpt.com/",
  goto: async (url, options) => {{ navigatedTo = {{ url, options }}; }},
}};
const context = {{ pages: () => [page] }};
const browser = {{ contexts: () => [context], close: async () => {{}} }};
const chromium = {{ connectOverCDP: async () => browser }};
const attached = await openContext(chromium, {{
  launchCdp: true,
  userDataDir: profile,
  projectKey: "owner-repo",
  repository: "owner/repo",
  contextIndex: 0,
  initialUrl: conversationUrl,
}}, {{ launchDedicatedChrome: async () => ({{ endpoint: "http://127.0.0.1:45678", process: null }}) }});

assert.deepEqual(navigatedTo, {{ url: conversationUrl, options: {{ timeout: 15000, waitUntil: "domcontentloaded" }} }});
await closeContext(attached);
''',
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
import {{ normalizeExistingConversationUrl }} from {RUNNER.as_uri()!r};

assert.throws(
  () => normalizeExistingConversationUrl("https://chatgpt.com/c/local-chatgpt%3Aabc"),
  /canonical.*conversation URL/i,
);
assert.equal(
  normalizeExistingConversationUrl("https://chatgpt.com/c/abc%2Ddef"),
  "https://chatgpt.com/c/abc-def",
);
'''
    )


def test_existing_capture_opens_the_thread_directly_and_uses_bounded_capture_by_default():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewPromptInNewTab }} from {RUNNER.as_uri()!r};

const threadUrl = "https://chatgpt.com/c/canonical-thread";
let currentUrl = "about:blank";
const navigations = [];
const page = {{
  url: () => currentUrl,
  goto: async (url) => {{ currentUrl = url; navigations.push(url); }},
  close: async () => {{}},
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Visible response",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};
const result = await runReviewPromptInNewTab({{ newPage: async () => page }}, {{
  existingConversationUrl: threadUrl,
}});

assert.deepEqual(navigations, [threadUrl]);
assert.equal(result.completion.status, "captured");
assert.equal(result.completion.response, "Visible response");
''',
    )

def test_capture_reopens_same_thread_url_before_reading_visible_output():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const threadUrl = "https://chatgpt.com/c/existing-review";
let navigations = 0;
const page = {{
  url: () => threadUrl,
  goto: async (url, options) => {{
    assert.equal(url, threadUrl);
    assert.equal(options.waitUntil, "domcontentloaded");
    navigations += 1;
  }},
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Visible response",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: threadUrl,
  reopenPage: async (options) => {{
    await page.goto(options.conversationUrl, {{ waitUntil: "domcontentloaded" }});
    return page;
  }},
}});

assert.equal(navigations, 1);
assert.equal(result.response, "Visible response");
''',
    )

def test_capture_continues_after_navigation_timeout_and_reads_visible_output():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let attempts = 0;
const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Visible after timeout",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: page.url(),
  reopenPage: async () => {{
    attempts += 1;
    const error = new Error("Navigation timeout");
    error.name = "TimeoutError";
    throw error;
  }},
}});

assert.equal(attempts, 1);
assert.equal(result.response, "Visible after timeout");
''',
    )


def test_capture_keeps_visible_text_when_submitted_turn_association_is_missing():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const originalNow = Date.now;
let now = 1000;
Date.now = () => now;
try {{
  const page = {{
    url: () => "https://chatgpt.com/c/review",
    waitForLoadState: async () => {{}},
    waitForTimeout: async (milliseconds) => {{ now += milliseconds; }},
    evaluate: async () => ({{ latestAssistantFollowsLatestUser: false }}),
    locator: (selector) => ({{
      evaluateAll: async (callback, includeText) => callback(
        selector.includes('data-message-author-role="user"') ? [] : [{{
          innerText: "Visible despite missing user-turn metadata",
          getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
        }}],
        includeText,
      ),
    }}),
  }};
  const result = await captureReviewResponse(page, {{
    intervalMs: 0,
    conversationUrl: "https://chatgpt.com/c/review",
    submittedPrompt: "submitted prompt",
    submittedUserTurnId: "missing-user-turn",
  }});
  assert.equal(result.response, "Visible despite missing user-turn metadata");
  assert.equal(result.responseTurnObserved, false);
}} finally {{
  Date.now = originalNow;
}}
''',
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


def test_conversation_identity_requires_a_chatgpt_conversation_path():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ extractConversationIdentity }} from {RUNNER.as_uri()!r};

assert.equal(extractConversationIdentity("https://chatgpt.com/c/requested"), "requested");
for (const url of [
  "https://chatgpt.com/?next=/c/requested",
  "https://chatgpt.com/#/c/requested",
  "https://example.invalid/c/requested",
]) assert.equal(extractConversationIdentity(url), null);
''',
    )


def test_route_unstable_snapshot_cannot_confirm_stale_assistant_content():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

let urlReads = 0;
const page = {{
      evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  url() {{
    const sample = Math.floor(urlReads / 4);
    const phase = sample === 0
      ? ["https://chatgpt.com/c/existing-review", "https://chatgpt.com/c/existing-review", "https://chatgpt.com/c/other", "https://chatgpt.com/c/other"]
      : ["https://chatgpt.com/c/existing-review", "https://chatgpt.com/c/existing-review", "https://chatgpt.com/c/existing-review", "https://chatgpt.com/c/existing-review"];
    return phase[urlReads++ % 4];
  }},
  waitForTimeout: async () => {{}},
  locator(selector) {{
    const interruptionSelector = selector.includes("conversation-turn-error")
      || selector.includes("response-error")
      || selector.includes("error-message")
      || selector.includes("role=alert");
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      count: async () => interruptionSelector ? 0 : 1,
      isVisible: async () => !interruptionSelector,
      evaluateAll: async (callback, includeText) => callback([{{
        innerText: includeText && urlReads < 4 ? "stale response" : "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText),
      innerText: async () => "",
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByRole(role, options) {{
    const completionAction = typeof options?.name === "string"
      && /Feedback|Regenerate response|Rate response/.test(options.name);
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      isVisible: async () => role === "textbox" || completionAction,
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => true }}),
}};

const snapshots = [];
const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  timeoutMs: 1000,
  onSnapshot: async (snapshot) => snapshots.push(snapshot),
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "existing-review");
assert.equal(snapshots[0].checkpointAccepted, false);
assert.notEqual(snapshots[0].assistantText, "stale response");
''',
    )


def test_submit_prompt_does_not_dispatch_after_termination_signal():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ submitPrompt }} from {RUNNER.as_uri()!r};

let clickCount = 0;
let beforeSubmitCount = 0;
const signal = new AbortController();
const composer = {{
  fill: async () => {{}},
  inputValue: async () => "review prompt",
  innerText: async () => "review prompt",
}};
const page = {{
  getByRole: () => ({{
    first() {{ return this; }},
    isVisible: async () => true,
    click: async () => {{ clickCount += 1; }},
  }}),
}};

await assert.rejects(
  submitPrompt(page, composer, "review prompt", {{
    beforeSubmit: async () => {{ beforeSubmitCount += 1; signal.abort(); }},
    signal: signal.signal,
  }}),
  (error) => error.code === "REVIEW_INTERRUPTED",
);
assert.equal(beforeSubmitCount, 1);
assert.equal(clickCount, 0);

const visibilitySignal = new AbortController();
const visibilityPage = {{
  getByRole: () => ({{
    first() {{ return this; }},
    isVisible: async () => {{ visibilitySignal.abort(); return true; }},
    click: async () => {{ clickCount += 1; }},
  }}),
}};
await assert.rejects(
  submitPrompt(visibilityPage, composer, "review prompt", {{ signal: visibilitySignal.signal }}),
  (error) => error.code === "REVIEW_INTERRUPTED",
);
assert.equal(clickCount, 0);
''',
    )


def test_read_only_route_transition_without_identity_is_tolerated():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const snapshots = [
  {{ url: "https://chatgpt.com/", text: "", ready: false }},
  {{ url: "https://chatgpt.com/c/existing-review", text: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", ready: true }},
];
const page = {{
  index: 0,
  evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
  url() {{ return this.current().url; }},
  waitForTimeout() {{ this.index += 1; }},
  locator(selector) {{
    const interruptionSelector = selector.includes("conversation-turn-error")
      || selector.includes("response-error")
      || selector.includes("error-message")
      || selector.includes("role=alert");
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      count: async () => interruptionSelector ? 0 : 1,
      isVisible: async () => !interruptionSelector && page.current().ready,
      evaluateAll: async (callback, includeText) => callback([{{
        innerText: includeText ? page.current().text : "",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText),
      innerText: async () => "",
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByRole(role, options) {{
    const completionAction = typeof options?.name === "string"
      && /Feedback|Regenerate response|Rate response/.test(options.name);
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      isVisible: async () => role === "textbox" || completionAction && page.current().ready,
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => page.current().ready }}),
}};

const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  timeoutMs: 1000,
}});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "existing-review");
''',
    )


def test_read_only_route_transition_grace_resets_after_recovery():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const snapshots = [
  {{ url: "https://chatgpt.com/", text: "", ready: false }},
  {{ url: "https://chatgpt.com/c/existing-review", text: "", ready: false }},
  {{ url: "https://chatgpt.com/", text: "", ready: false }},
  {{ url: "https://chatgpt.com/c/existing-review", text: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.", ready: true }},
];
let now = 0;
const originalNow = Date.now;
Date.now = () => now;
const page = {{
  index: 0,
  evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  current() {{ return snapshots[Math.min(this.index, snapshots.length - 1)]; }},
  url() {{ return this.current().url; }},
  waitForTimeout() {{
    now += this.index === 1 ? 39999 : 1;
    this.index += 1;
  }},
  locator(selector) {{
    const interruptionSelector = selector.includes("conversation-turn-error")
      || selector.includes("response-error")
      || selector.includes("error-message")
      || selector.includes("role=alert");
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      count: async () => interruptionSelector ? 0 : 1,
      isVisible: async () => !interruptionSelector && page.current().ready,
      evaluateAll: async (callback, includeText) => callback([{{
        innerText: includeText ? page.current().text : "",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText),
      innerText: async () => "",
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByRole(role, options) {{
    const completionAction = typeof options?.name === "string"
      && /Feedback|Regenerate response|Rate response/.test(options.name);
    const locator = {{
      first() {{ return this; }},
      last() {{ return this; }},
      nth() {{ return this; }},
      isVisible: async () => role === "textbox" || completionAction && page.current().ready,
      getByRole: () => locator,
      getByText: () => locator,
    }};
    return locator;
  }},
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => page.current().ready }}),
}};

try {{
  const result = await waitForExistingReviewCompletion(page, {{
    conversationUrl: "https://chatgpt.com/c/existing-review",
    timeoutMs: 100000,
  }});
  assert.equal(result.status, "confirmed");
  assert.equal(result.conversationId, "existing-review");
}} finally {{
  Date.now = originalNow;
}}
''',
    )


def test_existing_result_does_not_claim_requested_conversation_was_observed():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ createResult }} from {CLI_RUNNER.as_uri()!r};

const result = createResult({{ existingConversationUrl: "https://chatgpt.com/c/existing-review" }});
assert.equal(result.conversation_url, null);
assert.equal(result.conversation_id, null);
assert.equal(result.last_visible_conversation_url, null);
assert.equal(result.last_visible_conversation_id, null);
assert.equal(result.request_provenance.existing_conversation_url, "https://chatgpt.com/c/existing-review");
''',
    )


def test_completion_recovery_receives_termination_signal():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const abortController = new AbortController();
let completionCalls = 0;
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-recovery-signal",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  abortSignal: abortController.signal,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/recovery",
      conversationId: "recovery",
      assistantTurnCount: 0,
      assistantMessageId: null,
    }}),
    waitForReviewCompletion: async (_page, options) => {{
      completionCalls += 1;
      if (completionCalls === 1) throw new Error("observer failed");
      assert.equal(options.signal, abortController.signal);
      return {{
        status: "confirmed",
        checkpointAccepted: true,
        responseTurnObserved: true,
        currentUrl: "https://chatgpt.com/c/recovery",
        conversationId: "recovery",
        assistantMessageId: "assistant-1",
        assistantTurnIndex: 0,
        response: "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.",
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "completed");
assert.equal(completionCalls, 2);
''',
    )


def test_read_only_interruption_metadata_survives_error_wrapper():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewPromptInNewTab }} from {RUNNER.as_uri()!r};

const assistantElement = {{
  innerText: "Review for 0123456789abcdef0123456789abcdef01234567: no findings.",
  getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
}};
const emptyLocator = {{
  first() {{ return this; }},
  last() {{ return this; }},
  nth() {{ return this; }},
  count: async () => 0,
  isVisible: async () => false,
  evaluateAll: async () => [],
  innerText: async () => "",
  waitFor: async () => {{}},
}};
const assistantLocator = {{
  ...emptyLocator,
  count: async () => 1,
  evaluateAll: async (callback, includeText) => callback([assistantElement], includeText),
  getByRole: () => emptyLocator,
  getByText: () => emptyLocator,
}};
const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
      evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
  goto: async () => {{}},
  close: async () => {{}},
  locator: () => assistantLocator,
  getByRole: (role) => role === "textbox" ? {{ ...emptyLocator, isVisible: async () => true }} : emptyLocator,
  getByText: () => emptyLocator,
}};
const interruptionSignal = new AbortController();
interruptionSignal.abort();
const context = {{ newPage: async () => page }};

await assert.rejects(
  runReviewPromptInNewTab(context, {{
    existingConversationUrl: "https://chatgpt.com/c/existing-review",
    signal: interruptionSignal.signal,
  }}),
  (error) => {{
    assert.equal(error.code, "REVIEW_INTERRUPTED");
    assert.equal(error.interruptionSnapshot.currentUrl, "https://chatgpt.com/c/existing-review");
    assert.equal(error.interruptionSnapshot.conversationId, "existing-review");
    assert.equal(error.interruptionSnapshot.checkpointAccepted, true);
    return true;
  }},
);
''',
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


def test_submitted_user_turn_matching_tolerates_rendered_punctuation_spacing():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ readSubmittedUserTurnId }} from {RUNNER.as_uri()!r};

const page = {{
  locator: () => ({{
    evaluateAll: async (callback) => callback([{{
      innerText: "@GitHub Review this exact file revision:https://github.com/example/repo/blob/abc/file.js",
      getAttribute: (name) => name === "data-message-id" ? "submitted-user" : null,
    }}]),
  }}),
  waitForTimeout: async () => {{}},
}};

assert.equal(
  await readSubmittedUserTurnId(page, "@GitHub Review this exact file revision:\\nhttps://github.com/example/repo/blob/abc/file.js", {{ timeoutMs: 1 }}),
  "submitted-user",
);
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


def test_completion_rejects_normal_route_handoff_without_durable_turn_anchor():
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
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /conversation identity changed|submitted user turn|timeout|association/i);
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
assert.equal(result.last_visible_conversation_url, "https://chatgpt.com/c/rejected");
assert.equal(result.last_visible_conversation_id, "rejected");
assert.equal(responses.at(-1), "Reviewed 0123456789abcdef0123456789abcdef01234567; no findings.\\n");
'''
    )


def test_durable_checkpoint_stays_nonterminal_until_page_cleanup():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const page = {{ close: async () => {{}} }};
const checkpoints = [];
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-cleanup-checkpoint",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/cleanup-checkpoint",
      conversationId: "cleanup-checkpoint",
    }}),
    waitForReviewCompletion: async () => ({{
      status: "confirmed",
      currentUrl: "https://chatgpt.com/c/cleanup-checkpoint",
      conversationId: "cleanup-checkpoint",
      assistantMessageId: "assistant-1",
      assistantTurnIndex: 0,
      response: `Reviewed ${{sha}}; no findings.`,
    }}),
    writeResult: async (_outputDir, snapshot) => checkpoints.push({{ ...snapshot }}),
    writeResponse: async () => {{}},
  }},
}});

const pendingCheckpoint = checkpoints.find((snapshot) => snapshot.cleanup_status === "pending");
assert.ok(pendingCheckpoint);
assert.equal(pendingCheckpoint.status, "incomplete");
assert.equal(result.status, "completed");
'''
    )


def test_authoritative_completion_uses_selected_response_snapshot():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const fullResponse = `${{sha}}\\n\\n## Findings\\n\\n[P1] Completion can remain waiting after the response is visible.`;
const shortResponse = `${{sha}}\\n\\nNo findings.`;
const page = {{ isClosed: () => false, close: async () => {{}} }};
const responses = [];
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-monotonic-response",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/monotonic",
      conversationId: "monotonic",
    }}),
    waitForReviewCompletion: async (_page, {{ onSnapshot }}) => {{
      await onSnapshot({{ currentUrl: "https://chatgpt.com/c/monotonic", conversationId: "monotonic", assistantMessageId: "assistant-1", assistantTurnCount: 2, assistantText: fullResponse }});
      await onSnapshot({{ currentUrl: "https://chatgpt.com/c/monotonic", conversationId: "monotonic", assistantMessageId: "assistant-1", assistantTurnCount: 2, assistantText: shortResponse }});
      return {{ status: "confirmed", currentUrl: "https://chatgpt.com/c/monotonic", conversationId: "monotonic", assistantMessageId: "assistant-2", assistantTurnIndex: 1, response: shortResponse }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (_filePath, content) => responses.push(content),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(responses.at(-1), `${{shortResponse}}\\n`);
assert.equal(result.assistant_message_id, "assistant-2");
'''
    )
def test_longer_planning_checkpoint_does_not_overwrite_shorter_final_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const planningResponse = "## Plan\\n" + "- Inspect the pinned files\\n".repeat(12);
const finalResponse = `${{sha}}\\n\\nNo findings.`;
const page = {{ isClosed: () => false, close: async () => {{}} }};
const responses = [];
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-planning-longer-than-final",
  model: "GPT-6.2",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6.2",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/c/planning-longer-than-final",
      conversationId: "planning-longer-than-final",
    }}),
    waitForReviewCompletion: async (_page, {{ onSnapshot }}) => {{
      await onSnapshot({{
        currentUrl: "https://chatgpt.com/c/planning-longer-than-final",
        conversationId: "planning-longer-than-final",
        assistantMessageId: "assistant-1",
        assistantTurnCount: 2,
        assistantText: planningResponse,
      }});
      return {{
        status: "confirmed",
        currentUrl: "https://chatgpt.com/c/planning-longer-than-final",
        conversationId: "planning-longer-than-final",
        assistantMessageId: "assistant-1",
        assistantTurnIndex: 1,
        response: finalResponse,
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (filePath, content) => responses.push({{ filePath, content }}),
  }},
}});

assert.equal(result.status, "completed");
const finalWrite = responses.find((entry) => entry.filePath.endsWith("response.md"));
assert.ok(finalWrite);
assert.equal(finalWrite.content, `${{finalResponse}}\\n`);
const partialWrite = responses.find((entry) => entry.filePath.endsWith("response.partial.md"));
assert.ok(partialWrite);
assert.equal(partialWrite.content, `${{planningResponse.trim()}}\\n`);
''',
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


def test_bootstrap_page_selection_uses_a_chatgpt_page_when_multiple_tabs_exist():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ findBootstrapReviewPage }} from {CLI_RUNNER.as_uri()!r};

const page = {{ url: () => "https://chatgpt.com/" }};
const otherPage = {{ url: () => "about:blank" }};
assert.equal(await findBootstrapReviewPage({{ pages: () => [page] }}), page);
await assert.rejects(findBootstrapReviewPage({{ pages: () => [] }}, {{ timeoutMs: 0 }}), /bootstrap page/);
assert.equal(await findBootstrapReviewPage({{ pages: () => [otherPage, page] }}), page);
assert.equal(
  await findBootstrapReviewPage({{ pages: () => [otherPage, page] }}, {{ preferredUrl: "https://chatgpt.com/" }}),
  page,
);
'''
    )



def test_challenge_evidence_stops_before_refresh_and_reports_distinct_code():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ openChatGPT }} from {RUNNER.as_uri()!r};

let reloadCount = 0;
const composer = {{
  waitFor: async () => {{ throw new Error("not ready"); }},
  isVisible: async () => false,
}};
const page = {{
  url: () => "https://chatgpt.com/",
  title: async () => "Just a moment...",
  getByRole: () => ({{ first: () => composer }}),
  locator: (selector) => selector === "body"
    ? {{ innerText: async () => "" }}
    : {{ evaluateAll: async () => ["https://challenges.cloudflare.com/turnstile/v0/api.js"] }},
  reload: async () => {{ reloadCount += 1; }},
}};

await assert.rejects(
  openChatGPT(page),
  (error) => {{
    assert.equal(error.code, "CHATGPT_CHALLENGE");
    assert.equal(error.visibleEvidence.challengeDetected, true);
    assert.deepEqual(error.visibleEvidence.frameSources, ["https://challenges.cloudflare.com/turnstile/v0/api.js"]);
    return true;
  }},
);
assert.equal(reloadCount, 0);
'''
    )


def test_invalid_html_content_type_is_challenge_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ isChallengeEvidence }} from {RUNNER.as_uri()!r};

assert.equal(isChallengeEvidence({{ visibleText: "Invalid content type: text/html" }}), true);
''',
    )


def test_challenge_failure_code_is_persisted_without_marking_dispatch():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile, rm, writeFile }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-challenge-result-"));
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => {{
      const error = new Error("ChatGPT challenge page blocked the authenticated composer");
      error.code = "CHATGPT_CHALLENGE";
      error.visibleEvidence = {{ challengeDetected: true }};
      throw error;
    }},
    writeResult: async (directory, value) => writeFile(join(directory, "result.json"), JSON.stringify(value)),
  }},
}});

assert.equal(result.status, "blocked");
assert.equal(result.failure_code, "CHATGPT_CHALLENGE");
assert.equal(result.transaction_started, true);
assert.equal(result.submission_attempted, false);
const persisted = JSON.parse(await readFile(join(outputDir, "result.json"), "utf8"));
assert.equal(persisted.failure_code, "CHATGPT_CHALLENGE");
await rm(outputDir, {{ recursive: true, force: true }});
'''
    )

def test_owned_profile_context_selects_a_bootstrap_tab_before_releasing_lease():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ existsSync }} from "node:fs";
import {{ openContext, closeContext }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-profile-"));
const profile = join(root, "github-review", "owner-repo");
const lockPath = `${{profile}}.codex-review-profile.lock`;
let closeCount = 0;
const firstPage = {{}};
const secondPage = {{}};
const context = {{ pages: () => [firstPage, secondPage], close: async () => {{ closeCount += 1; assert.equal(existsSync(lockPath), true); }} }};
const chromium = {{ launchPersistentContext: async () => context }};
const attached = await openContext(chromium, {{ userDataDir: profile, projectKey: "owner-repo", repository: "owner/repo" }});
assert.equal(attached.reviewPage, firstPage);
await closeContext(attached);
assert.equal(closeCount, 1);
assert.equal(existsSync(lockPath), false);
'''
    )


def test_launch_failure_keeps_lease_when_owned_chrome_exit_is_unconfirmed():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ existsSync }} from "node:fs";
import {{ mkdtemp }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ openContext }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "github-review-lease-"));
const profile = join(root, "github-review", "owner-repo");
const chromeProcess = {{ exitCode: null, signalCode: null, kill: () => {{}} }};
const launchError = new Error("CDP startup failed");
launchError.chromeProcess = chromeProcess;
const chromium = {{}};
await assert.rejects(openContext(chromium, {{
  launchCdp: true,
  userDataDir: profile,
  projectKey: "owner-repo",
  repository: "owner/repo",
}}, {{ launchDedicatedChrome: async () => {{ throw launchError; }} }}), /CDP startup failed/);
assert.equal(existsSync(`${{profile}}.codex-review-profile.lock`), true);
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
        evaluate: async () => ({{ userTurnCount: 2, assistantTurnCount: 2, latestAssistantFollowsLatestUser: true }}),
    waitForTimeout: async () => {{ page.index += 1; }},
    locator(selector) {{
      return {{
        first() {{ return this; }},
        last() {{ return this; }},
        count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
        isVisible: async () => false,
        evaluateAll: async (callback, includeText) => callback([
          {{ innerText: "Older", getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null }},
          {{ innerText: "Review complete; 0123456789abcdef0123456789abcdef01234567", getAttribute: (name) => name === "data-message-id" ? "assistant-2" : null }},
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
assert.equal(checkpoints.at(-1).conversationId, "route-2");
assert.equal(checkpoints.at(-1).checkpointAccepted, false);
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


def test_cli_allows_existing_conversation_capture_without_model_or_effort():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ parseArguments }} from {CLI_RUNNER.as_uri()!r};

const options = parseArguments([
  "--cdp-endpoint", "http://127.0.0.1:9222",
  "--prompt-file", "review.txt",
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
  "--existing-conversation-url", "https://chatgpt.com/c/existing-review",
]);
assert.equal(options.model, undefined);
assert.equal(options.effort, undefined);
assert.equal(options.existingConversationUrl, "https://chatgpt.com/c/existing-review");
''',
    )


def test_cli_defaults_existing_conversation_capture_to_immediate_reopen():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ parseArguments }} from {CLI_RUNNER.as_uri()!r};

const common = [
  "--cdp-endpoint", "http://127.0.0.1:9222",
  "--prompt-file", "review.txt",
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
];
const capture = parseArguments([...common, "--existing-conversation-url", "https://chatgpt.com/c/existing-review"]);
assert.equal(capture.reopenIntervalMs, 0);
assert.equal(capture.reopenIntervalProvided, false);
const submitted = parseArguments([...common, "--model", "GPT-6.2", "--effort", "High"]);
assert.equal(submitted.reopenIntervalMs, 300000);
assert.equal(submitted.reopenIntervalProvided, false);
''',
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
    captured.reopenIntervalMs = options.reopenIntervalMs;
    return {{
      status: "completed",
      output_dir: "review-output/run-main-forward",
    }};
  }},
}});

assert.equal(exitCode, 0);
assert.equal(captured.existingConversationUrl, "https://chatgpt.com/c/existing-review");
assert.equal(captured.reopenIntervalMs, 0);
'''
    )


def test_main_reopens_owned_profile_page_at_conversation_url_without_replacing_context():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdir, writeFile }} from "node:fs/promises";
import {{ main }} from {CLI_RUNNER.as_uri()!r};

const outputDir = `${{process.env.TEMP}}/github-browser-review-main-reopen-${{Date.now()}}`;
const profileDir = `${{outputDir}}/github-review/owner-repo`;
const promptFile = `${{outputDir}}/review.txt`;
const conversationUrl = "https://chatgpt.com/c/existing-review";
const opened = [];
let navigatedTo = null;
let closeCount = 0;
const initialPage = {{
  url: () => navigatedTo || "https://chatgpt.com/",
  goto: async (url, options) => {{ navigatedTo = url; assert.equal(options.timeout, 15000); }},
  isClosed: () => false,
}};
await mkdir(outputDir, {{ recursive: true }});
await writeFile(promptFile, "Review https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md");

const exitCode = await main([
  "--launch-cdp",
  "--user-data-dir", profileDir,
  "--project-key", "owner-repo",
  "--model", "GPT-6",
  "--effort", "High",
  "--prompt-file", promptFile,
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
  "--existing-conversation-url", conversationUrl,
  "--output-dir", outputDir,
], {{
  createRunOutputDirectory: async (parentDir) => {{
    const runOutputDir = `${{parentDir}}/run-main-reopen`;
    await mkdir(runOutputDir, {{ recursive: true }});
    return {{ outputDir: runOutputDir, runId: "run-main-reopen" }};
  }},
  writeResult: async () => {{}},
  openReviewContext: async (options) => {{
    opened.push(options);
    return {{ context: {{ pages: () => [initialPage] }}, reviewPage: initialPage }};
  }},
  installTerminationCleanup: () => {{
    const cleanup = () => {{}};
    cleanup.getSignalCode = () => null;
    cleanup.closeOnce = async () => {{}};
    return cleanup;
  }},
  closeContext: async () => {{ closeCount += 1; }},
  runReviewTransaction: async (_context, options) => {{
    const page = await options.reopenPage({{ conversationUrl, page: initialPage }});
    assert.equal(page, initialPage);
    return {{ status: "completed", output_dir: "review-output/run-main-reopen" }};
  }},
}});

assert.equal(exitCode, 0);
assert.equal(opened.length, 1);
assert.equal(opened[0].initialUrl, conversationUrl);
assert.equal(opened[0].captureOnly, true);
assert.equal(navigatedTo, conversationUrl);
assert.equal(closeCount, 0);
''',
    )


def test_main_navigates_attached_cdp_page_to_capture_conversation_url():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdir, writeFile }} from "node:fs/promises";
import {{ main }} from {CLI_RUNNER.as_uri()!r};

const outputDir = `${{process.env.TEMP}}/github-browser-review-main-attached-cdp-${{Date.now()}}`;
const promptFile = `${{outputDir}}/review.txt`;
const conversationUrl = "https://chatgpt.com/c/existing-review";
let navigatedTo = null;
const page = {{
  url: () => "https://chatgpt.com/",
  goto: async (url, options) => {{ navigatedTo = {{ url, options }}; }},
}};
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
  "--existing-conversation-url", conversationUrl,
  "--reopen-interval", "0",
  "--output-dir", outputDir,
], {{
  createRunOutputDirectory: async (parentDir) => {{
    const runOutputDir = `${{parentDir}}/run-main-attached-cdp`;
    await mkdir(runOutputDir, {{ recursive: true }});
    return {{ outputDir: runOutputDir, runId: "run-main-attached-cdp" }};
  }},
  writeResult: async () => {{}},
  openReviewContext: async () => ({{ context: {{ pages: () => [page] }} }}),
  installTerminationCleanup: () => {{
    const cleanup = () => {{}};
    cleanup.getSignalCode = () => null;
    cleanup.closeOnce = async () => {{}};
    return cleanup;
  }},
  closeContext: async () => {{}},
  runReviewTransaction: async (_context, options) => {{
    const reopened = await options.reopenPage({{ conversationUrl, page }});
    assert.equal(reopened, page);
    return {{ status: "completed", output_dir: "review-output/run-main-attached-cdp" }};
  }},
}});

assert.equal(exitCode, 0);
assert.deepEqual(navigatedTo, {{ url: conversationUrl, options: {{ timeout: 15000, waitUntil: "domcontentloaded" }} }});
''',
    )


def test_batch_reviews_preserve_existing_conversation_verification_mode():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ validateReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const [review] = validateReviewBatch([{{
  prompt: `Review https://github.com/owner/repo/blob/${{sha}}/file.md at ${{sha}}`,
  repository: "owner/repo",
  commit_sha: sha,
  review_urls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  existing_conversation_url: "https://chatgpt.com/c/existing-review",
}}], {{ projectKey: "owner-repo", repository: "owner/repo" }});
assert.equal(review.model, undefined);
assert.equal(review.effort, undefined);
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
  reopenIntervalMs: 0,
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
        completion: {{
          status: "captured",
          currentUrl: "https://chatgpt.com/c/existing-review",
          conversationId: "existing-review",
          response: "Existing review of 0123456789abcdef0123456789abcdef01234567; no findings.",
          responseTurnObserved: true,
          checkpointAccepted: true,
        }},
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


def test_read_only_stale_snapshot_does_not_persist_response_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const writes = [];
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-read-only-stale-response",
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
      await options.onSnapshot({{
        checkpointAccepted: false,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        assistantMessageId: "assistant-old",
        assistantTurnCount: 1,
        assistantText: "Old response from before the pending request",
      }});
      return {{
        page,
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        completion: {{
          status: "incomplete",
          checkpointAccepted: false,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/existing-review",
          conversationId: "existing-review",
          response: "Old response from before the pending request",
          failureReason: "bounded existing conversation verification timeout",
        }},
      }};
    }},
    writeResult: async () => {{ }},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.deepEqual(writes, []);
''',
    )


def test_read_only_error_recovery_does_not_use_submission_observer():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/existing-review",
  close: async () => {{ }},
}};
const error = new Error("read-only verification failed");
error.reviewPage = page;
error.reviewBaseline = {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  conversationId: "existing-review",
  assistantMessageId: "assistant-old",
  assistantTurnCount: 1,
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-read-only-recovery",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  existingConversationUrl: "https://chatgpt.com/c/existing-review",
  dependencies: {{
    runReviewPromptInNewTab: async () => {{ throw error; }},
    waitForReviewCompletion: async () => {{ throw new Error("submission observer must not run"); }},
    writeResult: async () => {{ }},
    writeResponse: async () => {{ throw new Error("stale response must not be written"); }},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.completion, "not_started");
''',
    )


def test_read_only_accepted_response_is_removed_when_later_snapshot_is_stale():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ existsSync }} from "node:fs";
import {{ mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-read-only-stale-"));
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
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
      await options.onSnapshot({{
        checkpointAccepted: true,
        responseTurnObserved: true,
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        assistantMessageId: "assistant-old",
        assistantTurnCount: 1,
        assistantText: "Old response from before the pending request",
      }});
      await options.onSnapshot({{
        checkpointAccepted: false,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        assistantMessageId: "assistant-old",
        assistantTurnCount: 1,
        assistantText: "Old response from before the pending request",
      }});
      return {{
        page,
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        completion: {{
          status: "incomplete",
          checkpointAccepted: false,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/existing-review",
          conversationId: "existing-review",
          response: "Old response from before the pending request",
          failureReason: "bounded existing conversation verification timeout",
        }},
      }};
    }},
    writeResult: async () => {{ }},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(existsSync(join(outputDir, "response.md")), false);
assert.equal(result.assistant_message_id, null);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_read_only_stale_response_cleanup_failure_is_recorded():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdir, writeFile }} from "node:fs/promises";
import {{ mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-read-only-cleanup-failure-"));
const responseDir = join(outputDir, "response.md");
await mkdir(responseDir);
await writeFile(join(responseDir, "existing.txt"), "old response");
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
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
      for (let attempt = 0; attempt < 3; attempt += 1) {{
        await options.onSnapshot({{
          checkpointAccepted: false,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/existing-review",
          conversationId: "existing-review",
          assistantText: "Old response from before the pending request",
        }});
      }}
      return {{
        page,
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
        currentUrl: "https://chatgpt.com/c/existing-review",
        conversationId: "existing-review",
        completion: {{
          status: "incomplete",
          checkpointAccepted: false,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/existing-review",
          conversationId: "existing-review",
          response: "Old response from before the pending request",
          failureReason: "bounded existing conversation verification timeout",
        }},
      }};
    }},
  }},
}});

assert.equal(result.status, "incomplete");
assert.match(result.stale_response_cleanup_error, /EISDIR|ENOTEMPTY|EPERM|EBUSY/i);
assert.equal((result.failure_reason.match(/stale response cleanup failed/gi) || []).length, 1);
assert.match(result.failure_reason, /bounded existing conversation verification timeout/i);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_cleanup_failure_preserves_prior_failure_reason():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ persistCleanupFailure }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-cleanup-preservation-"));
const result = {{
  status: "incomplete",
  cleanup_status: "not_started",
  cleanup_warning: null,
  failure_scope: "review",
  failure_stage: "completion",
  failure_reason: "review timeout",
}};
await persistCleanupFailure(result, outputDir, "browser context close failed");
assert.equal(result.failure_reason, "review timeout; context cleanup failed: browser context close failed");
const persisted = JSON.parse(await readFile(join(outputDir, "result.json"), "utf8"));
assert.equal(persisted.failure_reason, result.failure_reason);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_page_cleanup_failure_preserves_checkpoint_diagnostic():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ markCleanupFailure }} from {CLI_RUNNER.as_uri()!r};

const result = {{
  status: "completed",
  cleanup_status: "completed",
  cleanup_warning: null,
  failure_scope: null,
  failure_stage: null,
  failure_reason: "result checkpoint failed: disk full",
}};
markCleanupFailure(result, "page close failed");
assert.equal(result.status, "incomplete");
assert.equal(result.failure_stage, "cleanup");
assert.equal(result.failure_reason, "result checkpoint failed: disk full; cleanup failed: page close failed");
''',
    )


def test_repeated_checkpoint_failures_are_deduplicated():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-checkpoint-deduplication-"));
let writeCount = 0;
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  existingConversationUrl: "https://chatgpt.com/c/review",
  dependencies: {{
    runReviewPromptInNewTab: async (_context, options) => {{
      for (let attempt = 0; attempt < 3; attempt += 1) {{
        await options.onSnapshot({{
          checkpointAccepted: true,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/review",
          conversationId: "review",
        }});
      }}
      return {{
        page,
        model: "GPT-6",
        effort: "High",
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
        currentUrl: "https://chatgpt.com/c/review",
        conversationId: "review",
        completion: {{
          status: "incomplete",
          checkpointAccepted: false,
          responseTurnObserved: false,
          currentUrl: "https://chatgpt.com/c/review",
          conversationId: "review",
          failureReason: "review timeout",
        }},
      }};
    }},
    writeResult: async () => {{
      writeCount += 1;
      if (writeCount >= 2 && writeCount <= 4) throw new Error("disk full");
    }},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal((result.failure_reason.match(/result checkpoint failed: disk full/gi) || []).length, 1);
assert.match(result.failure_reason, /review timeout/i);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_final_checkpoint_failure_preserves_prior_failure_reason():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-final-checkpoint-preservation-"));
let writeCount = 0;
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  existingConversationUrl: "https://chatgpt.com/c/review",
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      readOnlyVerification: true,
      submission: "not_attempted",
      dispatchState: "not_dispatched",
      currentUrl: "https://chatgpt.com/c/review",
      conversationId: "review",
      completion: {{
        status: "incomplete",
        checkpointAccepted: false,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/review",
        conversationId: "review",
        failureReason: "review timeout",
      }},
    }}),
    writeResult: async (directory, value) => {{
      writeCount += 1;
      if (writeCount === 3) throw new Error("disk full");
      await (await import("node:fs/promises")).writeFile(join(directory, "result.json"), JSON.stringify(value));
    }},
  }},
}});

assert.equal(result.status, "blocked");
assert.match(result.failure_reason, /review timeout/i);
assert.match(result.failure_reason, /result write failed: disk full/i);
const persisted = JSON.parse(await readFile(join(outputDir, "result.json"), "utf8"));
assert.match(persisted.failure_reason, /review timeout/i);
assert.match(persisted.failure_reason, /result write failed: disk full/i);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_recovery_failure_preserves_checkpoint_diagnostic():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile, rm, writeFile }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-recovery-preservation-"));
let writeCount = 0;
let observerCalls = 0;
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
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
    }}),
    waitForReviewCompletion: async (_page, options) => {{
      observerCalls += 1;
      await options.onSnapshot({{
        checkpointAccepted: true,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/review",
        conversationId: "review",
      }});
      throw new Error(observerCalls === 1 ? "primary observer failed" : "recovery observer failed");
    }},
    writeResult: async (directory, value) => {{
      writeCount += 1;
      if (writeCount === 3) throw new Error("disk full");
      await writeFile(join(directory, "result.json"), JSON.stringify(value));
    }},
  }},
}});

assert.equal(result.status, "incomplete");
assert.match(result.failure_reason, /result checkpoint failed: disk full/i);
assert.match(result.failure_reason, /evidence preservation failed: recovery observer failed/i);
const persisted = JSON.parse(await readFile(join(outputDir, "result.json"), "utf8"));
assert.match(persisted.failure_reason, /result checkpoint failed: disk full/i);
assert.match(persisted.failure_reason, /evidence preservation failed: recovery observer failed/i);
await rm(outputDir, {{ recursive: true, force: true }});
''',
    )


def test_completion_recovery_reuses_one_deadline_and_terminalizes_waiting():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const outputDir = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-recovery-deadline-"));
const page = {{ close: async () => {{}} }};
const deadlines = [];
let observerCalls = 0;
const result = await runReviewTransaction({{}}, {{
  runOutputDir: outputDir,
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
    }}),
    waitForReviewCompletion: async (_page, options) => {{
      deadlines.push(options.deadlineAt);
      observerCalls += 1;
      throw new Error(observerCalls === 1 ? "primary observer failed" : "recovery observer failed");
    }},
  }},
}});

assert.equal(deadlines.length, 2);
assert.equal(deadlines[0], deadlines[1]);
assert.equal(result.status, "incomplete");
assert.equal(result.completion, "incomplete");
assert.notEqual(result.completion, "waiting");
assert.match(result.failure_reason, /could not be confirmed after recovery/i);
await rm(outputDir, {{ recursive: true, force: true }});
''' ,
    )


def test_read_only_interruption_is_classified_as_completion_failure():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-read-only-interrupted",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  existingConversationUrl: "https://chatgpt.com/c/existing-review",
  dependencies: {{
    runReviewPromptInNewTab: async () => {{
      const error = new Error("Existing conversation verification interrupted by termination signal");
      error.code = "REVIEW_INTERRUPTED";
      error.reviewPage = page;
      error.reviewBaseline = {{ conversationUrl: "https://chatgpt.com/c/existing-review", conversationId: "existing-review" }};
      error.interruptionSnapshot = {{
        currentUrl: "https://chatgpt.com/",
        conversationId: null,
        assistantText: "",
        checkpointAccepted: false,
      }};
      throw error;
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.failure_stage, "completion");
assert.equal(result.submission, "not_started");
''',
    )


def test_planning_only_transaction_remains_partial_after_technical_completion():
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
assert.equal(result.response_capture, "final");
assert.equal(result.content_evidence_unconfirmed, true);
assert.match(result.failure_reason, /conclusive review outcome/);
'''
    )


def test_structurally_final_response_is_preserved_without_revision_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ existsSync, readFileSync }} from "node:fs";
import {{ mkdir, mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const root = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "review-capture-"));
const planningDir = join(root, "planning");
const finalDir = join(root, "final");
await mkdir(planningDir, {{ recursive: true }});
await mkdir(finalDir, {{ recursive: true }});
const page = {{ close: async () => {{}} }};
const base = (runOutputDir, response) => ({{
  runOutputDir,
  model: "GPT-6.2",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6.2",
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
        response,
      }},
    }}),
    writeResult: async () => {{ }},
  }},
}});

const planning = await runReviewTransaction({{}}, base(planningDir, "I will inspect the pull request and report findings."));
assert.equal(planning.status, "incomplete");
assert.equal(planning.response_capture, "final");
assert.equal(planning.content_evidence_unconfirmed, true);
assert.equal(existsSync(join(planningDir, "response.partial.md")), false);
assert.equal(existsSync(join(planningDir, "response.md")), true);
assert.equal(readFileSync(join(planningDir, "response.md"), "utf8"), "I will inspect the pull request and report findings.\\n");

await mkdir(join(finalDir, "response.partial.md"), {{ recursive: true }});
const final = await runReviewTransaction({{}}, base(finalDir, "Review complete; no findings."));
assert.equal(final.status, "incomplete");
assert.match(final.response_cleanup_warning, /EISDIR|is a directory/i);
assert.equal(final.response_capture, "final");
assert.equal(final.content_evidence_unconfirmed, true);
assert.equal(existsSync(join(finalDir, "response.md")), true);
assert.equal(readFileSync(join(finalDir, "response.md"), "utf8"), "Review complete; no findings.\\n");
assert.equal(existsSync(join(finalDir, "response.partial.md")), true);

await rm(root, {{ recursive: true, force: true }});
''',
    )


def test_pre_response_interruption_persists_identity_without_stale_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const writes = [];
const page = {{ close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-pre-response-interruption",
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
      currentUrl: "https://chatgpt.com/c/bootstrap",
      conversationId: "bootstrap",
    }}),
    waitForReviewCompletion: async (_page, {{ onSnapshot }}) => {{
      await onSnapshot({{
        checkpointAccepted: true,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/real-review",
        conversationId: "real-review",
        assistantMessageId: "old-assistant",
        assistantTurnCount: 1,
        assistantText: "Old response from before submission",
      }});
      return {{
        status: "interrupted",
        checkpointAccepted: true,
        responseTurnObserved: false,
        currentUrl: "https://chatgpt.com/c/real-review",
        conversationId: "real-review",
        assistantMessageId: "old-assistant",
        assistantTurnIndex: 0,
        response: "Old response from before submission",
        failureReason: "visible response interruption",
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/real-review");
assert.equal(result.conversation_id, "real-review");
assert.deepEqual(writes, []);
'''
    )


def test_exception_recovery_prefers_real_url_and_rejects_stale_assistant_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const writes = [];
let completionCalls = 0;
const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/real-review",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-exception-recovery",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  dependencies: {{
    runReviewPromptInNewTab: async () => {{
      return {{
        page,
        model: "GPT-6",
        effort: "High",
        promptSubmitted: true,
        submission: "acknowledged",
        dispatchState: "acknowledged",
        currentUrl: "https://chatgpt.com/",
        conversationId: null,
      }};
    }},
    waitForReviewCompletion: async () => {{
      completionCalls += 1;
      if (completionCalls === 1) {{
        const error = new Error("page lost during completion");
        error.reviewPage = page;
        error.reviewBaseline = {{ conversationUrl: "https://chatgpt.com/", conversationId: null }};
        throw error;
      }}
      return {{
      status: "incomplete",
      checkpointAccepted: true,
      responseTurnObserved: false,
      currentUrl: "https://chatgpt.com/c/real-review",
      conversationId: "real-review",
      assistantMessageId: "old-assistant",
      assistantTurnIndex: 0,
      response: "Old response from before submission",
      failureReason: "bounded completion timeout",
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/real-review");
assert.equal(result.conversation_id, "real-review");
assert.equal(result.assistant_message_id, null);
assert.deepEqual(writes, []);
'''
    )


def test_exception_recovery_promotes_confirmed_completion_after_completion_stage_error():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const writes = [];
let completionCalls = 0;
const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/recovered-review",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-completion-recovery",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: page.url(),
      conversationId: "recovered-review",
    }}),
    waitForReviewCompletion: async () => {{
      completionCalls += 1;
      if (completionCalls === 1) {{
        const error = new Error("page observer failed during completion");
        error.reviewPage = page;
        error.reviewBaseline = {{ conversationUrl: page.url(), conversationId: "recovered-review" }};
        throw error;
      }}
      return {{
        status: "confirmed",
        checkpointAccepted: true,
        responseTurnObserved: true,
        currentUrl: page.url(),
        conversationId: "recovered-review",
        assistantMessageId: "assistant-recovered",
        assistantTurnIndex: 0,
        response: `Reviewed ${{sha}}; no findings.`,
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(result.completion, "confirmed");
assert.equal(result.conversation_id, "recovered-review");
assert.equal(result.failure_stage, null);
assert.deepEqual(writes, [`Reviewed ${{sha}}; no findings.\\n`]);
'''
    )


def test_exception_recovery_acknowledges_confirmed_response_without_revision_evidence():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/recovered-review-no-marker",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-completion-recovery-no-marker",
  model: "GPT-6.2",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6.2",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: page.url(),
      conversationId: "recovered-review-no-marker",
    }}),
    waitForReviewCompletion: async () => {{
      const error = new Error("page observer failed during completion");
      error.reviewPage = page;
      error.reviewBaseline = {{ conversationUrl: page.url(), conversationId: "recovered-review-no-marker" }};
      if (!globalThis.recoveryAttempted) {{
        globalThis.recoveryAttempted = true;
        throw error;
      }}
      return {{
        status: "confirmed",
        checkpointAccepted: true,
        responseTurnObserved: true,
        currentUrl: page.url(),
        conversationId: "recovered-review-no-marker",
        assistantMessageId: "assistant-recovered",
        assistantTurnIndex: 0,
        response: "Review complete; no findings.",
      }};
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.completion, "confirmed");
assert.equal(result.submission, "acknowledged");
assert.equal(result.dispatch_state, "acknowledged");
assert.equal(result.content_evidence_unconfirmed, true);
assert.equal(result.failure_scope, "review");
assert.equal(result.failure_stage, "completion");
'''
    )


def test_existing_conversation_error_does_not_promote_submission_observer():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const writes = [];
const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/existing-review",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-existing-recovery",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  existingConversationUrl: page.url(),
  dependencies: {{
    runReviewPromptInNewTab: async () => {{
      const error = new Error("page observer failed during existing review");
      error.reviewPage = page;
      error.reviewBaseline = {{ conversationUrl: page.url(), conversationId: "existing-review" }};
      throw error;
    }},
    waitForReviewCompletion: async () => {{ throw new Error("submission observer must not run"); }},
    writeResult: async () => {{}},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.submission, "not_started");
assert.equal(result.completion, "not_started");
assert.equal(result.conversation_id, null);
assert.equal(result.last_visible_conversation_id, "existing-review");
assert.deepEqual(writes, []);
'''
    )


def test_post_dispatch_checkpoint_error_can_recover_confirmed_completion():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const writes = [];
let resultWrites = 0;
const page = {{
  isClosed: () => false,
  url: () => "https://chatgpt.com/c/checkpoint-recovery",
  close: async () => {{}},
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-checkpoint-recovery",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: page.url(),
      conversationId: "checkpoint-recovery",
    }}),
    waitForReviewCompletion: async () => ({{
      status: "confirmed",
      checkpointAccepted: true,
      responseTurnObserved: true,
      currentUrl: page.url(),
      conversationId: "checkpoint-recovery",
      assistantMessageId: "assistant-checkpoint",
      assistantTurnIndex: 0,
      response: `Reviewed ${{sha}}; no findings.`,
    }}),
    writeResult: async () => {{
      resultWrites += 1;
      if (resultWrites === 2) throw new Error("waiting checkpoint write failed");
    }},
    writeResponse: async (_path, content) => writes.push(content),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(result.completion, "confirmed");
assert.equal(result.conversation_id, "checkpoint-recovery");
assert.deepEqual(writes, [`Reviewed ${{sha}}; no findings.\\n`]);
'''
    )


def test_model_unavailable_selection_failure_is_review_scoped():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const selectionError = new Error("requested model is unavailable");
selectionError.code = "MODEL_UNAVAILABLE";
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-model-unavailable",
  model: "GPT-6.2",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [`https://github.com/owner/repo/blob/${{sha}}/file.md`],
  dependencies: {{
    runReviewPromptInNewTab: async () => {{ throw selectionError; }},
    writeResult: async () => {{}},
    closePage: async () => {{}},
  }},
}});

assert.equal(result.status, "blocked");
assert.equal(result.failure_stage, "selection");
assert.equal(result.failure_scope, "review");
assert.equal(result.dispatch_state, "not_dispatched");
'''
    )


def test_launch_fails_promptly_when_chrome_spawn_emits_error():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ EventEmitter }} from "node:events";
import {{ mkdtemp, rm }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ launchDedicatedChrome }} from {CLI_RUNNER.as_uri()!r};

const profile = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "github-review-cdp-error-"));
const chromeProcess = new EventEmitter();
chromeProcess.exitCode = null;
chromeProcess.signalCode = null;
chromeProcess.kill = () => {{
  chromeProcess.exitCode = 1;
  chromeProcess.emit("exit", 1, null);
}};
const spawnError = new Error("Chrome spawn failed");
const launch = launchDedicatedChrome(profile, {{
  spawnProcess: () => {{
    queueMicrotask(() => chromeProcess.emit("error", spawnError));
    return chromeProcess;
  }},
}});
await assert.rejects(launch, /Chrome spawn failed/);
await rm(profile, {{ recursive: true, force: true }});
'''
    )


def test_launch_uses_profile_owned_devtools_port():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile, rm, writeFile }} from "node:fs/promises";
import {{ join }} from "node:path";
import {{ launchDedicatedChrome }} from {CLI_RUNNER.as_uri()!r};

const profile = await mkdtemp(join(process.env.TEMP || process.env.TMP || ".", "github-review-cdp-"));
const chromeProcess = {{ exitCode: 0, signalCode: null }};
let endpointSeen = null;
const conversationUrl = "https://chatgpt.com/c/existing-review";
const launched = await launchDedicatedChrome(profile, {{
  initialUrl: conversationUrl,
  spawnProcess: (_executable, args) => {{
    assert.equal(args.includes("--remote-debugging-port=0"), true);
    assert.equal(args.at(-1), conversationUrl);
    void writeFile(join(profile, "DevToolsActivePort"), "45678\\nprofile-owned-browser\\n");
    return chromeProcess;
  }},
  waitForEndpoint: async (endpoint) => {{ endpointSeen = endpoint; }},
}});
assert.equal(endpointSeen, "http://127.0.0.1:45678");
assert.equal(launched.endpoint, endpointSeen);
assert.equal(launched.port, 45678);
await rm(profile, {{ recursive: true, force: true }});
'''
    )


def test_cdp_startup_timeout_reports_profile_port_and_endpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForChromeCdpEndpoint }} from {CLI_RUNNER.as_uri()!r};

await assert.rejects(
  waitForChromeCdpEndpoint("C:/profiles/review", {{
    readFileImpl: async () => "45678\\nprofile-owned-browser\\n",
    waitForEndpoint: async () => {{ throw new Error("HTTP 404"); }},
    timeoutMs: 1,
    pollIntervalMs: 0,
  }}),
  (error) => {{
    assert.match(error.message, /C:\\/profiles\\/review/);
    assert.match(error.message, /port 45678/);
    assert.match(error.message, /endpoint http:\\/\\/127\\.0\\.0\\.1:45678/);
    return true;
  }},
);
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


def test_signal_cleanup_aborts_observation_before_closing_context():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ installTerminationCleanup }} from {CLI_RUNNER.as_uri()!r};

let closeCount = 0;
let signalCode = null;
const cleanup = installTerminationCleanup({{}}, async () => {{ closeCount += 1; }}, (code) => {{ signalCode = code; }});
process.emit("SIGINT");
await new Promise((resolve) => setImmediate(resolve));
assert.equal(signalCode, 130);
assert.equal(closeCount, 0);
await cleanup.closeOnce();
assert.equal(closeCount, 1);
cleanup();
''',
    )


def test_signal_interruption_rejects_unstable_checkpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForReviewCompletion }} from {RUNNER.as_uri()!r};

let urlReads = 0;
const page = {{
  url: () => [
    "https://chatgpt.com/c/submitted",
    "https://chatgpt.com/c/submitted",
    "https://chatgpt.com/c/other",
    "https://chatgpt.com/c/other",
  ][Math.min(urlReads++, 3)],
  locator: () => ({{
    first() {{ return this; }},
    last() {{ return this; }},
    nth() {{ return this; }},
    count: async () => 0,
    isVisible: async () => false,
    evaluateAll: async () => [],
    innerText: async () => "",
  }}),
  getByRole: () => ({{ first() {{ return this; }}, last() {{ return this; }}, isVisible: async () => false }}),
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => false }}),
}};
const signal = new AbortController();
signal.abort();

await assert.rejects(
  waitForReviewCompletion(page, {{
    baseline: {{ assistantMessageId: null, assistantTurnCount: 0, conversationId: null, submittedPrompt: "" }},
    signal: signal.signal,
  }}),
  (error) => {{
    assert.equal(error.code, "REVIEW_INTERRUPTED");
    assert.equal(error.interruptionSnapshot.routeStable, false);
    assert.equal(error.interruptionSnapshot.checkpointAccepted, false);
    return true;
  }},
);
''',
    )


def test_interrupted_completion_persists_last_conversation_checkpoint():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const persisted = [];
const responses = [];
const page = {{ isClosed: () => false, url: () => "https://chatgpt.com/c/last-review", close: async () => {{}} }};
const interruptionSnapshot = {{
  currentUrl: "https://chatgpt.com/c/last-review",
  conversationId: "last-review",
  assistantMessageId: "assistant-1",
  assistantTurnCount: 1,
  assistantTurnIndex: 0,
  assistantText: "Review for 0123456789abcdef0123456789abcdef01234567: no findings.",
  response: "Review for 0123456789abcdef0123456789abcdef01234567: no findings.",
  responseTurnObserved: true,
  checkpointAccepted: true,
}};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-signal-checkpoint",
  model: "GPT-6",
  effort: "High",
  prompt: "review prompt",
  promptFile: "review.txt",
  repository: "owner/repo",
  commitSha: "0123456789abcdef0123456789abcdef01234567",
  reviewUrls: ["https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md"],
  abortSignal: new AbortController().signal,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      model: "GPT-6",
      effort: "High",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      currentUrl: "https://chatgpt.com/",
      conversationId: null,
    }}),
    waitForReviewCompletion: async () => {{
      const error = new Error("Review completion observation interrupted by termination signal");
      error.code = "REVIEW_INTERRUPTED";
      error.interruptionSnapshot = interruptionSnapshot;
      throw error;
    }},
    writeResult: async (_outputDir, value) => persisted.push(JSON.parse(JSON.stringify(value))),
    writeResponse: async (_path, content) => responses.push(content),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/c/last-review");
assert.equal(result.conversation_id, "last-review");
assert.equal(persisted.at(-1).conversation_url, "https://chatgpt.com/c/last-review");
assert.equal(responses.at(-1), `${{interruptionSnapshot.assistantText}}\\n`);
''',
    )


def test_rejected_interruption_route_stays_last_visible_only():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const page = {{ isClosed: () => false, url: () => "https://chatgpt.com/c/new-route", close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  runOutputDir: "review-output/run-rejected-signal-route",
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
      currentUrl: "https://chatgpt.com/",
      conversationId: null,
    }}),
    waitForReviewCompletion: async () => {{
      const error = new Error("Review completion observation interrupted by termination signal");
      error.code = "REVIEW_INTERRUPTED";
      error.interruptionSnapshot = {{
        currentUrl: "https://chatgpt.com/c/new-route",
        conversationId: "new-route",
        assistantText: "unbound route response",
        responseTurnObserved: true,
        checkpointAccepted: false,
      }};
      throw error;
    }},
    writeResult: async () => {{}},
    writeResponse: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.conversation_url, "https://chatgpt.com/");
assert.equal(result.conversation_id, null);
assert.equal(result.last_visible_conversation_url, "https://chatgpt.com/c/new-route");
assert.equal(result.last_visible_conversation_id, "new-route");
''',
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


def test_batch_continues_after_content_evidence_failure_when_lifecycle_settled():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return calls === 1
      ? {{
          status: "incomplete",
          completion: "confirmed",
          response_capture: "final",
          cleanup_status: "completed",
          submission: "acknowledged",
          dispatch_state: "acknowledged",
          failure_scope: "review",
          failure_stage: "completion",
          content_evidence_unconfirmed: true,
        }}
      : {{
          status: "completed",
          completion: "confirmed",
          cleanup_status: "completed",
          submission: "acknowledged",
          dispatch_state: "acknowledged",
        }};
  }},
  closeContextFn: async () => {{}},
}});

assert.equal(calls, 2);
assert.equal(results.length, 2);
assert.equal(results[0].status, "incomplete");
assert.equal(results[0].content_evidence_unconfirmed, true);
assert.equal(results[1].status, "completed");
'''
    )


def test_batch_stops_when_first_response_is_only_partial():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return {{
      status: "incomplete",
      completion: "incomplete",
      response_capture: "partial",
      dispatch_state: "acknowledged",
      cleanup_status: "completed",
      failure_scope: "review",
      failure_stage: "completion",
    }};
  }},
  closeContextFn: async () => {{}} ,
}});

assert.equal(calls, 1);
assert.equal(results[0].response_capture, "partial");
assert.equal(results[1].status, "skipped");
''',
    )


def test_batch_stops_when_dispatch_evidence_is_missing():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return calls === 1
      ? {{
          status: "incomplete",
          failure_scope: "review",
          cleanup_warning: null,
          submission: "acknowledged",
        }}
      : {{ status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

assert.equal(calls, 1);
assert.equal(results[1].status, "skipped");
'''
    )

def test_batch_continues_after_clean_pre_dispatch_selection_failure():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return calls === 1
      ? {{
          status: "blocked",
          failure_code: "MODEL_SELECTION_FAILED",
          failure_scope: "review",
          dispatch_state: "not_dispatched",
          cleanup_status: "completed",
          cleanup_warning: null,
        }}
      : {{ status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

assert.equal(calls, 2);
assert.equal(results[0].status, "blocked");
assert.equal(results[1].status, "completed");
'''
    )

def test_batch_stops_after_incomplete_existing_conversation_verification():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = [
  {{
    model: "GPT-5.6-Sol",
    effort: "High",
    prompt: `Review ${{reviewUrl}} at ${{sha}}`,
    repository: "owner/repo",
    commitSha: sha,
    reviewUrls: [reviewUrl],
    existingConversationUrl: "https://chatgpt.com/c/existing-review",
    runOutputDir: "review-output/run-existing",
  }},
  {{
    model: "GPT-6.2",
    effort: "High",
    prompt: `Review ${{reviewUrl}} at ${{sha}}`,
    repository: "owner/repo",
    commitSha: sha,
    reviewUrls: [reviewUrl],
    runOutputDir: "review-output/run-next",
  }},
];
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return calls === 1
      ? {{
          status: "incomplete",
          failure_scope: "review",
          failure_stage: "completion",
          failure_reason: "bounded existing conversation verification timeout",
          dispatch_state: "not_dispatched",
          cleanup_status: "completed",
          cleanup_warning: null,
          request_provenance: {{ existing_conversation_url: "https://chatgpt.com/c/existing-review" }},
        }}
      : {{ status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

assert.equal(calls, 1);
assert.equal(results[1].status, "skipped");
'''
    )

def test_batch_does_not_reuse_bootstrap_page_for_review_transactions():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const bootstrapPage = {{ name: "bootstrap" }};
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
const receivedPages = [];
await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo", reviewPage: bootstrapPage }},
  reviews,
  runTransaction: async (_context, options) => {{
    receivedPages.push(options.reviewPage);
    return {{ status: "completed", completion: "confirmed", cleanup_status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

assert.deepEqual(receivedPages, [undefined, undefined]);
''',
    )


def test_parallel_batch_dispatches_all_reviews_before_either_resolves():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
const started = [];
let release;
const gate = new Promise((resolve) => {{ release = resolve; }});
let resolveBothStarted;
const bothStarted = new Promise((resolve) => {{ resolveBothStarted = resolve; }});

const batch = runReviewBatch({{
  mode: "parallel",
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async (_context, options) => {{
    started.push(options.model);
    if (started.length === reviews.length) resolveBothStarted();
    await gate;
    return {{ status: "completed", completion: "confirmed", cleanup_status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

await bothStarted;
assert.deepEqual(started, ["GPT-5.6-Sol", "GPT-6.2"]);
release();
const results = await batch;
assert.deepEqual(results.map((result) => result.status), ["completed", "completed"]);
''',
    )


def test_model_unavailable_continues_only_after_clean_transaction_cleanup():
    run_node_assertion(
        f'''import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
  runOutputDir: `review-output/run-${{model}}`,
}}));
let calls = 0;
const results = await runReviewBatch({{
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async () => {{
    calls += 1;
    return calls === 1
      ? {{
          status: "blocked",
          failure_code: "MODEL_UNAVAILABLE",
          failure_scope: "review",
          dispatch_state: "not_dispatched",
          cleanup_status: "completed",
          cleanup_warning: null,
        }}
      : {{ status: "completed", completion: "confirmed", cleanup_status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});

assert.equal(calls, 2);
assert.equal(results[1].status, "completed");
''',
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
assert.equal(result[0].failure_scope, "review");
assert.equal(result[1].status, "skipped");
assert.equal(result[1].failure_scope, "shared_context");
'''
    )


def test_existing_conversation_completion_rejects_stale_assistant_when_new_user_turn_pending():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
  waitForTimeout: async () => {{ }},
  locator(selector) {{
    const isUserTurn = selector.includes("data-message-author-role=\\\"user\\\"")
      || selector.includes("data-user-message-bubble");
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert")
        ? 0
        : isUserTurn ? 2 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => callback(
        isUserTurn
          ? [
            {{ innerText: "older review request", getAttribute: () => "user-old" }},
            {{ innerText: "new pending review request", getAttribute: () => "user-new" }},
          ]
          : [{{ innerText: "older completed response", getAttribute: () => "assistant-old" }}],
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
  getByText: () => ({{ first() {{ return this; }}, isVisible: async () => true }}),
}};

const snapshots = [];
const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  timeoutMs: 10,
  onSnapshot: async (snapshot) => snapshots.push(snapshot),
}});
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /bounded existing conversation verification timeout/);
assert.equal(snapshots.at(-1).checkpointAccepted, false);
assert.equal(snapshots.at(-1).responseTurnObserved, false);
''',
    )


def test_existing_conversation_completion_rejects_equal_counts_when_latest_user_is_pending():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
  waitForTimeout: async () => {{ }},
  evaluate: async () => ({{
    userTurnCount: 2,
    assistantTurnCount: 2,
    latestAssistantFollowsLatestUser: false,
  }}),
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => callback([
        {{ innerText: "older completed response", getAttribute: () => "assistant-old" }},
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

const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  timeoutMs: 10,
}});
assert.equal(result.status, "incomplete");
''',
    )


def test_existing_conversation_completion_fails_closed_when_turn_order_is_unavailable():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/existing-review",
  waitForTimeout: async () => {{ }},
  evaluate: async () => {{ throw new Error("turn inspection unavailable"); }},
  locator(selector) {{
    return {{
      first() {{ return this; }},
      last() {{ return this; }},
      count: async () => selector.includes("conversation-turn-error") || selector.includes("role=alert") ? 0 : 1,
      isVisible: async () => false,
      evaluateAll: async (callback, includeText) => callback([
        {{ innerText: "older completed response", getAttribute: () => "assistant-old" }},
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

const result = await waitForExistingReviewCompletion(page, {{
  conversationUrl: "https://chatgpt.com/c/existing-review",
  timeoutMs: 10,
}});
assert.equal(result.status, "incomplete");
''',
    )


def test_existing_conversation_completion_accepts_current_visible_markers():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ waitForExistingReviewCompletion }} from {RUNNER.as_uri()!r};

function pageFor(snapshots) {{
  const page = {{
    index: 0,
    evaluate: async () => ({{ userTurnCount: 1, assistantTurnCount: 1, latestAssistantFollowsLatestUser: true }}),
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
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Reviewed the pinned revision; no findings."]] }},
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Reviewed the pinned revision; no findings."]] }},
  {{ url: "https://chatgpt.com/c/existing-review", assistant: [["assistant-1", "Reviewed the pinned revision; no findings."]] }},
]), {{ conversationUrl: "https://chatgpt.com/c/existing-review", timeoutMs: 1000 }});
assert.equal(result.status, "confirmed");
assert.equal(result.conversationId, "existing-review");
assert.equal(result.response, "Reviewed the pinned revision; no findings.");
'''
    )

def test_atomic_write_uses_unique_temp_files_and_retries_transient_windows_rename_errors():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ atomicWrite }} from {CLI_RUNNER.as_uri()!r};

const operations = [];
let moveAttempts = 0;
await atomicWrite("C:/tmp/result.json", "content", {{
  makeTempId: () => "unique-id",
  write: async (path, value, encoding) => operations.push(["write", path, value, encoding]),
  move: async (source, target) => {{
    operations.push(["move", source, target]);
    moveAttempts += 1;
    if (moveAttempts < 3) {{
      const error = new Error("file is temporarily locked");
      error.code = "EPERM";
      throw error;
    }}
  }},
  remove: async (path) => operations.push(["remove", path]),
  sleep: async () => {{}},
}});

assert.equal(moveAttempts, 3);
assert.equal(operations[0][0], "write");
assert.match(operations[0][1], /result\\.json\\.\\d+\\.unique-id\\.tmp$/);
assert.equal(new Set(operations.filter(([kind]) => kind === "move").map(([, source]) => source)).size, 1);
assert.equal(operations.at(-1)[0], "remove");
'''
    )


def test_cli_requires_project_key_for_owned_user_data_dir_mode():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ parseArguments }} from {CLI_RUNNER.as_uri()!r};

const common = [
  "--user-data-dir", "C:/tmp/.codex/profiles/github-review/owner-repo",
  "--model", "GPT-6.2",
  "--effort", "High",
  "--prompt-file", "review.txt",
  "--repository", "owner/repo",
  "--commit-sha", "0123456789abcdef0123456789abcdef01234567",
  "--review-url", "https://github.com/owner/repo/blob/0123456789abcdef0123456789abcdef01234567/file.md",
];

assert.throws(() => parseArguments(common), /Missing required argument: --project-key/);
const options = parseArguments([...common, "--project-key", "owner-repo"]);
assert.equal(options.projectKey, "owner-repo");
'''
    )

def test_capture_mode_reopens_after_delay_and_accepts_partial_response():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let reopenCalls = 0;
let loadStateCalls = 0;
let snapshot;
const page = (url, text) => {{
  const locator = {{
    evaluateAll: async (callback, includeText) => callback([
      {{
        innerText: text,
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }},
    ], includeText),
  }};
  return {{
    url: () => url,
    waitForLoadState: async (state, options) => {{
      loadStateCalls += 1;
      assert.equal(state, "domcontentloaded");
      assert.equal(options.timeout, 15000);
    }},
    locator: () => locator,
  }};
}};
const initialPage = page("https://chatgpt.com/c/review", "I will inspect this later.");
const reopenedPage = page("https://chatgpt.com/c/review", "I will inspect this later.");
const result = await captureReviewResponse(initialPage, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
  reopenPage: async (options) => {{
    reopenCalls += 1;
    assert.equal(options.conversationUrl, "https://chatgpt.com/c/review");
    assert.equal(options.page, initialPage);
    return reopenedPage;
  }},
  onSnapshot: async (value) => {{ snapshot = value; }},
}});

assert.equal(reopenCalls, 1);
assert.equal(loadStateCalls, 1);
assert.equal(result.status, "captured");
assert.equal(result.response, "I will inspect this later.");
assert.equal(snapshot.response, result.response);
''',
    )


def test_capture_mode_retries_when_reopened_page_is_still_navigating():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let attempts = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => {{
      attempts += 1;
      if (attempts === 1) throw new Error("Execution context was destroyed, most likely because of a navigation");
      return callback([{{
        innerText: "Captured after navigation stabilized",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText);
    }},
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
}});

assert.equal(attempts, 3);
assert.equal(result.status, "captured");
assert.equal(result.response, "Captured after navigation stabilized");
''',
    )





def test_capture_mode_resets_stability_after_route_mismatch():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let attempts = 0;
let currentUrl = "https://chatgpt.com/c/review";
const page = {{
  url: () => currentUrl,
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => {{
      attempts += 1;
      currentUrl = attempts === 2
        ? "https://chatgpt.com/"
        : "https://chatgpt.com/c/review";
      return callback([{{
        innerText: "Captured after route stabilization",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText);
    }},
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
}});

assert.equal(attempts, 4);
assert.equal(result.status, "captured");
assert.equal(result.response, "Captured after route stabilization");
''',
    )


def test_capture_mode_waits_for_empty_assistant_container_to_get_text():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let attempts = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: attempts++ === 0 ? "" : "Captured after hydration",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
}});

assert.equal(attempts, 3);
assert.equal(result.response, "Captured after hydration");
''',
    )

def test_capture_mode_rejects_homepage_capture_url():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const page = (url, text) => {{
  const locator = {{
    evaluateAll: async (callback, includeText) => callback([
      {{
        innerText: text,
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }},
    ], includeText),
  }};
  return {{
    url: () => url,
    waitForLoadState: async () => {{}},
    locator: () => locator,
  }};
}};

const initialPage = page("https://chatgpt.com/c/created-review", "Captured response");
let reopenCalls = 0;
const result = await captureReviewResponse(initialPage, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/",
  reopenPage: async (options) => {{
    reopenCalls += 1;
    return initialPage;
  }},
}});

assert.equal(reopenCalls, 0);
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /Canonical conversation URL required/);
''',
    )


def test_capture_mode_marks_missing_output_incomplete():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-empty-capture-"));
const url = "https://chatgpt.com/c/review";
const page = {{ url: () => url }};
const result = await runReviewTransaction({{}}, {{
  existingConversationUrl: url,
  runOutputDir: root,
  reviewPage: page,
  reopenIntervalMs: 0,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      currentUrl: url,
      conversationId: "review",
      readOnlyVerification: true,
      checkpointAccepted: true,
      completion: {{
        status: "captured",
        conversationId: "review",
        currentUrl: url,
        response: "",
        assistantMessageId: null,
        responseTurnObserved: false,
        checkpointAccepted: true,
      }},
    }}),
  }},
}});

assert.equal(result.status, "incomplete");
assert.equal(result.completion, "captured");
assert.match(result.failure_reason, /No visible assistant output was captured/);
''',
    )


def test_capture_mode_persists_visible_empty_assistant_output():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-visible-empty-capture-"));
const url = "https://chatgpt.com/c/review";
const page = {{ url: () => url }};
const result = await runReviewTransaction({{}}, {{
  existingConversationUrl: url,
  runOutputDir: root,
  reviewPage: page,
  reopenIntervalMs: 0,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      currentUrl: url,
      conversationId: "review",
      readOnlyVerification: true,
      checkpointAccepted: true,
      completion: {{
        status: "captured",
        conversationId: "review",
        currentUrl: url,
        response: "",
        assistantMessageId: "assistant-1",
        responseTurnObserved: true,
        checkpointAccepted: true,
      }},
    }}),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(await readFile(join(root, "response.md"), "utf8"), "");
''',
    )


def test_capture_mode_prefers_supplied_existing_thread_over_redirected_page_url():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-existing-thread-"));
const threadUrl = "https://chatgpt.com/c/6b0816f9-ef38-83eb-a3ce-15fd11bd2e21";
const homePage = {{ url: () => "https://chatgpt.com/", close: async () => {{}} }};
const reopenedPage = {{
  url: () => threadUrl,
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Captured from the supplied thread.",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};
let reopenedUrl = null;
const result = await runReviewTransaction({{}}, {{
  existingConversationUrl: threadUrl,
  runOutputDir: root,
  reviewPage: homePage,
  reopenIntervalMs: 0,
  reopenPage: async ({{ conversationUrl }}) => {{
    reopenedUrl = conversationUrl;
    return reopenedPage;
  }},
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page: homePage,
      currentUrl: "https://chatgpt.com/",
      conversationId: null,
      readOnlyVerification: true,
      checkpointAccepted: true,
    }}),
  }},
}});

assert.equal(reopenedUrl, threadUrl);
assert.equal(result.status, "completed");
assert.equal(await readFile(join(root, "response.md"), "utf8"), "Captured from the supplied thread.\\n");
''',
    )

def test_capture_mode_rejects_synthetic_conversation_url():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const provisionalUrl = "https://chatgpt.com/c/local-chatgpt%3Aabc";
const canonicalUrl = "https://chatgpt.com/c/6b0816f9-ef38-83eb-a3ce-15fd11bd2e21";
const page = {{
  url: () => canonicalUrl,
}};
const reopenedPage = {{
  url: () => canonicalUrl,
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Captured from the canonical thread.",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};
let reopenedUrl = null;
const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: provisionalUrl,
  reopenPage: async ({{ conversationUrl }}) => {{
    reopenedUrl = conversationUrl;
    return reopenedPage;
  }},
}});

assert.equal(reopenedUrl, null);
assert.equal(result.status, "incomplete");
assert.match(result.failureReason, /Canonical conversation URL required/);
''',
    )

def test_capture_mode_preserves_reopen_failure_root_cause():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-reopen-failure-"));
const url = "https://chatgpt.com/c/review";
const page = {{ url: () => url, close: async () => {{}} }};
const result = await runReviewTransaction({{}}, {{
  model: "GPT-6.2",
  effort: "High",
  prompt: "Review the pinned change.",
  runOutputDir: root,
  reviewPage: page,
  reopenIntervalMs: 0,
  reopenPage: async () => {{ throw new Error("profile reopen failed: browser disconnected"); }},
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      currentUrl: url,
      conversationId: "review",
      promptSubmitted: true,
      submission: "acknowledged",
      dispatchState: "acknowledged",
      model: "GPT-6.2",
      effort: "High",
    }}),
    closePage: async () => {{}},
  }},
}});

assert.equal(result.status, "incomplete");
assert.match(result.failure_reason, /profile reopen failed: browser disconnected/);
''',
    )

def test_capture_mode_persists_partial_response_as_the_captured_result():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-capture-"));
const url = "https://chatgpt.com/c/review";
const page = {{ url: () => url }};
const result = await runReviewTransaction({{}}, {{
  existingConversationUrl: url,
  runOutputDir: root,
  reviewPage: page,
  reopenIntervalMs: 0,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      currentUrl: url,
      conversationId: "review",
      readOnlyVerification: true,
      checkpointAccepted: true,
      completion: {{
        status: "captured",
        conversationId: "review",
        currentUrl: url,
        response: "I will inspect this later.",
        assistantMessageId: "assistant-1",
        responseTurnObserved: true,
        checkpointAccepted: true,
      }},
    }}),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(result.completion, "captured");
assert.equal(await readFile(join(root, "response.md"), "utf8"), "I will inspect this later.\\n");
''',
    )


def test_capture_mode_persists_visible_response_without_turn_association():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ mkdtemp, readFile }} from "node:fs/promises";
import {{ tmpdir }} from "node:os";
import {{ join }} from "node:path";
import {{ runReviewTransaction }} from {CLI_RUNNER.as_uri()!r};

const root = await mkdtemp(join(tmpdir(), "github-review-capture-visible-"));
const url = "https://chatgpt.com/c/review";
const page = {{ url: () => url }};
const result = await runReviewTransaction({{}}, {{
  existingConversationUrl: url,
  runOutputDir: root,
  reviewPage: page,
  reopenIntervalMs: 0,
  dependencies: {{
    runReviewPromptInNewTab: async () => ({{
      page,
      currentUrl: url,
      conversationId: "review",
      readOnlyVerification: true,
      checkpointAccepted: true,
      completion: {{
        status: "captured",
        conversationId: "review",
        currentUrl: url,
        response: "Visible raw response",
        assistantMessageId: "assistant-1",
        responseTurnObserved: false,
        checkpointAccepted: true,
      }},
    }}),
  }},
}});

assert.equal(result.status, "completed");
assert.equal(await readFile(join(root, "response.md"), "utf8"), "Visible raw response\\n");
''',
    )


def test_submit_prompt_waits_for_conversation_route_after_acknowledgement():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ submitPrompt }} from {RUNNER.as_uri()!r};

const prompt = "Review the pinned change.";
let currentUrl = "https://chatgpt.com/";
let composerText = prompt;
const composer = {{
  fill: async (value) => {{ composerText = value; }},
  inputValue: async () => composerText,
  innerText: async () => composerText,
  press: async () => {{}},
}};
const sendButton = {{
  isVisible: async () => true,
  click: async () => {{ composerText = ""; }},
}};
const page = {{
  url: () => currentUrl,
  getByRole: (role, options) => ({{
    first: () => role === "button" ? sendButton : composer,
  }}),
  waitForTimeout: async () => {{ currentUrl = "https://chatgpt.com/c/created-review"; }},
}};

const result = await submitPrompt(page, composer, prompt);
assert.equal(result.currentUrl, "https://chatgpt.com/c/created-review");
assert.equal(result.conversationId, "created-review");
''',
    )


def test_capture_mode_retains_conversation_url_when_submission_page_is_closed():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const closedPage = {{ url: () => {{ throw new Error("Target page, context or browser has been closed"); }} }};
const reopenedPage = {{
  url: () => "https://chatgpt.com/c/review",
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Captured response",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};

const result = await captureReviewResponse(closedPage, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
  reopenPage: async (options) => {{
    assert.equal(options.conversationUrl, "https://chatgpt.com/c/review");
    return reopenedPage;
  }},
}});
assert.equal(result.response, "Captured response");
''',
    )


def test_capture_mode_does_not_capture_stale_assistant_turn_before_submitted_turn():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let assistantReads = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForLoadState: async () => {{}},
  waitForTimeout: async () => {{}},
  locator: (selector) => ({{
    evaluateAll: async (callback, includeText) => {{
      if (selector.includes("data-message-author-role=\\\"user\\\"")) {{
        return callback([{{
          innerText: "latest prompt",
          getAttribute: (name) => name === "data-message-id" ? "user-2" : null,
        }}], includeText);
      }}
      assistantReads += 1;
      const stale = assistantReads < 3;
      return callback([{{
        innerText: stale ? "Older response" : "Latest response",
        getAttribute: (name) => name === "data-message-id" ? (stale ? "assistant-1" : "assistant-2") : null,
      }}], includeText);
    }},
  }}),
  evaluate: async () => ({{
    latestAssistantFollowsLatestUser: assistantReads >= 3,
  }}),
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
  submittedPrompt: "latest prompt",
  submittedUserTurnId: "user-2",
}});

assert.equal(result.status, "captured");
assert.equal(result.response, "Latest response");
assert.ok(assistantReads >= 4);
''',
    )


def test_capture_mode_requires_a_repeated_visible_sample_before_capture():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let reads = 0;
const page = {{
  url: () => "https://chatgpt.com/c/review",
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => {{
      reads += 1;
      return callback([{{
        innerText: reads === 1 ? "Still streaming" : "Stable response",
        getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
      }}], includeText);
    }},
  }}),
  waitForTimeout: async () => {{}},
}};

const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
}});

assert.equal(result.status, "captured");
assert.equal(result.response, "Stable response");
assert.ok(reads >= 3);
''',
    )


def test_capture_mode_rejects_visible_output_from_wrong_conversation():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/c/other",
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Wrong conversation output",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};
const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/c/review",
}});
assert.equal(result.response, "");
assert.equal(result.checkpointAccepted, false);
assert.equal(result.responseTurnObserved, false);
''',
    )


def test_capture_mode_rejects_homepage_as_conversation_url():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

const page = {{
  url: () => "https://chatgpt.com/",
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: "Homepage output",
      getAttribute: (name) => name === "data-message-id" ? "assistant-1" : null,
    }}], includeText),
  }}),
}};
const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/",
}});
assert.equal(result.response, "");
assert.equal(result.checkpointAccepted, false);
assert.equal(result.responseTurnObserved, false);
''',
    )

def test_capture_mode_does_not_reopen_homepage_when_thread_url_is_unavailable():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let reopenCalls = 0;
const page = {{
  url: () => "https://chatgpt.com/",
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([], includeText),
  }}),
}};
const result = await captureReviewResponse(page, {{
  intervalMs: 0,
  conversationUrl: "https://chatgpt.com/",
  reopenPage: async () => {{
    reopenCalls += 1;
    throw new Error("homepage must not be reopened as a capture destination");
  }},
}});

assert.equal(reopenCalls, 0);
assert.equal(result.response, "");
assert.equal(result.checkpointAccepted, false);
assert.equal(result.responseTurnObserved, false);
''',
    )


def test_parallel_capture_lock_serializes_capture_operations():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ captureReviewResponse }} from {RUNNER.as_uri()!r};

let active = 0;
let maximumActive = 0;
let tail = Promise.resolve();
const captureLock = async (operation) => {{
  const previous = tail;
  let release;
  tail = new Promise((resolve) => {{ release = resolve; }});
  await previous;
  active += 1;
  maximumActive = Math.max(maximumActive, active);
  try {{ return await operation(); }} finally {{ active -= 1; release(); }}
}};
const page = (id) => ({{
  url: () => `https://chatgpt.com/c/${{id}}`,
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: `Response ${{id}}`,
      getAttribute: (name) => name === "data-message-id" ? `assistant-${{id}}` : null,
    }}], includeText),
  }}),
}});

await Promise.all(["one", "two"].map((id) => captureReviewResponse(page(id), {{
  intervalMs: 0,
  conversationUrl: `https://chatgpt.com/c/${{id}}`,
  captureLock,
}})));
assert.equal(maximumActive, 1);
''',
    )


def test_existing_conversation_capture_uses_parallel_capture_lock():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewPromptInNewTab }} from {RUNNER.as_uri()!r};

let active = 0;
let maximumActive = 0;
let tail = Promise.resolve();
const captureLock = async (operation) => {{
  const previous = tail;
  let release;
  tail = new Promise((resolve) => {{ release = resolve; }});
  await previous;
  active += 1;
  maximumActive = Math.max(maximumActive, active);
  try {{ return await operation(); }} finally {{ active -= 1; release(); }}
}};
let nextPageId = 0;
const context = {{}};
const page = (id) => ({{
  goto: async () => {{}},
  close: async () => {{}},
  getByRole: () => ({{ first: () => ({{ waitFor: async () => {{}}, isVisible: async () => true }}) }}),
  url: () => `https://chatgpt.com/c/${{id}}`,
  waitForLoadState: async () => {{}},
  locator: () => ({{
    evaluateAll: async (callback, includeText) => callback([{{
      innerText: `Response ${{id}}`,
      getAttribute: (name) => name === "data-message-id" ? `assistant-${{id}}` : null,
    }}], includeText),
  }}),
}});

await Promise.all(["one", "two"].map((id) => runReviewPromptInNewTab(context, {{
  existingConversationUrl: `https://chatgpt.com/c/${{id}}`,
  captureIntervalMs: 0,
  captureLock,
  reviewPage: page(id),
}})));
assert.equal(maximumActive, 1);
''',
    )

def test_parallel_dispatch_gate_staggers_second_dispatch_without_waiting_for_generation():
    run_node_assertion(
        f'''
import assert from "node:assert/strict";
import {{ runReviewBatch }} from {CLI_RUNNER.as_uri()!r};

const sha = "0123456789abcdef0123456789abcdef01234567";
const reviewUrl = `https://github.com/owner/repo/blob/${{sha}}/file.md`;
const reviews = ["GPT-5.6-Sol", "GPT-6.2"].map((model) => ({{
  model,
  effort: "High",
  prompt: `Review ${{reviewUrl}} at ${{sha}}`,
  repository: "owner/repo",
  commitSha: sha,
  reviewUrls: [reviewUrl],
}}));
const events = [];
const startedAt = Date.now();
const resultPromise = runReviewBatch({{
  mode: "parallel",
  attached: {{ context: {{}}, projectKey: "owner-repo", repository: "owner/repo" }},
  reviews,
  runTransaction: async (_context, options) => {{
    await options.dispatchGate.beforeDispatch();
    events.push([options.model, Date.now() - startedAt]);
    await new Promise((resolve) => setTimeout(resolve, 40));
    return {{ status: "completed", completion: "captured", cleanup_status: "completed" }};
  }},
  closeContextFn: async () => {{}},
}});
const results = await resultPromise;
assert.deepEqual(results.map((result) => result.status), ["completed", "completed"]);
assert.deepEqual(events.map(([model]) => model), ["GPT-5.6-Sol", "GPT-6.2"]);
assert.ok(events[1][1] - events[0][1] >= 2500);
''',
    )
