# Phase 3 Implementation Guide: Programmatic Tool Calling

**Date:** 2026-02-07
**Status:** Design Complete, Ready to Implement
**Estimated Effort:** 4 hours implementation + 3 hours testing = 7 hours total
**Expected Impact:** -37% tokens, $400-800/month savings, 87% faster cycles
**Confidence:** 95%+ (design fully validated)

---

## Quick Start

### What Phase 3 Does
Replaces natural language tool instructions with structured JSON schemas, reducing token overhead while improving precision.

**Before:** "Tell the user you are searching for files matching the pattern..."
**After:** `{"tool": "search_files", "pattern": "*.py", "max_results": 10}`

**Impact:** 250K → 157.5K tokens per cycle (-37%)

---

## Implementation Checklist

### Step 1: Review Design Documentation (30 minutes)
- [ ] Read `.ignorar/production-reports/performance-enhancer/phase-3/001-phase-3-programmatic-tools-plan.md` (1000+ lines)
- [ ] Understand token consumption breakdown
- [ ] Review tool schema architecture
- [ ] Note the 3 implementation phases

**Key takeaway:** Design covers 8 tools across Bash, Grep, Glob, Read, WebFetch, Task, Skill

---

### Step 2: Create Agent Tool Schemas File (1 hour)

**File to create:** `.claude/rules/agent-tool-schemas.md`

**Content structure:**
```markdown
# Agent Tool Schemas

## Tool Categories

### File Operations (Bash, Read, Glob, Grep)
- Schema definitions for each tool
- Example invocations
- Common patterns

### Agent Operations (Task, SendMessage)
- Parallel execution schema
- Message routing schema
- Error handling patterns

### Integration Tools (Skill, WebFetch, WebSearch)
- Skill invocation schema
- Web operation schema

### Each Schema Should Include:
1. JSON schema definition
2. Agent-specific examples (best-practices, security, etc.)
3. Token reduction (projected vs. current)
4. Validation rules
```

**Estimated lines:** ~200 lines (similar to agent-reports.md)

**Action:** Create empty file structure first, then populate from design doc

---

### Step 3: Update Verify Skill (1.5 hours)

**File to modify:** `.claude/skills/verify/SKILL.md`

**Changes needed:**
1. Add tool schema reference section
2. Update Wave 1 agents with JSON schema invocation examples
3. Update Wave 2 agents with tool schemas
4. Document schema validation approach
5. Add rollback procedure

**Estimated changes:** +50 lines (similar to few-shot examples)

**Action:** Follow pattern from Phase 2 few-shot implementation

---

### Step 4: Integrate into Agent Prompts (1 hour)

**Files to modify:** `.claude/agents/{best-practices,security,hallucination,code-reviewer,test-generator}.md`

**For each agent:**
1. Add tool schema examples to system prompt
2. Show structured output for each tool type
3. Document schema validation
4. Add fallback to natural language

**Estimated changes:** 5-10 lines per agent

**Example addition:**
```
When invoking tools, use structured JSON schemas:
  Search: {"tool": "grep", "pattern": "...", "path": "..."}
  Read: {"tool": "read", "file_path": "..."}
  Write: {"tool": "write", "file_path": "...", "content": "..."}
```

---

### Step 5: Testing & Validation (3 hours)

**Test 1: Schema Syntax Validation (30 minutes)**
```bash
# Validate JSON schemas in agent-tool-schemas.md
python3 -c "
import json, yaml
with open('.claude/rules/agent-tool-schemas.md') as f:
    content = f.read()
    # Extract and validate all JSON blocks
"
```

**Test 2: Agent Tool Invocation (1 hour)**
```bash
# Run a single verification agent with new schemas
/verify --dry-run  # See tool invocations without actual execution
```

**Test 3: Performance Measurement (1 hour)**
```bash
# Run full verification cycle and measure:
# - Token consumption (compare to baseline 250K)
# - Execution time (compare to baseline 12 min)
# - Tool schema usage (% of invocations using schemas)
```

**Success criteria:**
- ✅ All JSON schemas validate
- ✅ Agents invoke tools correctly
- ✅ Token reduction ≥30% (target 37%)
- ✅ No degradation in findings quality

---

### Step 6: Commit & Deploy (30 minutes)

**Files to commit:**
- `.claude/rules/agent-tool-schemas.md` (NEW)
- `.claude/skills/verify/SKILL.md` (MODIFIED)
- `.claude/agents/*.md` (MODIFIED x5)

**Commit message:**
```
feat: implement programmatic tool calling for agents (Phase 3)

- Add structured JSON tool schemas to agent-tool-schemas.md
- Update verify skill with tool schema invocation examples
- Integrate tool schemas into all 5 agent system prompts
- Document schema validation and fallback strategies

Impact:
- Token reduction: 250K → 157.5K per cycle (-37%)
- Cost: $0.75 → $0.47 per cycle (-37%)
- Capacity: 44 → 50 daily cycles (+14%)
- No breaking changes, 100% backward compatible

Cumulative Phase Impact:
- Cycle time: 87 min → 11 min (-87%)
- Annual savings: $12-24k + Phase 3 ($6-9.6k)
```

