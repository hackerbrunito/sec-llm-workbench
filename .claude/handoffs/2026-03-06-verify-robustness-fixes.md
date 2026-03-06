# Handoff: /verify System Robustness Fixes
**Date:** 2026-03-06
**Priority:** HIGH — all items must be fixed before next SIOPV phase
**Produced by:** Robustness audit (previous session, score: 71/100)
**Target score after fixes:** 85+/100

---

## FIRST ACTION REQUIRED (before touching any file)

**Go online and check Claude Code best practices.** The audit was done from memory (training data). Claude Code has had significant updates. Before fixing anything:

1. Use WebFetch to check: `https://docs.anthropic.com/en/docs/claude-code/settings`
2. Use WebFetch to check: `https://docs.anthropic.com/en/docs/claude-code/hooks`
3. Use WebFetch to check: `https://docs.anthropic.com/en/docs/claude-code/slash-commands`
4. Use WebFetch to check: `https://docs.anthropic.com/en/docs/claude-code/agents` (sub-agents / Task tool)
5. Use WebFetch on the Claude Code changelog or release notes if available

Then compare what you find online against what exists in the meta-project files and update the fix plan accordingly. Some of the "gaps" may already be correct for the current Claude Code version, or there may be NEW best practices we haven't adopted yet.

After online research, proceed with the fixes below.

---

## Meta-Project Location

`/Users/bruno/sec-llm-workbench/` (the meta-project, NOT SIOPV)

Active project (SIOPV): `~/siopv/` — DO NOT touch SIOPV files in this session. This session is 100% meta-project work.

---

## Fix List (ordered by severity)

### FIX 1 — HIGH: best-practices-enforcer permission bug
**File:** `.claude/agents/best-practices-enforcer.md`
**Problem:** Frontmatter has `disallowedTools: [Write, Edit]` but the agent description says "Verify and auto-correct" and the report format has "Auto-Corrections Applied" tables. The agent literally cannot write or edit files, making every auto-correction claim a hallucination.
**Decision to make:** Choose ONE model:
- Option A: Give it write/edit permission — remove `disallowedTools: [Write, Edit]` and `permissionMode: plan`. Change to `permissionMode: acceptEdits`. Agent can actually fix things.
- Option B: Keep it read-only — remove ALL language about "auto-corrections" from description, report format, and actions. Change "auto-correct" in description to "report". Remove the "Auto-Corrections Applied" table from report format. Remove "Fix Applied" column from violation tables.

Recommendation: **Option B** (read-only). Verification agents should not modify code — that's code-implementer's job. The agent's identity is an auditor, not a fixer.

**Exact changes needed in `.claude/agents/best-practices-enforcer.md`:**
- Line 4: Change `description: "Verify and fix Python 2026 best practices..."` → `"Verify and report Python 2026 best practices..."`
- Line 40: Change `"Verify and auto-correct..."` → `"Verify and report..."`
- In Actions section: Remove step 3 "Auto-correct when possible" or change to "Document all violations found"
- In Report Format: Remove "Auto-Corrections Applied" section. Remove "Fix Applied" column from violation tables. Keep "Manual Review Required" section but rename to "Violations Requiring Fix".
- Keep `disallowedTools: [Write, Edit]` and `permissionMode: plan` as-is (they are correct).

---

### FIX 2 — HIGH: verification-thresholds.md workflow section is stale
**File:** `.claude/docs/verification-thresholds.md`
**Problem:** The "Workflow Integration" section (around line 362–374) lists only 5 agents under `/verify command`. Wave 3's 9 agents are missing. Anyone reading this section alone thinks /verify only runs 5 agents.
**Fix:** Update the "Workflow Integration → /verify Command" subsection to list ALL 14 agents grouped by wave:

```
### /verify Command
Runs automatically in 3 waves:

**Wave 1 (~7 min, parallel):**
- best-practices-enforcer
- security-auditor
- hallucination-detector

**Wave 2 (~5 min, parallel):**
- code-reviewer
- test-generator

**Wave 3 (~7 min, parallel):**
- integration-tracer
- async-safety-auditor
- semantic-correctness-auditor
- smoke-test-runner
- config-validator
- regression-guard
- dependency-scanner
- circular-import-detector
- import-resolver

Total: ~19 minutes (vs. ~87 minutes sequential)
```

