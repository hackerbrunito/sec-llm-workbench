# Orchestrator Briefing: /verify Improvements Implementation
# Date: 2026-03-05
# Author: Claude Code (main context)
# Purpose: Complete instructions for orchestrator and all worker agents

---

## CONTEXT

You are the **orchestrator and team lead** for implementing 6 pending improvements to the `/verify`
command in the MetaProject located at `/Users/bruno/sec-llm-workbench/`.

This is the MetaProject — a Python project generator framework. It is NOT the target project (SIOPV).
All file operations in this briefing refer to MetaProject files unless explicitly stated otherwise.

**MetaProject path:** `/Users/bruno/sec-llm-workbench/`
**Handoff file (source of truth for all 6 items):** `.claude/handoffs/2026-03-05-verify-improvements-handoff.md`

---

## YOUR ROLE AS ORCHESTRATOR

You coordinate agents. You do NOT read files, write files, or implement anything yourself.

Your job:
1. Spawn Wave A agents (A1, A2, A3, A4) simultaneously — give them all the green light at once
2. Wait for all 4 Wave A agents to report DONE via SendMessage
3. Spawn Wave B agents (B1, B2, B3) simultaneously — give them all the green light at once
4. Wait for all 3 Wave B agents to report DONE via SendMessage
5. Spawn Wave C agent (C1) — the summarizer
6. Wait for C1 to report DONE via SendMessage
7. Relay C1's summary message back to the user (main context)

**If any agent reports FAILED:** stop the wave, report FAILED status with agent name and reason to user. Do not proceed to the next wave.

---

## TEAM STRUCTURE

```
Orchestrator (you)
├── Wave A — spawn simultaneously
│   ├── A1: Create smoke-test-runner.md
│   ├── A2: Create config-validator.md
│   ├── A3: Create regression-guard.md
│   └── A4: Update integration-tracer.md (AST improvement)
│
├── [Wait for all 4 Wave A agents to report DONE]
│
├── Wave B — spawn simultaneously after Wave A completes
│   ├── B1: Edit SKILL.md (5 changes: guard + timeout + wire 3 new agents)
│   ├── B2: Edit verification-thresholds.md (add 3 new agent entries)
│   └── B3: Edit 04-agents.md (document 3 new agents)
│
├── [Wait for all 3 Wave B agents to report DONE]
│
└── Wave C — spawn after Wave B completes
    └── C1: Write final summary report + SendMessage to orchestrator
```

---

## COMMUNICATION PROTOCOL

### What agents send back to you (via SendMessage)

Each agent sends ONE message when done. Format:

```
AGENT: [agent-name]
STATUS: DONE | FAILED
FILE: [exact path of file created or edited]
SUMMARY: [2-4 sentences describing what was done, what was added, any warnings]
```

### What you send to user at the end

When C1 sends its final message, relay it directly to the user as-is.
Do not add interpretation or commentary beyond "All waves complete."

---

## GIT INSTRUCTIONS FOR ALL AGENTS

All agents commit in the **MetaProject** directory: `/Users/bruno/sec-llm-workbench/`

Before committing, run:
```bash
cd /Users/bruno/sec-llm-workbench
git add <file-path>
git commit -m "<commit message>"
```

The pre-commit hook checks for pending markers in the SIOPV project (`~/siopv/.build/checkpoints/pending/`).
As long as SIOPV has no pending Python files awaiting verification, commits will go through.
If the hook blocks the commit, include that as a WARNING in your SendMessage — do not retry.

---

## WAVE A AGENT PROMPTS

### A1 — Create smoke-test-runner.md

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are implementing Item 2 from the /verify improvements plan in the MetaProject.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Create the file `.claude/agents/smoke-test-runner.md`

STEP 1 — Read these files for context (do not skip):
- `.claude/handoffs/2026-03-05-verify-improvements-handoff.md` (read Item 2 section)
- `.claude/agents/async-safety-auditor.md` (use as format reference for YAML frontmatter and structure)

STEP 2 — Create `.claude/agents/smoke-test-runner.md` with this exact content structure:

YAML frontmatter (copy this exactly):
```
<!-- version: 2026-03 -->
---
name: smoke-test-runner
description: Execute end-to-end pipeline smoke test with synthetic CVE input. Verifies the pipeline runs from START to END without crashing and output contains required fields. Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: default
cache_control: ephemeral
budget_tokens: 15000
---
```

Body content must include these sections (write them in full detail):

## Project Context (CRITICAL)
- You are invoked from the meta-project (sec-llm-workbench/). You are NOT working on the meta-project.
- Target project path is provided in your invocation prompt. If not provided, read `.build/active-project`.
- All `uv run` commands must use `cd` with the expanded target path.
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project).

## Role Definition
You are the Smoke Test Runner. Your job is to actually execute the target project's pipeline with a synthetic CVE input and verify it runs end-to-end without crashing, producing output with all required fields. Static analysis cannot catch runtime failures — you can.

## Actions (implement all of these in order)

1. Read `.build/active-project` to get TARGET path. Expand `~` to `$HOME`.
2. Read `$TARGET/pyproject.toml` to discover the project name and CLI entry points.
3. Read `$TARGET/README.md` (if exists) to find how to run the pipeline.
4. Discover the CLI command:
   - Grep for `@app.command` or `@cli.command` in `$TARGET/src/` to find the main command
   - Identify what input parameter accepts a CVE ID (look for `cve_id`, `cve`, `vulnerability_id`)
