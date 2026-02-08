#!/usr/bin/env python3
"""MCP Observability - Context7 Call Monitoring Utilities.

Tracks Context7 MCP calls for performance and reliability monitoring:
- Call counts (resolve-library-id, query-docs)
- Latency metrics (avg, p95, p99)
- Error rates
- Fallback activation tracking
- Alert thresholds: >10% fallback rate OR >5s p95 latency

Usage:
    python mcp-observability.py --log-file <path> [--output json|summary]
    python mcp-observability.py --analyze-session <session-id>
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Alert thresholds
FALLBACK_RATE_THRESHOLD = 0.10  # 10%
P95_LATENCY_THRESHOLD_MS = 5000  # 5 seconds


@dataclass
class MCPCallMetrics:
    """Metrics for MCP tool calls."""

    total_calls: int = 0
    resolve_library_id_calls: int = 0
    query_docs_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    fallback_activations: int = 0
    latencies_ms: list[float] = field(default_factory=list)

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.failed_calls / self.total_calls) * 100

    @property
    def fallback_rate(self) -> float:
        """Calculate fallback activation rate as percentage."""
        if self.total_calls == 0:
            return 0.0
        return (self.fallback_activations / self.total_calls) * 100

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency in milliseconds."""
        if not self.latencies_ms:
            return 0.0
        return sum(self.latencies_ms) / len(self.latencies_ms)

    @property
    def p95_latency_ms(self) -> float:
        """Calculate p95 latency in milliseconds."""
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def p99_latency_ms(self) -> float:
        """Calculate p99 latency in milliseconds."""
        if not self.latencies_ms:
            return 0.0
        sorted_latencies = sorted(self.latencies_ms)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]


@dataclass
class AlertStatus:
    """Alert status for MCP observability."""

    high_fallback_rate: bool = False
    high_p95_latency: bool = False
    alerts: list[str] = field(default_factory=list)

    def add_alert(self, message: str) -> None:
        """Add an alert message."""
        self.alerts.append(message)


def parse_log_file(log_path: Path) -> MCPCallMetrics:
    """Parse log file to extract MCP call metrics.

    Expected log format (JSON lines):
        {"timestamp": "...", "tool": "context7_resolve_library_id", "latency_ms": 234, "status": "success"}
        {"timestamp": "...", "tool": "context7_query_docs", "latency_ms": 456, "status": "error"}
        {"timestamp": "...", "event": "fallback_activated", "reason": "context7_timeout"}

    Args:
        log_path: Path to log file containing MCP call data

    Returns:
        MCPCallMetrics with aggregated statistics
    """
    metrics = MCPCallMetrics()

    if not log_path.exists():
        return metrics

    with log_path.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Handle tool call entries
            if "tool" in entry:
                tool = entry.get("tool", "")
                if tool in ("context7_resolve_library_id", "mcp__context7__resolve-library-id"):
                    metrics.resolve_library_id_calls += 1
                    metrics.total_calls += 1
                elif tool in ("context7_query_docs", "mcp__context7__query-docs"):
                    metrics.query_docs_calls += 1
                    metrics.total_calls += 1

                # Track success/failure
                status = entry.get("status", "unknown")
                if status == "success":
                    metrics.successful_calls += 1
                elif status in ("error", "failed"):
                    metrics.failed_calls += 1

                # Track latency
                latency_ms = entry.get("latency_ms")
                if latency_ms is not None:
                    metrics.latencies_ms.append(float(latency_ms))

            # Handle fallback activation events
            elif entry.get("event") == "fallback_activated":
                metrics.fallback_activations += 1

    return metrics


def check_alerts(metrics: MCPCallMetrics) -> AlertStatus:
    """Check if any alert thresholds are exceeded.

    Args:
        metrics: MCP call metrics to evaluate

    Returns:
        AlertStatus with triggered alerts
    """
    status = AlertStatus()

    # Check fallback rate
    if metrics.fallback_rate > (FALLBACK_RATE_THRESHOLD * 100):
        status.high_fallback_rate = True
        status.add_alert(
            f"⚠️  HIGH FALLBACK RATE: {metrics.fallback_rate:.1f}% "
            f"(threshold: {FALLBACK_RATE_THRESHOLD * 100}%)"
        )

    # Check p95 latency
    if metrics.p95_latency_ms > P95_LATENCY_THRESHOLD_MS:
        status.high_p95_latency = True
        status.add_alert(
            f"⚠️  HIGH P95 LATENCY: {metrics.p95_latency_ms:.0f}ms "
            f"(threshold: {P95_LATENCY_THRESHOLD_MS}ms)"
        )

    return status


