---
name: verify
disable-model-invocation: true
description: "Executes mandatory 5-agent verification using batched TeamCreate architecture (context-safe, any codebase size)"
context: fork
agent: general-purpose
argument-hint: "[--fix] [--simple]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Task", "TeamCreate", "SendMessage"]
---

# /verify

Executes the mandatory 5-agent verification cycle and cleans pending markers.
Uses TeamCreate + Operator architecture by default (context-safe, any codebase size).

## Usage

```
/verify              # Batched mode (default — context-safe, any codebase size)
/verify --fix        # Auto-fix with ruff before launching agents
/verify --simple     # Simple wave mode (small codebases only — see Mode Selection)
```

---

## STEP 0: Project Discovery (do this before anything else)

```bash
TARGET=$(cat .build/active-project)
TARGET="${TARGET/#\~/$HOME}"
echo "$TARGET"
```

This gives you `{PROJECT_PATH}` — the absolute path to the active project.
All subsequent operations use this value. Never hardcode a project name.

Check pending files:

```bash
ls .build/checkpoints/pending/ 2>/dev/null || echo "none"
```

If no pending files: report "No pending files to verify" and stop.

---

## STEP 1: Mode Selection

**Default: Batched mode.** Use `--simple` only if ALL of the following are true:
- Fewer than 15 Python files in `{PROJECT_PATH}/src/`
- No file exceeds 200 lines
- User explicitly passed `--simple`

Otherwise: always use Batched mode.

---

## Mode 1: Batched (Default — TeamCreate + Operator)

### Core Principles

1. **Stateless batches** — each agent spawn handles exactly one batch. No agent carries state from a previous spawn. Filesystem is the only shared state.
2. **Filesystem as shared memory** — prompts are minimal pointers (manifest path + section header). File lists and large data live on disk, not in prompts.
3. **Incremental append** — each agent type has exactly one report file for the entire run. Every spawn of the same agent type appends its batch section. No merge step.
4. **Fixed timestamp** — the Operator computes `FIXED_TIMESTAMP` once at startup and embeds it in every manifest section. All spawns of the same agent write to the same filename.
5. **Sequential-per-agent, parallel-across-agents** — batches for a given agent type run one at a time (spawn → DONE → next spawn). Different agent types run in parallel with each other.
6. **Context preservation** — main session, Operator, and every verification agent must protect their context window. No large data embedded in prompts.
7. **No autonomous recovery** — if something goes wrong, the Operator asks the human. Never self-recovers.

### Main Session Role (YOU — the Claude instance reading this)

1. Read active project path (STEP 0 above)
2. Create the team: `TeamCreate`
3. Spawn the Operator agent with the prompt below — pass `{PROJECT_PATH}`
4. **Wait silently** — no check-ins, no file reads, no autonomous actions
5. Receive ONE compact verdict message from the Operator
6. Display the verdict verbatim to the human

You do NOT: read files, define batch manifests, spawn verification agents directly, or interpret agent idleness.

---

### Operator Prompt