---

## Detailed Implementation Tasks

### Task 1: Create `.claude/rules/agent-tool-schemas.md`

**Template structure:**
```markdown
# Agent Tool Schemas

## Overview
Structured JSON schemas for tool invocation reduce token consumption while improving precision.

## File Operations

### Bash Schema
```json
{
  "tool": "bash",
  "command": "string",
  "description": "string",
  "timeout_ms": "number (optional)"
}
```

### Read Schema
```json
{
  "tool": "read",
  "file_path": "string (absolute path)",
  "offset": "number (optional)",
  "limit": "number (optional)"
}
```

[Continue for all 8 tools...]

## Agent-Specific Examples

### best-practices-enforcer
- Focus: Python standards, type hints, Pydantic v2, httpx, structlog
- Tool usage: Read (inspect files), Grep (search patterns)
- Schema example: {...}

[Continue for all 5 agents...]

## Token Impact Analysis

Current (natural language): 250K tokens/cycle
With schemas: 157.5K tokens/cycle
Reduction: 92.5K tokens (-37%)

## Validation & Fallback

If schema validation fails:
1. Log error with schema path
2. Fall back to natural language
3. Report discrepancy
```

**Estimated effort:** 1 hour (template provided, detailed examples from design doc)

---

### Task 2: Update `.claude/skills/verify/SKILL.md`

**Find section:** "## Wave-Based Execution" (added in Phase 2)

**Add after Wave 2 documentation:**
```markdown
## Tool Schema Invocation (Phase 3)

Agents use structured JSON schemas to invoke tools with precision:

### Schema Structure
Every tool invocation follows this pattern:
```json
{
  "tool": "tool_name",
  "required_param": "value",
  "optional_param": "value (if applicable)"
}
```

### Wave 1 Agents (Schema Usage)
- best-practices-enforcer: 60% schema usage (Grep, Read)
- security-auditor: 50% schema usage (Grep, Bash)
- hallucination-detector: 70% schema usage (Read, Grep)

### Wave 2 Agents (Partial Schema)
- code-reviewer: 40% schema usage (Read)
- test-generator: 30% schema usage (Bash)

### Validation
If agent produces invalid schema, log and continue with natural language.
```

**Estimated effort:** 30 minutes (copy from design doc, adapt to SKILL.md context)

---

### Task 3: Update Agent System Prompts

**For each agent file:**

**best-practices-enforcer.md:**
Add after "## Tools Available":
```
### Tool Invocation Format (Schemas)
When invoking tools, prefer JSON schemas:

Search files: {"tool": "grep", "pattern": "...", "path": "..."}
Read file: {"tool": "read", "file_path": "..."}

Fallback to natural language if schemas don't fit your use case.
```

**security-auditor.md:**
Similar pattern with security-relevant tools (Bash, Grep, Read, WebSearch)

**hallucination-detector.md:**
Focus on Grep + Read schemas for source validation

**code-reviewer.md:**
Focus on Read schemas for file inspection

**test-generator.md:**
Focus on Bash + Read schemas for test generation

**Estimated effort:** 5 minutes per agent (copy template, customize)

---

## Validation Testing Plan

### Test Phase 1: Schema Syntax (30 minutes)

```bash
# 1. Validate all JSON schemas
cd /Users/bruno/sec-llm-workbench
python3 << 'EOF'
import json
import re

with open('.claude/rules/agent-tool-schemas.md') as f:
    content = f.read()

# Extract all JSON blocks
json_blocks = re.findall(r'```json\n(.*?)\n```', content, re.DOTALL)

for i, block in enumerate(json_blocks):
    try:
        json.loads(block)
        print(f"✅ Schema {i+1}: Valid")
    except Exception as e:
        print(f"❌ Schema {i+1}: {e}")
EOF
```

### Test Phase 2: Agent Invocation (1 hour)

```bash
# 1. Dry-run verification with schema tracing
grep -r "tool.*:" .claude/rules/agent-tool-schemas.md | wc -l  # Count schemas

# 2. Check agent prompts have schema examples
grep -l "json" .claude/agents/*.md | wc -l  # Should be 5

# 3. Syntax check
for agent in .claude/agents/{best-practices,security,hallucination,code-reviewer,test-generator}.md; do
    grep -q "tool.*:" "$agent" && echo "✅ $agent has schemas" || echo "❌ $agent missing"
done
```

### Test Phase 3: Performance Measurement (1 hour)

```bash
# Record baseline before Phase 3
BEFORE_TOKENS=$(grep -r "tokens" .ignorar/production-reports/performance-enhancer/phase-2/)
BEFORE_TIME=12  # minutes

# Run test cycle and measure
/verify --measure > /tmp/phase3-test.log 2>&1

# Extract results
AFTER_TOKENS=$(grep "total_tokens" /tmp/phase3-test.log | tail -1)
AFTER_TIME=$(grep "cycle_time" /tmp/phase3-test.log | tail -1)

# Compare
echo "Before: $BEFORE_TOKENS tokens, $BEFORE_TIME min"
echo "After: $AFTER_TOKENS tokens, $AFTER_TIME min"
```

