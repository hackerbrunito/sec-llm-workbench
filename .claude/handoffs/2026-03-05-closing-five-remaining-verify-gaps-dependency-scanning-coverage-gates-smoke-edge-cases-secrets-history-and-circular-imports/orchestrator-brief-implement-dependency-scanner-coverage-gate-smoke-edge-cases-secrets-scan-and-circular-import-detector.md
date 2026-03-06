# Orchestrator Briefing: Close 5 Remaining /verify Gaps
# Date: 2026-03-05
# Author: Claude Code (main context)
# Purpose: Complete self-contained instructions for orchestrator + all 8 worker agents.
#          The orchestrator reads this file and executes the plan exactly as written.
#          No improvisation. No interpretation. Follow every step literally.

---

## CONTEXT

You are the **orchestrator** for implementing 5 remaining improvements to the `/verify`
command in the MetaProject at `/Users/bruno/sec-llm-workbench/`.

This is the MetaProject — a Python project generator framework used to verify SIOPV
and future Python projects. You are NOT working on SIOPV (`~/siopv/`).
All file operations refer to MetaProject files unless explicitly stated.

**MetaProject path:** `/Users/bruno/sec-llm-workbench/`

**Background:** The `/verify` command now runs 11 agents. After a review session, 5 gaps
were identified that the 11 agents cannot detect. This briefing implements all 5 gaps.

### The 5 gaps being closed:

| # | Gap | What is missing |
|---|-----|----------------|
| 1 | Dependency CVE scanning | No agent runs `uv pip audit` to detect known CVEs in pyproject.toml dependencies |
| 2 | Coverage threshold enforcement | No agent enforces a minimum test coverage %; coverage can silently drop to 0% |
| 3 | Smoke test edge cases | smoke-test-runner only tests one input (CVE-2024-1234); 3 edge cases are missing |
| 4 | Secrets in git history | No scan of git history for accidentally committed secrets (only current file state) |
| 5 | Circular import detection | No agent detects Python circular imports that cause ImportError at runtime |

---

## YOUR ROLE AS ORCHESTRATOR

You coordinate agents. You do NOT read project files, write project files, or implement
anything yourself. Your only tools for coordination are: Agent (to spawn), SendMessage
(to communicate), and Read (only for this briefing file).

### Your exact execution steps:

1. Read this briefing file completely before doing anything else
2. Spawn all 4 Wave A agents **simultaneously** (single response with 4 Agent tool calls)
3. Wait for ALL 4 Wave A agents to send you a DONE message via SendMessage
4. When each Wave A agent reports DONE, check the UNBLOCKS field in its message.
   If it says NONE, no action needed. If it names an agent, that agent is in Wave B
   and will be spawned in step 5.
5. Once ALL 4 Wave A agents are DONE: spawn all 3 Wave B agents **simultaneously**
6. Wait for ALL 3 Wave B agents to send you a DONE message via SendMessage
7. Once ALL 3 Wave B agents are DONE: spawn Wave C agent (C1 summarizer)
8. Wait for C1 to send you its DONE message
9. Relay C1's complete message verbatim to the main context (team lead) via SendMessage

### If any agent reports FAILED:
- Stop immediately. Do NOT proceed to the next wave.
- Send the main context (team lead) a message:
  `BLOCKED: Agent <name> reported FAILED. Reason: <copy SUMMARY from agent's message>. Awaiting instructions.`
- Wait for instructions from main context before continuing.

---

## TEAM STRUCTURE

```
Orchestrator (you)
├── Wave A — spawn all 4 simultaneously (no file conflicts)
│   ├── A1: Create .claude/agents/dependency-scanner.md          [new file]
│   ├── A2: Edit .claude/agents/smoke-test-runner.md             [add 3 edge cases]
│   ├── A3: Create .claude/agents/circular-import-detector.md    [new file]
│   └── A4: Create .claude/scripts/scan-git-history-for-secrets.sh [new file]
│
├── [GATE: Wait for ALL 4 Wave A agents to report DONE]
│
├── Wave B — spawn all 3 simultaneously (no file conflicts, different files)
│   ├── B1: Edit .claude/skills/verify/SKILL.md                  [coverage gate + 2 new agents]
│   ├── B2: Edit .claude/docs/verification-thresholds.md         [2 new agent entries]
│   └── B3: Edit .claude/workflow/04-agents.md                   [2 new agent sections]
│
├── [GATE: Wait for ALL 3 Wave B agents to report DONE]
│
└── Wave C — spawn after Wave B completes
    └── C1: Summarizer — verify files, read reports, write summary, relay to orchestrator
```

**Why Wave A before Wave B?**
Wave B agents (B1, B2, B3) must reference the dependency-scanner and circular-import-detector
agents by name, PASS criteria, and report paths. These details come from the Wave A agent files.
B1 reads `dependency-scanner.md` and `circular-import-detector.md` before wiring them into
SKILL.md. B2 and B3 do the same for thresholds and documentation. Therefore Wave A must
complete and commit before Wave B begins.

**Why Wave B agents can run in parallel?**
B1 edits `SKILL.md`, B2 edits `verification-thresholds.md`, B3 edits `04-agents.md`.
These are three completely different files. No merge conflicts are possible.

---

## COMMUNICATION PROTOCOL

### What each agent sends you when done

Every agent sends you EXACTLY ONE message when it finishes, in this exact format:

```
AGENT: <agent-id> (<agent-role>)
STATUS: DONE | FAILED
FILE: <exact relative path from MetaProject root>
COMMIT: <7-char git commit hash from git log --oneline -1>
SUMMARY: <2-4 sentences: what was done, what was added, any warnings or notes>
UNBLOCKS: NONE | <name of Wave B agent waiting on this Wave A agent>
```

Example of a valid DONE message:
```
AGENT: A1 (dependency-scanner creator)
STATUS: DONE
FILE: .claude/agents/dependency-scanner.md
COMMIT: a3f91bc
SUMMARY: Created dependency-scanner.md agent. Agent runs uv pip audit and falls back to
pip-audit if unavailable. Checks all packages in pyproject.toml against known CVE databases.
PASS criteria: 0 CRITICAL or HIGH severity CVEs in dependencies.
UNBLOCKS: NONE
```

### What you send to waiting agents (Wave B only)

When a Wave A agent you were waiting on reports DONE, immediately send the corresponding
Wave B agent (once all 4 Wave A are done, spawn all Wave B simultaneously — do NOT spawn
Wave B agents individually as each Wave A completes, wait for ALL 4 first).

### What you send to the main context at the end

When C1 sends you its final message, relay it verbatim to the main context using:
```
SendMessage(type="message", recipient="team-lead", content=<C1's exact message>, summary="All 5 verify gaps implemented")
```

---

## GIT INSTRUCTIONS FOR ALL AGENTS

