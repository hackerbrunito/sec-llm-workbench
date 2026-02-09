# Script Classification Review - Phase 5 Follow-up

**Date:** 2026-02-09
**Reviewer:** teammate (general-purpose agent)
**Total Scripts Reviewed:** 6

---

## Executive Summary

Reviewed 6 untracked Python scripts in `.claude/scripts/`. Classification breakdown:

- **PRODUCTION:** 2 scripts (keep, add docstrings if needed)
- **EXPERIMENTAL:** 3 scripts (move to `.ignorar/experimental-scripts/`)
- **OBSOLETE:** 1 script (recommend deletion)

---

## Classification Table

| Script | Classification | Referenced | Quality | Recommendation |
|--------|----------------|------------|---------|----------------|
| `hybrid-verification.py` | EXPERIMENTAL | ✅ Yes (workflow/04-agents.md) | High | Move to experimental, document Phase 4 work |
| `self-consistency-vote.py` | EXPERIMENTAL | ✅ Yes (agents/security-auditor.md) | High | Move to experimental, advanced feature |
| `submit-batch-verification.py` | EXPERIMENTAL | ✅ Yes (skills/verify/SKILL.md) | High | Move to experimental, batch API (50% cost savings) |
| `test-hybrid-cost-savings.py` | EXPERIMENTAL | ❌ No | Medium | Move to experimental, simulation test |
| `test-self-consistency.py` | OBSOLETE | ❌ No | Medium | Delete (depends on experimental script) |
| `track-context-usage.py` | OBSOLETE | ❌ No | Low | Delete (no CLI integration, no usage) |

---

## Detailed Analysis

### 1. hybrid-verification.py

**Purpose:** Hybrid model verification orchestrator implementing two-phase verification:
- Phase 1 (Cheap): Haiku/Sonnet does broad scanning, flags suspicious sections
- Phase 2 (Expensive): Opus does targeted deep dive on flagged sections only
- Expected cost savings: -26% vs single-model baseline

**Quality Assessment:**
- ✅ Comprehensive module-level docstring
- ✅ Type hints throughout (modern Python 3.11+ syntax)
- ✅ Pydantic v2 dataclasses with proper validation
- ✅ Error handling in all async operations
- ✅ Structlog for structured logging
- ✅ Well-documented cost models and thresholds

**References:**
- Referenced in `.claude/workflow/04-agents.md` (Lines 222, 227)
- Part of "Agent Teams (Opus 4.6)" and "Hybrid Model Strategy (Phase 4)" sections

**Classification Rationale:** EXPERIMENTAL
- This is Phase 4 optimization work (not yet deployed in production)
- Implements advanced two-phase verification strategy
- No evidence of actual usage (no logs, no integration in `/verify` skill)
- High-quality code but experimental feature

**Recommendation:**
- Move to `.ignorar/experimental-scripts/phase4-hybrid-verification/`
- Add README.md explaining Phase 4 context and cost savings research
- Preserve as reference for future optimization work

---

### 2. self-consistency-vote.py

**Purpose:** Self-consistency voting for high-stakes verification decisions using N-sample voting (Wang et al. 2022).
- Generates N independent responses, extracts decisions, returns majority vote
- Expected accuracy improvement: +12-18% on ambiguous cases
- Used for reducing false positives in security findings

**Quality Assessment:**
- ✅ Excellent module-level docstring with usage examples
- ✅ Type hints throughout (modern syntax)
- ✅ Pydantic v2 models with proper validation
- ✅ Async implementation using asyncio
- ✅ CLI interface for testing
- ✅ Structlog for structured logging

**References:**
- Referenced in `.claude/agents/security-auditor.md` (Line 207)
- Mentioned as "Script: `.claude/scripts/self-consistency-vote.py`"
- Part of advanced security auditing features

**Classification Rationale:** EXPERIMENTAL
- Advanced feature for ambiguous security findings
- Not integrated into main verification workflow (not in `/verify` skill)
- High-quality implementation but experimental
- Adds API cost (3× calls for voting) without proven ROI

**Recommendation:**
- Move to `.ignorar/experimental-scripts/self-consistency-voting/`
- Document use cases and expected accuracy improvements
- Consider integration after validating cost-benefit ratio

