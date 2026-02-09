#!/usr/bin/env python3
"""
Batch API verification script for Claude Code verification agents.

Submits verification agent requests to Anthropic Batch API for 50% cost reduction.
Supports polling, exponential backoff, and results parsing.

Installation:
    pip install httpx anthropic structlog pydantic
    # OR with uv:
    uv pip install httpx anthropic structlog pydantic

Usage:
    python submit-batch-verification.py submit --wave 1  # Submit Wave 1 agents
    python submit-batch-verification.py submit --wave 2  # Submit Wave 2 agents
    python submit-batch-verification.py poll BATCH_ID    # Poll batch status
    python submit-batch-verification.py results BATCH_ID # Download results

Features:
- 50% cost savings vs. synchronous API
- Batch processing for non-interactive verification tasks
- Exponential backoff polling
- Structured report generation
- JSONL logging

Requirements:
- Python 3.11+
- httpx>=0.24.0
- anthropic>=0.18.0
- structlog>=23.0.0
- pydantic>=2.0.0
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import structlog
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
)
logger = structlog.get_logger(__name__)


# ============================================================================
# Pydantic Models (v2)
# ============================================================================


class MessageRequest(BaseModel):
    """Single message request for verification agent."""

    model_config = ConfigDict(strict=True, frozen=True)

    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str


class BatchRequestParams(BaseModel):
    """Parameters for a single batch request."""

    model_config = ConfigDict(strict=True)

    model: str = Field(default="claude-sonnet-4-5-20250929")
    max_tokens: int = Field(default=8000, ge=1, le=8192)
    messages: list[MessageRequest]
    system: str | None = None
    temperature: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("model")
    @classmethod
    def validate_model(cls, v: str) -> str:
        """Validate model name."""
        allowed_models = {
            "claude-opus-4-6",
            "claude-opus-4-5",
            "claude-sonnet-4-5-20250929",
            "claude-haiku-4-5-20251001",
        }
        if v not in allowed_models:
            raise ValueError(f"model must be one of {allowed_models}")
        return v


class BatchRequest(BaseModel):
    """Single request in a message batch."""

    model_config = ConfigDict(strict=True)

    custom_id: str
    params: BatchRequestParams


class BatchCreateRequest(BaseModel):
    """Request to create a message batch."""

    model_config = ConfigDict(strict=True)

    requests: list[BatchRequest] = Field(..., min_length=1, max_length=10000)


class RequestCounts(BaseModel):
    """Request counts for a batch."""

    model_config = ConfigDict(strict=True, frozen=True)

    processing: int = 0
    succeeded: int = 0
    errored: int = 0
    canceled: int = 0
    expired: int = 0


class BatchStatus(BaseModel):
    """Status of a message batch."""

    model_config = ConfigDict(strict=True, frozen=True)

    id: str
    type: str
    processing_status: str
    request_counts: RequestCounts
    ended_at: str | None = None
    created_at: str
    expires_at: str
    cancel_initiated_at: str | None = None
    results_url: str | None = None


class BatchResultSucceeded(BaseModel):
    """Succeeded batch result."""

    model_config = ConfigDict(strict=True, frozen=True)

    type: str = Field(..., pattern=r"^succeeded$")
    message: dict[str, Any]


class BatchResultErrored(BaseModel):
    """Errored batch result."""

    model_config = ConfigDict(strict=True, frozen=True)

    type: str = Field(..., pattern=r"^errored$")
    error: dict[str, Any]


class BatchResultExpired(BaseModel):
    """Expired batch result."""

    model_config = ConfigDict(strict=True, frozen=True)

    type: str = Field(..., pattern=r"^expired$")


class BatchResultCanceled(BaseModel):
    """Canceled batch result."""

    model_config = ConfigDict(strict=True, frozen=True)

    type: str = Field(..., pattern=r"^canceled$")


class BatchIndividualResult(BaseModel):
    """Individual result from batch processing."""

    model_config = ConfigDict(strict=True)

    custom_id: str
    result: dict[str, Any]  # Can be any of the result types above


# ============================================================================
# Agent Configuration
# ============================================================================


@dataclass
class AgentConfig:
    """Configuration for a verification agent."""

    name: str
    wave: int
    prompt_template: str
    model: str = "claude-sonnet-4-5-20250929"
    max_tokens: int = 8000


# Wave 1: Pattern recognition agents (3 agents, ~7 min)
WAVE_1_AGENTS = [
    AgentConfig(
        name="best-practices-enforcer",
        wave=1,
        model="claude-sonnet-4-5-20250929",
        prompt_template="""Verify Python code for modern standards compliance.

