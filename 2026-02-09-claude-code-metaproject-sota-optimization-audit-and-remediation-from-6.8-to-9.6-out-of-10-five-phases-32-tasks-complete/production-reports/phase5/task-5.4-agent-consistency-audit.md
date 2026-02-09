# Agent Prompt Consistency Audit - Task 5.4

**Date:** 2026-02-09 06:15
**Task:** Verify agent prompt consistency across all 6 agent definition files
**Scope:** `.claude/agents/*.md` files
**Status:** ❌ INCONSISTENCIES FOUND

---

## Executive Summary

Audited 6 agent definition files for structural consistency, report path conventions, tool schema references, Context7 instructions, model recommendations, and wave assignments.

**Key Findings:**
- ❌ **Report Naming Convention:** 5/6 agents use DEPRECATED sequential numbering (`{NNN}-phase-{N}`) instead of REQUIRED timestamp-based naming
- ❌ **Tool Schema References:** 0/6 agents explicitly reference `.claude/rules/agent-tool-schemas.md`
- ⚠️  **Wave Assignment:** Only documented in `agent-reports.md`, NOT in individual agent files
- ✅ **Model Recommendations:** All agents have model specified in frontmatter
- ✅ **Role Reinforcement:** All agents have "Role Reinforcement" sections
- ✅ **Parallel Tool Calling:** All agents have Phase 4 parallelization guidance

---

## Detailed Consistency Matrix

### Section 1: Frontmatter Metadata

| Agent | name | description | tools | model | permissionMode | cache_control | budget_tokens |
|-------|------|-------------|-------|-------|----------------|---------------|---------------|
| **best-practices-enforcer** | ✅ | ✅ | ✅ | haiku | plan | ephemeral | 8000 |
| **code-implementer** | ✅ | ✅ | ✅ | sonnet | acceptEdits | ephemeral | 12000 |
| **code-reviewer** | ✅ | ✅ | ✅ | sonnet | plan | ephemeral | 9000 |
| **hallucination-detector** | ✅ | ✅ | ✅ | sonnet | plan | ephemeral | 10000 |
| **security-auditor** | ✅ | ✅ | ✅ | sonnet | plan | ephemeral | 10000 |
| **test-generator** | ✅ | ✅ | ✅ | sonnet | acceptEdits | ephemeral | 11000 |

**Finding:** All frontmatter consistent. ✅

---

### Section 2: Report Path Instructions