5. Check the pipeline is installed: `cd $TARGET && uv run python -c "import [project_name]"` — if this fails, report FAIL with reason.
6. Run the pipeline with synthetic input: `cd $TARGET && uv run [cli-command] [cve-flag] CVE-2024-1234 2>&1`
   - Capture full output including any exception tracebacks
   - Set a timeout: if command does not complete in 120 seconds, kill it and report TIMEOUT-FAIL
7. Inspect the output:
   - If any unhandled exception appears in output: FAIL
   - If output is empty: FAIL with reason "no output produced"
   - If output contains JSON or dict-like structure: parse and check for required fields
8. Required output fields check: verify output contains ALL of:
   - `classification` or `category`
   - `severity` or `cvss_score`
   - `cve_id` or `id`
   - If any required field is missing: FAIL with reason "missing field: [field_name]"
9. Save report to `.ignorar/production-reports/smoke-test-runner/phase-{N}/{TIMESTAMP}-phase-{N}-smoke-test-runner-smoke-test.md`
   - Create directory if it does not exist
   - {N} = content of `.build/current-phase`
   - {TIMESTAMP} = `date +%Y-%m-%d-%H%M%S`

## PASS/FAIL Criteria
- PASS: Pipeline runs end-to-end without exception, output contains all required fields
- FAIL: Any unhandled exception, timeout, empty output, or missing required field

## Findings Severity
| Finding | Severity |
|---------|----------|
| Unhandled exception during pipeline run | CRITICAL |
| Pipeline timeout (>120 seconds) | CRITICAL |
| Missing required output field | HIGH |
| Empty output (no data produced) | HIGH |
| Import failure (project not installable) | CRITICAL |

## Report Format
```markdown
# Smoke Test Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [project path]
**Input:** CVE-2024-1234 (synthetic)

## Execution Summary
- Command run: [full command]
- Exit code: [N]
- Duration: [N] seconds
- Status: PASS / FAIL

## Output Inspection
- Output length: [N] characters
- Required fields found: classification=[Y/N], severity=[Y/N], cve_id=[Y/N]

## Findings
[List any CRITICAL/HIGH findings]

## Result
SMOKE TEST PASSED / FAILED
```

STEP 3 — Commit the file:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/smoke-test-runner.md
git commit -m "feat: add smoke-test-runner agent (Item 2 - verify improvements)"
```

STEP 4 — Send a message to the orchestrator with this exact format:
```
AGENT: A1 (smoke-test-runner creator)
STATUS: DONE
FILE: .claude/agents/smoke-test-runner.md
SUMMARY: Created smoke-test-runner.md agent. Agent discovers CLI entry point, runs pipeline with CVE-2024-1234, checks output for classification/severity/cve_id fields. PASS criteria: 0 crashes, all required fields present. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe what went wrong in SUMMARY.
---

### A2 — Create config-validator.md

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are implementing Item 3 from the /verify improvements plan in the MetaProject.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Create the file `.claude/agents/config-validator.md`

STEP 1 — Read these files for context (do not skip):
- `.claude/handoffs/2026-03-05-verify-improvements-handoff.md` (read Item 3 section)
- `.claude/agents/async-safety-auditor.md` (use as format reference for YAML frontmatter and structure)

STEP 2 — Create `.claude/agents/config-validator.md` with this exact content structure:

YAML frontmatter (copy this exactly):
```
<!-- version: 2026-03 -->
---
name: config-validator
description: Validate that all required environment variables are documented in .env.example and that docker-compose.yml service names/ports match what the code expects. Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: plan
disallowedTools: [Write, Edit]
cache_control: ephemeral
budget_tokens: 10000
---
```

Body content must include these sections (write them in full detail):

## Project Context (CRITICAL)
- You are invoked from the meta-project. Target project path is provided in your invocation prompt or read from `.build/active-project`.
- All file operations target the target project directory.
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project).

## Role Definition
You are the Config Validator. Your job is to ensure the target project's configuration is consistent: every environment variable the code reads must be documented in `.env.example`, and every Docker service name/port the code references must match what `docker-compose.yml` defines.

## Actions (implement all in order)

1. Read `.build/active-project` to get TARGET. Expand `~` to `$HOME`.

2. Build required env vars list:
   - Grep `$TARGET/src` for `settings.` attribute access patterns (e.g., `settings.api_key`, `settings.database_url`)
   - Grep `$TARGET/src` for `os.getenv(` calls — extract the var name from the first argument
   - Grep `$TARGET/src` for `os.environ[` and `os.environ.get(` patterns
   - Deduplicate and sort the list

3. Read `$TARGET/.env.example` (if it exists):
   - Extract all variable names (lines matching `VAR_NAME=`)
   - If `.env.example` does not exist: report FAIL "no .env.example found"

4. Compare: flag any required var (from step 2) not present in `.env.example`

5. Read `$TARGET/docker-compose.yml` (if it exists):
   - Extract all service names (under `services:` key)
   - Extract all port mappings
   - If no docker-compose.yml: skip steps 6-7, note in report

