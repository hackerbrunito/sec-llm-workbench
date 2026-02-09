# Phase 4 Real-Time Cost Monitoring System - Technical Design

**Date:** 2026-02-08
**Monitoring Architect:** Phase 4 Wave 2 Monitoring System
**Program:** SIOPV Performance Optimization Program
**Status:** DESIGN COMPLETE - READY FOR IMPLEMENTATION

---

## Executive Summary

This document defines a **real-time cost monitoring system** for Phase 4 Wave 2, designed to track three optimization strategies in production: Prompt Caching (-15-16% tokens), Adaptive Validation (-15-22% tokens), and Model Routing (-5-12% tokens).

The monitoring system provides:
- **Real-time metrics dashboard** tracking token consumption, cost per cycle, and savings breakdown
- **Intelligent alerting** detecting anomalies (>10% token overage, cache hit rate <60%, validation accuracy <85%)
- **Data collection at critical points** (before/after /verify, daily aggregations, weekly trends)
- **Integration with Wave 1 designs** to monitor caching effectiveness, validation accuracy, model quality
- **Rollback triggers** if F1 score drops >5% or cost savings fall below 5%

**Key Metrics:**
- Token consumption per cycle (target: 142-144K, -10-15% from baseline 158.8K)
- Cost per cycle (target: $0.355-0.360, -10-15% from baseline $0.397)
- Cache hit rate (target: >70%)
- Validation classification accuracy (target: >85%)
- Model routing F1 score (target: ≥0.85 per agent)

**Monitoring Requirements for Consolidator:**
Synthesize metrics across 3 optimizations. Provide weekly cost trend analysis, optimization effectiveness comparison, and rollback trigger monitoring. Enable data-driven decisions on Phase 5 continuation.

---

## 1. Metrics Dashboard Design

### 1.1 Dashboard Architecture

**Location:** `.ignorar/dashboards/phase-4-cost-monitoring.html`

**Update Frequency:** Real-time (updated every cycle, ~11 minutes)

**Technology Stack:**
- Backend: Python structlog + JSON append-only log
- Frontend: HTML5 + Chart.js for visualization
- Data source: `.ignorar/monitoring/phase-4/metrics.json`

### 1.2 Primary Metrics (Real-Time Cycle Tracking)

#### Metric 1: Token Consumption Per Cycle

**Display:** Line chart with trend
- X-axis: Cycle number (0-360 per month)
- Y-axis: Tokens (100K-180K range)
- Baseline: 158.8K (orange dashed line)
- Target: 142-144K (green band)
- Actual: Blue line (updates every cycle)

**Formula:**
```
tokens_per_cycle = sum(agent_tokens) for all 5 verification agents
```

**Thresholds:**
- Green: 120K-144K (exceeds target)
- Yellow: 144K-158K (on track)
- Red: >158K (degradation, alert)

**Data Points to Log:**
```json
{
  "cycle_number": 42,
  "timestamp": "2026-02-08T14:30:00Z",
  "tokens_consumed": {
    "best-practices-enforcer": 19450,
    "security-auditor": 31200,
    "hallucination-detector": 28120,
    "code-reviewer": 28950,
    "test-generator": 27350
  },
  "total_tokens": 135070,
  "baseline_tokens": 158800
}
```

#### Metric 2: Cost Per Cycle (USD)

**Display:** Gauge + trend sparkline
- Current cost: $0.338 (vs baseline $0.397)
- Savings: $0.059 per cycle (15%)
- Trend: 7-day moving average

**Formula:**
```
cost_per_cycle = total_tokens / 1_000_000 * 2.50  # Haiku pricing $2.50/1M tokens
```

**Threshold Alert:**
- Alert if cost > $0.437 (10% above baseline)
- Investigate if < $0.300 (unusually low)

**Cost Breakdown:**
```json
{
  "cycle_number": 42,
  "cost_per_cycle": 0.3377,
  "baseline_cost": 0.3970,
  "savings": 0.0593,
  "savings_percentage": 14.9
}
```

#### Metric 3: Savings Breakdown (Stacked Bar Chart)

**Display:** 3-color stacked bar showing contribution from each optimization

Components:
1. **Caching Savings** (purple): Expected 16-24K tokens → 8-12% of total
2. **Validation Savings** (teal): Expected 24-35K tokens → 15-22% of total
3. **Routing Savings** (orange): Expected 8-19K tokens → 5-12% of total

**Formula:**
```
caching_savings = (baseline_tokens - cached_tokens)
validation_savings = (baseline_tokens - validation_optimized_tokens)
routing_savings = (baseline_tokens - routed_tokens)
```

**Data Points to Log:**
```json
{
  "cycle_number": 42,
  "savings_breakdown": {
    "caching": {
      "tokens": 20500,
      "percentage": 12.9
    },
    "adaptive_validation": {
      "tokens": 18500,
      "percentage": 11.7
    },
    "model_routing": {
      "tokens": 6000,
      "percentage": 3.8
    },
    "total_savings_tokens": 45000,
    "total_savings_percentage": 28.4
  }
}
```

#### Metric 4: Daily/Weekly/Monthly Aggregations

**Daily View:**
- Average tokens per cycle (12-30 cycles per day)
- Daily cost (sum of cycles)
- Average cycle time
- Breakdown by agent

**Weekly View:**
- Trend line (7-day moving average)
- Cost trend (baseline vs actual)
- Agent-by-agent comparison
- Alert frequency (how many alerts per week)

**Monthly View:**
- Total month cost ($)
- Savings vs baseline ($)
- ROI (if monitoring cost ~$10/month, savings must exceed)
- Agent ranking (which agents contribute most to savings)

### 1.3 Advanced Metrics (Optimization-Specific Tracking)

#### Metric 5: Cache Hit Rate

**Display:** Progress bar + gauge
- Target: >70% hit rate
- Yellow: 60-70%
- Red: <60%

**Formula:**
```
cache_hit_rate = cache_hits / (cache_hits + cache_misses)
```

**Data Points to Log (per agent):**
```json
{
  "cycle_number": 42,
  "cache_metrics": {
    "best-practices-enforcer": {
      "hits": 1,
      "misses": 0,
      "hit_rate": 1.0
    },
    "security-auditor": {
      "hits": 1,
      "misses": 0,
      "hit_rate": 1.0
    },
    "hallucination-detector": {
      "hits": 1,
      "misses": 0,
      "hit_rate": 1.0
    },
    "code-reviewer": {
      "hits": 1,
      "misses": 0,
      "hit_rate": 1.0
    },
    "test-generator": {
      "hits": 1,
      "misses": 0,
      "hit_rate": 1.0
    },
    "overall_hit_rate": 1.0
  },
  "cache_tokens_saved": 23775
}
```

