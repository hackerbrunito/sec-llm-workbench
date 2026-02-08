#!/usr/bin/env python3
"""
Routing Savings Measurement Framework

Analyzes API usage logs to validate hierarchical model routing savings.
Compares actual distribution vs expected (40% Haiku, 50% Sonnet, 10% Opus).

Usage:
    python .claude/scripts/measure-routing-savings.py --log-file ~/.claude/logs/api-calls.jsonl
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import sys
from collections import defaultdict


@dataclass
class ModelMetrics:
    """Container for per-model metrics"""
    name: str
    count: int = 0
    tokens: int = 0
    cost: float = 0.0

    @property
    def avg_cost_per_call(self) -> float:
        return self.cost / self.count if self.count > 0 else 0.0

    @property
    def avg_tokens_per_call(self) -> int:
        return self.tokens // self.count if self.count > 0 else 0


class RoutingSavingsAnalyzer:
    """Analyzes hierarchical routing savings"""

    # 2026 API pricing (dollars per million tokens)
    PRICING = {
        "haiku": {"input": 0.25, "output": 1.25},
        "sonnet": {"input": 3.0, "output": 15.0},
        "opus": {"input": 15.0, "output": 75.0},
    }

    # Expected distribution targets
    EXPECTED_DISTRIBUTION = {
        "haiku": 0.40,
        "sonnet": 0.50,
        "opus": 0.10,
    }

    def __init__(self, log_file: Path) -> None:
        self.log_file = Path(log_file)
        self.metrics: dict[str, ModelMetrics] = {
            model: ModelMetrics(name=model) for model in self.PRICING.keys()
        }
        self.total_cost = 0.0
        self.total_tokens = 0
        self.calls = []

    def load_logs(self) -> None:
        """Load and parse API call logs from JSONL file"""
        if not self.log_file.exists():
            print(f"⚠️  Log file not found: {self.log_file}", file=sys.stderr)
            return

        try:
            with open(self.log_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line)
                        self.calls.append(entry)
                    except json.JSONDecodeError:
                        continue
        except IOError as e:
            print(f"❌ Error reading log file: {e}", file=sys.stderr)

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a call (in dollars)"""
        pricing = self.PRICING.get(model.lower(), self.PRICING["sonnet"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def process_calls(self) -> None:
        """Process loaded calls and accumulate metrics"""
        for call in self.calls:
            model = call.get("model", "unknown").lower()
            if model not in self.metrics:
                continue

            input_tokens = call.get("input_tokens", 0)
            output_tokens = call.get("output_tokens", 0)
            total_tokens = input_tokens + output_tokens

            cost = self.calculate_cost(model, input_tokens, output_tokens)

            metrics = self.metrics[model]
            metrics.count += 1
            metrics.tokens += total_tokens
            metrics.cost += cost

            self.total_cost += cost
            self.total_tokens += total_tokens

    def get_distribution(self) -> dict[str, float]:
        """Get actual distribution by count"""
        total_calls = sum(m.count for m in self.metrics.values())
        if total_calls == 0:
            return {m: 0.0 for m in self.metrics}
        return {m: self.metrics[m].count / total_calls for m in self.metrics}

    def calculate_opus_baseline_cost(self) -> float:
        """Calculate what the cost would be if all calls were Opus"""
        opus_pricing = self.PRICING["opus"]
        input_cost = (self.total_tokens * 0.7 / 1_000_000) * opus_pricing["input"]
        output_cost = (self.total_tokens * 0.3 / 1_000_000) * opus_pricing["output"]
        return input_cost + output_cost

    def report(self) -> None:
        """Print comprehensive analysis report"""
        total_calls = sum(m.count for m in self.metrics.values())

        if total_calls == 0:
            print("❌ No valid log entries found. No data to analyze.")
            return

        print("\n" + "=" * 70)
        print("HIERARCHICAL ROUTING SAVINGS ANALYSIS")
        print("=" * 70)

        print(f"\n📊 SUMMARY")
        print(f"  Total Calls: {total_calls}")
        print(f"  Total Tokens: {self.total_tokens:,}")
        print(f"  Actual Cost: ${self.total_cost:.2f}")

        opus_baseline = self.calculate_opus_baseline_cost()
        savings = opus_baseline - self.total_cost
        savings_pct = (savings / opus_baseline * 100) if opus_baseline > 0 else 0

        print(f"  All-Opus Baseline: ${opus_baseline:.2f}")
        print(f"  Savings: ${savings:.2f} ({savings_pct:.1f}%)")

        print(f"\n📈 MODEL DISTRIBUTION")
        dist = self.get_distribution()
        for model in ["haiku", "sonnet", "opus"]:
            expected = self.EXPECTED_DISTRIBUTION[model] * 100
            actual = dist[model] * 100
            status = "✅" if abs(actual - expected) < 5 else "⚠️ "
            print(f"  {status} {model.upper():6} | Expected: {expected:5.1f}% | Actual: {actual:5.1f}%")

        print(f"\n💰 COST BREAKDOWN")
        for model in ["haiku", "sonnet", "opus"]:
            metrics = self.metrics[model]
            pct = (metrics.cost / self.total_cost * 100) if self.total_cost > 0 else 0
            print(
                f"  {model.upper():6} | Calls: {metrics.count:4} | "
                f"Cost: ${metrics.cost:7.2f} ({pct:5.1f}%) | "
                f"Avg: ${metrics.avg_cost_per_call:.4f}/call"
            )

        print(f"\n📋 MONTHLY PROJECTION (150 cycles/month)")
        monthly_cost = self.total_cost * 150 / max(total_calls, 1)
        monthly_baseline = opus_baseline * 150 / max(total_calls, 1)
        monthly_savings = monthly_baseline - monthly_cost
        print(f"  Projected Monthly Cost: ${monthly_cost:.2f}")
        print(f"  All-Opus Monthly Baseline: ${monthly_baseline:.2f}")
        print(f"  Monthly Savings: ${monthly_savings:.2f}")

        print(f"\n📅 ANNUAL PROJECTION")
        annual_cost = monthly_cost * 12
        annual_baseline = monthly_baseline * 12
        annual_savings = monthly_savings * 12
        print(f"  Projected Annual Cost: ${annual_cost:.2f}")
        print(f"  All-Opus Annual Baseline: ${annual_baseline:.2f}")
        print(f"  Annual Savings: ${annual_savings:.2f}")

        print("\n" + "=" * 70)


def main() -> None:
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze hierarchical model routing savings from API logs"
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path.home() / ".claude" / "logs" / "api-calls.jsonl",
        help="Path to JSONL log file with API calls",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )

    args = parser.parse_args()

    analyzer = RoutingSavingsAnalyzer(args.log_file)
    analyzer.load_logs()
    analyzer.process_calls()

    if args.output == "json":
        dist = analyzer.get_distribution()
        print(
            json.dumps(
                {
                    "total_calls": sum(m.count for m in analyzer.metrics.values()),
                    "total_tokens": analyzer.total_tokens,
                    "total_cost": analyzer.total_cost,
                    "opus_baseline_cost": analyzer.calculate_opus_baseline_cost(),
                    "distribution": dist,
                    "metrics": {
                        model: {
                            "count": analyzer.metrics[model].count,
                            "tokens": analyzer.metrics[model].tokens,
                            "cost": analyzer.metrics[model].cost,
                        }
                        for model in analyzer.metrics
                    },
                }
            )
        )
    else:
        analyzer.report()


if __name__ == "__main__":
    main()