6. Grep `$TARGET/src` for references to each docker service name:
   - Check hostnames used in connection strings, URLs, or settings defaults
   - Flag any service name in code that does not match a service defined in docker-compose.yml

7. Read `$TARGET/src/**/settings.py` or `$TARGET/src/**/config.py`:
   - Find all `Settings` fields with no default value (fields that MUST come from env)
   - Cross-reference with `.env.example` — flag any required Settings field not documented

8. Save report to `.ignorar/production-reports/config-validator/phase-{N}/{TIMESTAMP}-phase-{N}-config-validator-config-check.md`

## PASS/FAIL Criteria
- PASS: All required env vars documented in .env.example, all docker service references consistent
- FAIL: Any undocumented required env var OR any mismatched service name/port

## Findings Severity
| Finding | Severity |
|---------|----------|
| Required env var missing from .env.example | HIGH |
| Docker service name in code not in docker-compose.yml | HIGH |
| Settings field with no default not in .env.example | HIGH |
| .env.example missing entirely | CRITICAL |

## Report Format
```markdown
# Config Validator Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [project path]

## Summary
- Required env vars found in code: N
- Documented in .env.example: N
- Undocumented (FAIL): N
- Docker services in docker-compose.yml: N
- Docker service references in code: N
- Mismatched references: N
- Status: PASS / FAIL

## Findings
[List all HIGH/CRITICAL findings with file:line]

## Result
CONFIG VALIDATOR PASSED / FAILED
```

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/config-validator.md
git commit -m "feat: add config-validator agent (Item 3 - verify improvements)"
```

STEP 4 — Send a message to the orchestrator:
```
AGENT: A2 (config-validator creator)
STATUS: DONE
FILE: .claude/agents/config-validator.md
SUMMARY: Created config-validator.md agent. Agent greps settings.* and os.getenv() to build required env vars list, cross-references with .env.example, validates docker-compose service names against code references. PASS criteria: all env vars documented, all docker services consistent. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

### A3 — Create regression-guard.md

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are implementing Item 6 from the /verify improvements plan in the MetaProject.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Create the file `.claude/agents/regression-guard.md`

STEP 1 — Read these files for context (do not skip):
- `.claude/handoffs/2026-03-05-verify-improvements-handoff.md` (read Item 6 section)
- `.claude/agents/async-safety-auditor.md` (use as format reference for YAML frontmatter and structure)

STEP 2 — Create `.claude/agents/regression-guard.md` with this exact content structure:

YAML frontmatter (copy this exactly):
```
<!-- version: 2026-03 -->
---
name: regression-guard
description: Detect cross-phase regressions by finding recently changed files, building a reverse dependency map, running pytest on affected modules, and flagging any previously-passing test that now fails. Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: default
cache_control: ephemeral
budget_tokens: 15000
---
```

Body content must include these sections (write in full detail):

## Project Context (CRITICAL)
- You are invoked from the meta-project. Target project path provided in prompt or read from `.build/active-project`.
- All file operations and git commands must target the target project directory.
- Reports go to `sec-llm-workbench/.ignorar/production-reports/` (meta-project).

## Role Definition
You are the Regression Guard. Your job is to ensure that changes to shared modules have not broken functionality verified in earlier phases. You run pytest only on modules that are reverse-dependent on recently changed files — not the full test suite — to catch regressions efficiently.

## Actions (implement all in order)

1. Read `.build/active-project` to get TARGET. Expand `~` to `$HOME`.

2. Find recently changed files:
   ```bash
   cd $TARGET && git diff HEAD~1 --name-only
   ```
   Filter to `.py` files only.

3. Build reverse dependency map:
   For each changed file, grep the entire `$TARGET/src` directory to find which other modules import it:
   ```bash
   grep -rn "from [module_path] import\|import [module_name]" $TARGET/src --include="*.py"
   ```
   Collect all files that import from any changed file.

4. Identify affected test files:
   For each reverse-dependent module, find its corresponding test file in `$TARGET/tests/`:
   - `src/siopv/foo/bar.py` → look for `tests/foo/test_bar.py` or `tests/test_bar.py`
   - Use Glob to find matches

5. Run pytest on affected test files only:
   ```bash
   cd $TARGET && uv run pytest [affected_test_files] -v --tb=short 2>&1
   ```
   If no affected test files found: report PASS with note "no reverse-dependent tests found"

6. Parse pytest output:
   - Extract PASSED, FAILED, ERROR counts
   - Identify which specific tests failed (test name + file + line)
   - A FAIL means a test that ran is now failing — do not flag tests that were already skipped

7. Save report to `.ignorar/production-reports/regression-guard/phase-{N}/{TIMESTAMP}-phase-{N}-regression-guard-regression-check.md`

## PASS/FAIL Criteria
- PASS: All tests in affected modules pass (0 FAILED, 0 ERROR)
- FAIL: Any FAILED or ERROR in affected test modules

## Findings Severity
| Finding | Severity |
|---------|----------|
| Previously-passing test now FAILED | HIGH |
| Test ERROR (exception during collection/setup) | HIGH |

