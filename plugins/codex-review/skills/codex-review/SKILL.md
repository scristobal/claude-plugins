---
name: codex-review
description: >
  Get a consensus code review by running a deliberation between Claude and Codex (a separate AI model).
  Both models independently review the code, then debate their findings until they agree.
  Use this skill whenever the user asks for a code review, wants feedback on their changes,
  says "review my code", "review this", "what do you think of these changes", "check my work",
  "does this look right", or wants a second opinion on code. Also trigger when the user
  mentions "codex review", asks to "run a review", or wants another model to look at their code.
  Even casual requests like "any issues with this?" or "how does this look?" should trigger this skill
  when there are code changes in the working tree.
---

# Codex Code Review

Get a high-confidence code review through deliberation between two independent models. Claude and Codex each review the code separately, then go back and forth to challenge, validate, and reconcile their findings. The result is a consensus review where both models agree — catching more issues and filtering out false positives.

## Prerequisites

This plugin bundles the Codex MCP server. You need `codex` installed and available on your PATH.

## Workflow

### 1. Determine the comparison branch

Use the branch the user specifies. If none is specified, use the repository's default branch (typically `main` or `master`).

### 2. Spawn the review agent

Use the Agent tool to spawn a subagent with the instructions from `${CLAUDE_PLUGIN_ROOT}/agents/reviewer.md`. Pass along:

- The comparison branch name
- The user's explanation of their goal
- The current working directory path

The subagent handles the full deliberation loop with Codex and returns a consensus review.

### 3. Present the review

The agent returns a consensus report with findings both models agreed on. Present it to the user as-is.

Save the `THREAD_ID` from the response — you can use it for follow-ups with Codex via `mcp__codex__codex-reply`.

### 4. Handle follow-ups

If the user wants to discuss a finding, ask about alternatives, or push back on a recommendation, call `mcp__codex__codex-reply` with the saved `threadId` and the user's follow-up question.

## Tips

- Always include the user's goal/context — it helps both models distinguish intentional decisions from mistakes.
- For large diffs (500+ lines), tell the agent to ask Codex to focus on the most-changed files first.
- The review runs in read-only sandbox mode. Codex uses git to inspect changes but never modifies the repository.
