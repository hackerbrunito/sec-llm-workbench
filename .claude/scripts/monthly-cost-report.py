#!/usr/bin/env python3
"""Monthly Cost Report Generator for META-PROJECT.

Analyzes API usage logs to generate comprehensive monthly cost reports including:
- Model routing distribution (Haiku/Sonnet/Opus percentages)
- Cost per cycle and per agent type
- Token consumption breakdown (input/output split)
- Savings comparison vs all-Opus baseline
- Alert triggers for threshold violations

Usage:
    python .claude/scripts/monthly-cost-report.py
    python .claude/scripts/monthly-cost-report.py --month 2026-02
    python .claude/scripts/monthly-cost-report.py --config custom-config.json
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ModelUsage:
    """Container for per-model usage metrics."""

    name: str
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens (input + output)."""
        return self.input_tokens + self.output_tokens

    @property
    def avg_cost_per_call(self) -> float:
        """Calculate average cost per call."""
        return self.cost_usd / self.calls if self.calls > 0 else 0.0

    @property
    def distribution_pct(self, total_calls: int) -> float:
        """Calculate distribution percentage."""
        return (self.calls / total_calls * 100) if total_calls > 0 else 0.0


@dataclass
class AgentUsage:
    """Container for per-agent usage metrics."""

    name: str
    calls: int = 0
    total_cost: float = 0.0
    model_breakdown: dict[str, int] = field(default_factory=dict)


@dataclass
class CostReport:
    """Comprehensive cost report container."""

    month: str
    total_calls: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    models: dict[str, ModelUsage] = field(default_factory=dict)
    agents: dict[str, AgentUsage] = field(default_factory=dict)
    cycles_analyzed: int = 0


