# Master Remediation Plan: META-PROJECT Claude Code → SOTA 10/10
Generated: 2026-02-08
Input: team3-gap-analysis/prioritized-remediation-list.md (47 findings)

## Executive Summary

**Current SOTA Score:** 9.2/10
**Target SOTA Score:** 10/10
**Gap to Close:** 0.8 points across 47 findings
**Total Estimated Cost:** $120-180 (token usage across all phases)
**Total Estimated Time:** 9-10 weeks
**Estimated Annual Savings:** $4,200/year (validated baseline, not $20-35k overstated claims)

### Key Metrics
- **Findings Breakdown:** 1 CRITICAL, 5 HIGH, 11 MEDIUM, 30 LOW
- **Effort Distribution:** 12 Small (hours), 14 Medium (1-2 days), 3 Large (3-5 days), 3 XL (1+ weeks)
- **Quick Wins (Week 1):** 6 items, 8-14 hours, fixes 1 CRITICAL + 2 HIGH
- **Cycle Time Target:** 87 min → 10.84 min (-87.5% via Phase 4B parallel execution)
- **Token Reduction Target:** 250K → 157.5K per cycle (-37% via Phase 3 schemas)

### Top 5 Highest-ROI Items
1. **F01** - Extract verification thresholds (CRITICAL, 2-3h, Impact 10/10, prevents arbitrary PASS/FAIL)
2. **F05** - Deploy parallel execution (HIGH, 3-5d, Impact 10/10, -87.5% cycle time)
3. **I01** - Deploy prompt caching (MEDIUM, 2-4h, Impact 9/10, 75-90% read cost savings)
4. **F02** - Agent validation script (HIGH, 1-2d, Impact 9/10, prevents silent misconfig)
5. **F04** - Complete Phase 3 schema deployment (HIGH, 1-2d, Impact 9/10, $42/month savings)

### SOTA Score Breakdown (Current → Target)
- **Context Management:** 9.0 → 10.0 (+0.1: prompt caching, long context optimization)
- **Cost Efficiency:** 8.5 → 10.0 (+0.15: hierarchical routing, batch API, accurate cost claims)
- **Quality Assurance:** 9.5 → 10.0 (+0.05: threshold single source, agent validation, CoT)
- **Workflow Automation:** 9.5 → 10.0 (+0.05: parallel execution, fallback strategies)
- **Documentation & Traceability:** 9.0 → 10.0 (+0.1: broken refs fixed, model selection documented)
- **Advanced Features:** 8.0 → 10.0 (+0.2: progressive tool discovery, MCP gateway, MCP Apps)
- **Architecture:** 9.8 → 10.0 (+0.02: hybrid models, self-consistency voting)

### Implementation Strategy
- **Week 1:** Quick wins (6 items) - HIGH ROI, minimal effort
- **Week 2:** High-priority fixes (3 items) - Foundation for future phases
- **Weeks 3-4:** Major enhancements (3 items) - Parallel execution + hierarchical routing
- **Weeks 5-8:** Advanced features (6 items) - Batch API, CoT, hybrid models
- **Weeks 9-10:** Polish + validation (4 items) - MCP Apps, enterprise gateway evaluation

## Phase 1: Quick Wins (Week 1)

**Goal:** Fix 1 CRITICAL + 2 HIGH severity issues, deploy 75-90% cost savings via prompt caching
**Total Estimated Time:** 8-14 hours
**Total Estimated Cost:** $15-25 in tokens

### Task 1.1: Extract Verification Thresholds (F01 - CRITICAL)
- **Finding:** Thresholds scattered across docs, enables arbitrary PASS/FAIL decisions
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple file extraction/reorganization, no synthesis needed
- **max_turns:** 10
- **Input Size:** 200 lines (05-before-commit.md, 04-agents.md, errors-to-rules.md)
- **Output:** `.claude/rules/verification-thresholds.md` (~100 lines)
- **Dependencies:** None
- **Estimated Tokens:** 5,000 (Haiku: $0.40/$2 per MTok)
- **Estimated Cost:** $0.02
- **Actions:**
  1. Read `.claude/workflow/05-before-commit.md` (extract threshold table)
  2. Create `.claude/rules/verification-thresholds.md`
  3. Update references in `04-agents.md` and `05-before-commit.md`
  4. Update `pre-git-commit.sh` to reference centralized file

### Task 1.2: Fix Placeholder Conventions Broken Reference (F03 - HIGH)
- **Finding:** `placeholder-conventions.md` references non-existent `TEMPLATE-MEGAPROMPT-VIBE-CODING.md`
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple file search + edit, no complex reasoning
- **max_turns:** 8
- **Input Size:** 50 lines (placeholder-conventions.md)
- **Output:** Updated placeholder-conventions.md (~60 lines)
- **Dependencies:** None
- **Estimated Tokens:** 3,000
- **Estimated Cost:** $0.01
- **Actions:**
  1. Search for `TEMPLATE-MEGAPROMPT` in `.claude/` and project archives
  2. If not found: update reference to point to `.claude/workflow/` files
  3. If found: verify link is correct

### Task 1.3: Add Threshold Reference to 04-agents.md (F06 - HIGH)
- **Finding:** Agents lack explicit PASS/FAIL criteria documentation
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple reference addition after Task 1.1 completes
- **max_turns:** 5
- **Input Size:** 150 lines (04-agents.md)
- **Output:** Updated 04-agents.md (~160 lines)
- **Dependencies:** Task 1.1 (needs centralized threshold file to exist)
- **Estimated Tokens:** 2,000
- **Estimated Cost:** $0.01
- **Actions:**
  1. Add reference section in 04-agents.md
  2. Link to `.claude/rules/verification-thresholds.md`

### Task 1.4: Deploy Prompt Caching (I01 - MEDIUM, High ROI)
- **Finding:** cache_control markers documented but not deployed
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires synthesis across multiple agent prompts + API validation
- **max_turns:** 15
- **Input Size:** 500 lines (all agent prompts, workflow docs)
- **Output:** Updated prompts with cache_control markers (~600 lines total)
- **Dependencies:** None
- **Estimated Tokens:** 20,000 (Sonnet: $3/$15 per MTok)
- **Estimated Cost:** $0.30
- **Actions:**
  1. Identify static content in system prompts (workflow docs, standards, examples)
  2. Add `cache_control: {"type": "ephemeral"}` markers
  3. Deploy to all 6 agents (code-implementer + 5 verification)
  4. Validate with API logs (check cache hit rates)
  5. Document actual savings in `.ignorar/production-reports/cache-performance.md`

### Task 1.5: Recalibrate Cost Savings Claims (I02 - MEDIUM)
- **Finding:** Claims $20-35k/year; actual ~$4.2k/year per audit
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple text replacement + calculation validation
- **max_turns:** 10
- **Input Size:** 300 lines (agent-tool-schemas.md, cost projections)
- **Output:** Updated cost claims in all docs (~320 lines)
- **Dependencies:** None
- **Estimated Tokens:** 8,000
- **Estimated Cost:** $0.03
- **Actions:**
  1. Grep for "$20", "$35", "year", "savings" across `.claude/`
  2. Replace with validated $4.2k/year baseline
  3. Add methodology documentation: 150 cycles/month × $0.47/cycle × 12 months
  4. Add confidence intervals and assumptions

### Task 1.6: Test Context7 MCP Fallback (I05 - MEDIUM)
- **Finding:** Fallback to WebSearch documented but untested
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple testing script, no complex logic
- **max_turns:** 12
- **Input Size:** 100 lines (Context7 config, fallback logic)
- **Output:** Test script + monitoring config (~150 lines)
- **Dependencies:** None
- **Estimated Tokens:** 10,000
- **Estimated Cost:** $0.04
- **Actions:**
  1. Create `.claude/scripts/test-context7-fallback.sh`
  2. Add timeout configs (Context7: 5s, WebSearch: 10s)
  3. Implement fallback testing (inject Context7 failure)
  4. Add monitoring/alerting for Context7 availability
  5. Document results in `.ignorar/production-reports/context7-fallback-test.md`

### Phase 1 Context Budget
| Task | Agent Type | Model | Input (lines) | Output (lines) | Est. Tokens | Est. Cost |
|------|------------|-------|---------------|----------------|-------------|-----------|
| 1.1  | general-purpose | Haiku | 200 | 100 | 5,000 | $0.02 |
| 1.2  | general-purpose | Haiku | 50 | 60 | 3,000 | $0.01 |
| 1.3  | general-purpose | Haiku | 150 | 160 | 2,000 | $0.01 |
| 1.4  | general-purpose | Sonnet | 500 | 600 | 20,000 | $0.30 |
| 1.5  | general-purpose | Haiku | 300 | 320 | 8,000 | $0.03 |
| 1.6  | general-purpose | Haiku | 100 | 150 | 10,000 | $0.04 |
| **Total** | - | - | **1,300** | **1,390** | **48,000** | **$0.41** |

