# Task 5.6: Deduplication Audit Report

**Date:** 2026-02-09
**Scope:** `.claude/rules/*.md` and `.claude/docs/*.md`
**Agent:** teammate-2 (general-purpose agent)

---

## Executive Summary

Analyzed 10 files across `.claude/rules/` (6 files) and `.claude/docs/` (4 files) for content duplication. Identified **8 major duplication patterns** requiring consolidation.

**Key Findings:**
- Python standards duplicated across 3 files
- Tech stack rules duplicated across 3 files
- Model selection guidance duplicated across 2 files
- Context7 MCP guidance duplicated across 2 files
- Agent report paths guidance duplicated across 2 files

**Recommendation:** Consolidate duplicated content and replace with cross-references to establish Single Source of Truth (SSOT) pattern.

---

## Duplication Patterns Identified

### 1. Python Standards Duplication

**Duplicated Content:** Modern Python type hints, Pydantic v2, httpx, structlog, pathlib usage

**Locations:**
- `.claude/docs/python-standards.md` (FULL DETAIL - 310 lines)
- `.claude/docs/techniques.md` (SUMMARY - lines 122-160)
- `.claude/rules/tech-stack.md` (MINIMAL - lines 9-14)

**Severity:** HIGH
**Lines Duplicated:** ~150 lines equivalent

**Analysis:**
- `python-standards.md` is the **canonical source** with complete examples, error patterns, and testing guidance
- `techniques.md` duplicates sections 11-13 (Modern Type Hints, Pydantic v2, Async HTTP)
- `tech-stack.md` lists the same stack items without detail

**SSOT Decision:** `.claude/docs/python-standards.md`

**Consolidation Plan:**
- **python-standards.md:** Keep as-is (detailed reference)
- **techniques.md:** Replace sections 11-13 with: `**→ See .claude/docs/python-standards.md for complete Python 2026 standards**`
- **tech-stack.md:** Keep minimal list (different purpose: quick reference vs detailed guide)

---

### 2. Tech Stack Listing Duplication

**Duplicated Content:** List of core technologies (uv, Pydantic v2, httpx, structlog, pathlib)

**Locations:**
- `.claude/rules/tech-stack.md` (AUTHORITATIVE - lines 9-14)
- `.claude/docs/techniques.md` (VISUAL SUMMARY - lines 161-183)
- `.claude/docs/python-standards.md` (IMPLIED - throughout examples)

**Severity:** MEDIUM
**Lines Duplicated:** ~30 lines equivalent

**Analysis:**
- `tech-stack.md` is minimal and authoritative
- `techniques.md` provides a visual summary box
- `python-standards.md` shows usage in examples (not duplication, just application)

**SSOT Decision:** `.claude/rules/tech-stack.md`

**Consolidation Plan:**
- **tech-stack.md:** Keep as-is (canonical list)
- **techniques.md:** Keep visual summary (different purpose: overview vs reference)
- **python-standards.md:** Keep examples (not duplication)

**Verdict:** NO CHANGE NEEDED - Different purposes justify overlap

---

### 3. Context7 MCP Query Guidance Duplication

**Duplicated Content:** Instruction to query Context7 before writing code

**Locations:**
- `.claude/rules/tech-stack.md` (lines 16-17): "Before Write/Edit: Query Context7 MCP for library syntax"
- `.claude/docs/mcp-setup.md` (lines 14-16): "Used by: code-implementer, best-practices-enforcer, hallucination-detector"
- `.claude/rules/agent-tool-schemas.md` (lines 382-458): Full tool schema for Context7 MCP

**Severity:** MEDIUM
**Lines Duplicated:** ~20 lines conceptual overlap

**Analysis:**
- `tech-stack.md` gives general guidance (when to use)
- `mcp-setup.md` provides setup instructions and agent mappings
- `agent-tool-schemas.md` provides technical schemas for tool invocation

**SSOT Decision:** **Multi-SSOT** (different aspects)
- **When to use:** `tech-stack.md`
- **How to set up:** `mcp-setup.md`
- **How to call (technical):** `agent-tool-schemas.md`