```
You are the Operator for the /verify process in the project at {PROJECT_PATH}.

Your job: coordinate batched verification of all Python source and test files.

Meta-project rules — read ALL of these before doing anything else:
- ~/sec-llm-workbench/.claude/rules/verification-thresholds.md
- ~/sec-llm-workbench/.claude/workflow/04-agents.md
- ~/sec-llm-workbench/.claude/docs/errors-to-rules.md

Then execute in order:
1. Inspect {PROJECT_PATH}/src/ and {PROJECT_PATH}/tests/ — list all Python files, count lines per file
2. Compute FIXED_TIMESTAMP once: $(date +%Y-%m-%d-%H%M%S)
3. Define batch assignments for all 5 agents (see batch sizing rules below)
4. Write the batch manifest to:
   {PROJECT_PATH}/.ignorar/production-reports/batch-manifest.md
   (First line of manifest: FIXED_TIMESTAMP: {value})
5. Confirm these report directories exist — create if missing:
   {PROJECT_PATH}/.ignorar/production-reports/best-practices-enforcer/current/
   {PROJECT_PATH}/.ignorar/production-reports/security-auditor/current/
   {PROJECT_PATH}/.ignorar/production-reports/hallucination-detector/current/
   {PROJECT_PATH}/.ignorar/production-reports/code-reviewer/current/
   {PROJECT_PATH}/.ignorar/production-reports/test-generator/current/
   {PROJECT_PATH}/.ignorar/production-reports/static-checks/current/
6. Spawn Wave 1 agents — first batch of each type in parallel (across types)
7. As each agent reports DONE: spawn next batch for that agent type only
8. When all Wave 1 types finish all batches → spawn Wave 2 (same pattern)
9. When all Wave 2 types finish all batches → spawn Static Checks Agent
10. When static checks report file exists → spawn Final Report Agent
11. Receive compact verdict from Final Report Agent → relay verbatim to main session → shut down

Batch sizing rules:
| Agent                   | Context Risk | Batch Size         | Grouping                        |
|-------------------------|--------------|--------------------|----------------------------------|
| best-practices-enforcer | Low          | 4–5 files          | By module directory              |
| security-auditor        | Medium       | 3–4 files          | By module directory              |
| hallucination-detector  | High         | By library         | httpx / pydantic / structlog / etc. |
| code-reviewer           | Medium       | 3–4 files          | By module directory              |
| test-generator          | Highest      | 1 module per batch | pytest scoped to that module only |

Model assignments (Opus is explicitly forbidden — no exceptions):
| Role                    | Model  | Rationale                              |
|-------------------------|--------|----------------------------------------|
| You (Operator)          | Sonnet | Reads files, reasons, coordinates      |
| best-practices-enforcer | Haiku  | Mechanical grep pattern detection      |
| security-auditor        | Haiku  | Mechanical grep + bandit               |
| hallucination-detector  | Sonnet | Context7 queries + reasoning required  |
| code-reviewer           | Sonnet | Quality scoring + reasoning required   |
| test-generator          | Haiku  | Run pytest + read coverage output      |
| Static Checks Agent     | Haiku  | 4 bash commands — pure mechanical      |
| Final Report Agent      | Haiku  | grep summary + threshold lookup        |

Operator rules — no exceptions:
- Do NOT embed file lists or large data in agent prompts (use manifest sections)
- Do NOT read report files or batch sections into your own context
- Do NOT spawn next batch before previous batch reports DONE
- Do NOT make autonomous decisions when something goes wrong — ask the human
- Confirm file existence with ls — never reading content
- If anything goes wrong: report to human what was expected, what was observed, no fix
```

---

### Batch Manifest Format

Written by Operator to `{PROJECT_PATH}/.ignorar/production-reports/batch-manifest.md`
before any agent is spawned.

**First line:**
```
FIXED_TIMESTAMP: 2026-02-23-143022
```

**Each section:**
```markdown
## [{agent-name}] [batch-{N}-of-{T}]

**Files to analyze:**
- /absolute/path/to/file1.py
- /absolute/path/to/file2.py

**Append findings to:**
{PROJECT_PATH}/.ignorar/production-reports/{agent-name}/current/{FIXED_TIMESTAMP}-{agent-name}.md

**IS_LAST_BATCH:** false
```

Last batch for each agent type has `IS_LAST_BATCH: true`.

---

### Agent Prompt Template (each batch spawn)

```
You are {agent-name} for the project at {PROJECT_PATH} — verification run.

YOUR SCOPE: BATCH {B} of {T} ({batch-description}).

Rules to follow:
- ~/sec-llm-workbench/.claude/rules/verification-thresholds.md
- ~/sec-llm-workbench/.claude/workflow/04-agents.md

Batch manifest:
{PROJECT_PATH}/.ignorar/production-reports/batch-manifest.md

Read ONLY the section with this exact header:
## [{agent-name}] [batch-{B}-of-{T}]
Ignore all other sections.

That section contains: files to analyze, shared report path, IS_LAST_BATCH flag.

When done:
1. If report file does not exist: create it with document header first (see append mechanism below)
2. Append your batch section (## Batch {B} of {T}) using bash >> append
3. If IS_LAST_BATCH is true: also append ## Summary (All Batches) section
4. Send operator: "DONE: {agent-name} batch {B} of {T} — appended to {path}"
5. Wait for shutdown — take no further action.

DO NOT analyze files outside your manifest section.
DO NOT overwrite the report file — always append (>>).
DO NOT read other agents' report files.
```

---

### Report File Structure (Incremental Append)

**Path pattern:**
```
{PROJECT_PATH}/.ignorar/production-reports/{agent-name}/current/{FIXED_TIMESTAMP}-{agent-name}.md
```

**Append mechanism each batch spawn executes:**
```bash
# Create header only if file does not exist yet
[ -f {report_path} ] || cat > {report_path} << 'HEADER'
# {agent-name} — Verification Report
Generated: {FIXED_TIMESTAMP}
Project: {PROJECT_PATH}
---
HEADER

# Every batch (including first): append batch section
cat >> {report_path} << 'BATCH'
## Batch {B} of {T} — {description}

**Files analyzed:**
- /path/file1.py
- /path/file2.py

### Findings

[findings here]

### Batch {B} Status: PASS / FAIL

---
BATCH

# Last batch only: also append Summary section
cat >> {report_path} << 'SUMMARY'
## Summary (All Batches)

| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |

**Threshold applied:** [from verification-thresholds.md]
**Overall Status: PASS / FAIL**
SUMMARY
```