### Phase 1 Success Criteria
- ✅ `.claude/rules/verification-thresholds.md` created and referenced
- ✅ Placeholder conventions fixed (no broken doc links)
- ✅ Prompt caching deployed with >50% cache hit rate
- ✅ Cost claims updated to $4.2k/year with documented methodology
- ✅ Context7 fallback tested and monitoring active
- ✅ All changes committed with `/verify` passing

## Phase 2: High-Priority Fixes (Week 2)

**Goal:** Deploy agent validation, complete Phase 3 schemas, enforce code-implementer workflow
**Total Estimated Time:** 4-6 days
**Total Estimated Cost:** $35-50 in tokens

### Task 2.1: Create Agent Configuration Validation Script (F02 - HIGH)
- **Finding:** No automated check that agent definitions match 04-agents.md spec
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires code synthesis + understanding of YAML frontmatter validation
- **max_turns:** 20
- **Input Size:** 400 lines (04-agents.md, agent YAML examples)
- **Output:** `.claude/scripts/validate-agents.py` (~250 lines)
- **Dependencies:** Phase 1 complete (verification thresholds extracted)
- **Estimated Tokens:** 35,000 (Sonnet: $3/$15 per MTok)
- **Estimated Cost:** $0.53
- **Actions:**
  1. Read `.claude/workflow/04-agents.md` for agent spec
  2. Read `.claude/agents/` directory structure
  3. Create validation script:
     - Check agent names match spec
     - Verify tool schemas present
     - Validate YAML frontmatter
     - Check report path conventions
  4. Integrate into pre-commit hook
  5. Generate report: `.ignorar/production-reports/agent-validation/initial-audit.md`

### Task 2.2: Complete Phase 3 Schema Deployment (F04 - HIGH)
- **Finding:** 40 JSON schemas documented but deployment checklist unmarked
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires auditing 5 agent prompts + updating with JSON examples
- **max_turns:** 25
- **Input Size:** 1,200 lines (agent-tool-schemas.md, 5 agent prompt files)
- **Output:** Updated agent prompts (~1,400 lines total)
- **Dependencies:** Task 2.1 (validation script ensures schema correctness)
- **Estimated Tokens:** 50,000
- **Estimated Cost:** $0.75
- **Actions:**
  1. Read `.claude/rules/agent-tool-schemas.md`
  2. Audit each agent prompt for schema usage:
     - best-practices-enforcer
     - security-auditor
     - hallucination-detector
     - code-reviewer
     - test-generator
  3. Add JSON schema examples to each prompt
  4. Mark deployment checklist complete in agent-tool-schemas.md
  5. Validate with API logs (check for structured tool calls)
  6. Generate report: `.ignorar/production-reports/phase3-schema-deployment.md`

### Task 2.3: Enforce code-implementer Consultation Order (F07 - MEDIUM)
- **Finding:** Consultation order (python-standards → tech-stack → Context7) is trust-based
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires prompt engineering + template creation
- **max_turns:** 15
- **Input Size:** 300 lines (code-implementer prompt template, workflow docs)
- **Output:** Updated code-implementer prompt (~350 lines)
- **Dependencies:** None
- **Estimated Tokens:** 25,000
- **Estimated Cost:** $0.38
- **Actions:**
  1. Add "Sources Consulted" section to code-implementer report template
  2. Update prompt to require citations:
     - ✓ Consulted `.claude/docs/python-standards.md`
     - ✓ Consulted `.claude/rules/tech-stack.md`
     - ✓ Queried Context7 for [library names]
  3. Add orchestrator validation step (check report mentions Context7)
  4. Update `.claude/workflow/02-reflexion-loop.md` with validation requirement
  5. Generate report: `.ignorar/production-reports/code-implementer-workflow-enforcement.md`

### Task 2.4: Test Schema Fallback Strategy (F08 - MEDIUM)
- **Finding:** Fallback to natural language documented but untested
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple test suite creation
- **max_turns:** 12
- **Input Size:** 200 lines (agent-tool-schemas.md, validation examples)
- **Output:** Test suite (~150 lines)
- **Dependencies:** Task 2.2 (schemas must be deployed first)
- **Estimated Tokens:** 12,000
- **Estimated Cost:** $0.05
- **Actions:**
  1. Create `.claude/scripts/test-schema-fallback.py`
  2. Inject invalid JSON into schema validation
  3. Verify graceful fallback to natural language
  4. Log errors to `.ignorar/production-reports/schema-fallback-test.md`
  5. Add monitoring for schema parse failures

### Task 2.5: Document Model Selection Strategy (I03 - MEDIUM)
- **Finding:** All agents use Opus 4.6; no Haiku/Sonnet routing logic documented
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires synthesis of routing rules + cost analysis
- **max_turns:** 18
- **Input Size:** 500 lines (agent definitions, cost data, Anthropic research)
- **Output:** `.claude/rules/model-selection-strategy.md` (~200 lines)
- **Dependencies:** Phase 1 complete (cost claims recalibrated)
- **Estimated Tokens:** 30,000
- **Estimated Cost:** $0.45
- **Actions:**
  1. Define routing criteria:
     - **Haiku ($0.40/$2):** File reading, searching, auditing, simple transforms, validation
     - **Sonnet ($3/$15):** Synthesis, comparison, gap analysis, code review, multi-file refactoring
     - **Opus ($5/$25):** Final orchestration, decisions requiring full project context
  2. Create decision tree with examples
  3. Document 40-60% expected savings
  4. Add to `.claude/workflow/04-agents.md` reference section

### Phase 2 Context Budget
| Task | Agent Type | Model | Input (lines) | Output (lines) | Est. Tokens | Est. Cost |
|------|------------|-------|---------------|----------------|-------------|-----------|
| 2.1  | code-implementer | Sonnet | 400 | 250 | 35,000 | $0.53 |
| 2.2  | code-implementer | Sonnet | 1,200 | 1,400 | 50,000 | $0.75 |
| 2.3  | general-purpose | Sonnet | 300 | 350 | 25,000 | $0.38 |
| 2.4  | general-purpose | Haiku | 200 | 150 | 12,000 | $0.05 |
| 2.5  | general-purpose | Sonnet | 500 | 200 | 30,000 | $0.45 |
| **Total** | - | - | **2,600** | **2,350** | **152,000** | **$2.16** |

### Phase 2 Success Criteria
- ✅ Agent validation script operational + integrated into pre-commit
- ✅ All 5 verification agents using JSON schemas (verified via API logs)
- ✅ code-implementer reports include "Sources Consulted" section
- ✅ Schema fallback tested with 100% graceful degradation
- ✅ Model selection strategy documented with routing decision tree
- ✅ All changes pass `/verify` and committed

## Phase 3: Major Enhancements (Weeks 3-4)

**Goal:** Deploy parallel execution (-87.5% cycle time) + hierarchical routing (53% cost reduction)
**Total Estimated Time:** 8-12 days
**Total Estimated Cost:** $60-90 in tokens

### Task 3.1: Deploy Phase 4B Parallel Execution (F05 - HIGH, Impact 10/10)
- **Finding:** Wave-based parallelization designed but not implemented
- **Agent:** `code-implementer` (Opus)
- **Model Justification:** Complex multi-file implementation requiring full project context
- **max_turns:** 25
- **Input Size:** 2,000 lines (workflow docs, agent definitions, team coordination logic)
- **Output:** Parallel execution implementation (~800 lines code + config)
- **Dependencies:** Phase 2 complete (agent validation ensures correctness)
- **Estimated Tokens:** 120,000 (Opus: $5/$25 per MTok)
- **Estimated Cost:** $3.00
- **Actions:**
  1. Read `.claude/workflow/04-agents.md` (wave definitions)
  2. Implement wave-based coordination:
     - **Wave 1 (parallel, 7 min):** best-practices-enforcer, security-auditor, hallucination-detector
     - **Wave 2 (parallel, 5 min):** code-reviewer, test-generator
  3. Add TaskList coordination for shared state
  4. Implement SendMessage for inter-agent communication
  5. Add idle state management
  6. Create `.claude/scripts/orchestrate-parallel-verification.py`
  7. Update `.claude/skills/verify/SKILL.md` to use parallel execution
  8. Test with real verification cycle (measure actual time)
  9. Generate report: `.ignorar/production-reports/phase4b-parallel-deployment.md`

### Task 3.2: Validate Parallel Execution Performance (F05 - Validation)
- **Finding:** Need to confirm 87 → 10.84 min theoretical matches actual
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple execution + timing measurement
- **max_turns:** 10
- **Input Size:** 100 lines (test script)
- **Output:** Performance report (~150 lines)
- **Dependencies:** Task 3.1 (parallel execution must be deployed)
- **Estimated Tokens:** 8,000
- **Estimated Cost:** $0.03
- **Actions:**
  1. Run 3 full verification cycles with parallel execution
  2. Measure actual wall-clock time per wave
  3. Compare to baseline sequential (87 min)
  4. Generate report: `.ignorar/production-reports/parallel-execution-performance.md`
  5. Update `.claude/rules/agent-reports.md` with actual timings

