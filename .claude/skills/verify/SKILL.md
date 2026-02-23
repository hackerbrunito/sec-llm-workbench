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
6. **Two-tier summarization** — batch agents write findings only. After all batches for an agent type complete, a dedicated report-summarizer reads the full report and produces a compact summary (20-30 lines). The final-report-agent reads only the 5 compact summaries — never full reports.
7. **Context preservation** — main session, Operator, and every verification agent must protect their context window. No large data embedded in prompts.
8. **No autonomous recovery** — if something goes wrong, the Operator asks the human. Never self-recovers.

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
   (First line: FIXED_TIMESTAMP: {value})
5. Confirm these directories exist — create if missing:
   {PROJECT_PATH}/.ignorar/production-reports/best-practices-enforcer/current/
   {PROJECT_PATH}/.ignorar/production-reports/security-auditor/current/
   {PROJECT_PATH}/.ignorar/production-reports/hallucination-detector/current/
   {PROJECT_PATH}/.ignorar/production-reports/code-reviewer/current/
   {PROJECT_PATH}/.ignorar/production-reports/test-generator/current/
   {PROJECT_PATH}/.ignorar/production-reports/static-checks/current/
6. Spawn Wave 1 agents — first batch of each type in parallel (across types)
7. As each batch reports DONE: spawn the next batch for that agent type
8. As each Wave 1 agent TYPE completes ALL its batches:
   → immediately spawn report-summarizer for that type (do not wait for other types)
9. When ALL Wave 1 types have finished all batches → spawn Wave 2 (same pattern)
10. As each Wave 2 agent TYPE completes ALL its batches:
    → immediately spawn report-summarizer for that type
    → when ALL Wave 2 types have finished all batches → also spawn Static Checks Agent
11. Wait for ALL 5 report-summarizers AND Static Checks Agent to report DONE
12. Spawn Final Report Agent
13. Receive compact verdict from Final Report Agent → relay verbatim to main session → shut down

Batch sizing rules:
| Agent                   | Context Risk | Batch Size         | Grouping                            |
|-------------------------|--------------|--------------------|--------------------------------------|
| best-practices-enforcer | Low          | 4–5 files          | By module directory                  |
| security-auditor        | Medium       | 3–4 files          | By module directory                  |
| hallucination-detector  | High         | By library         | httpx / pydantic / structlog / etc.  |
| code-reviewer           | Medium       | 3–4 files          | By module directory                  |
| test-generator          | Highest      | 1 module per batch | pytest scoped to that module only    |

Model assignments (Opus is explicitly forbidden — no exceptions):
| Role                    | Model  | Rationale                              |
|-------------------------|--------|----------------------------------------|
| You (Operator)          | Sonnet | Reads files, reasons, coordinates      |
| best-practices-enforcer | Haiku  | Mechanical grep pattern detection      |
| security-auditor        | Haiku  | Mechanical grep + bandit               |
| hallucination-detector  | Sonnet | Context7 queries + reasoning required  |
| code-reviewer           | Sonnet | Quality scoring + reasoning required   |
| test-generator          | Haiku  | Run pytest + read coverage output      |
| report-summarizer       | Haiku  | Read one report, distill findings      |
| static-checks-agent     | Haiku  | 4 bash commands — pure mechanical      |
| final-report-agent      | Haiku  | Read 5 compact summaries, send verdict |

Operator rules — no exceptions:
- Do NOT embed file lists or large data in agent prompts (use manifest sections)
- Do NOT read report files or batch sections into your own context
- Do NOT spawn next batch before previous batch reports DONE
- Do NOT spawn report-summarizer before all batches for that type report DONE
- Do NOT spawn final-report-agent before all 5 summaries and static checks report DONE
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
```

No `IS_LAST_BATCH` field — the report-summarizer handles the summary after all batches complete.

---

### Batch Agent Prompt Template

```
You are {agent-name} for the project at {PROJECT_PATH} — verification run.

YOUR SCOPE: BATCH {B} of {T} ({batch-description}). Analyze ONLY the files in your batch.