def generate_json_output(metrics: MCPCallMetrics, alerts: AlertStatus) -> str:
    """Generate JSON output with metrics and alerts.

    Args:
        metrics: MCP call metrics
        alerts: Alert status

    Returns:
        JSON string with formatted output
    """
    output = {
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_calls": metrics.total_calls,
            "resolve_library_id_calls": metrics.resolve_library_id_calls,
            "query_docs_calls": metrics.query_docs_calls,
            "successful_calls": metrics.successful_calls,
            "failed_calls": metrics.failed_calls,
            "fallback_activations": metrics.fallback_activations,
            "error_rate_percent": round(metrics.error_rate, 2),
            "fallback_rate_percent": round(metrics.fallback_rate, 2),
            "latency": {
                "avg_ms": round(metrics.avg_latency_ms, 2),
                "p95_ms": round(metrics.p95_latency_ms, 2),
                "p99_ms": round(metrics.p99_latency_ms, 2),
            },
        },
        "alerts": {
            "high_fallback_rate": alerts.high_fallback_rate,
            "high_p95_latency": alerts.high_p95_latency,
            "messages": alerts.alerts,
        },
    }
    return json.dumps(output, indent=2)


def generate_summary_output(metrics: MCPCallMetrics, alerts: AlertStatus) -> str:
    """Generate human-readable summary output.

    Args:
        metrics: MCP call metrics
        alerts: Alert status

    Returns:
        Formatted summary string
    """
    lines = [
        "=" * 60,
        "MCP OBSERVABILITY SUMMARY",
        "=" * 60,
        "",
        "📊 Call Statistics:",
        f"  Total Calls:            {metrics.total_calls}",
        f"  ├─ resolve-library-id:  {metrics.resolve_library_id_calls}",
        f"  └─ query-docs:          {metrics.query_docs_calls}",
        "",
        f"✅ Successful:            {metrics.successful_calls}",
        f"❌ Failed:                {metrics.failed_calls}",
        f"🔄 Fallback Activations:  {metrics.fallback_activations}",
        "",
        "📈 Performance Metrics:",
        f"  Error Rate:             {metrics.error_rate:.2f}%",
        f"  Fallback Rate:          {metrics.fallback_rate:.2f}%",
        f"  Avg Latency:            {metrics.avg_latency_ms:.2f}ms",
        f"  P95 Latency:            {metrics.p95_latency_ms:.2f}ms",
        f"  P99 Latency:            {metrics.p99_latency_ms:.2f}ms",
        "",
    ]

    # Add alerts section
    if alerts.alerts:
        lines.extend(
            [
                "🚨 ALERTS:",
                *[f"  {alert}" for alert in alerts.alerts],
                "",
            ]
        )
    else:
        lines.extend(
            [
                "✅ No alerts - all metrics within thresholds",
                "",
            ]
        )

    lines.extend(
        [
            "=" * 60,
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    """Main entry point for MCP observability tool."""
    parser = argparse.ArgumentParser(
        description="MCP Observability - Monitor Context7 call performance and reliability"
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Path to MCP call log file (JSON lines format)",
    )
    parser.add_argument(
        "--output",
        choices=["json", "summary"],
        default="summary",
        help="Output format (default: summary)",
    )
    parser.add_argument(
        "--analyze-session",
        type=str,
        help="Analyze specific session ID (searches in ~/.claude/logs/)",
    )

    args = parser.parse_args()

    # Determine log file path
    if args.analyze_session:
        # Search for session log in standard location
        log_dir = Path.home() / ".claude" / "logs"
        log_path = log_dir / f"{args.analyze_session}.jsonl"
        if not log_path.exists():
            print(f"❌ Session log not found: {log_path}", file=sys.stderr)
            return 1
    elif args.log_file:
        log_path = args.log_file
    else:
        print("❌ Either --log-file or --analyze-session must be provided", file=sys.stderr)
        parser.print_help()
        return 1

    # Parse log and calculate metrics
    metrics = parse_log_file(log_path)

    # Check for alerts
    alerts = check_alerts(metrics)

    # Generate output
    if args.output == "json":
        print(generate_json_output(metrics, alerts))
    else:
        print(generate_summary_output(metrics, alerts))

    # Return non-zero if alerts triggered
    return 1 if alerts.alerts else 0


if __name__ == "__main__":
    sys.exit(main())