### Task 3.3: Implement Hierarchical Model Routing (M03 - MEDIUM, Impact 9/10)
- **Finding:** All agents use Opus; no complexity-based routing
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires code synthesis but not full project context
- **max_turns:** 20
- **Input Size:** 800 lines (model selection strategy, agent definitions)
- **Output:** Routing implementation (~400 lines)
- **Dependencies:** Task 2.5 (model selection strategy documented)
- **Estimated Tokens:** 45,000
- **Estimated Cost:** $0.68
- **Actions:**
  1. Read `.claude/rules/model-selection-strategy.md`
  2. Create complexity classifier:
     - Regex-based task analysis
     - Keyword matching (e.g., "simple", "complex", "synthesis")
     - File count estimation
  3. Implement routing logic in orchestrator:
     - **Haiku:** File ops, search, audit, simple validation
     - **Sonnet:** Code review, gap analysis, multi-file refactor
     - **Opus:** Full project context decisions
  4. Add override mechanism for explicit model selection
  5. Generate report: `.ignorar/production-reports/hierarchical-routing-deployment.md`

### Task 3.4: Measure Hierarchical Routing Cost Savings (M03 - Validation)
- **Finding:** Validate 53% cost reduction claim
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple cost calculation + comparison
- **max_turns:** 8
- **Input Size:** 200 lines (API logs, routing decisions)
- **Output:** Cost analysis report (~100 lines)
- **Dependencies:** Task 3.3 (routing must be deployed + run for 1 week)
- **Estimated Tokens:** 6,000
- **Estimated Cost:** $0.02
- **Actions:**
  1. Collect 1 week of API logs with routing decisions
  2. Calculate actual costs: Haiku vs Sonnet vs Opus distribution
  3. Compare to baseline (all Opus)
  4. Generate report: `.ignorar/production-reports/routing-cost-analysis.md`
  5. Update cost projections in agent-tool-schemas.md

### Task 3.5: Optimize Few-Shot Examples (I04 - LOW, combine with caching)
- **Finding:** Unclear if using 1-2 examples (optimal) or 5+ (diminishing returns)
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires synthesis across agent prompts
- **max_turns:** 15
- **Input Size:** 600 lines (all agent prompts)
- **Output:** Optimized prompts (~650 lines)
- **Dependencies:** Phase 1 Task 1.4 (prompt caching deployed)
- **Estimated Tokens:** 28,000
- **Estimated Cost:** $0.42
- **Actions:**
  1. Audit all 6 agent prompts for few-shot example count
  2. Reduce to 1-2 examples max per agent
  3. Add cache_control markers around examples (combine with Phase 1.4)
  4. Measure token reduction (expect 60% on static examples)
  5. Generate report: `.ignorar/production-reports/few-shot-optimization.md`

### Task 3.6: Implement MCP Observability (I08 - MEDIUM)
- **Finding:** No monitoring for Context7 latency, errors, fallback activation
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires code for JSON-RPC timing + logging
- **max_turns:** 18
- **Input Size:** 400 lines (Context7 config, logging patterns)
- **Output:** Monitoring implementation (~300 lines)
- **Dependencies:** Phase 1 Task 1.6 (fallback tested)
- **Estimated Tokens:** 35,000
- **Estimated Cost:** $0.53
- **Actions:**
  1. Add JSON-RPC call timing wrappers
  2. Implement error tracking (Context7 failures)
  3. Log fallback activations (Context7 → WebSearch)
  4. Create dashboard: `.ignorar/production-reports/mcp-observability/dashboard.md`
  5. Add alerts for >10% fallback rate or >5s latency

### Phase 3 Context Budget
| Task | Agent Type | Model | Input (lines) | Output (lines) | Est. Tokens | Est. Cost |
|------|------------|-------|---------------|----------------|-------------|-----------|
| 3.1  | code-implementer | Opus | 2,000 | 800 | 120,000 | $3.00 |
| 3.2  | general-purpose | Haiku | 100 | 150 | 8,000 | $0.03 |
| 3.3  | code-implementer | Sonnet | 800 | 400 | 45,000 | $0.68 |
| 3.4  | general-purpose | Haiku | 200 | 100 | 6,000 | $0.02 |
| 3.5  | general-purpose | Sonnet | 600 | 650 | 28,000 | $0.42 |
| 3.6  | code-implementer | Sonnet | 400 | 300 | 35,000 | $0.53 |
| **Total** | - | - | **4,100** | **2,400** | **242,000** | **$4.68** |

### Phase 3 Success Criteria
- ✅ Parallel execution operational with 10-12 min actual cycle time (vs 87 min baseline)
- ✅ Hierarchical routing deployed with >40% cost reduction measured
- ✅ Few-shot examples reduced to 1-2 per agent + cached
- ✅ MCP observability dashboard active with <5% fallback rate
- ✅ All changes pass `/verify` and committed
- ✅ SOTA score: 9.2 → 9.6 (+0.4 from cycle time + cost optimizations)

## Phase 4: Advanced Features (Weeks 5-8)

**Goal:** Deploy Batch API (50% discount), CoT (+15-25% accuracy), hybrid models (-26% cost)
**Total Estimated Time:** 3-4 weeks
**Total Estimated Cost:** $80-120 in tokens

### Task 4.1: Implement Batch API for Verification Agents (M02 - LOW, Impact 8/10)
- **Finding:** All agents use synchronous API; Batch API offers 50% discount
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires understanding async patterns but not full context
- **max_turns:** 20
- **Input Size:** 600 lines (verification agent workflows, Anthropic Batch API docs)
- **Output:** Batch submission implementation (~350 lines)
- **Dependencies:** Phase 3 Task 3.1 (parallel execution as baseline)
- **Estimated Tokens:** 40,000
- **Estimated Cost:** $0.60
- **Actions:**
  1. Identify batch-eligible tasks (verification agents = non-interactive)
  2. Implement batch submission logic:
     - Queue verification requests
     - Submit via Batch API (24h max latency)
     - Poll for completion
  3. Update `.claude/skills/verify/SKILL.md` with batch mode flag
  4. Measure cost savings (expect 50% on verification cycles)
  5. Generate report: `.ignorar/production-reports/batch-api-deployment.md`

### Task 4.2: Deploy Chain-of-Thought for Complex Agents (M07 - LOW, Impact 7/10)
- **Finding:** Unclear if agents use CoT reasoning (+15-25% accuracy)
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires prompt engineering synthesis
- **max_turns:** 15
- **Input Size:** 500 lines (security-auditor, hallucination-detector prompts)
- **Output:** Updated prompts with CoT triggers (~550 lines)
- **Dependencies:** None
- **Estimated Tokens:** 30,000
- **Estimated Cost:** $0.45
- **Actions:**
  1. Add CoT triggers to complex agents:
     - security-auditor: "Let's analyze step by step for vulnerabilities"
     - hallucination-detector: "Show your reasoning when comparing syntax"
  2. Measure accuracy improvement (track CRITICAL finding precision)
  3. Accept +100% token cost for ROI-positive tasks
  4. Generate report: `.ignorar/production-reports/cot-deployment.md`

### Task 4.3: Implement Hybrid Model Strategy (M05 - LOW, Impact 8/10)
- **Finding:** Single model per agent; hybrid gives -26% cost via cheap summary + expensive verification
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires multi-agent orchestration design
- **max_turns:** 22
- **Input Size:** 800 lines (agent definitions, orchestration patterns)
- **Output:** Hybrid agent implementations (~500 lines)
- **Dependencies:** Phase 3 Task 3.3 (hierarchical routing operational)
- **Estimated Tokens:** 50,000
- **Estimated Cost:** $0.75
- **Actions:**
  1. Split code-implementer:
     - **Haiku:** Initial code draft (fast, cheap)
     - **Opus:** Refinement + quality check (slow, expensive)
  2. Split verification agents:
     - **Sonnet:** Full file scan (broad coverage)
     - **Opus:** Deep analysis on flagged sections only (targeted precision)
  3. Measure cost savings (expect -26%)
  4. Generate report: `.ignorar/production-reports/hybrid-model-deployment.md`

### Task 4.4: Implement Self-Consistency Voting for High-Stakes Tasks (M04 - LOW, Impact 7/10)
- **Finding:** All agents single-path; N=3 voting gives +12-18% accuracy
- **Agent:** `code-implementer` (Sonnet)
- **Model Justification:** Requires voting logic implementation
- **max_turns:** 18
- **Input Size:** 400 lines (security-auditor workflow)
- **Output:** Voting implementation (~250 lines)
- **Dependencies:** Task 4.3 (hybrid models reduce voting cost overhead)
- **Estimated Tokens:** 38,000
- **Estimated Cost:** $0.57
- **Actions:**
  1. Implement N=3 self-consistency for security-auditor CRITICAL findings
  2. Run 3 independent analyses with different random seeds
  3. Take majority vote on severity classification
  4. Accept 3-5× token cost for high-stakes decisions
  5. Measure accuracy improvement (track false positive reduction)
  6. Generate report: `.ignorar/production-reports/self-consistency-deployment.md`

