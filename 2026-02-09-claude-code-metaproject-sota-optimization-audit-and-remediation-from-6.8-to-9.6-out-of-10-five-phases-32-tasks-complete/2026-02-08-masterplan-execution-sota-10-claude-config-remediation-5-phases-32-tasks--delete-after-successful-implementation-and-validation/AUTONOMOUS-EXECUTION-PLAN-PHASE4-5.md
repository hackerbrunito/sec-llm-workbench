# Autonomous Execution Plan: Phases 4-5

**Date:** 2026-02-08
**Target:** SOTA 9.6 → 10.0 via autonomous Lead Agent orchestration
**Total Tasks:** 15 tasks (8 in Phase 4, 7 in Phase 5)
**Estimated Time:** 3-4 weeks (Phase 4) + 2 weeks (Phase 5) = 5-6 weeks total
**Estimated Cost:** $5.59 in tokens ($2.96 Phase 4 + $2.63 Phase 5)

---

## Executive Summary

This document describes the **improved autonomous execution architecture** for Phases 4-5 based on lessons learned from Phase 3.

### The Problem with Phase 3 Architecture

**OLD APPROACH (Phase 3 - problematic):**
```
Human orchestrator (top-level Claude)
  ├─ Receives ALL agent reports in its context
  ├─ Manages task delegation directly
  ├─ Coordinates agent dependencies
  └─ Writes checkpoints and progress files

RESULT: Context bloat, single point of failure, compaction risk
```

**Issues encountered:**
1. Top-level Claude accumulated ~150K tokens by end of Phase 3
2. Agent reports (7 files × ~20KB) consumed orchestrator context
3. Human orchestrator became bottleneck for coordination
4. Risk of losing progress to compaction if context exceeded 200K

### The Solution: Lead Agent Architecture

**NEW APPROACH (Phase 4-5 - better):**
```
Top-Level Claude (minimal context, monitoring only)
  └─ Lead Agent (Sonnet, full orchestrator authority)
       ├─ Task Agent A (Haiku/Sonnet, executes task)
       ├─ Task Agent B (Haiku/Sonnet, executes task)
       ├─ Task Agent C (Haiku/Sonnet, executes task)
       ├─ Validator Agent 1 (Haiku, checks subset of files)
       ├─ Validator Agent 2 (Haiku, checks subset of files)
       └─ Checkpoint Agent (Haiku, saves progress)
```

**RESULT: Context isolation, autonomous progress, failure recovery**

### Key Architectural Principles

1. **Top-Level Claude = Pure Monitor**
   - Creates ONE team with ONE Lead Agent
   - Gives Lead Agent the FULL execution plan
   - Only intervenes at human checkpoints
   - Does NOT read files, run bash, or analyze reports

2. **Lead Agent = Autonomous Orchestrator**
   - Receives complete Phase 4 (or Phase 5) plan in prompt
   - Creates all tasks via TaskCreate with dependencies
   - Spawns sub-agents via Task tool (with team_name)
   - Manages task list, coordination, validation
   - Writes own checkpoints to disk
   - Saves progress before context runs out

3. **Sub-Agents = Independent Executors**
   - Each has 200K context budget (isolated from Lead Agent)
   - Writes report to `.ignorar/production-reports/`
   - Sends summary to Lead Agent (not full report)
   - Shuts down after task completion

4. **Validators = Small, Focused Checkers**
   - 2-3 validators instead of 1 large validator
   - Each checks 5-10 files maximum
   - Haiku model (fast, cheap, sufficient for validation)
   - Reports to Lead Agent via SendMessage

5. **Failure Recovery Protocol**
   - Lead Agent saves checkpoint after each milestone
   - If Lead Agent runs out of context: saves state, sends message
   - Top-level spawns NEW Lead Agent with checkpoint
   - New Lead Agent resumes from saved state

---

## Phase 4: Advanced Optimizations

**Target:** SOTA 9.6 → 9.8
**Tasks:** 8 tasks
**Estimated Time:** 3-4 weeks
**Estimated Cost:** $2.96 in tokens
**Key Deliverables:** Batch API, CoT, hybrid models, self-consistency voting

### Phase 4 Task Breakdown