Files to verify: {files}

Check for:
- Type hints (list[str] not List[str])
- Pydantic v2 (ConfigDict not class Config)
- httpx async (not requests)
- structlog (not print)
- pathlib (not os.path)

Output JSON schema:
{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 42,
      "severity": "MEDIUM",
      "finding": "Using typing.List instead of list[str]",
      "fix": "Replace with: list[str]"
    }}
  ],
  "summary": {{
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }}
}}
""",
    ),
    AgentConfig(
        name="security-auditor",
        wave=1,
        model="claude-sonnet-4-5-20250929",
        prompt_template="""Audit code for security vulnerabilities.

Files to verify: {files}

Check for:
- OWASP Top 10 vulnerabilities
- Hardcoded secrets (API keys, passwords)
- SQL injection patterns
- XSS patterns
- Command injection

Output JSON schema:
{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 15,
      "severity": "CRITICAL",
      "finding": "Hardcoded API key detected",
      "cwe": "CWE-798",
      "fix": "Load from environment: api_key = os.getenv('API_KEY')"
    }}
  ],
  "summary": {{
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }}
}}
""",
    ),
    AgentConfig(
        name="hallucination-detector",
        wave=1,
        model="claude-sonnet-4-5-20250929",
        prompt_template="""Verify library syntax against official documentation.

Files to verify: {files}

Check for:
- Deprecated library APIs
- Incorrect function signatures
- Wrong parameter names/types
- Missing imports
- Version mismatches

Output JSON schema:
{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 20,
      "severity": "HIGH",
      "finding": "Using deprecated httpx.Client parameter 'proxies' (removed in v0.24)",
      "fix": "Use 'proxy' parameter instead: httpx.Client(proxy='...')"
    }}
  ],
  "summary": {{
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }}
}}
""",
    ),
]

# Wave 2: Quality & testing agents (2 agents, ~5 min)
WAVE_2_AGENTS = [
    AgentConfig(
        name="code-reviewer",
        wave=2,
        model="claude-sonnet-4-5-20250929",
        prompt_template="""Review code quality and maintainability.

Files to verify: {files}

Check for:
- Cyclomatic complexity (>10 = flag)
- DRY violations
- Naming consistency
- Function length (>30 lines)
- Performance bottlenecks

Output JSON schema:
{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 50,
      "severity": "MEDIUM",
      "finding": "Function has cyclomatic complexity of 15 (threshold: 10)",
      "fix": "Extract helper functions to reduce complexity"
    }}
  ],
  "summary": {{
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }},
  "score": 9.5
}}
""",
    ),
    AgentConfig(
        name="test-generator",
        wave=2,
        model="claude-sonnet-4-5-20250929",
        prompt_template="""Analyze test coverage and generate tests.

Files to verify: {files}

Check for:
- Coverage < 80%
- Missing edge case tests
- Uncovered error paths
- Mock management issues