---

### 3. submit-batch-verification.py

**Purpose:** Batch API verification script for Claude Code verification agents.
- Submits verification agent requests to Anthropic Batch API for 50% cost reduction
- Supports polling, exponential backoff, and results parsing
- Wave-based submission (Wave 1: 3 agents, Wave 2: 2 agents)

**Quality Assessment:**
- ✅ Comprehensive module-level docstring
- ✅ Type hints throughout (Pydantic v2 models)
- ✅ Error handling and retry logic
- ✅ CLI interface with subcommands (submit, poll, results)
- ✅ Structlog for structured logging
- ✅ Well-documented batch API operations

**References:**
- Referenced in `.claude/skills/verify/SKILL.md` (Lines 31, 35, 36)
- Part of Batch API integration documentation
- Commands: `submit --wave 1|2`, `poll BATCH_ID`, `results BATCH_ID`

**Classification Rationale:** EXPERIMENTAL
- Batch API feature for cost optimization (50% savings)
- Not integrated into production workflow (not in main `/verify` execution)
- Requires manual invocation (not automated)
- High-quality code but experimental feature

**Recommendation:**
- Move to `.ignorar/experimental-scripts/batch-api-verification/`
- Document batch API integration strategy
- Consider integration after validating latency trade-offs (batches take 24h)

---

### 4. test-hybrid-cost-savings.py

**Purpose:** Simulation test for hybrid verification cost savings.
- Tests hybrid model strategy vs single-model baselines
- Validates -26% cost reduction claim across 5 verification cycles
- Pure simulation (no real API calls)

**Quality Assessment:**
- ⚠️  No module-level docstring (only brief comment)
- ✅ Type hints on functions
- ✅ Dataclasses for structured data
- ✅ JSON output for results
- ⚠️  Hardcoded timestamp for reproducibility (not ideal)
- ⚠️  No error handling

**References:**
- Not referenced in any `.claude/` configuration files
- Standalone simulation test

**Classification Rationale:** EXPERIMENTAL
- Test harness for hybrid verification research
- Supports `hybrid-verification.py` (also experimental)
- No integration into production workflow
- Useful for cost analysis but not production code

**Recommendation:**
- Move to `.ignorar/experimental-scripts/phase4-hybrid-verification/tests/`
- Group with `hybrid-verification.py` for context
- Add docstring explaining simulation methodology

---

### 5. test-self-consistency.py

**Purpose:** Test harness for self-consistency voting system.
- Validates `self-consistency-vote.py` with 3 ambiguous security patterns
- Pytest-based test suite
- Demonstrates accuracy improvement on borderline cases

**Quality Assessment:**
- ⚠️  Brief module-level docstring
- ✅ Type hints on test functions
- ✅ Pytest markers for async tests
- ✅ Multiple test cases (ambiguous SQL, secrets, XSS)
- ⚠️  Imports from `self_consistency_vote` (dependency on experimental script)
- ⚠️  No mock for Anthropic API (tests make real API calls)

**References:**
- Not referenced in any `.claude/` configuration files
- Standalone test for experimental feature

**Classification Rationale:** OBSOLETE
- Test for experimental feature (`self-consistency-vote.py`)
- If parent feature is experimental, tests should be too
- Makes real API calls (expensive for testing)
- No evidence of execution or integration

**Recommendation:**
- **DELETE:** Tests for experimental features should be colocated
- If `self-consistency-vote.py` is kept, move test to same experimental directory
- Current standalone location suggests abandoned development

---

### 6. track-context-usage.py

**Purpose:** Track and alert on context usage patterns.
- Monitors token consumption per session and agent type
- Alerts at 150K (warning) and 180K (critical) thresholds
- Logs to `~/.claude/logs/context-usage.jsonl`

**Quality Assessment:**
- ⚠️  Brief module-level docstring
- ❌ No type hints (uses old-style Python 3.6-3.8 patterns)
- ⚠️  Uses `datetime.utcnow()` (deprecated in Python 3.12+)
- ⚠️  No structlog (uses print statements)
- ⚠️  Hard-coded paths and constants
- ⚠️  CLI with multiple subcommands but no usage in workflow