All agents commit in the **MetaProject** directory: `/Users/bruno/sec-llm-workbench/`

Every agent follows this commit sequence immediately after completing its task:

```bash
cd /Users/bruno/sec-llm-workbench
git add <exact-file-path>
git commit -m "<commit message as specified in agent prompt>"
```

Rules:
- Commit IMMEDIATELY after task completion — do not wait for other agents
- Stage ONLY the one file the agent was responsible for
- Do NOT use `git add .` or `git add -A` — always name the specific file
- If the pre-commit hook blocks the commit, include it as a WARNING in SUMMARY
  and do NOT retry — report it and let the orchestrator handle it
- After committing, run `git log --oneline -1` and include the hash in the DONE message

---

## WAVE A AGENT PROMPTS

### A1 — Create dependency-scanner.md

**Spawn with:** `subagent_type="general-purpose"`, `name="A1-dependency-scanner"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly (copy verbatim, no changes):**

---
You are agent A1. Your single task is to create one new agent definition file.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Create `.claude/agents/dependency-scanner.md`

ESTIMATED CONTEXT USAGE: ~12k tokens. You have plenty of room.

STEP 1 — Read these two files for context and format reference:
- `.claude/agents/async-safety-auditor.md` (study the YAML frontmatter format and section structure)
- `.claude/agents/smoke-test-runner.md` (study the Actions section format)

Do NOT read any other files. These two are sufficient context.

STEP 2 — Create the file `.claude/agents/dependency-scanner.md` with exactly this content:

```
<!-- version: 2026-03 -->
---
name: dependency-scanner
description: Scan all project dependencies in pyproject.toml for known CVEs using uv pip audit (primary) or pip-audit (fallback). Reports CRITICAL and HIGH severity vulnerabilities. Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: default
cache_control: ephemeral
budget_tokens: 10000
---

## Project Context (CRITICAL)

- You are invoked from the meta-project (sec-llm-workbench/). You are NOT working on the meta-project itself.
- Target project path is provided in your invocation prompt. If not provided, read `.build/active-project`.
- Expand `~` to `$HOME` in all paths before use.
- All `uv run` and `cd` commands must use the fully expanded target project path.
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project directory).

## Role Definition

You are the Dependency Scanner. Your job is to detect known CVEs in the target project's
Python dependencies before they reach production. Static code analysis cannot catch
vulnerable package versions — only a dependency audit can. You run `uv pip audit` against
the installed packages in the target project's virtual environment and report any
CRITICAL or HIGH severity findings.

## Actions (execute in order, do not skip any step)

1. Read `.build/active-project` to get TARGET. Run: `TARGET=$(cat .build/active-project); TARGET="${TARGET/#\~/$HOME}"`

2. Verify pyproject.toml exists: `ls "$TARGET/pyproject.toml"` — if missing, report FAIL "no pyproject.toml found".

3. Attempt primary audit method:
   ```bash
   cd "$TARGET" && uv pip audit 2>&1
   ```
   Capture full output including any error messages.

4. If `uv pip audit` fails with "command not found" or "unknown command", attempt fallback:
   ```bash
   cd "$TARGET" && uv run pip-audit --format=json 2>&1
   ```
   If fallback also fails, report FAIL "neither uv pip audit nor pip-audit available — install pip-audit with: uv add --dev pip-audit".

5. Parse the audit output:
   - Count total packages scanned
   - Extract all vulnerabilities found: package name, installed version, CVE ID, severity, description
   - Categorize by severity: CRITICAL, HIGH, MEDIUM, LOW

6. Apply PASS/FAIL logic:
   - PASS: 0 CRITICAL findings AND 0 HIGH findings
   - FAIL: any CRITICAL or HIGH finding
   - WARNING (non-blocking): MEDIUM or LOW findings are logged but do not cause FAIL

7. Save report to:
   `.ignorar/production-reports/dependency-scanner/phase-{N}/{TIMESTAMP}-phase-{N}-dependency-scanner-audit.md`
   where {N} = content of `.build/current-phase`, {TIMESTAMP} = `date +%Y-%m-%d-%H%M%S`
   Create the directory if it does not exist.

## PASS/FAIL Criteria

- PASS: 0 CRITICAL CVEs, 0 HIGH CVEs in any dependency
- FAIL: Any CRITICAL or HIGH severity CVE found in any dependency
- WARNING (non-blocking): MEDIUM or LOW CVEs — logged in report, do not block

## Findings Severity

| Finding | Severity |
|---------|----------|
| CVE with CVSS >= 9.0 in any dependency | CRITICAL |
| CVE with CVSS 7.0-8.9 in any dependency | HIGH |
| CVE with CVSS 4.0-6.9 in any dependency | MEDIUM |
| CVE with CVSS < 4.0 in any dependency | LOW |
| Audit tool unavailable | CRITICAL (cannot verify) |
| pyproject.toml missing | CRITICAL |

## Report Format

```markdown
# Dependency Scanner Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [project path]
**Audit method:** uv pip audit | pip-audit (fallback)

## Summary
- Total packages scanned: N
- CRITICAL CVEs: N
- HIGH CVEs: N
- MEDIUM CVEs: N
- LOW CVEs: N
- Status: PASS / FAIL

## Findings

### [CVE-XXXX-XXXXX] [Severity] — [package-name] [version]
- **Description:** [CVE description]
- **CVSS Score:** N.N
- **Fix:** Upgrade to [package-name] >= [fixed-version]

## Result
DEPENDENCY SCAN PASSED / FAILED
```
```

STEP 3 — Commit the file:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/dependency-scanner.md
git commit -m "feat: add dependency-scanner agent — CVE audit for project dependencies (Gap 1)"
```

STEP 4 — Write a brief implementation report:
Create `.ignorar/production-reports/dependency-scanner/2026-03-05-dependency-scanner-implementation-report.md`
with content:
```
# Dependency Scanner — Implementation Report
**Date:** 2026-03-05
**Task:** Create .claude/agents/dependency-scanner.md
**File created:** .claude/agents/dependency-scanner.md
**Commit:** [paste hash from git log --oneline -1]

## What Was Done
Created dependency-scanner.md agent definition. Agent uses uv pip audit as primary
method with pip-audit as fallback. Checks pyproject.toml dependencies for CRITICAL
and HIGH CVEs. PASS criteria: 0 CRITICAL + 0 HIGH findings.

## Result
DONE
```

STEP 5 — Send a message to the orchestrator (recipient: "orchestrator"):
```
AGENT: A1 (dependency-scanner creator)
STATUS: DONE
FILE: .claude/agents/dependency-scanner.md
COMMIT: [7-char hash from git log --oneline -1]
SUMMARY: Created dependency-scanner.md. Agent runs uv pip audit (fallback: pip-audit) against installed packages. Checks for CRITICAL/HIGH CVEs. PASS = 0 CRITICAL + 0 HIGH. Report path: .ignorar/production-reports/dependency-scanner/. File committed.
UNBLOCKS: NONE
```

