# Vibe Coding 2026 Plugin

A comprehensive Claude Code plugin for Python 2026 development with:

- 8 specialized agents (code-implementer + 5 verification + 2 research)
- 16 skills for domain-specific patterns
- 12 lifecycle hooks for enforcement and traceability
- Reflexion Loop (PRA) workflow with human-in-the-loop checkpoints
- Self-correcting error system (errors-to-rules)
- Full traceability (JSONL logging + session summaries)

## Installation

Copy the `.claude/` directory to your project root, or install via Claude Code plugin manager.

## Requirements

- Python 3.11+
- uv (package manager)
- Node.js (for Context7 MCP)
- ruff, mypy, pytest