Rules to follow:
- ~/sec-llm-workbench/.claude/rules/verification-thresholds.md
- ~/sec-llm-workbench/.claude/workflow/04-agents.md

Batch manifest:
{PROJECT_PATH}/.ignorar/production-reports/batch-manifest.md

Read ONLY the section with this exact header:
## [{agent-name}] [batch-{B}-of-{T}]
Ignore all other sections.

That section contains: the files to analyze and the shared report path to append to.

When done:
1. If the report file does not exist yet: create it with the document header (see append
   mechanism below)
2. Append your batch section using bash >> (see append mechanism below)
3. End your batch section with the line: ### Batch {B} Status: PASS / FAIL
4. Send operator: "DONE: {agent-name} batch {B} of {T} — appended to {path}"
5. Wait for shutdown. Take no further action.

⚠️ CRITICAL — append rules:
- Use ONLY bash >> to write to the report file. NEVER use the Write tool on this file.
- NEVER overwrite the report file. Always append (>>).
- Do NOT analyze files outside your manifest section.
- Do NOT read other agents' report files.
```

---

### Append Mechanism (batch agents execute this)

```bash
# Create header only if file does not exist
[ -f {report_path} ] || cat > {report_path} << 'HEADER'
# {agent-name} — Verification Report
Generated: {FIXED_TIMESTAMP}
Project: {PROJECT_PATH}
---
HEADER

# Append this batch's section
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
```

---

### Report-Summarizer Prompt (spawned once per agent type, after all its batches complete)

```
You are the report-summarizer for {agent-name}.

Read the full report at:
{PROJECT_PATH}/.ignorar/production-reports/{agent-name}/current/{FIXED_TIMESTAMP}-{agent-name}.md

Read the thresholds from:
~/sec-llm-workbench/.claude/rules/verification-thresholds.md

Produce a compact summary (20-30 lines) and write it to:
{PROJECT_PATH}/.ignorar/production-reports/{agent-name}/current/{FIXED_TIMESTAMP}-{agent-name}-summary.md

Summary format:
# {agent-name} — Compact Summary
Generated: {FIXED_TIMESTAMP}

## Batch Results
| Batch   | Status |
|---------|--------|
| Batch 1 | PASS   |
(one row per batch)

## Findings Count
| Severity | Count |
|----------|-------|
| CRITICAL | N     |
| HIGH     | N     |
| MEDIUM   | N     |
| LOW      | N     |

## Blocking Issues (CRITICAL / HIGH only — max 5)
- file:line — description
(or "None" if all clear)

## Overall Status: PASS / FAIL
Threshold applied: [from verification-thresholds.md]

When done:
1. Write the compact summary to the path above
2. Send operator: "DONE: {agent-name} summary — Overall: PASS/FAIL — saved to {path}"
3. Shut down.
```

---

### Static Checks Agent Prompt (spawned after all Wave 2 batches complete)

```
You are the static-checks-agent for the project at {PROJECT_PATH}.

Run 4 checks and save all output (stdout + stderr + exit codes) to:
{PROJECT_PATH}/.ignorar/production-reports/static-checks/current/{FIXED_TIMESTAMP}-static-checks.md

Use bash redirection only — do not use Write tool.

Commands to run:
  cd {PROJECT_PATH}
  uv run ruff format src tests --check
  uv run ruff check src tests
  uv run mypy src
  uv run pytest tests/ -v

After saving: send operator "DONE: static checks — report saved to {path}"
Shut down after sending.
```

---

### Final Report Agent Prompt (spawned after all 5 summaries + static checks complete)

```
You are the final-report-agent.

Read these 5 compact summary files (20-30 lines each):
- {PROJECT_PATH}/.ignorar/production-reports/best-practices-enforcer/current/{FIXED_TIMESTAMP}-best-practices-enforcer-summary.md
- {PROJECT_PATH}/.ignorar/production-reports/security-auditor/current/{FIXED_TIMESTAMP}-security-auditor-summary.md
- {PROJECT_PATH}/.ignorar/production-reports/hallucination-detector/current/{FIXED_TIMESTAMP}-hallucination-detector-summary.md
- {PROJECT_PATH}/.ignorar/production-reports/code-reviewer/current/{FIXED_TIMESTAMP}-code-reviewer-summary.md
- {PROJECT_PATH}/.ignorar/production-reports/test-generator/current/{FIXED_TIMESTAMP}-test-generator-summary.md