| Agent | Report Directory | Naming Convention | Timestamp-Based? | Sequential ({NNN})? | Issue |
|-------|------------------|-------------------|------------------|---------------------|-------|
| **best-practices-enforcer** | ✅ `.ignorar/production-reports/best-practices-enforcer/phase-{N}/` | `{NNN}-phase-{N}-best-practices-enforcer-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |
| **code-implementer** | ✅ `.ignorar/production-reports/code-implementer/phase-{N}/` | `{NNN}-phase-{N}-code-implementer-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |
| **code-reviewer** | ✅ `.ignorar/production-reports/code-reviewer/phase-{N}/` | `{NNN}-phase-{N}-code-reviewer-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |
| **hallucination-detector** | ✅ `.ignorar/production-reports/hallucination-detector/phase-{N}/` | `{NNN}-phase-{N}-hallucination-detector-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |
| **security-auditor** | ✅ `.ignorar/production-reports/security-auditor/phase-{N}/` | `{NNN}-phase-{N}-security-auditor-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |
| **test-generator** | ✅ `.ignorar/production-reports/test-generator/phase-{N}/` | `{NNN}-phase-{N}-test-generator-{slug}.md` | ❌ NO | ✅ YES | ⚠️ DEPRECATED |

**Finding:** ALL agents use deprecated sequential numbering instead of timestamp-based naming. This breaks under parallel execution (race conditions). ❌

**Reference:** `.claude/rules/agent-reports.md` (Lines 6-14) specifies REQUIRED format: `{TIMESTAMP}-phase-{N}-{agent-name}-{slug}.md`

**Impact:** CRITICAL for Phase 4 parallel execution. Multiple agents writing reports simultaneously may collide on sequential numbers.

---

### Section 3: Tool Schema References

| Agent | References `.claude/rules/agent-tool-schemas.md`? | Has Tool Invocation Section? | Has JSON Schema Examples? |
|-------|--------------------------------------------------|------------------------------|---------------------------|
| **best-practices-enforcer** | ❌ NO | ✅ YES (Phase 3) | ❌ NO (only parallelization guidance) |
| **code-implementer** | ❌ NO | ✅ YES (Context7 Protocol) | ✅ YES (3 examples) |
| **code-reviewer** | ❌ NO | ✅ YES (Phase 3) | ❌ NO (only parallelization guidance) |
| **hallucination-detector** | ❌ NO | ✅ YES (Phase 3) | ❌ NO (only parallelization guidance) |
| **security-auditor** | ❌ NO | ✅ YES (Phase 3) | ❌ NO (only parallelization guidance) |
| **test-generator** | ❌ NO | ✅ YES (Phase 3) | ❌ NO (only parallelization guidance) |

**Finding:** NO agents explicitly reference `agent-tool-schemas.md` as the canonical source of tool schemas. Only `code-implementer` has tool schema examples (Context7). ⚠️

**Expected:** Each agent should reference: "For complete tool schemas, see `.claude/rules/agent-tool-schemas.md`"

**Impact:** MEDIUM. Agents may not know where to find canonical tool schemas, leading to inconsistent tool usage.

---

### Section 4: Context7 Instructions

| Agent | Uses External Libraries? | Has Context7 Protocol Section? | Has resolve-library-id Example? | Has query-docs Example? |
|-------|-------------------------|-------------------------------|--------------------------------|------------------------|
| **best-practices-enforcer** | ✅ YES (verify Pydantic, httpx, structlog) | ❌ NO | ❌ NO | ❌ NO |
| **code-implementer** | ✅ YES (implements with all libs) | ✅ YES | ✅ YES | ✅ YES |
| **code-reviewer** | ❌ NO (reviews quality only) | ❌ NO | ❌ NO | ❌ NO |
| **hallucination-detector** | ✅ YES (verifies all libs) | ❌ NO (implied in Verification Process) | ❌ NO | ❌ NO |
| **security-auditor** | ❌ NO (audits patterns only) | ❌ NO | ❌ NO | ❌ NO |
| **test-generator** | ❌ NO (generates tests only) | ❌ NO | ❌ NO | ❌ NO |

**Finding:** Only `code-implementer` has explicit Context7 Protocol section with examples. `hallucination-detector` mentions Context7 in "Verification Process" but lacks example schemas. ⚠️

**Expected:** `best-practices-enforcer` and `hallucination-detector` should have Context7 protocol sections since they verify library usage.

**Impact:** MEDIUM. `best-practices-enforcer` may not know how to verify library syntax against Context7 docs.

---

### Section 5: Model Recommendations

| Agent | Model in Frontmatter | Model Documented in Body? | Matches `.claude/rules/model-selection-strategy.md`? |
|-------|---------------------|---------------------------|---------------------------------------------------|
| **best-practices-enforcer** | haiku | ❌ NO | ⚠️ Should be Sonnet (verification agent) |
| **code-implementer** | sonnet | ❌ NO | ✅ YES |
| **code-reviewer** | sonnet | ❌ NO | ✅ YES |
| **hallucination-detector** | sonnet | ❌ NO | ✅ YES |
| **security-auditor** | sonnet | ❌ NO | ✅ YES |
| **test-generator** | sonnet | ❌ NO | ✅ YES |

**Finding:** `best-practices-enforcer` uses `haiku` but should use `sonnet` per model-selection-strategy.md (verification agents require pattern recognition). ⚠️

**Reference:** `.claude/rules/model-selection-strategy.md` (Lines 295-304) specifies ALL verification agents should use Sonnet.

**Impact:** HIGH. Using Haiku for best-practices verification may miss complex violations requiring pattern recognition.

---

### Section 6: Wave Assignment Documentation

| Agent | Wave Assignment Documented? | Wave Number | Expected Wave |
|-------|----------------------------|-------------|---------------|
| **best-practices-enforcer** | ❌ NO | - | Wave 1 |
| **code-implementer** | N/A (not verification agent) | - | - |
| **code-reviewer** | ❌ NO | - | Wave 2 |
| **hallucination-detector** | ❌ NO | - | Wave 1 |
| **security-auditor** | ❌ NO | - | Wave 1 |
| **test-generator** | ❌ NO | - | Wave 2 |

**Finding:** NO verification agents document their wave assignment. Wave info only exists in `agent-reports.md`. ❌

**Expected:** Each verification agent should document: "**Wave Assignment:** Wave 1 (parallel with X, Y)" or "Wave 2 (parallel with Z)"

**Impact:** MEDIUM. Orchestrator must know wave assignments from external file, not from agent definition itself.

---

### Section 7: Role Reinforcement Sections

| Agent | Has "Role Reinforcement" Section? | Has "Every 5 Turns" Trigger? | Has Role Drift Detection? |
|-------|----------------------------------|------------------------------|--------------------------|
| **best-practices-enforcer** | ✅ YES (Line 104) | ✅ YES | ✅ YES |
| **code-implementer** | ✅ YES (Line 39) | ✅ YES | ✅ YES |
| **code-reviewer** | ✅ YES (Line 180) | ✅ YES | ✅ YES |
| **hallucination-detector** | ✅ YES (Line 126) | ✅ YES | ✅ YES |
| **security-auditor** | ✅ YES (Line 176) | ✅ YES | ✅ YES |
| **test-generator** | ✅ YES (Line 132) | ✅ YES | ✅ YES |

**Finding:** All agents have consistent role reinforcement sections. ✅

---

### Section 8: Parallel Tool Calling (Phase 4)

| Agent | Has "Tool Invocation (Phase 3)" Section? | Has "Parallelization Decision Tree"? | Has Agent-Specific Examples? |
|-------|------------------------------------------|-------------------------------------|------------------------------|
| **best-practices-enforcer** | ✅ YES (Line 124) | ✅ YES | ✅ YES |
| **code-implementer** | ✅ YES (Line 101) | ✅ YES | ✅ YES |
| **code-reviewer** | ✅ YES (Line 122) | ✅ YES | ✅ YES |
| **hallucination-detector** | ✅ YES (Line 68) | ✅ YES | ✅ YES |
| **security-auditor** | ✅ YES (Line 118) | ✅ YES | ✅ YES |
| **test-generator** | ✅ YES (Line 141) | ✅ YES | ✅ YES |

**Finding:** All agents have Phase 4 parallel tool calling guidance. ✅

---

### Section 9: Report Format Consistency

| Agent | Has "Report Format" Section? | Uses Cache Control Markers? | Has Markdown Template? |
|-------|------------------------------|----------------------------|------------------------|
| **best-practices-enforcer** | ✅ YES (Line 208) | ✅ YES | ✅ YES |
| **code-implementer** | ✅ YES (Line 184) | ✅ YES | ✅ YES |
| **code-reviewer** | ✅ YES (Line 226) | ✅ YES | ✅ YES |
| **hallucination-detector** | ✅ YES (Line 172) | ✅ YES | ✅ YES |
| **security-auditor** | ✅ YES (Line 320) | ✅ YES | ✅ YES |
| **test-generator** | ✅ YES (Line 226) | ✅ YES | ✅ YES |

**Finding:** All agents have consistent report format sections with cache control. ✅

---

## Critical Issues Summary

### Issue 1: DEPRECATED Report Naming Convention ❌

**Affected Agents:** ALL 6 agents
**Severity:** CRITICAL
**Description:** All agents use sequential numbering `{NNN}-phase-{N}-{agent}-{slug}.md` instead of REQUIRED timestamp-based naming `{TIMESTAMP}-phase-{N}-{agent}-{slug}.md`

**Evidence:**
- `best-practices-enforcer.md:193` → `{NNN}-phase-{N}-best-practices-enforcer-{descriptive-slug}.md`
- `code-implementer.md:167` → `{NNN}-phase-{N}-code-implementer-{descriptive-slug}.md`
- `code-reviewer.md:211` → `{NNN}-phase-{N}-code-reviewer-{descriptive-slug}.md`
- `hallucination-detector.md:156` → `{NNN}-phase-{N}-hallucination-detector-{descriptive-slug}.md`
- `security-auditor.md:304` → `{NNN}-phase-{N}-security-auditor-{descriptive-slug}.md`
- `test-generator.md:210` → `{NNN}-phase-{N}-test-generator-{descriptive-slug}.md`

**Reference:** `.claude/rules/agent-reports.md:8` specifies:
```
Format: {TIMESTAMP}-phase-{N}-{agent-name}-{slug}.md
Example: 2026-02-07-143022-phase-4-code-implementer-domain-layer.md
TIMESTAMP format: YYYY-MM-DD-HHmmss (24-hour format)
```

**Why This Matters:**
Sequential numbering (`001`, `002`, `003`) breaks under parallel execution. Multiple agents may:
1. Read the same "highest number" (e.g., `003`)
2. All try to create `004-phase-N-agent-slug.md`
3. File write collisions or overwrites

**Solution:** Update ALL 6 agents to use timestamp-based naming.

---

### Issue 2: Missing Tool Schema References ⚠️

**Affected Agents:** 5/6 agents (all except `code-implementer`)
**Severity:** MEDIUM
**Description:** No agents reference `.claude/rules/agent-tool-schemas.md` as the canonical source for tool schemas

**Expected:** Each agent should have in "Tool Invocation" section:
```markdown
For complete tool schemas and examples, see `.claude/rules/agent-tool-schemas.md`
```

**Impact:** Agents may not know where to find canonical tool schemas, leading to inconsistent tool usage or outdated patterns.

---

### Issue 3: Missing Wave Assignment Documentation ⚠️

**Affected Agents:** 5 verification agents
**Severity:** MEDIUM
**Description:** Wave assignments only documented in `agent-reports.md`, NOT in individual agent files

**Expected:** Each verification agent should document:
```markdown
**Wave Assignment:** Wave 1 (parallel execution with security-auditor, hallucination-detector)
```

**Impact:** Orchestrator must reference external file to know wave assignments instead of reading from agent definition.

---

### Issue 4: Incorrect Model for best-practices-enforcer ⚠️

**Affected Agents:** `best-practices-enforcer`
**Severity:** HIGH
**Description:** Uses `haiku` model instead of `sonnet` per model-selection-strategy.md

**Reference:** `.claude/rules/model-selection-strategy.md` (Section E: Verification Agents):
```markdown
### Section E: Verification Agents