**Consolidation Plan:**
- **tech-stack.md:** Add reference: `**→ See .claude/docs/mcp-setup.md for Context7 setup instructions**`
- **mcp-setup.md:** Keep as-is
- **agent-tool-schemas.md:** Keep as-is

---

### 4. Agent Report Persistence Guidance Duplication

**Duplicated Content:** Instructions to save agent reports to `.ignorar/production-reports/`

**Locations:**
- `.claude/rules/agent-reports.md` (FULL DETAIL - lines 1-64)
- `.claude/workflow/04-agents.md` (REFERENCE - line 16 in table notes)

**Severity:** LOW
**Lines Duplicated:** ~10 lines reference

**Analysis:**
- `agent-reports.md` is the canonical source with full naming conventions
- `04-agents.md` only references it in passing

**SSOT Decision:** `.claude/rules/agent-reports.md`

**Consolidation Plan:**
- **agent-reports.md:** Keep as-is (canonical)
- **04-agents.md:** Already references correctly via workflow notes

**Verdict:** NO CHANGE NEEDED - Proper cross-reference already exists

---

### 5. Model Selection Strategy Duplication

**Duplicated Content:** Model routing rules (Haiku/Sonnet/Opus)

**Locations:**
- `.claude/rules/model-selection-strategy.md` (FULL DETAIL - 500+ lines decision tree)
- `.claude/workflow/04-agents.md` (SUMMARY - lines 11-44, table with model recommendations)
- `.claude/workflow/06-decisions.md` (REFERENCE - lines 40-98)

**Severity:** HIGH
**Lines Duplicated:** ~80 lines equivalent

**Analysis:**
- `model-selection-strategy.md` is the canonical decision tree
- `04-agents.md` duplicates quick reference table
- `06-decisions.md` duplicates model routing rules section

**SSOT Decision:** `.claude/rules/model-selection-strategy.md`

**Consolidation Plan:**
- **model-selection-strategy.md:** Keep as-is (canonical)
- **04-agents.md:** Replace model table with: `**→ See .claude/rules/model-selection-strategy.md for model selection decision tree**`
- **06-decisions.md:** Replace "Model Routing Rules" section (lines 40-98) with: `**→ See .claude/rules/model-selection-strategy.md for complete model routing strategy**`

---

### 6. Verification Threshold Duplication

**Duplicated Content:** PASS/FAIL criteria for verification agents

**Locations:**
- `.claude/rules/verification-thresholds.md` (FULL DETAIL - canonical)
- `.claude/workflow/05-before-commit.md` (SUMMARY TABLE - lines 14-28)

**Severity:** MEDIUM
**Lines Duplicated:** ~25 lines

**Analysis:**
- `verification-thresholds.md` is explicitly documented as SSOT (line 4)
- `05-before-commit.md` duplicates the threshold table

**SSOT Decision:** `.claude/rules/verification-thresholds.md`

**Consolidation Plan:**
- **verification-thresholds.md:** Keep as-is (canonical)
- **05-before-commit.md:** Replace threshold table with: `**→ See .claude/rules/verification-thresholds.md for complete threshold definitions**`

---

### 7. uv Package Manager Guidance Duplication

**Duplicated Content:** Instructions to use uv (never pip)