Also update the "Before Commit Checklist" text if it says "5 agentes" — it should say "14 agentes en 3 waves".

---

### FIX 3 — MEDIUM: orchestrate-parallel-verification.py has placeholder values
**File:** `.claude/scripts/orchestrate-parallel-verification.py`
**Problem:** The script is labeled a "simulation/reference" and has:
- `score = 10.0  # Placeholder` in `check_thresholds()` for code-reviewer
- `coverage = 85.0  # Placeholder` in `check_thresholds()` for test-generator
- Only handles Wave 1 + Wave 2 (no Wave 3) in `orchestrate()` method
- `self.thresholds` dict only has 5 agents, not 14
- Wave 3 note in docstring says "2 waves" not 3

**Two options:**
- Option A: Fully implement it as a real script (complex, may break things)
- Option B: Clearly mark it as documentation-only and fix the misleading placeholders

Recommendation: **Option B** — it cannot actually run agents (those are LLM Task() calls, not subprocess calls). Make it honest documentation.

**Changes:**
1. Update module docstring to explicitly say: "REFERENCE DOCUMENTATION ONLY — not executed at runtime. Actual agent invocation happens via Task() tool in the LLM orchestrator reading SKILL.md."
2. Add Wave 3 to the `orchestrate()` method with the same pattern (even as simulation)
3. Add all 14 agent names to `self.thresholds` dict (with placeholder thresholds for Wave 3 agents)
4. In `check_thresholds()`, replace misleading hardcoded values with explicit `NotImplementedError` or a comment saying "In production: read from agent report file at .ignorar/production-reports/..."
5. Update docstring: "Wave 1 (~7 min) + Wave 2 (~5 min) + Wave 3 (~7 min) = ~19 min total"

---

### FIX 4 — MEDIUM: check-reviewer-score.sh score extraction fragility
**File:** `.claude/scripts/check-reviewer-score.sh`
**Problem:** If regex patterns fail to extract score, script exits 0 with WARNING (allows commit). An agent using "Rating: 8.5" format bypasses the 9.0 threshold gate.
**Fix:** Make the graceful degradation more restrictive, OR standardize the score format in code-reviewer agent definition.

**Preferred approach:** Standardize the format in the code-reviewer agent first, then tighten the script.

Step 1 — Read `.claude/agents/code-reviewer.md` and add to its Report Format section:
```
**REQUIRED LINE (exactly this format, for score extraction):**
`Overall Score: X.X/10`
```
Make this mandatory in the report format template.

Step 2 — In `check-reviewer-score.sh`: after all pattern attempts fail, instead of exiting 0, print a clear warning that the score could not be extracted AND change exit behavior to depend on whether this is a first-time run (no reports at all) vs a report exists but parsing failed. If a report exists but score can't be extracted, that should be treated more cautiously — consider making it exit 1 (FAIL) instead of 0 (WARN).

Actually: check if the file exists but is malformed vs no file exists at all. Currently both cases return exit 0. Split them:
- No reports directory / no report files → exit 0 (WARN) [first time setup]
- Report exists but score not parseable → exit 1 (FAIL) [malformed report = require fix]

---

### FIX 5 — LOW: budget_tokens deprecated in agent frontmatter
**Problem:** Multiple agent `.md` files have `budget_tokens: N` in their frontmatter. Per the claude-api skill and Anthropic docs (verify online first!), `budget_tokens` is deprecated for Sonnet 4.6. Need to confirm if it's still used in Claude Code agent definitions or if it's simply ignored.

**Files to check and fix:**
- `.claude/agents/best-practices-enforcer.md` — `budget_tokens: 8000`
- `.claude/agents/import-resolver.md` — `budget_tokens: 15000`
- `.claude/agents/dependency-scanner.md` — `budget_tokens: 10000`
- Check ALL other agent files in `.claude/agents/` for `budget_tokens`

**Action:** First check online whether Claude Code agent frontmatter supports `budget_tokens` or if it should be removed/replaced. If deprecated, remove the field from all agent frontmatter files. Do NOT add `thinking: {type: "adaptive"}` to agent frontmatter unless confirmed as valid syntax by online docs.

---

