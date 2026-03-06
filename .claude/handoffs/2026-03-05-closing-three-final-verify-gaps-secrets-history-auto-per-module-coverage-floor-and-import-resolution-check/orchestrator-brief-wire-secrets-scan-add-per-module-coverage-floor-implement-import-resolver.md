# Orchestrator Briefing: Close 3 Final /verify Gaps
# Date: 2026-03-05
# Author: Claude Code (main context)
# Purpose: Complete self-contained instructions for orchestrator + all 6 worker agents.
#          The orchestrator reads this file and executes the plan exactly as written.
#          No improvisation. No interpretation. Follow every step literally.

---

## CONTEXT

You are the **orchestrator** for implementing the 3 final improvements to the `/verify`
command in the MetaProject at `/Users/bruno/sec-llm-workbench/`.

This is the MetaProject — not the SIOPV project. All file operations refer to MetaProject
files at `/Users/bruno/sec-llm-workbench/` unless explicitly stated otherwise.

**MetaProject path:** `/Users/bruno/sec-llm-workbench/`

### The 3 gaps being closed:

| # | Gap | What is missing | Solution |
|---|-----|----------------|---------|
| 1 | Secrets history scan is manual | `.claude/scripts/scan-git-history-for-secrets.sh` exists but is not wired into `/verify` | Wire it into SKILL.md as an automatic pre-check |
| 2 | Per-module coverage floor | Coverage gate checks project average (≥75%) but ignores per-module floors | Create a Python script that reads coverage.xml and flags any module below 50% |
| 3 | Import resolution check | No agent detects unresolvable imports (`from x import y` where x or y does not exist) | Create a new agent that uses `ast` + `importlib` to resolve every import |

---

## YOUR ROLE AS ORCHESTRATOR

You coordinate agents. You do NOT read project files, write project files, or implement
anything yourself. Your only tools are: Agent (to spawn), SendMessage (to communicate),
and Read (only for this briefing file).

### Your exact execution steps:

1. Read this briefing file completely before doing anything else
2. Spawn all 2 Wave A agents **simultaneously** (single response with 2 Agent tool calls)
3. Wait for ALL 2 Wave A agents to send you a DONE message via SendMessage
4. Once ALL 2 Wave A agents are DONE: spawn all 3 Wave B agents **simultaneously**
5. Wait for ALL 3 Wave B agents to send you a DONE message via SendMessage
6. Once ALL 3 Wave B agents are DONE: spawn Wave C agent (C1 summarizer)
7. Wait for C1 to send you its DONE message
8. Relay C1's complete message verbatim to the main context (team lead) via SendMessage

### If any agent reports FAILED:
- Stop immediately. Do NOT proceed to the next wave.
- Send the main context (team lead) a message:
  `BLOCKED: Agent <name> reported FAILED. Reason: <copy SUMMARY from agent's message>. Awaiting instructions.`
- Wait for instructions from main context before continuing.

---

## TEAM STRUCTURE

```
Orchestrator (you)
├── Wave A — spawn both simultaneously (new files, no conflicts)
│   ├── A1: Create .claude/agents/import-resolver.md           [new file]
│   └── A2: Create .claude/scripts/check-module-coverage.py   [new file]
│
├── [GATE: Wait for BOTH Wave A agents to report DONE]
│
├── Wave B — spawn all 3 simultaneously (different files, no conflicts)
│   ├── B1: Edit .claude/skills/verify/SKILL.md               [3 changes: secrets auto, coverage floor, import-resolver]
│   ├── B2: Edit .claude/docs/verification-thresholds.md      [2 new entries: import-resolver, per-module coverage]
│   └── B3: Edit .claude/workflow/04-agents.md                [document import-resolver agent]
│
├── [GATE: Wait for ALL 3 Wave B agents to report DONE]
│
└── Wave C — spawn after Wave B completes
    └── C1: Summarizer — verify files, read reports, write summary, relay to orchestrator
```

**Why Wave A before Wave B?**
B1 must read `import-resolver.md` to correctly wire the agent into SKILL.md.
B2 must read `import-resolver.md` to add accurate thresholds.
B3 must read `import-resolver.md` to document the agent correctly.
Therefore Wave A must commit before Wave B begins.

