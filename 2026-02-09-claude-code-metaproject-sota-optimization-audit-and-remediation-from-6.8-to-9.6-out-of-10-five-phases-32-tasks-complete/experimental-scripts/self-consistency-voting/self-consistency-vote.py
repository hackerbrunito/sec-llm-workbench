#!/usr/bin/env python3
"""
Self-consistency voting for high-stakes verification decisions.

Implements N-sample voting (Wang et al. 2022) for improved accuracy on critical
security findings. Generates N independent responses, extracts decisions, and
returns majority vote with confidence score.

Expected accuracy improvement: +12-18% on ambiguous cases.

Installation:
    uv pip install httpx anthropic structlog pydantic

Usage:
    from self_consistency_vote import vote_on_security_finding

    result = await vote_on_security_finding(
        prompt="Analyze this code for SQL injection: ...",
        n_samples=3,
        model="claude-sonnet-4.5"
    )
    # result = {"decision": "CRITICAL", "confidence": 1.0, "votes": [3, 0, 0, 0]}
"""

from __future__ import annotations

import asyncio
from collections import Counter
from dataclasses import dataclass
from typing import Any

import structlog
from anthropic import Anthropic
from pydantic import BaseModel, ConfigDict, Field

logger = structlog.get_logger()


class VotingResult(BaseModel):
    """Result of self-consistency voting."""

    model_config = ConfigDict(frozen=True)

    decision: str = Field(description="Majority vote decision")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score (votes/total)")
    votes: list[int] = Field(description="Vote distribution by severity")
    samples: list[str] = Field(description="Raw samples for audit trail")
    prompt: str = Field(description="Original prompt")
    n_samples: int = Field(ge=1, description="Number of samples generated")


@dataclass
class SeverityLevel:
    """Severity level mapping."""

    name: str
    index: int


SEVERITY_LEVELS = [
    SeverityLevel("CRITICAL", 0),
    SeverityLevel("HIGH", 1),
    SeverityLevel("MEDIUM", 2),
    SeverityLevel("LOW", 3),
]


def extract_severity(response: str) -> str:
    """
    Extract severity level from agent response.

    Searches for keywords in order: CRITICAL > HIGH > MEDIUM > LOW.
    Returns first match.
    """
    response_upper = response.upper()

    for severity in SEVERITY_LEVELS:
        if severity.name in response_upper:
            return severity.name

    # Default to MEDIUM if no keyword found
    logger.warning("no_severity_found", response_preview=response[:100])
    return "MEDIUM"


async def generate_sample(
    client: Anthropic,
    prompt: str,
    model: str,
    temperature: float = 0.7,
) -> str:
    """
    Generate a single sample response.

    Uses temperature=0.7 for diversity while maintaining quality.
    """
    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=2000,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


async def vote_on_security_finding(
    prompt: str,
    n_samples: int = 3,
    model: str = "claude-sonnet-4.5",
    temperature: float = 0.7,
) -> VotingResult:
    """
    Perform self-consistency voting on a security finding.

    Args:
        prompt: The analysis prompt (e.g., "Analyze for SQL injection: ...")
        n_samples: Number of independent samples (default 3, recommended 3-5)
        model: Claude model to use (default Sonnet 4.5)
        temperature: Sampling temperature (default 0.7 for diversity)

    Returns:
        VotingResult with majority decision, confidence, and vote distribution

    Example:
        result = await vote_on_security_finding(
            prompt="Assess SQL injection risk in: cursor.execute(f'SELECT * FROM users WHERE id={user_id}')",
            n_samples=3
        )
        if result.decision == "CRITICAL" and result.confidence >= 0.67:
            print(f"High confidence CRITICAL finding: {result.confidence:.0%}")
    """
    logger.info("voting_start", n_samples=n_samples, model=model)

    client = Anthropic()

    # Generate N independent samples in parallel
    tasks = [
        generate_sample(client, prompt, model, temperature) for _ in range(n_samples)
    ]
    samples = await asyncio.gather(*tasks)

    # Extract severity from each sample
    decisions = [extract_severity(sample) for sample in samples]

    # Count votes
    vote_counts = Counter(decisions)
    logger.info("votes_counted", vote_distribution=dict(vote_counts))

    # Majority vote
    majority_decision, majority_count = vote_counts.most_common(1)[0]
    confidence = majority_count / n_samples

    # Build vote array [CRITICAL, HIGH, MEDIUM, LOW]
    votes = [
        vote_counts.get(severity.name, 0) for severity in SEVERITY_LEVELS
    ]

    logger.info(
        "voting_complete",
        decision=majority_decision,
        confidence=confidence,
        votes=votes,
    )

    return VotingResult(
        decision=majority_decision,
        confidence=confidence,
        votes=votes,
        samples=samples,
        prompt=prompt,
        n_samples=n_samples,
    )


async def vote_with_threshold(
    prompt: str,
    n_samples: int = 3,
    min_confidence: float = 0.67,
    model: str = "claude-sonnet-4.5",
) -> tuple[bool, VotingResult]:
    """
    Vote with confidence threshold for binary decision (report or not).

    Returns (should_report, result) tuple.

    Example:
        should_report, result = await vote_with_threshold(
            prompt="Analyze security issue...",
            n_samples=3,
            min_confidence=0.67  # 2/3 threshold
        )
        if should_report and result.decision in ("CRITICAL", "HIGH"):
            findings.append(result)
    """
    result = await vote_on_security_finding(prompt, n_samples, model)

    should_report = result.confidence >= min_confidence

    logger.info(
        "threshold_check",
        decision=result.decision,
        confidence=result.confidence,
        threshold=min_confidence,
        should_report=should_report,
    )

    return should_report, result


# CLI interface for testing
async def main() -> None:
    """CLI interface for manual testing."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python self-consistency-vote.py 'Your prompt here'")
        sys.exit(1)

    prompt = sys.argv[1]
    n_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 3

    result = await vote_on_security_finding(prompt, n_samples)

    print(f"\n=== Voting Result ===")
    print(f"Decision: {result.decision}")
    print(f"Confidence: {result.confidence:.0%}")
    print(f"Votes: CRITICAL={result.votes[0]}, HIGH={result.votes[1]}, MEDIUM={result.votes[2]}, LOW={result.votes[3]}")
    print(f"\n=== Samples ===")
    for i, sample in enumerate(result.samples, 1):
        print(f"\nSample {i}:")
        print(sample[:200] + "..." if len(sample) > 200 else sample)


if __name__ == "__main__":
    asyncio.run(main())