class MonthlyReportGenerator:
    """Generate monthly cost tracking reports."""

    def __init__(self, config_path: Path) -> None:
        """Initialize report generator with configuration.

        Args:
            config_path: Path to cost-tracking-config.json
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.report: CostReport | None = None

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from JSON file.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config is invalid JSON
        """
        if not self.config_path.exists():
            logger.error("config_not_found", path=str(self.config_path))
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            return json.loads(self.config_path.read_text())
        except json.JSONDecodeError as e:
            logger.error("config_parse_error", error=str(e))
            raise

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int
    ) -> float:
        """Calculate cost for a model call.

        Args:
            model: Model name (haiku/sonnet/opus)
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        pricing = self.config["pricing"].get(
            model.lower(), self.config["pricing"]["sonnet"]
        )
        input_cost = (input_tokens / 1_000_000) * pricing["input_per_mtok"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_per_mtok"]
        return input_cost + output_cost

    def _parse_log_entry(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        """Parse a log entry and extract relevant fields.

        Args:
            entry: JSON log entry

        Returns:
            Parsed entry with normalized fields, or None if not relevant
        """
        # Filter for relevant events (API calls with model info)
        if "model" not in entry or "tokens" not in entry:
            return None

        model = entry.get("model", "unknown").lower()
        if model not in ["haiku", "sonnet", "opus"]:
            return None

        tokens = entry.get("tokens", {})
        input_tokens = tokens.get("input", 0)
        output_tokens = tokens.get("output", 0)

        return {
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "agent": entry.get("agent", "unknown"),
            "timestamp": entry.get("timestamp", ""),
        }

    def _scan_logs_for_month(self, month: str) -> list[dict[str, Any]]:
        """Scan all log files for a given month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            List of parsed log entries for the month
        """
        entries = []
        log_paths = self.config["log_paths"]

        # Scan agents logs
        agents_dir = Path(log_paths["agents"])
        if agents_dir.exists():
            for log_file in agents_dir.glob(f"{month}-*.jsonl"):
                entries.extend(self._parse_log_file(log_file))

        # Scan sessions logs
        sessions_dir = Path(log_paths["sessions"])
        if sessions_dir.exists():
            for log_file in sessions_dir.glob(f"{month}-*.jsonl"):
                entries.extend(self._parse_log_file(log_file))

        logger.info(
            "logs_scanned",
            month=month,
            entries_found=len(entries),
            agents_checked=agents_dir.exists(),
            sessions_checked=sessions_dir.exists(),
        )

        return entries

    def _parse_log_file(self, log_path: Path) -> list[dict[str, Any]]:
        """Parse a single JSONL log file.

        Args:
            log_path: Path to log file

        Returns:
            List of parsed entries
        """
        entries = []

        try:
            with log_path.open("r") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        parsed = self._parse_log_entry(entry)
                        if parsed:
                            entries.append(parsed)
                    except json.JSONDecodeError:
                        logger.warning(
                            "log_parse_error",
                            file=str(log_path),
                            line=line_num,
                        )
                        continue
        except IOError as e:
            logger.error("log_read_error", file=str(log_path), error=str(e))

        return entries

    def generate_report(self, month: str) -> CostReport:
        """Generate comprehensive cost report for a month.

        Args:
            month: Month in YYYY-MM format

        Returns:
            CostReport with complete analysis
        """
        logger.info("generating_report", month=month)

        entries = self._scan_logs_for_month(month)

        report = CostReport(month=month)
        report.models = {
            model: ModelUsage(name=model) for model in ["haiku", "sonnet", "opus"]
        }

        for entry in entries:
            model = entry["model"]
            input_tokens = entry["input_tokens"]
            output_tokens = entry["output_tokens"]
            agent = entry["agent"]

            # Calculate cost
            cost = self._calculate_cost(model, input_tokens, output_tokens)

            # Update model metrics
            model_usage = report.models[model]
            model_usage.calls += 1
            model_usage.input_tokens += input_tokens
            model_usage.output_tokens += output_tokens
            model_usage.cost_usd += cost

            # Update agent metrics
            if agent not in report.agents:
                report.agents[agent] = AgentUsage(name=agent)
            agent_usage = report.agents[agent]
            agent_usage.calls += 1
            agent_usage.total_cost += cost
            agent_usage.model_breakdown[model] = (
                agent_usage.model_breakdown.get(model, 0) + 1
            )

            # Update totals
            report.total_calls += 1
            report.total_tokens += input_tokens + output_tokens
            report.total_cost_usd += cost

        self.report = report
        logger.info(
            "report_generated",
            month=month,
            total_calls=report.total_calls,
            total_cost=report.total_cost_usd,
        )

        return report

    def _calculate_opus_baseline(self) -> float:
        """Calculate what cost would be if all calls were Opus.

        Returns:
            Baseline cost in USD
        """
        if not self.report:
            return 0.0

        opus_pricing = self.config["pricing"]["opus"]
        # Assume 70% input, 30% output (typical distribution)
        input_tokens = self.report.total_tokens * 0.7
        output_tokens = self.report.total_tokens * 0.3

        input_cost = (input_tokens / 1_000_000) * opus_pricing["input_per_mtok"]
        output_cost = (output_tokens / 1_000_000) * opus_pricing["output_per_mtok"]

        return input_cost + output_cost

    def _check_alerts(self) -> list[str]:
        """Check if any alert thresholds are exceeded.

        Returns:
            List of alert messages
        """
        if not self.report:
            return []

        alerts = []
        thresholds = self.config["alert_thresholds"]

        # Check monthly cost threshold
        if self.report.total_cost_usd > thresholds["monthly_cost_usd"]:
            alerts.append(
                f"⚠️  MONTHLY COST EXCEEDED: ${self.report.total_cost_usd:.2f} "
                f"(threshold: ${thresholds['monthly_cost_usd']:.2f})"
            )

        # Check Haiku distribution (should be at least 30%)
        if self.report.total_calls > 0:
            haiku_pct = (
                self.report.models["haiku"].calls / self.report.total_calls
            )
            if haiku_pct < thresholds["haiku_distribution_min"]:
                alerts.append(
                    f"⚠️  LOW HAIKU USAGE: {haiku_pct*100:.1f}% "
                    f"(target: >{thresholds['haiku_distribution_min']*100:.0f}%)"
                )

            # Check Opus distribution (should be at most 20%)
            opus_pct = self.report.models["opus"].calls / self.report.total_calls
            if opus_pct > thresholds["opus_distribution_max"]:
                alerts.append(
                    f"⚠️  HIGH OPUS USAGE: {opus_pct*100:.1f}% "
                    f"(target: <{thresholds['opus_distribution_max']*100:.0f}%)"
                )

        return alerts

    def save_markdown_report(self, output_path: Path) -> None:
        """Save report as formatted Markdown file.

        Args:
            output_path: Path to save report
        """
        if not self.report:
            logger.error("no_report_to_save")
            return

        output_path.parent.mkdir(parents=True, exist_ok=True)

        opus_baseline = self._calculate_opus_baseline()
        savings = opus_baseline - self.report.total_cost_usd
        savings_pct = (savings / opus_baseline * 100) if opus_baseline > 0 else 0

        expected = self.config["expected_distribution"]
        alerts = self._check_alerts()

        # Build markdown content
        lines = [
            f"# Monthly Cost Report - {self.report.month}",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## Executive Summary",
            "",
            f"- **Total API Calls:** {self.report.total_calls:,}",
            f"- **Total Tokens:** {self.report.total_tokens:,}",
            f"- **Actual Cost:** ${self.report.total_cost_usd:.2f}",
            f"- **All-Opus Baseline:** ${opus_baseline:.2f}",
            f"- **Savings:** ${savings:.2f} ({savings_pct:.1f}%)",
            "",
        ]

        # Alerts section
        if alerts:
            lines.extend(["## 🚨 Alerts", ""])
            lines.extend([f"- {alert}" for alert in alerts])
            lines.append("")

        # Model distribution
        lines.extend(["## Model Distribution", ""])
        lines.append("| Model | Calls | % | Expected % | Status |")
        lines.append("|-------|------:|--:|----------:|--------|")

        for model in ["haiku", "sonnet", "opus"]:
            usage = self.report.models[model]
            actual_pct = (
                usage.calls / self.report.total_calls * 100
                if self.report.total_calls > 0
                else 0
            )
            expected_pct = expected[model] * 100
            delta = actual_pct - expected_pct
            status = "✅" if abs(delta) < 5 else ("⚠️" if abs(delta) < 10 else "❌")

            lines.append(
                f"| {model.upper()} | {usage.calls:,} | {actual_pct:.1f}% | "
                f"{expected_pct:.1f}% | {status} |"
            )

        lines.append("")

        # Cost breakdown
        lines.extend(["## Cost Breakdown by Model", ""])
        lines.append("| Model | Calls | Input Tokens | Output Tokens | Cost | Avg/Call |")
        lines.append("|-------|------:|-------------:|--------------:|-----:|---------:|")

        for model in ["haiku", "sonnet", "opus"]:
            usage = self.report.models[model]
            lines.append(
                f"| {model.upper()} | {usage.calls:,} | "
                f"{usage.input_tokens:,} | {usage.output_tokens:,} | "
                f"${usage.cost_usd:.2f} | ${usage.avg_cost_per_call:.4f} |"
            )

        lines.append("")

        # Agent breakdown
        if self.report.agents:
            lines.extend(["## Cost by Agent", ""])
            lines.append("| Agent | Calls | Cost | Haiku | Sonnet | Opus |")
            lines.append("|-------|------:|-----:|------:|-------:|-----:|")

            for agent_name in sorted(self.report.agents.keys()):
                agent = self.report.agents[agent_name]
                haiku_calls = agent.model_breakdown.get("haiku", 0)
                sonnet_calls = agent.model_breakdown.get("sonnet", 0)
                opus_calls = agent.model_breakdown.get("opus", 0)

                lines.append(
                    f"| {agent_name} | {agent.calls:,} | ${agent.total_cost:.2f} | "
                    f"{haiku_calls} | {sonnet_calls} | {opus_calls} |"
                )

            lines.append("")

        # Projections
        cycles_per_month = self.config["projection_defaults"]["cycles_per_month"]
        if self.report.total_calls > 0:
            cost_per_cycle = self.report.total_cost_usd / max(
                self.report.total_calls, 1
            )
            monthly_projection = cost_per_cycle * cycles_per_month
            annual_projection = monthly_projection * 12

            lines.extend(
                [
                    "## Monthly Projection (150 cycles/month)",
                    "",
                    f"- **Cost per Cycle:** ${cost_per_cycle:.4f}",
                    f"- **Projected Monthly Cost:** ${monthly_projection:.2f}",
                    f"- **Projected Annual Cost:** ${annual_projection:.2f}",
                    "",
                ]
            )

        # Footer
        lines.extend(
            [
                "---",
                "",
                "**Generated by:** `.claude/scripts/monthly-cost-report.py`",
                "**Configuration:** `.claude/scripts/cost-tracking-config.json`",
                "",
            ]
        )

        output_path.write_text("\n".join(lines))
        logger.info("report_saved", path=str(output_path))


def main() -> int:
    """Main entry point for monthly cost report generator.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = argparse.ArgumentParser(
        description="Generate monthly cost tracking reports for META-PROJECT"
    )
    parser.add_argument(
        "--month",
        type=str,
        help="Month in YYYY-MM format (default: current month)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).parent / "cost-tracking-config.json",
        help="Path to config file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Custom output path for report",
    )

    args = parser.parse_args()

    # Determine month
    month = args.month or datetime.now().strftime("%Y-%m")

    # Initialize generator
    try:
        generator = MonthlyReportGenerator(args.config)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        return 1

    # Generate report
    try:
        report = generator.generate_report(month)
    except Exception as e:
        logger.error("report_generation_failed", error=str(e))
        print(f"❌ Failed to generate report: {e}", file=sys.stderr)
        return 1

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_dir = Path(generator.config["output_directory"])
        output_path = output_dir / f"{month}-cost-report.md"

    # Save report
    try:
        generator.save_markdown_report(output_path)
        print(f"✅ Report saved to: {output_path}")
    except Exception as e:
        logger.error("report_save_failed", error=str(e))
        print(f"❌ Failed to save report: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