Output JSON schema:
{{
  "findings": [
    {{
      "file": "path/to/file.py",
      "line": 10,
      "severity": "MEDIUM",
      "finding": "Function 'validate_input' has no test coverage",
      "fix": "Add test_validate_input_success and test_validate_input_invalid"
    }}
  ],
  "summary": {{
    "total": 0,
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0
  }},
  "coverage": 65.0
}}
""",
    ),
]


# ============================================================================
# Batch API Client
# ============================================================================


class BatchAPIClient:
    """Client for Anthropic Batch API operations."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize the batch API client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.base_url = "https://api.anthropic.com/v1"
        self.anthropic_version = "2023-06-01"

        self.project_root = Path.cwd()
        self.pending_dir = self.project_root / ".build" / "checkpoints" / "pending"
        self.reports_dir = self.project_root / ".ignorar" / "production-reports"
        self.logs_dir = self.project_root / ".build" / "logs" / "agents"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    async def get_pending_files(self) -> list[str]:
        """Get list of pending Python files requiring verification.

        Returns:
            List of Python file paths marked as pending
        """
        if not self.pending_dir.exists():
            return []

        pending_files = []
        for marker in self.pending_dir.glob("*.pending"):
            # Extract original file path from marker filename
            # Format: {hash}.py.pending
            original_file = marker.stem  # Removes .pending
            if original_file.endswith(".py"):
                pending_files.append(str(self.project_root / "src" / original_file))

        logger.info("pending_files_detected", count=len(pending_files))
        return pending_files

    async def create_batch(
        self,
        agents: Sequence[AgentConfig],
        pending_files: list[str],
    ) -> BatchStatus:
        """Create a message batch for verification agents.

        Args:
            agents: List of agent configurations to run
            pending_files: List of pending files to verify

        Returns:
            BatchStatus with batch ID and initial status
        """
        files_str = "\n".join(f"- {f}" for f in pending_files)

        # Build batch requests
        requests = []
        for agent in agents:
            prompt = agent.prompt_template.format(files=files_str)
            request = BatchRequest(
                custom_id=f"{agent.name}-{uuid.uuid4().hex[:8]}",
                params=BatchRequestParams(
                    model=agent.model,
                    max_tokens=agent.max_tokens,
                    messages=[
                        MessageRequest(
                            role="user",
                            content=prompt,
                        )
                    ],
                ),
            )
            requests.append(request)

        batch_request = BatchCreateRequest(requests=requests)

        # Submit batch
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.post(
                f"{self.base_url}/messages/batches",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.anthropic_version,
                    "content-type": "application/json",
                },
                json=batch_request.model_dump(),
            )
            response.raise_for_status()

            data = response.json()
            batch_status = BatchStatus(**data)

            logger.info(
                "batch_created",
                batch_id=batch_status.id,
                agent_count=len(requests),
                status=batch_status.processing_status,
            )

            return batch_status

    async def poll_batch(
        self,
        batch_id: str,
        poll_interval: int = 60,
        max_wait_seconds: int = 3600,
    ) -> BatchStatus:
        """Poll batch status until processing completes.

        Args:
            batch_id: Batch ID to poll
            poll_interval: Seconds between polls (default: 60)
            max_wait_seconds: Maximum seconds to wait (default: 3600 = 1 hour)

        Returns:
            Final BatchStatus

        Raises:
            TimeoutError: If max_wait_seconds exceeded
        """
        start_time = time.time()
        poll_count = 0

        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            while True:
                elapsed = time.time() - start_time
                if elapsed > max_wait_seconds:
                    raise TimeoutError(
                        f"Batch {batch_id} did not complete within {max_wait_seconds}s"
                    )

                response = await client.get(
                    f"{self.base_url}/messages/batches/{batch_id}",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": self.anthropic_version,
                    },
                )
                response.raise_for_status()

                data = response.json()
                batch_status = BatchStatus(**data)

                poll_count += 1
                logger.info(
                    "batch_polled",
                    batch_id=batch_id,
                    poll_count=poll_count,
                    status=batch_status.processing_status,
                    elapsed_seconds=int(elapsed),
                    request_counts=batch_status.request_counts.model_dump(),
                )

                if batch_status.processing_status == "ended":
                    logger.info(
                        "batch_completed",
                        batch_id=batch_id,
                        total_polls=poll_count,
                        total_seconds=int(elapsed),
                    )
                    return batch_status

                # Exponential backoff with jitter
                backoff = min(poll_interval * (1.5**poll_count), 300)  # Max 5 min
                jitter = backoff * 0.1
                await asyncio.sleep(backoff + jitter)

    async def download_results(
        self,
        batch_id: str,
    ) -> list[BatchIndividualResult]:
        """Download batch results from results_url.

        Args:
            batch_id: Batch ID to download results for

        Returns:
            List of individual batch results
        """
        # First get batch status to retrieve results_url
        async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
            response = await client.get(
                f"{self.base_url}/messages/batches/{batch_id}",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.anthropic_version,
                },
            )
            response.raise_for_status()

            batch_status = BatchStatus(**response.json())

            if not batch_status.results_url:
                raise ValueError(f"Batch {batch_id} has no results_url yet")

            # Download results (JSONL format)
            results_response = await client.get(
                batch_status.results_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": self.anthropic_version,
                },
            )
            results_response.raise_for_status()

            # Parse JSONL
            results = []
            for line in results_response.text.strip().split("\n"):
                if line:
                    result_data = json.loads(line)
                    results.append(BatchIndividualResult(**result_data))

            logger.info(
                "batch_results_downloaded",
                batch_id=batch_id,
                result_count=len(results),
            )

            return results

    def parse_agent_findings(
        self,
        result: BatchIndividualResult,
    ) -> dict[str, Any]:
        """Parse agent findings from batch result.

        Args:
            result: Individual batch result

        Returns:
            Parsed findings dictionary
        """
        result_type = result.result.get("type")

        if result_type == "succeeded":
            message = result.result.get("message", {})
            content = message.get("content", [])

            # Extract text from content blocks
            text_content = ""
            for block in content:
                if block.get("type") == "text":
                    text_content += block.get("text", "")

            # Attempt to parse JSON from response
            try:
                findings = json.loads(text_content)
                return {
                    "status": "PASS",
                    "findings": findings.get("findings", []),
                    "summary": findings.get("summary", {}),
                    "score": findings.get("score"),
                    "coverage": findings.get("coverage"),
                }
            except json.JSONDecodeError:
                logger.warning(
                    "failed_to_parse_agent_response",
                    custom_id=result.custom_id,
                    content_preview=text_content[:200],
                )
                return {
                    "status": "FAIL",
                    "error": "Failed to parse agent response as JSON",
                }

        elif result_type == "errored":
            error = result.result.get("error", {})
            return {
                "status": "FAIL",
                "error": error.get("message", "Unknown error"),
                "error_type": error.get("type"),
            }

        elif result_type in ("expired", "canceled"):
            return {
                "status": "FAIL",
                "error": f"Request {result_type}",
            }

        else:
            return {
                "status": "FAIL",
                "error": f"Unknown result type: {result_type}",
            }

    def generate_report(
        self,
        batch_id: str,
        agents: Sequence[AgentConfig],
        results: list[BatchIndividualResult],
        total_cost: float,
        sync_cost: float,
    ) -> Path:
        """Generate detailed report for batch verification.

        Args:
            batch_id: Batch ID
            agents: List of agents used
            results: List of batch results
            total_cost: Total batch cost
            sync_cost: Estimated synchronous cost

        Returns:
            Path to generated report
        """
        timestamp = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        wave_num = agents[0].wave if agents else 0
        report_dir = self.reports_dir / "batch-verification" / f"phase-{wave_num}"
        report_dir.mkdir(parents=True, exist_ok=True)

        report_path = (
            report_dir
            / f"{timestamp}-phase4-task41-batch-verification-wave{wave_num}.md"
        )

        # Build report content
        report_lines = [
            f"# Batch Verification Report - Wave {wave_num}",
            "",
            f"**Date:** {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
            f"**Batch ID:** {batch_id}",
            f"**Agents:** {len(agents)}",
            f"**Results:** {len(results)}",
            "",
            "---",
            "",
            "## Cost Comparison",
            "",
            f"- **Batch API Cost:** ${total_cost:.4f} (50% discount)",
            f"- **Synchronous API Cost:** ${sync_cost:.4f}",
            f"- **Savings:** ${sync_cost - total_cost:.4f} ({((sync_cost - total_cost) / sync_cost * 100):.1f}%)",
            "",
            "---",
            "",
            "## Agent Results",
            "",
        ]

        for result in results:
            parsed = self.parse_agent_findings(result)
            agent_name = result.custom_id.rsplit("-", 1)[0]

            report_lines.extend(
                [
                    f"### {agent_name}",
                    "",
                    f"- **Status:** {parsed['status']}",
                ]
            )

            if parsed["status"] == "PASS":
                summary = parsed.get("summary", {})
                report_lines.extend(
                    [
                        f"- **Total Findings:** {summary.get('total', 0)}",
                        f"- **Critical:** {summary.get('critical', 0)}",
                        f"- **High:** {summary.get('high', 0)}",
                        f"- **Medium:** {summary.get('medium', 0)}",
                        f"- **Low:** {summary.get('low', 0)}",
                    ]
                )

                if parsed.get("score") is not None:
                    report_lines.append(f"- **Score:** {parsed['score']}/10")

                if parsed.get("coverage") is not None:
                    report_lines.append(f"- **Coverage:** {parsed['coverage']}%")

            else:
                report_lines.append(f"- **Error:** {parsed.get('error', 'Unknown')}")

            report_lines.append("")

        report_content = "\n".join(report_lines)
        report_path.write_text(report_content)

        logger.info(
            "report_generated",
            report_path=str(report_path),
            lines=len(report_lines),
        )

        return report_path