## Report Format
```markdown
# Regression Guard Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [project path]

## Summary
- Changed files (HEAD~1): N
- Reverse-dependent modules: N
- Affected test files: N
- Tests run: N
- PASSED: N | FAILED: N | ERROR: N
- Status: PASS / FAIL

## Changed Files
[list]

## Reverse Dependencies Found
[list: changed_file → dependent_module]

## Regressions
[For each FAILED test: test name, file, line, error message]

## Result
REGRESSION GUARD PASSED / FAILED
```

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/regression-guard.md
git commit -m "feat: add regression-guard agent (Item 6 - verify improvements)"
```

STEP 4 — Send a message to the orchestrator:
```
AGENT: A3 (regression-guard creator)
STATUS: DONE
FILE: .claude/agents/regression-guard.md
SUMMARY: Created regression-guard.md agent. Agent uses git diff HEAD~1 to find changed files, builds reverse dependency map via grep, runs pytest on affected test modules only, flags any newly-failing tests. PASS criteria: 0 FAILED or ERROR in affected modules. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

### A4 — Update integration-tracer.md (AST improvement)

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are implementing Item 4 from the /verify improvements plan in the MetaProject.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Update the existing file `.claude/agents/integration-tracer.md` to add AST-based call graph analysis as the preferred method, with grep-based tracing as a fallback.

STEP 1 — Read these files:
- `.claude/handoffs/2026-03-05-verify-improvements-handoff.md` (read Item 4 section)
- `.claude/agents/integration-tracer.md` (read the FULL current content — you will edit this file)

STEP 2 — Add a new section to integration-tracer.md

Insert the following new section BEFORE the existing "## Verification Checklist" section.
Do NOT remove or modify any existing content. Only ADD the new section.

New section to insert:

```markdown
## AST-Based Call Graph (Preferred Method)

Before falling back to grep-based tracing, attempt to build a precise call graph using Python's `ast` module. This eliminates false positives from grep matching string literals or comments.

### Option A: Pure Python ast (no new dependencies)

```bash
TARGET="${TARGET/#\~/$HOME}"
python3 - <<'EOF'
import ast
import os
import sys
from pathlib import Path
from collections import defaultdict

target = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TARGET", "")
src = Path(target) / "src"

# Build: function_name -> list of functions it calls
call_graph = defaultdict(set)
definitions = {}  # function_name -> file:line

for py_file in src.rglob("*.py"):
    try:
        tree = ast.parse(py_file.read_text())
    except SyntaxError:
        continue
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            full_name = f"{py_file.stem}.{node.name}"
            definitions[full_name] = f"{py_file}:{node.lineno}"
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        call_graph[full_name].add(child.func.attr)
                    elif isinstance(child.func, ast.Name):
                        call_graph[full_name].add(child.func.id)

# Print call graph
for func, callees in sorted(call_graph.items()):
    print(f"{func} -> {', '.join(sorted(callees))}")
EOF
```

### Option B: pyan3 (if available)

```bash
TARGET="${TARGET/#\~/$HOME}"
cd "$TARGET"
# Check if pyan3 is available
if uv run python -c "import pyan" 2>/dev/null; then
    uv run pyan3 src/**/*.py --dot --no-defines > /tmp/callgraph.dot 2>/dev/null
    echo "Call graph written to /tmp/callgraph.dot"
else
    echo "pyan3 not available — using ast-based method above"
fi
```

### Fallback: grep-based tracing

If both AST methods fail (syntax errors, import failures), fall back to the grep-based approach described in the Verification Checklist below. Note any fallback in the report.
```

STEP 3 — Update the version comment at the top of the file:
Change `<!-- version: 2026-02 -->` to `<!-- version: 2026-03 -->`

STEP 4 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/agents/integration-tracer.md
git commit -m "feat: add AST-based call graph to integration-tracer (Item 4 - verify improvements)"
```

STEP 5 — Send a message to the orchestrator:
```
AGENT: A4 (integration-tracer updater)
STATUS: DONE
FILE: .claude/agents/integration-tracer.md
SUMMARY: Added AST-based call graph section as preferred method before grep-based fallback. Includes pure Python ast option (no new deps) and pyan3 option (if available). Version bumped to 2026-03. Grep-based tracing remains as documented fallback. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

## WAVE B AGENT PROMPTS

### B1 — Edit SKILL.md (5 changes)

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are implementing Items 1, 2, 3, 5, and 6 (SKILL.md wiring only) from the /verify improvements plan.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Edit `.claude/skills/verify/SKILL.md` to add 5 changes. All changes are additive — do not remove any existing content.

STEP 1 — Read these files fully before editing:
- `.claude/skills/verify/SKILL.md` (full current content)
- `.claude/handoffs/2026-03-05-verify-improvements-handoff.md` (Items 1, 2, 3, 5, 6)
- `.claude/agents/smoke-test-runner.md` (to know the agent name and PASS criteria)
- `.claude/agents/config-validator.md` (to know the agent name and PASS criteria)
- `.claude/agents/regression-guard.md` (to know the agent name and PASS criteria)

STEP 2 — Make these 5 edits to SKILL.md:

**CHANGE 1 (Item 1): Add active-project guard at the very start of Step 1**

Find the line that starts "### 1. Identificar Archivos Pendientes" in SKILL.md.
Immediately after that heading and before the existing bash block, insert this new bash block:

```bash
# VALIDATION: Ensure active-project is set and valid before proceeding
TARGET=$(cat .build/active-project 2>/dev/null || echo "")
TARGET="${TARGET/#\~/$HOME}"  # expand ~ to absolute path
if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
    echo "ERROR: .build/active-project is missing or points to non-existent directory: '$TARGET'"
    echo "Fix: echo '~/yourproject/' > .build/active-project"
    exit 1
fi
if [ ! -f "$TARGET/pyproject.toml" ]; then
    echo "ERROR: Target project has no pyproject.toml at: $TARGET"
    echo "This does not look like a valid Python project."
    exit 1
fi
echo "Active project validated: $TARGET"
```

**CHANGE 2 (Item 5): Add Wave 3 timeout and retry logic**

Find the line "Wait for all 3 to complete." in the Wave 3 section.
Immediately after that line, insert:

```
**Wave 3 Timeout and Retry Policy:**
- If a Wave 3 agent does not produce its report file within 10 minutes:
  1. Mark that agent as TIMEOUT-FAIL
  2. Continue with the remaining Wave 3 agents — do NOT stop the wave
  3. Report TIMEOUT-FAIL in the final verdict — do not silently skip it
  4. Retry once after all Wave 3 agents complete if time permits

**After each Wave 3 agent completes, verify its report file was created:**
- Check that the expected report path exists on disk
- If the report file is missing: mark that agent as FAIL with reason "report file not found"
- A Wave 3 agent that runs but produces no report is treated as FAILED
```

**CHANGE 3 (Item 2): Add smoke-test-runner to Wave 3**

Find the Wave 3 section. After the `semantic-correctness-auditor` Task block (the last agent in Wave 3),
add this new Task block:

```
**smoke-test-runner:**
```
Task(subagent_type="smoke-test-runner", prompt="""Execute end-to-end pipeline smoke test with synthetic CVE input.
Verify the pipeline runs from START to END without crashing and output contains all required fields.

Target project: [TARGET_PROJECT]

PASS criteria: Pipeline runs end-to-end without exception, output contains classification, severity, and cve_id fields.

Save your report to `.ignorar/production-reports/smoke-test-runner/phase-{N}/{TIMESTAMP}-phase-{N}-smoke-test-runner-smoke-test.md`
""")
```

Also update the Wave 3 timing comment from "Submit 3 agents in parallel" to "Submit 6 agents in parallel"
and update the threshold reference to include smoke-test-runner: PASS = 0 crashes, required fields present.

**CHANGE 4 (Item 3): Add config-validator to Wave 3**

In the same Wave 3 section, after the smoke-test-runner block, add:

```
**config-validator:**
```
Task(subagent_type="config-validator", prompt="""Validate environment variable documentation and docker service consistency.
Check that all settings.* and os.getenv() references have corresponding entries in .env.example.
Check that docker-compose.yml service names match what the code expects.

Target project: [TARGET_PROJECT]

PASS criteria: All required env vars documented in .env.example, all docker service references consistent.

Save your report to `.ignorar/production-reports/config-validator/phase-{N}/{TIMESTAMP}-phase-{N}-config-validator-config-check.md`
""")
```

Also update threshold reference: config-validator: PASS = all env vars documented, services consistent.

**CHANGE 5 (Item 6): Add regression-guard to Wave 3**

In the same Wave 3 section, after the config-validator block, add:

```
**regression-guard:**
```
Task(subagent_type="regression-guard", prompt="""Check for cross-phase regressions in recently changed files.
Use git diff HEAD~1 to find changed files, build reverse dependency map, run pytest on affected modules.
Flag any previously-passing test that now fails.

Target project: [TARGET_PROJECT]

PASS criteria: All previously-passing tests in reverse-dependent modules still pass (0 FAILED, 0 ERROR).

Save your report to `.ignorar/production-reports/regression-guard/phase-{N}/{TIMESTAMP}-phase-{N}-regression-guard-regression-check.md`
""")
```

Also update threshold reference: regression-guard: PASS = 0 regressions in reverse-dependent modules.

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/skills/verify/SKILL.md
git commit -m "feat: wire 3 new agents into SKILL.md + add active-project guard + Wave 3 timeout (Items 1,2,3,5,6)"
```

STEP 4 — Send a message to the orchestrator:
```
AGENT: B1 (SKILL.md editor)
STATUS: DONE
FILE: .claude/skills/verify/SKILL.md
SUMMARY: Applied 5 changes to SKILL.md: (1) active-project guard with pyproject.toml validation at Step 1 start, (2) Wave 3 timeout/retry policy with report file verification, (3) smoke-test-runner Task block added to Wave 3, (4) config-validator Task block added to Wave 3, (5) regression-guard Task block added to Wave 3. Wave 3 now has 6 parallel agents. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

### B2 — Edit verification-thresholds.md

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are adding 3 new agent entries to the verification thresholds document.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Edit `.claude/docs/verification-thresholds.md` to add entries for 3 new agents.

STEP 1 — Read these files fully:
- `.claude/docs/verification-thresholds.md` (full current content)
- `.claude/agents/smoke-test-runner.md`
- `.claude/agents/config-validator.md`
- `.claude/agents/regression-guard.md`

STEP 2 — Make these 3 additions to verification-thresholds.md:

**ADDITION 1: Add 3 rows to the Verification Thresholds Table**

Find the existing table at the top of the file. After the `semantic-correctness-auditor` row, add:

```
| **smoke-test-runner** | Runtime Verification | 0 crashes, all required fields present | Any crash, timeout, or missing field | Yes | smoke-test-runner |
| **config-validator** | Configuration | All env vars documented, services consistent | Any undocumented env var or mismatched service | Yes | config-validator |
| **regression-guard** | Regression | 0 previously-passing tests failing | Any test regression in affected modules | Yes | regression-guard |
```

**ADDITION 2: Add 3 detailed sections at the end of the "Details by Agent" area**

After the existing section `### 8. semantic-correctness-auditor`, add:

```markdown
### 9. smoke-test-runner

**Scope:** End-to-end pipeline execution with synthetic input — the only agent that actually runs the project

**Runtime Checks:**
- Pipeline imports cleanly (`uv run python -c "import [project]"`)
- Pipeline runs start-to-end with CVE-2024-1234 without unhandled exception
- Pipeline completes within 120 seconds (timeout = CRITICAL)
- Output contains all required fields: `classification`/`category`, `severity`/`cvss_score`, `cve_id`/`id`

**Pass:** Pipeline runs without exception, all required fields present
**Fail:** Any unhandled exception, timeout, empty output, or missing required field

---

### 10. config-validator

**Scope:** Environment variable documentation and Docker service consistency

**Checks:**
- All `settings.*` attribute accesses have corresponding entry in `.env.example`
- All `os.getenv(` calls reference a var documented in `.env.example`
- All `Settings` fields with no default are in `.env.example`
- All Docker service names referenced in code exist in `docker-compose.yml`
- All Docker service ports in code match `docker-compose.yml` definitions

**Pass:** All required env vars documented, all docker service references consistent
**Fail:** Any undocumented required env var OR any mismatched service name/port

---

### 11. regression-guard

**Scope:** Cross-phase regression detection via reverse dependency analysis and targeted pytest

**Checks:**
- Uses `git diff HEAD~1 --name-only` to identify recently changed Python files
- Builds reverse dependency map: which modules import from changed files
- Runs pytest on test files corresponding to reverse-dependent modules only
- Flags any test that was passing before and is now FAILED or ERROR

**Pass:** 0 FAILED, 0 ERROR in all reverse-dependent test modules
**Fail:** Any FAILED or ERROR in affected test modules
```

**ADDITION 3: Update the "Last Updated" date**

Find the line `**Last Updated:** 2026-02-08` and change it to `**Last Updated:** 2026-03-05`

STEP 3 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/docs/verification-thresholds.md
git commit -m "feat: add thresholds for smoke-test-runner, config-validator, regression-guard (Items 2,3,6)"
```

STEP 4 — Send a message to the orchestrator:
```
AGENT: B2 (verification-thresholds.md editor)
STATUS: DONE
FILE: .claude/docs/verification-thresholds.md
SUMMARY: Added 3 new rows to thresholds table and 3 new detailed sections (sections 9, 10, 11) for smoke-test-runner, config-validator, and regression-guard. Updated Last Updated date to 2026-03-05. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

### B3 — Edit 04-agents.md

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are documenting 3 new agents in the agents workflow file.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Edit `.claude/workflow/04-agents.md` to document smoke-test-runner, config-validator, and regression-guard.

STEP 1 — Read these files fully:
- `.claude/workflow/04-agents.md` (full current content — study the format of existing agent sections like "### 7. async-safety-auditor")
- `.claude/agents/smoke-test-runner.md`
- `.claude/agents/config-validator.md`
- `.claude/agents/regression-guard.md`
- `.claude/docs/verification-thresholds.md`

STEP 2 — Add 3 new agent sections to 04-agents.md

Study the format of "### 7. async-safety-auditor" and "### 8. semantic-correctness-auditor" carefully.
Follow the EXACT same structure for each new section.

After the existing `### 8. semantic-correctness-auditor` section, add:

**Section for smoke-test-runner:**
```markdown
### 9. smoke-test-runner

**Scope:** End-to-end runtime verification — the only agent that actually executes the project

**Model:** Sonnet

**When to use:**
- Every /verify run (Wave 3, parallel with other Wave 3 agents)
- Especially critical after changes to graph topology, node implementations, or CLI entry points
- After any change to the pipeline's main execution path

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Import failure** | Project cannot be imported via `uv run python -c "import [project]"` | CRITICAL |
| **Pipeline crash** | Unhandled exception during pipeline run with CVE-2024-1234 | CRITICAL |
| **Timeout** | Pipeline does not complete within 120 seconds | CRITICAL |
| **Missing required field** | Output dict missing `classification`/`severity`/`cve_id` | HIGH |
| **Empty output** | Pipeline completes but produces no output | HIGH |

**PASS/FAIL criteria:**
- **PASS:** Pipeline runs end-to-end without exception, output contains all required fields
- **FAIL:** Any CRITICAL or HIGH finding

**Example invocation:**
```python
Task(
    subagent_type="smoke-test-runner",
    model="sonnet",
    prompt="""Execute end-to-end pipeline smoke test.

Target project: `[TARGET_PROJECT]`

Run pipeline with synthetic input CVE-2024-1234 and verify output contains
classification, severity, and cve_id fields.

PASS criteria: 0 crashes, all required fields present.

Save your report to `.ignorar/production-reports/smoke-test-runner/phase-{N}/{TIMESTAMP}-phase-{N}-smoke-test-runner-smoke-test.md`
"""
)
```
```

**Section for config-validator:**
```markdown
### 10. config-validator

**Scope:** Configuration consistency — env vars and Docker service references

**Model:** Sonnet

**When to use:**
- After adding new Settings fields or new os.getenv() calls
- After modifying docker-compose.yml service definitions
- After any change to infrastructure configuration
- Every /verify run (Wave 3)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Missing .env.example** | No .env.example file found in project root | CRITICAL |
| **Undocumented env var** | settings.* or os.getenv() reference not in .env.example | HIGH |
| **Mismatched docker service** | Service name in code not defined in docker-compose.yml | HIGH |
| **Undocumented Settings field** | Settings field with no default not in .env.example | HIGH |

**PASS/FAIL criteria:**
- **PASS:** All required env vars documented, all docker service references consistent
- **FAIL:** Any CRITICAL or HIGH finding

**Example invocation:**
```python
Task(
    subagent_type="config-validator",
    model="sonnet",
    prompt="""Validate configuration consistency.

Target project: `[TARGET_PROJECT]`

Check all settings.* and os.getenv() references against .env.example.
Check docker-compose.yml service names against code references.

PASS criteria: all env vars documented, all docker services consistent.

Save your report to `.ignorar/production-reports/config-validator/phase-{N}/{TIMESTAMP}-phase-{N}-config-validator-config-check.md`
"""
)
```
```

**Section for regression-guard:**
```markdown
### 11. regression-guard

**Scope:** Cross-phase regression detection via targeted pytest on reverse-dependent modules

**Model:** Sonnet

**When to use:**
- After changes to shared modules (state, DI, constants, graph topology)
- When completing a phase that modifies modules used in earlier phases
- Every /verify run (Wave 3)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Test regression** | Previously-passing test now FAILED after recent changes | HIGH |
| **Test ERROR** | Test fails to collect or setup due to import/fixture error | HIGH |

**Verification method:**
1. `git diff HEAD~1 --name-only` to find recently changed files
2. Grep to find all modules that import from changed files (reverse dependency map)
3. Find corresponding test files for each reverse-dependent module
4. Run `uv run pytest [affected_tests] -v --tb=short`
5. Flag any FAILED or ERROR

**PASS/FAIL criteria:**
- **PASS:** 0 FAILED, 0 ERROR in all reverse-dependent test modules
- **FAIL:** Any FAILED or ERROR in affected test modules

**Example invocation:**
```python
Task(
    subagent_type="regression-guard",
    model="sonnet",
    prompt="""Check for cross-phase regressions.

Target project: `[TARGET_PROJECT]`

Find recently changed files, build reverse dependency map, run pytest on affected modules.
Flag any previously-passing test that now fails.

PASS criteria: 0 regressions in reverse-dependent modules.

Save your report to `.ignorar/production-reports/regression-guard/phase-{N}/{TIMESTAMP}-phase-{N}-regression-guard-regression-check.md`
"""
)
```
```

STEP 3 — Also update the Wave 3 agents table at the top of the Wave 3 section in 04-agents.md:
Find the table that lists `integration-tracer`, `async-safety-auditor`, `semantic-correctness-auditor`.
Add 3 new rows:
```
| smoke-test-runner | Wave 3 | End-to-end pipeline execution | ~500+ lines | Sonnet |
| config-validator | Wave 3 | Env var and docker config consistency | ~500+ lines | Sonnet |
| regression-guard | Wave 3 | Cross-phase regression detection | ~500+ lines | Sonnet |
```

STEP 4 — Commit:
```bash
cd /Users/bruno/sec-llm-workbench
git add .claude/workflow/04-agents.md
git commit -m "feat: document smoke-test-runner, config-validator, regression-guard in 04-agents (Items 2,3,6)"
```

STEP 5 — Send a message to the orchestrator:
```
AGENT: B3 (04-agents.md editor)
STATUS: DONE
FILE: .claude/workflow/04-agents.md
SUMMARY: Added sections 9, 10, 11 documenting smoke-test-runner, config-validator, and regression-guard. Each section follows existing format with scope, model, when-to-use, checks table, PASS/FAIL criteria, and example invocation. Updated Wave 3 agents table with 3 new rows. File committed successfully.
```
If anything failed, replace STATUS with FAILED and describe in SUMMARY.
---

## WAVE C AGENT PROMPT

### C1 — Summarizer

**Spawn as:** `subagent_type="general-purpose"`
**Pass this prompt exactly:**

---
You are the final summarizer for the /verify improvements implementation.

MetaProject path: /Users/bruno/sec-llm-workbench/

YOUR SINGLE TASK: Read the git log, verify all files are in place, write a final summary report, and send it to the orchestrator.

STEP 1 — Verify all files exist:
```bash
ls /Users/bruno/sec-llm-workbench/.claude/agents/smoke-test-runner.md
ls /Users/bruno/sec-llm-workbench/.claude/agents/config-validator.md
ls /Users/bruno/sec-llm-workbench/.claude/agents/regression-guard.md
ls /Users/bruno/sec-llm-workbench/.claude/agents/integration-tracer.md
ls /Users/bruno/sec-llm-workbench/.claude/skills/verify/SKILL.md
ls /Users/bruno/sec-llm-workbench/.claude/docs/verification-thresholds.md
ls /Users/bruno/sec-llm-workbench/.claude/workflow/04-agents.md
```

STEP 2 — Get git log of recent commits:
```bash
cd /Users/bruno/sec-llm-workbench && git log --oneline -10
```

STEP 3 — Write a final summary report to:
`.ignorar/production-reports/verify-improvements/2026-03-05-verify-improvements-final-summary.md`

Report format:
```markdown
# /verify Improvements — Final Implementation Summary
**Date:** 2026-03-05
**Implemented by:** TeamCreate agent team (Orchestrator + 8 worker agents)

## Items Implemented

| Item | Description | Status | File |
|------|-------------|--------|------|
| 1 | Active-project guard at /verify start | DONE | .claude/skills/verify/SKILL.md |
| 2 | smoke-test-runner agent | DONE | .claude/agents/smoke-test-runner.md |
| 3 | config-validator agent | DONE | .claude/agents/config-validator.md |
| 4 | AST-based call graph for integration-tracer | DONE | .claude/agents/integration-tracer.md |
| 5 | Wave 3 timeout and retry logic | DONE | .claude/skills/verify/SKILL.md |
| 6 | regression-guard agent | DONE | .claude/agents/regression-guard.md |

## Files Created
- .claude/agents/smoke-test-runner.md
- .claude/agents/config-validator.md
- .claude/agents/regression-guard.md

## Files Modified
- .claude/agents/integration-tracer.md (AST section added)
- .claude/skills/verify/SKILL.md (guard + timeout + 3 new agent wiring)
- .claude/docs/verification-thresholds.md (3 new agent entries)
- .claude/workflow/04-agents.md (3 new agent sections)

## Git Commits (last 8)
[paste output of git log --oneline -10 here]

## /verify Coverage After Implementation

| Check | Agent | Status |
|-------|-------|--------|
| Type hints, Pydantic v2, httpx | best-practices-enforcer | Active |
| OWASP, secrets, injection | security-auditor | Active |
| Library API hallucinations | hallucination-detector | Active |
| Code quality, complexity | code-reviewer | Active |
| Test coverage | test-generator | Active |
| Hollow endpoints, broken chains | integration-tracer (with AST) | Active |
| asyncio.run() in async contexts | async-safety-auditor | Active |
| No-op validators, swallowed exceptions | semantic-correctness-auditor | Active |
| Active-project guard | SKILL.md guard block | Active |
| End-to-end pipeline execution | smoke-test-runner | Active |
| Env var / docker config consistency | config-validator | Active |
| Cross-phase regression | regression-guard | Active |

## Result
All 6 items from the 2026-03-05 handoff have been implemented.
/verify now runs 11 agents across Wave 1, Wave 2, and Wave 3.
```

STEP 4 — Commit the summary report:
```bash
cd /Users/bruno/sec-llm-workbench
git add .ignorar/production-reports/verify-improvements/2026-03-05-verify-improvements-final-summary.md
git commit -m "docs: add verify improvements final implementation summary"
```

STEP 5 — Send a message to the orchestrator with this content:

```
AGENT: C1 (summarizer)
STATUS: DONE
FILE: .ignorar/production-reports/verify-improvements/2026-03-05-verify-improvements-final-summary.md

IMPLEMENTATION COMPLETE

All 6 items from the 2026-03-05 handoff have been implemented across 8 agents in 2 waves.

Files created (3):
- .claude/agents/smoke-test-runner.md
- .claude/agents/config-validator.md
- .claude/agents/regression-guard.md

Files modified (4):
- .claude/agents/integration-tracer.md (AST call graph section added)
- .claude/skills/verify/SKILL.md (guard + timeout + 3 new agents wired in)
- .claude/docs/verification-thresholds.md (sections 9, 10, 11 added)
- .claude/workflow/04-agents.md (sections 9, 10, 11 added)

Total git commits: 8
/verify now covers 11 agents total (was 8). Full coverage table in final summary report.
```
---

## FILE PATHS REFERENCE

All paths are relative to `/Users/bruno/sec-llm-workbench/` unless stated as absolute.

| File | Purpose | Wave |
|------|---------|------|
| `.claude/agents/smoke-test-runner.md` | New agent — create | A1 |
| `.claude/agents/config-validator.md` | New agent — create | A2 |
| `.claude/agents/regression-guard.md` | New agent — create | A3 |
| `.claude/agents/integration-tracer.md` | Existing agent — update | A4 |
| `.claude/skills/verify/SKILL.md` | Orchestration skill — 5 edits | B1 |
| `.claude/docs/verification-thresholds.md` | Thresholds — 3 new entries | B2 |
| `.claude/workflow/04-agents.md` | Agent docs — 3 new sections | B3 |
| `.ignorar/production-reports/verify-improvements/` | Final summary report | C1 |

---

## DEPENDENCY RULES

- Wave B MUST NOT start until ALL 4 Wave A agents have reported DONE
- Wave C MUST NOT start until ALL 3 Wave B agents have reported DONE
- If any Wave A agent reports FAILED: stop, do not start Wave B, report to user
- If any Wave B agent reports FAILED: stop, do not start Wave C, report to user

---

*End of briefing. The orchestrator reads this file and executes the plan as written.*