### Task 4.5: Formalize Role-Based Prompting (M08 - LOW, Impact 6/10)
- **Finding:** Agents have names but unclear if role preserved across turns
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple prompt template updates
- **max_turns:** 12
- **Input Size:** 400 lines (all agent prompts)
- **Output:** Updated prompts with role definitions (~450 lines)
- **Dependencies:** None
- **Estimated Tokens:** 10,000
- **Estimated Cost:** $0.04
- **Actions:**
  1. Add role definitions to system prompts (50-100 tokens each):
     - "You are a Python best practices enforcer specializing in type hints and Pydantic v2"
     - "You are a security auditor focused on OWASP Top 10 vulnerabilities"
  2. Add role reinforcement in multi-turn conversations
  3. Measure quality improvement via user feedback
  4. Generate report: `.ignorar/production-reports/role-based-prompting.md`

### Task 4.6: Optimize Long Context Usage (M09 - LOW, Impact 5/10)
- **Finding:** No measurement of context usage; >200K costs 2× base rate
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple monitoring + alerting
- **max_turns:** 10
- **Input Size:** 200 lines (session logs)
- **Output:** Context monitoring script (~150 lines)
- **Dependencies:** None
- **Estimated Tokens:** 8,000
- **Estimated Cost:** $0.03
- **Actions:**
  1. Implement context tracking per session
  2. Identify high-context agents (>200K threshold)
  3. Add pruning strategies (clear between phases)
  4. Alert if approaching 200K
  5. Generate report: `.ignorar/production-reports/context-optimization.md`

### Task 4.7: Expand Tool Descriptions to 150 Tokens (M11 - MEDIUM)
- **Finding:** Tool descriptions may be too brief; 150 tokens recommended
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires synthesis of examples + failure modes
- **max_turns:** 15
- **Input Size:** 600 lines (agent-tool-schemas.md)
- **Output:** Expanded tool descriptions (~800 lines)
- **Dependencies:** Phase 2 Task 2.2 (schemas deployed)
- **Estimated Tokens:** 32,000
- **Estimated Cost:** $0.48
- **Actions:**
  1. Audit all tool descriptions in agent-tool-schemas.md
  2. Expand to ~150 tokens each:
     - Add examples
     - Document constraints
     - List failure modes
  3. Measure retry reduction (expect -20% tool misuse)
  4. Generate report: `.ignorar/production-reports/tool-description-expansion.md`

### Task 4.8: Enable Parallel Tool Calling (M12 - MEDIUM)
- **Finding:** Unclear if agents invoke multiple tools in single API call
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple prompt updates + validation
- **max_turns:** 10
- **Input Size:** 300 lines (agent prompts)
- **Output:** Updated prompts (~320 lines)
- **Dependencies:** None
- **Estimated Tokens:** 9,000
- **Estimated Cost:** $0.04
- **Actions:**
  1. Update agent prompts: "When tools are independent, invoke them simultaneously"
  2. Add examples of parallel tool calls
  3. Validate with API logs (check for multi-tool requests)
  4. Measure latency improvement (expect 6× faster for 6 tools)
  5. Generate report: `.ignorar/production-reports/parallel-tool-calling.md`

### Phase 4 Context Budget
| Task | Agent Type | Model | Input (lines) | Output (lines) | Est. Tokens | Est. Cost |
|------|------------|-------|---------------|----------------|-------------|-----------|
| 4.1  | code-implementer | Sonnet | 600 | 350 | 40,000 | $0.60 |
| 4.2  | general-purpose | Sonnet | 500 | 550 | 30,000 | $0.45 |
| 4.3  | code-implementer | Sonnet | 800 | 500 | 50,000 | $0.75 |
| 4.4  | code-implementer | Sonnet | 400 | 250 | 38,000 | $0.57 |
| 4.5  | general-purpose | Haiku | 400 | 450 | 10,000 | $0.04 |
| 4.6  | general-purpose | Haiku | 200 | 150 | 8,000 | $0.03 |
| 4.7  | general-purpose | Sonnet | 600 | 800 | 32,000 | $0.48 |
| 4.8  | general-purpose | Haiku | 300 | 320 | 9,000 | $0.04 |
| **Total** | - | - | **4,200** | **3,370** | **217,000** | **$2.96** |

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

## Phase 5: Polish and Validation (Weeks 9-10)

**Goal:** Fix remaining issues, evaluate MCP Apps, audit over-prompting, validate SOTA 10/10
**Total Estimated Time:** 2 weeks
**Total Estimated Cost:** $40-60 in tokens

### Task 5.1: Audit and Remove Over-Prompting Language (W01 - MEDIUM)
- **Finding:** Unknown if "CRITICAL: ALWAYS" language present; Opus 4.6 more responsive without it
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires pattern analysis + rewriting across many files
- **max_turns:** 18
- **Input Size:** 2,000 lines (all `.claude/` files, agent prompts)
- **Output:** Updated files with adaptive language (~2,100 lines)
- **Dependencies:** None
- **Estimated Tokens:** 45,000
- **Estimated Cost:** $0.68
- **Actions:**
  1. Grep for "CRITICAL:", "ALWAYS", "MUST", "NEVER" patterns
  2. Replace with adaptive language:
     - "CRITICAL: ALWAYS verify" → "Verify when needed"
     - "MUST consult Context7" → "Consult Context7 for external libraries"
  3. Test agent compliance (ensure no behavioral regression)
  4. Generate report: `.ignorar/production-reports/over-prompting-removal.md`

### Task 5.2: Measure System Prompt Token Budget (W02 - LOW)
- **Finding:** CLAUDE.md optimized but total token count unknown
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple token counting
- **max_turns:** 8
- **Input Size:** 500 lines (CLAUDE.md + workflow docs loaded at session start)
- **Output:** Token measurement report (~50 lines)
- **Dependencies:** Task 5.1 (after over-prompting removal)
- **Estimated Tokens:** 6,000
- **Estimated Cost:** $0.02
- **Actions:**
  1. Measure CLAUDE.md + all referenced docs token count
  2. Compare to Anthropic recommendation (<2,000 tokens)
  3. If >2,000, apply further compression
  4. Generate report: `.ignorar/production-reports/system-prompt-token-audit.md`

### Task 5.3: Evaluate MCP Apps for Interactive Debugging (M06 - LOW, evaluate first)
- **Finding:** Production-ready Feb 2026; interactive debugging UIs
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires research + synthesis of MCP Apps capabilities
- **max_turns:** 15
- **Input Size:** 300 lines (MCP Apps docs, current workflow)
- **Output:** Evaluation report + recommendation (~200 lines)
- **Dependencies:** None (evaluation only, no implementation)
- **Estimated Tokens:** 28,000
- **Estimated Cost:** $0.42
- **Actions:**
  1. Research MCP Apps production readiness (Feb 2026 status)
  2. Evaluate use cases:
     - Interactive verification dashboard
     - Agent debugging UI
     - Real-time monitoring
  3. Assess integration effort vs. benefit
  4. Generate recommendation: `.ignorar/production-reports/mcp-apps-evaluation.md`

### Task 5.4: Evaluate Progressive Tool Discovery (M01 - XL effort, defer vs. evaluate)
- **Finding:** 98.7% token reduction potential (50K → 300 tokens) but requires MCP gateway
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires architectural analysis
- **max_turns:** 20
- **Input Size:** 400 lines (progressive discovery patterns, current tool loading)
- **Output:** Evaluation report + roadmap (~250 lines)
- **Dependencies:** Task 5.3 (MCP Apps evaluation informs gateway design)
- **Estimated Tokens:** 38,000
- **Estimated Cost:** $0.57
- **Actions:**
  1. Analyze current tool loading overhead (~50K tokens estimated)
  2. Design MCP gateway layer for dynamic loading
  3. Estimate implementation effort (1+ week)
  4. Cost-benefit analysis: 98.7% reduction vs. 1 week dev time
  5. Generate roadmap: `.ignorar/production-reports/progressive-discovery-roadmap.md`
  6. **Recommendation:** Defer to Phase 6 (post-SOTA 10/10) unless break-even <2 months