# ============================================================================
# CLI Commands
# ============================================================================


async def cmd_submit(args: argparse.Namespace) -> int:
    """Submit batch verification for a wave.

    Args:
        args: CLI arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    client = BatchAPIClient()

    # Get pending files
    pending_files = await client.get_pending_files()
    if not pending_files:
        logger.info("no_pending_files")
        print("No pending files to verify.")
        return 0

    # Select agents for wave
    agents = WAVE_1_AGENTS if args.wave == 1 else WAVE_2_AGENTS

    print(f"Submitting Wave {args.wave} batch verification...")
    print(f"Agents: {', '.join(a.name for a in agents)}")
    print(f"Pending files: {len(pending_files)}")

    # Create batch
    batch_status = await client.create_batch(agents, pending_files)

    print(f"\nBatch created: {batch_status.id}")
    print(f"Status: {batch_status.processing_status}")
    print(f"Expires at: {batch_status.expires_at}")
    print(f"\nPoll with: python {__file__} --poll {batch_status.id}")

    return 0


async def cmd_poll(args: argparse.Namespace) -> int:
    """Poll batch status until completion.

    Args:
        args: CLI arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    client = BatchAPIClient()

    print(f"Polling batch {args.batch_id}...")

    try:
        batch_status = await client.poll_batch(
            args.batch_id,
            poll_interval=60,
            max_wait_seconds=3600,
        )

        print(f"\nBatch completed!")
        print(f"Status: {batch_status.processing_status}")
        print(f"Request counts:")
        print(f"  Succeeded: {batch_status.request_counts.succeeded}")
        print(f"  Errored: {batch_status.request_counts.errored}")
        print(f"  Expired: {batch_status.request_counts.expired}")
        print(f"  Canceled: {batch_status.request_counts.canceled}")

        if batch_status.results_url:
            print(f"\nResults URL: {batch_status.results_url}")
            print(f"Download with: python {__file__} --results {args.batch_id}")

        return 0

    except TimeoutError as e:
        logger.error("poll_timeout", error=str(e))
        print(f"ERROR: {e}")
        return 1


