#!/usr/bin/env node
// worker/githubAutomation.js — GitHub Actions automation handler
// Runs via: node worker/githubAutomation.js (from .github/workflows/automation.yml)
const { Octokit } = require("octokit");
const fs = require("fs");

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

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

  if (labels.length > 0) {
    await octokit.issues.addLabels({
      owner,
      repo,
      issue_number: number,
      labels,
    });
    console.log(`Issue #${number}: added labels [${labels.join(", ")}]`);
  }
}

async function handlePullRequest(payload) {
  const { pull_request } = payload;
  const { number } = pull_request;
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;

  await octokit.issues.addLabels({
    owner,
    repo,
    issue_number: number,
    labels: ["needs-review"],
  });
  console.log(`PR #${number}: added label [needs-review]`);
}

async function main() {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  const eventName = process.env.GITHUB_EVENT_NAME;

  if (!eventPath || !eventName) {
    console.error("Missing GITHUB_EVENT_PATH or GITHUB_EVENT_NAME");
    process.exit(1);
  }

  const payload = JSON.parse(fs.readFileSync(eventPath, "utf8"));
  console.log(`Event: ${eventName}`);

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
