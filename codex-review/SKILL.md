---
name: codex-review
description: >
  Get an independent code review from Codex (a separate AI model) via its MCP server.
  Use this skill whenever the user asks for a code review, wants feedback on their changes,
  says "review my code", "review this", "what do you think of these changes", "check my work",
  "does this look right", or wants a second opinion on code. Also trigger when the user
  mentions "codex review", asks to "run a review", or wants another model to look at their code.
  Even casual requests like "any issues with this?" or "how does this look?" should trigger this skill
  when there are code changes in the working tree.
---

# Codex Code Review

Get an independent code review from Codex via its MCP server. The review runs in a subagent so Codex can work independently without blocking your conversation.

## Prerequisites

The Codex MCP server must be configured in `.mcp.json`:
```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

## Workflow

### 1. Gather the diff

Run `git diff HEAD` to capture all uncommitted changes. If the diff is empty, tell the user there are no changes to review and stop.

If there are untracked files the user wants reviewed, read those files and include their contents alongside the diff.

### 2. Spawn the review agent

Use the Agent tool to spawn a subagent for the review. Read the agent instructions from `agents/reviewer.md` (relative to this skill's directory) and pass them as the agent prompt, along with:

- The full git diff
- The user's explanation of their goal
- The current working directory path

Example agent prompt:
```
[contents of agents/reviewer.md]

---

## Your task

Working directory: /path/to/project
Author's goal: [user's explanation]

Diff to review:
[git diff output]
```

### 3. Present the review

The agent will return a formatted summary report with findings organized by severity (critical/warning/suggestion) and a verdict. Present this to the user.

Save the `THREAD_ID` from the agent's response — you'll need it for follow-ups.

### 4. Handle follow-ups

If the user wants to discuss a finding, ask about alternatives, or push back on a recommendation, call `mcp__codex__codex-reply` with the saved `threadId` and the user's follow-up question. This continues the conversation with Codex so it has full context.

## Tips

- Always include the user's goal/context — it helps Codex distinguish intentional decisions from mistakes.
- For large diffs (500+ lines), tell the agent to ask Codex to focus on the most-changed files first, then follow up on the rest.
- The review runs in read-only sandbox mode. Codex inspects the code but never modifies it.