If STEP 3 failed (commit blocked), set STATUS: FAILED and explain in SUMMARY.
---

### A2 — Extend smoke-test-runner.md with 3 edge cases

**Spawn with:** `subagent_type="general-purpose"`, `name="A2-smoke-edge-cases"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent A2. Your single task is to extend one existing agent definition file with 3 edge case test inputs.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Edit `.claude/agents/smoke-test-runner.md` to add 3 edge case inputs after the existing happy-path test.

ESTIMATED CONTEXT USAGE: ~15k tokens. You have plenty of room.

STEP 1 — Read this file completely:
- `.claude/agents/smoke-test-runner.md` (read the FULL file — you will edit it)

Do NOT read any other files.

STEP 2 — Locate the "## Actions" section. Find step 6 which runs the pipeline with CVE-2024-1234.
After step 9 (the final "Save report" step), add the following new section:

Find the exact text of step 9 in the file (it ends with the report save instruction).
Immediately after that step, insert this new section:

```markdown
## Edge Case Tests (run after happy-path test in step 6)

After the main happy-path test (CVE-2024-1234), run these 3 additional edge case inputs
to verify robustness. Each is independent — a failure in one does not stop the others.

### Edge Case 1: Malformed CVE ID
```bash
cd "$TARGET" && timeout 60 uv run [cli-command] [cve-flag] "NOT-A-CVE-ID" 2>&1
```
Expected behavior: pipeline handles gracefully (validation error or empty result — NOT an unhandled exception).
FAIL condition: any unhandled exception / traceback.

### Edge Case 2: Non-existent but valid CVE format
```bash
cd "$TARGET" && timeout 60 uv run [cli-command] [cve-flag] "CVE-9999-99999" 2>&1
```
Expected behavior: pipeline returns result with empty/unknown enrichment (no crash).
FAIL condition: any unhandled exception / traceback.

### Edge Case 3: Empty string input
```bash
cd "$TARGET" && timeout 60 uv run [cli-command] [cve-flag] "" 2>&1
```
Expected behavior: pipeline returns validation error or empty result — NOT an unhandled exception.
FAIL condition: any unhandled exception / traceback.

### Edge Case Result Aggregation
- Count how many of the 3 edge cases produced unhandled exceptions
- If 0: edge cases PASS (report as EDGE CASES PASS)
- If 1-3: edge cases FAIL (report each failure with the exception message)
- Edge case results are logged in the report but do NOT override the main PASS/FAIL verdict
- A project that passes the happy path but fails all 3 edge cases is still PASS (main) with WARNING (edge cases)
```

Also update the version comment at the top of the file:
Change `<!-- version: 2026-03 -->` (if it exists) to keep it as `<!-- version: 2026-03 -->`
or if the current version is `<!-- version: 2026-02 -->`, change it to `<!-- version: 2026-03 -->`.

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/smoke-test-runner.md
git commit -m "feat: add 3 edge case inputs to smoke-test-runner (Gap 3 — malformed CVE, non-existent CVE, empty input)"
```

STEP 4 — Write implementation report:
Create `.ignorar/production-reports/smoke-edge-cases/2026-03-05-smoke-edge-cases-implementation-report.md`:
```
# Smoke Test Edge Cases — Implementation Report
**Date:** 2026-03-05
**Task:** Extend smoke-test-runner.md with 3 edge case inputs
**File edited:** .claude/agents/smoke-test-runner.md
**Commit:** [paste hash]

## What Was Done
Added Edge Case Tests section after step 9 of the Actions section.
Edge cases: malformed CVE ID, non-existent CVE (CVE-9999-99999), empty string.
Edge case failures are warnings (do not override main PASS/FAIL verdict).

## Result
DONE
```

STEP 5 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: A2 (smoke-edge-cases extender)
STATUS: DONE
FILE: .claude/agents/smoke-test-runner.md
COMMIT: [7-char hash]
SUMMARY: Added "Edge Case Tests" section to smoke-test-runner.md with 3 inputs: malformed CVE ID, non-existent CVE-9999-99999, empty string. Edge failures are warnings and do not override main verdict. File committed.
UNBLOCKS: NONE
```
---

### A3 — Create circular-import-detector.md

**Spawn with:** `subagent_type="general-purpose"`, `name="A3-circular-import-detector"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent A3. Your single task is to create one new agent definition file.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Create `.claude/agents/circular-import-detector.md`

ESTIMATED CONTEXT USAGE: ~12k tokens. You have plenty of room.

STEP 1 — Read these two files for context and format reference:
- `.claude/agents/async-safety-auditor.md` (YAML frontmatter and section structure reference)
- `.claude/agents/integration-tracer.md` (AST-based analysis reference — study how AST is used)

Do NOT read any other files.

STEP 2 — Create `.claude/agents/circular-import-detector.md` with exactly this content:

