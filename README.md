A marketplace of Claude Code plugins for code review, developer tooling, and AI-powered workflows.

![Plugin marketplace in Claude Code](docs/plugins.png)

## Install

From within a Claude Code session:

```
/plugin marketplace add scristobal/claude-plugins
```

Then browse and install plugins with `/plugin` > Discover.

## Plugins

| Plugin | Description |
|--------|-------------|
| **codex-review** | Consensus code review through deliberation between Claude and Codex. Both models independently review code, then debate findings until they agree. |
| **code-review** | Apply code review comments from `.code-review.md` files. Companion skill for [scristobal/code-review.nvim](https://github.com/scristobal/code-review.nvim). |
| **lsp-servers** | LSP server configurations for rust-analyzer, clangd, sourcekit-lsp, kotlin-lsp, lua-language-server, ty, tsgo, and gleam. |
