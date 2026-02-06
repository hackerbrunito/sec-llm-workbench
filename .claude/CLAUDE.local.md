# Local Project Preferences

## Language
Prefer Spanish for comments and documentation, English for code and identifiers.

## Context Management
- Use /clear between unrelated tasks
- After 2 failed corrections, /clear and rewrite prompt
- Monitor context with /context regularly

## Model Strategy
- Planning/architecture: Use Opus (best quality for design decisions)
- Code execution/agents: Use Sonnet (best cost/speed ratio)
- Quick tasks: Use Haiku (lowest cost, fastest)

## Recommended Plugins

Install from `claude-plugins-official` marketplace:

```bash
/plugin install pyright-lsp@claude-plugins-official      # Python type checking LSP
/plugin install security-guidance@claude-plugins-official # Security anti-pattern hooks
/plugin install commit-commands@claude-plugins-official   # Git workflow automation
/plugin install code-review@claude-plugins-official       # Automated PR review (5 agents)
```

## Development Notes
- Active project: SIOPV (~/siopv/)
- Current deadline: March 1, 2026
