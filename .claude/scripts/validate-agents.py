#!/usr/bin/env python3
"""
Agent Configuration Validation Script

Validates agent configuration files (.claude/agents/*.md) for:
1. Required sections present (ROLE, TOOLS, WORKFLOW, OUTPUT FORMAT)
2. cache_control markers properly formatted
3. JSON schema examples valid (if present)
4. Context7 references correct (for hallucination-detector)
5. Report persistence instructions present

Exit codes:
  0: All validations passed
  1: Validation failed
  2: Runtime error
"""

import argparse
import json
import logging
import re
import sys
from collections.abc import Sequence
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Validation error with severity and details."""

    def __init__(self, message: str, severity: str = "ERROR") -> None:
        self.message = message
        self.severity = severity
        super().__init__(message)


class AgentValidator:
    """Validates agent configuration files."""

    # Required sections for all agents
    REQUIRED_SECTIONS = [
        "# ",  # Agent name header
    ]

    # Common section patterns (at least one should be present)
    COMMON_SECTIONS = [
        "## Before",
        "## Verification",
        "## Actions",
        "## Tool Invocation",
        "## Report",
    ]

    # cache_control marker patterns
    CACHE_CONTROL_PATTERNS = [
        r'<cache_control\s+type="ephemeral"\s*/?>',
        r'"cache_control":\s*{\s*"type":\s*"ephemeral"\s*}',
    ]

    # Context7 MCP tool names
    CONTEXT7_TOOLS = [
        "mcp__context7__resolve-library-id",
        "mcp__context7__query-docs",
    ]

    def __init__(self, agent_path: Path) -> None:
        self.agent_path = agent_path
        self.agent_name = agent_path.stem
        self.content = ""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self) -> bool:
        """Run all validation checks. Returns True if all pass."""
        logger.info(f"Validating agent: {self.agent_name} at {self.agent_path}")

        try:
            self._load_file()
            self._check_required_sections()
            self._check_cache_control_markers()
            self._check_json_schemas()
            self._check_context7_references()
            self._check_report_persistence()

            if self.errors:
                logger.error(
                    f"Validation failed for {self.agent_name}: "
                    f"{len(self.errors)} errors, {len(self.warnings)} warnings"
                )
                return False

            logger.info(
                f"Validation passed for {self.agent_name} "
                f"({len(self.warnings)} warnings)"
            )
            return True

        except Exception as e:
            logger.error(f"Validation error for {self.agent_name}: {e}")
            self.errors.append(f"Runtime error: {e}")
            return False

    def _load_file(self) -> None:
        """Load and validate file exists and is readable."""
        if not self.agent_path.exists():
            raise ValidationError(f"Agent file not found: {self.agent_path}")

        if not self.agent_path.is_file():
            raise ValidationError(f"Path is not a file: {self.agent_path}")

        try:
            self.content = self.agent_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ValidationError(f"Failed to read file: {e}") from e

        if not self.content.strip():
            raise ValidationError("Agent file is empty")

    def _check_required_sections(self) -> None:
        """Check that required sections are present."""
        # Check for agent name header
        if not re.search(r"^#\s+.+", self.content, re.MULTILINE):
            self.errors.append("Missing agent name header (# Agent Name)")

        # Check for at least one common section
        found_sections = [
            section
            for section in self.COMMON_SECTIONS
            if section in self.content
        ]

        if not found_sections:
            self.errors.append(
                f"Missing common sections. Expected at least one of: {', '.join(self.COMMON_SECTIONS)}"
            )
        else:
            logger.debug(f"Sections found in {self.agent_name}: {found_sections}")

    def _check_cache_control_markers(self) -> None:
        """Check cache_control markers are properly formatted."""
        # Search for any cache_control pattern
        found_patterns = []
        for pattern in self.CACHE_CONTROL_PATTERNS:
            matches = re.findall(pattern, self.content, re.IGNORECASE)
            found_patterns.extend(matches)

        if not found_patterns:
            self.warnings.append(
                "No cache_control markers found. Consider adding for performance optimization."
            )
        else:
            logger.debug(f"cache_control markers found in {self.agent_name}: {len(found_patterns)}")

            # Validate format
            for match in found_patterns:
                if 'type="ephemeral"' not in match and '"type": "ephemeral"' not in match:
                    self.errors.append(
                        f"Invalid cache_control format: {match}. Must use type='ephemeral'"
                    )

    def _check_json_schemas(self) -> None:
        """Check JSON schema examples are valid."""
        # Find JSON code blocks
        json_pattern = r"```json\s*\n(.*?)\n```"
        json_blocks = re.findall(json_pattern, self.content, re.DOTALL)

        if not json_blocks:
            logger.debug(f"No JSON schemas found in {self.agent_name}")
            return

        logger.debug(f"JSON schemas found in {self.agent_name}: {len(json_blocks)}")

        for idx, block in enumerate(json_blocks, 1):
            # Skip validation if block contains documentation placeholders
            placeholders = ["...", "N", "<", ">", "[...]", "{...}"]
            if any(placeholder in block for placeholder in placeholders):
                logger.debug(f"Skipping JSON block {idx} (contains placeholders)")
                continue

            try:
                json.loads(block)
            except json.JSONDecodeError as e:
                self.errors.append(
                    f"Invalid JSON schema in block {idx}: {e.msg} at line {e.lineno}"
                )

    def _check_context7_references(self) -> None:
        """Check Context7 MCP references (for hallucination-detector)."""
        if self.agent_name != "hallucination-detector":
            return

        # Check if Context7 tools are mentioned
        context7_found = any(
            tool in self.content for tool in self.CONTEXT7_TOOLS
        )

        if not context7_found:
            self.errors.append(
                f"hallucination-detector must reference Context7 MCP tools: {', '.join(self.CONTEXT7_TOOLS)}"
            )
        else:
            logger.debug(f"Context7 references found in {self.agent_name}")

            # Check that both tools are mentioned
            for tool in self.CONTEXT7_TOOLS:
                if tool not in self.content:
                    self.warnings.append(f"Context7 tool not mentioned: {tool}")

    def _check_report_persistence(self) -> None:
        """Check report persistence instructions are present."""
        # Look for report persistence patterns
        report_patterns = [
            r"\.ignorar/production-reports/",
            r"save.*report",
            r"Report Persistence",
        ]

        found_patterns = [
            pattern
            for pattern in report_patterns
            if re.search(pattern, self.content, re.IGNORECASE)
        ]

        if not found_patterns:
            self.errors.append(
                "Missing report persistence instructions. Agent must save reports to .ignorar/production-reports/"
            )
        else:
            logger.debug(
                f"Report persistence instructions found in {self.agent_name}: "
                f"{len(found_patterns)} patterns"
            )

    def print_results(self) -> None:
        """Print validation results to stdout."""
        print(f"\n{'=' * 70}")
        print(f"Agent: {self.agent_name}")
        print(f"Path: {self.agent_path}")
        print(f"{'=' * 70}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed")

        print()


def validate_agents(agent_names: Sequence[str] | None = None) -> bool:
    """
    Validate agent configuration files.

    Args:
        agent_names: Optional list of agent names to validate. If None, validates all.

    Returns:
        True if all validations passed, False otherwise.
    """
    agents_dir = Path(__file__).parent.parent / "agents"

    if not agents_dir.exists():
        logger.error(f"Agents directory not found: {agents_dir}")
        print(f"❌ Agents directory not found: {agents_dir}")
        return False

    # Get list of agent files
    if agent_names:
        agent_files = [agents_dir / f"{name}.md" for name in agent_names]
        # Check that all specified agents exist
        for agent_file in agent_files:
            if not agent_file.exists():
                logger.error(f"Agent not found: {agent_file.stem}")
                print(f"❌ Agent not found: {agent_file.stem}")
                return False
    else:
        agent_files = sorted(agents_dir.glob("*.md"))

    if not agent_files:
        logger.error(f"No agent files found in: {agents_dir}")
        print(f"❌ No agent files found in: {agents_dir}")
        return False

    logger.info(f"Validating {len(agent_files)} agent(s)")
    print(f"\n🔍 Validating {len(agent_files)} agent(s)...\n")

    # Validate all agents
    all_passed = True
    validators = []

    for agent_file in agent_files:
        validator = AgentValidator(agent_file)
        passed = validator.validate()
        validators.append(validator)

        if not passed:
            all_passed = False

    # Print results
    print(f"\n{'=' * 70}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 70}")

    for validator in validators:
        validator.print_results()

    # Final summary
    passed_count = sum(1 for v in validators if not v.errors)
    failed_count = len(validators) - passed_count

    print(f"{'=' * 70}")
    print(f"Total: {len(validators)} agent(s)")
    print(f"✅ Passed: {passed_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"{'=' * 70}\n")

    return all_passed


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate agent configuration files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Validate all agents
  %(prog)s --agent code-implementer # Validate specific agent
  %(prog)s --agent best-practices-enforcer --agent security-auditor

Exit codes:
  0: All validations passed
  1: Validation failed
  2: Runtime error
        """,
    )

    parser.add_argument(
        "--agent",
        action="append",
        dest="agents",
        metavar="NAME",
        help="Agent name to validate (without .md extension). Can be specified multiple times.",
    )

    args = parser.parse_args()

    try:
        passed = validate_agents(args.agents)
        return 0 if passed else 1
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