#### Task 4.1: Implement Batch API for Verification Agents
**Finding:** M02 - LOW severity, Impact 8/10
**Description:** All agents use synchronous API; Batch API offers 50% discount
**Agent:** code-implementer (Sonnet)
**Model Justification:** Requires understanding async patterns but not full context
**max_turns:** 20
**Dependencies:** Phase 3 Task 3.1 (parallel execution as baseline)
**Estimated Tokens:** 40,000
**Estimated Cost:** $0.60

**Actions:**
1. Identify batch-eligible tasks (verification agents = non-interactive)
2. Implement batch submission logic:
   - Queue verification requests
   - Submit via Batch API (24h max latency)
   - Poll for completion
3. Update `.claude/skills/verify/SKILL.md` with batch mode flag
4. Measure cost savings (expect 50% on verification cycles)
5. Generate report: `.ignorar/production-reports/phase4/batch-api-deployment.md`

**Acceptance Criteria:**
- Batch submission script operational
- API integration tested (mock + real requests)
- Cost savings >40% validated
- Documentation updated

---

#### Task 4.2: Deploy Chain-of-Thought for Complex Agents
**Finding:** M07 - LOW severity, Impact 7/10
**Description:** Unclear if agents use CoT reasoning (+15-25% accuracy)
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires prompt engineering synthesis
**max_turns:** 15
**Dependencies:** None
**Estimated Tokens:** 30,000
**Estimated Cost:** $0.45

**Actions:**
1. Add CoT triggers to complex agents:
   - security-auditor: "Let's analyze step by step for vulnerabilities"
   - hallucination-detector: "Show your reasoning when comparing syntax"
2. Measure accuracy improvement (track CRITICAL finding precision)
3. Accept +100% token cost for ROI-positive tasks
4. Generate report: `.ignorar/production-reports/phase4/cot-deployment.md`

**Acceptance Criteria:**
- CoT prompts added to security-auditor + hallucination-detector
- Accuracy improvement >10% measured
- Token cost increase documented
- Report shows precision improvement on CRITICAL findings

---

#### Task 4.3: Implement Hybrid Model Strategy
**Finding:** M05 - LOW severity, Impact 8/10
**Description:** Single model per agent; hybrid gives -26% cost via cheap summary + expensive verification
**Agent:** code-implementer (Sonnet)
**Model Justification:** Requires multi-agent orchestration design
**max_turns:** 22
**Dependencies:** Phase 3 Task 3.3 (hierarchical routing operational)
**Estimated Tokens:** 50,000
**Estimated Cost:** $0.75

**Actions:**
1. Split code-implementer:
   - **Haiku:** Initial code draft (fast, cheap)
   - **Opus:** Refinement + quality check (slow, expensive)
2. Split verification agents:
   - **Sonnet:** Full file scan (broad coverage)
   - **Opus:** Deep analysis on flagged sections only (targeted precision)
3. Measure cost savings (expect -26%)
4. Generate report: `.ignorar/production-reports/phase4/hybrid-model-deployment.md`

**Acceptance Criteria:**
- Hybrid model patterns implemented for 2+ agents
- Cost reduction >20% measured
- Quality maintained or improved (no regression)
- Documentation with examples

---

#### Task 4.4: Implement Self-Consistency Voting for High-Stakes Tasks
**Finding:** M04 - LOW severity, Impact 7/10
**Description:** All agents single-path; N=3 voting gives +12-18% accuracy
**Agent:** code-implementer (Sonnet)
**Model Justification:** Requires voting logic implementation
**max_turns:** 18
**Dependencies:** Task 4.3 (hybrid models reduce voting cost overhead)
**Estimated Tokens:** 38,000
**Estimated Cost:** $0.57

**Actions:**
1. Implement N=3 self-consistency for security-auditor CRITICAL findings
2. Run 3 independent analyses with different random seeds
3. Take majority vote on severity classification
4. Accept 3-5× token cost for high-stakes decisions
5. Measure accuracy improvement (track false positive reduction)
6. Generate report: `.ignorar/production-reports/phase4/self-consistency-deployment.md`

**Acceptance Criteria:**
- Voting logic operational for security-auditor
- Accuracy improvement >10% on CRITICAL findings
- False positive rate reduced
- Cost-benefit analysis shows ROI

---

#### Task 4.5: Formalize Role-Based Prompting
**Finding:** M08 - LOW severity, Impact 6/10
**Description:** Agents have names but unclear if role preserved across turns
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple prompt template updates
**max_turns:** 12
**Dependencies:** None
**Estimated Tokens:** 10,000
**Estimated Cost:** $0.04