### FIX 6 — LOW: No self-test suite for meta-project scripts
**Problem:** `check-module-coverage.py`, `check-reviewer-score.sh`, `scan-git-history-for-secrets.sh`, `post-code.sh` have zero automated tests. The system that verifies code has no verification of its own.

**What to create:** A minimal test suite at `.claude/tests/` with:
1. `test_check_module_coverage.py` — unit tests for the Python script:
   - Test PASS when all modules >= 50%
   - Test FAIL when any module < 50%
   - Test WARNING when coverage.xml missing
   - Test that `__init__.py` files are skipped
   - Test that `<string>` entries are skipped

2. `test_check_reviewer_score.sh` (bash test) — tests for the score extraction script:
   - Test PASS when score is "Overall Score: 9.5/10"
   - Test PASS when score is "Score: 9.0/10"
   - Test FAIL when score is "Overall Score: 8.5/10"
   - Test WARN (exit 0) when no reports directory
   - After FIX 4: Test FAIL when report exists but score unparseable

3. `test_scan_git_secrets.sh` — basic smoke test:
   - Test that script exits 1 when known secret pattern found
   - Test that script exits 0 when no secrets found

**Important:** These tests must run from the meta-project directory. Use `python3 -m pytest .claude/tests/` NOT `uv run pytest` (the meta-project itself may not have a pyproject.toml venv). Actually check if meta-project has its own pyproject.toml — if not, create a minimal one so tests can run with `uv run pytest .claude/tests/`.

---

## Files to Read Before Starting

Before making any edits, read these files to understand current state:
1. `.claude/agents/best-practices-enforcer.md` (full file — for FIX 1)
2. `.claude/agents/code-reviewer.md` (full file — for FIX 4)
3. `.claude/docs/verification-thresholds.md` (full file — for FIX 2)
4. `.claude/scripts/orchestrate-parallel-verification.py` (full file — for FIX 3)
5. `.claude/scripts/check-reviewer-score.sh` (full file — for FIX 4)
6. ALL files in `.claude/agents/` that have `budget_tokens` in frontmatter (glob search — for FIX 5)
7. Check if `.claude/tests/` directory already exists

Use Grep to find budget_tokens across all agents:
```bash
grep -rl "budget_tokens" /Users/bruno/sec-llm-workbench/.claude/agents/
```

---

## Execution Order

1. **Online research first** (WebFetch Claude Code docs)
2. FIX 5 first (budget_tokens) — requires online research to confirm
3. FIX 1 (best-practices-enforcer) — standalone file edit
4. FIX 2 (verification-thresholds.md) — standalone file edit
5. FIX 3 (orchestrate-parallel-verification.py) — standalone file edit
6. FIX 4 (check-reviewer-score.sh + code-reviewer.md) — two files, related
7. FIX 6 (self-test suite) — new files, do last (most complex)

After all fixes: run `/verify` on the meta-project itself if possible, or at minimum run `ruff check .claude/scripts/ .claude/tests/` and `python3 -m pytest .claude/tests/ -v`.

---

## Do NOT Touch

- SIOPV project (`~/siopv/`) — out of scope for this session
- `.claude/workflow/*.md` — not part of this fix (thresholds.md is in `.claude/docs/`, not workflow)
- `SKILL.md` — it's already correct (all 14 agents, 3 waves, proper Wave 3 enforcement)
- `pre-git-commit.sh` — already correct
- `post-code.sh` — already correct
- `scan-git-history-for-secrets.sh` — no changes needed (the script itself is fine; only needs a test)

---

## Context for Next Session

This is the meta-project `sec-llm-workbench`. It is NOT a project being built — it is the orchestration framework that manages project verification. Current state:
- 14 verification agents defined in `.claude/agents/`
- 3-wave parallel `/verify` skill in `.claude/skills/verify/SKILL.md`
- Pre-commit hook in `.claude/hooks/pre-git-commit.sh`
- Robustness audit conducted 2026-03-06, score 71/100
- Target: 85+/100 after these fixes
- SIOPV (the actual project being built) is at `~/siopv/`, phase 7 pending

The SIOPV project has its own backlog of CRITICAL issues (hollow CLI, asyncio.run in graph nodes, etc.) but those are a SEPARATE session. This session is 100% meta-project framework fixes.