**Locations:**
- `.claude/rules/tech-stack.md` (line 10): "uv (NEVER pip)"
- `.claude/docs/techniques.md` (lines 7-19): Full section on uv usage
- `.claude/docs/errors-to-rules.md` (line 18, rule #1): "SIEMPRE uv (nunca pip/venv)"

**Severity:** LOW
**Lines Duplicated:** ~5 lines reference

**Analysis:**
- `tech-stack.md` states the rule (what)
- `techniques.md` provides usage examples (how)
- `errors-to-rules.md` documents why (historical mistake)

**SSOT Decision:** **Multi-SSOT** (different aspects)
- **What:** `tech-stack.md`
- **How:** `techniques.md`
- **Why:** `errors-to-rules.md`

**Consolidation Plan:**
NO CHANGE NEEDED - Different purposes justify overlap

---

### 8. Agent Execution vs Documentation Duplication

**Duplicated Content:** "Agents execute, don't just document"

**Locations:**
- `.claude/docs/techniques.md` (lines 22-31): Section 2
- `.claude/docs/errors-to-rules.md` (line 19, rule #2): "Agentes EJECUTAN, no solo documentan"

**Severity:** LOW
**Lines Duplicated:** ~3 lines concept

**Analysis:**
- `techniques.md` explains the pattern as a best practice
- `errors-to-rules.md` documents it as a historical error to avoid

**SSOT Decision:** **Multi-SSOT** (different contexts)
- **Best practice:** `techniques.md`
- **Error log:** `errors-to-rules.md`

**Consolidation Plan:**
NO CHANGE NEEDED - Different purposes (education vs history)

---

## Summary of Required Changes

### High Priority (Significant Duplication)

| File | Section | Action |
|------|---------|--------|
| `.claude/docs/techniques.md` | Lines 122-160 (Python standards) | Replace with reference to `python-standards.md` |
| `.claude/workflow/04-agents.md` | Lines 11-44 (Model table) | Replace with reference to `model-selection-strategy.md` |
| `.claude/workflow/06-decisions.md` | Lines 40-98 (Model routing) | Replace with reference to `model-selection-strategy.md` |
| `.claude/workflow/05-before-commit.md` | Lines 14-28 (Threshold table) | Replace with reference to `verification-thresholds.md` |

### Medium Priority (Minor Duplication)

| File | Section | Action |
|------|---------|--------|
| `.claude/rules/tech-stack.md` | Lines 16-17 | Add reference to `mcp-setup.md` |

### No Change Needed (Justified Overlap)

| Files | Reason |
|-------|--------|
| `tech-stack.md` + `techniques.md` visual summary | Different purposes (list vs overview) |
| `techniques.md` + `errors-to-rules.md` agent execution | Different contexts (education vs history) |
| `tech-stack.md` + `techniques.md` + `errors-to-rules.md` uv | Different aspects (what/how/why) |

---

## Token Impact Analysis

### Before Consolidation
Estimated duplicated content loaded into context:
- Python standards duplication: ~150 lines
- Model selection duplication: ~80 lines
- Verification threshold duplication: ~25 lines
- Context7 MCP duplication: ~20 lines

**Total redundant tokens:** ~275 lines ≈ **6,600 tokens wasted**

### After Consolidation
All duplicates replaced with single-line cross-references:
- Each reference: ~15 tokens
- Total references: 5

**New redundant tokens:** ~75 tokens
**Savings:** 6,525 tokens per context load (98.8% reduction)

### Annual Impact (Rough Estimate)
Assuming:
- 150 agent invocations/month
- 50% load these files into context
- $3/MTok input (Sonnet pricing)

**Before:** 150 × 0.5 × 6,600 tokens × 12 months = 5.94M tokens/year = **$17.82/year**
**After:** 150 × 0.5 × 75 tokens × 12 months = 67.5K tokens/year = **$0.20/year**
**Savings:** $17.62/year (98.8% reduction)

*Note: Small in absolute terms but demonstrates compounding effect of duplication*

---

## Single Source of Truth Mapping

| Topic | SSOT File | Purpose |
|-------|-----------|---------|
| **Python Standards** | `.claude/docs/python-standards.md` | Complete examples, testing, error handling |
| **Tech Stack List** | `.claude/rules/tech-stack.md` | Canonical list of technologies |
| **Model Selection** | `.claude/rules/model-selection-strategy.md` | Decision tree for Haiku/Sonnet/Opus |
| **Verification Thresholds** | `.claude/rules/verification-thresholds.md` | PASS/FAIL criteria |
| **Agent Reports** | `.claude/rules/agent-reports.md` | Report naming and persistence |
| **Agent Tool Schemas** | `.claude/rules/agent-tool-schemas.md` | JSON schemas for tool invocation |
| **MCP Setup** | `.claude/docs/mcp-setup.md` | Context7 setup instructions |
| **Techniques Catalog** | `.claude/docs/techniques.md` | Quick reference for all patterns |
| **Error Logging** | `.claude/docs/errors-to-rules.md` | Historical mistakes to avoid |
| **Traceability** | `.claude/docs/traceability.md` | Logging and reporting system |
| **Placeholder Conventions** | `.claude/rules/placeholder-conventions.md` | Naming standards for placeholders |

---

## Recommended Cross-Reference Format

When replacing duplicated content, use this format:

```markdown
**→ See `.claude/rules/X.md` for [specific topic]**
```

**Examples:**
- `**→ See .claude/docs/python-standards.md for complete Python 2026 standards**`
- `**→ See .claude/rules/model-selection-strategy.md for model selection decision tree**`
- `**→ See .claude/rules/verification-thresholds.md for complete threshold definitions**`

---

## Files Requiring Edits

### 1. `.claude/docs/techniques.md`

**Location:** Lines 122-160
**Current:** Full sections on Modern Type Hints, Pydantic v2, Async HTTP
**Replace with:**
```markdown
## 11-13. Python 2026 Standards

**→ See `.claude/docs/python-standards.md` for complete Python 2026 standards**

Quick summary:
- Modern type hints: `list[str]`, `X | None` (not `List[str]`, `Optional[X]`)
- Pydantic v2: `ConfigDict`, `@field_validator` (not `class Config`, `@validator`)
- Async HTTP: `httpx.AsyncClient` (not `requests`)
```

---

### 2. `.claude/workflow/04-agents.md`

**Location:** Lines 11-44
**Current:** Model recommendation table
**Replace with:**
```markdown
## Model Selection

**→ See `.claude/rules/model-selection-strategy.md` for model selection decision tree**

**Quick Reference:**
- **code-implementer:** Sonnet (default), Opus (>5 modules, architectural)
- **All 5 verification agents:** Sonnet (pattern recognition)
```

---

### 3. `.claude/workflow/06-decisions.md`

**Location:** Lines 40-98
**Current:** Model Routing Rules section
**Replace with:**
```markdown
## Model Routing Rules

**→ See `.claude/rules/model-selection-strategy.md` for complete model routing strategy**
```

---

### 4. `.claude/workflow/05-before-commit.md`

**Location:** Lines 14-28
**Current:** Verification Thresholds table
**Replace with:**
```markdown
## Verification Thresholds

**→ See `.claude/rules/verification-thresholds.md` for complete threshold definitions**
```

---

### 5. `.claude/rules/tech-stack.md`

**Location:** After line 17
**Current:** Ends with "Execute /verify before commit."
**Add:**
```markdown

**→ See `.claude/docs/mcp-setup.md` for Context7 MCP setup instructions**
```

---

## Validation Checklist

After implementing consolidation changes:

- [ ] All cross-references use consistent format
- [ ] SSOT files remain unchanged (canonical sources)
- [ ] No content deleted, only replaced with references
- [ ] All references point to existing files
- [ ] Token count reduced by ~98%
- [ ] No broken workflows (all references valid)

---

## Next Steps

1. **Implement edits** to 5 files listed above
2. **Validate cross-references** (run `grep -r "See \\.claude" .claude/`)
3. **Test workflow** (ensure agents can still find guidance)
4. **Update task #6** to completed
5. **Report to team lead** with summary of changes

---

## Conclusion

Identified and mapped 8 duplication patterns across 10 files. Recommended consolidating 4 high-priority duplications (Python standards, model selection, verification thresholds) and 1 medium-priority duplication (Context7 MCP guidance).

**Impact:**
- **Token savings:** ~6,500 tokens per context load (98.8% reduction)
- **Maintenance benefit:** Single source of truth prevents future drift
- **Clarity benefit:** Clearer ownership of canonical content

**Files requiring edits:** 5
**SSOT files established:** 11
**Cross-references to add:** 5

---

**Report Status:** ✅ Complete
**Saved to:** `.ignorar/production-reports/phase5/task-5.6-deduplication-audit.md`
**Date:** 2026-02-09
