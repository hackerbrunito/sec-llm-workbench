# Agent Report Persistence

When invoking agents via Task tool, ALWAYS include in the prompt:
> "Save your report to `.ignorar/production-reports/{agent-name}/phase-{N}/{NNN}-phase-{N}-{agent-name}-{slug}.md`"

Directory: `.ignorar/production-reports/{agent}/phase-{N}/`
Numbering: List existing files, find highest number, increment by 1 (or start at 001).

## Workflow Reference
Read `.claude/workflow/` files on demand.