---

### Static Checks Agent Prompt

```
You are the Static Checks Agent for the project at {PROJECT_PATH}.

Run these 4 commands (cd to project first):
  cd {PROJECT_PATH}
  uv run ruff format src tests --check
  uv run ruff check src tests
  uv run mypy src
  uv run pytest tests/ -v

Save all stdout, stderr, and exit codes to:
{PROJECT_PATH}/.ignorar/production-reports/static-checks/current/{FIXED_TIMESTAMP}-static-checks.md

Then send operator: "DONE: static checks — report saved to {path}"
Shut down after sending.
```

---

### Final Report Agent Prompt

```
You are the Final Report Agent.

Your ONLY job:
1. Read FIXED_TIMESTAMP from the first line of:
   {PROJECT_PATH}/.ignorar/production-reports/batch-manifest.md

2. Extract ONLY the ## Summary section of each agent report using bash:
   grep -A 30 "## Summary" {report_path}

3. Read the full static checks report (it is small — stdout of 4 commands).

4. Apply thresholds from:
   ~/sec-llm-workbench/.claude/rules/verification-thresholds.md

5. Compose the compact verdict (≤ 30 lines) using the Verdict Format below.

6. Send verdict as a MESSAGE to the operator (SendMessage — do NOT print it, SEND it).

7. Shut down immediately after sending.

Do NOT write any file. Do NOT read full report files. Do NOT read other sections.
```

### Verdict Format (sent as message — never written to a file)

```
VERIFICATION — FINAL VERDICT

Agent Results:
| Agent                    | Status | Notes                  |
|--------------------------|--------|------------------------|
| best-practices-enforcer  | PASS   | 0 violations           |
| security-auditor         | PASS   | 0 CRITICAL/HIGH        |
| hallucination-detector   | PASS   | 0 hallucinations       |
| code-reviewer            | PASS   | Score: 9.2/10          |
| test-generator           | PASS   | Coverage: 84%          |

Static Checks:
| Check       | Status |
|-------------|--------|
| ruff format | PASS   |
| ruff check  | PASS   |
| mypy        | PASS   |
| pytest      | PASS   |

OVERALL: PASS ✓   (or FAIL — list which agents/checks failed)

Report files:
- {PROJECT_PATH}/.ignorar/production-reports/best-practices-enforcer/current/{FIXED_TIMESTAMP}-best-practices-enforcer.md
- {PROJECT_PATH}/.ignorar/production-reports/security-auditor/current/{FIXED_TIMESTAMP}-security-auditor.md
- {PROJECT_PATH}/.ignorar/production-reports/hallucination-detector/current/{FIXED_TIMESTAMP}-hallucination-detector.md
- {PROJECT_PATH}/.ignorar/production-reports/code-reviewer/current/{FIXED_TIMESTAMP}-code-reviewer.md
- {PROJECT_PATH}/.ignorar/production-reports/test-generator/current/{FIXED_TIMESTAMP}-test-generator.md
- {PROJECT_PATH}/.ignorar/production-reports/static-checks/current/{FIXED_TIMESTAMP}-static-checks.md
```

---

## Mode 2: Simple Waves (--simple flag only)

Only use when `--simple` is explicitly passed AND fewer than 15 Python files AND no file > 200 lines.
No TeamCreate. Main session spawns agents directly in 2 waves.

### Step 1: Pending Files

```bash
ls .build/checkpoints/pending/ 2>/dev/null
```

### Wave 1 (Parallel — ~7 min max)

Submit 3 agents simultaneously:

**best-practices-enforcer:**
```
Task(subagent_type="best-practices-enforcer", model="haiku", prompt="""
Verify Python files in {PROJECT_PATH}: type hints, Pydantic v2, httpx, structlog, pathlib.

EXPECTED OUTPUT STRUCTURE:
## Findings
### 1. [Title]
- **File:** src/module/file.py:42
- **Severity:** MEDIUM
- **Pattern:** [description]
- **Fix:** [how to fix]

## Summary
- Total violations: N
- CRITICAL: 0 / MEDIUM: N / LOW: N

Save report to: {PROJECT_PATH}/.ignorar/production-reports/best-practices-enforcer/current/{TIMESTAMP}-best-practices-enforcer.md
""")
```