**Why Wave B agents run in parallel?**
B1 edits `SKILL.md`, B2 edits `verification-thresholds.md`, B3 edits `04-agents.md`.
Three completely different files. No merge conflicts possible.

---

## COMMUNICATION PROTOCOL

### What each agent sends you when done

Every agent sends you EXACTLY ONE message when it finishes, in this exact format:

```
AGENT: <agent-id> (<agent-role>)
STATUS: DONE | FAILED
FILE: <exact relative path from MetaProject root>
COMMIT: <7-char git commit hash from `git log --oneline -1`>
SUMMARY: <2-4 sentences: what was done, what was added, any warnings or notes>
UNBLOCKS: NONE | <name of Wave B agent waiting on this Wave A agent>
```

### What you send the main context when C1 is done

Relay C1's complete DONE message verbatim. Do not summarize or paraphrase it.

---

## GIT INSTRUCTIONS FOR ALL AGENTS

Every agent MUST:
1. Complete its task (create or edit its ONE file)
2. Stage ONLY its own file: `git add <exact-file-path>`
3. Commit immediately: `git commit -m "feat: <descriptive message>"`
4. Read the commit hash: `git log --oneline -1`
5. Write report to `.ignorar/production-reports/<agent-name>/2026-03-05-<agent-name>-implementation-report.md`
6. Send DONE message to orchestrator

**CRITICAL:** Never batch commits. Never wait for other agents. Commit immediately after
completing the task. Never use `git add .` or `git add -A` — always use the exact file path.

---

## WAVE A AGENT PROMPTS

### Agent A1: import-resolver creator

**Your name:** A1 (import-resolver creator)
**Your task:** Create ONE new file: `.claude/agents/import-resolver.md`
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`

**Step 1 — Read these files first (in this order):**
1. Read `.claude/agents/dependency-scanner.md` — use as style/format reference for agent files
2. Read `.claude/agents/circular-import-detector.md` — use as secondary format reference

**Step 2 — Create `.claude/agents/import-resolver.md` with this exact content:**

The file must define an agent that does the following when invoked during `/verify`:

**Agent name:** `import-resolver`
**Purpose:** Detect unresolvable imports in the target project — imports that will cause `ImportError` or `ModuleNotFoundError` at runtime.

**What it checks:**
- Every `import X` statement in every `.py` file under `src/`
- Every `from X import Y` statement — both that module X exists AND that name Y is exported by X
- Skips relative imports (`.module`, `..module`) — those are handled by the circular-import-detector
- Skips `TYPE_CHECKING` blocks (imports only used for type hints, not at runtime)
- Skips `try/except ImportError` blocks (conditional imports, safe to ignore)

**How it works (the agent must follow these exact steps):**
1. Read `.build/active-project` to find the target project path. Expand `~` to `$HOME`.
2. Verify `pyproject.toml` exists in the target path.
3. Walk all `.py` files under `src/` using `find $TARGET/src -name "*.py"`.
4. For each file, use Python's `ast` module to extract all import statements:
   ```bash
   uv run python3 -c "
   import ast, sys
   from pathlib import Path
   src = Path('$TARGET/src')
   imports = []
   for f in src.rglob('*.py'):
       try:
           tree = ast.parse(f.read_text())
       except SyntaxError:
           continue
       for node in ast.walk(tree):
           if isinstance(node, ast.Import):
               for alias in node.names:
                   imports.append((str(f), alias.name, None))
           elif isinstance(node, ast.ImportFrom):
               if node.level == 0 and node.module:  # absolute import only
                   names = [a.name for a in node.names if a.name != '*']
                   imports.append((str(f), node.module, names))
   for file, mod, names in imports:
       print(f'{file}|{mod}|{names or \"\"}')
   " 2>/dev/null
   ```
5. For each extracted import, attempt resolution:
   ```bash
   cd $TARGET && uv run python3 -c "import <module>" 2>&1
   ```
   If the exit code is non-zero and the error contains "ModuleNotFoundError" or "ImportError",
   flag it as FAIL with the file path, line context, and error message.
6. For `from X import Y` statements where X resolves successfully, also check that Y exists:
   ```bash
   cd $TARGET && uv run python3 -c "from <module> import <name>" 2>&1
   ```
7. Collect all failures. Deduplicate by (module, name) to avoid reporting the same missing
   import from 10 different files.
8. Report PASS if 0 unresolvable imports. Report FAIL if any unresolvable import found.

**PASS/FAIL criteria:**
- PASS: 0 unresolvable absolute imports
- FAIL: Any `ModuleNotFoundError` or `ImportError` from an absolute import outside `try/except ImportError` blocks and outside `TYPE_CHECKING` blocks

**Report format** (the agent saves its report to):
`.ignorar/production-reports/import-resolver/phase-{N}/{TIMESTAMP}-phase-{N}-import-resolver-{slug}.md`

**Report structure:**
```markdown
# Import Resolver Report

