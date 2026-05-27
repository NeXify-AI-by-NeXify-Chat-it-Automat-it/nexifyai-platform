#!/usr/bin/env node
// worker/githubAutomation.js — GitHub Actions automation handler
// Version: 2.0 — added auto-merge, risk classification, PM API integration
// Runs via: node worker/githubAutomation.js (from .github/workflows/automation.yml)
const { Octokit } = require("octokit");
const fs = require("fs");
const http = require("http");

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });
const PM_API_URL = process.env.PM_API_URL || "http://127.0.0.1:8421";
const PM_API_TOKEN = process.env.PM_API_TOKEN || "pm_local_dev_token";

// ─── Safety Classification ───────────────────────────────────────────────────
// Determines if a PR is low-risk enough for auto-merge.
// Only auto-merge if ALL conditions are met.

const SAFE_LABELS = new Set(["auto-merge", "dependencies", "docs-only", "governance", "ci"]);
const BLOCKING_LABELS = new Set(["security", "bug", "blocked", "needs-review", "needs-triage", "secret-leak"]);
const SAFE_BOTS = new Set(["dependabot[bot]", "dependabot-preview[bot]", "renovate[bot]", "github-actions[bot]", "snyk-bot"]);

async function isSafeForAutoMerge(pullRequest, labels) {
  const author = pullRequest.user.login;
  const title = (pullRequest.title || "").toLowerCase();
  const body = (pullRequest.body || "").toLowerCase();

  const labelNames = labels.map((l) => (typeof l === "string" ? l : l.name));

  // ─── Positive eligibility FIRST ─────────────────────────────────────────
  // Check safe conditions BEFORE blocking labels to avoid self-block:
  // Automation adds needs-review to new PRs, then checks eligibility and
  // finds needs-review → returns false. Chicken-egg self-block.
  const hasAutoMergeLabel = labelNames.includes("auto-merge");
  const hasDependenciesLabel = labelNames.includes("dependencies");
  const isBotPR = SAFE_BOTS.has(author);
  const isDependencyUpdate = /(?:update|bump|upgrade|dependabot|renovate)/i.test(title) &&
    /(?:dependenc|action|npm|pip|package|docker)/i.test(title + " " + body);
  const isDocsGovernance = labelNames.includes("docs-only") || labelNames.includes("governance");
  const isLowRiskChange = labelNames.includes("documentation") || labelNames.includes("adr");
  const isCIConfigChange = labelNames.includes("ci");

  let safeReason = null;
  if (isBotPR || isDependencyUpdate || hasDependenciesLabel) {
    safeReason = "bot_or_dependency";
  } else if (hasAutoMergeLabel) {
    safeReason = "auto_merge_label";
  } else if (isDocsGovernance || isLowRiskChange) {
    safeReason = "docs_governance";
  } else if (isCIConfigChange) {
    safeReason = "ci_only";
  }

  if (safeReason) {
    // If positively eligible, only block on CRITICAL labels (security, bug, blocked, secret-leak)
    // NOT needs-review/needs-triage (automation adds those itself)
    const criticalBlockers = ["security", "bug", "blocked", "secret-leak"];
    for (const label of labelNames) {
      if (criticalBlockers.includes(label)) {
        console.log(`  → Blocked by critical label: "${label}"`);
        return { safe: false, reason: `Critical label: ${label}` };
      }
    }
    console.log(`  → Safe: ${safeReason} (author=${author})`);
    return { safe: true, reason: safeReason, method: "squash" };
  }

  // ─── No positive match — check ALL blocking labels ──────────────────────
  for (const label of labelNames) {
    if (BLOCKING_LABELS.has(label)) {
      console.log(`  → Blocked by label: "${label}"`);
      return { safe: false, reason: `Blocking label: ${label}` };
    }
  }

  console.log(`  → Not eligible for auto-merge (author=${author})`);
  return { safe: false, reason: "not_eligible" };
}

// ─── Enable Auto-Merge via GitHub API ────────────────────────────────────────
// Uses GitHub's native auto-merge feature which waits for all required CI checks.
// REST API docs: PUT /repos/{owner}/{repo}/pulls/{pull_number}/auto-merge