### Task 5.5: Pin Tech Stack Versions (I06 - LOW)
- **Finding:** tech-stack.md missing version constraints (e.g., "Pydantic v2.5+")
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple file updates
- **max_turns:** 8
- **Input Size:** 100 lines (tech-stack.md)
- **Output:** Updated with version pins (~120 lines)
- **Dependencies:** None
- **Estimated Tokens:** 5,000
- **Estimated Cost:** $0.02
- **Actions:**
  1. Add version constraints to tech-stack.md:
     - Pydantic v2.5+
     - httpx 0.24+
     - structlog 23.1+
     - pathlib (stdlib, Python 3.11+)
  2. Reference from hallucination-detector verification criteria
  3. Generate report: `.ignorar/production-reports/version-pinning.md`

### Task 5.6: Validate Adaptive Thinking Budgets (I07 - LOW)
- **Finding:** Adaptive thinking documented but unclear if active
- **Agent:** `general-purpose` (Haiku)
- **Model Justification:** Simple validation check
- **max_turns:** 8
- **Input Size:** 200 lines (agent configs, API logs)
- **Output:** Validation report (~50 lines)
- **Dependencies:** None
- **Estimated Tokens:** 6,000
- **Estimated Cost:** $0.02
- **Actions:**
  1. Verify adaptive thinking enabled for Opus 4.6 agents
  2. Check API logs for auto-decide vs. fixed extended thinking
  3. Confirm no extended_thinking overrides in agent configs
  4. Generate report: `.ignorar/production-reports/adaptive-thinking-validation.md`

### Task 5.7: Final SOTA Validation (All 47 Findings Resolved)
- **Finding:** Need to validate all remediations complete and SOTA = 10/10
- **Agent:** `general-purpose` (Sonnet)
- **Model Justification:** Requires comprehensive audit + synthesis
- **max_turns:** 25
- **Input Size:** 3,000 lines (all production reports from Phases 1-5)
- **Output:** Final SOTA validation report (~400 lines)
- **Dependencies:** All Phase 1-5 tasks complete
- **Estimated Tokens:** 60,000
- **Estimated Cost:** $0.90
- **Actions:**
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

### Phase 5 Context Budget
| Task | Agent Type | Model | Input (lines) | Output (lines) | Est. Tokens | Est. Cost |
|------|------------|-------|---------------|----------------|-------------|-----------|
| 5.1  | general-purpose | Sonnet | 2,000 | 2,100 | 45,000 | $0.68 |
| 5.2  | general-purpose | Haiku | 500 | 50 | 6,000 | $0.02 |
| 5.3  | general-purpose | Sonnet | 300 | 200 | 28,000 | $0.42 |
| 5.4  | general-purpose | Sonnet | 400 | 250 | 38,000 | $0.57 |
| 5.5  | general-purpose | Haiku | 100 | 120 | 5,000 | $0.02 |
| 5.6  | general-purpose | Haiku | 200 | 50 | 6,000 | $0.02 |
| 5.7  | general-purpose | Sonnet | 3,000 | 400 | 60,000 | $0.90 |
| **Total** | - | - | **6,500** | **3,170** | **188,000** | **$2.63** |

### Phase 5 Success Criteria
- ✅ All over-prompting language removed (adaptive triggering active)
- ✅ System prompt <2,000 tokens confirmed
- ✅ MCP Apps evaluation complete with recommendation
- ✅ Progressive tool discovery roadmap created (defer to Phase 6)
- ✅ Tech stack versions pinned
- ✅ Adaptive thinking validated for all Opus agents
- ✅ **FINAL VALIDATION:** All 47 findings remediated, SOTA = 10/10 confirmed

## Cost-Effectiveness: Model Selection Per Task

### Model Pricing (Per Million Tokens)
- **Haiku:** $0.40 input / $2.00 output
- **Sonnet 4.5:** $3.00 input / $15.00 output
- **Opus 4.6:** $5.00 input / $25.00 output

### Selection Criteria by Phase

**Phase 1 (Quick Wins):**
- 5/6 tasks use Haiku (simple file ops, text replacement, testing)
- 1/6 uses Sonnet (prompt caching requires synthesis across agents)
- **Rationale:** 83% Haiku usage for maximum ROI on quick wins

**Phase 2 (High-Priority Fixes):**
- 1/5 tasks use Haiku (simple testing)
- 4/5 use Sonnet (code synthesis, multi-file analysis, documentation)
- **Rationale:** 80% Sonnet for quality on foundational fixes

**Phase 3 (Major Enhancements):**
- 2/6 tasks use Haiku (validation, measurement)
- 3/6 use Sonnet (routing logic, optimization, monitoring)
- 1/6 uses Opus (parallel execution requires full project context)
- **Rationale:** Reserve Opus for complex architectural changes only

**Phase 4 (Advanced Features):**
- 3/8 tasks use Haiku (simple prompts, monitoring, validation)
- 4/8 use Sonnet (code synthesis, prompt engineering)
- 1/8 uses Opus (none - all advanced features within Sonnet capability)
- **Rationale:** 62% Haiku+Sonnet, avoiding Opus where possible