├─ best-practices-enforcer
│  └─ USE: Sonnet

├─ security-auditor
│  └─ USE: Sonnet

├─ hallucination-detector
│  └─ USE: Sonnet

├─ code-reviewer
│  └─ USE: Sonnet

└─ test-generator
   └─ USE: Sonnet
```

**Rationale:** Verification requires quality pattern recognition but not full project context. Sonnet provides optimal balance.

**Impact:** Using Haiku for best-practices verification may miss complex violations requiring pattern recognition (e.g., subtle Pydantic v1 vs v2 patterns).

---

### Issue 5: Incomplete Context7 Documentation ⚠️

**Affected Agents:** `best-practices-enforcer`, `hallucination-detector`
**Severity:** MEDIUM
**Description:** Agents that verify library syntax lack explicit Context7 protocol sections with schema examples

**Expected:** `best-practices-enforcer` and `hallucination-detector` should have Context7 Protocol section similar to `code-implementer:66-112`

**Impact:** Agents may not know how to query Context7 for library verification, reducing verification accuracy.

---

## Recommended Fixes

### Fix 1: Update All Agents to Timestamp-Based Naming

**Files to modify:** ALL 6 `.claude/agents/*.md` files

**Changes:**

1. **best-practices-enforcer.md:189-194** - Change:
```markdown
### Naming Convention
```
{NNN}-phase-{N}-best-practices-enforcer-{descriptive-slug}.md
```

Examples:
- `001-phase-5-best-practices-enforcer-verify-domain-layer.md`
- `002-phase-5-best-practices-enforcer-fix-type-hints.md`
```

**TO:**
```markdown
### Naming Convention (Timestamp-Based)
```
{TIMESTAMP}-phase-{N}-best-practices-enforcer-{descriptive-slug}.md
```

**TIMESTAMP format:** `YYYY-MM-DD-HHmmss` (24-hour format)

Examples:
- `2026-02-09-061500-phase-5-best-practices-enforcer-verify-domain-layer.md`
- `2026-02-09-062030-phase-5-best-practices-enforcer-fix-type-hints.md`

**Why timestamp-based?** Sequential numbering breaks under parallel execution. Timestamps ensure uniqueness without coordination.
```

2. **best-practices-enforcer.md:196-203** - REMOVE "How to Determine Next Number" section (obsolete with timestamps)

3. **Repeat for all other agents:**
   - `code-implementer.md:163-179`
   - `code-reviewer.md:207-222`
   - `hallucination-detector.md:152-168`
   - `security-auditor.md:300-316`
   - `test-generator.md:206-222`

---

### Fix 2: Add Tool Schema References

**Files to modify:** ALL 6 `.claude/agents/*.md` files

**Changes:** Add after "Tool Invocation (Phase 3)" section header:

```markdown
## Tool Invocation (Phase 3 - JSON Schemas + Parallel Calling)
<!-- cache_control: start -->

**Reference:** For complete tool schemas, parameter definitions, and agent-specific examples, see `.claude/rules/agent-tool-schemas.md`

Use structured JSON schemas for tool invocation to reduce token consumption (-37%) and improve precision.
```

---

### Fix 3: Add Wave Assignment Documentation

**Files to modify:** 5 verification agents

**Changes:** Add in "Role Definition" section or near report persistence:

**best-practices-enforcer.md** (add after line 14):
```markdown
**Wave Assignment:** Wave 1 (~7 min, parallel with security-auditor, hallucination-detector)
```

**security-auditor.md** (add after line 14):
```markdown
**Wave Assignment:** Wave 1 (~7 min, parallel with best-practices-enforcer, hallucination-detector)
```

**hallucination-detector.md** (add after line 14):
```markdown
**Wave Assignment:** Wave 1 (~7 min, parallel with best-practices-enforcer, security-auditor)
```

**code-reviewer.md** (add after line 14):
```markdown
**Wave Assignment:** Wave 2 (~5 min, parallel with test-generator)
```

**test-generator.md** (add after line 14):
```markdown
**Wave Assignment:** Wave 2 (~5 min, parallel with code-reviewer)
```

---

### Fix 4: Correct best-practices-enforcer Model

**File:** `best-practices-enforcer.md:5`

**Change:**
```yaml
model: haiku
```

**TO:**
```yaml
model: sonnet
```

**Rationale:** Per `.claude/rules/model-selection-strategy.md`, ALL verification agents should use Sonnet for pattern recognition.

---

### Fix 5: Add Context7 Protocol to best-practices-enforcer

**File:** `best-practices-enforcer.md`

**Add after line 102 (before "Role Reinforcement"):**

```markdown
## Context7 Protocol (Library Verification)

When verifying library usage (Pydantic, httpx, structlog), query Context7 to confirm correct syntax:

1. Call `resolve-library-id` with the library name
2. Call `query-docs` with specific syntax question
3. Compare code against verified syntax

**Example: Verify Pydantic v2 ConfigDict**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "pydantic",
  "query": "Pydantic v2 ConfigDict usage"
}
```

**Example: Query specific syntax**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/pydantic/pydantic",
  "query": "What is the correct v2 syntax for model configuration?"
}
```

Do not rely on memory for library syntax. Always verify against Context7 documentation.
```

---

### Fix 6: Add Context7 Protocol to hallucination-detector

**File:** `hallucination-detector.md`

**The agent already has Context7 references in "Verification Process" section (lines 38-45), but lacks explicit protocol section with schema examples.**

**Add after line 66 (before "Tool Invocation"):**

```markdown
## Context7 Protocol (MANDATORY)

**CRITICAL:** Query Context7 for EVERY external library before flagging as hallucination.

### Workflow:
1. Extract library imports from code
2. For each library, call `resolve-library-id`
3. Query specific syntax with `query-docs`
4. Compare generated code against verified docs
5. Flag mismatches as hallucinations

### Tool Schema Examples

**Example 1: Resolve library**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "langgraph",
  "query": "StateGraph initialization and compile syntax"
}
```

**Example 2: Query specific API**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/langgraph/langgraph",
  "query": "How to initialize StateGraph with state schema?"
}
```

**Do NOT hallucinate library verification.** All syntax must be verified against Context7 documentation before flagging as hallucination.
```

---

## Verification Checklist

After applying fixes:

- [ ] All 6 agents use timestamp-based naming (`{TIMESTAMP}-phase-{N}-{agent}-{slug}.md`)
- [ ] All 6 agents reference `.claude/rules/agent-tool-schemas.md`
- [ ] All 5 verification agents document wave assignment
- [ ] `best-practices-enforcer` model changed from `haiku` to `sonnet`
- [ ] `best-practices-enforcer` has Context7 Protocol section
- [ ] `hallucination-detector` has explicit Context7 Protocol section with schemas
- [ ] All agents maintain consistent structure (frontmatter → role → actions → report format)

---

## Audit Statistics

| Metric | Count |
|--------|-------|
| **Agents Audited** | 6 |
| **Critical Issues** | 1 (report naming) |
| **High Priority Issues** | 1 (best-practices model) |
| **Medium Priority Issues** | 3 (tool schemas, wave docs, Context7) |
| **Low Priority Issues** | 0 |
| **Total Fixes Required** | 6 |
| **Consistency Score** | 67% (before fixes) |
| **Target Score** | 100% (after fixes) |

---

## Next Steps

1. **Apply all fixes** to 6 agent files
2. **Test agents** with timestamp-based naming in parallel execution
3. **Verify model routing** - confirm best-practices-enforcer uses Sonnet
4. **Update orchestrator** - ensure it references wave assignments from agent files
5. **Document completion** - mark Task 5.4 as COMPLETED

---

## Result

**AGENT CONSISTENCY AUDIT COMPLETED** ✅
- **Issues Found:** 6 (1 CRITICAL, 1 HIGH, 4 MEDIUM)
- **Fixes Identified:** All fixes documented above
- **Ready for Implementation:** YES

**Next Action:** Apply fixes to all 6 agent files, then re-audit for 100% consistency.