```
<!-- version: 2026-03 -->
---
name: circular-import-detector
description: Detect Python circular imports in the target project using AST-based import graph analysis. Circular imports cause ImportError at runtime. Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: plan
disallowedTools: [Write, Edit]
cache_control: ephemeral
budget_tokens: 12000
---

## Project Context (CRITICAL)

- You are invoked from the meta-project (sec-llm-workbench/). You are NOT working on the meta-project.
- Target project path is provided in your invocation prompt or read from `.build/active-project`.
- Expand `~` to `$HOME` before use.
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project).

## Role Definition

You are the Circular Import Detector. Python circular imports (module A imports module B,
which imports module A) cause `ImportError: cannot import name X` or `AttributeError`
at runtime. These pass all linters and type checkers — they only fail when the module
is first loaded. Your job is to detect these cycles before they reach production.

## Actions (execute in order)

1. Read `.build/active-project` to get TARGET. Expand `~` to `$HOME`.

2. Find all Python source files:
   ```bash
   find "$TARGET/src" -name "*.py" -not -path "*/\.*" | sort
   ```

3. Build an import graph using Python's ast module. Run this inline Python script:
   ```bash
   cd "$TARGET" && python3 - <<'PYEOF'
   import ast, sys, os
   from pathlib import Path
   from collections import defaultdict, deque

   src = Path(os.environ.get("TARGET", ".")) / "src"
   # Map: module_dotpath -> set of imported module_dotpaths
   imports = defaultdict(set)
   file_to_module = {}

   def path_to_module(p):
       rel = p.relative_to(src)
       parts = list(rel.with_suffix("").parts)
       if parts[-1] == "__init__":
           parts = parts[:-1]
       return ".".join(parts)

   for py_file in src.rglob("*.py"):
       mod = path_to_module(py_file)
       file_to_module[str(py_file)] = mod
       try:
           tree = ast.parse(py_file.read_text(errors="ignore"))
       except SyntaxError:
           continue
       for node in ast.walk(tree):
           if isinstance(node, ast.Import):
               for alias in node.names:
                   imports[mod].add(alias.name)
           elif isinstance(node, ast.ImportFrom):
               if node.module:
                   base = node.module if node.level == 0 else ""
                   if base:
                       imports[mod].add(base)

   # Detect cycles using DFS
   def find_cycles():
       visited = set()
       path = []
       path_set = set()
       cycles = []

       def dfs(node):
           visited.add(node)
           path.append(node)
           path_set.add(node)
           for neighbor in imports.get(node, set()):
               # Only check internal modules (same package)
               if not any(neighbor.startswith(m) for m in imports):
                   continue
               if neighbor in path_set:
                   idx = path.index(neighbor)
                   cycles.append(list(path[idx:]) + [neighbor])
               elif neighbor not in visited:
                   dfs(neighbor)
           path.pop()
           path_set.discard(node)

       for mod in list(imports.keys()):
           if mod not in visited:
               dfs(mod)
       return cycles

   cycles = find_cycles()
   if cycles:
       print(f"CYCLES_FOUND: {len(cycles)}")
       for c in cycles:
           print(" -> ".join(c))
   else:
       print("NO_CYCLES_FOUND")
   PYEOF
   ```
   Capture all output.

4. Parse the output:
   - If output starts with "NO_CYCLES_FOUND": PASS
   - If output starts with "CYCLES_FOUND": FAIL — extract each cycle chain

5. For each cycle found, identify the files involved:
   ```bash
   grep -rn "^from\|^import" "$TARGET/src" --include="*.py" | grep "[cycle-module-name]"
   ```
   This helps pinpoint the exact import lines causing each cycle.

6. Save report to:
   `.ignorar/production-reports/circular-import-detector/phase-{N}/{TIMESTAMP}-phase-{N}-circular-import-detector-scan.md`
   Create directory if needed.

## PASS/FAIL Criteria

- PASS: 0 circular import cycles detected in `src/`
- FAIL: Any circular import cycle detected (even one causes potential runtime crashes)

## Findings Severity

| Finding | Severity |
|---------|----------|
| Circular import cycle involving core modules (state, di, graph) | CRITICAL |
| Circular import cycle in any module | HIGH |

## Report Format

```markdown
# Circular Import Detector Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [project path]
**Files scanned:** N .py files

## Summary
- Total modules analyzed: N
- Circular import cycles found: N
- Status: PASS / FAIL

## Cycles Found (if any)
### Cycle 1
Chain: module.a -> module.b -> module.c -> module.a
Files involved:
- src/[path]/a.py line N: from module.b import X
- src/[path]/b.py line N: from module.c import Y
- src/[path]/c.py line N: from module.a import Z
Fix: Break cycle by extracting shared dependency to a new module, or use lazy imports.

## Result
CIRCULAR IMPORT SCAN PASSED / FAILED
```
```

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/circular-import-detector.md
git commit -m "feat: add circular-import-detector agent — AST-based cycle detection (Gap 5)"
```

STEP 4 — Write implementation report:
Create `.ignorar/production-reports/circular-import-detector/2026-03-05-circular-import-detector-implementation-report.md`:
```
# Circular Import Detector — Implementation Report
**Date:** 2026-03-05
**Task:** Create .claude/agents/circular-import-detector.md
**File created:** .claude/agents/circular-import-detector.md
**Commit:** [paste hash]

## What Was Done
Created circular-import-detector.md agent. Uses inline Python ast module script to build
full import graph across all .py files in src/. DFS cycle detection finds all circular
chains. PASS criteria: 0 cycles. FAIL: any cycle detected.

## Result
DONE
```

STEP 5 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: A3 (circular-import-detector creator)
STATUS: DONE
FILE: .claude/agents/circular-import-detector.md
COMMIT: [7-char hash]
SUMMARY: Created circular-import-detector.md. Uses inline Python ast script to build import graph and detect cycles via DFS. Covers all .py files in src/. PASS = 0 cycles. Reports to .ignorar/production-reports/circular-import-detector/. File committed.
UNBLOCKS: NONE
```
---

### A4 — Create scan-git-history-for-secrets.sh

**Spawn with:** `subagent_type="general-purpose"`, `name="A4-secrets-history-scanner"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent A4. Your single task is to create one new script file.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Create `.claude/scripts/scan-git-history-for-secrets.sh`

ESTIMATED CONTEXT USAGE: ~8k tokens. You have plenty of room.

STEP 1 — Read this file for context:
- `.claude/scripts/check-reviewer-score.sh` (study its bash style and structure)

Do NOT read any other files.

STEP 2 — Create `.claude/scripts/scan-git-history-for-secrets.sh` with exactly this content:

```bash
#!/usr/bin/env bash
# scan-git-history-for-secrets.sh
# One-time scan of git history for accidentally committed secrets.
# Scans ALL commits in git log for common secret patterns.
# Usage: bash .claude/scripts/scan-git-history-for-secrets.sh [project-path]
# If project-path is omitted, uses .build/active-project

set -euo pipefail

# Resolve target project path
TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    TARGET=$(cat .build/active-project 2>/dev/null || echo "")
    TARGET="${TARGET/#\~/$HOME}"
fi

if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
    echo "ERROR: Target project path not found. Pass it as argument or set .build/active-project"
    exit 1
fi

if [ ! -d "$TARGET/.git" ]; then
    echo "ERROR: $TARGET is not a git repository"
    exit 1
fi

echo "Scanning git history for secrets in: $TARGET"
echo "This may take a moment for large repos..."
echo ""

FINDINGS=0
REPORT_FILE="/tmp/secrets-history-scan-$(date +%Y%m%d-%H%M%S).txt"

# Secret patterns to search for in git history
# Format: description|regex_pattern
PATTERNS=(
    "AWS Access Key|AKIA[0-9A-Z]{16}"
    "AWS Secret Key|[aA]ws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]"
    "Generic API Key|api[_-]?key['\"\s]*[:=]['\"\s]*[0-9a-zA-Z\-_]{20,}"
    "Generic Secret|secret['\"\s]*[:=]['\"\s]*[0-9a-zA-Z\-_]{20,}"
    "Generic Password|password['\"\s]*[:=]['\"\s]*[^\s]{8,}"
    "Private Key Header|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    "GitHub Token|gh[pousr]_[0-9a-zA-Z]{36,}"
    "Anthropic API Key|sk-ant-[a-zA-Z0-9\-_]{40,}"
    "OpenAI API Key|sk-[a-zA-Z0-9]{48}"
    "Slack Token|xox[baprs]-[0-9a-zA-Z\-]+"
    "Hardcoded Bearer Token|[Bb]earer [0-9a-zA-Z\-_.]{20,}"
    "Database URL with credentials|[a-z]+://[^:]+:[^@]+@[a-z0-9\-.]+"
    "Hex encoded secret (32+ chars)|[0-9a-f]{32,}"
)

