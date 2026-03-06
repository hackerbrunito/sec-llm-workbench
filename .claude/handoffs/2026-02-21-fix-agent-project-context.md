# Handoff: Fix Hardcoded SIOPV References in Agent Definitions

**Date:** 2026-02-21
**Status:** PENDING — fixes need to be applied and committed
**Branch:** main
**Last commit:** c297618 (fix: remove ruff/mypy/pytest dependency checks from session-start.sh)

---

## What Was Done This Session (COMPLETED)

### 1. Fixed session-start.sh (committed as c297618)
Removed ruff/mypy/pytest global dependency checks from the meta-project hook. These tools live in project venvs (e.g. `~/siopv/.venv/`), not globally installed. The hook was failing on session start because these binaries don't exist on the system PATH.

### 2. Moved 5 stale pending markers
Moved DLP-related pending marker files from `sec-llm-workbench/.build/checkpoints/pending/` to `~/siopv/.build/checkpoints/pending/`. These were left over from a previous SIOPV session where the markers ended up in the wrong project.

### 3. An agent added "Project Context" sections to 6 agent files (PARTIALLY BROKEN)
The agent correctly added a "Project Context (CRITICAL)" section to all 6 agent definition files in `.claude/agents/` and added a "Required: Target Project Path" subsection to `04-agents.md`. The intent is correct (agents must know they operate on a target project, not the meta-project). **However, the agent hardcoded `~/siopv/` as an example in every file**, which is incorrect for a generic framework.

---

## What Needs to Be Done (PENDING)

### Core Problem

`sec-llm-workbench/` is a GENERIC orchestration framework. It must never hardcode a specific project name. The active project is determined dynamically from:
- `projects/*.json` (project registry)
- `.build/active-project` (runtime state, if it exists)
- The invocation prompt from the human

The agent used `~/siopv/` as a concrete example in every file. This must be replaced with a generic placeholder following the convention in `.claude/rules/placeholder-conventions.md`:
- Use `[TARGET_PROJECT]` for user-substituted values (triggers convention)
- Use `<path/to/project>` for documentation example values

---

### Task 1: Fix 6 Agent Definition Files

Each file in `/Users/bruno/sec-llm-workbench/.claude/agents/` has this line:

```
- **Target project path** will be provided in your invocation prompt (e.g. `~/siopv/`)
```

Replace `~/siopv/` with `<path/to/project>` in all 6 files:

- `/Users/bruno/sec-llm-workbench/.claude/agents/code-implementer.md`
- `/Users/bruno/sec-llm-workbench/.claude/agents/best-practices-enforcer.md`
- `/Users/bruno/sec-llm-workbench/.claude/agents/security-auditor.md`
- `/Users/bruno/sec-llm-workbench/.claude/agents/hallucination-detector.md`
- `/Users/bruno/sec-llm-workbench/.claude/agents/code-reviewer.md`
- `/Users/bruno/sec-llm-workbench/.claude/agents/test-generator.md`

The full "Project Context (CRITICAL)" section in each file looks like this (verified in `code-implementer.md`):

```markdown
## Project Context (CRITICAL)

You are being invoked from the **meta-project** (`sec-llm-workbench/`), which is the orchestrator. You are NOT working on the meta-project itself.

- **Target project path** will be provided in your invocation prompt (e.g. `~/siopv/`)
- All file operations (Read, Write, Edit, Glob, Grep) must target the **target project**, not the meta-project
- All git operations (`git add`, `git commit`, `git status`, `git diff`) must run from the **target project directory**
- All `uv run` commands (ruff, mypy, pytest) must run from the **target project directory**
- Never commit target project code to `sec-llm-workbench/`
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project) — this is the only thing that stays in the meta-project
```

The only change needed: replace `` `~/siopv/` `` with `` `<path/to/project>` `` in the example text.

**Verification after fix:**
```bash
grep -r "siopv\|~/siopv\|SIOPV" /Users/bruno/sec-llm-workbench/.claude/agents/
# Expected: no output
```

---

### Task 2: Fix 04-agents.md

File: `/Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md`

Around line 51, the "Required: Target Project Path" subsection says:

```
> "Target project: `~/siopv/` (or the active project path from `.build/active-project`). All file and git operations must use this directory."
```