## Summary
- Files scanned: N
- Unique imports checked: N
- Unresolvable imports found: N
- Status: PASS / FAIL

## Findings (if any)
### [ID] CRITICAL Unresolvable Import
- Import: `from X import Y` or `import X`
- Found in: path/to/file.py
- Error: ModuleNotFoundError: No module named 'X'
- Fix: Install X via `uv add X` or correct the import path

## Statistics
- Absolute imports checked: N
- Relative imports skipped: N
- TYPE_CHECKING blocks skipped: N
- try/except ImportError blocks skipped: N
```

**Step 3 — Commit:**
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/import-resolver.md
git commit -m "feat: add import-resolver agent (detects unresolvable imports)"
git log --oneline -1
```

**Step 4 — Write report:**
Create `.ignorar/production-reports/import-resolver-creator/2026-03-05-import-resolver-creator-implementation-report.md` with:
```markdown
# Import Resolver Creator — Implementation Report
**Date:** 2026-03-05
**Task:** Create .claude/agents/import-resolver.md
**File created:** .claude/agents/import-resolver.md
**Commit:** <hash>

## What Was Done
Created the import-resolver agent definition file. The agent uses Python's ast module
to extract all absolute imports from src/, then attempts to resolve each one using
`uv run python3 -c "import X"` in the target project. Unresolvable imports are flagged
as CRITICAL failures. Relative imports, TYPE_CHECKING blocks, and try/except ImportError
blocks are skipped to avoid false positives.

## Result
DONE
```

**Step 5 — Send DONE message to orchestrator:**
```
AGENT: A1 (import-resolver creator)
STATUS: DONE
FILE: .claude/agents/import-resolver.md
COMMIT: <7-char hash>
SUMMARY: Created import-resolver.md agent. Uses ast to extract all absolute imports from src/, resolves each with uv run python3 in the target project, flags ModuleNotFoundError/ImportError as CRITICAL. Skips relative imports, TYPE_CHECKING blocks, and try/except ImportError.
UNBLOCKS: B1, B2, B3
```

---

### Agent A2: per-module coverage script creator

