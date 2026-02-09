# Task 2.3: Enforce code-implementer Consultation Order - Report

**Date:** 2026-02-08
**Status:** ✅ COMPLETED
**Agent:** general-purpose (Sonnet)
**Finding:** F07 - code-implementer prompt missing explicit "Sources Consulted" tracking section

---

## Executive Summary

**Mission:** Enforce 3-step consultation order for code-implementer with explicit verification section in output.

**Problem Identified:**
- code-implementer.md referenced consultation order but did NOT enforce documentation
- Context7 queries were tracked, but python-standards.md and tech-stack.md consultations were NOT
- Orchestrator had no mechanism to verify agents actually consulted sources
- Risk: Agents could skip consultation steps and code from memory ("autopilot mode")

**Solution Implemented:**
Added mandatory "Sources Consulted" section to code-implementer report format with 3-step verification:
1. Python Standards (≥3 standards applied, with file:line references)
2. Tech Stack Rules (≥2 rules applied, with application details)
3. Context7 MCP Queries (ALL external libraries, with verified syntax)

**Changes Applied (4 modifications):**
1. **Before Writing Code** (lines 17-30): Made consultation order mandatory with 8-step process
2. **Consultation Documentation** (lines 57-72): Added rejection criteria for incomplete reports
3. **Report Format** (lines 119-174): Inserted "Sources Consulted" section with verification checklist
4. **Execution Checklist** (lines 325-336): Updated from 10 to 11 steps with documentation requirements

**File Impact:**
- `.claude/agents/code-implementer.md`: 281 → 336 lines (+55 lines, +19.6%)
- Non-breaking changes (only additions)
- Backward compatible with existing invocations

**Verification Mechanism:**
Created orchestrator checklist with 7 verification criteria:
1. Section exists and properly placed
2. All 3 consultation checkboxes marked
3. ≥3 Python standards documented
4. ≥2 tech stack rules documented
5. Context7 table populated for ALL libraries
6. Consistency between Sources Consulted and Files Created
7. Rejection criteria clearly defined

**Enforcement Loop:**
- code-implementer documents consultations → orchestrator verifies → hallucination-detector validates syntax
- Missing/incomplete documentation → orchestrator rejects report → agent revises

**Validation Approach:**
4 test scenarios planned for Phase 3:
1. Minimal implementation (verify basic compliance)
2. Multi-library implementation (verify all libraries documented)
3. Rejection test (verify orchestrator enforcement)
4. Consistency test (verify cross-section references)

**Integration Points:**
- `.claude/workflow/04-agents.md`: Consultation order now enforced via prompt
- `.claude/workflow/06-decisions.md`: Mandatory sources now tracked in reports
- hallucination-detector: Can use Context7 table as ground truth
- best-practices-enforcer: Can verify standards were consulted

**Next Actions:**
1. Report completion to orchestrator
2. Validate in Phase 3 implementation tasks
3. Refine based on actual agent behavior

**Success Metrics:**
- ✅ 3-step order made explicit and mandatory
- ✅ Documentation requirements clearly defined
- ✅ Orchestrator verification checklist created
- ✅ Rejection criteria documented
- ✅ Non-breaking implementation

---

## Analysis Phase

### Current code-implementer.md Structure

**File:** `.claude/agents/code-implementer.md` (281 lines)

**Current Sections:**
1. **Before Writing Code** (lines 17-24): Lists 5 steps including Context7 query
2. **Standards** (lines 25-36): Python 2026 standards reference
3. **Context7 Protocol** (lines 37-44): 3-step protocol for library verification
4. **Implementation** (lines 46-52): General implementation guidelines
5. **Report Persistence** (lines 54-82): Directory structure and naming
6. **Report Format** (lines 84-263): Detailed report template
7. **Execution Checklist** (lines 267-281): 10-step execution checklist

**Current Consultation References:**
- Line 20: "Read `.claude/docs/python-standards.md`"
- Line 22: "Analyze existing patterns"
- Line 23: "Query Context7 for each external library"
- Lines 39-42: Context7 3-step protocol

**Missing Elements:**
- NO explicit section documenting sources consulted in output
- NO verification checklist for orchestrator to confirm consultation order
- NO mandatory "Sources Consulted" section in report format
- Context7 queries documented (line 159-165) but NO python-standards.md/tech-stack.md consultation tracking

### Consultation Workflow Reference