**Alert Trigger:**
```
IF cache_hit_rate < 0.60:
  ALERT severity=HIGH
  "Cache hit rate degraded: %.1f%%, expected >70%%" % (hit_rate * 100)
  ACTION: Check for agent prompt changes or cache invalidation issues
```

#### Metric 6: Validation Accuracy & Override Rate

**Display:** Dual metric + trend

**Metric 6a: Classification Accuracy**
- Target: >85%
- Formula: `correct_classifications / total_classifications`
- Tracks how often adaptive-validation correctly identifies skip-worthy changes

**Metric 6b: Override Trigger Frequency**
- Target: 5-40% (optimal range where validation catches edge cases)
- Formula: `override_triggers / total_cycles`
- Tracks false negative rate (validation should occasionally miss, triggering override)

**Data Points to Log:**
```json
{
  "cycle_number": 42,
  "validation_metrics": {
    "classification_accuracy": 0.87,
    "accuracy_target": 0.85,
    "override_triggers": 12,
    "total_cycles_tracked": 50,
    "override_trigger_rate": 0.24,
    "override_trigger_target": [0.05, 0.40],
    "false_negative_rate": 0.08,
    "defects_by_category": {
      "type_hints": 0.92,
      "pydantic": 0.85,
      "httpx": 0.88,
      "structlog": 0.86,
      "pathlib": 0.90
    }
  }
}
```

**Alert Triggers:**
```
IF classification_accuracy < 0.85:
  ALERT severity=MEDIUM
  "Validation accuracy degraded: %.1f%%, expected >85%%" % (accuracy * 100)
  ACTION: Review validation rule training data
  
IF override_trigger_rate < 0.05:
  ALERT severity=LOW
  "Validation rules may be too aggressive"
  ACTION: Relax thresholds
  
IF override_trigger_rate > 0.40:
  ALERT severity=LOW
  "Validation rules may be too conservative"
  ACTION: Tighten thresholds
```

#### Metric 7: Model Routing Quality (F1 Score per Agent)

**Display:** 5-agent radar chart + detail table

**Metric 7a: F1 Score per Agent**
- Target: ≥0.85 per agent
- Tracks quality of model selection (Sonnet vs Haiku)
- Green: ≥0.85
- Yellow: 0.80-0.85
- Red: <0.80

**Metric 7b: Token Savings by Agent Model**
- Shows which agents benefit most from Haiku
- Haiku expected 5-12% tokens savings vs Sonnet

**Data Points to Log:**
```json
{
  "cycle_number": 42,
  "routing_metrics": {
    "best-practices-enforcer": {
      "model_used": "haiku",
      "f1_score": 0.88,
      "f1_target": 0.85,
      "token_saving_vs_sonnet": 2100
    },
    "security-auditor": {
      "model_used": "sonnet",
      "f1_score": 0.92,
      "reason_downgrade_not_attempted": "High complexity requires Sonnet"
    },
    "hallucination-detector": {
      "model_used": "haiku",
      "f1_score": 0.86,
      "token_saving_vs_sonnet": 3500
    },
    "code-reviewer": {
      "model_used": "haiku",
      "f1_score": 0.84,
      "f1_warning": "Below target, consider upgrading to Sonnet next cycle"
    },
    "test-generator": {
      "model_used": "haiku",
      "f1_score": 0.87,
      "token_saving_vs_sonnet": 2800
    },
    "overall_f1": 0.875,
    "overall_f1_target": 0.85,
    "total_token_savings_from_routing": 8400
  }
}
```

**Alert Triggers:**
```
IF f1_score[agent] < 0.80:
  ALERT severity=CRITICAL
  "Agent %s routing quality degraded: F1=%.2f, expected >=0.85" % (agent, f1)
  ACTION: Disable Haiku routing for this agent, use Sonnet
  
IF f1_score[agent] drops by >0.05 in single cycle:
  ALERT severity=HIGH
  "Agent %s F1 score dropped sharply: %.2f -> %.2f" % (agent, prev_f1, current_f1)
  ACTION: Review recent code changes, investigate quality regression
```

#### Metric 8: Per-Agent Token Usage Increase Detection

**Display:** 5-color gauge showing which agents are under control

**Formula per agent:**
```
token_increase = (current_tokens - baseline_tokens) / baseline_tokens
```

**Alert Trigger:**
```
IF token_increase[agent] > 0.20:  # >20% increase
  ALERT severity=HIGH
  "Agent %s token usage increased %.1f%%, expected <20%%" % (agent, increase * 100)
  ACTION: Check agent prompt size, run hallucination-detector
```

**Data Points to Log:**
```json
{
  "cycle_number": 42,
  "per_agent_analysis": {
    "best-practices-enforcer": {
      "baseline": 23400,
      "current": 19450,
      "change_percentage": -16.8,
      "status": "green"
    },
    "security-auditor": {
      "baseline": 37400,
      "current": 31200,
      "change_percentage": -16.6,
      "status": "green"
    },
    "hallucination-detector": {
      "baseline": 33400,
      "current": 28120,
      "change_percentage": -15.8,
      "status": "green"
    },
    "code-reviewer": {
      "baseline": 33400,
      "current": 28950,
      "change_percentage": -13.3,
      "status": "green"
    },
    "test-generator": {
      "baseline": 31200,
      "current": 27350,
      "change_percentage": -12.4,
      "status": "green"
    }
  }
}
```

---

## 2. Alerting System Design

### 2.1 Alert Architecture

**Alert Delivery Channels:**
1. **stdout logging** (always enabled)
2. **Slack webhook** (optional, disabled by default)
3. **File log** (`.ignorar/monitoring/phase-4/alerts.log`)

**Alert Levels:**
- **CRITICAL**: Immediate action required (F1 score <0.80, cost >15% above baseline)
- **HIGH**: Investigate within 1 hour (token >20% increase, cache <60%)
- **MEDIUM**: Monitor, no immediate action (validation accuracy <85%, F1 0.80-0.85)
- **LOW**: Information only (override trigger rate outside 5-40%)

### 2.2 Alert Definitions