**Actions:**
1. Add role definitions to system prompts (50-100 tokens each):
   - "You are a Python best practices enforcer specializing in type hints and Pydantic v2"
   - "You are a security auditor focused on OWASP Top 10 vulnerabilities"
2. Add role reinforcement in multi-turn conversations
3. Measure quality improvement via user feedback
4. Generate report: `.ignorar/production-reports/phase4/role-based-prompting.md`

**Acceptance Criteria:**
- Role definitions added to all 6 agent prompts
- Role reinforcement tested in multi-turn sessions
- Documentation updated

---

#### Task 4.6: Optimize Long Context Usage
**Finding:** M09 - LOW severity, Impact 5/10
**Description:** No measurement of context usage; >200K costs 2× base rate
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple monitoring + alerting
**max_turns:** 10
**Dependencies:** None
**Estimated Tokens:** 8,000
**Estimated Cost:** $0.03

**Actions:**
1. Implement context tracking per session
2. Identify high-context agents (>200K threshold)
3. Add pruning strategies (clear between phases)
4. Alert if approaching 200K
5. Generate report: `.ignorar/production-reports/phase4/context-optimization.md`

**Acceptance Criteria:**
- Context monitoring script operational
- Alerting configured for >200K threshold
- Pruning strategies documented
- Report shows context usage patterns

---

#### Task 4.7: Expand Tool Descriptions to 150 Tokens
**Finding:** M11 - MEDIUM severity
**Description:** Tool descriptions may be too brief; 150 tokens recommended
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires synthesis of examples + failure modes
**max_turns:** 15
**Dependencies:** Phase 2 Task 2.2 (schemas deployed)
**Estimated Tokens:** 32,000
**Estimated Cost:** $0.48

**Actions:**
1. Audit all tool descriptions in agent-tool-schemas.md
2. Expand to ~150 tokens each:
   - Add examples
   - Document constraints
   - List failure modes
3. Measure retry reduction (expect -20% tool misuse)
4. Generate report: `.ignorar/production-reports/phase4/tool-description-expansion.md`

**Acceptance Criteria:**
- All tool descriptions expanded to 120-180 tokens
- Examples added for each tool
- Retry rate reduced by >15%
- Documentation updated

---

#### Task 4.8: Enable Parallel Tool Calling
**Finding:** M12 - MEDIUM severity
**Description:** Unclear if agents invoke multiple tools in single API call
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple prompt updates + validation
**max_turns:** 10
**Dependencies:** None
**Estimated Tokens:** 9,000
**Estimated Cost:** $0.04

**Actions:**
1. Update agent prompts: "When tools are independent, invoke them simultaneously"
2. Add examples of parallel tool calls
3. Validate with API logs (check for multi-tool requests)
4. Measure latency improvement (expect 6× faster for 6 tools)
5. Generate report: `.ignorar/production-reports/phase4/parallel-tool-calling.md`

**Acceptance Criteria:**
- Parallel tool calling examples added to all agent prompts
- API logs show multi-tool requests
- Latency improvement >3× measured
- Documentation updated

---

### Phase 4 Dependencies Graph

```
Task 4.1 (Batch API)        ← No deps
Task 4.2 (CoT)              ← No deps
Task 4.3 (Hybrid models)    ← Phase 3 Task 3.3 (routing)
Task 4.4 (Self-consistency) ← Task 4.3 (hybrid models)
Task 4.5 (Role prompting)   ← No deps
Task 4.6 (Context monitor)  ← No deps
Task 4.7 (Tool descriptions)← Phase 2 Task 2.2 (schemas)
Task 4.8 (Parallel tools)   ← No deps

INDEPENDENT: 4.1, 4.2, 4.5, 4.6, 4.7, 4.8 (can run in parallel)
SEQUENTIAL: 4.3 → 4.4 (must run in order)
```

### Phase 4 Success Criteria

- ✅ Batch API operational with 50% cost reduction on verification cycles
- ✅ CoT deployed for security-auditor + hallucination-detector with +15% accuracy
- ✅ Hybrid models deployed with -26% cost measured
- ✅ Self-consistency voting active for CRITICAL findings
- ✅ Role-based prompting formalized across all agents
- ✅ Context usage <200K per session (alerting active)
- ✅ Tool descriptions expanded to ~150 tokens with -20% retry reduction
- ✅ Parallel tool calling validated via API logs
- ✅ SOTA score: 9.6 → 9.8 (+0.2 from advanced optimizations)

