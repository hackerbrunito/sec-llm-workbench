> **OBSOLETE — FULLY IMPLEMENTED 2026-03-05:** All 6 items in this handoff have been implemented and committed to main by a TeamCreate agent team. This file is superseded by `.ignorar/production-reports/verify-improvements/2026-03-05-verify-improvements-final-summary.md`.

# Handoff: /verify Command Improvements

**Date:** 2026-03-05
**Session context:** Audit of the /verify command revealed critical gaps. Gaps 1-3 were fixed in this session. Items 1-6 below are pending improvements for the next session.

---

## What Was Fixed in This Session

### Fixed 1: Wave 3 agent files created (CRITICAL)
Three agent definition files were missing — Claude Code was falling back to general-purpose agents with no instructions.
- Created: `.claude/agents/integration-tracer.md`
- Created: `.claude/agents/async-safety-auditor.md`
- Created: `.claude/agents/semantic-correctness-auditor.md`

### Fixed 2: Pending marker path mismatch (CRITICAL)
`post-code.sh` writes markers to `~/siopv/.build/checkpoints/pending/` but `/verify` and `pre-git-commit.sh` were checking `~/sec-llm-workbench/.build/checkpoints/pending/` (always empty). Result: `/verify` always reported "no pending files" and skipped all agents.
- Fixed: `.claude/hooks/pre-git-commit.sh` — now reads `.build/active-project` to find target project
- Fixed: `.claude/skills/verify/SKILL.md` — Step 1 (identify pending) and Step 4 (cleanup) now use active project path

### Fixed 3: Undefined `{slug}` placeholder in Wave 3 prompts (HIGH)
Replaced with fixed descriptive values in `SKILL.md`:
- `integration-tracer` → `full-trace`
- `async-safety-auditor` → `async-audit`
- `semantic-correctness-auditor` → `semantic-scan`

---

## Pending Improvements (6 items — implement in next session)

### Item 1 — Active-project guard at /verify start (HIGH priority, easy)

**Problem:** If `.build/active-project` is missing, empty, or points to a non-existent path, `/verify` silently falls back to the meta-project's pending dir (always empty) and skips all 8 agents with no warning.

**Fix needed:** Add a validation block at the very start of SKILL.md Step 1:
```bash
TARGET=$(cat .build/active-project 2>/dev/null || echo "")
TARGET="${TARGET/#\~/$HOME}"
if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
    echo "ERROR: .build/active-project is missing or invalid: '$TARGET'"
    echo "Set it with: echo '~/yourproject/' > .build/active-project"
    exit 1
fi
if [ ! -f "$TARGET/pyproject.toml" ]; then
    echo "ERROR: Target project has no pyproject.toml: $TARGET"
    exit 1
fi
```

**Files to modify:** `.claude/skills/verify/SKILL.md`

---

### Item 2 — Smoke-test-runner agent (HIGH priority, medium effort)

**Problem:** All 8 agents do static analysis only. None of them actually execute the program. A project can pass all 8 agents and still fail at runtime.

**Fix needed:** Create `.claude/agents/smoke-test-runner.md`

**What it does:**
1. Reads `.build/active-project` to find the target project
2. Starts the pipeline with a known synthetic CVE input (e.g., `CVE-2024-1234`)
3. Verifies the pipeline reaches the END node without crashing
4. Verifies the output contains expected fields (e.g., `classification`, `severity`, `cve_id`)
5. Reports PASS if output is valid, FAIL if crash or missing fields

**Wave assignment:** Wave 3 (parallel with existing Wave 3 agents) or a new Wave 4

**Files to create:** `.claude/agents/smoke-test-runner.md`
**Files to modify:** `.claude/skills/verify/SKILL.md` (add smoke-test-runner to Wave 3 or Wave 4)
**Files to modify:** `.claude/docs/verification-thresholds.md` (add smoke-test-runner thresholds)
**Files to modify:** `.claude/workflow/04-agents.md` (document the new agent)

**PASS criteria:** Pipeline runs end-to-end without exception, output dict contains required keys
**FAIL criteria:** Any unhandled exception, missing required output fields, or timeout

---

### Item 3 — Config/env validator agent (MEDIUM priority, medium effort)

**Problem:** No agent checks whether the project's required environment variables are all documented in `.env.example`, or whether `docker-compose.yml` service names/ports match what the code expects.

**Fix needed:** Create `.claude/agents/config-validator.md`

**What it does:**
1. Greps all `settings.*` and `os.getenv(` references in `src/` to build a list of required env vars
2. Reads `.env.example` and extracts all documented vars
3. Flags any required var not present in `.env.example`
4. Reads `docker-compose.yml` service names and ports
5. Greps the codebase for references to those service names (e.g., `openfga`, `keycloak`) and verifies they match
6. Checks that all `Settings` fields with no default have a corresponding entry in `.env.example`

**Wave assignment:** Wave 3 (parallel with existing Wave 3 agents)

**Files to create:** `.claude/agents/config-validator.md`
**Files to modify:** `.claude/skills/verify/SKILL.md`
**Files to modify:** `.claude/docs/verification-thresholds.md`
**Files to modify:** `.claude/workflow/04-agents.md`