{
echo "Git History Secrets Scan Report"
echo "================================"
echo "Target: $TARGET"
echo "Date: $(date)"
echo ""
} >> "$REPORT_FILE"

cd "$TARGET"

for pattern_entry in "${PATTERNS[@]}"; do
    description="${pattern_entry%%|*}"
    pattern="${pattern_entry##*|}"

    matches=$(git log -p --all --full-history -- . 2>/dev/null | grep -E "$pattern" | grep -v "^Binary" | head -20 || true)

    if [ -n "$matches" ]; then
        FINDINGS=$((FINDINGS + 1))
        echo "  [FOUND] $description"
        {
        echo "## $description"
        echo "Pattern: $pattern"
        echo "Matches (first 20):"
        echo "$matches" | head -20
        echo ""
        } >> "$REPORT_FILE"
    fi
done

echo ""
echo "================================"
if [ "$FINDINGS" -gt 0 ]; then
    echo "RESULT: $FINDINGS secret pattern(s) found in git history."
    echo "Review $REPORT_FILE for details."
    echo ""
    echo "To remove secrets from git history, use:"
    echo "  git filter-repo --path <file> --invert-paths"
    echo "  OR: BFG Repo Cleaner (https://rtyley.github.io/bfg-repo-cleaner/)"
    echo ""
    echo "IMPORTANT: After removing from history, rotate all exposed credentials immediately."
    exit 1
else
    echo "RESULT: No secret patterns found in git history. CLEAN."
    exit 0
fi
```

STEP 3 — Make the script executable and commit:
```bash
cd /Users/bruno/sec-llm-workbench
chmod +x .claude/scripts/scan-git-history-for-secrets.sh
git add .claude/scripts/scan-git-history-for-secrets.sh
git commit -m "feat: add scan-git-history-for-secrets.sh script — one-time git history audit (Gap 4)"
```

STEP 4 — Write implementation report:
Create `.ignorar/production-reports/secrets-history-scanner/2026-03-05-secrets-history-scanner-implementation-report.md`:
```
# Secrets History Scanner — Implementation Report
**Date:** 2026-03-05
**Task:** Create .claude/scripts/scan-git-history-for-secrets.sh
**File created:** .claude/scripts/scan-git-history-for-secrets.sh
**Commit:** [paste hash]

## What Was Done
Created bash script that scans full git history (all commits, all branches) for 14
common secret patterns including AWS keys, API tokens, private keys, database URLs,
and hardcoded passwords. Reports to /tmp/ with full match context. Script exits 1
if findings found (CI-friendly), 0 if clean.

## Result
DONE
```

STEP 5 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: A4 (secrets-history-scanner creator)
STATUS: DONE
FILE: .claude/scripts/scan-git-history-for-secrets.sh
COMMIT: [7-char hash]
SUMMARY: Created scan-git-history-for-secrets.sh. Scans full git log -p for 14 secret patterns (AWS, GitHub, Anthropic, OpenAI, private keys, DB URLs, etc). Reports to /tmp/. Exit 1 if secrets found, 0 if clean. Includes remediation guidance (git filter-repo, BFG). File committed and made executable.
UNBLOCKS: NONE
```
---

## WAVE B AGENT PROMPTS

**IMPORTANT:** Do NOT spawn any Wave B agent until ALL 4 Wave A agents have reported DONE.
Wave B agents read the files created by Wave A. If Wave A is not complete, Wave B reads
incomplete or missing files.

Once all 4 Wave A agents report DONE, spawn B1, B2, and B3 **simultaneously** in a single response.

### B1 — Edit SKILL.md

**Spawn with:** `subagent_type="general-purpose"`, `name="B1-skill-editor"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent B1. Your single task is to edit one existing file with two related changes.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Edit `.claude/skills/verify/SKILL.md` with exactly 2 changes:
  Change 1: Add a coverage threshold gate to Step 5 (Verificaciones Adicionales)
  Change 2: Add dependency-scanner and circular-import-detector Task blocks to Wave 3

ESTIMATED CONTEXT USAGE: ~25k tokens (reading large SKILL.md + making 2 edits). You have room.

STEP 1 — Read these files completely (do not skip any):
- `.claude/skills/verify/SKILL.md` (full content — you will edit this file)
- `.claude/agents/dependency-scanner.md` (to get PASS criteria and report path format)
- `.claude/agents/circular-import-detector.md` (to get PASS criteria and report path format)

STEP 2 — CHANGE 1: Add coverage threshold gate to Step 5

Find the section "### 5. Verificaciones Adicionales" in SKILL.md.
Find the line: `uv run pytest tests/ -v`

Replace that line with:
```
uv run pytest tests/ -v --cov src --cov-report=term-missing --cov-fail-under=75
```

This adds coverage measurement and enforces a 75% minimum threshold. If coverage drops
below 75%, the Step 5 verification block will fail with a non-zero exit code.

STEP 3 — CHANGE 2: Add 2 new Task blocks to Wave 3

Find the Wave 3 section in SKILL.md. Locate the `regression-guard` Task block (the last
Task block in Wave 3). Immediately after the closing triple-backtick of the regression-guard
block, insert these two new Task blocks:

```
**dependency-scanner:**
```
Task(subagent_type="dependency-scanner", prompt="""Scan all project dependencies for known CVEs.
Check pyproject.toml packages against vulnerability databases using uv pip audit.

Target project: [TARGET_PROJECT]

PASS criteria: 0 CRITICAL CVEs, 0 HIGH CVEs in any dependency.

Save your report to `.ignorar/production-reports/dependency-scanner/phase-{N}/{TIMESTAMP}-phase-{N}-dependency-scanner-audit.md`
""")
```

**circular-import-detector:**
```
Task(subagent_type="circular-import-detector", prompt="""Detect circular imports in all Python source files.
Build full import graph using AST analysis and run DFS cycle detection.

Target project: [TARGET_PROJECT]

PASS criteria: 0 circular import cycles in src/.

Save your report to `.ignorar/production-reports/circular-import-detector/phase-{N}/{TIMESTAMP}-phase-{N}-circular-import-detector-scan.md`
""")
```

Also update the Wave 3 threshold reference comment (if it exists) to include:
- dependency-scanner: PASS = 0 CRITICAL + 0 HIGH CVEs in dependencies
- circular-import-detector: PASS = 0 circular import cycles

STEP 4 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/skills/verify/SKILL.md
git commit -m "feat: add coverage gate (75%) to Step 5 + wire dependency-scanner and circular-import-detector into Wave 3 (Gaps 1,2,5)"
```

STEP 5 — Write implementation report:
Create `.ignorar/production-reports/skill-editor-b1/2026-03-05-skill-editor-b1-implementation-report.md`:
```
# SKILL.md Editor (B1) — Implementation Report
**Date:** 2026-03-05
**Task:** Edit .claude/skills/verify/SKILL.md with 2 changes
**File edited:** .claude/skills/verify/SKILL.md
**Commit:** [paste hash]