**Your name:** A2 (per-module coverage script creator)
**Your task:** Create ONE new file: `.claude/scripts/check-module-coverage.py`
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`

**Step 1 — Read this file first:**
Read `.claude/scripts/scan-git-history-for-secrets.sh` — use as style reference for scripts.

**Step 2 — Create `.claude/scripts/check-module-coverage.py` with this exact logic:**

The script is a standalone Python script that:
1. Accepts the target project path as the first command-line argument (`sys.argv[1]`)
2. Reads `coverage.xml` from the target project root (generated by `pytest --cov --cov-report=xml`)
3. Parses the XML to extract per-module line-rate coverage
4. Flags any module where line-rate < 0.50 (50% floor)
5. Prints a summary table
6. Exits with code 0 if all modules pass, code 1 if any module fails

**The script must handle these cases:**
- `coverage.xml` not found → print warning "coverage.xml not found at {path}. Run pytest --cov --cov-report=xml first." and exit 1
- Empty coverage.xml → print "No modules found in coverage.xml" and exit 0
- Module with filename `<string>` or `<unknown>` → skip (these are eval'd code, not real modules)

**Script structure:**
```python
#!/usr/bin/env python3
"""
check-module-coverage.py — Per-module coverage floor enforcement.

Usage: python3 check-module-coverage.py <target-project-path>

Reads coverage.xml from the target project and flags any module below 50% line coverage.
Exit code 0 = all modules pass. Exit code 1 = one or more modules below floor.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FLOOR = 0.50  # 50% minimum per module

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check-module-coverage.py <target-project-path>")
        sys.exit(1)

    target = Path(sys.argv[1]).expanduser().resolve()
    coverage_xml = target / "coverage.xml"

    if not coverage_xml.exists():
        print(f"WARNING: coverage.xml not found at {coverage_xml}")
        print("Run: cd {target} && uv run pytest --cov --cov-report=xml")
        sys.exit(1)

    tree = ET.parse(coverage_xml)
    root = tree.getroot()

    failures = []
    modules_checked = 0

    for cls in root.iter("class"):
        filename = cls.get("filename", "")
        # Skip non-real modules
        if not filename or filename.startswith("<"):
            continue
        # Skip __init__.py files (often intentionally empty)
        if filename.endswith("__init__.py"):
            continue

        line_rate = float(cls.get("line-rate", "1.0"))
        modules_checked += 1

        if line_rate < FLOOR:
            failures.append({
                "file": filename,
                "coverage": line_rate,
                "pct": f"{line_rate * 100:.1f}%",
            })

    print(f"\n=== Per-Module Coverage Floor Check (minimum: {FLOOR*100:.0f}%) ===")
    print(f"Modules checked: {modules_checked}")

    if not failures:
        print(f"PASS: All {modules_checked} modules meet the {FLOOR*100:.0f}% floor.")
        sys.exit(0)
    else:
        print(f"\nFAIL: {len(failures)} module(s) below {FLOOR*100:.0f}% coverage floor:\n")
        for f in sorted(failures, key=lambda x: x["coverage"]):
            print(f"  {f['pct']:>7}  {f['file']}")
        print(f"\nFIX: Add tests for the modules listed above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Step 3 — Make it executable and commit:**
```bash
cd /Users/bruno/sec-llm-workbench
chmod +x .claude/scripts/check-module-coverage.py
git add .claude/scripts/check-module-coverage.py
git commit -m "feat: add check-module-coverage.py script (per-module 50% floor)"
git log --oneline -1
```

**Step 4 — Write report:**
Create `.ignorar/production-reports/coverage-script-creator/2026-03-05-coverage-script-creator-implementation-report.md` with:
```markdown
# Coverage Script Creator — Implementation Report
**Date:** 2026-03-05
**Task:** Create .claude/scripts/check-module-coverage.py
**File created:** .claude/scripts/check-module-coverage.py
**Commit:** <hash>

## What Was Done
Created check-module-coverage.py, a standalone Python script that reads coverage.xml
and enforces a 50% minimum line coverage floor per module. Skips __init__.py files
and <string>/<unknown> eval'd modules. Prints a summary table of failing modules.
Exits 0 on PASS, exits 1 on FAIL. Takes target project path as argv[1].

## Result
DONE
```

**Step 5 — Send DONE message to orchestrator:**
```
AGENT: A2 (per-module coverage script creator)
STATUS: DONE
FILE: .claude/scripts/check-module-coverage.py
COMMIT: <7-char hash>
SUMMARY: Created check-module-coverage.py. Reads coverage.xml, enforces 50% floor per module. Skips __init__.py and eval'd modules. Exits 0 on PASS, 1 on FAIL. Takes target path as argv[1].
UNBLOCKS: B1
```

---

## WAVE B AGENT PROMPTS

### Agent B1: SKILL.md editor

**Your name:** B1 (SKILL.md editor)
**Your task:** Edit ONE file: `.claude/skills/verify/SKILL.md`
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`
**Dependency:** Wait until orchestrator sends you a message saying Wave A is complete.

**Step 1 — Read these files (in this order):**
1. Read `.claude/skills/verify/SKILL.md` — the file you will edit
2. Read `.claude/agents/import-resolver.md` — so you know the agent name and report path format
3. Read `.claude/scripts/check-module-coverage.py` — so you know the exact invocation

**Step 2 — Make THREE changes to SKILL.md:**

**Change 1: Wire secrets scan as automatic pre-check (add near the top, before Wave 1)**

Find the section in SKILL.md that describes Step 1 (identifying pending files or starting verification). BEFORE that section, add a new step:

```markdown
## Pre-Check: Secrets in Git History

Run the secrets history scan automatically on every /verify invocation:

```bash
TARGET=$(cat .build/active-project 2>/dev/null || echo "")
TARGET="${TARGET/#\~/$HOME}"
bash .claude/scripts/scan-git-history-for-secrets.sh "$TARGET" 2>/dev/null || true
```

This scan checks git history for accidentally committed secrets (API keys, tokens, passwords).
It runs in non-blocking mode (`|| true`) — a finding is logged as WARNING but does not
halt the verification pipeline. Review the output manually if warnings are reported.
```

**Change 2: Wire per-module coverage floor after the pytest coverage step**

Find the line in SKILL.md that runs `pytest --cov` or checks coverage. After that coverage
check, add:

```markdown
### Per-Module Coverage Floor (50% minimum)

After running pytest with coverage, enforce the per-module floor:

```bash
TARGET=$(cat .build/active-project 2>/dev/null | sed "s|~|$HOME|g")
python3 /Users/bruno/sec-llm-workbench/.claude/scripts/check-module-coverage.py "$TARGET"
```

PASS: All modules meet 50% floor.
FAIL: Any module below 50% — fix by adding tests for that module before proceeding.
```

**Change 3: Add import-resolver to Wave 3 agents**

Find the Wave 3 section in SKILL.md (where integration-tracer, async-safety-auditor,
and semantic-correctness-auditor are listed). Add import-resolver as a 4th Wave 3 agent
running in parallel:

```markdown
Task(
    subagent_type="import-resolver",
    model="sonnet",
    prompt="""Detect all unresolvable imports in the target project.