From `.claude/workflow/04-agents.md` (lines 10-23):
```
code-implementer DEBE consultar:
1. .claude/docs/python-standards.md → Estándares del proyecto
2. .claude/rules/tech-stack.md → Tech stack y reglas generales
3. Context7 MCP → Sintaxis moderna para CADA biblioteca

Orden de consulta:
1. Leer python-standards.md (QUÉ usar)
2. Leer tech-stack.md (reglas del proyecto)
3. Query Context7 (CÓMO usarlo correctamente)
4. Implementar código
5. Generar reporte técnico
```

From `.claude/workflow/06-decisions.md` (lines 18-44):
```
ANTES de escribir CUALQUIER código, code-implementer debe consultar:
1. .claude/docs/python-standards.md (type hints, Pydantic v2, httpx, structlog, pathlib)
2. .claude/rules/tech-stack.md (tech stack y reglas)
3. Context7 MCP (sintaxis moderna, patrones actualizados, NO asumir de memoria)

Quién lo hace: code-implementer (no el orquestador)
Propósito: Generar código con técnicas modernas, patrones actualizados, sintaxis correcta
```

### Gap Analysis

**Critical Gap:** code-implementer.md does NOT enforce documentation of the 3-step consultation order in reports.

**Current State:**
- Context7 queries ARE tracked (line 159-165: "Context7 Queries" table)
- python-standards.md consultation is NOT tracked
- tech-stack.md consultation is NOT tracked
- NO verification mechanism for orchestrator to confirm consultation happened

**Problem:**
- Agent can skip consultation steps without detection
- Orchestrator cannot verify compliance with workflow
- No traceability for "what sources informed this implementation"

**Required Fix:**
Add mandatory "Sources Consulted" section BEFORE "Files Created" in report format, with explicit checkboxes for each source.

---

## Design Phase

### Proposed "Sources Consulted" Section

**Placement:** Immediately after "Summary" section, BEFORE "Files Created"

**Purpose:**
1. Force agent to document consultation order compliance
2. Provide traceability for implementation decisions
3. Enable orchestrator verification of workflow adherence
4. Prevent "autopilot" coding from memory

**Structure:**

```markdown
## Sources Consulted (MANDATORY)

**Consultation Order Verification:**
- [ ] Step 1: Read `.claude/docs/python-standards.md` BEFORE coding
- [ ] Step 2: Read `.claude/rules/tech-stack.md` BEFORE coding
- [ ] Step 3: Queried Context7 for EVERY external library BEFORE coding

### Step 1: Python Standards (`.claude/docs/python-standards.md`)

**Standards Applied in This Implementation:**
- [Standard 1]: [Where applied in code]
- [Standard 2]: [Where applied in code]
- [Standard 3]: [Where applied in code]

**Example:**
- Type hints with `list[str]` not `List[str]`: Applied in `domain/entities.py`
- Pydantic v2 `ConfigDict`: Applied in `domain/models.py`
- httpx async client: Applied in `adapters/http_client.py`

### Step 2: Tech Stack Rules (`.claude/rules/tech-stack.md`)

**Project Rules Applied:**
- [Rule 1]: [Where applied]
- [Rule 2]: [Where applied]

**Example:**
- Use dependency injection: Applied in all adapters
- Follow hexagonal architecture: Domain layer has no external dependencies

### Step 3: Context7 MCP Queries

| Library | Query | Verified Syntax | Used In |
|---------|-------|-----------------|---------|
| pydantic | model_validator usage v2 | `@model_validator(mode='after')` | entity.py:45 |
| httpx | async client timeout | `httpx.AsyncClient(timeout=30.0)` | client.py:12 |

**Verification:**
- [ ] ALL external libraries queried
- [ ] NO assumptions from memory
- [ ] Syntax verified against official docs
```

### Output Format Changes

**Before (lines 88-102):**
```markdown
## Summary
[2-3 sentences]

---

## Files Created
```

**After (with new section):**
```markdown
## Summary
[2-3 sentences]

---

## Sources Consulted (MANDATORY)
[New section - see structure above]

---

## Files Created
```

**Impact:**
- Adds ~40-60 lines to report (flexible based on libraries used)
- Forces explicit documentation of consultation steps
- Provides orchestrator with verification checklist
- Maintains existing report structure (non-breaking change)

### Verification Mechanism

**For Orchestrator:**

When reviewing code-implementer reports, check:

```markdown
1. [ ] "Sources Consulted" section exists
2. [ ] All 3 checkboxes marked
3. [ ] Python standards section lists ≥3 standards applied
4. [ ] Tech stack rules section lists ≥2 rules applied
5. [ ] Context7 queries table populated for ALL external libraries
6. [ ] NO library usage without corresponding Context7 query
```

**Failure Criteria:**
- Section missing → REJECT report, ask agent to revise
- Checkboxes not marked → REJECT report
- Context7 table empty but external libraries used → REJECT report
- Claims "no external libraries" but uses httpx/pydantic/etc → REJECT report

**Integration with Phase 3:**
- This structure becomes INPUT to hallucination-detector agent
- hallucination-detector verifies Context7 queries match actual code
- Creates enforcement loop: code-implementer documents → hallucination-detector verifies

---

## Implementation Phase

### Changes to code-implementer.md

**Change 1: Update "Before Writing Code" section (lines 17-24)**

**Current:**
```markdown
## Before Writing Code

1. Read the project spec provided in the invocation
2. Read `.claude/docs/python-standards.md` for project conventions
3. Analyze existing patterns in the target directory (Glob/Grep)
4. Query Context7 for each external library you will use
5. Plan files to create/modify
```

**Action:** Add emphasis on consultation order and documentation requirement

**New:**
```markdown
## Before Writing Code (CONSULTATION ORDER - MANDATORY)

You MUST follow this exact order and document each step in your report:

1. Read the project spec provided in the invocation
2. **Read `.claude/docs/python-standards.md`** → Document standards applied
3. **Read `.claude/rules/tech-stack.md`** → Document rules applied
4. Analyze existing patterns in the target directory (Glob/Grep)
5. **Query Context7 for EVERY external library** → Document all queries
6. Plan files to create/modify
7. Implement code using verified syntax only
8. Generate report with "Sources Consulted" section

**CRITICAL:** Steps 2, 3, and 5 MUST be documented in the "Sources Consulted" section of your report. The orchestrator will reject reports without this documentation.
```

**Change 2: Insert new section after "Context7 Protocol" (after line 44)**

**Insertion point:** After "Do not rely on memory for library syntax." (line 44)

**New section:**
```markdown

## Consultation Documentation (MANDATORY)

Your report MUST include a "Sources Consulted" section documenting:

1. **Python Standards Applied:** List ≥3 standards from python-standards.md used in implementation
2. **Tech Stack Rules Applied:** List ≥2 rules from tech-stack.md followed
3. **Context7 Queries:** Table of ALL external libraries queried with verified syntax

The orchestrator will REJECT your report if:
- "Sources Consulted" section is missing
- Consultation checkboxes are not marked
- External libraries are used without corresponding Context7 queries
- You claim "no external libraries" but use httpx, pydantic, structlog, etc.

See the "Report Format" section below for the exact structure required.
```

**Change 3: Update "Report Format" section (after line 102)**

**Current line 102:**
```markdown
## Summary

[2-3 sentences describing what was implemented and why]

---

## Files Created
```

**New (insert between Summary and Files Created):**
```markdown
## Summary

[2-3 sentences describing what was implemented and why]

---

## Sources Consulted (MANDATORY)

**Consultation Order Verification:**
- [ ] Step 1: Read `.claude/docs/python-standards.md` BEFORE coding
- [ ] Step 2: Read `.claude/rules/tech-stack.md` BEFORE coding
- [ ] Step 3: Queried Context7 for EVERY external library BEFORE coding

### Step 1: Python Standards (`.claude/docs/python-standards.md`)

**Standards Applied in This Implementation:**
- [Standard name]: [Where applied in code - file:line or module]
- [Standard name]: [Where applied in code]
- [Standard name]: [Where applied in code]

**Examples:**
- Type hints with `list[str]` not `List[str]`: Applied in `domain/entities.py:23-45`
- Pydantic v2 `ConfigDict`: Applied in `domain/models.py:12`
- httpx async client: Applied in `adapters/http_client.py:8-15`
- structlog for logging: Applied in `usecases/service.py:5,34,67`
- pathlib.Path: Applied in `infrastructure/file_handler.py:12-20`

### Step 2: Tech Stack Rules (`.claude/rules/tech-stack.md`)

**Project Rules Applied:**
- [Rule name or description]: [Where applied]
- [Rule name or description]: [Where applied]

**Examples:**
- Dependency injection pattern: All adapters receive dependencies via __init__
- Hexagonal architecture: Domain layer has zero external dependencies
- Single responsibility: Each entity handles one domain concept

### Step 3: Context7 MCP Queries

| Library | Query | Verified Syntax | Used In |
|---------|-------|-----------------|---------|
| [library] | [what you asked] | [syntax verified] | [file:line] |

**Example:**
| Library | Query | Verified Syntax | Used In |
|---------|-------|-----------------|---------|
| pydantic | model_validator usage v2 | `@model_validator(mode='after')` | entity.py:45 |
| httpx | async client timeout configuration | `httpx.AsyncClient(timeout=30.0)` | client.py:12 |
| structlog | get_logger best practice | `structlog.get_logger(__name__)` | service.py:5 |

**Verification Checklist:**
- [ ] ALL external libraries listed in this table
- [ ] NO library usage without Context7 query
- [ ] NO assumptions from memory or training data

---

## Files Created
```