#### Alert A1: Token Overage Detection

**Trigger:** `total_tokens > baseline_tokens * 1.10` (>10% increase from 158.8K)

**Alert Level:** HIGH

**Message:**
```
[ALERT HIGH] Phase 4 Monitoring - Token Overage Detected
Cycle: 42
Current tokens: 174.68K (baseline: 158.8K)
Overage: +15.88K (+10.0%)
Threshold: <158.8K (+10% = 174.68K)
Action: Investigate agent token consumption breakdown
Breakdown:
  - best-practices-enforcer: 19.45K (-16.8% vs baseline) ✓
  - security-auditor: 31.20K (-16.6% vs baseline) ✓
  - hallucination-detector: 28.12K (-15.8% vs baseline) ✓
  - code-reviewer: 28.95K (-13.3% vs baseline) ⚠ (higher than expected)
  - test-generator: 27.35K (-12.4% vs baseline) ⚠ (higher than expected)
Details: code-reviewer and test-generator consumed more than projected
```

#### Alert A2: Cost Savings Below Target

**Trigger:** `actual_savings < 0.10 * baseline_cost` (savings <10% of baseline)

**Alert Level:** MEDIUM

**Message:**
```
[ALERT MEDIUM] Phase 4 Monitoring - Cost Savings Degraded
Cycle: 42
Baseline cost: $0.397
Current cost: $0.356
Savings: $0.041 (10.3% - BELOW TARGET)
Target savings: >10% (target cost: <$0.357)
Action: Review optimization effectiveness
Possible causes:
  1. Cache hit rate below 70% (check cache metrics)
  2. Validation rules too conservative (few skips)
  3. Model routing degradation (few Haiku uses)
Next step: Run diagnostics on each optimization
```

#### Alert A3: Cache Hit Rate Degradation

**Trigger:** `cache_hit_rate < 0.60` (below 60%)

**Alert Level:** HIGH

**Message:**
```
[ALERT HIGH] Phase 4 Monitoring - Cache Hit Rate Critical
Cycle: 42
Cache hit rate: 52% (target: >70%)
Baseline hit rate: 95%
Degradation: -43%
Affected agents:
  - best-practices-enforcer: 0.60 ⚠
  - security-auditor: 0.48 🔴
  - hallucination-detector: 0.55 ⚠
Action: Check for:
  1. Agent prompt changes (hash-based cache invalidation)
  2. Agent environment differences
  3. Clock drift between cache validation
Recovery: Verify cache manager logic, check timestamps
```

#### Alert A4: Validation Accuracy Below Target

**Trigger:** `classification_accuracy < 0.85` (below 85%)

**Alert Level:** MEDIUM

**Message:**
```
[ALERT MEDIUM] Phase 4 Monitoring - Validation Accuracy Degraded
Cycle: 42
Classification accuracy: 82% (target: >85%)
Baseline accuracy: 90%
Degradation: -8%
Impact: ~2% of changes incorrectly classified (skipped when should verify, or vice versa)
Affected categories:
  - type_hints: 78% accuracy (target: 85%) 🔴
  - pydantic: 83% accuracy (target: 85%) ⚠
  - other: >85% ✓
Action: 
  1. Review type_hints validation rules (likely too aggressive)
  2. Analyze false positives/negatives
  3. Adjust classification thresholds
```

#### Alert A5: Validation Override Rate Out of Range

**Trigger:** 
- `override_trigger_rate < 0.05` OR
- `override_trigger_rate > 0.40`

**Alert Level:** LOW (informational)

**Severity:** LOW (can be ignored, just trend data)

**Message:**
```
[ALERT LOW] Phase 4 Monitoring - Validation Override Rate Outside Target
Cycle: 42
Override trigger rate: 2% (target: 5-40%)
Status: RULES TOO AGGRESSIVE
Impact: Skipping too many cycles, not catching defects
Action (optional): Relax validation thresholds to increase override triggers
Recommendation: Current behavior is conservative, acceptable for safety
```

#### Alert A6: Model Routing F1 Score Degradation

**Trigger:** `f1_score[agent] < 0.80` (below minimum quality threshold)

**Alert Level:** CRITICAL

**Message:**
```
[ALERT CRITICAL] Phase 4 Monitoring - Model Routing Quality Critical
Cycle: 42
Agent: code-reviewer
F1 Score: 0.78 (target: ≥0.85, minimum: ≥0.80)
Status: FAILING
Impact: Haiku model insufficient for this agent, switching to Sonnet
Token cost increase: +2.5K per cycle vs Haiku
Action: IMMEDIATE - Disable Haiku routing for code-reviewer
  1. Update routing config to exclude code-reviewer from Haiku
  2. Next cycle will use Sonnet
  3. Investigate why Haiku quality degraded (model update, prompt change?)
  4. Retest Haiku routing after investigation
Recovery: Update phase-4-monitoring/routing-config.json to exclude agent
```

#### Alert A7: F1 Score Sharp Drop

**Trigger:** `(previous_f1 - current_f1) > 0.05` (>5% drop in single cycle)

**Alert Level:** HIGH

**Message:**
```
[ALERT HIGH] Phase 4 Monitoring - Model Routing Quality Sharp Drop
Cycle: 42
Agent: hallucination-detector
F1 Score: 0.81 (previous: 0.87)
Drop: -0.06 (-6.9%)
Status: UNUSUAL - investigate before next cycle
Possible causes:
  1. Code changes made this cycle (more complex for Haiku)
  2. Model quality degradation
  3. Routing threshold adjusted
Action:
  1. Review code changes in this cycle
  2. Check if complexity increased
  3. Monitor next cycle to confirm trend
  4. If drop persists, escalate to CRITICAL (F1 <0.80)
```

#### Alert A8: Per-Agent Token Increase Spike

**Trigger:** `token_increase[agent] > 0.20` (>20% increase from baseline)

**Alert Level:** HIGH

**Message:**
```
[ALERT HIGH] Phase 4 Monitoring - Agent Token Usage Anomaly
Cycle: 42
Agent: test-generator
Baseline tokens: 31.2K
Current tokens: 38.8K
Increase: +7.6K (+24.4%)
Status: ABOVE TOLERANCE (20%)
Possible causes:
  1. Test code more complex this cycle
  2. Validation skips fewer tests
  3. Agent prompt grew (hallucination detection?)
Action:
  1. Check if code-under-test is more complex
  2. Verify agent prompt unchanged
  3. Run hallucination-detector on test-generator output
  4. If prompt grew, investigate why and reset
```