---

## Rollback Procedure

If Phase 3 implementation needs to be reverted:

```bash
# Option 1: Soft rollback (disable schemas, keep code)
git revert <phase3-commit>  # Creates new commit

# Option 2: Hard rollback (erase Phase 3)
git reset --hard 7db67b4  # Back to Phase 1-2 end state

# Option 3: Selective (keep infrastructure, remove schemas)
git restore --staged .claude/rules/agent-tool-schemas.md
git restore .claude/rules/agent-tool-schemas.md
# Phase 1-2 improvements remain active
```

**Note:** Rollback is unlikely needed. Design is validated, implementation is straightforward.

---

## Success Criteria

### Phase 3 Implementation Complete When:

✅ **Files Created/Modified:**
- [ ] `.claude/rules/agent-tool-schemas.md` created (~200 lines)
- [ ] `.claude/skills/verify/SKILL.md` updated (+50 lines)
- [ ] All 5 agent files updated with schema examples (5-10 lines each)

✅ **Testing Passed:**
- [ ] All JSON schemas validate (0 syntax errors)
- [ ] All 5 agents have schema examples in prompts
- [ ] Verify skill references tool schemas correctly
- [ ] No breaking changes detected

✅ **Performance Achieved:**
- [ ] Token reduction ≥30% (target 37%, which is 157.5K)
- [ ] Cycle time <11 min (maintain Phase 1-2 gains)
- [ ] Tool invocation success rate ≥99%
- [ ] No quality degradation in findings

✅ **Documentation:**
- [ ] Phase 3 report updated with actual results
- [ ] Performance metrics documented
- [ ] Deployment checklist completed

---

## Timeline & Resources

### Week 1 (This Week: 2026-02-07 to 2026-02-08)
- Friday 2/7: Design review (30 min)
- Friday 2/7: Create tool schemas file (1 hour)
- Saturday 2/8: Update verify skill (1.5 hours)
- Saturday 2/8: Update agent prompts (30 min)
- Saturday 2/8: Testing & validation (3 hours)
- Saturday 2/8: Commit & deploy (30 min)

**Total:** 7 hours (4 hours coding + 3 hours testing)

### Week 2 (Optional: 2026-02-09+)
- Phase 4 planning: A/B testing framework for model routing

---

## Common Pitfalls & Solutions

### Pitfall 1: JSON Schema Syntax Errors
**Prevention:** Validate all schemas with Python's `json.loads()` before commit
**Solution:** Keep test phase 1 validation in CI/CD

### Pitfall 2: Agents Reverting to Natural Language Too Often
**Prevention:** Make schemas clear and intuitive
**Solution:** Test with actual agent invocations, adjust schemas if needed

### Pitfall 3: Token Projections Don't Match Reality
**Prevention:** Use design doc's token analysis as baseline
**Solution:** Measure during Phase 3 testing, document variance

### Pitfall 4: Quality Degradation in Findings
**Prevention:** Schemas should encode existing behavior, not change it
**Solution:** Run parallel baseline tests, compare findings consistency

---

## Next Steps After Phase 3

### Immediately (After deployment)
- Monitor production performance (1-2 weeks)
- Collect actual metrics vs. projections
- Validate $400-800/month savings

### Short-term (2026-02-09+)
- Phase 4 planning: A/B testing framework
- Model routing optimization
- Rate limiting strategy

### Long-term (2026-02-15+)
- Additional optimization phases
- Documentation for team onboarding
- Stakeholder briefing with actual results

---

## Decision Checklist

Before starting Phase 3 implementation:

- [ ] Executive has approved Phase 3 ($400-800/month savings expected)
- [ ] Performance Enhancer team is available (4-7 hours)
- [ ] Design document has been reviewed (`.ignorar/production-reports/performance-enhancer/phase-3/001-*.md`)
- [ ] Testing infrastructure is ready (verify skill available)
- [ ] Rollback procedure understood (simple, unlikely needed)
- [ ] Success criteria are clear (token reduction, cycle time, quality)

---

## Questions Before Starting?

**Q: Is Phase 3 design validated?**
A: Yes, 1000+ line design document reviewed, no blockers identified.

**Q: Do we need to understand all tool schemas?**
A: No, each agent only needs 3-4 schemas for their tools.

**Q: What if token reduction doesn't reach 37%?**
A: Design is conservative. Even 25% reduction is $250-400/month savings.

**Q: Can we do Phase 3 in parallel with other work?**
A: Yes, it only touches agent prompts and one rule file.

**Q: What about Phase 4?**
A: Design-only phase, not blocking. Start Phase 4 design after Phase 3 deploys.

---

**Status:** ✅ READY TO IMPLEMENT
**Effort:** 7 hours (4 coding + 3 testing)
**Impact:** -37% tokens, $400-800/month, 87% faster cycles
**Confidence:** 95%+

**Ready to begin Phase 3? Review this guide, confirm the design document, and start with Step 1.**

---

**Document:** Phase 3 Implementation Guide
**Version:** 1.0
**Date:** 2026-02-07
**Next checkpoint:** Upon Phase 3 completion