---

## Phase 5: Final Polish and Validation

**Target:** SOTA 9.8 → 10.0
**Tasks:** 7 tasks
**Estimated Time:** 2 weeks
**Estimated Cost:** $2.63 in tokens
**Key Deliverables:** Over-prompting removal, MCP Apps evaluation, FINAL SOTA 10/10 validation

### Phase 5 Task Breakdown

#### Task 5.1: Audit and Remove Over-Prompting Language
**Finding:** W01 - MEDIUM severity
**Description:** Unknown if "CRITICAL: ALWAYS" language present; Opus 4.6 more responsive without it
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires pattern analysis + rewriting across many files
**max_turns:** 18
**Dependencies:** None
**Estimated Tokens:** 45,000
**Estimated Cost:** $0.68

**Actions:**
1. Grep for "CRITICAL:", "ALWAYS", "MUST", "NEVER" patterns
2. Replace with adaptive language:
   - "CRITICAL: ALWAYS verify" → "Verify when needed"
   - "MUST consult Context7" → "Consult Context7 for external libraries"
3. Test agent compliance (ensure no behavioral regression)
4. Generate report: `.ignorar/production-reports/phase5/over-prompting-removal.md`

**Files to audit:**
- `.claude/CLAUDE.md`
- `.claude/workflow/*.md` (7 files)
- `.claude/agents/*.md` (6 files)
- `.claude/rules/*.md` (6 files)

**Acceptance Criteria:**
- All instances of aggressive language replaced
- Adaptive language tested with agents
- No behavioral regression (>90% compliance maintained)
- Report documents changes with before/after examples

---

#### Task 5.2: Measure System Prompt Token Budget
**Finding:** W02 - LOW severity
**Description:** CLAUDE.md optimized but total token count unknown
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple token counting
**max_turns:** 8
**Dependencies:** Task 5.1 (after over-prompting removal)
**Estimated Tokens:** 6,000
**Estimated Cost:** $0.02

**Actions:**
1. Measure CLAUDE.md + all referenced docs token count
2. Compare to Anthropic recommendation (<2,000 tokens)
3. If >2,000, apply further compression
4. Generate report: `.ignorar/production-reports/phase5/system-prompt-token-audit.md`

**Files to measure:**
- `.claude/CLAUDE.md`
- Referenced workflow files at session start
- Total system prompt token count

**Acceptance Criteria:**
- Token count measured and documented
- Comparison to <2,000 token target
- Compression recommendations if needed
- Report saved to disk

---

#### Task 5.3: Evaluate MCP Apps for Interactive Debugging
**Finding:** M06 - LOW severity, evaluate first
**Description:** Production-ready Feb 2026; interactive debugging UIs
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires research + synthesis of MCP Apps capabilities
**max_turns:** 15
**Dependencies:** None (evaluation only, no implementation)
**Estimated Tokens:** 28,000
**Estimated Cost:** $0.42

**Actions:**
1. Research MCP Apps production readiness (Feb 2026 status)
2. Evaluate use cases:
   - Interactive verification dashboard
   - Agent debugging UI
   - Real-time monitoring
3. Assess integration effort vs. benefit
4. Generate recommendation: `.ignorar/production-reports/phase5/mcp-apps-evaluation.md`

**Acceptance Criteria:**
- Research complete (check Anthropic docs for Feb 2026 status)
- Use cases documented with examples
- Integration effort estimated
- Recommendation: deploy now vs. defer to Phase 6

---

#### Task 5.4: Evaluate Progressive Tool Discovery
**Finding:** M01 - XL effort, defer vs. evaluate
**Description:** 98.7% token reduction potential (50K → 300 tokens) but requires MCP gateway
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires architectural analysis
**max_turns:** 20
**Dependencies:** Task 5.3 (MCP Apps evaluation informs gateway design)
**Estimated Tokens:** 38,000
**Estimated Cost:** $0.57

**Actions:**
1. Analyze current tool loading overhead (~50K tokens estimated)
2. Design MCP gateway layer for dynamic loading
3. Estimate implementation effort (1+ week)
4. Cost-benefit analysis: 98.7% reduction vs. 1 week dev time
5. Generate roadmap: `.ignorar/production-reports/phase5/progressive-discovery-roadmap.md`
6. **Recommendation:** Defer to Phase 6 (post-SOTA 10/10) unless break-even <2 months