### 2.3 Alert Filtering & Suppression

**Rules:**
1. Don't alert on first-cycle anomalies (need 2 consecutive failures)
2. Suppress duplicate alerts within 15 minutes
3. Auto-resolve alerts if metric recovers above threshold for 3 cycles
4. Escalate alerts from MEDIUM→HIGH→CRITICAL if persistent >2 days

**Configuration:**
```json
{
  "alerts": {
    "deduplication_window_minutes": 15,
    "consecutive_failures_threshold": 2,
    "auto_resolve_threshold_cycles": 3,
    "escalation_rules": {
      "medium_to_high_days": 2,
      "high_to_critical_days": 1
    }
  }
}
```

---

## 3. Data Collection Architecture

### 3.1 Collection Points

#### Collection Point 1: Pre-/verify Cycle Start

**When:** Before `/verify` skill execution (in hook or skill start)

**What to Log:**
```json
{
  "cycle_id": "cycle_42",
  "cycle_number": 42,
  "timestamp_start": "2026-02-08T14:30:00Z",
  "commit_hash": "abc1234def5678",
  "files_changed": [
    "src/module_a.py",
    "src/module_b.py"
  ],
  "change_categories": [
    "type_hints",
    "pydantic"
  ],
  "skip_decisions": {
    "best-practices-enforcer": false,
    "security-auditor": false,
    "hallucination-detector": true,
    "code-reviewer": false,
    "test-generator": false
  },
  "skip_count": 1,
  "skip_percentage": 20
}
```

**Collection Location:** `.ignorar/monitoring/phase-4/cycle-start.json` (append-only log)

#### Collection Point 2: Post-/verify Cycle End

**When:** After all 5 agents complete and reports generated

**What to Log:**
```json
{
  "cycle_id": "cycle_42",
  "cycle_number": 42,
  "timestamp_end": "2026-02-08T14:41:22Z",
  "cycle_duration_seconds": 682,
  "per_agent_metrics": {
    "best-practices-enforcer": {
      "tokens_consumed": 19450,
      "time_seconds": 142,
      "pass_status": true,
      "issues_found": 0,
      "cache_hit": true
    },
    "security-auditor": {
      "tokens_consumed": 31200,
      "time_seconds": 156,
      "pass_status": true,
      "issues_found": 2,
      "cache_hit": true
    },
    "hallucination-detector": {
      "tokens_consumed": 28120,
      "time_seconds": 148,
      "pass_status": true,
      "issues_found": 0,
      "cache_hit": true
    },
    "code-reviewer": {
      "tokens_consumed": 28950,
      "time_seconds": 144,
      "pass_status": true,
      "issues_found": 1,
      "cache_hit": false
    },
    "test-generator": {
      "tokens_consumed": 27350,
      "time_seconds": 139,
      "pass_status": true,
      "issues_found": 5,
      "cache_hit": true
    }
  },
  "total_tokens": 135070,
  "total_time_seconds": 682,
  "overall_pass": true
}
```

**Collection Location:** `.ignorar/monitoring/phase-4/cycle-end.json` (append-only log)

#### Collection Point 3: Daily Aggregation

**When:** Nightly (00:00 UTC) or after 25th cycle of day

**What to Log:**
```json
{
  "date": "2026-02-08",
  "cycles_run": 22,
  "cycle_range": [21, 42],
  "aggregate_metrics": {
    "total_tokens": "2,971,540",
    "average_tokens_per_cycle": 135070,
    "total_cost": "$7.43",
    "average_cost_per_cycle": 0.3377,
    "total_savings_vs_baseline": "$1.63",
    "total_savings_percentage": 14.9,
    "average_cycle_time_seconds": 682,
    "cycles_passed": 22,
    "cycles_failed": 0,
    "pass_rate": 1.0
  },
  "cache_metrics": {
    "average_hit_rate": 0.95,
    "agents_hit_rate": {
      "best-practices-enforcer": 1.0,
      "security-auditor": 0.95,
      "hallucination-detector": 0.95,
      "code-reviewer": 0.91,
      "test-generator": 0.95
    }
  },
  "validation_metrics": {
    "average_accuracy": 0.87,
    "average_override_rate": 0.18
  },
  "routing_metrics": {
    "average_f1_score": 0.87,
    "agents_using_haiku": 4,
    "agents_using_sonnet": 1
  }
}
```

**Collection Location:** `.ignorar/monitoring/phase-4/daily-aggregate.json`

#### Collection Point 4: Weekly Trend Analysis

**When:** Weekly (every Monday 00:00 UTC)

**What to Log:**
```json
{
  "week_number": 6,
  "date_range": "2026-02-02 to 2026-02-08",
  "cycles_run": 148,
  "trend_analysis": {
    "token_consumption_trend": "DOWN (avg 135K, target 142K)",
    "cost_trend": "DOWN (avg $0.338, target <$0.357)",
    "cost_savings": {
      "week_total": "$51.78",
      "vs_baseline": 16.2,
      "monthly_projection": "$223.05"
    },
    "cache_hit_rate": {
      "average": 0.94,
      "trend": "STABLE",
      "best_agent": "best-practices-enforcer: 1.0",
      "worst_agent": "code-reviewer: 0.88"
    },
    "validation_accuracy": {
      "average": 0.86,
      "trend": "STABLE",
      "category_breakdown": {
        "type_hints": 0.89,
        "pydantic": 0.84,
        "httpx": 0.87,
        "structlog": 0.85,
        "pathlib": 0.89
      }
    },
    "routing_quality": {
      "average_f1": 0.87,
      "trend": "UP",
      "agents_at_risk": []
    },
    "alerts_fired": {
      "critical": 0,
      "high": 2,
      "medium": 3,
      "low": 5,
      "resolved": 8
    }
  }
}
```

**Collection Location:** `.ignorar/monitoring/phase-4/weekly-trend.json`

#### Collection Point 5: Monthly Aggregation

**When:** First day of month (00:00 UTC)

