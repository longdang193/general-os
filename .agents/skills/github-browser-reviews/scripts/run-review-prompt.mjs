import { MENU_TRANSITION_TIMEOUT_MS, selectReviewModel } from "./select-review-model.mjs";

const CHATGPT_URL = "https://chatgpt.com/";
export const UI_ACTION_TIMEOUT_MS = 5000;
export const COMPOSER_READINESS_TIMEOUT_MS = 30000;
export const SUBMISSION_ACK_TIMEOUT_MS = 10000;
export const SUBMISSION_ACK_POLL_MS = 50;
export const SUBMITTED_TURN_ID_TIMEOUT_MS = 2000;
export const AMBIGUOUS_DISPATCH_TIMEOUT_MS = 15000;
export const ASSISTANT_TURN_SELECTOR = '[data-message-author-role="assistant"]:visible:not([data-message-author-role="assistant"] [data-message-author-role="assistant"]), [data-response-body]:visible';
const ASSISTANT_FALLBACK_SELECTOR = 'main [class*="MarkdownRoot-"]:visible:not(.rich-text-user-turn)';
const ASSISTANT_TURN_SELECTORS = [ASSISTANT_TURN_SELECTOR, ASSISTANT_FALLBACK_SELECTOR];
const USER_TURN_SELECTOR = '[data-message-author-role="user"]:visible:not([data-message-author-role="user"] [data-message-author-role="user"]), [data-user-message-bubble="true"]:visible';
export const INTERRUPTION_PATTERN = /(?:something went wrong|network error|response interrupted|stopped responding)/i;
export const INTERRUPTION_UI_SELECTOR = '[data-testid="conversation-turn-error"]:visible, [data-testid="response-error"]:visible, [data-testid="error-message"]:visible';
const GENERIC_ALERT_SELECTOR = '[role="alert"]:visible';
export const COMPLETION_TIMEOUT_MS = 900000;
const COMPLETION_INITIAL_BACKOFF_MS = 250;
const COMPLETION_MAX_BACKOFF_MS = 1000;

export class ReviewPromptError extends Error {
  constructor(message, failureScope, cause) {
    super(message);
    this.name = "ReviewPromptError";
    this.failureScope = failureScope;
    if (cause) this.cause = cause;
  }
}
function withFailureScope(error, failureScope) {
  if (error?.failureScope) return error;
  const message = error instanceof Error ? error.message : String(error);
  const sharedScope = error?.code === "MODEL_UNAVAILABLE" || error?.code === "AUTHENTICATION_REQUIRED";
  const wrapped = new ReviewPromptError(message, sharedScope ? "shared_context" : failureScope, error);
  if (error && typeof error === "object") {
    wrapped.reviewPage = error.reviewPage;
    wrapped.reviewBaseline = error.reviewBaseline;
    wrapped.submissionAttempted = error.submissionAttempted === true;
    wrapped.dispatchState = error.dispatchState || null;
    wrapped.visibleEvidence = error.visibleEvidence || null;
  }
  return wrapped;
}
function normalizeComposerText(value) {
  return value.replace(/\s+/g, " ").trim();
}
function normalizePromptText(value) {
  return normalizeComposerText(value).replace(/\s*`n\s*/g, "`n");
}

function isChallengeEvidence(evidence) {
  const content = `${evidence?.currentUrl || ""} ${evidence?.visibleText || ""}`;
  return /(?:cloudflare|challenge-platform|verify you are human|checking your browser|just a moment|human verification)/i.test(content);
}

function assertPrompt(prompt) {
  if (typeof prompt !== "string" || prompt.trim() === "") {
    throw new Error("prompt must be a non-empty string");
  }
}

async function waitForVisibleComposer(composer) {
  try {
    await composer.waitFor({ state: "visible", timeout: COMPOSER_READINESS_TIMEOUT_MS });
    return await composer.isVisible();
  } catch {
    return false;
  }
}

async function assertComposerReadinessCanRetry(page) {
  const evidence = await captureVisibleEvidence(page).catch(() => null);
  if (isChallengeEvidence(evidence)) {
    throw new ReviewPromptError("ChatGPT challenge page blocked the authenticated composer", "shared_context");
  }
  if (evidence?.loginVisible) {
    throw new ReviewPromptError("ChatGPT authentication is required for the dedicated profile", "shared_context");
  }
}

async function openChatGPT(page) {
  if (!page.url().startsWith("https://chatgpt.com/")) {
    await page.goto(CHATGPT_URL, { timeout: COMPOSER_READINESS_TIMEOUT_MS });
  }

  const composer = page.getByRole("textbox", { name: "Ask ChatGPT" }).first();
  if (await waitForVisibleComposer(composer)) return composer;

  await assertComposerReadinessCanRetry(page);
  if (typeof page.reload === "function") {
    try {
      await page.reload({ timeout: COMPOSER_READINESS_TIMEOUT_MS, waitUntil: "domcontentloaded" });
    } catch {
      // Continue to the bounded post-refresh readiness check.
    }
    if (await waitForVisibleComposer(composer)) return composer;
  }

  await assertComposerReadinessCanRetry(page);
  throw new Error("Authenticated ChatGPT composer was not found");
}

export async function captureVisibleEvidence(page) {
  if (!page) return null;
  let currentUrl = null;
  try {
    currentUrl = typeof page.url === "function" ? page.url() : null;
  } catch {
    currentUrl = null;
  }
  let visibleText = "";
  try {
    visibleText = (await page.locator("body").innerText({ timeout: UI_ACTION_TIMEOUT_MS }))
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 4000);
  } catch {
    visibleText = "";
  }
  let composerVisible = false;
  try {
    composerVisible = await page.getByRole("textbox", { name: "Ask ChatGPT" }).first().isVisible();
  } catch {
    composerVisible = false;
  }
  let loginVisible = false;
  try {
    loginVisible = await page.getByRole("button", { name: /^(Log in|Sign up)$/i }).first().isVisible();
  } catch {
    loginVisible = false;
  }
  return {
    currentUrl,
    visibleText,
    composerVisible,
    loginVisible,
  };
}

