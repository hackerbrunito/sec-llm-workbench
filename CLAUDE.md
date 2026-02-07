# META-PROYECTO: Framework Vibe Coding 2026

## CRITICAL RULES

**YOU MUST** at session start:
1. Read @.claude/workflow/01-session-start.md
2. Read project specification if working on a project

**YOU MUST** when writing code:
3. Query Context7 MCP before using external libraries
4. Follow @.claude/workflow/02-reflexion-loop.md

**YOU MUST** before commit:
5. Execute `/verify` (runs 5 verification agents)
6. Follow @.claude/workflow/05-before-commit.md

**IMPORTANT** - Human checkpoints:
7. See @.claude/workflow/03-human-checkpoints.md

## References (read on demand)

| Topic | File |
|-------|------|
| Session start | @.claude/workflow/01-session-start.md |
| Reflexion Loop | @.claude/workflow/02-reflexion-loop.md |
| Human checkpoints | @.claude/workflow/03-human-checkpoints.md |
| Agents | @.claude/workflow/04-agents.md |
| Before commit | @.claude/workflow/05-before-commit.md |
| Auto decisions | @.claude/workflow/06-decisions.md |
| Error history | @.claude/docs/errors-to-rules.md |

## On-Demand References (loaded via skills, NOT at startup)

| Topic | Skill / File |
|-------|-------------|
| Orchestrator invocation | `/orchestrator-protocol` or read `.claude/workflow/07-orchestrator-invocation.md` |
| Python standards | `/coding-standards-2026` skill |
| Techniques catalog | `/techniques-reference` or read `.claude/docs/techniques.md` |

## Compact Instructions

When compacting context, preserve:
- Current project name and phase
- Active task description and progress
- Pending verification file list
- Error patterns from errors-to-rules.md
- Key architectural decisions made in this session