**Acceptance Criteria:**
- Current overhead measured
- MCP gateway design documented
- Implementation effort estimated
- ROI analysis complete
- Recommendation: Phase 6 deployment vs. defer

---

#### Task 5.5: Pin Tech Stack Versions
**Finding:** I06 - LOW severity
**Description:** tech-stack.md missing version constraints (e.g., "Pydantic v2.5+")
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple file updates
**max_turns:** 8
**Dependencies:** None
**Estimated Tokens:** 5,000
**Estimated Cost:** $0.02

**Actions:**
1. Add version constraints to tech-stack.md:
   - Pydantic v2.5+
   - httpx 0.24+
   - structlog 23.1+
   - pathlib (stdlib, Python 3.11+)
2. Reference from hallucination-detector verification criteria
3. Generate report: `.ignorar/production-reports/phase5/version-pinning.md`

**Acceptance Criteria:**
- Version constraints added for all major libraries
- hallucination-detector references updated
- Report documents version choices

---

#### Task 5.6: Validate Adaptive Thinking Budgets
**Finding:** I07 - LOW severity
**Description:** Adaptive thinking documented but unclear if active
**Agent:** general-purpose (Haiku)
**Model Justification:** Simple validation check
**max_turns:** 8
**Dependencies:** None
**Estimated Tokens:** 6,000
**Estimated Cost:** $0.02

**Actions:**
1. Verify adaptive thinking enabled for Opus 4.6 agents
2. Check API logs for auto-decide vs. fixed extended thinking
3. Confirm no extended_thinking overrides in agent configs
4. Generate report: `.ignorar/production-reports/phase5/adaptive-thinking-validation.md`

**Acceptance Criteria:**
- Adaptive thinking validated for all Opus agents
- API logs checked for auto-decide usage
- No overrides found in configs
- Report documents validation results

---

#### Task 5.7: Final SOTA Validation (All 47 Findings Resolved)
**Finding:** Need to validate all remediations complete and SOTA = 10/10
**Agent:** general-purpose (Sonnet)
**Model Justification:** Requires comprehensive audit + synthesis
**max_turns:** 25
**Dependencies:** All Phase 1-5 tasks complete
**Estimated Tokens:** 60,000
**Estimated Cost:** $0.90

**Actions:**
1. Review all 47 findings from gap analysis
2. Validate remediation for each:
   - **Category 1 (GOOD):** Confirmed unchanged
   - **Category 2 (IMPROVE):** All 8 optimizations deployed
   - **Category 3 (FIX):** All 8 fixes applied
   - **Category 4 (WRONG):** Both redone from scratch
   - **Category 5 (MISSING):** 12 features evaluated/deployed
3. Score each SOTA category (Context, Cost, Quality, Workflow, Docs, Features, Architecture)
4. Generate final report: `.ignorar/production-reports/FINAL-SOTA-VALIDATION.md`
5. **Success Criteria:** All categories = 10/10, overall SOTA = 10/10

**Files to audit:**
- `.ignorar/2026-02-08-claude-config-sota-audit-and-remediation-plan--delete-after-successful-implementation/team3-gap-analysis/prioritized-remediation-list.md` (47 findings)
- All production reports from Phases 1-5
- All modified files in `.claude/`

**Acceptance Criteria:**
- All 47 findings validated with evidence
- Each SOTA category scored
- Overall SOTA score = 10/10
- Report documents validation methodology

---

### Phase 5 Dependencies Graph

```
Task 5.1 (Over-prompting)   ← No deps
Task 5.2 (Token budget)     ← Task 5.1 (after cleanup)
Task 5.3 (MCP Apps eval)    ← No deps
Task 5.4 (Progressive disc) ← Task 5.3 (informs design)
Task 5.5 (Version pins)     ← No deps
Task 5.6 (Adaptive thinking)← No deps
Task 5.7 (Final validation) ← ALL tasks 5.1-5.6 complete

INDEPENDENT: 5.1, 5.3, 5.5, 5.6 (can run in parallel)
SEQUENTIAL: 5.1 → 5.2, 5.3 → 5.4
FINAL: 5.7 waits for ALL previous tasks
```

### Phase 5 Success Criteria

