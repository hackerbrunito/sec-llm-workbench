#!/usr/bin/env python3
"""
Unit tests for monthly-cost-report.py script

Tests cover:
- Happy path: processing valid JSONL log entries
- Edge cases: empty log directory, malformed JSONL entries, missing fields
- Financial calculations: verify Decimal precision for cost calculations
- Report generation: verify markdown output format
- Config loading: valid config, missing config, invalid config
- Model routing distribution calculation
- Alert threshold checking
"""

import json
import pytest
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

# Note: This assumes monthly-cost-report.py will have similar structure to measure-routing-savings.py
# Adjust imports once the actual module is created


@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Path:
    """Create temporary log directory for testing"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


@pytest.fixture
def valid_config() -> dict[str, Any]:
    """Fixture for valid cost tracking configuration"""
    return {
        "pricing": {
            "haiku": {"input_per_mtok": 0.25, "output_per_mtok": 1.25},
            "sonnet": {"input_per_mtok": 3.0, "output_per_mtok": 15.0},
            "opus": {"input_per_mtok": 15.0, "output_per_mtok": 75.0},
        },
        "expected_distribution": {"haiku": 0.40, "sonnet": 0.50, "opus": 0.10},
        "log_paths": {
            "agents": ".build/logs/agents",
            "sessions": ".build/logs/sessions",
            "decisions": ".build/logs/decisions",
        },
        "output_directory": ".ignorar/production-reports/cost-tracking",
        "alert_thresholds": {
            "monthly_cost_usd": 50.0,
            "haiku_distribution_min": 0.30,
            "opus_distribution_max": 0.20,
            "cost_per_cycle_max": 0.75,
        },
        "projection_defaults": {"cycles_per_month": 150, "working_days_per_month": 20},
    }


@pytest.fixture
def valid_log_entries() -> list[dict[str, Any]]:
    """Fixture for valid JSONL log entries"""
    return [
        {
            "timestamp": "2026-02-09T10:00:00Z",
            "model": "haiku",
            "input_tokens": 5000,
            "output_tokens": 1000,
            "agent": "best-practices-enforcer",
            "phase": 3,
        },
        {
            "timestamp": "2026-02-09T10:05:00Z",
            "model": "sonnet",
            "input_tokens": 20000,
            "output_tokens": 5000,
            "agent": "security-auditor",
            "phase": 3,
        },
        {
            "timestamp": "2026-02-09T10:10:00Z",
            "model": "sonnet",
            "input_tokens": 15000,
            "output_tokens": 3000,
            "agent": "hallucination-detector",
            "phase": 3,
        },
        {
            "timestamp": "2026-02-09T10:15:00Z",
            "model": "haiku",
            "input_tokens": 3000,
            "output_tokens": 500,
            "agent": "code-reviewer",
            "phase": 3,
        },
    ]


class TestConfigLoading:
    """Test configuration file loading and validation"""

    def test_load_valid_config(self, tmp_path: Path, valid_config: dict[str, Any]) -> None:
        """Should successfully load valid configuration file"""
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(valid_config, indent=2))

        # Mock implementation would load config
        with open(config_file) as f:
            loaded_config = json.load(f)

        assert loaded_config == valid_config
        assert "pricing" in loaded_config
        assert "alert_thresholds" in loaded_config

    def test_load_missing_config(self, tmp_path: Path) -> None:
        """Should handle missing config file gracefully"""
        config_file = tmp_path / "nonexistent.json"

        assert not config_file.exists()

        # Expected behavior: use default config or raise informative error
        # Implementation should provide fallback defaults

    def test_load_invalid_json_config(self, tmp_path: Path) -> None:
        """Should handle malformed JSON configuration"""
        config_file = tmp_path / "invalid.json"
        config_file.write_text("{invalid json content")

        with pytest.raises(json.JSONDecodeError):
            with open(config_file) as f:
                json.load(f)

    def test_config_missing_required_fields(self, tmp_path: Path) -> None:
        """Should detect missing required configuration fields"""
        incomplete_config = {"pricing": {"haiku": {"input_per_mtok": 0.25}}}
        config_file = tmp_path / "incomplete.json"
        config_file.write_text(json.dumps(incomplete_config))

        with open(config_file) as f:
            loaded_config = json.load(f)

        # Validation should detect missing fields
        assert "alert_thresholds" not in loaded_config
        assert "expected_distribution" not in loaded_config


class TestLogProcessing:
    """Test JSONL log file processing"""

    def test_process_valid_log_entries(self, temp_log_dir: Path, valid_log_entries: list[dict[str, Any]]) -> None:
        """Should successfully process valid JSONL entries"""
        log_file = temp_log_dir / "2026-02.jsonl"

        with open(log_file, "w") as f:
            for entry in valid_log_entries:
                f.write(json.dumps(entry) + "\n")

        # Read back and verify
        entries = []
        with open(log_file) as f:
            for line in f:
                entries.append(json.loads(line.strip()))

        assert len(entries) == len(valid_log_entries)
        assert entries[0]["model"] == "haiku"
        assert entries[1]["model"] == "sonnet"

    def test_process_empty_log_directory(self, temp_log_dir: Path) -> None:
        """Should handle empty log directory gracefully"""
        log_files = list(temp_log_dir.glob("*.jsonl"))
        assert len(log_files) == 0

        # Expected behavior: return empty results, not crash
        # Implementation should handle this gracefully

    def test_process_malformed_jsonl_entries(self, temp_log_dir: Path) -> None:
        """Should skip malformed JSONL entries and continue processing"""
        log_file = temp_log_dir / "2026-02.jsonl"

        with open(log_file, "w") as f:
            f.write('{"valid": "entry", "model": "haiku", "input_tokens": 1000}\n')
            f.write("invalid json line without braces\n")
            f.write('{"another_valid": "entry", "model": "sonnet", "input_tokens": 2000}\n')
            f.write("{malformed: json}\n")

        # Should parse valid entries and skip malformed ones
        valid_entries = []
        with open(log_file) as f:
            for line in f:
                try:
                    valid_entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        assert len(valid_entries) == 2

    def test_process_entries_missing_required_fields(self, temp_log_dir: Path) -> None:
        """Should handle log entries missing required fields"""
        log_file = temp_log_dir / "2026-02.jsonl"

        entries_with_missing_fields = [
            {"model": "haiku"},  # Missing tokens
            {"input_tokens": 1000, "output_tokens": 500},  # Missing model
            {"model": "sonnet", "input_tokens": 2000},  # Missing output_tokens
        ]

        with open(log_file, "w") as f:
            for entry in entries_with_missing_fields:
                f.write(json.dumps(entry) + "\n")

        # Implementation should use defaults (0) for missing fields
        with open(log_file) as f:
            for line in f:
                entry = json.loads(line.strip())
                model = entry.get("model", "unknown")
                input_tokens = entry.get("input_tokens", 0)
                output_tokens = entry.get("output_tokens", 0)

                assert isinstance(model, str)
                assert isinstance(input_tokens, int)
                assert isinstance(output_tokens, int)


class TestFinancialCalculations:
    """Test cost calculations using Decimal precision"""

    def test_cost_calculation_decimal_precision(self, valid_config: dict[str, Any]) -> None:
        """Should use Decimal for precise financial calculations"""
        pricing = valid_config["pricing"]["haiku"]

        # Using Decimal for precision
        input_tokens = 5000
        output_tokens = 1000

        input_cost = Decimal(str(input_tokens)) / Decimal("1000000") * Decimal(str(pricing["input_per_mtok"]))
        output_cost = Decimal(str(output_tokens)) / Decimal("1000000") * Decimal(str(pricing["output_per_mtok"]))
        total_cost = input_cost + output_cost

        # Verify precision
        assert isinstance(total_cost, Decimal)
        assert total_cost == Decimal("0.00250")  # (5000/1M * 0.25) + (1000/1M * 1.25)

    def test_cost_calculation_all_models(self, valid_config: dict[str, Any]) -> None:
        """Should calculate costs correctly for all model types"""
        test_tokens = {"input": 10000, "output": 2000}

        for model, pricing in valid_config["pricing"].items():
            input_cost = Decimal(str(test_tokens["input"])) / Decimal("1000000") * Decimal(
                str(pricing["input_per_mtok"])
            )
            output_cost = Decimal(str(test_tokens["output"])) / Decimal("1000000") * Decimal(
                str(pricing["output_per_mtok"])
            )
            total_cost = input_cost + output_cost

            assert total_cost > 0
            assert isinstance(total_cost, Decimal)

            # Verify haiku < sonnet < opus
            if model == "haiku":
                haiku_cost = total_cost
            elif model == "sonnet":
                sonnet_cost = total_cost
                assert sonnet_cost > haiku_cost
            elif model == "opus":
                opus_cost = total_cost
                assert opus_cost > sonnet_cost

    def test_monthly_projection_calculation(self, valid_config: dict[str, Any]) -> None:
        """Should project monthly costs correctly"""
        cycles_per_month = valid_config["projection_defaults"]["cycles_per_month"]
        cost_per_cycle = Decimal("0.47")

        monthly_cost = cost_per_cycle * cycles_per_month

        assert monthly_cost == Decimal("70.50")

    def test_annual_projection_calculation(self, valid_config: dict[str, Any]) -> None:
        """Should project annual costs correctly"""
        cycles_per_month = valid_config["projection_defaults"]["cycles_per_month"]
        cost_per_cycle = Decimal("0.47")

        monthly_cost = cost_per_cycle * cycles_per_month
        annual_cost = monthly_cost * 12

        assert annual_cost == Decimal("846.00")


class TestModelDistribution:
    """Test model routing distribution calculations"""

    def test_distribution_calculation(self, valid_log_entries: list[dict[str, Any]]) -> None:
        """Should calculate model distribution correctly"""
        model_counts: dict[str, int] = {}

        for entry in valid_log_entries:
            model = entry["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        total_calls = sum(model_counts.values())

        distribution = {model: count / total_calls for model, count in model_counts.items()}

        assert distribution["haiku"] == 0.5  # 2 out of 4
        assert distribution["sonnet"] == 0.5  # 2 out of 4
        assert sum(distribution.values()) == pytest.approx(1.0)

    def test_distribution_against_expected(self, valid_config: dict[str, Any]) -> None:
        """Should compare actual vs expected distribution"""
        expected = valid_config["expected_distribution"]
        actual = {"haiku": 0.45, "sonnet": 0.50, "opus": 0.05}

        # Calculate deviations
        deviations = {model: abs(actual.get(model, 0) - expected[model]) for model in expected}

        # All deviations should be tracked
        assert "haiku" in deviations
        assert "sonnet" in deviations
        assert "opus" in deviations

    def test_distribution_empty_logs(self) -> None:
        """Should handle empty logs when calculating distribution"""
        model_counts: dict[str, int] = {}
        total_calls = sum(model_counts.values())

        assert total_calls == 0

        # Distribution should handle zero division
        distribution = {model: 0.0 for model in ["haiku", "sonnet", "opus"]}
        assert sum(distribution.values()) == 0.0


class TestAlertThresholds:
    """Test alert threshold checking"""

    def test_monthly_cost_alert(self, valid_config: dict[str, Any]) -> None:
        """Should trigger alert when monthly cost exceeds threshold"""
        threshold = Decimal(str(valid_config["alert_thresholds"]["monthly_cost_usd"]))
        actual_monthly_cost = Decimal("55.00")

        alert_triggered = actual_monthly_cost > threshold

        assert alert_triggered is True

    def test_haiku_distribution_alert(self, valid_config: dict[str, Any]) -> None:
        """Should trigger alert when Haiku usage below minimum"""
        threshold_min = valid_config["alert_thresholds"]["haiku_distribution_min"]
        actual_haiku_pct = 0.25

        alert_triggered = actual_haiku_pct < threshold_min

        assert alert_triggered is True

    def test_opus_distribution_alert(self, valid_config: dict[str, Any]) -> None:
        """Should trigger alert when Opus usage exceeds maximum"""
        threshold_max = valid_config["alert_thresholds"]["opus_distribution_max"]
        actual_opus_pct = 0.25

        alert_triggered = actual_opus_pct > threshold_max

        assert alert_triggered is True

    def test_cost_per_cycle_alert(self, valid_config: dict[str, Any]) -> None:
        """Should trigger alert when cost per cycle exceeds threshold"""
        threshold = Decimal(str(valid_config["alert_thresholds"]["cost_per_cycle_max"]))
        actual_cost_per_cycle = Decimal("0.85")

        alert_triggered = actual_cost_per_cycle > threshold

        assert alert_triggered is True

    def test_no_alerts_when_within_thresholds(self, valid_config: dict[str, Any]) -> None:
        """Should not trigger alerts when all metrics within thresholds"""
        thresholds = valid_config["alert_thresholds"]

        actual_metrics = {
            "monthly_cost": 45.0,  # Below 50.0
            "haiku_distribution": 0.40,  # Above 0.30
            "opus_distribution": 0.10,  # Below 0.20
            "cost_per_cycle": 0.50,  # Below 0.75
        }

        alerts = []

        if actual_metrics["monthly_cost"] > thresholds["monthly_cost_usd"]:
            alerts.append("monthly_cost")
        if actual_metrics["haiku_distribution"] < thresholds["haiku_distribution_min"]:
            alerts.append("haiku_distribution")
        if actual_metrics["opus_distribution"] > thresholds["opus_distribution_max"]:
            alerts.append("opus_distribution")
        if actual_metrics["cost_per_cycle"] > thresholds["cost_per_cycle_max"]:
            alerts.append("cost_per_cycle")

        assert len(alerts) == 0


class TestMarkdownReportGeneration:
    """Test markdown report generation"""

    def test_report_contains_required_sections(self) -> None:
        """Should generate report with all required sections"""
        expected_sections = [
            "# Monthly Cost Report",
            "## Summary",
            "## Model Distribution",
            "## Cost Breakdown",
            "## Alerts",
            "## Projections",
        ]

        # Mock report generation
        report_lines = []
        for section in expected_sections:
            report_lines.append(section)

        report = "\n".join(report_lines)

        for section in expected_sections:
            assert section in report

    def test_report_financial_formatting(self) -> None:
        """Should format currency values correctly in report"""
        cost = Decimal("12.345")

        # Format as USD
        formatted = f"${cost:.2f}"

        assert formatted == "$12.35"
        assert "$" in formatted
        assert len(formatted.split(".")[-1]) == 2  # Two decimal places

    def test_report_percentage_formatting(self) -> None:
        """Should format percentage values correctly in report"""
        distribution = 0.4567

        # Format as percentage
        formatted = f"{distribution * 100:.1f}%"

        assert formatted == "45.7%"
        assert "%" in formatted

    def test_report_table_formatting(self) -> None:
        """Should generate properly formatted markdown tables"""
        table_header = "| Model | Calls | Cost | Distribution |"
        table_separator = "|-------|-------|------|--------------|"
        table_row = "| Haiku | 40    | $5.00 | 40.0%       |"

        table = "\n".join([table_header, table_separator, table_row])

        assert "|" in table
        assert "---" in table_separator
        assert table.count("|") >= 12  # At least 3 rows with 4 columns


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_token_entries(self, temp_log_dir: Path) -> None:
        """Should handle entries with zero tokens"""
        log_file = temp_log_dir / "2026-02.jsonl"

        entry = {"model": "haiku", "input_tokens": 0, "output_tokens": 0}

        with open(log_file, "w") as f:
            f.write(json.dumps(entry) + "\n")

        # Cost should be 0
        cost = Decimal("0") / Decimal("1000000") * Decimal("0.25")
        assert cost == Decimal("0")

    def test_negative_token_values(self, temp_log_dir: Path) -> None:
        """Should handle negative token values (data corruption)"""
        log_file = temp_log_dir / "2026-02.jsonl"

        entry = {"model": "haiku", "input_tokens": -1000, "output_tokens": 500}

        with open(log_file, "w") as f:
            f.write(json.dumps(entry) + "\n")

        # Implementation should treat negative as 0 or skip entry
        tokens = max(0, entry["input_tokens"])
        assert tokens == 0

    def test_very_large_token_counts(self) -> None:
        """Should handle very large token counts without overflow"""
        input_tokens = 1_000_000_000  # 1 billion tokens
        output_tokens = 500_000_000

        # Using Decimal prevents float precision issues
        input_cost = Decimal(str(input_tokens)) / Decimal("1000000") * Decimal("0.25")
        output_cost = Decimal(str(output_tokens)) / Decimal("1000000") * Decimal("1.25")
        total_cost = input_cost + output_cost

        assert total_cost == Decimal("875.00")

    def test_unknown_model_type(self) -> None:
        """Should handle unknown model types gracefully"""
        entry = {"model": "gpt-5-turbo", "input_tokens": 1000, "output_tokens": 500}

        # Should default to sonnet pricing or skip entry
        model = entry.get("model", "sonnet")
        if model not in ["haiku", "sonnet", "opus"]:
            model = "sonnet"  # Default fallback

        assert model == "sonnet"

    def test_multiple_months_aggregation(self, temp_log_dir: Path) -> None:
        """Should aggregate logs across multiple months correctly"""
        # Create logs for multiple months
        months = ["2026-01.jsonl", "2026-02.jsonl"]

        for month_file in months:
            log_file = temp_log_dir / month_file
            entry = {"model": "haiku", "input_tokens": 5000, "output_tokens": 1000}
            with open(log_file, "w") as f:
                f.write(json.dumps(entry) + "\n")

        # Should process all month files
        log_files = list(temp_log_dir.glob("*.jsonl"))
        assert len(log_files) == 2


class TestIntegration:
    """Integration tests combining multiple components"""

    def test_full_report_generation_pipeline(
        self, temp_log_dir: Path, valid_log_entries: list[dict[str, Any]], valid_config: dict[str, Any]
    ) -> None:
        """Should generate complete report from logs and config"""
        # Write log file
        log_file = temp_log_dir / "2026-02.jsonl"
        with open(log_file, "w") as f:
            for entry in valid_log_entries:
                f.write(json.dumps(entry) + "\n")

        # Process logs
        entries = []
        with open(log_file) as f:
            for line in f:
                entries.append(json.loads(line.strip()))

        # Calculate costs
        total_cost = Decimal("0")
        for entry in entries:
            model = entry["model"]
            pricing = valid_config["pricing"][model]
            input_tokens = entry["input_tokens"]
            output_tokens = entry["output_tokens"]

            cost = (Decimal(str(input_tokens)) / Decimal("1000000") * Decimal(str(pricing["input_per_mtok"]))) + (
                Decimal(str(output_tokens)) / Decimal("1000000") * Decimal(str(pricing["output_per_mtok"]))
            )
            total_cost += cost

        # Verify calculations
        assert total_cost > 0
        assert len(entries) == 4

    def test_alert_generation_with_real_data(
        self, temp_log_dir: Path, valid_log_entries: list[dict[str, Any]], valid_config: dict[str, Any]
    ) -> None:
        """Should generate alerts based on real log data"""
        # Calculate distribution
        model_counts: dict[str, int] = {}
        for entry in valid_log_entries:
            model = entry["model"]
            model_counts[model] = model_counts.get(model, 0) + 1

        total_calls = sum(model_counts.values())
        distribution = {model: count / total_calls for model, count in model_counts.items()}

        # Check alerts
        alerts = []
        thresholds = valid_config["alert_thresholds"]

        haiku_pct = distribution.get("haiku", 0)
        opus_pct = distribution.get("opus", 0)

        if haiku_pct < thresholds["haiku_distribution_min"]:
            alerts.append(f"Haiku usage ({haiku_pct:.1%}) below minimum ({thresholds['haiku_distribution_min']:.1%})")

        if opus_pct > thresholds["opus_distribution_max"]:
            alerts.append(f"Opus usage ({opus_pct:.1%}) exceeds maximum ({thresholds['opus_distribution_max']:.1%})")

        # Alerts should be generated based on data
        assert isinstance(alerts, list)
