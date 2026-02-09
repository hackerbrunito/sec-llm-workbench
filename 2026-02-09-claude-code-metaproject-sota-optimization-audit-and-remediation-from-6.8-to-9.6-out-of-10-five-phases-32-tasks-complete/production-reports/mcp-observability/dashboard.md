# MCP Observability Dashboard

**Last Updated:** YYYY-MM-DD HH:MM
**Report Period:** Last 24 hours
**Context7 MCP Server:** Production

---

## Current Health Status

| Metric | Value | Status | Threshold |
|--------|-------|--------|-----------|
| Overall Status | 🟢 HEALTHY | ✅ | - |
| Error Rate | 0.0% | ✅ | <5% |
| Fallback Rate | 0.0% | ✅ | <10% |
| P95 Latency | 0ms | ✅ | <5000ms |
| Uptime | 99.9% | ✅ | >99% |

**Quick Health Check:**
```bash
python .claude/scripts/mcp-health-check.py
```

---

## Call Statistics

### Total Calls (24h)

| Call Type | Count | Percentage |
|-----------|-------|------------|
| resolve-library-id | 0 | 0% |
| query-docs | 0 | 0% |
| **Total** | **0** | **100%** |

### Success vs Failure

| Status | Count | Rate |
|--------|-------|------|
| ✅ Successful | 0 | 0% |
| ❌ Failed | 0 | 0% |
| 🔄 Fallback Activated | 0 | 0% |

---

## Latency Metrics

### Response Time Distribution

| Percentile | Latency (ms) | Status |
|------------|--------------|--------|
| Average | 0.00 | ✅ |
| P50 (Median) | 0.00 | ✅ |
| P95 | 0.00 | ✅ |
| P99 | 0.00 | ✅ |
| Max | 0.00 | - |

### Latency by Call Type

| Call Type | Avg (ms) | P95 (ms) | P99 (ms) |
|-----------|----------|----------|----------|
| resolve-library-id | 0.00 | 0.00 | 0.00 |
| query-docs | 0.00 | 0.00 | 0.00 |

**Latency Trend (Last 7 Days):**
```
[Chart placeholder - use mcp-observability.py to generate metrics]
```

---

## Error Rate

### Error Distribution (24h)

| Error Type | Count | Percentage |
|------------|-------|------------|
| Timeout | 0 | 0% |
| Connection Failed | 0 | 0% |
| Invalid Response | 0 | 0% |
| Rate Limited | 0 | 0% |
| Other | 0 | 0% |

### Recent Errors (Last 10)

_No errors recorded in the last 24 hours._

---

## Fallback Activations

### Fallback Events (24h)

| Timestamp | Reason | Call Type | Resolution |
|-----------|--------|-----------|------------|
| - | - | - | - |

**Fallback Rate Trend:**
```
[Chart placeholder - Monitor for >10% fallback rate]
```

### Fallback Reasons

| Reason | Count | Percentage |
|--------|-------|------------|
| Context7 Timeout | 0 | 0% |
| Context7 Error | 0 | 0% |
| Invalid Library | 0 | 0% |
| Rate Limit | 0 | 0% |

---

## Active Alerts

### Current Alerts (0)

_No active alerts. All metrics within thresholds._

### Alert History (Last 24h)

| Timestamp | Alert | Severity | Duration | Resolution |
|-----------|-------|----------|----------|------------|
| - | - | - | - | - |

### Alert Thresholds

| Metric | Warning | Critical | Current |
|--------|---------|----------|---------|
| Fallback Rate | >5% | >10% | 0% ✅ |
| P95 Latency | >3s | >5s | 0ms ✅ |
| Error Rate | >3% | >5% | 0% ✅ |
| Uptime | <99.5% | <99% | 99.9% ✅ |

---

## Top Libraries Queried (24h)

| Library | Queries | Avg Latency | Error Rate |
|---------|---------|-------------|------------|
| httpx | 0 | 0ms | 0% |
| pydantic | 0 | 0ms | 0% |
| structlog | 0 | 0ms | 0% |
| langchain | 0 | 0ms | 0% |
| anthropic | 0 | 0ms | 0% |

---

## Agent Usage Breakdown

### Calls by Agent (24h)

| Agent | Total Calls | Avg Latency | Fallback Rate |
|-------|-------------|-------------|---------------|
| hallucination-detector | 0 | 0ms | 0% |
| code-implementer | 0 | 0ms | 0% |
| best-practices-enforcer | 0 | 0ms | 0% |
| security-auditor | 0 | 0ms | 0% |
| other | 0 | 0ms | 0% |

---

## Recommendations

### Performance Optimization

- [ ] **No action required** - All metrics within healthy ranges
- [ ] Monitor fallback rate trend over next 48h
- [ ] Consider caching frequently queried libraries (httpx, pydantic)

### Reliability Improvements

- [ ] **No issues detected** - System operating normally
- [ ] Review fallback logs if rate exceeds 5%
- [ ] Add retry logic for transient Context7 errors

### Monitoring Enhancements

- [ ] Set up automated alerting for >10% fallback rate
- [ ] Create Grafana dashboard for real-time monitoring
- [ ] Enable detailed logging for Context7 calls >5s latency

---

## How to Generate Metrics

### Run Observability Tool

```bash
# Analyze log file
python .claude/scripts/mcp-observability.py --log-file ~/.claude/logs/mcp-calls.jsonl

# JSON output for automation
python .claude/scripts/mcp-observability.py --log-file ~/.claude/logs/mcp-calls.jsonl --output json

# Analyze specific session
python .claude/scripts/mcp-observability.py --analyze-session 2026-02-08-session-123
```

### Run Health Check

```bash
# Quick health check
python .claude/scripts/mcp-health-check.py

# Test with custom library
python .claude/scripts/mcp-health-check.py --library pydantic

# Automated monitoring (exits 0 if healthy)
python .claude/scripts/mcp-health-check.py --quiet && echo "MCP Healthy" || echo "MCP Degraded"
```

### Log Format

MCP call logs should follow this JSON lines format:

```json
{"timestamp": "2026-02-08T10:30:00Z", "tool": "context7_resolve_library_id", "library": "httpx", "latency_ms": 234, "status": "success"}
{"timestamp": "2026-02-08T10:30:05Z", "tool": "context7_query_docs", "library_id": "/httpx/httpx", "query": "AsyncClient timeout", "latency_ms": 456, "status": "success"}
{"timestamp": "2026-02-08T10:30:10Z", "event": "fallback_activated", "reason": "context7_timeout", "call_type": "query_docs"}
```

---

## References

- **Agent Tool Schemas:** `.claude/rules/agent-tool-schemas.md`
- **Fallback Strategy:** See "Fallback & Observability" section
- **Health Check Script:** `.claude/scripts/mcp-health-check.py`
- **Observability Script:** `.claude/scripts/mcp-observability.py`

---

**Dashboard Version:** 1.0
**Generated by:** MCP Observability Tools
**Next Review:** YYYY-MM-DD