- ✅ All over-prompting language removed (adaptive triggering active)
- ✅ System prompt <2,000 tokens confirmed
- ✅ MCP Apps evaluation complete with recommendation
- ✅ Progressive tool discovery roadmap created (defer to Phase 6)
- ✅ Tech stack versions pinned
- ✅ Adaptive thinking validated for all Opus agents
- ✅ **FINAL VALIDATION:** All 47 findings remediated, SOTA = 10/10 confirmed

---

## Lead Agent Responsibilities

### 1. Planning & Task Management
- Read LEAD-AGENT-PROMPT-PHASE4.md (or PHASE5) at startup
- Create all tasks via TaskCreate with proper dependencies
- Track task completion via TaskUpdate
- Maintain task list coordination via TaskList

### 2. Agent Spawning & Coordination
- Spawn sub-agents via Task tool with explicit model parameter
- Use team_name parameter to add agents to current team
- Monitor agent completion via TaskList
- Send messages via SendMessage for coordination

### 3. Validation & Quality Control
- After task completion, spawn validator agents (2-3 small ones)
- Each validator checks 5-10 files maximum (Haiku model)
- Collect validation summaries
- Report issues back to implementing agent

### 4. Checkpoint & Progress Tracking
- Write checkpoint after each milestone:
  - After completing independent task group
  - After validation cycle
  - Before running out of context
- Save to: `.ignorar/.../PHASE{N}-PROGRESS-CHECKPOINT.md`
- Include: completed tasks, pending tasks, issues, next steps

### 5. Context Management
- Monitor own context usage
- If approaching 180K tokens: save checkpoint, send status to top-level
- Top-level will spawn NEW Lead Agent with checkpoint
- New Lead Agent resumes from saved state

### 6. Human Checkpoints
- Pause and send message to top-level for approval at:
  - Phase start (announce plan)
  - After all tasks complete (present summary)
  - Before any destructive action
- Use SendMessage with type="message" to top-level

### 7. Failure Recovery
- If sub-agent fails: analyze error, respawn with updated prompt
- If validation fails: delegate correction to implementing agent
- If blocked by external issue: save checkpoint, notify top-level
- Document all failures in checkpoint file

---

## Checkpoint Protocol

### When to Save Checkpoints
1. After completing a group of independent tasks
2. After validation cycle completes
3. Before approaching 180K token context
4. When blocked by external issue

### Checkpoint File Format
**Path:** `.ignorar/2026-02-08-masterplan-execution-sota-10-claude-config-remediation-5-phases-32-tasks--delete-after-successful-implementation-and-validation/PHASE{N}-PROGRESS-CHECKPOINT.md`

**Contents:**
```markdown
# Phase {N} Progress Checkpoint

**Date:** YYYY-MM-DD HH:MM:SS
**Lead Agent:** {agent_id}
**Context Usage:** {tokens}K / 200K
**Completed Tasks:** {X} / {Y}
**Status:** IN_PROGRESS / BLOCKED / READY_FOR_VALIDATION

## Completed Tasks
- [X] Task {N}.1: {description} - Agent {id} - Report: {path}
- [X] Task {N}.2: {description} - Agent {id} - Report: {path}

## Pending Tasks
- [ ] Task {N}.3: {description} - Blocked by: {reason}
- [ ] Task {N}.4: {description} - Ready to start

## Issues & Blockers
- Issue 1: {description}
- Issue 2: {description}

## Next Steps
1. Complete Task {N}.3
2. Spawn validation agents
3. Write final report

## Resume Instructions
If this checkpoint is loaded by a new Lead Agent:
1. Read all completed task reports
2. Verify files on disk
3. Resume with Task {N}.3
```

---

## Failure Recovery Protocol

### Scenario 1: Lead Agent Runs Out of Context

**Detection:** Lead Agent monitors own context, approaches 180K tokens

**Action:**
1. Lead Agent saves checkpoint with full state
2. Lead Agent sends message to top-level:
   ```
   Type: message
   Content: "Phase {N} Lead Agent approaching context limit (180K).
            Checkpoint saved at: {path}.
            Completed: {X}/{Y} tasks.
            Request new Lead Agent to resume."
   Summary: "Context limit reached, checkpoint saved"
   ```
3. Top-level spawns NEW Lead Agent with checkpoint path in prompt
4. New Lead Agent reads checkpoint, resumes work

**Prevention:**
- Use sub-agents for all work (isolation)
- Read only summaries (not full reports)
- Write checkpoints frequently

