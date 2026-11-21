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
          current().assistant.map(([id, text]) => ({{
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
}};
const stable = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
]), {{ baseline, timeoutMs: 1000 }});
assert.equal(stable.status, "confirmed");
assert.equal(stable.conversationId, "route-2");

const changed = await waitForReviewCompletion(pageFor([
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"]] }},
  {{ url: "https://chatgpt.com/c/route-1", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
  {{ url: "https://chatgpt.com/c/route-2", assistant: [["old", "Previous"], ["new", "Finished review"]] }},
]), {{ baseline, timeoutMs: 1000 }});
assert.equal(changed.status, "incomplete");
assert.match(changed.failureReason, /after response evidence was bound/);
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
      response: "Existing review",
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
          response: "Review",
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