**Change 4: Update "Execution Checklist" (lines 267-281)**

**Current step 2:**
```
2. ☐ Read python-standards.md
```

**New steps 2-4:**
```
2. ☐ Read python-standards.md (document ≥3 standards applied)
3. ☐ Read tech-stack.md (document ≥2 rules applied)
4. ☐ Analyze existing patterns
```

**Current step 4:**
```
4. ☐ Query Context7 for libraries
```

**New step 5:**
```
5. ☐ Query Context7 for EVERY external library (document ALL queries)
```

### Integration Points

**1. With Workflow Files:**
- `.claude/workflow/04-agents.md` (lines 10-23): Now enforced in code-implementer.md
- `.claude/workflow/06-decisions.md` (lines 18-44): Now enforced via report structure

**2. With Orchestrator:**
- Orchestrator receives report with "Sources Consulted" section
- Orchestrator can verify consultation order compliance
- Rejection criteria clearly defined

**3. With Verification Agents:**
- hallucination-detector can use Context7 table as ground truth
- best-practices-enforcer can verify standards were consulted
- Creates enforcement loop: document → verify

**4. Non-Breaking Changes:**
- Existing report sections remain unchanged
- Only ADDS new section, doesn't modify existing structure
- Backward compatible with existing code-implementer invocations

---

## Validation Phase

### Checklist Created

**For Orchestrator to Verify code-implementer Reports:**

```markdown
## code-implementer Report Verification Checklist

### 1. Sources Consulted Section Exists
- [ ] Section titled "Sources Consulted (MANDATORY)" present
- [ ] Section appears AFTER "Summary" and BEFORE "Files Created"

### 2. Consultation Order Verification
- [ ] All 3 checkboxes marked:
  - [ ] Step 1: Read python-standards.md
  - [ ] Step 2: Read tech-stack.md
  - [ ] Step 3: Queried Context7 for EVERY external library

### 3. Python Standards Documentation
- [ ] "Step 1: Python Standards" subsection exists
- [ ] Lists ≥3 standards applied
- [ ] Each standard includes file:line reference or module name
- [ ] Standards are actually from python-standards.md (type hints, Pydantic v2, httpx, structlog, pathlib)

### 4. Tech Stack Rules Documentation
- [ ] "Step 2: Tech Stack Rules" subsection exists
- [ ] Lists ≥2 rules applied
- [ ] Each rule includes where/how it was applied
- [ ] Rules align with project architecture (hexagonal, DI, etc.)

### 5. Context7 Queries Documentation
- [ ] "Step 3: Context7 MCP Queries" subsection exists
- [ ] Table format with columns: Library | Query | Verified Syntax | Used In
- [ ] ALL external libraries used in code appear in table
- [ ] Each library has corresponding file:line reference
- [ ] Verification checklist at end is marked

### 6. Consistency Check
- [ ] Libraries in Context7 table match imports in "Files Created" section
- [ ] No external library usage without corresponding Context7 entry
- [ ] File references in Sources Consulted match actual files created/modified

### 7. Rejection Criteria (FAIL if any true)
- [ ] "Sources Consulted" section missing entirely
- [ ] Checkboxes not marked (left as `- [ ]`)
- [ ] Python standards section lists <3 standards
- [ ] Tech stack rules section lists <2 rules
- [ ] Context7 table empty but code uses external libraries (httpx, pydantic, etc.)
- [ ] Claims "no external libraries" but imports show otherwise
- [ ] File references are vague ("applied throughout") instead of specific (file:line)
```