## What Was Done
Change 1: Added --cov src --cov-report=term-missing --cov-fail-under=75 to pytest command in Step 5.
Change 2: Added dependency-scanner and circular-import-detector Task blocks at end of Wave 3.
/verify now runs 13 agents total (Wave 3 has 8 agents).

## Result
DONE
```

STEP 6 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: B1 (SKILL.md editor)
STATUS: DONE
FILE: .claude/skills/verify/SKILL.md
COMMIT: [7-char hash]
SUMMARY: Change 1: Added pytest --cov-fail-under=75 coverage gate to Step 5. Change 2: Added dependency-scanner and circular-import-detector Task blocks to Wave 3. /verify now runs 13 agents (Wave 3 has 8). File committed.
UNBLOCKS: NONE
```
---

### B2 — Edit verification-thresholds.md

**Spawn with:** `subagent_type="general-purpose"`, `name="B2-thresholds-editor"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent B2. Your single task is to edit one existing file with 3 additions.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Edit `.claude/docs/verification-thresholds.md` to add entries for 2 new agents.

ESTIMATED CONTEXT USAGE: ~20k tokens. You have plenty of room.

STEP 1 — Read these files fully:
- `.claude/docs/verification-thresholds.md` (full current content)
- `.claude/agents/dependency-scanner.md`
- `.claude/agents/circular-import-detector.md`

STEP 2 — Make 3 additions:

**ADDITION 1: Add 2 rows to the Verification Thresholds Table**

Find the table in the file. Find the row for `regression-guard` (should be row 11).
Immediately after that row, add:

```
| **dependency-scanner** | Dependency Security | 0 CRITICAL CVEs, 0 HIGH CVEs | Any CRITICAL or HIGH CVE in dependencies | Yes | dependency-scanner |
| **circular-import-detector** | Import Graph | 0 circular import cycles | Any circular import cycle detected | Yes | circular-import-detector |
```

**ADDITION 2: Add 2 detailed sections after the existing section 11 (regression-guard)**

After the last existing agent section (`### 11. regression-guard`), add:

```markdown
### 12. dependency-scanner

**Scope:** Known CVE detection in Python package dependencies via uv pip audit

**Checks:**
- Runs `uv pip audit` against all packages installed in the target project virtual environment
- Falls back to `pip-audit --format=json` if uv pip audit is unavailable
- Reports CRITICAL (CVSS >= 9.0), HIGH (CVSS 7.0-8.9), MEDIUM, and LOW findings
- MEDIUM and LOW are non-blocking warnings

**Pass:** 0 CRITICAL CVEs, 0 HIGH CVEs in any dependency
**Fail:** Any CRITICAL or HIGH severity CVE in any installed package

---

### 13. circular-import-detector

**Scope:** Python circular import cycle detection using AST-based import graph analysis

**Checks:**
- Parses all .py files in src/ using Python's `ast` module
- Builds a directed import graph (module A -> modules that A imports)
- Runs DFS cycle detection on the full graph
- Reports each cycle as a chain: module.a -> module.b -> module.c -> module.a
- Provides exact import lines in each file that form the cycle

**Pass:** 0 circular import cycles detected in src/
**Fail:** Any circular import cycle detected (even one causes potential ImportError at runtime)
```

**ADDITION 3: Update the Last Updated date**

Find `**Last Updated:** 2026-03-05` — if already today's date, leave it. If it's an
older date, change it to `**Last Updated:** 2026-03-05`.

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/docs/verification-thresholds.md
git commit -m "feat: add thresholds for dependency-scanner (section 12) and circular-import-detector (section 13) (Gaps 1,5)"
```

STEP 4 — Write implementation report:
Create `.ignorar/production-reports/thresholds-editor-b2/2026-03-05-thresholds-editor-b2-implementation-report.md`:
```
# verification-thresholds.md Editor (B2) — Implementation Report
**Date:** 2026-03-05
**Task:** Add sections 12 and 13 to verification-thresholds.md
**File edited:** .claude/docs/verification-thresholds.md
**Commit:** [paste hash]

## What Was Done
Added 2 table rows and 2 detailed sections (12: dependency-scanner, 13: circular-import-detector).
Updated Last Updated date if needed.

## Result
DONE
```

STEP 5 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: B2 (verification-thresholds.md editor)
STATUS: DONE
FILE: .claude/docs/verification-thresholds.md
COMMIT: [7-char hash]
SUMMARY: Added 2 table rows and sections 12 (dependency-scanner) and 13 (circular-import-detector) to verification-thresholds.md. Thresholds: dep-scanner PASS=0 CRITICAL+HIGH CVEs, circular-import PASS=0 cycles. Updated Last Updated date. File committed.
UNBLOCKS: NONE
```
---

### B3 — Edit 04-agents.md

**Spawn with:** `subagent_type="general-purpose"`, `name="B3-agents-doc-editor"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**Pass this prompt exactly:**

---
You are agent B3. Your single task is to edit one existing file with 2 new agent sections.

MetaProject path: /Users/bruno/sec-llm-workbench/

TASK: Edit `.claude/workflow/04-agents.md` to document dependency-scanner and circular-import-detector.

ESTIMATED CONTEXT USAGE: ~30k tokens (04-agents.md is large). You have room but be efficient.

STEP 1 — Read these files fully:
- `.claude/workflow/04-agents.md` (full content — study the format of "### 9. smoke-test-runner" and "### 11. regression-guard" as format templates)
- `.claude/agents/dependency-scanner.md`
- `.claude/agents/circular-import-detector.md`

STEP 2 — Add 2 new agent sections after the existing `### 11. regression-guard` section.

Follow the EXACT same format as sections 9, 10, 11 (scope, model, when to use, what it checks table, PASS/FAIL criteria, example invocation).

**Section 12 — dependency-scanner:**
```markdown
### 12. dependency-scanner

**Scope:** Known CVE detection in Python package dependencies

**Model:** Sonnet

**When to use:**
- Every /verify run (Wave 3, parallel with other Wave 3 agents)
- After adding or upgrading any package in pyproject.toml
- Before releasing to production (security gate)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **CRITICAL CVE** | Dependency has CVE with CVSS >= 9.0 | CRITICAL |
| **HIGH CVE** | Dependency has CVE with CVSS 7.0-8.9 | HIGH |
| **MEDIUM CVE** | Dependency has CVE with CVSS 4.0-6.9 | MEDIUM (warning) |
| **LOW CVE** | Dependency has CVE with CVSS < 4.0 | LOW (warning) |
| **Audit tool unavailable** | Neither uv pip audit nor pip-audit is installed | CRITICAL |

**PASS/FAIL criteria:**
- **PASS:** 0 CRITICAL CVEs, 0 HIGH CVEs in any dependency
- **FAIL:** Any CRITICAL or HIGH CVE in any installed package
- **Warning (non-blocking):** MEDIUM or LOW CVEs

**Example invocation:**
```python
Task(
    subagent_type="dependency-scanner",
    model="sonnet",
    prompt="""Scan all project dependencies for known CVEs.

Target project: `[TARGET_PROJECT]`

Run uv pip audit and report all CRITICAL and HIGH severity CVEs.

PASS criteria: 0 CRITICAL CVEs, 0 HIGH CVEs.

Save your report to `.ignorar/production-reports/dependency-scanner/phase-{N}/{TIMESTAMP}-phase-{N}-dependency-scanner-audit.md`
"""
)
```
```

