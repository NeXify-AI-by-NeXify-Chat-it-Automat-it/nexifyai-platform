#!/usr/bin/env node
import { Octokit } from "octokit";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

export async function handleIssue(context: { issue: any; payload: any }) {
  const { issue, payload } = context;
  const { number } = issue;
  const title = issue.title.toLowerCase();
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;

  if (title.includes("bug")) {
    await octokit.rest.issues.addLabels({
      owner,
      repo,
      issue_number: number,
      labels: ["bug", "needs-triage"],
    });
  }
}

export async function handlePullRequest(context: { payload: any }) {
  const { payload } = context;
  const { pull_request } = payload;
  const { number } = pull_request;
  const owner = payload.repository.owner.login;
  const repo = payload.repository.name;

  // Add needs-review label to all new PRs
  await octokit.rest.issues.addLabels({
    owner,
    repo,
    issue_number: number,
    labels: ["needs-review"],
  });
}

export const handler = async (context: { payload: any; issue?: any }) => {
  const { event_type } = context.payload;
  if (event_type === "issues") {
    await handleIssue(context);
  } else if (event_type === "pull_request") {
    await handlePullRequest(context);
  }
};