---

### Scenario 2: Sub-Agent Fails

**Detection:** Sub-agent reports failure or timeout

**Action:**
1. Lead Agent reads error from agent report
2. Lead Agent analyzes root cause
3. Lead Agent respawns agent with updated prompt:
   - Add error context
   - Add specific instructions to avoid failure
   - Reduce max_turns if timeout
4. If fails again: escalate to top-level (human checkpoint)

**Prevention:**
- Use appropriate model (Haiku for simple, Sonnet for complex)
- Set realistic max_turns (10-25 depending on task)
- Include clear acceptance criteria in prompt

---

### Scenario 3: Validation Fails

**Detection:** Validator agents report issues in files

**Action:**
1. Lead Agent collects validation findings
2. Lead Agent delegates correction to original implementing agent
3. Implementing agent fixes issues
4. Lead Agent respawns validators to re-check
5. If passes: proceed. If fails again: escalate to top-level

**Prevention:**
- Use 2-3 focused validators (not 1 large validator)
- Each validator checks 5-10 files maximum
- Clear validation criteria in prompt

---

### Scenario 4: External Blocker

**Detection:** Task blocked by missing file, unavailable service, etc.

**Action:**
1. Lead Agent saves checkpoint with blocker details
2. Lead Agent sends message to top-level:
   ```
   Type: message
   Content: "Phase {N} blocked by: {blocker description}.
            Action required: {what human needs to do}.
            Checkpoint saved at: {path}."
   Summary: "External blocker, human action required"
   ```
3. Top-level human resolves blocker
4. Top-level resumes Lead Agent or spawns new one with checkpoint

**Prevention:**
- Validate dependencies before starting task
- Check file existence before attempting operations
- Verify service availability (Context7, MCP servers)

---

## Human Checkpoint Protocol

### When to Pause for Human Approval

1. **Phase Start**
   - Announce plan summary
   - List all tasks with dependencies
   - Wait for "proceed" confirmation

2. **After All Tasks Complete**
   - Present summary of all task results
   - List validation findings
   - Wait for approval to commit changes

3. **Before Destructive Action**
   - File deletion
   - Multi-module refactoring (>3 modules)
   - Architectural changes
   - Wait for explicit approval

### Message Format

```
SendMessage(
  type="message",
  recipient="top-level-orchestrator",
  content="[Checkpoint Type]: [Details]. Awaiting approval to proceed.",
  summary="Human checkpoint: [brief description]"
)
```

### Top-Level Response

Top-level responds with one of:
- "Proceed" → Lead Agent continues
- "Pause" → Lead Agent saves checkpoint and waits
- "Modify: [instructions]" → Lead Agent adjusts plan and re-checks

---

## Lessons Learned from Phase 3

### What Worked Well

1. **Pure Orchestration**
   - Top-level delegating all work to agents = successful
   - Agent isolation prevented context pollution
   - Reports on disk = full traceability

2. **Model Selection**
   - Sonnet for verification agents = optimal quality/cost
   - Haiku for file validation = sufficient and cheap
   - Opus for parallel execution implementation = necessary for complexity

3. **Write-First Pattern**
   - Agents creating skeleton in turn 1 = no partial report loss
   - All reports saved to `.ignorar/production-reports/`
   - Checkpoint files enabled recovery

4. **Parallel Execution (Phase 3.1)**
   - Wave-based coordination worked as designed
   - 87 min → 12 min (86% improvement)
   - Validated with orchestration script

### What Didn't Work

1. **Single Large Validator**
   - Validation agent ac47131 tried to read 20+ files
   - Ran into context issues
   - Failed to complete before compaction

2. **Orchestrator Context Accumulation**
   - Top-level accumulated ~150K tokens by end of Phase 3
   - Reading all agent reports (7 × ~20KB) consumed context
   - Risk of losing progress if exceeded 200K

3. **Human Orchestrator as Coordinator**
   - Bottleneck for task delegation
   - Manual tracking of dependencies
   - No automated checkpoint writing

### Improvements for Phase 4-5

1. **Lead Agent Architecture**
   - ONE Lead Agent with full autonomy
   - Lead Agent writes own checkpoints
   - Top-level only monitors

2. **Split Validators**
   - 2-3 validators instead of 1
   - Each checks 5-10 files maximum
   - Haiku model (fast, cheap, sufficient)