async function enableAutoMerge(owner, repo, pullNumber, mergeMethod) {
  console.log(`Enabling auto-merge for PR #${pullNumber} (method: ${mergeMethod})`);

  // Step 1: Post a comment indicating auto-merge was triggered
  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: pullNumber,
    body: [
      `🤖 **Auto-Merge aktiviert**`,
      ``,
      `Diese PR wurde als sicher eingestuft.`,
      `Methode: \`${mergeMethod}\``,
      ``,
      `Auto-Merge wird automatisch ausgeführt, sobald alle CI-Checks bestanden sind.`,
    ].join('\n'),
  });

  // Step 2: Enable native GitHub auto-merge (waits for all required checks)
  // Uses the PUT /repos/{owner}/{repo}/pulls/{pull_number}/auto-merge REST endpoint
  // This is the canonical way to enable auto-merge via REST API v3
  try {
    await octokit.request("PUT /repos/{owner}/{repo}/pulls/{pull_number}/auto-merge", {
      owner,
      repo,
      pull_number: pullNumber,
      merge_method: mergeMethod,
    });
    console.log(`✅ Auto-merge enabled for PR #${pullNumber}`);
    return { success: true };
  } catch (error) {
    // If the native auto-merge endpoint isn't available (older GitHub Enterprise),
    // log the error and inform via comment — do NOT attempt immediate merge
    console.error(`Auto-merge API failed for PR #${pullNumber}:`, error.message);

    // Post a comment explaining the situation instead of an unreliable fallback
    await octokit.rest.issues.createComment({
      owner,
      repo,
      issue_number: pullNumber,
      body: [
        `⚠️ **Auto-Merge konnte nicht aktiviert werden**`,
        ``,
        `Grund: ${error.message}`,
        ``,
        `Bitte manuell mergen, sobald alle CI-Checks bestanden sind.`,
      ].join('\n'),
    }).catch(() => {}); // non-fatal if comment fails

    return { success: false, error: error.message };
  }
}

// ─── PM API Integration ──────────────────────────────────────────────────────

function sendToPMApi(endpoint, payload) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(payload);
    const options = {
      hostname: new URL(PM_API_URL).hostname,
      port: new URL(PM_API_URL).port || 8421,
      path: endpoint,
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Content-Length": Buffer.byteLength(data),
        Authorization: `Bearer ${PM_API_TOKEN}`,
      },
    };
    const req = http.request(options, (res) => {
      let body = "";
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => resolve({ status: res.statusCode, body }));
    });
    req.on("error", (err) => {
      console.warn(`PM API call failed (${endpoint}): ${err.message}`);
      resolve(null); // non-fatal
    });
    req.write(data);
    req.end();
  });
}

// ─── Event Handlers ──────────────────────────────────────────────────────────

async function handleIssue(payload) {
  const { issue } = payload;
  const { number } = issue;
  const title = issue.title.toLowerCase();
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;

  const labels = [];
  if (title.includes("bug")) {
    labels.push("bug", "needs-triage");
  }
  if (title.includes("security")) {
    labels.push("security", "priority-p0");
  }
  if (title.includes("auto-merge") || title.includes("automerge")) {
    labels.push("auto-merge");
  }

  if (labels.length > 0) {
    await octokit.rest.issues.addLabels({
      owner,
      repo,
      issue_number: number,
      labels,
    });
    console.log(`Issue #${number}: added labels [${labels.join(", ")}]`);
  }
}

async function handlePullRequest(payload) {
  const { pull_request, action } = payload;
  const { number } = pull_request;
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;
  const isNewPr = action === "opened" || action === "reopened" || action === "ready_for_review";
  const isUpdated = action === "synchronize" || action === "labeled" || action === "unlabeled";

  console.log(`PR #${number}: action=${action} author=${pull_request.user.login}`);

  // Step 1: Get current labels BEFORE any changes
  const { data: currentLabels } = await octokit.rest.issues.listLabelsOnIssue({
    owner,
    repo,
    issue_number: number,
  });


  // Step 3: Check auto-merge eligibility
  const assessment = await isSafeForAutoMerge(pull_request, currentLabels);

  // Step 4: Send evaluation to PM API for tracking
  try {
    await sendToPMApi("/worker/auto-merge-evaluation", {
      task_id: `pr-${number}`,
      pull_request: number,
      status: assessment.safe ? "auto_merge_eligible" : "not_eligible",
      reason: assessment.reason,
      action,
      author: pull_request.user.login,
    });
  } catch (_) {
    // PM API may not be available — non-fatal
  }

  // Step 5: Enable auto-merge if safe
  if (assessment.safe) {
    const result = await enableAutoMerge(owner, repo, number, assessment.method);
    if (result.success) {
      // Update label from needs-review to auto-merge
      await octokit.rest.issues.removeLabel({
        owner,
        repo,
        issue_number: number,
        name: "needs-review",
      }).catch(() => {}); // label may not exist

      await octokit.rest.issues.addLabels({
        owner,
        repo,
        issue_number: number,
        labels: ["auto-merge"],
      });
      console.log(`PR #${number}: auto-merge enabled, label updated`);
    }
  } else {
    console.log(`PR #${number}: ${assessment.reason || "not eligible for auto-merge"}`);
  }
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  const eventName = process.env.GITHUB_EVENT_NAME;

  if (!eventPath || !eventName) {
    console.error("Missing GITHUB_EVENT_PATH or GITHUB_EVENT_NAME");
    process.exit(1);
  }

  const payload = JSON.parse(fs.readFileSync(eventPath, "utf8"));
  console.log(`Event: ${eventName} | Repository: ${payload.repository?.full_name}`);

  if (eventName === "issues") {
    await handleIssue(payload);
  } else if (eventName === "pull_request" || eventName === "pull_request_target") {
    await handlePullRequest(payload);
  } else {
    console.log(`Unhandled event: ${eventName}`);
  }
}

main().catch((err) => {
  console.error("Automation failed:", err.message);
  process.exit(1);
});