async def cmd_results(args: argparse.Namespace) -> int:
    """Download and parse batch results.

    Args:
        args: CLI arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    client = BatchAPIClient()

    print(f"Downloading results for batch {args.batch_id}...")

    try:
        results = await client.download_results(args.batch_id)

        print(f"\nResults downloaded: {len(results)}")

        # Parse and display results
        for result in results:
            parsed = client.parse_agent_findings(result)
            agent_name = result.custom_id.rsplit("-", 1)[0]

            print(f"\n{agent_name}:")
            print(f"  Status: {parsed['status']}")

            if parsed["status"] == "PASS":
                summary = parsed.get("summary", {})
                print(f"  Total findings: {summary.get('total', 0)}")
                print(f"  Critical: {summary.get('critical', 0)}")
                print(f"  High: {summary.get('high', 0)}")
            else:
                print(f"  Error: {parsed.get('error', 'Unknown')}")

        # Generate report
        agents = WAVE_1_AGENTS if "best-practices" in results[0].custom_id else WAVE_2_AGENTS

        # Estimate costs (placeholder - actual costs from API response)
        total_cost = 0.50  # Placeholder
        sync_cost = 1.00  # Placeholder

        report_path = client.generate_report(
            args.batch_id,
            agents,
            results,
            total_cost,
            sync_cost,
        )

        print(f"\nReport saved to: {report_path}")

        return 0

    except Exception as e:
        logger.error("download_failed", error=str(e))
        print(f"ERROR: {e}")
        return 1


# ============================================================================
# Main CLI
# ============================================================================


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch API verification for Claude Code agents"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Submit command
    submit_parser = subparsers.add_parser("submit", help="Submit batch verification")
    submit_parser.add_argument(
        "--wave",
        type=int,
        choices=[1, 2],
        required=True,
        help="Wave number (1 or 2)",
    )

    # Poll command
    poll_parser = subparsers.add_parser("poll", help="Poll batch status")
    poll_parser.add_argument("batch_id", help="Batch ID to poll")

    # Results command
    results_parser = subparsers.add_parser("results", help="Download batch results")
    results_parser.add_argument("batch_id", help="Batch ID to download results for")

    args = parser.parse_args()

    # Route to command
    if args.command == "submit":
        return asyncio.run(cmd_submit(args))
    elif args.command == "poll":
        return asyncio.run(cmd_poll(args))
    elif args.command == "results":
        return asyncio.run(cmd_results(args))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