**What to Log:**
```json
{
  "month": "2026-02",
  "cycles_run": 587,
  "date_range": "2026-02-01 to 2026-02-28",
  "summary": {
    "total_cost": "$198.41",
    "baseline_cost": "$232.72",
    "total_savings": "$34.31",
    "savings_percentage": 14.7
  },
  "roi": {
    "optimization_investment": "$45.00",
    "monthly_savings": "$34.31",
    "payback_period_days": 39.1,
    "status": "POSITIVE ROI"
  },
  "optimization_effectiveness": {
    "prompt_caching": {
      "expected_savings": "10-15%",
      "actual_savings": "14.9%",
      "status": "✓ EXCEEDS TARGET"
    },
    "adaptive_validation": {
      "expected_savings": "15-22%",
      "actual_savings": "18.2%",
      "status": "✓ ON TARGET"
    },
    "model_routing": {
      "expected_savings": "5-12%",
      "actual_savings": "8.5%",
      "status": "✓ ON TARGET"
    }
  },
  "agent_ranking_by_contribution": [
    {
      "rank": 1,
      "agent": "security-auditor",
      "tokens_saved": 12400,
      "percentage_of_total": 32.1
    },
    {
      "rank": 2,
      "agent": "hallucination-detector",
      "tokens_saved": 9200,
      "percentage_of_total": 23.8
    },
    {
      "rank": 3,
      "agent": "best-practices-enforcer",
      "tokens_saved": 8100,
      "percentage_of_total": 21.0
    },
    {
      "rank": 4,
      "agent": "test-generator",
      "tokens_saved": 5800,
      "percentage_of_total": 15.0
    },
    {
      "rank": 5,
      "agent": "code-reviewer",
      "tokens_saved": 3700,
      "percentage_of_total": 9.6
    }
  ]
}
```

**Collection Location:** `.ignorar/monitoring/phase-4/monthly-aggregate.json`

### 3.2 Data Storage Format

**Master Metrics File:** `.ignorar/monitoring/phase-4/metrics.json`

**Format:** Append-only JSON log (newline-delimited JSON for streaming)

**Schema:**
```json
{
  "schema_version": "1.0",
  "timestamp": "2026-02-08T14:41:22Z",
  "entry_type": "cycle_complete",
  "cycle_number": 42,
  "data": { ... }
}
```

**File Structure:**
```
.ignorar/
└── monitoring/
    └── phase-4/
        ├── metrics.json           # Master append-only log (all cycles)
        ├── alerts.log             # Alert history
        ├── cycle-start.json       # Per-cycle pre-verify data
        ├── cycle-end.json         # Per-cycle post-verify data
        ├── daily-aggregate.json   # Daily summaries
        ├── weekly-trend.json      # Weekly trends
        └── monthly-aggregate.json # Monthly summaries
```

**Sample metrics.json entry:**
```
{"schema_version":"1.0","timestamp":"2026-02-08T14:30:00Z","entry_type":"cycle_start","cycle_number":42,"commit":"abc1234","files_changed":2,"categories":["type_hints","pydantic"],"skip_count":1}
{"schema_version":"1.0","timestamp":"2026-02-08T14:41:22Z","entry_type":"cycle_complete","cycle_number":42,"tokens":135070,"cost":0.3377,"baseline":158800,"savings":0.0593,"cache_hit_rate":0.95,"validation_accuracy":0.87,"routing_f1":0.87}
```

### 3.3 Data Collection Frequency

| Data Type | Collection Frequency | Latency |
|-----------|---------------------|---------|
| Cycle start | Before /verify | <1 sec |
| Cycle complete | After /verify ends | <5 sec |
| Daily aggregate | Nightly 00:00 UTC | +24 hrs |
| Weekly trend | Every Monday 00:00 UTC | +7 days |
| Monthly summary | 1st of month 00:00 UTC | +30 days |

---

## 4. Integration Points with Wave 1 Designs

### 4.1 Prompt Caching Monitoring

**From Prompt Caching Specialist Report:**
- Expected cache hit rate: 95%+ during cycle, 85-90% session-long
- Expected savings: 16-24K tokens per cycle (10-15% reduction)
- Cache window: 5-10 minutes ephemeral

**Monitoring Integration:**

1. **Collect Cache Metrics:**
   ```python
   # In verify skill, after agent execution:
   cache_stats = cache_manager.get_stats()
   logger.info('cache_metrics', 
       agent=agent_name,
       hits=cache_stats['hits'],
       misses=cache_stats['misses'],
       hit_rate=cache_stats['hit_rate'],
       tokens_saved=cache_stats['tokens_saved']
   )
   ```

2. **Alert on Cache Degradation:**
   - If hit rate drops <60%: HIGH alert
   - Check for: agent prompt changes, cache invalidation logic, clock drift

3. **Track Cache Contribution:**
   - Calculate tokens saved per agent from cache
   - Add to "caching" row in savings breakdown
   - Monitor correlation between cache hits and token reduction

4. **Baseline Measurement (Week 1):**
   - Run 3 cycles with caching disabled
   - Record baseline token consumption (158.8K per cycle)
   - Compare against cached cycles

### 4.2 Adaptive Validation Monitoring

**From Adaptive Validation Specialist Report:**
- Expected accuracy: >85% classification accuracy
- Expected savings: 24-35K tokens (15-22% reduction)
- 6 change categories: type_hints, pydantic, httpx, structlog, pathlib, other

**Monitoring Integration:**

1. **Collect Validation Metrics:**
   ```python
   # In adaptive validation module:
   logger.info('validation_decision',
       category=change_category,
       skip_decision=should_skip,
       confidence=confidence_score,
       correct=was_classification_correct  # Known from fallback pass
   )
   ```

2. **Accuracy Tracking:**
   - Calculate per-category accuracy (6 categories)
   - Track false positive rate (skipped when should verify)
   - Track false negative rate (verified when could skip)

3. **Alert on Accuracy Degradation:**
   - If overall accuracy <85%: MEDIUM alert
   - If per-category accuracy <80%: HIGH alert
   - Identify which categories are failing

4. **Override Trigger Analysis:**
   - Count cycles where fallback verification triggered
   - Target: 5-40% (captures edge cases, not too conservative)
   - If outside range: LOW alert (informational)

5. **Token Savings Attribution:**
   - Calculate skipped cycles count
   - Estimate tokens saved by skips: skipped_cycles × baseline_tokens
   - Add to "adaptive_validation" row in savings breakdown

### 4.3 Model Routing Monitoring

**From Model Routing Analyst Report:**
- Expected F1 score per agent: ≥0.85
- Expected savings: 8-19K tokens (5-12% reduction)
- Models: Haiku (faster, cheaper) vs Sonnet (more capable)

**Monitoring Integration:**