Read the static checks report:
- {PROJECT_PATH}/.ignorar/production-reports/static-checks/current/{FIXED_TIMESTAMP}-static-checks.md

Read thresholds from:
- ~/sec-llm-workbench/.claude/rules/verification-thresholds.md

Compose the compact verdict (≤ 30 lines) using the format below.
Send it as a SendMessage to the operator. Do NOT print it — SEND it.
Write no files. Shut down immediately after sending.
```

### Verdict Format (sent as message — never written to file)

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

Full reports: {PROJECT_PATH}/.ignorar/production-reports/
```

---

### Architecture Flow

```
Main session
│  TeamCreate → spawns Operator → waits silently
│  Receives ONE verdict message → displays to human. Reads zero files.
│
Operator
│  1. Reads rules + project files
│  2. Computes FIXED_TIMESTAMP, writes batch manifest
│  3. Spawns Wave 1 (parallel across types, sequential within)
│  4. As each Wave 1 type finishes all batches → spawns its report-summarizer
│  5. Spawns Wave 2 (same pattern as Wave 1)
│  6. As each Wave 2 type finishes all batches → spawns its report-summarizer
│  7. After all Wave 2 batches done → spawns Static Checks Agent
│  8. Waits for all 5 summaries + Static Checks to report DONE
│  9. Spawns Final Report Agent
│ 10. Receives verdict → relays to main session → shuts down
│
├── WAVE 1 (batch agents — sequential per type, parallel across types)
│   ├── best-practices-enforcer  batch-1→DONE→batch-2→DONE → [report-summarizer BPE]
│   ├── security-auditor         batch-1→DONE→batch-2→DONE → [report-summarizer SA]
│   └── hallucination-detector   batch-httpx→DONE→batch-pydantic→DONE → [report-summarizer HD]
│
├── WAVE 2 (same pattern)
│   ├── code-reviewer    batch-1→DONE→batch-2→DONE → [report-summarizer CR]
│   └── test-generator   batch-mod1→DONE→batch-mod2→DONE → [report-summarizer TG]
│
├── REPORT SUMMARIZERS (5 total — Haiku — run as soon as their type finishes)
│   Each reads ONE full report → writes ONE compact summary (20-30 lines)
│
├── STATIC CHECKS AGENT (Haiku — after all Wave 2 batches done)
│   Runs 4 bash commands → saves output via bash redirection
│
└── FINAL REPORT AGENT (Haiku — after all 5 summaries + static checks done)
        Reads 5 compact summaries (~150 lines total) + static checks report
        Applies thresholds → composes verdict → sends as message → shuts down

Context used by main session: ONE message. Zero file reads.
Context used by Final Report Agent: ~150-230 lines total. No overflow risk.
```

---

## Mode 2: Simple Waves (--simple flag only)

Use only when `--simple` is explicitly passed AND fewer than 15 Python files AND no file > 200 lines.
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
- Total violations: N / CRITICAL: 0 / MEDIUM: N / LOW: N

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
- **CWE:** CWE-89 / **Severity:** CRITICAL
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
### ✅ VERIFIED: httpx.AsyncClient(timeout=30.0) — src/api/client.py:15
### ⚠️ HALLUCINATED: [pattern] — [file:line] — Recommendation: [correct usage]

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
Analyze test coverage in {PROJECT_PATH}. Threshold: ≥ 80%.

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
  "agent": "<agent_name>",
  "status": "PASSED|FAILED",
  "duration_ms": 0
}
```

## Marker System

- `post-code.sh` creates markers in `.build/checkpoints/pending/` after Write/Edit on `.py` files
- `pre-git-commit.sh` blocks commit if pending markers exist
- `/verify` runs agents and cleans markers if all pass

## Verification Thresholds Reference

Full definitions: `~/sec-llm-workbench/.claude/rules/verification-thresholds.md`

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