**PASS criteria:** All required env vars documented, all docker service references consistent
**FAIL criteria:** Any undocumented required env var, any mismatched service name

---

### Item 4 — AST-based call graph for integration-tracer (MEDIUM priority, hard effort)

**Problem:** The current `integration-tracer` agent uses grep + read to trace call chains. This is imprecise — it can miss parameter dropping that occurs 2-3 function hops deep, and it cannot reliably distinguish function calls from string literals or comments.

**Fix needed:** Update `.claude/agents/integration-tracer.md` to instruct the agent to use Python's `ast` module or the `pyan3` tool for actual call graph construction.

**Approach:**
```bash
# Install pyan3 in the target project
cd "$TARGET" && uv add --dev pyan3
# Generate call graph
uv run pyan3 src/**/*.py --dot --no-defines > /tmp/callgraph.dot
```
Then parse the dot output to find unreachable nodes and broken chains.

**Alternative (no new dependency):** Write a small Python script that uses `ast.parse()` to extract function definitions and their `ast.Call` nodes, building a call graph in pure Python. Save this script to `.claude/scripts/build-call-graph.py`.

**Files to modify:** `.claude/agents/integration-tracer.md`
**Files to create (optional):** `.claude/scripts/build-call-graph.py`

---

### Item 5 — Wave 3 timeout and retry logic (LOW priority, easy)

**Problem:** If a Wave 3 agent hangs (e.g., Context7 times out, agent enters a loop) or returns garbage output (no "PASS"/"FAIL" in report), the orchestrator has no instruction to retry or mark it as failed-to-execute.

**Fix needed:** Add to SKILL.md Wave 3 section:
```
If a Wave 3 agent does not produce a report file within 10 minutes:
1. Mark that agent as TIMEOUT-FAIL
2. Continue with remaining Wave 3 agents
3. Report TIMEOUT-FAIL in the final verdict — do not silently skip
4. Retry once after Wave 3 completes if time permits
```

Also add validation after each Wave 3 agent completes:
- Verify the report file was actually created at the expected path
- If not: mark as FAIL with reason "report file not found"

**Files to modify:** `.claude/skills/verify/SKILL.md`

---

### Item 6 — Cross-phase regression check (MEDIUM priority, medium effort)

**Problem:** When verifying Phase 7 code, no agent checks whether changes to shared modules (state, DI, graph topology, constants) accidentally broke behavior that was verified in Phases 1-6. Each `/verify` run is isolated to files marked as pending.

**Fix needed:** Create `.claude/agents/regression-guard.md`

**What it does:**
1. Reads `.build/active-project` to find the target project
2. Runs `git diff HEAD~1 --name-only` to find all recently changed files
3. For each changed file, identifies which other modules import it (reverse dependency map)
4. Runs the full pytest suite on those reverse-dependent modules
5. Flags any test that was previously passing and is now failing

**Wave assignment:** Wave 2 (after code-reviewer, before Wave 3) or parallel with Wave 3

**Files to create:** `.claude/agents/regression-guard.md`
**Files to modify:** `.claude/skills/verify/SKILL.md`
**Files to modify:** `.claude/docs/verification-thresholds.md`
**Files to modify:** `.claude/workflow/04-agents.md`

**PASS criteria:** All previously-passing tests in reverse-dependent modules still pass
**FAIL criteria:** Any previously-passing test now fails after recent changes

---

## Current /verify Coverage After This Session's Fixes

| Check | Covered by | Status |
|-------|-----------|--------|
| Type hints, Pydantic v2, httpx | best-practices-enforcer | ✅ Working |
| OWASP, secrets, injection | security-auditor | ✅ Working |
| Library API hallucinations | hallucination-detector | ✅ Working |
| Code quality, complexity | code-reviewer | ✅ Working |
| Test coverage | test-generator | ✅ Working |
| Hollow endpoints, broken chains | integration-tracer | ✅ Fixed (agent file created) |
| asyncio.run() in async contexts | async-safety-auditor | ✅ Fixed (agent file created) |
| No-op validators, swallowed exceptions | semantic-correctness-auditor | ✅ Fixed (agent file created) |
| Active project guard | — | ❌ Not yet (Item 1) |
| End-to-end pipeline execution | — | ❌ Not yet (Item 2) |
| Env var / docker config consistency | — | ❌ Not yet (Item 3) |
| AST-based call graph | — | ❌ Not yet (Item 4) |
| Wave 3 timeout/retry | — | ❌ Not yet (Item 5) |
| Cross-phase regression | — | ❌ Not yet (Item 6) |

---

## Files Modified in This Session

```
.claude/agents/integration-tracer.md          — CREATED
.claude/agents/async-safety-auditor.md        — CREATED
.claude/agents/semantic-correctness-auditor.md — CREATED
.claude/hooks/pre-git-commit.sh               — MODIFIED (pending dir path fix)
.claude/skills/verify/SKILL.md                — MODIFIED (pending dir path fix + slug fix)
```
