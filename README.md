A marketplace of Claude Code plugins for code review, developer tooling, and AI-powered workflows.

| Plugin | Description |
|--------|-------------|
| **codex-review** | Consensus code review through deliberation between Claude and Codex. Both models independently review code, then debate findings until they agree. See [evaluation results](plugins/codex-review/evaluation/results.md).<br>Requires [codex](https://github.com/openai/codex) installed. |
| **code-review** | Apply code review comments from `.code-review.md` files.<br>Companion skill for [scristobal/code-review.nvim](https://github.com/scristobal/code-review.nvim). |
| **rust-analyzer-lsp** | LSP server configuration for rust-analyzer. |
| **clangd-lsp** | LSP server configuration for clangd (C/C++). |
| **sourcekit-lsp** | LSP server configuration for sourcekit-lsp (Swift). |
| **kotlin-lsp** | LSP server configuration for kotlin-lsp. |
| **lua-lsp** | LSP server configuration for lua-language-server. |
| **ty-lsp** | LSP server configuration for ty (Python). |
| **tsgo-lsp** | LSP server configuration for tsgo (TypeScript/JavaScript). |
| **gleam-lsp** | LSP server configuration for gleam. |

From within a Claude Code session:

```
/plugin marketplace add scristobal/claude-plugins
```

Then browse and install plugins with `/plugin` > Discover.

![Plugin marketplace in Claude Code](docs/plugins.png)

