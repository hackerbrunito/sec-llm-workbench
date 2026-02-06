# Core Rules (Auto-loaded)

## Tech Stack
- Python 3.11+ (`list[str]`, `X | None`)
- uv (NEVER pip)
- Pydantic v2
- httpx async
- structlog
- pathlib

## Before Write/Edit
Query Context7 MCP for library syntax.

## After Write/Edit
Execute /verify before commit.

## Placeholder Conventions
- `.template` files: `{{ lowercase_snake_case }}` (Cookiecutter standard)
- Documentation: `<angle-brackets>` for example values
- Triggers: `[UPPER_CASE]` for user-substituted values
- Bash: `${VARIABLE}` for environment variables
- Full registry: see `TEMPLATE-MEGAPROMPT-VIBE-CODING.md` § Placeholder Conventions

## Agent Report Persistence

When invoking agents via Task tool, ALWAYS include in the prompt:
> "Save your report to `.ignorar/production-reports/{agent-name}/phase-{N}/{NNN}-phase-{N}-{agent-name}-{slug}.md`"

Directory: `.ignorar/production-reports/{agent}/phase-{N}/`
Numbering: List existing files, find highest number, increment by 1 (or start at 001).

## Workflow Reference
Read `.claude/workflow/` files on demand.