Target project: `[TARGET_PROJECT]`

Steps:
1. Read .build/active-project to find the target project path
2. Walk all .py files under src/ using ast to extract absolute import statements
3. For each import, run: uv run python3 -c "import <module>" in the target project
4. For from-imports, also check: uv run python3 -c "from <module> import <name>"
5. Skip: relative imports, TYPE_CHECKING blocks, try/except ImportError blocks
6. Flag any ModuleNotFoundError or ImportError as CRITICAL
7. Deduplicate findings by (module, name)

PASS criteria: 0 unresolvable absolute imports.

Save your report to `.ignorar/production-reports/import-resolver/phase-{N}/{TIMESTAMP}-phase-{N}-import-resolver-{slug}.md`
"""
)
```

**Step 3 — Commit:**
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/skills/verify/SKILL.md
git commit -m "feat: wire secrets scan auto + per-module coverage floor + import-resolver in Wave 3"
git log --oneline -1
```

**Step 4 — Write report:**
Create `.ignorar/production-reports/skill-editor/2026-03-05-skill-editor-implementation-report.md` with:
```markdown
# SKILL.md Editor — Implementation Report
**Date:** 2026-03-05
**Task:** Edit .claude/skills/verify/SKILL.md — 3 changes
**File edited:** .claude/skills/verify/SKILL.md
**Commit:** <hash>

## What Was Done
1. Added Pre-Check section: secrets scan runs automatically on every /verify (non-blocking)
2. Added per-module coverage floor check after pytest --cov (blocks on any module <50%)
3. Added import-resolver as 4th Wave 3 agent (parallel with integration-tracer, async-safety-auditor, semantic-correctness-auditor)

## Result
DONE
```

**Step 5 — Send DONE message to orchestrator:**
```
AGENT: B1 (SKILL.md editor)
STATUS: DONE
FILE: .claude/skills/verify/SKILL.md
COMMIT: <7-char hash>
SUMMARY: Added 3 changes to SKILL.md: (1) pre-check secrets scan runs automatically on every /verify invocation in non-blocking mode, (2) per-module coverage floor script runs after pytest --cov blocking on any module <50%, (3) import-resolver added as 4th Wave 3 agent parallel with existing 3.
UNBLOCKS: NONE
```

---

### Agent B2: verification-thresholds.md editor

**Your name:** B2 (thresholds editor)
**Your task:** Edit ONE file: `.claude/docs/verification-thresholds.md`
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`
**Dependency:** Wait until orchestrator sends you a message saying Wave A is complete.

**Step 1 — Read these files:**
1. Read `.claude/docs/verification-thresholds.md` — the file you will edit
2. Read `.claude/agents/import-resolver.md` — to get accurate PASS/FAIL criteria

**Step 2 — Add TWO new sections at the end of verification-thresholds.md:**

Add these two sections after the last existing numbered section:

```markdown
## 14. import-resolver

**Agent:** `import-resolver`
**Wave:** Wave 3 (parallel)
**Checks:** All absolute `import X` and `from X import Y` statements in `src/`

| Result | Criteria |
|--------|----------|
| PASS | 0 unresolvable absolute imports |
| FAIL | Any `ModuleNotFoundError` or `ImportError` from an absolute import outside `try/except ImportError` and outside `TYPE_CHECKING` blocks |
| SKIP | If `src/` directory does not exist in target project |

**Severity:** CRITICAL — an unresolvable import causes `ImportError` at runtime, crashing the application.

**What is skipped:**
- Relative imports (`.module`, `..module`) — covered by circular-import-detector
- `TYPE_CHECKING` blocks — imports never executed at runtime
- `try/except ImportError` blocks — conditional imports, safe to skip

---

## 15. Per-Module Coverage Floor

**Script:** `.claude/scripts/check-module-coverage.py`
**When:** Runs after `pytest --cov --cov-report=xml` in the coverage step
**Input:** `coverage.xml` in the target project root

| Result | Criteria |
|--------|----------|
| PASS | All non-`__init__.py` modules in coverage.xml have line-rate ≥ 50% |
| FAIL | Any module with line-rate < 50% |
| WARNING | `coverage.xml` not found — run `pytest --cov --cov-report=xml` first |

**Floor:** 50% per module (in addition to the existing 75% project-wide gate)

**What is excluded:**
- `__init__.py` files (intentionally sparse, aggregates imports)
- `<string>` and `<unknown>` entries (eval'd code, not real modules)

**Note:** A project can pass the 75% project-wide gate while having individual modules
at 0%. This floor prevents new modules from being silently uncovered.
```

**Step 3 — Commit:**
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/docs/verification-thresholds.md
git commit -m "feat: add thresholds for import-resolver and per-module coverage floor"
git log --oneline -1
```

**Step 4 — Write report:**
Create `.ignorar/production-reports/thresholds-editor/2026-03-05-thresholds-editor-implementation-report.md` with:
```markdown
# Thresholds Editor — Implementation Report
**Date:** 2026-03-05
**Task:** Add sections 14 and 15 to verification-thresholds.md
**File edited:** .claude/docs/verification-thresholds.md
**Commit:** <hash>

## What Was Done
Added section 14 (import-resolver): PASS = 0 unresolvable imports, FAIL = any ImportError.
Added section 15 (per-module coverage floor): PASS = all modules ≥50%, FAIL = any module <50%.
Both sections include exclusion rules to prevent false positives.

## Result
DONE
```

**Step 5 — Send DONE message to orchestrator:**
```
AGENT: B2 (thresholds editor)
STATUS: DONE
FILE: .claude/docs/verification-thresholds.md
COMMIT: <7-char hash>
SUMMARY: Added section 14 (import-resolver thresholds: PASS=0 unresolvable, FAIL=any ImportError, skips TYPE_CHECKING/try-except blocks) and section 15 (per-module coverage floor: PASS=all modules >=50%, FAIL=any module <50%, excludes __init__.py).
UNBLOCKS: NONE
```

---

### Agent B3: 04-agents.md editor

**Your name:** B3 (agents doc editor)
**Your task:** Edit ONE file: `.claude/workflow/04-agents.md`
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`
**Dependency:** Wait until orchestrator sends you a message saying Wave A is complete.

**Step 1 — Read these files:**
1. Read `.claude/workflow/04-agents.md` — the file you will edit (read it fully)
2. Read `.claude/agents/import-resolver.md` — to get accurate documentation

**Step 2 — Add import-resolver documentation to 04-agents.md:**

Find the section in `04-agents.md` that documents the Wave 3 verification agents
(the section containing `async-safety-auditor` and `semantic-correctness-auditor`).

After the last Wave 3 agent documentation block, add a new section:

```markdown
### 9. import-resolver

**Scope:** Runtime import resolution — detects imports that will cause `ImportError` at startup

**Model:** Sonnet

**When to use:**
- After any code-implementer cycle that adds new modules, installs new dependencies, or refactors package structure
- When adding new `from X import Y` statements that reference internal or external modules
- After changing `pyproject.toml` dependencies (a removed dependency may leave broken imports)
- During any Phase verification (runs as Wave 3 agent automatically)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Unresolvable module** | `import X` where X cannot be imported in the target project's venv | CRITICAL |
| **Missing name** | `from X import Y` where X exists but Y is not exported by X | CRITICAL |

**What it skips:**
- Relative imports (`.module`, `..module`) — circular-import-detector handles those
- `TYPE_CHECKING` blocks — not executed at runtime
- `try/except ImportError` blocks — intentionally conditional, safe to ignore
- Star imports (`from X import *`) — cannot be statically resolved

**Verification method:**
1. Walk `src/` with `ast` to extract all absolute import statements
2. For each `import X`: run `uv run python3 -c "import X"` in target project
3. For each `from X import Y`: run `uv run python3 -c "from X import Y"` in target project
4. Capture stdout/stderr, flag `ModuleNotFoundError` / `ImportError` as CRITICAL
5. Deduplicate by (module, name) to avoid redundant reports

**PASS/FAIL criteria:**
- **PASS:** 0 unresolvable absolute imports
- **FAIL:** Any `ModuleNotFoundError` or `ImportError` outside safe blocks

**Example invocation:**
```python
Task(
    subagent_type="import-resolver",
    model="sonnet",
    prompt="""Detect all unresolvable imports in the target project.