1. **Collect Routing Metrics:**
   ```python
   # In model router:
   logger.info('model_decision',
       agent=agent_name,
       model_selected=model,
       complexity_score=complexity,
       f1_score=expected_quality,
       token_delta_vs_baseline=token_saving
   )
   ```

2. **F1 Score Tracking:**
   - Per-agent F1 score calculation
   - Compare against 0.85 target and 0.80 minimum
   - Track 5-point moving average to smooth noise

3. **Critical Alert Rules:**
   - If F1 <0.80: CRITICAL alert, disable Haiku for agent
   - If F1 drops >0.05 in single cycle: HIGH alert, investigate
   - If F1 0.80-0.85: MEDIUM alert, monitor closely

4. **Haiku vs Sonnet Usage:**
   - Count agents using Haiku vs Sonnet
   - Expected: 4 Haiku, 1 Sonnet (or 5 Haiku if complexity allows)
   - Track if agents upgrade/downgrade between cycles

5. **Token Savings Attribution:**
   - Calculate per-agent token delta (Haiku vs Sonnet)
   - Sum across agents using Haiku
   - Add to "model_routing" row in savings breakdown

### 4.4 Consolidated Tracking

**Dashboard Integration:**

The 3 optimization contributions are tracked separately and summed:

```
Total Savings = Caching Savings + Validation Savings + Routing Savings

Example (Cycle 42):
Caching:     +20.5K tokens (12.9%)
Validation:  +18.5K tokens (11.7%)
Routing:     +6.0K tokens (3.8%)
────────────────────────────────
Total:       +45.0K tokens (28.4%) ← Exceeds individual targets!
```

---

## 5. Implementation Roadmap

### Week 1: Baseline Collection (Feb 8-14)

**Objective:** Establish baseline metrics before Phase 4 deployment

**Tasks:**

1. **Implement Data Collection Points** (2 days)
   - Add hooks to /verify skill to log cycle start/end
   - Implement metrics.json append-only log
   - Add per-agent metrics collection
   - Baseline: Run 3 cycles without optimizations, log baseline tokens (target: 158.8K per cycle)

2. **Baseline Verification** (1 day)
   - Run 10 cycles with unoptimized agents
   - Verify baseline metrics match Phase 3 spec (158.8K tokens per cycle)
   - Establish "normal" cache hit rate (should be 0% without caching enabled)

3. **Dashboard Infrastructure** (2 days)
   - Create `.ignorar/dashboards/phase-4-cost-monitoring.html` skeleton
   - Implement real-time metrics reader (parse metrics.json)
   - Create Chart.js graphs for tokens, cost, savings breakdown
   - Manual refresh only (no auto-update yet)

4. **Alert Framework Setup** (1 day)
   - Implement alert logger to `.ignorar/monitoring/phase-4/alerts.log`
   - Define alert thresholds in config
   - Test alert generation with mock data

**Deliverables:**
- Baseline metrics logged for 10 cycles
- metrics.json contains 10 cycle entries
- Basic HTML dashboard displays metrics
- Alert framework ready for Phase 4 deployment

**Success Criteria:**
- Baseline tokens: 158.8K ± 5K per cycle
- Dashboard shows historical metrics correctly
- Alert system generates well-formatted messages

---

### Week 2: Dashboard & Alerting Live (Feb 15-21)

**Objective:** Deploy Phase 4 optimizations with real-time monitoring

**Tasks:**

1. **Enable Phase 4 Optimizations** (1 day)
   - Enable prompt caching in /verify skill
   - Enable adaptive validation in skip-decision logic
   - Enable model routing in agent invocation
   - Run first optimized cycle, log all metrics

2. **Real-Time Dashboard** (2 days)
   - Add auto-refresh to dashboard (every 5 minutes)
   - Implement Chart.js graphs:
     * Token consumption line chart (baseline + target + actual)
     * Cost per cycle gauge + sparkline
     * Savings breakdown stacked bar
     * Cache hit rate progress bar
   - Add summary cards (current cost, savings, alert count)

3. **Alerting Go-Live** (2 days)
   - Implement alert checks in data collection
   - Set up Slack webhook integration (optional)
   - Test all 8 alert types with Phase 4 metrics
   - Configure alert deduplication & escalation

4. **Daily Aggregation** (1 day)
   - Implement daily summary calculation
   - Create daily-aggregate.json file
   - Display daily trend in dashboard

**Deliverables:**
- Phase 4 optimizations enabled
- Real-time dashboard operational
- Alerts firing correctly for Phase 4 metrics
- Daily aggregations calculated

**Success Criteria:**
- Dashboard updates every 5 minutes
- Token consumption 142-144K per cycle (on target)
- Cache hit rate >70%
- Zero false-positive alerts in first 50 cycles

---

### Week 3: Trend Analysis & Rollback Ready (Feb 22-28)

**Objective:** Establish trends, finalize monitoring, enable rollback if needed

**Tasks:**

1. **Weekly Trend Analysis** (1 day)
   - Implement weekly summary calculation
   - Track trends: tokens, cost, cache hit rate, accuracy
   - Create weekly-trend.json after first week of Phase 4

2. **Optimization Effectiveness Report** (1 day)
   - Compare actual savings vs projected savings
   - Per-optimization breakdown (caching vs validation vs routing)
   - Identify best-performing optimization

3. **Rollback Monitoring Setup** (1 day)
   - Implement rollback trigger checks:
     * F1 score <0.80: Disable Haiku routing for agent
     * Cost savings <5%: Alert team, prepare rollback
     * Cache hit rate <60%: Investigate, consider reverting caching
   - Create rollback procedure documentation
   - Test rollback procedure with single agent

4. **Non-Technical Stakeholder Dashboard** (1 day)
   - Simplify dashboard for non-technical viewers
   - High-level metrics only: Total cost, Monthly savings, ROI
   - Remove detailed agent breakdowns
   - Add monthly projection

**Deliverables:**
- Weekly trend analysis operational
- Rollback triggers defined and monitored
- Simplified dashboard for stakeholders
- Optimization effectiveness comparison

**Success Criteria:**
- Weekly trends align with daily metrics
- No rollback triggered (all optimizations on target)
- Stakeholder dashboard accurate & understandable

---

## 6. Monitoring Requirements for Consolidator

### 6.1 Key Metrics to Synthesize

The **Consolidator** must synthesize metrics across all 3 Wave 1 optimizations:

**Daily Synthesis:**
1. Combine daily costs from each optimization
2. Calculate cumulative daily savings vs baseline
3. Track which optimization is driving most value
4. Monitor for optimization conflicts (one optimization degrading another)

**Weekly Synthesis:**
1. Trend analysis: Are optimizations working better together?
2. Compare actual savings vs Phase 4 targets
3. Early warning detection: Any optimization below 50% of expected savings?
4. Alert threshold review: Are alert thresholds tuned correctly?

**Monthly Synthesis:**
1. ROI validation: Are cost savings exceeding optimization investment?
2. Optimization ranking: Which optimization is most effective?
3. Phase 5 planning: Are there combinations of optimizations that work better?
4. Capacity planning: How many more cycles can we run per day?

### 6.2 Consolidator Data Requirements

**From Monitoring Architect, provide weekly:**

1. **Token Consumption Breakdown**
   ```
   Baseline: 158.8K tokens/cycle
   After Caching: -20.5K (12.9%)
   After Validation: -18.5K (11.7%)
   After Routing: -6.0K (3.8%)
   ────────────────────
   Current: 113.3K tokens/cycle (28.6% reduction)
   Target: 142-144K (need to find extra 28-31K tokens)
   ```
   *Note: This summary shows that combined optimizations may exceed Phase 4 targets. Consolidator must validate.*

2. **Optimization Effectiveness Ranking**
   ```
   1. Adaptive Validation: 18.5K savings (41% of total)
   2. Prompt Caching: 20.5K savings (46% of total)
   3. Model Routing: 6.0K savings (13% of total)
   
   Best ROI: Validation (easiest to implement, high impact)
   Highest Impact: Caching (single largest optimization)
   Risk Profile: Routing (quality depends on model selection)
   ```

3. **Quality Metrics Summary**
   ```
   Caching Quality: Cache hit rate 95% (✓ excellent)
   Validation Quality: Accuracy 87% (✓ on target, 85% required)
   Routing Quality: F1 score 0.87 (✓ on target, 0.85 required)
   
   Conclusion: All 3 optimizations at expected quality levels
   ```

4. **Cost Savings Projection**
   ```
   Daily cost (current): $7.43 (baseline: $8.71)
   Daily savings: $1.28 (14.7%)
   Monthly projection: $28.16 (baseline: $31.23)
   Annual projection: $337.92
   
   At current optimization cost ($45), payback period: 35 days ✓
   ```

5. **Risk Assessment Summary**
   ```
   Critical Risks: NONE (all on target)
   High Risks: NONE
   Medium Risks: Validation override rate (currently 18%, target 5-40%) - within range
   Low Risks: Cache hit rate variance (95% observed vs 70% minimum)
   
   Recommendation: Phase 4 deployment approved, no rollback indicators
   ```

### 6.3 Monitoring Checkpoint Questions for Consolidator

When reviewing monitoring data, Consolidator must answer:

1. **Are all 3 optimizations working together effectively?**
   - Check if combined savings = sum of individual savings
   - If less: optimizations may conflict
   - If more: synergies detected (potential Phase 5 opportunity)

2. **Is any optimization significantly underperforming?**
   - Caching: hit rate <70%?
   - Validation: accuracy <85%?
   - Routing: F1 score <0.85?
   - If yes: investigate and prepare rollback

3. **Are cost savings real and sustained?**
   - Check week-over-week trend
   - If savings declining: investigate degradation
   - If savings increasing: optimization reached peak efficiency

4. **Is monitoring overhead acceptable (<5% of tokens)?**
   - Count logging tokens per cycle
   - Should be <7K tokens (Phase 4 target is 142K+)
   - If exceeds: disable lower-priority metrics

5. **Are alert thresholds calibrated correctly?**
   - Too many false positives: relax thresholds
   - Too few catches real issues: tighten thresholds
   - Target: 1-2 alerts per week, <10% false positive rate

---

## 7. Alert Thresholds & Configuration

### 7.1 Alert Threshold Summary Table

| Alert | Trigger | Level | Action | Escalation |
|-------|---------|-------|--------|------------|
| Token Overage | >158.8K × 1.10 = 174.7K | HIGH | Investigate breakdown | CRITICAL if >20% |
| Cost Degradation | Savings <10% of baseline | MEDIUM | Check optimizations | HIGH if <5% |
| Cache Hit Rate | <60% | HIGH | Check invalidation | CRITICAL if <40% |
| Validation Accuracy | <85% | MEDIUM | Review rules | HIGH if <80% |
| Override Rate | <5% or >40% | LOW | Monitor trend | None (info only) |
| Routing F1 | <0.80 | CRITICAL | Disable Haiku | Immediate rollback |
| F1 Sharp Drop | >5% in 1 cycle | HIGH | Investigate | CRITICAL if continues |
| Agent Token Spike | >20% increase | HIGH | Check code/prompt | CRITICAL if >30% |

---

## 8. Rollback & Contingency Planning

### 8.1 Rollback Triggers

**Automatic Rollback (no human approval needed):**

1. **Model Routing F1 Score <0.80**
   - Trigger: Single agent F1 <0.80
   - Action: Disable Haiku routing for that agent (use Sonnet)
   - Impact: +2-3K tokens per cycle for that agent
   - Recovery: Re-test Haiku routing after investigation

2. **Cache Hit Rate <60% for >3 consecutive cycles**
   - Trigger: Persistent low cache hit rate
   - Action: Disable caching, revert to Phase 3 behavior
   - Impact: +20K tokens per cycle (revert caching savings)
   - Recovery: Investigate cache invalidation logic, re-enable

3. **Overall Cost Savings <5%**
   - Trigger: Combined optimization savings <8K tokens per cycle
   - Action: Pause Phase 4, rollback one optimization at a time
   - Impact: Revert to Phase 3 (159K tokens baseline)
   - Recovery: Investigate which optimization is failing

### 8.2 Manual Rollback Procedures

**If Consolidator decides to rollback:**

1. **Rollback Prompt Caching:**
   ```bash
   # Disable cache in verify skill
   sed -i 's/CACHE_ENABLED = True/CACHE_ENABLED = False/' .claude/skills/verify/SKILL.md
   # Revert to Phase 3 behavior
   git checkout main -- src/orchestrator/cache_manager.py
   # Test with next /verify cycle
   ```