export async function preflightAuthenticatedContext(context, existingPage = null) {
  let page;
  let failure;
  const ownsPage = !existingPage;
  try {
    page = existingPage || await context.newPage();
    await openChatGPT(page);
  } catch (error) {
    failure = withFailureScope(error, "shared_context");
  }

  if (failure && page) {
    failure.visibleEvidence = await captureVisibleEvidence(page);
  }

  try {
    if (ownsPage && page) await page.close();
  } catch (error) {
    failure ||= withFailureScope(error, "shared_context");
  }

  if (failure) throw failure;
  return { authenticated: true };
}

/**
 * Open a new ChatGPT tab from an existing authenticated Playwright context.
 * The context must already own the user's authenticated session.
 */
export async function openReviewTab(context) {
  let page;
  try {
    page = await context.newPage();
  } catch (error) {
    throw withFailureScope(error, "shared_context");
  }
  try {
    await openChatGPT(page);
    return page;
  } catch (error) {
    const visibleEvidence = await captureVisibleEvidence(page).catch(() => null);
    const failureScope = isChallengeEvidence(visibleEvidence) ? "shared_context" : "review";
    const scopedError = withFailureScope(error, failureScope);
    if (visibleEvidence) scopedError.visibleEvidence = visibleEvidence;
    await page.close().catch(() => {});
    throw scopedError;
  }
}

async function closeModelMenu(page) {
  const menu = page.getByRole("menu", { name: "Select ChatGPT model" }).first();
  if (!(await menu.isVisible())) return;

  await page.keyboard.press("Escape", { timeout: MENU_TRANSITION_TIMEOUT_MS });
  await menu.waitFor({ state: "hidden", timeout: MENU_TRANSITION_TIMEOUT_MS });
}