Target project: `[TARGET_PROJECT]`

Walk src/ with ast, extract all absolute imports, resolve each with uv run python3.
Skip relative imports, TYPE_CHECKING blocks, and try/except ImportError blocks.
Flag any ModuleNotFoundError or ImportError as CRITICAL.

PASS criteria: 0 unresolvable absolute imports.

Save your report to `.ignorar/production-reports/import-resolver/phase-{N}/{TIMESTAMP}-phase-{N}-import-resolver-{slug}.md`
"""
)
```
```

**Step 3 — Commit:**
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/workflow/04-agents.md
git commit -m "feat: document import-resolver agent in 04-agents.md"
git log --oneline -1
```

**Step 4 — Write report:**
Create `.ignorar/production-reports/agents-doc-editor/2026-03-05-agents-doc-editor-implementation-report.md` with:
```markdown
# Agents Doc Editor — Implementation Report
**Date:** 2026-03-05
**Task:** Document import-resolver agent in 04-agents.md
**File edited:** .claude/workflow/04-agents.md
**Commit:** <hash>

## What Was Done
Added section 9 (import-resolver) to the Wave 3 agents documentation in 04-agents.md.
Documents when to use it, what it checks (unresolvable modules and missing names),
what it skips (relative imports, TYPE_CHECKING, try/except), verification method,
PASS/FAIL criteria, and example invocation.

## Result
DONE
```

**Step 5 — Send DONE message to orchestrator:**
```
AGENT: B3 (agents doc editor)
STATUS: DONE
FILE: .claude/workflow/04-agents.md
COMMIT: <7-char hash>
SUMMARY: Added section 9 (import-resolver) to Wave 3 agents documentation in 04-agents.md. Documents CRITICAL severity for unresolvable modules and missing names, lists what is skipped, provides example invocation and PASS/FAIL criteria.
UNBLOCKS: NONE
```

---

## WAVE C AGENT PROMPT

### Agent C1: Summarizer

**Your name:** C1 (summarizer)
**Your task:** Verify all implementation files exist, read all reports, write final summary,
send to orchestrator.
**MetaProject path:** `/Users/bruno/sec-llm-workbench/`

**Step 1 — Verify all 5 implementation files exist on disk:**
```bash
ls /Users/bruno/sec-llm-workbench/.claude/agents/import-resolver.md
ls /Users/bruno/sec-llm-workbench/.claude/scripts/check-module-coverage.py
ls /Users/bruno/sec-llm-workbench/.claude/skills/verify/SKILL.md
ls /Users/bruno/sec-llm-workbench/.claude/docs/verification-thresholds.md
ls /Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md
```

**Step 2 — Verify git commits landed:**
```bash
cd /Users/bruno/sec-llm-workbench && git log --oneline -10
```
Confirm you see 5 commits from this implementation (feat: add import-resolver, feat: add check-module-coverage.py, feat: wire secrets scan, feat: add thresholds, feat: document import-resolver).

**Step 3 — Read all agent report files:**
- `.ignorar/production-reports/import-resolver-creator/2026-03-05-import-resolver-creator-implementation-report.md`
- `.ignorar/production-reports/coverage-script-creator/2026-03-05-coverage-script-creator-implementation-report.md`
- `.ignorar/production-reports/skill-editor/2026-03-05-skill-editor-implementation-report.md`
- `.ignorar/production-reports/thresholds-editor/2026-03-05-thresholds-editor-implementation-report.md`
- `.ignorar/production-reports/agents-doc-editor/2026-03-05-agents-doc-editor-implementation-report.md`

**Step 4 — Write final summary:**
Create `.ignorar/production-reports/final-summary/2026-03-05-final-three-gaps-summary.md`

Include:
- List of all 5 files created/edited with commit hashes
- PASS/FAIL status of each agent
- What /verify can now do that it couldn't before
- git log --oneline -10 output

**Step 5 — Commit the summary:**
```bash
cd /Users/bruno/sec-llm-workbench
git add .ignorar/production-reports/final-summary/2026-03-05-final-three-gaps-summary.md
git commit -m "docs: add final summary report for 3-gap closure implementation"
git log --oneline -1
```

Wait — `.ignorar/` is gitignored. Do NOT commit. Just write the file. Skip this commit step.

**Step 6 — Send DONE message to orchestrator:**

```
AGENT: C1 (summarizer)
STATUS: DONE
FILE: .ignorar/production-reports/final-summary/2026-03-05-final-three-gaps-summary.md

IMPLEMENTATION COMPLETE — /verify 3 FINAL GAP CLOSURE

All 3 remaining gaps in /verify have been implemented across 5 agents in 3 waves.

Files created (2 new):
- .claude/agents/import-resolver.md (Gap 3: import resolution check)
- .claude/scripts/check-module-coverage.py (Gap 2: per-module 50% coverage floor)

Files modified (3):
- .claude/skills/verify/SKILL.md (Gap 1: secrets scan auto + Gap 2 floor + Gap 3 agent in Wave 3)
- .claude/docs/verification-thresholds.md (sections 14, 15 added)
- .claude/workflow/04-agents.md (import-resolver documented as section 9)

Git commits (5 total):
<list each commit hash and message>

/verify now runs 14 agents automatically (was 13).
Secrets git history scan runs automatically on every /verify (non-blocking).
Per-module 50% coverage floor enforced after pytest --cov.
Import resolver checks all absolute imports resolve in the target project venv.
```

---

## FILE PATHS REFERENCE TABLE

| Wave | Agent | File | Action |
|------|-------|------|--------|
| A | A1 | `.claude/agents/import-resolver.md` | CREATE |
| A | A2 | `.claude/scripts/check-module-coverage.py` | CREATE |
| B | B1 | `.claude/skills/verify/SKILL.md` | EDIT (3 changes) |
| B | B2 | `.claude/docs/verification-thresholds.md` | EDIT (add sections 14, 15) |
| B | B3 | `.claude/workflow/04-agents.md` | EDIT (add section 9) |
| C | C1 | `.ignorar/production-reports/final-summary/2026-03-05-final-three-gaps-summary.md` | CREATE (not committed) |

---

## DEPENDENCY RULES

- Wave B cannot start until BOTH Wave A agents report DONE
- Wave C cannot start until ALL THREE Wave B agents report DONE
- If any Wave A agent reports FAILED → stop, escalate to main context
- If any Wave B agent reports FAILED → stop, escalate to main context
- If C1 reports FAILED → escalate to main context

---

## CONTEXT SAFETY NOTES

| Agent | Task | Estimated tokens |
|-------|------|-----------------|
| A1 | Read 2 ref files (~150 lines each) + write 1 new file (~120 lines) | ~15k tokens |
| A2 | Read 1 ref file (~50 lines) + write 1 new file (~80 lines) | ~10k tokens |
| B1 | Read SKILL.md (~300 lines) + import-resolver.md + script + edit | ~30k tokens |
| B2 | Read verification-thresholds.md (~200 lines) + import-resolver.md + edit | ~20k tokens |
| B3 | Read 04-agents.md (~400 lines) + import-resolver.md + edit | ~30k tokens |
| C1 | Read 5 report files (~50 lines each) + ls + git log + write summary | ~20k tokens |
| Orchestrator | Receive 5 DONE messages + relay C1 | ~15k tokens |

All agents well within 200k context limit.