2. **Rollback Adaptive Validation:**
   ```bash
   # Disable skip decisions
   sed -i 's/VALIDATION_SKIP_ENABLED = True/VALIDATION_SKIP_ENABLED = False/' src/orchestrator/adaptive_validation.py
   # All agents run (no skips)
   # Revert to Phase 3 behavior
   ```

3. **Rollback Model Routing:**
   ```bash
   # Force all agents to Sonnet
   sed -i 's/MODEL_ROUTING_ENABLED = True/MODEL_ROUTING_ENABLED = False/' src/orchestrator/model_router.py
   # Revert to Phase 3 behavior
   ```

---

## 9. Implementation Code Examples

### 9.1 Data Collection in Python

```python
# In verify skill or orchestrator
import json
import structlog
from pathlib import Path
from datetime import datetime

logger = structlog.get_logger()

class MetricsCollector:
    def __init__(self):
        self.metrics_dir = Path(".ignorar/monitoring/phase-4")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_log = self.metrics_dir / "metrics.json"
    
    def log_cycle_start(self, cycle_number, commit, files_changed, categories):
        """Log metrics at cycle start"""
        entry = {
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry_type": "cycle_start",
            "cycle_number": cycle_number,
            "commit": commit,
            "files_changed_count": len(files_changed),
            "categories": categories,
            "skip_count": len([c for c in categories if c in ["type_hints", "pydantic"]])
        }
        self._append_metric(entry)
    
    def log_cycle_end(self, cycle_number, per_agent_tokens, cache_stats, validation_accuracy):
        """Log metrics at cycle end"""
        total_tokens = sum(per_agent_tokens.values())
        baseline = 158800
        
        entry = {
            "schema_version": "1.0",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "entry_type": "cycle_complete",
            "cycle_number": cycle_number,
            "tokens_consumed": total_tokens,
            "baseline_tokens": baseline,
            "savings_tokens": baseline - total_tokens,
            "savings_percentage": (baseline - total_tokens) / baseline,
            "cost_per_cycle": total_tokens / 1_000_000 * 2.50,
            "per_agent_tokens": per_agent_tokens,
            "cache_hit_rate": cache_stats.get("hit_rate", 0.0),
            "validation_accuracy": validation_accuracy
        }
        self._append_metric(entry)
    
    def _append_metric(self, entry):
        """Append entry to metrics log (JSON lines format)"""
        with open(self.metrics_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
        logger.info("metric_logged", entry_type=entry.get("entry_type"))

# Usage in verify skill:
collector = MetricsCollector()
collector.log_cycle_start(42, "abc1234", ["src/module_a.py"], ["type_hints"])
# ... run agents ...
collector.log_cycle_end(
    42,
    per_agent_tokens={
        "best-practices-enforcer": 19450,
        "security-auditor": 31200,
        "hallucination-detector": 28120,
        "code-reviewer": 28950,
        "test-generator": 27350
    },
    cache_stats={"hit_rate": 0.95},
    validation_accuracy=0.87
)
```

### 9.2 Alert Checker

```python
class AlertChecker:
    def __init__(self):
        self.alert_log = Path(".ignorar/monitoring/phase-4/alerts.log")
        self.alert_log.parent.mkdir(parents=True, exist_ok=True)
    
    def check_alerts(self, cycle_metrics):
        """Check all alert conditions"""
        alerts = []
        
        # A1: Token Overage
        tokens = cycle_metrics["tokens_consumed"]
        if tokens > 174700:  # 158.8K * 1.10
            alerts.append({
                "level": "HIGH",
                "type": "token_overage",
                "message": f"Token consumption {tokens}K exceeds baseline by 10%",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # A2: Cost Savings Below Target
        savings_pct = cycle_metrics["savings_percentage"]
        if savings_pct < 0.10:
            alerts.append({
                "level": "MEDIUM",
                "type": "cost_savings_low",
                "message": f"Cost savings {savings_pct:.1%} below 10% target",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # A3: Cache Hit Rate
        cache_hit_rate = cycle_metrics.get("cache_hit_rate", 0.0)
        if cache_hit_rate < 0.60:
            alerts.append({
                "level": "HIGH",
                "type": "cache_hit_rate_low",
                "message": f"Cache hit rate {cache_hit_rate:.1%} below 60% target",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Log alerts
        for alert in alerts:
            self._log_alert(alert)
        
        return alerts
    
    def _log_alert(self, alert):
        """Log alert to alerts.log"""
        with open(self.alert_log, "a") as f:
            f.write(json.dumps(alert) + "\n")

# Usage:
checker = AlertChecker()
alerts = checker.check_alerts(cycle_metrics)
for alert in alerts:
    logger.warning(alert["type"], level=alert["level"], message=alert["message"])
```

---

## Conclusion

**Real-Time Monitoring System is READY FOR DEPLOYMENT:**

✅ **Comprehensive Metrics:** Token consumption, cost, savings breakdown, cache hits, validation accuracy, routing quality

✅ **Intelligent Alerting:** 8 alert types covering all Phase 4 optimization targets, with escalation rules

✅ **Multi-Level Data Collection:** Cycle-level, daily, weekly, monthly aggregations for trend analysis

✅ **Wave 1 Integration:** Monitors caching effectiveness, validation accuracy, model routing quality

✅ **Rollback Ready:** Automatic rollback triggers for F1 score <0.80, manual procedures for other optimizations

✅ **Stakeholder Dashboard:** Real-time visualization for technical and non-technical audiences

**Phase 4 Deployment Prerequisites:**
1. Week 1: Baseline metrics established (158.8K tokens per cycle verified)
2. Week 2: All 3 optimizations enabled with real-time monitoring
3. Week 3: Trends analyzed, rollback tested, Consolidator briefed

**Consolidator Synthesis Requirements:**
- Weekly reports combining all 3 optimization metrics
- Cost trend analysis and ROI validation
- Rollback trigger monitoring (F1 score, hit rates, accuracy)
- Phase 5 planning input (optimization synergies, best practices)

**Expected Phase 4 Outcome:**
- Token consumption: 142-144K per cycle (10-15% reduction from 158.8K baseline)
- Monthly cost: ~$198-205 (down from $232)
- Daily capacity: ~35-37 cycles (up from ~30)
- ROI: Break-even in 35-40 days

---

**MONITORING DESIGN - STATUS: READY FOR IMPLEMENTATION**
**Prepared: 2026-02-08**
**Next Steps: Assign code-implementer for Week 1 baseline collection**