**security-auditor:**
```
Task(subagent_type="security-auditor", model="haiku", prompt="""
Audit security in {PROJECT_PATH}: OWASP Top 10, secrets, injection, LLM security.

EXPECTED OUTPUT STRUCTURE:
## Security Findings
### 1. [Vulnerability Title]
- **File:** src/module/file.py:34
- **CWE:** CWE-89
- **Severity:** CRITICAL
- **Fix:** [parameterized queries / env var / etc.]
- **OWASP:** A03:2021

## Summary
- Total: N / CRITICAL: N / HIGH: N / MEDIUM: N

Save report to: {PROJECT_PATH}/.ignorar/production-reports/security-auditor/current/{TIMESTAMP}-security-auditor.md
""")
```

**hallucination-detector:**
```
Task(subagent_type="hallucination-detector", model="sonnet", prompt="""
Verify library syntax in {PROJECT_PATH} against Context7 MCP.

EXPECTED OUTPUT STRUCTURE:
## Hallucination Check Results
### ✅ VERIFIED USAGE
#### 1. httpx AsyncClient
- **Pattern:** httpx.AsyncClient(timeout=30.0)
- **File:** src/api/client.py:15
- **Context7 Status:** VERIFIED

### ⚠️ HALLUCINATED USAGE
#### 1. [Method name]
- **Pattern:** [what the code does]
- **Status:** UNVERIFIED — not in docs
- **Recommendation:** [correct usage]

## Summary
- Total checked: N / VERIFIED: N / HALLUCINATED: N

Save report to: {PROJECT_PATH}/.ignorar/production-reports/hallucination-detector/current/{TIMESTAMP}-hallucination-detector.md
""")
```

Wait for all 3 to complete.

### Wave 2 (Parallel — ~5 min max)

**code-reviewer:**
```
Task(subagent_type="code-reviewer", model="sonnet", prompt="""
Review code quality in {PROJECT_PATH}: complexity, DRY, naming, maintainability.
Score out of 10. Threshold: ≥ 9.0/10 to pass.

Save report to: {PROJECT_PATH}/.ignorar/production-reports/code-reviewer/current/{TIMESTAMP}-code-reviewer.md
""")
```

**test-generator:**
```
Task(subagent_type="test-generator", model="haiku", prompt="""
Analyze test coverage in {PROJECT_PATH}. Generate missing tests. Threshold: ≥ 80%.

Save report to: {PROJECT_PATH}/.ignorar/production-reports/test-generator/current/{TIMESTAMP}-test-generator.md
""")
```

Wait for both to complete.

### Static Checks (after Wave 2)

```bash
cd {PROJECT_PATH}
uv run ruff format src tests --check
uv run ruff check src tests
uv run mypy src
uv run pytest tests/ -v
```

### If --fix was passed

Run before launching agents:
```bash
cd {PROJECT_PATH}
uv run ruff format src tests
uv run ruff check src tests --fix
```

---

## After All Agents Pass: Clean Markers

```bash
rm -rf .build/checkpoints/pending/*
```

## Agent Logging (both modes — mandatory)

After each agent completes, append to `.build/logs/agents/YYYY-MM-DD.jsonl`:

```json
{
  "id": "<uuid>",
  "timestamp": "<ISO8601>",
  "session_id": "<session_id>",
  "agent": "<agent_name>",
  "files": ["<file1>", "<file2>"],
  "status": "PASSED|FAILED",
  "findings": [],
  "duration_ms": 0
}
```

## Marker System

- `post-code.sh` creates markers in `.build/checkpoints/pending/` after Write/Edit on `.py` files
- `pre-git-commit.sh` blocks commit if pending markers exist
- `/verify` runs agents and cleans markers if all pass

## Verification Thresholds Reference

See: `~/sec-llm-workbench/.claude/rules/verification-thresholds.md`

| Agent                   | PASS                        | FAIL                    | Blocking |
|-------------------------|-----------------------------|-------------------------|----------|
| best-practices-enforcer | 0 violations                | Any violation           | Yes      |
| security-auditor        | 0 CRITICAL/HIGH             | Any CRITICAL/HIGH       | Yes      |
| hallucination-detector  | 0 hallucinations            | Any hallucination       | Yes      |
| code-reviewer           | Score ≥ 9.0/10              | Score < 9.0/10          | Yes      |
| test-generator          | All pass + coverage ≥ 80%   | Any fail OR cov < 80%   | Yes      |
| ruff check              | 0 errors, 0 warnings        | Any error or warning    | Yes      |
| ruff format             | No changes needed           | Changes required        | Yes      |
| mypy                    | 0 errors                    | Any error               | Yes      |