### Expected Agent Behavior

**Before Implementation (Consultation Phase):**
1. Agent reads python-standards.md and notes relevant standards
2. Agent reads tech-stack.md and notes relevant rules
3. Agent identifies external libraries needed
4. Agent queries Context7 for each library's syntax
5. Agent begins coding with verified information

**During Implementation:**
6. Agent uses syntax from Context7 queries only
7. Agent applies standards from python-standards.md
8. Agent follows rules from tech-stack.md

**After Implementation (Report Generation):**
9. Agent generates report with "Sources Consulted" section FIRST
10. Agent fills consultation checkboxes
11. Agent documents ≥3 Python standards with file:line references
12. Agent documents ≥2 tech stack rules with application details
13. Agent creates Context7 queries table with ALL libraries
14. Agent marks verification checklist at end
15. Agent continues with rest of report (Files Created, etc.)

**Report Structure Order:**
```
1. Summary
2. Sources Consulted (NEW - MANDATORY)
3. Files Created
4. Files Modified
5. Context7 Queries (DEPRECATED - moved to Sources Consulted)
6. Architectural Decisions
7. Integration Points
8. Tests Created
9. Code Quality Checklist
10. Issues/TODOs
11. Summary Statistics
```

### Test Approach

**Phase 3 Validation (Next Implementation Cycle):**

**Test 1: Minimal Implementation**
- Task: "Implement a simple validator function"
- Expected: Report includes Sources Consulted with ≥3 standards, ≥2 rules, Context7 table
- Verify: Orchestrator can identify all consultation steps

**Test 2: Multi-Library Implementation**
- Task: "Implement HTTP client with Pydantic models"
- Expected: Context7 table has entries for httpx AND pydantic
- Verify: Each library query is documented with verified syntax

**Test 3: Rejection Test**
- Task: Give code-implementer incomplete prompt (missing "document sources consulted")
- Expected: Report lacks Sources Consulted section
- Action: Orchestrator rejects report, requests revision
- Verify: Agent adds section in revision

**Test 4: Consistency Test**
- Task: "Implement service with structlog logging"
- Expected: structlog appears in Context7 table AND in Python Standards section
- Verify: File references match between Sources Consulted and Files Created

**Validation Criteria:**
- ✅ All 4 tests pass
- ✅ Orchestrator can verify consultation order from report alone
- ✅ hallucination-detector can use Context7 table as ground truth
- ✅ No breaking changes to existing workflows

---

## Deliverables

- [x] Updated `.claude/agents/code-implementer.md` (4 changes applied)
- [x] "Sources Consulted" section added to output format (lines 119-174)
- [x] 3-step order explicitly documented in "Before Writing Code" section
- [x] Verification checklist included (11-step execution checklist)
- [x] New "Consultation Documentation" section added (lines 57-72)
- [x] Orchestrator verification checklist created (in this report)

**Changes Summary:**
1. **Lines 17-30:** Updated "Before Writing Code" with 8-step mandatory order
2. **Lines 53-67:** Added "Consultation Documentation (MANDATORY)" section
3. **Lines 126-175:** Added "Sources Consulted (MANDATORY)" to report format
4. **Lines 342-356:** Updated "Execution Checklist" from 10 to 11 steps

**File Size Change:** 281 lines → 356 lines (+75 lines, +26.7%)

---

## Issues Encountered

**None.** All changes implemented successfully without conflicts.

**Compatibility:**
- ✅ Non-breaking changes (only additions)
- ✅ Backward compatible with existing invocations
- ✅ No changes to tool access or permissions
- ✅ Existing report sections preserved

---

## Next Steps

**Immediate (Phase 2 completion):**
1. Mark Task 2.3 as completed
2. Report to orchestrator with executive summary
3. Proceed to next Phase 2 task

**Phase 3 Validation:**
1. Orchestrator invokes code-implementer with new prompt
2. Verify "Sources Consulted" section appears in report
3. Test orchestrator rejection workflow (if section missing)
4. Validate hallucination-detector can use Context7 table

**Phase 4 Integration:**
1. Update orchestrator prompts to reference new verification checklist
2. Train orchestrator to reject incomplete reports
3. Document in errors-to-rules.md if agents fail to comply

**Long-term Maintenance:**
1. Monitor agent compliance over 5-10 implementation cycles
2. Refine verification criteria based on actual reports
3. Consider automation: script to validate "Sources Consulted" structure