export function extractConversationIdentity(url) {
  const match = url.match(/\/c\/([^/?#]+)/);
  if (!match) return null;
  try {
    return decodeURIComponent(match[1]);
  } catch {
    return match[1];
  }
}

export function normalizeExistingConversationUrl(value) {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error("existing conversation URL must be a non-empty ChatGPT conversation URL");
  }
  let parsed;
  try {
    parsed = new URL(value.trim());
  } catch {
    throw new Error(`Invalid existing conversation URL: ${value}`);
  }
  if (!(parsed.protocol === "https:" && ["chatgpt.com", "www.chatgpt.com"].includes(parsed.hostname))) {
    throw new Error(`Existing conversation URL must use https://chatgpt.com/c/<id>: ${value}`);
  }
  const conversationId = extractConversationIdentity(parsed.href);
  const pathConversationId = parsed.pathname.replace(/^\/c\//, "").replace(/\/+$/g, "");
  let decodedPathConversationId = null;
  try {
    decodedPathConversationId = decodeURIComponent(pathConversationId);
  } catch {
    // Keep invalid route segments on the existing validation failure path.
  }
  if (!conversationId || !pathConversationId || pathConversationId.includes("/") || decodedPathConversationId !== conversationId) {
    throw new Error(`Existing conversation URL must use https://chatgpt.com/c/<id>: ${value}`);
  }
  return `https://chatgpt.com/c/${encodeURIComponent(conversationId)}`;
}

export async function readVisibleInterruption(page) {
  const interruption = page.locator(INTERRUPTION_UI_SELECTOR).first();
  if ((await interruption.count()) > 0 && await interruption.isVisible()) return true;

  const alert = page.locator(GENERIC_ALERT_SELECTOR).first();
  if ((await alert.count()) === 0 || !(await alert.isVisible())) return false;
  return INTERRUPTION_PATTERN.test(normalizeComposerText(await alert.innerText({ timeout: UI_ACTION_TIMEOUT_MS })));
}

async function readVisibleAssistantMessage(page, { includeText = true } = {}) {
  for (const selector of ASSISTANT_TURN_SELECTORS) {
    const turns = page.locator(selector);
    let snapshots;
    if (typeof turns.evaluateAll === "function") {
      snapshots = await turns.evaluateAll((elements, readText) => elements.map((element) => ({
        assistantMessageId: ["data-message-id", "data-turn-id", "data-chatgpt-selection-message-id", "data-response-body", "data-testid", "id"]
          .map((attribute) => element.getAttribute(attribute))
          .find(Boolean) || null,
        assistantText: readText ? (element.innerText || "").trim() : "",
      })), includeText);
    } else {
      const count = await turns.count();
      if (count === 0) continue;

      const selected = turns.nth(count - 1);
      let assistantMessageId = null;
      for (const attribute of ["data-message-id", "data-turn-id", "data-testid", "id"]) {
        const value = await selected.getAttribute(attribute, { timeout: UI_ACTION_TIMEOUT_MS });
        if (value) {
          assistantMessageId = value;
          break;
        }
      }

      snapshots = [{
        assistantMessageId,
        assistantText: includeText ? (await selected.innerText({ timeout: UI_ACTION_TIMEOUT_MS })).trim() : "",
      }];
    }

    if (snapshots.length === 0) continue;

    const selected = snapshots[snapshots.length - 1];
    return {
      assistantMessageId: selected.assistantMessageId || `visible-assistant-turn-${snapshots.length - 1}`,
      assistantText: selected.assistantText,
      assistantTurnCount: snapshots.length,
    };
  }

  return {
    assistantMessageId: null,
    assistantText: "",
    assistantTurnCount: 0,
  };
}

async function hasSubmittedUserTurn(page, prompt, submittedUserTurnId = null) {
  if (!prompt) return true;
  try {
    const turns = page.locator(USER_TURN_SELECTOR);
    const snapshots = await turns.evaluateAll((elements) => elements.map((element) => ({
      id: element.getAttribute("data-message-id")
        || element.getAttribute("data-user-message-id")
        || element.getAttribute("data-testid")
        || element.id
        || null,
      text: element.innerText || "",
    })));
    const expectedPrompt = normalizePromptText(prompt);
    if (submittedUserTurnId) return snapshots.some((snapshot) => snapshot.id === submittedUserTurnId);
    return snapshots.some((snapshot) => normalizePromptText(snapshot.text).includes(expectedPrompt));
  } catch {
    return false;
  }
}

export async function readSubmittedUserTurnId(page, prompt, { timeoutMs = SUBMITTED_TURN_ID_TIMEOUT_MS } = {}) {
  if (!prompt) return null;
  const deadline = Date.now() + timeoutMs;
  const expectedPrompt = normalizePromptText(prompt);
  let firstAttempt = true;
  while (firstAttempt || Date.now() <= deadline) {
    firstAttempt = false;
    try {
      const turns = page.locator(USER_TURN_SELECTOR);
      const snapshots = await turns.evaluateAll((elements) => elements.map((element) => ({
        id: element.getAttribute("data-message-id")
          || element.getAttribute("data-user-message-id")
          || element.getAttribute("data-testid")
          || element.id
          || null,
        text: element.innerText || "",
      })));
      const submittedTurnId = snapshots
        .filter((snapshot) => snapshot.id && normalizePromptText(snapshot.text).includes(expectedPrompt))
        .at(-1)?.id || null;
      if (submittedTurnId) return submittedTurnId;
    } catch {
      // The SPA may replace the conversation turn while routing after dispatch.
    }

    const remaining = deadline - Date.now();
    if (remaining <= 0 || typeof page.waitForTimeout !== "function") break;
    await page.waitForTimeout(Math.min(SUBMISSION_ACK_POLL_MS, remaining));
  }
  return null;
}

export async function isPromptVisibleInComposer(composer, prompt) {
  const expectedPrompt = normalizePromptText(prompt);

  try {
    if (normalizePromptText(await composer.inputValue()) === expectedPrompt) return true;
  } catch {
    // Contenteditable composers do not expose inputValue.
  }

  return normalizePromptText(await composer.innerText()) === expectedPrompt;
}

async function readCompletionSnapshot(page, { includeText } = {}) {
  const stopButton = page.getByRole("button", { name: /^(Stop generating|Stop response)$/i }).first();
  const generating = await stopButton.isVisible();
  const assistantMessage = await readVisibleAssistantMessage(page, {
    includeText: includeText ?? !generating,
  });
  const responseAction = page.getByRole("button", { name: /^(Regenerate response|Rate response|Feedback)$/i }).last();
  const composer = page.getByRole("textbox", { name: "Ask ChatGPT" }).first();
  const currentUrl = page.url();
  const conversationId = extractConversationIdentity(currentUrl);
  let responseCompleteVisible = false;
  if (typeof page.getByText === "function") {
    try {
      responseCompleteVisible = await page.getByText("Response complete", { exact: true }).first().isVisible();
    } catch {
      responseCompleteVisible = false;
    }
  }

  let responseActionsReady = false;
  let assistantTurnScopeAvailable = false;
  try {
    const assistantTurns = page.locator(ASSISTANT_TURN_SELECTOR);
    const assistantTurnCount = await assistantTurns.count();
    if (assistantTurnCount > 0) {
      const currentAssistantTurn = assistantTurns.nth(assistantTurnCount - 1);
      const scopedResponseAction = currentAssistantTurn.getByRole("button", { name: /^(Regenerate response|Rate response|Feedback)$/i }).last();
      assistantTurnScopeAvailable = true;
      responseActionsReady = await scopedResponseAction.isVisible();
      if (!responseActionsReady) {
        responseActionsReady = await currentAssistantTurn.getByText("Response complete", { exact: true }).first().isVisible();
      }
    }
  } catch {
    responseActionsReady = false;
  }
  if (!assistantTurnScopeAvailable && !responseActionsReady) responseActionsReady = await responseAction.isVisible() || responseCompleteVisible;

  return {
    ...assistantMessage,
    composerReady: await composer.isVisible() && !generating,
    conversationId,
    currentUrl,
    generating,
    interrupted: await readVisibleInterruption(page),
    responseActionsReady,
  };
}

export function evaluateReviewCompletion({
  assistantMessageId,
  assistantText,
  assistantTurnCount,
  baselineAssistantTurnCount,
  composerReady,
  conversationId,
  expectedConversationId = null,
  generationObserved,
  generating,
  interrupted,
  responseActionsReady,
  stableSampleCount,
  submittedTurnObserved = true,
  allowStableTextFallback = false,
}) {
  return !generating
    && !interrupted
    && Boolean(conversationId)
    && (!expectedConversationId || conversationId === expectedConversationId)
    && Boolean(assistantMessageId)
    && assistantTurnCount > baselineAssistantTurnCount
    && Boolean(assistantText.trim())
    && (responseActionsReady && stableSampleCount >= 1 && (generationObserved || assistantTurnCount > baselineAssistantTurnCount)
      || allowStableTextFallback && composerReady && stableSampleCount >= 2)
    && submittedTurnObserved;
}

export async function submitPrompt(page, composer, prompt, { beforeSubmit } = {}) {
  await composer.fill(prompt, { timeout: UI_ACTION_TIMEOUT_MS });

  if (!(await isPromptVisibleInComposer(composer, prompt))) {
    throw new Error("Prompt was not visibly entered");
  }

  const sendButton = page.getByRole("button", { name: /^(Send|Send message|Submit)$/i }).first();
  if (beforeSubmit) await beforeSubmit();
  let dispatchState = "not_dispatched";
  try {
    if (await sendButton.isVisible()) {
      dispatchState = "possibly_dispatched";
      await sendButton.click({ timeout: UI_ACTION_TIMEOUT_MS });
    } else {
      dispatchState = "possibly_dispatched";
      await composer.press("Enter", { timeout: UI_ACTION_TIMEOUT_MS });
    }
  } catch (error) {
    error.submissionAttempted = dispatchState !== "not_dispatched";
    error.dispatchState = dispatchState;
    throw error;
  }

  try {
    const deadline = Date.now() + SUBMISSION_ACK_TIMEOUT_MS;
    while (await isPromptVisibleInComposer(composer, prompt)) {
      const remaining = deadline - Date.now();
      if (remaining <= 0) {
        const error = new Error("Prompt submission was not visibly acknowledged");
        error.submissionAttempted = true;
        error.dispatchState = "possibly_dispatched";
        throw error;
      }
      await page.waitForTimeout(Math.min(SUBMISSION_ACK_POLL_MS, remaining));
    }
  } catch (error) {
    error.submissionAttempted = true;
    error.dispatchState ||= "possibly_dispatched";
    throw error;
  }

  const currentUrl = page.url();
  return {
    currentUrl,
    conversationId: extractConversationIdentity(currentUrl),
    submissionConversationId: extractConversationIdentity(currentUrl),
    dispatchState: "acknowledged",
    submission: "acknowledged",
  };
}

async function prepareReviewPrompt(page, { model, effort }) {
  const composer = await openChatGPT(page);
  try {
    await selectReviewModel(page, { model, effort });
  } catch (error) {
    throw withFailureScope(error, "review");
  }
  await closeModelMenu(page);
  return { composer, effort, model };
}

/**
 * Navigate an existing authenticated ChatGPT page, select the requested
 * review model and effort, fill the prompt, and submit it exactly once.
 *
 * The caller owns the browser session. This helper never launches a browser,
 * authenticates, retries, or reruns a review request.
 */
export async function waitForReviewCompletion(page, {
  baseline,
  timeoutMs = COMPLETION_TIMEOUT_MS,
  initialTimeoutMs = null,
  completionTimeoutMs = timeoutMs,
  onSnapshot,
  acceptSnapshot = () => true,
} = {}) {
  if (!baseline) throw new Error("baseline is required for completion observation");

  const initialDeadline = Date.now() + (initialTimeoutMs ?? timeoutMs);
  let deadline = initialDeadline;
  let ambiguityActive = initialTimeoutMs !== null && initialTimeoutMs !== undefined;
  let backoffMs = COMPLETION_INITIAL_BACKOFF_MS;
  let previousText = "";
  let previousAssistantTurnCount = null;
  let generationObserved = false;
  let stableSampleCount = 0;
  let snapshot;
  let baselineAssistantTurnCount = baseline.assistantTurnCount;
  let expectedConversationId = baseline.conversationId || null;
  let responseConversationId = null;
  let submittedUserTurnId = baseline.submittedUserTurnId || null;
  let submittedTurnAnchorObserved = false;
  let submittedTurnAnchorConversationId = null;
  let conversationTransitionDeadline = null;
  let handoffConversationId = null;
  let handoffAssistantText = null;
  let handoffResponseProgressed = false;
  const submissionConversationId = baseline.submissionConversationId || null;
  const syntheticSubmissionRoute = submissionConversationId?.startsWith("local-chatgpt:") === true;
  const submissionAcknowledged = baseline.submission === "acknowledged"
    || baseline.dispatchState === "acknowledged";

  while (Date.now() <= deadline) {
    if (await readVisibleInterruption(page)) {
      const interruptedSnapshot = await readCompletionSnapshot(page, { includeText: true });
      const submittedTurnObserved = await hasSubmittedUserTurn(page, baseline.submittedPrompt, submittedUserTurnId);
      const responseTurnObserved = interruptedSnapshot.generating
        || interruptedSnapshot.assistantTurnCount > baselineAssistantTurnCount
        || Boolean(interruptedSnapshot.assistantMessageId && interruptedSnapshot.assistantMessageId !== baseline.assistantMessageId);
      if (submittedTurnObserved && (!expectedConversationId || interruptedSnapshot.conversationId === expectedConversationId)) {
        if (onSnapshot) await onSnapshot({ ...interruptedSnapshot, responseTurnObserved });
      }
      return {
        ...interruptedSnapshot,
        response: interruptedSnapshot.assistantText,
        responseTurnObserved,
        status: "interrupted",
        checkpointAccepted: submittedTurnObserved
          && (!expectedConversationId || interruptedSnapshot.conversationId === expectedConversationId),
        failureReason: "visible response interruption",
      };
    }

    snapshot = await readCompletionSnapshot(page);
    const conversationChanged = !responseConversationId
      && expectedConversationId
      && snapshot.conversationId
      && snapshot.conversationId !== expectedConversationId;
    if (conversationChanged) {
      if (handoffConversationId !== snapshot.conversationId) {
        handoffConversationId = snapshot.conversationId;
        handoffAssistantText = snapshot.assistantText;
        handoffResponseProgressed = snapshot.generating;
      } else if (snapshot.generating || snapshot.assistantText !== handoffAssistantText) {
        handoffResponseProgressed = true;
      }
    }
    if (conversationChanged && conversationTransitionDeadline === null) {
      conversationTransitionDeadline = Date.now() + Math.min(COMPOSER_READINESS_TIMEOUT_MS, timeoutMs);
    }
    if (!submittedUserTurnId && baseline.submittedPrompt) {
      submittedUserTurnId = await readSubmittedUserTurnId(page, baseline.submittedPrompt, { timeoutMs: 0 });
    }
    let submittedTurnObserved = (submittedTurnAnchorObserved
      && (!snapshot.conversationId || snapshot.conversationId === submittedTurnAnchorConversationId))
      || await hasSubmittedUserTurn(page, baseline.submittedPrompt, submittedUserTurnId);
    if (submittedTurnObserved) {
      submittedTurnAnchorObserved = true;
      submittedTurnAnchorConversationId = snapshot.conversationId || submittedTurnAnchorConversationId;
    }
    const acknowledgedSubmissionAssistantTurn = submissionAcknowledged
      && baselineAssistantTurnCount === 0
      && submissionConversationId
      && snapshot.conversationId === submissionConversationId
      && snapshot.assistantTurnCount > baselineAssistantTurnCount
      && Boolean(snapshot.assistantMessageId && snapshot.assistantMessageId !== baseline.assistantMessageId);
    if (acknowledgedSubmissionAssistantTurn) {
      submittedTurnObserved = true;
      submittedTurnAnchorObserved = true;
    }
    if (responseConversationId && snapshot.conversationId && snapshot.conversationId !== responseConversationId) {
      return {
        ...snapshot,
        response: snapshot.assistantText,
        status: "incomplete",
        checkpointAccepted: false,
        failureReason: "conversation identity changed after response evidence was bound",
      };
    }
    if (conversationChanged) {
      const transitionFreshnessObserved = syntheticSubmissionRoute && handoffResponseProgressed;
      const newAssistantTurnObserved = transitionFreshnessObserved
        || Boolean(snapshot.assistantMessageId && snapshot.assistantMessageId !== baseline.assistantMessageId);
      const durableTurnAnchorObserved = Boolean(submittedUserTurnId)
        || acknowledgedSubmissionAssistantTurn
        || syntheticSubmissionRoute && submittedTurnObserved
        || transitionFreshnessObserved;
      const newConversationAnchorObserved = newAssistantTurnObserved
        && durableTurnAnchorObserved;
      if (transitionFreshnessObserved) {
        submittedTurnObserved = true;
        submittedTurnAnchorObserved = true;
        submittedTurnAnchorConversationId = snapshot.conversationId;
      }
      if (!newConversationAnchorObserved) {
        if (submissionAcknowledged && baselineAssistantTurnCount === 0) {
          await page.waitForTimeout(backoffMs);
          backoffMs = Math.min(backoffMs * 2, COMPLETION_MAX_BACKOFF_MS);
          continue;
        }
        if (conversationTransitionDeadline !== null && Date.now() <= conversationTransitionDeadline) {
          await page.waitForTimeout(backoffMs);
          backoffMs = Math.min(backoffMs * 2, COMPLETION_MAX_BACKOFF_MS);
          continue;
        }
        return {
          ...snapshot,
          response: snapshot.assistantText,
          status: "incomplete",
          checkpointAccepted: false,
          failureReason: "conversation identity changed before submitted user turn identity was bound",
        };
      }
      expectedConversationId = snapshot.conversationId;
      const newAssistantTurn = transitionFreshnessObserved
        || (snapshot.assistantMessageId && snapshot.assistantMessageId !== baseline.assistantMessageId);
      baselineAssistantTurnCount = snapshot.generating || newAssistantTurn
        ? Math.max(0, snapshot.assistantTurnCount - 1)
        : snapshot.assistantTurnCount;
    }
    if (!expectedConversationId && snapshot.conversationId) expectedConversationId = snapshot.conversationId;
    generationObserved ||= snapshot.generating;
    const responseTurnObserved = snapshot.generating
      || snapshot.assistantTurnCount > baselineAssistantTurnCount
      || (conversationChanged && (handoffResponseProgressed
        || Boolean(snapshot.assistantMessageId && snapshot.assistantMessageId !== baseline.assistantMessageId)));
    const responseEvidenceObserved = responseTurnObserved
      || snapshot.responseActionsReady;
    if (onSnapshot && submittedTurnObserved) {
      await onSnapshot({ ...snapshot, checkpointAccepted: true, responseTurnObserved });
    }
    if (!responseConversationId && responseTurnObserved && snapshot.conversationId && submittedTurnObserved) {
      responseConversationId = snapshot.conversationId;
      expectedConversationId = responseConversationId;
    }
    if (ambiguityActive && responseEvidenceObserved) {
      deadline = Date.now() + completionTimeoutMs;
      ambiguityActive = false;
    }
    const sameAssistantTurn = previousAssistantTurnCount === null
      || snapshot.assistantTurnCount === previousAssistantTurnCount;
    if (snapshot.assistantText === previousText
      && (sameAssistantTurn || snapshot.responseActionsReady)
      && snapshot.assistantText) {
      stableSampleCount += 1;
    } else {
      stableSampleCount = 0;
      previousText = snapshot.assistantText;
    }
    previousAssistantTurnCount = snapshot.assistantTurnCount;

    if (evaluateReviewCompletion({
      ...snapshot,
      baselineAssistantTurnCount,
      expectedConversationId,
      generationObserved,
      stableSampleCount,
      submittedTurnObserved,
      allowStableTextFallback: true,
    }) && await acceptSnapshot(snapshot)) {
      return {
        ...snapshot,
        assistantTurnIndex: snapshot.assistantTurnCount - 1,
        response: snapshot.assistantText,
        status: "confirmed",
        checkpointAccepted: true,
        responseTurnObserved: true,
      };
    }

    await page.waitForTimeout(backoffMs);
    backoffMs = Math.min(backoffMs * 2, COMPLETION_MAX_BACKOFF_MS);
  }

  const finalSnapshot = await readCompletionSnapshot(page, { includeText: true });
  const finalSubmittedTurnObserved = (submittedTurnAnchorObserved
    && (!finalSnapshot.conversationId || finalSnapshot.conversationId === submittedTurnAnchorConversationId))
    || await hasSubmittedUserTurn(page, baseline.submittedPrompt, submittedUserTurnId);
  const finalResponseTurnObserved = finalSnapshot.generating
    || finalSnapshot.assistantTurnCount > baselineAssistantTurnCount
    || Boolean(finalSnapshot.assistantMessageId && finalSnapshot.assistantMessageId !== baseline.assistantMessageId);
  const finalCheckpointAccepted = (!expectedConversationId || finalSnapshot.conversationId === expectedConversationId)
    && finalSubmittedTurnObserved;
  if (onSnapshot && finalCheckpointAccepted) {
    await onSnapshot({ ...finalSnapshot, checkpointAccepted: true, responseTurnObserved: finalResponseTurnObserved });
  }
  return {
    ...finalSnapshot,
    response: finalSnapshot.assistantText,
    responseTurnObserved: finalResponseTurnObserved,
    status: "incomplete",
    checkpointAccepted: finalCheckpointAccepted,
    failureReason: "bounded completion timeout or ambiguous response association",
  };
}

export async function waitForExistingReviewCompletion(page, {
  conversationUrl,
  timeoutMs = COMPLETION_TIMEOUT_MS,
  onSnapshot,
} = {}) {
  const expectedConversationUrl = normalizeExistingConversationUrl(conversationUrl);
  const expectedConversationId = extractConversationIdentity(expectedConversationUrl);
  const deadline = Date.now() + timeoutMs;
  let previousText = "";
  let previousMessageId = null;
  let stableSampleCount = 0;
  let snapshot;

  while (Date.now() <= deadline) {
    snapshot = await readCompletionSnapshot(page, { includeText: true });
    if (snapshot.conversationId !== expectedConversationId) {
      return {
        ...snapshot,
        response: snapshot.assistantText,
        status: "incomplete",
        checkpointAccepted: false,
        failureReason: "existing conversation identity changed during verification",
      };
    }
    if (snapshot.interrupted) {
      if (onSnapshot) await onSnapshot({ ...snapshot, checkpointAccepted: true });
      return {
        ...snapshot,
        response: snapshot.assistantText,
        status: "interrupted",
        checkpointAccepted: true,
        failureReason: "visible response interruption",
      };
    }
    if (onSnapshot) await onSnapshot(snapshot);
    const sameMessage = !snapshot.assistantMessageId
      || !previousMessageId
      || snapshot.assistantMessageId === previousMessageId;
    if (snapshot.assistantText === previousText
      && (sameMessage || snapshot.responseActionsReady)
      && snapshot.assistantText) {
      stableSampleCount += 1;
    } else {
      stableSampleCount = 0;
      previousText = snapshot.assistantText;
    }
    previousMessageId = snapshot.assistantMessageId;

    if (evaluateReviewCompletion({
      ...snapshot,
      assistantTurnCount: 1,
      baselineAssistantTurnCount: 0,
      expectedConversationId,
      stableSampleCount,
    }) && snapshot.responseActionsReady) {
      return {
        ...snapshot,
        assistantTurnIndex: Math.max(0, snapshot.assistantTurnCount - 1),
        response: snapshot.assistantText,
        status: "confirmed",
        checkpointAccepted: true,
      };
    }
    await page.waitForTimeout(COMPLETION_INITIAL_BACKOFF_MS);
  }

  const finalSnapshot = await readCompletionSnapshot(page, { includeText: true });
  const finalCheckpointAccepted = finalSnapshot.conversationId === expectedConversationId;
  if (onSnapshot && finalCheckpointAccepted) await onSnapshot({ ...finalSnapshot, checkpointAccepted: true });
  return {
    ...finalSnapshot,
    response: finalSnapshot.assistantText,
    status: "incomplete",
    checkpointAccepted: finalCheckpointAccepted,
    failureReason: "bounded existing conversation verification timeout",
  };
}

export async function runReviewPrompt(page, { beforeSubmit, model, effort, prompt }) {
  assertPrompt(prompt);
  const { composer } = await prepareReviewPrompt(page, { model, effort });
  const baselineAssistant = await readVisibleAssistantMessage(page, { includeText: false });
  const baseline = {
    assistantMessageId: baselineAssistant.assistantMessageId,
    assistantTurnCount: baselineAssistant.assistantTurnCount,
    conversationId: extractConversationIdentity(page.url()),
    conversationUrl: page.url(),
    submittedPrompt: normalizePromptText(prompt),
  };
  let submission;
  try {
    submission = await submitPrompt(page, composer, prompt, { beforeSubmit });
  } catch (error) {
    error.reviewBaseline = baseline;
    error.submissionAttempted = error.submissionAttempted === true;
    error.dispatchState ||= "not_dispatched";
    throw error;
  }

  return {
    ...baseline,
    ...submission,
    submittedUserTurnId: await readSubmittedUserTurnId(page, prompt),
    model,
    effort,
    promptSubmitted: true,
  };
}

export async function runReviewPromptInNewTab(context, options = {}) {
  const hasExistingConversationUrl = Object.prototype.hasOwnProperty.call(options, "existingConversationUrl")
    && options.existingConversationUrl !== undefined;
  const existingConversationUrl = hasExistingConversationUrl
    ? normalizeExistingConversationUrl(options.existingConversationUrl)
    : null;
  const ownsPage = !options.reviewPage;
  const page = options.reviewPage || await openReviewTab(context);
  try {
    if (!ownsPage && !options.existingConversationUrl) {
      await page.goto(CHATGPT_URL, { timeout: COMPOSER_READINESS_TIMEOUT_MS });
    }
    if (!ownsPage) await openChatGPT(page);
    if (existingConversationUrl) {
      await page.goto(existingConversationUrl, { timeout: COMPOSER_READINESS_TIMEOUT_MS });
      const completion = await waitForExistingReviewCompletion(page, {
        conversationUrl: existingConversationUrl,
        onSnapshot: options.onSnapshot,
      });
      return {
        page,
        ...completion,
        completion,
        model: null,
        effort: null,
        modelVerified: null,
        effortVerified: null,
        promptSubmitted: false,
        readOnlyVerification: true,
        submission: "not_attempted",
        dispatchState: "not_dispatched",
      };
    }
    return { page, ...(await runReviewPrompt(page, options)) };
  } catch (error) {
    if (error && typeof error === "object") {
      error.reviewPage = page;
      if (existingConversationUrl && !error.reviewBaseline) {
        const conversationUrl = existingConversationUrl;
        error.reviewBaseline = {
          conversationUrl,
          conversationId: extractConversationIdentity(conversationUrl),
          assistantMessageId: null,
          assistantTurnCount: 0,
        };
      }
      if (!error.visibleEvidence) error.visibleEvidence = await captureVisibleEvidence(page).catch(() => null);
    }
    if (!error?.reviewBaseline && ownsPage) await page.close().catch(() => {});
    throw withFailureScope(error, "review");
  }
}