**Section 13 — circular-import-detector:**
```markdown
### 13. circular-import-detector

**Scope:** Python circular import cycle detection via AST-based import graph analysis

**Model:** Sonnet

**When to use:**
- Every /verify run (Wave 3, parallel with other Wave 3 agents)
- After adding new modules or restructuring the package layout
- After any refactoring that moves imports between modules

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Circular import cycle** | Module A imports B which imports A (direct or transitive) | HIGH |
| **Core module in cycle** | Cycle involves state, DI, graph, or config modules | CRITICAL |

**Verification method:**
1. Find all .py files in src/ using `find`
2. Parse each file with `ast.parse()` to extract Import and ImportFrom nodes
3. Build directed graph: module -> set of modules it imports
4. Run DFS on the full graph to detect cycles
5. For each cycle: report the full chain and the exact import lines

**PASS/FAIL criteria:**
- **PASS:** 0 circular import cycles in src/
- **FAIL:** Any circular import cycle detected

**Example invocation:**
```python
Task(
    subagent_type="circular-import-detector",
    model="sonnet",
    prompt="""Detect circular imports in all Python source files.

Target project: `[TARGET_PROJECT]`

Build full import graph using AST and run DFS cycle detection.

PASS criteria: 0 cycles in src/.

Save your report to `.ignorar/production-reports/circular-import-detector/phase-{N}/{TIMESTAMP}-phase-{N}-circular-import-detector-scan.md`
"""
)
```
```

STEP 3 — Also update the Wave 3 agents table (find where it lists the existing Wave 3 agents):
Add 2 new rows after the regression-guard row:
```
| dependency-scanner | Wave 3 | CVE scan of all dependencies | ~300+ lines | Sonnet |
| circular-import-detector | Wave 3 | Circular import cycle detection | ~300+ lines | Sonnet |
```

STEP 4 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/workflow/04-agents.md
git commit -m "feat: document dependency-scanner (section 12) and circular-import-detector (section 13) in 04-agents (Gaps 1,5)"
```

STEP 5 — Write implementation report:
Create `.ignorar/production-reports/agents-doc-editor-b3/2026-03-05-agents-doc-editor-b3-implementation-report.md`:
```
# 04-agents.md Editor (B3) — Implementation Report
**Date:** 2026-03-05
**Task:** Add sections 12 and 13 to 04-agents.md
**File edited:** .claude/workflow/04-agents.md
**Commit:** [paste hash]

## What Was Done
Added sections 12 (dependency-scanner) and 13 (circular-import-detector) following
exact same format as existing sections 9-11. Updated Wave 3 agents table with 2 new rows.

## Result
DONE
```

STEP 6 — Send message to orchestrator (recipient: "orchestrator"):
```
AGENT: B3 (04-agents.md editor)
STATUS: DONE
FILE: .claude/workflow/04-agents.md
COMMIT: [7-char hash]
SUMMARY: Added sections 12 (dependency-scanner) and 13 (circular-import-detector) to 04-agents.md following existing format. Includes scope, model, when-to-use, checks table, PASS/FAIL criteria, example invocations. Updated Wave 3 table with 2 new rows. File committed.
UNBLOCKS: NONE
```
---

## WAVE C AGENT PROMPT

### C1 — Summarizer

**Spawn with:** `subagent_type="general-purpose"`, `name="C1-summarizer"`, `team_name="verify-gap-closure-2-2026-03-05"`, `mode="bypassPermissions"`, `run_in_background=true`

**ONLY spawn after ALL 3 Wave B agents have reported DONE.**

**Pass this prompt exactly:**

---
You are agent C1, the final summarizer for the /verify gap closure implementation.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR TASK: Verify all files are in place, read all implementation reports, write a final
summary report, commit it, and send the summary to the orchestrator.

STEP 1 — Verify all expected files exist on disk:
```bash
ls /Users/bruno/sec-llm-workbench/.claude/agents/dependency-scanner.md
ls /Users/bruno/sec-llm-workbench/.claude/agents/smoke-test-runner.md
ls /Users/bruno/sec-llm-workbench/.claude/agents/circular-import-detector.md
ls /Users/bruno/sec-llm-workbench/.claude/scripts/scan-git-history-for-secrets.sh
ls /Users/bruno/sec-llm-workbench/.claude/skills/verify/SKILL.md
ls /Users/bruno/sec-llm-workbench/.claude/docs/verification-thresholds.md
ls /Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md
```
Note any missing files as FAILED items.

STEP 2 — Get git log to confirm all commits:
```bash
cd /Users/bruno/sec-llm-workbench && git log --oneline -10
```

STEP 3 — Read available implementation reports (use Glob to find them):
```bash
find /Users/bruno/sec-llm-workbench/.ignorar/production-reports/ -name "2026-03-05-*-implementation-report.md" 2>/dev/null
```
Read each report found and extract the "Result" line.

STEP 4 — Create the directory and write the final summary:
```bash
mkdir -p /Users/bruno/sec-llm-workbench/.ignorar/production-reports/final-summary
```

Write to: `.ignorar/production-reports/final-summary/2026-03-05-verify-gap-closure-2-final-summary.md`

Content:
```markdown
# /verify Gap Closure — Final Implementation Summary
**Date:** 2026-03-05
**Implemented by:** TeamCreate agent team (Orchestrator + 7 worker agents across 3 waves)

## Gaps Closed

| Gap | Description | Status | Agent/File |
|-----|-------------|--------|-----------|
| 1 | Dependency CVE scanning | DONE | .claude/agents/dependency-scanner.md |
| 2 | Coverage threshold enforcement (75%) | DONE | .claude/skills/verify/SKILL.md |
| 3 | Smoke test edge cases (3 additional inputs) | DONE | .claude/agents/smoke-test-runner.md |
| 4 | Secrets in git history (one-time scan script) | DONE | .claude/scripts/scan-git-history-for-secrets.sh |
| 5 | Circular import detection | DONE | .claude/agents/circular-import-detector.md |