**References:**
- Not referenced in any `.claude/` configuration files
- No integration with hooks or skills
- Log directory `~/.claude/logs/context-usage.jsonl` not used elsewhere

**Classification Rationale:** OBSOLETE
- Context tracking is useful but not integrated
- Code quality below project standards (no type hints, old patterns)
- No evidence of usage (no logs, no references)
- Functionality could be replaced by Claude Code's built-in context tracking

**Recommendation:**
- **DELETE:** Not production-ready and not integrated
- If context tracking is needed, reimplement with:
  - Modern type hints
  - Structlog integration
  - Integration with hooks system
  - Alignment with `.claude/rules/` standards

---

## Implementation Plan

### Step 1: Create Experimental Directory Structure

```bash
mkdir -p .ignorar/experimental-scripts/phase4-hybrid-verification/tests
mkdir -p .ignorar/experimental-scripts/self-consistency-voting
mkdir -p .ignorar/experimental-scripts/batch-api-verification
```

### Step 2: Move EXPERIMENTAL Scripts

```bash
# Hybrid verification + test
mv .claude/scripts/hybrid-verification.py .ignorar/experimental-scripts/phase4-hybrid-verification/
mv .claude/scripts/test-hybrid-cost-savings.py .ignorar/experimental-scripts/phase4-hybrid-verification/tests/

# Self-consistency voting
mv .claude/scripts/self-consistency-vote.py .ignorar/experimental-scripts/self-consistency-voting/

# Batch API verification
mv .claude/scripts/submit-batch-verification.py .ignorar/experimental-scripts/batch-api-verification/
```

### Step 3: Delete OBSOLETE Scripts

```bash
rm .claude/scripts/test-self-consistency.py
rm .claude/scripts/track-context-usage.py
```

### Step 4: Update References

Update the following files to reflect new paths:

1. `.claude/workflow/04-agents.md` (Lines 222, 227):
   - Change: `.claude/scripts/hybrid-verification.py`
   - To: `.ignorar/experimental-scripts/phase4-hybrid-verification/hybrid-verification.py`
   - Note: Mark as experimental feature

2. `.claude/agents/security-auditor.md` (Line 207):
   - Change: `.claude/scripts/self-consistency-vote.py`
   - To: `.ignorar/experimental-scripts/self-consistency-voting/self-consistency-vote.py`
   - Note: Mark as experimental feature (not in production workflow)

3. `.claude/skills/verify/SKILL.md` (Lines 31, 35, 36):
   - Change: `.claude/scripts/submit-batch-verification.py`
   - To: `.ignorar/experimental-scripts/batch-api-verification/submit-batch-verification.py`
   - Note: Mark as experimental feature (not in production workflow)

### Step 5: Create README Files

Create README.md in each experimental directory documenting:
- Purpose and research context
- Integration status (experimental, not production)
- Expected benefits (cost savings, accuracy improvements)
- Trade-offs (latency, complexity)
- Future integration plan (if any)

---

## Findings Summary

### Scripts to Keep (with Relocation)
- **3 experimental scripts** with references → Move to `.ignorar/experimental-scripts/`
- **1 experimental test** without references → Move to `.ignorar/experimental-scripts/`

### Scripts to Delete
- **1 test script** for experimental feature → Delete (no value without parent)
- **1 utility script** with no integration → Delete (obsolete)

### Next Steps
1. ✅ Report generated (this file)
2. ⏳ Await human approval for classification
3. ⏳ Execute move/delete operations
4. ⏳ Update references in `.claude/` files
5. ⏳ Create README files for experimental directories
6. ⏳ Verify git status (ensure no untracked files remain in `.claude/scripts/`)

---

## References

- **Workflow documentation:** `.claude/workflow/04-agents.md`
- **Agent definitions:** `.claude/agents/security-auditor.md`
- **Skills:** `.claude/skills/verify/SKILL.md`
- **Python standards:** `.claude/docs/python-standards.md`
- **Tech stack:** `.claude/rules/tech-stack.md`

---

**Report Status:** Complete
**Awaiting:** Human approval for implementation plan