**Phase 5 (Polish + Validation):**
- 3/7 tasks use Haiku (measurement, simple audits)
- 4/7 use Sonnet (comprehensive audits, evaluations)
- 0/7 use Opus (validation doesn't require full context)
- **Rationale:** 100% avoid Opus for validation work

### Total Cost Breakdown
| Phase | Haiku Cost | Sonnet Cost | Opus Cost | Phase Total |
|-------|------------|-------------|-----------|-------------|
| Phase 1 | $0.11 | $0.30 | $0.00 | $0.41 |
| Phase 2 | $0.05 | $2.11 | $0.00 | $2.16 |
| Phase 3 | $0.08 | $1.60 | $3.00 | $4.68 |
| Phase 4 | $0.13 | $2.83 | $0.00 | $2.96 |
| Phase 5 | $0.08 | $2.55 | $0.00 | $2.63 |
| **Total** | **$0.45** | **$9.39** | **$3.00** | **$12.84** |

**Grand Total (All Phases):** $12.84 in token costs
**Implementation Time:** 9-10 weeks
**Annual Savings (Post-Implementation):** $4,200/year (validated baseline)
**Break-Even:** <1 month after deployment
**ROI:** 327× first year ($4,200 / $12.84)

## Anti-Compaction Guarantees: Context Budget Table

### Write-First Pattern (MANDATORY)
**Every agent MUST create output file within first 3 turns:**
- Turn 1: Create skeleton with section headers
- Turns 2-5: Read inputs incrementally
- Turns 6+: Fill sections using Edit tool
- **Guarantee:** Partial report on disk > complete analysis lost to compaction

### Context Budget Per Phase

| Phase | Tasks | Total Input (lines) | Total Output (lines) | Est. Tokens | Max Agents | Context Safety |
|-------|-------|---------------------|----------------------|-------------|------------|----------------|
| Phase 1 | 6 | 1,300 | 1,390 | 48,000 | 6 concurrent | ✅ SAFE (24% budget) |
| Phase 2 | 5 | 2,600 | 2,350 | 152,000 | 5 concurrent | ✅ SAFE (76% budget) |
| Phase 3 | 6 | 4,100 | 2,400 | 242,000 | 3 concurrent | ⚠️ HIGH (121% budget)* |
| Phase 4 | 8 | 4,200 | 3,370 | 217,000 | 4 concurrent | ⚠️ HIGH (108% budget)* |
| Phase 5 | 7 | 6,500 | 3,170 | 188,000 | 4 concurrent | ✅ SAFE (94% budget) |

*Budget exceeded: Use agent delegation to isolate context. Each agent has independent 200K budget.

### Anti-Compaction Strategies

**1. Agent Delegation (Phases 3-4)**
- Claude orchestrator delegates to specialized agents
- Each agent has independent 200K context window
- Orchestrator receives only summaries (max 50 lines per agent)
- **Example:** Phase 3 Task 3.1 (120K tokens) runs in isolated code-implementer context

**2. max_turns Limits**
| Agent Type | Simple Tasks | Medium Tasks | Complex Tasks | Max Allowed |
|------------|--------------|--------------|---------------|-------------|
| Haiku | 8-10 turns | 12-15 turns | N/A | 15 turns |
| Sonnet | 12-15 turns | 18-22 turns | 25 turns | 25 turns |
| Opus | N/A | 20-25 turns | 25 turns | 25 turns |

**3. Input Size Limits**
- Single file read: <3,000 lines (if larger, use digest agent first)
- Multi-file analysis: <5,000 lines total (split into sub-agents if exceeded)
- **Validation:** Pre-task grep to estimate input size before delegation

**4. Output Persistence**
- All agents write reports to `.ignorar/production-reports/`
- Orchestrator reads reports AFTER agent completes (not streamed)
- Reports stay on disk (never compacted)
- **Format:** Markdown with structured sections for easy re-ingestion

**5. Incremental Filling (This Agent's Pattern)**
| Turn | Action | Context Growth |
|------|--------|----------------|
| 1 | Write skeleton | +500 tokens |
| 2 | Read gap analysis (424 lines) | +7,000 tokens |
| 3-8 | Edit sections incrementally | +2,000 tokens/turn |
| **Total** | 8 turns | ~20,000 tokens peak |

### Phase 3-4 Mitigation (High Context Risk)

**Phase 3 Task 3.1 (120K tokens, Opus):**
- Delegate to isolated code-implementer agent
- Orchestrator receives 50-line summary only
- Full report persisted to disk
- **Context isolation:** 120K in agent context, 2K in orchestrator context

**Phase 4 Tasks (217K total):**
- Run tasks sequentially (not all at once)
- Use /clear between task groups
- Delegate complex tasks (4.3, 4.4) to isolated agents
- **Batching:** Tasks 4.1-4.2 → /clear → Tasks 4.3-4.4 → /clear → Tasks 4.5-4.8

### Success Metrics
- ✅ Zero context-induced compaction events
- ✅ All agent outputs persisted to disk before turn limit
- ✅ Orchestrator context stays <150K throughout all phases
- ✅ No "partial report lost" incidents

## Execution Architecture: Pure Orchestrator Design

### Core Principle
**Claude (main session) = 100% orchestrator, 0% executor**
- Claude does NOT: read files, write code, run searches, analyze reports, run bash validation
- Claude ONLY: creates teams, defines tasks, spawns agents, tracks completion, coordinates agents

### Orchestration-Only Operations

**1. Team Management**
```
TeamCreate(team_name="phase1-quick-wins", description="Week 1 remediation")
```

**2. Task Definition**
```
TaskCreate(
  subject="Extract verification thresholds",
  description="Read 05-before-commit.md, create .claude/rules/verification-thresholds.md, update references",
  activeForm="Extracting verification thresholds"
)
```

**3. Agent Delegation**
```
Task(
  subagent_type="general-purpose",
  model="haiku",
  max_turns=10,
  team_name="phase1-quick-wins",
  prompt="Extract threshold table from .claude/workflow/05-before-commit.md and create centralized .claude/rules/verification-thresholds.md. Update all references."
)
```

**4. Progress Tracking**
```
TaskUpdate(taskId="1", status="completed")
TaskList()  # Check next available work
```

**5. Agent Coordination**
```
SendMessage(
  type="message",
  recipient="haiku-validator",
  content="Task 1.1 complete, proceed with Task 1.3 (depends on threshold file)",
  summary="Dependency unblocked"
)
```

### Agent Execution Architecture

**All work delegated to specialized agents:**

| Agent Type | Responsibility | Model Default | Tools Available |
|------------|----------------|---------------|-----------------|
| general-purpose | File ops, simple tasks, validation | Haiku/Sonnet | All tools |
| code-implementer | Code synthesis, implementation | Sonnet/Opus | Read, Write, Edit, Context7 MCP, Bash |
| Explore | Codebase search, research | Haiku | Glob, Grep, Read, WebFetch |
| Plan | Architecture design, planning | Sonnet | All except Edit/Write |

### Validation Pattern (100% Delegated)

**Anti-Pattern (orchestrator doing work):**
```
# ❌ WRONG - Orchestrator running bash
Bash(command="ruff check src/")
Read(file_path="src/models/user.py")
# Orchestrator analyzes results ❌
```

**Correct Pattern (pure delegation):**
```
# ✅ CORRECT - Orchestrator delegates
Task(
  subagent_type="general-purpose",
  model="haiku",
  max_turns=8,
  prompt="Run ruff check on src/ and report violations. Save report to .ignorar/production-reports/ruff-validation.md"
)
# Orchestrator reads ONLY the final report summary
```

### Workflow Per Phase

**Phase 1-5 Execution Pattern:**
1. Claude creates team: `TeamCreate(team_name="phaseN-...")`
2. Claude defines all tasks: `TaskCreate(...)` for each task in phase
3. Claude spawns agents with explicit model selection: `Task(subagent_type=..., model=...)`
4. Agents execute and write reports to `.ignorar/production-reports/`
5. Claude tracks completion: `TaskUpdate(status="completed")`
6. Claude reads agent report summaries (NOT full reports, just summaries)
7. Claude coordinates dependencies via `SendMessage`
8. Repeat until phase complete

### Context Isolation Benefits

**Without Pure Orchestration (problematic):**
- Orchestrator reads 4,100 lines in Phase 3 → 242K tokens → compaction risk
- Orchestrator analyzes reports inline → context pollution
- Orchestrator reruns validation → token waste

**With Pure Orchestration (optimal):**
- Orchestrator delegates to agent → agent uses 242K in isolated context
- Orchestrator receives 50-line summary → 2K tokens
- Orchestrator context stays clean → no compaction risk
- **Savings:** 242K → 2K = 99% context reduction per delegation

### Agent Report Structure

**All agents follow this template:**
```markdown
# [Agent Name] Report: [Task Description]
Generated: [timestamp]
Agent: [agent-type] ([model])

## Executive Summary (50 lines max - FOR ORCHESTRATOR)
- Status: PASS/FAIL
- Findings: X total (Y critical, Z high)
- Top 3 Issues: [list]
- Next Steps: [recommendations]

## Detailed Analysis (500+ lines - FOR AUDIT)
[Full technical details...]
```

**Orchestrator reads ONLY Executive Summary section**
**Full report preserved on disk for human audit**

### Success Criteria
- ✅ Zero Bash/Read/Grep/Edit calls in orchestrator (100% delegation)
- ✅ Orchestrator context <50K at all times (vs. 200K limit)
- ✅ All 32 tasks across 5 phases delegated to specialized agents
- ✅ Agent reports follow Executive Summary + Details structure
- ✅ Full traceability: every task → agent ID → report path

## SOTA Scoring: Current → Target Per Category

### Overall Score
- **Current:** 9.2/10
- **Target:** 10.0/10
- **Gap:** 0.8 points

### Category Breakdown

| Category | Current | Target | Gap | Key Remediations |
|----------|---------|--------|-----|------------------|
| **Context Management** | 9.0 | 10.0 | +0.1 | Prompt caching (I01), long context optimization (M09), adaptive thinking (I07) |
| **Cost Efficiency** | 8.5 | 10.0 | +0.15 | Hierarchical routing (M03), batch API (M02), cost claims fixed (I02), hybrid models (M05) |
| **Quality Assurance** | 9.5 | 10.0 | +0.05 | Threshold single source (F01), agent validation (F02), CoT (M07), self-consistency (M04) |
| **Workflow Automation** | 9.5 | 10.0 | +0.05 | Parallel execution (F05), fallback strategies (I05, F08) |
| **Documentation & Traceability** | 9.0 | 10.0 | +0.1 | Broken refs fixed (F03), model selection documented (I03), role-based prompting (M08) |
| **Advanced Features** | 8.0 | 10.0 | +0.2 | Progressive discovery (M01), MCP Apps (M06), tool descriptions (M11), parallel tool calling (M12) |
| **Architecture** | 9.8 | 10.0 | +0.02 | Over-prompting removed (W01), system prompt optimized (W02) |

### Detailed Scoring Matrix

#### 1. Context Management (9.0 → 10.0)
**Current State:**
- ✅ Write-first pattern deployed
- ✅ Report persistence with timestamps
- ✅ Agent isolation via Task delegation
- ⚠️ No prompt caching (Phase 1 Task 1.4)
- ⚠️ No long context monitoring (Phase 4 Task 4.6)

**Target State:**
- ✅ All above +
- ✅ Prompt caching with >50% hit rate
- ✅ Context monitoring <200K threshold
- ✅ Adaptive thinking validated

**Remediation:** Phase 1 (I01), Phase 4 (M09), Phase 5 (I07)

#### 2. Cost Efficiency (8.5 → 10.0)
**Current State:**
- ✅ Phase 3 schemas deployed (-37% tokens)
- ⚠️ All agents use Opus (no hierarchical routing)
- ⚠️ No batch API (missing 50% discount)
- ❌ Cost claims overstated ($20-35k vs. actual $4.2k)

**Target State:**
- ✅ Hierarchical routing (Haiku/Sonnet/Opus) with 53% savings
- ✅ Batch API for verification agents (50% discount)
- ✅ Hybrid models (-26% cost)
- ✅ Accurate cost claims with methodology

**Remediation:** Phase 1 (I02), Phase 2 (I03), Phase 3 (M03), Phase 4 (M02, M05)

#### 3. Quality Assurance (9.5 → 10.0)
**Current State:**
- ✅ 5 verification agents operational
- ✅ 2 strategic checkpoints
- ❌ Thresholds scattered (arbitrary PASS/FAIL risk)
- ⚠️ No agent config validation
- ⚠️ No CoT for complex reasoning

**Target State:**
- ✅ All above +
- ✅ Centralized verification thresholds
- ✅ Agent validation script in pre-commit
- ✅ CoT for security-auditor + hallucination-detector
- ✅ Self-consistency voting for CRITICAL findings

**Remediation:** Phase 1 (F01), Phase 2 (F02), Phase 4 (M07, M04)

#### 4. Workflow Automation (9.5 → 10.0)
**Current State:**
- ✅ Reflexion loop (PRA pattern)
- ✅ 5-agent verification suite
- ❌ Sequential execution (87 min cycles)
- ⚠️ No fallback testing

**Target State:**
- ✅ Parallel execution (Wave 1 + Wave 2 = 10-12 min)
- ✅ Context7 fallback tested with monitoring
- ✅ Schema fallback validated

**Remediation:** Phase 1 (I05), Phase 2 (F08), Phase 3 (F05)

#### 5. Documentation & Traceability (9.0 → 10.0)
**Current State:**
- ✅ 7 workflow files complete
- ✅ Report persistence with structured naming
- ❌ Broken doc reference (placeholder-conventions.md)
- ⚠️ Model selection strategy undocumented
- ⚠️ Threshold refs missing in 04-agents.md

**Target State:**
- ✅ All doc references valid
- ✅ Model selection strategy with decision tree
- ✅ Threshold refs in all workflow docs
- ✅ Role-based prompting formalized

**Remediation:** Phase 1 (F03, F06), Phase 2 (I03), Phase 4 (M08)

#### 6. Advanced Features (8.0 → 10.0)
**Current State:**
- ✅ Context7 MCP integration
- ❌ No progressive tool discovery (50K → 300 tokens potential)
- ❌ No MCP Apps integration
- ⚠️ Tool descriptions may be <150 tokens
- ⚠️ Unclear if parallel tool calling active

**Target State:**
- ✅ Progressive tool discovery roadmap (defer to Phase 6)
- ✅ MCP Apps evaluated
- ✅ Tool descriptions expanded to ~150 tokens
- ✅ Parallel tool calling validated

**Remediation:** Phase 4 (M11, M12), Phase 5 (M01 evaluation, M06 evaluation)

#### 7. Architecture (9.8 → 10.0)
**Current State:**
- ✅ Pure orchestrator design
- ✅ Agent isolation via teams
- ✅ CLAUDE.md <50 lines
- ⚠️ Unknown if over-prompting language present
- ⚠️ System prompt token count unmeasured

**Target State:**
- ✅ No over-prompting language (adaptive triggers)
- ✅ System prompt <2,000 tokens confirmed

**Remediation:** Phase 5 (W01, W02)

### Scoring Milestones

**After Phase 1 (Week 1):** 9.2 → 9.4 (+0.2)
- Context Management: +0.05 (caching)
- Cost Efficiency: +0.05 (claims fixed)
- Quality Assurance: +0.05 (thresholds centralized)
- Documentation: +0.05 (broken refs fixed)

**After Phase 2 (Week 2):** 9.4 → 9.5 (+0.1)
- Quality Assurance: +0.03 (validation script)
- Cost Efficiency: +0.05 (Phase 3 schemas complete)
- Documentation: +0.02 (model selection documented)

**After Phase 3 (Week 4):** 9.5 → 9.6 (+0.1)
- Workflow Automation: +0.05 (parallel execution)
- Cost Efficiency: +0.05 (hierarchical routing)

**After Phase 4 (Week 8):** 9.6 → 9.8 (+0.2)
- Cost Efficiency: +0.05 (batch API + hybrid models)
- Quality Assurance: +0.02 (CoT + self-consistency)
- Advanced Features: +0.1 (tool descriptions + parallel calling)
- Context Management: +0.03 (long context optimization)

**After Phase 5 (Week 10):** 9.8 → 10.0 (+0.2)
- Architecture: +0.02 (over-prompting removed, system prompt optimized)
- Advanced Features: +0.1 (evaluations complete)
- Documentation: +0.03 (all refs fixed, role-based formalized)
- Context Management: +0.02 (adaptive thinking validated)
- Quality Assurance: +0.03 (all validations complete)

## Risk Register

### High-Impact Risks

#### R1: Parallel Execution Deployment Complexity (Phase 3)
- **Probability:** MEDIUM (40%)
- **Impact:** HIGH (blocks -87.5% cycle time improvement)
- **Description:** Wave-based coordination with TaskList + SendMessage is complex; idle state management may have edge cases
- **Mitigation:**
  - Allocate 5 days (not 3) for Task 3.1
  - Use Opus (not Sonnet) for full project context
  - Test with 3 verification cycles before declaring success
  - Fallback: Sequential execution with partial parallelization (Wave 1 only = 50% improvement)
- **Owner:** Phase 3 code-implementer agent
- **Status:** Pre-mitigation

#### R2: Context Budget Overrun in Phase 3-4 (Phase 3-4)
- **Probability:** MEDIUM (35%)
- **Impact:** MEDIUM (compaction risk, partial reports lost)
- **Description:** Phase 3 (242K tokens) and Phase 4 (217K tokens) exceed 200K budget if orchestrator reads full inputs
- **Mitigation:**
  - Enforce write-first pattern (skeleton in turn 1)
  - Use pure orchestrator design (agents work in isolation)
  - Orchestrator reads summaries only (50 lines max)
  - Use /clear between task groups in Phase 4
- **Owner:** Orchestrator (this session's successors)
- **Status:** Mitigation designed (Anti-Compaction Guarantees section)

#### R3: Cost Savings Not Realized (Phase 3-4)
- **Probability:** LOW (20%)
- **Impact:** MEDIUM (53% hierarchical routing savings may be overstated)
- **Description:** Anthropic research shows 53% savings; actual may vary based on task distribution
- **Mitigation:**
  - Validate with 1 week of API logs (Phase 3 Task 3.4)
  - Adjust routing thresholds if savings <40%
  - Document actual vs. projected in cost analysis report
  - Fallback: Batch API (50% discount) compensates if routing underperforms
- **Owner:** Phase 3 validation agent
- **Status:** Validation planned

### Medium-Impact Risks

#### R4: Context7 MCP Unavailability (Phase 1-5)
- **Probability:** LOW (15%)
- **Impact:** MEDIUM (fallback to WebSearch adds latency)
- **Description:** Context7 MCP may have outages or rate limits
- **Mitigation:**
  - Deploy fallback testing (Phase 1 Task 1.6)
  - Add monitoring with <5% fallback rate target
  - Implement 5s timeout → WebSearch with 10s timeout
  - Document degraded mode operation
- **Owner:** Phase 1 validation agent
- **Status:** Mitigation planned

#### R5: Schema Validation Failures (Phase 2)
- **Probability:** LOW (15%)
- **Impact:** MEDIUM (blocks $42/month savings if schemas malformed)
- **Description:** 40 JSON schemas may have syntax errors or missing properties
- **Mitigation:**
  - Create validation script (Phase 2 Task 2.1)
  - Test schema fallback (Phase 2 Task 2.4)
  - Integrate validation into pre-commit hook
  - Graceful degradation to natural language if schema fails
- **Owner:** Phase 2 code-implementer + validation agents
- **Status:** Mitigation planned

#### R6: Agent Validation Script False Positives (Phase 2)
- **Probability:** MEDIUM (30%)
- **Impact:** LOW (pre-commit blocks valid commits)
- **Description:** Validation script may be overly strict or miss edge cases
- **Mitigation:**
  - Start with warnings-only mode (not blocking)
  - Iterate based on 1 week of real usage
  - Add override mechanism for false positives
  - Document validation rules with examples
- **Owner:** Phase 2 code-implementer agent
- **Status:** Mitigation planned

### Low-Impact Risks

#### R7: MCP Apps Not Production-Ready Feb 2026 (Phase 5)
- **Probability:** MEDIUM (40%)
- **Impact:** LOW (deferred evaluation, not blocking SOTA 10/10)
- **Description:** Anthropic timeline may slip; MCP Apps may not be ready
- **Mitigation:**
  - Phase 5 Task 5.3 is evaluation-only (no implementation dependency)
  - Defer to Phase 6 if not ready
  - Alternative: Build custom debugging UI using existing MCP servers
- **Owner:** Phase 5 evaluation agent
- **Status:** Acceptable risk (deferred feature)

#### R8: Progressive Tool Discovery Implementation Effort Underestimated (Phase 5)
- **Probability:** HIGH (60%)
- **Impact:** LOW (deferred to Phase 6, not blocking SOTA 10/10)
- **Description:** MCP gateway implementation may take 2+ weeks (not 1 week)
- **Mitigation:**
  - Phase 5 Task 5.4 is roadmap-only (no implementation)
  - Defer implementation to Phase 6 (post-SOTA 10/10)
  - Document cost-benefit: 98.7% reduction vs. 2-week effort
  - Break-even analysis: if <2 months ROI, prioritize; else defer
- **Owner:** Phase 5 evaluation agent
- **Status:** Acceptable risk (deferred feature)

#### R9: Over-Prompting Removal Causes Behavioral Regression (Phase 5)
- **Probability:** LOW (15%)
- **Impact:** MEDIUM (agents may skip critical steps)
- **Description:** Removing "CRITICAL: ALWAYS" language may reduce compliance
- **Mitigation:**
  - Test agent compliance after language changes (Phase 5 Task 5.1)
  - Keep adaptive triggers: "Verify when needed" instead of removing entirely
  - Rollback if >10% compliance drop
  - Document behavioral changes in report
- **Owner:** Phase 5 audit agent
- **Status:** Mitigation planned

### Risk Summary Table

| Risk ID | Phase | Probability | Impact | Mitigation Status | Owner |
|---------|-------|-------------|--------|-------------------|-------|
| R1 | 3 | MEDIUM (40%) | HIGH | Designed | code-implementer |
| R2 | 3-4 | MEDIUM (35%) | MEDIUM | Designed | Orchestrator |
| R3 | 3-4 | LOW (20%) | MEDIUM | Planned | Validation agent |
| R4 | 1-5 | LOW (15%) | MEDIUM | Planned | Validation agent |
| R5 | 2 | LOW (15%) | MEDIUM | Planned | code-implementer |
| R6 | 2 | MEDIUM (30%) | LOW | Planned | code-implementer |
| R7 | 5 | MEDIUM (40%) | LOW | Acceptable | Evaluation agent |
| R8 | 5 | HIGH (60%) | LOW | Acceptable | Evaluation agent |
| R9 | 5 | LOW (15%) | MEDIUM | Planned | Audit agent |

### Risk Escalation Criteria
- **High-Impact + Medium/High Probability:** Immediate escalation to human
- **Medium-Impact + High Probability:** Weekly status check
- **Low-Impact:** Monitor only, escalate if materialized

## Success Criteria

### Overall Target
**SOTA Score: 9.2/10 → 10.0/10**

Each 0.1 point mapped to specific deliverables:

### 9.2 → 9.3 (Phase 1, Week 1)
- ✅ F01: `.claude/rules/verification-thresholds.md` created and referenced (CRITICAL)
- ✅ F03: Placeholder conventions broken reference fixed (HIGH)
- ✅ F06: Threshold reference added to 04-agents.md (HIGH)

### 9.3 → 9.4 (Phase 1, Week 1)
- ✅ I01: Prompt caching deployed with >50% cache hit rate
- ✅ I02: Cost claims recalibrated to $4.2k/year with methodology
- ✅ I05: Context7 fallback tested with monitoring active

### 9.4 → 9.5 (Phase 2, Week 2)
- ✅ F02: Agent validation script operational + pre-commit integration (HIGH)
- ✅ F04: Phase 3 schemas deployed to all 5 agents (HIGH)
- ✅ F07: code-implementer consultation order enforced (MEDIUM)
- ✅ F08: Schema fallback tested with 100% graceful degradation (MEDIUM)

### 9.5 → 9.6 (Phase 2-3, Weeks 2-4)
- ✅ I03: Model selection strategy documented with decision tree
- ✅ F05: Parallel execution deployed with 10-12 min actual cycles (HIGH)

### 9.6 → 9.7 (Phase 3, Week 4)
- ✅ M03: Hierarchical routing deployed with >40% cost reduction (MEDIUM)
- ✅ I04: Few-shot examples optimized to 1-2 per agent
- ✅ I08: MCP observability dashboard active with <5% fallback rate

### 9.7 → 9.8 (Phase 4, Weeks 5-6)
- ✅ M02: Batch API deployed with 50% cost reduction on verification cycles
- ✅ M07: CoT deployed for security-auditor + hallucination-detector with +15% accuracy
- ✅ M05: Hybrid models deployed with -26% cost measured

### 9.8 → 9.9 (Phase 4, Weeks 7-8)
- ✅ M04: Self-consistency voting active for CRITICAL findings
- ✅ M08: Role-based prompting formalized across all agents
- ✅ M09: Context usage <200K per session (alerting active)
- ✅ M11: Tool descriptions expanded to ~150 tokens with -20% retry reduction
- ✅ M12: Parallel tool calling validated via API logs

### 9.9 → 10.0 (Phase 5, Weeks 9-10)
- ✅ W01: Over-prompting language removed (adaptive triggers active)
- ✅ W02: System prompt <2,000 tokens confirmed
- ✅ M06: MCP Apps evaluation complete with recommendation
- ✅ M01: Progressive tool discovery roadmap created (defer to Phase 6)
- ✅ I06: Tech stack versions pinned
- ✅ I07: Adaptive thinking validated for all Opus agents
- ✅ **FINAL:** All 47 findings remediated, SOTA = 10/10 confirmed via comprehensive audit

### Category-Specific Success Criteria

#### Context Management = 10.0
- ✅ Prompt caching deployed with >50% hit rate (saves 75-90% read costs)
- ✅ Long context monitoring active (alerts if >200K tokens)
- ✅ Adaptive thinking validated for all Opus 4.6 agents
- ✅ Write-first pattern enforced (skeleton in turn 1 for all agents)
- ✅ Zero compaction-induced partial report loss

#### Cost Efficiency = 10.0
- ✅ Hierarchical routing operational (Haiku/Sonnet/Opus) with >40% savings
- ✅ Batch API active for verification agents (50% discount)
- ✅ Hybrid models deployed (-26% cost)
- ✅ Cost claims accurate: $4.2k/year baseline with documented methodology
- ✅ Phase 3 schemas deployed ($42/month savings = $504/year)
- ✅ **Total validated savings:** $4,200/year (baseline) + optimizations

#### Quality Assurance = 10.0
- ✅ Verification thresholds centralized (prevents arbitrary PASS/FAIL)
- ✅ Agent validation script in pre-commit (prevents silent misconfig)
- ✅ CoT deployed for complex agents (+15-25% accuracy)
- ✅ Self-consistency voting for CRITICAL findings (+12-18% accuracy)
- ✅ code-implementer consultation order enforced (Context7 always queried)

#### Workflow Automation = 10.0
- ✅ Parallel execution operational (87 min → 10-12 min = -87.5% cycle time)
- ✅ Context7 fallback tested (<5% fallback rate)
- ✅ Schema fallback validated (100% graceful degradation)
- ✅ 5 verification agents running in 2 waves (Wave 1: 7 min, Wave 2: 5 min)

#### Documentation & Traceability = 10.0
- ✅ All doc references valid (no broken links)
- ✅ Model selection strategy documented with decision tree
- ✅ Threshold refs in all workflow docs (04-agents.md, 05-before-commit.md)
- ✅ Role-based prompting formalized (50-100 tokens per agent)
- ✅ Tech stack versions pinned (prevents drift)

#### Advanced Features = 10.0
- ✅ Tool descriptions expanded to ~150 tokens (-20% retry rate)
- ✅ Parallel tool calling validated (6× latency improvement)
- ✅ MCP Apps evaluation complete (recommendation documented)
- ✅ Progressive tool discovery roadmap (98.7% potential, defer to Phase 6)
- ✅ MCP observability dashboard active

#### Architecture = 10.0
- ✅ No over-prompting language (adaptive triggers only)
- ✅ System prompt <2,000 tokens (vs. typical 3,500)
- ✅ Pure orchestrator design (100% delegation, 0% execution)
- ✅ Agent isolation via teams (independent context windows)

### Validation Methodology

**Phase Completion Checklist (per phase):**
1. All tasks marked `completed` in TaskList
2. All agent reports saved to `.ignorar/production-reports/`
3. All changes pass `/verify` (5 verification agents)
4. All changes committed to git
5. Phase validation report confirms SOTA score increment

**Final Validation (Phase 5 Task 5.7):**
1. Review all 47 findings from gap analysis
2. Validate remediation evidence for each (check production reports)
3. Score each SOTA category (7 categories × 10 points)
4. Calculate overall SOTA score (weighted average)
5. **Pass Criteria:** All categories = 10.0/10.0, overall = 10.0/10.0

### Acceptance Criteria

**Minimum Viable Success (9.8/10):**
- All CRITICAL + HIGH severity issues fixed (1 + 5 = 6 items)
- Parallel execution deployed (-87.5% cycle time)
- Hierarchical routing deployed (>40% cost reduction)
- All documentation complete and accurate

**Target Success (10.0/10):**
- All 47 findings remediated (verified via comprehensive audit)
- All 7 SOTA categories = 10.0/10.0
- Zero open issues in gap analysis
- Full traceability: every finding → remediation → evidence

**Stretch Success (10.0/10 + Phase 6 Ready):**
- Progressive tool discovery implementation started
- MCP Apps integrated (if production-ready)
- Enterprise MCP gateway design complete
- Batch API savings >50% validated with 1 month data

---

## End of Master Remediation Plan

**Total Plan Size:** ~600 lines
**Total Phases:** 5 (9-10 weeks)
**Total Tasks:** 32 (6 + 5 + 6 + 8 + 7)
**Total Estimated Cost:** $12.84 in tokens
**Expected Annual Savings:** $4,200/year
**Expected ROI:** 327× first year
**Target Achievement:** SOTA 10/10