## Files Created (4)
- .claude/agents/dependency-scanner.md
- .claude/agents/circular-import-detector.md
- .claude/scripts/scan-git-history-for-secrets.sh
- [smoke-test-runner.md was edited, not created]

## Files Modified (4)
- .claude/agents/smoke-test-runner.md (3 edge case inputs added)
- .claude/skills/verify/SKILL.md (coverage gate + 2 new agents wired in Wave 3)
- .claude/docs/verification-thresholds.md (sections 12, 13 added)
- .claude/workflow/04-agents.md (sections 12, 13 added)

## Git Commits (last 10)
[paste output of git log --oneline -10]

## /verify Coverage After This Implementation

| Check | Agent | Status |
|-------|-------|--------|
| Type hints, Pydantic v2, httpx | best-practices-enforcer | Active |
| OWASP, secrets, injection | security-auditor | Active |
| Library API hallucinations | hallucination-detector | Active |
| Code quality, complexity | code-reviewer | Active |
| Test coverage generation | test-generator | Active |
| Hollow endpoints, broken chains | integration-tracer (AST) | Active |
| asyncio.run() in async contexts | async-safety-auditor | Active |
| No-op validators, swallowed exceptions | semantic-correctness-auditor | Active |
| Active-project guard | SKILL.md guard block | Active |
| End-to-end pipeline execution | smoke-test-runner | Active |
| Smoke test edge cases | smoke-test-runner (extended) | Active |
| Env var / docker config consistency | config-validator | Active |
| Cross-phase regression | regression-guard | Active |
| Dependency CVE scanning | dependency-scanner | Active |
| Circular import detection | circular-import-detector | Active |
| Coverage threshold (>=75%) | SKILL.md pytest gate | Active |
| Secrets in git history | .claude/scripts/scan-git-history-for-secrets.sh | Manual (run once) |

## Notes
- Gap 4 (secrets history scan) is a one-time manual script, not a /verify agent.
  Run it with: `bash .claude/scripts/scan-git-history-for-secrets.sh`
- Coverage threshold is set to 75%. Adjust in SKILL.md if project target is different.
- /verify now runs 13 agents automatically (was 11).

## Result
ALL 5 GAPS CLOSED. Implementation complete.
```

STEP 5 — Commit the summary report:
```bash
cd /Users/bruno/sec-llm-workbench
git add .ignorar/production-reports/final-summary/2026-03-05-verify-gap-closure-2-final-summary.md
git commit -m "docs: add verify gap closure 2 final implementation summary"
```

STEP 6 — Send this message to the orchestrator (recipient: "orchestrator"):

```
AGENT: C1 (summarizer)
STATUS: DONE
FILE: .ignorar/production-reports/final-summary/2026-03-05-verify-gap-closure-2-final-summary.md

IMPLEMENTATION COMPLETE — /verify GAP CLOSURE 2

All 5 remaining gaps in /verify have been implemented across 7 agents in 3 waves.

Files created (3 new agents/scripts):
- .claude/agents/dependency-scanner.md (Gap 1: CVE audit via uv pip audit)
- .claude/agents/circular-import-detector.md (Gap 5: AST cycle detection)
- .claude/scripts/scan-git-history-for-secrets.sh (Gap 4: one-time git history scan)

Files modified (4):
- .claude/agents/smoke-test-runner.md (Gap 3: 3 edge cases added)
- .claude/skills/verify/SKILL.md (Gap 2: coverage gate 75% + 2 new agents in Wave 3)
- .claude/docs/verification-thresholds.md (sections 12, 13 added)
- .claude/workflow/04-agents.md (sections 12, 13 added)

/verify now runs 13 agents automatically (was 11).
Coverage gate enforces >=75% minimum.
Secrets history scan is manual (run once): bash .claude/scripts/scan-git-history-for-secrets.sh
Full coverage table and git commits in final summary report.
```
---

## FILE PATHS REFERENCE TABLE

All paths relative to `/Users/bruno/sec-llm-workbench/` unless shown as absolute.

| File | Action | Agent | Wave |
|------|--------|-------|------|
| `.claude/agents/dependency-scanner.md` | CREATE | A1 | Wave A |
| `.claude/agents/smoke-test-runner.md` | EDIT (add edge cases) | A2 | Wave A |
| `.claude/agents/circular-import-detector.md` | CREATE | A3 | Wave A |
| `.claude/scripts/scan-git-history-for-secrets.sh` | CREATE | A4 | Wave A |
| `.claude/skills/verify/SKILL.md` | EDIT (coverage gate + 2 agents) | B1 | Wave B |
| `.claude/docs/verification-thresholds.md` | EDIT (sections 12, 13) | B2 | Wave B |
| `.claude/workflow/04-agents.md` | EDIT (sections 12, 13) | B3 | Wave B |
| `.ignorar/production-reports/final-summary/2026-03-05-verify-gap-closure-2-final-summary.md` | CREATE | C1 | Wave C |

---

## DEPENDENCY RULES

```
Wave B MUST NOT start until ALL 4 Wave A agents have reported DONE.
Wave C MUST NOT start until ALL 3 Wave B agents have reported DONE.

If any Wave A agent reports FAILED:
  → Stop. Do NOT start Wave B.
  → SendMessage to team-lead: "BLOCKED: Agent <X> FAILED. Reason: <summary>. Awaiting instructions."

If any Wave B agent reports FAILED:
  → Stop. Do NOT start Wave C.
  → SendMessage to team-lead: "BLOCKED: Agent <X> FAILED. Reason: <summary>. Awaiting instructions."

If an agent goes idle without reporting:
  → User monitors Tmux panes. User will inform team-lead.
  → team-lead will send orchestrator a nudge.
  → Orchestrator re-sends the task prompt to the idle agent.
```

---

## CONTEXT SAFETY NOTES

Estimated token usage per agent (well within 200k limit for all):

| Agent | Files read | Estimated tokens | Safety margin |
|-------|-----------|-----------------|---------------|
| A1 | 2 agent files (~200 lines each) | ~10k | High |
| A2 | 1 agent file (~200 lines) | ~12k | High |
| A3 | 2 agent files (~200 lines each) | ~12k | High |
| A4 | 1 script file (~100 lines) | ~8k | High |
| B1 | SKILL.md (~450 lines) + 2 agent files | ~25k | Good |
| B2 | thresholds.md (~200 lines) + 2 agent files | ~18k | High |
| B3 | 04-agents.md (~600 lines) + 2 agent files | ~35k | Good |
| C1 | 7 ls outputs + git log + 7 report files (~100 lines each) | ~30k | Good |
| Orchestrator | This briefing + 8 short DONE messages | ~25k | Good |

No agent approaches the 200k context limit. No splitting required.

---

*End of briefing. The orchestrator reads this file and executes the plan exactly as written.
No improvisation. No interpretation. Every step is specified. Follow it literally.*