Replace with:

```
> "Target project: `[TARGET_PROJECT]` — the active project path from `projects/*.json` or `.build/active-project`. All file and git operations must use this directory."
```

This communicates to the orchestrator that it must pass the actual path dynamically when constructing the agent invocation prompt. The `[TARGET_PROJECT]` notation follows the "Triggers" convention from `.claude/rules/placeholder-conventions.md`.

**Verification after fix:**
```bash
grep -n "siopv\|SIOPV" /Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md
# Expected: no output
```

---

### Task 3: Verify post-code.sh (no changes needed, just confirm)

File: `/Users/bruno/sec-llm-workbench/.claude/hooks/post-code.sh`

Lines 86-92 were modified this session to store pending markers in the target project's `.build/`, not the meta-project's. This logic uses `pyproject.toml` detection to find the project root. **No SIOPV hardcoding exists here.** The logic is correct. Just confirm it looks like this:

```bash
if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
    VERIFICATION_DIR="$PROJECT_DIR/.build/checkpoints/pending"
else
    VERIFICATION_DIR="${CLAUDE_PROJECT_DIR:-.}/.build/checkpoints/pending"
fi
```

No changes needed to this file.

---

### Task 4: Check CLAUDE.local.md for hardcoded references

File: `/Users/bruno/sec-llm-workbench/.claude/CLAUDE.local.md`

This file currently contains:
```
## Development Notes
- Active project: SIOPV (~/siopv/)
- Current deadline: March 1, 2026
```

This is the **correct** place to store the active project (it is the local, gitignored configuration that changes per session). No fix needed here — this is intentional user configuration, not a framework hardcoding. Leave it as-is.

---

### Task 5: Commit all changes

After completing Tasks 1 and 2, run the verification to confirm no SIOPV references remain in framework files:

```bash
grep -r "siopv\|~/siopv\|SIOPV" \
  /Users/bruno/sec-llm-workbench/.claude/agents/ \
  /Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md
# Expected: no output
```

Then commit:

```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/ .claude/workflow/04-agents.md
git commit -m "fix: replace hardcoded siopv paths with generic placeholders in agent definitions"
```

**Note:** This is a documentation-only change (markdown files in `.claude/`). The pre-commit hook only blocks `.py` files without verification markers. This commit does not require running `/verify`.

---

## Key Architectural Principle (Do Not Violate)

- `sec-llm-workbench/` is a GENERIC framework for orchestrating ANY Python project
- It must NEVER hardcode a specific project name (SIOPV or anything else)
- The active project is determined dynamically at runtime
- Agent files (`.claude/agents/*.md`) are framework definitions, not project-specific configs
- `CLAUDE.local.md` is the ONLY file allowed to reference the current active project by name (it is gitignored and user-managed)

---

## Placeholder Convention Reference

From `/Users/bruno/sec-llm-workbench/.claude/rules/placeholder-conventions.md`:

| Context | Convention | Example |
|---------|------------|---------|
| Template files | `{{ lowercase_snake_case }}` | `{{ project_name }}` |
| Documentation examples | `<angle-brackets>` | `<path/to/project>` |
| User-substituted triggers | `[UPPER_CASE]` | `[TARGET_PROJECT]` |
| Bash environment vars | `${VARIABLE}` | `${TIMESTAMP}` |

For agent files: use `<path/to/project>` (documentation example convention) since the path shown is illustrative.
For 04-agents.md invocation instructions: use `[TARGET_PROJECT]` (trigger convention) since it signals the orchestrator to substitute the real value.

---

## Files Summary

| File | Status | Action Required |
|------|--------|----------------|
| `.claude/agents/code-implementer.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/agents/best-practices-enforcer.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/agents/security-auditor.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/agents/hallucination-detector.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/agents/code-reviewer.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/agents/test-generator.md` | Has `~/siopv/` | Replace with `<path/to/project>` |
| `.claude/workflow/04-agents.md` | Has `~/siopv/` | Replace with `[TARGET_PROJECT]` |
| `.claude/hooks/post-code.sh` | Clean (no SIOPV) | Verify only, no changes |
| `.claude/CLAUDE.local.md` | Has `~/siopv/` | INTENTIONAL — do not change |