3. **Summary-Only Reporting**
   - Sub-agents send summaries to Lead Agent (50 lines max)
   - Full reports stay on disk
   - Lead Agent context stays clean (<50K)

4. **Automated Dependency Management**
   - Lead Agent uses TaskCreate with blockedBy/blocks
   - TaskList coordination for shared state
   - SendMessage for explicit coordination

---

## Cost & Timing Estimates

### Phase 4 Cost Breakdown

| Task | Agent | Model | Tokens | Cost |
|------|-------|-------|--------|------|
| 4.1  | code-implementer | Sonnet | 40,000 | $0.60 |
| 4.2  | general-purpose | Sonnet | 30,000 | $0.45 |
| 4.3  | code-implementer | Sonnet | 50,000 | $0.75 |
| 4.4  | code-implementer | Sonnet | 38,000 | $0.57 |
| 4.5  | general-purpose | Haiku | 10,000 | $0.04 |
| 4.6  | general-purpose | Haiku | 8,000 | $0.03 |
| 4.7  | general-purpose | Sonnet | 32,000 | $0.48 |
| 4.8  | general-purpose | Haiku | 9,000 | $0.04 |
| **Total** | | | **217,000** | **$2.96** |

### Phase 5 Cost Breakdown

| Task | Agent | Model | Tokens | Cost |
|------|-------|-------|--------|------|
| 5.1  | general-purpose | Sonnet | 45,000 | $0.68 |
| 5.2  | general-purpose | Haiku | 6,000 | $0.02 |
| 5.3  | general-purpose | Sonnet | 28,000 | $0.42 |
| 5.4  | general-purpose | Sonnet | 38,000 | $0.57 |
| 5.5  | general-purpose | Haiku | 5,000 | $0.02 |
| 5.6  | general-purpose | Haiku | 6,000 | $0.02 |
| 5.7  | general-purpose | Sonnet | 60,000 | $0.90 |
| **Total** | | | **188,000** | **$2.63** |

### Combined Phase 4-5 Total

**Total Tokens:** 405,000
**Total Cost:** $5.59
**Estimated Time:** 5-6 weeks
**Expected ROI:** $4,200/year savings (baseline) + optimizations

---

## Success Metrics

### Phase 4 Success (SOTA 9.6 → 9.8)

- ✅ Batch API operational with 50% cost reduction
- ✅ CoT deployed with +15% accuracy improvement
- ✅ Hybrid models deployed with -26% cost measured
- ✅ Self-consistency voting active for CRITICAL findings
- ✅ Role-based prompting formalized
- ✅ Context usage <200K per session
- ✅ Tool descriptions expanded with -20% retry reduction
- ✅ Parallel tool calling validated

### Phase 5 Success (SOTA 9.8 → 10.0)

- ✅ Over-prompting language removed
- ✅ System prompt <2,000 tokens
- ✅ MCP Apps evaluation complete
- ✅ Progressive tool discovery roadmap
- ✅ Tech stack versions pinned
- ✅ Adaptive thinking validated
- ✅ **FINAL:** All 47 findings remediated, SOTA = 10/10

### Lead Agent Success

- ✅ Zero context-induced failures
- ✅ All checkpoints saved successfully
- ✅ All tasks completed with validation
- ✅ No human intervention needed except at checkpoints
- ✅ Full traceability maintained

---

## File Locations Reference

| Purpose | Path |
|---------|------|
| Master plan | `.ignorar/2026-02-08-claude-config-sota-audit-and-remediation-plan--delete-after-successful-implementation/team4-master-plan/MASTER-REMEDIATION-PLAN.md` |
| Phase 3 checkpoint | `.ignorar/.../PHASE3-PROGRESS-CHECKPOINT.md` |
| Phase 3 inventory | `.ignorar/production-reports/phase3/PHASE3-DELIVERABLES-INVENTORY.md` |
| Orchestrator handoff | `.ignorar/.../ORCHESTRATOR-HANDOFF-POST-PHASE3.md` |
| This plan | `.ignorar/.../AUTONOMOUS-EXECUTION-PLAN-PHASE4-5.md` |
| Lead Agent prompt | `.ignorar/.../LEAD-AGENT-PROMPT-PHASE4.md` (next file to create) |

---

**End of Autonomous Execution Plan**

**Next Action:** Create `LEAD-AGENT-PROMPT-PHASE4.md` with complete self-contained instructions for Lead Agent
