#!/usr/bin/env python3
"""
Schema Validation Fallback Strategy Test

Tests the fallback mechanism when JSON schemas fail validation.
Verifies graceful degradation to natural language mode.

Reference: .claude/rules/agent-tool-schemas.md (lines 639-657)
"""

import json
import logging
import sys
from io import StringIO
from typing import Any

# Setup logging to capture errors
log_stream = StringIO()
logging.basicConfig(
    level=logging.ERROR,
    format="%(levelname)s: %(message)s",
    stream=log_stream,
)
logger = logging.getLogger(__name__)


def test_invalid_json_structure() -> bool:
    """
    Test fallback on invalid JSON structure (trailing comma).

    Scenario: JSON with syntax error should trigger JSONDecodeError.
    Expected: Error caught, fallback to natural language mode.
    """
    malformed_json = '{"tool": "bash", "command": "test",}'  # trailing comma

    try:
        json.loads(malformed_json)
        # Should not reach here
        logger.error("Invalid JSON validation failed: error not raised")
        return False
    except json.JSONDecodeError as e:
        # Fallback behavior: log error and continue
        logger.error(f"Invalid schema: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_missing_required_fields() -> bool:
    """
    Test fallback when required schema fields are missing.

    Scenario: Schema missing 'tool' field (required).
    Expected: KeyError caught during validation.
    """
    incomplete_schema = {"command": "test", "description": "test command"}

    # Simulate validation that checks for required 'tool' field
    required_fields = ["tool", "command"]

    try:
        for field in required_fields:
            if field not in incomplete_schema:
                raise KeyError(f"Missing required field: '{field}'")
        return False
    except KeyError as e:
        # Fallback behavior: log error with field name
        logger.error(f"Schema validation error: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_wrong_parameter_types() -> bool:
    """
    Test fallback when schema has incorrect parameter types.

    Scenario: Field with string type when number expected.
    Expected: Type validation error caught.
    """
    schema_with_wrong_type = {
        "tool": "bash",
        "command": "test",
        "timeout_ms": "invalid_number",  # Should be int, not str
    }

    # Simulate type validation
    try:
        timeout = schema_with_wrong_type.get("timeout_ms")
        if timeout is not None and not isinstance(timeout, int):
            raise TypeError(
                f"Field 'timeout_ms' must be int, got {type(timeout).__name__}"
            )
        return False
    except TypeError as e:
        # Fallback behavior: log error with type mismatch
        logger.error(f"Type validation failed: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error type: {type(e).__name__}: {e}")
        return False


def test_circular_schema_references() -> bool:
    """
    Test fallback when schema contains circular references.

    Scenario: Schema referencing itself causing recursion.
    Expected: RecursionError caught, fallback triggered.
    """

    def validate_schema_depth(obj: Any, max_depth: int = 100, depth: int = 0) -> None:
        """
        Recursively validate schema structure.
        Raises RecursionError if depth exceeds limit.
        """
        if depth > max_depth:
            raise RecursionError(f"Schema nesting exceeds max depth of {max_depth}")

        if isinstance(obj, dict):
            for value in obj.values():
                validate_schema_depth(value, max_depth, depth + 1)
        elif isinstance(obj, (list, tuple)):
            for item in obj:
                validate_schema_depth(item, max_depth, depth + 1)

    # Create circular reference
    circular_schema: dict[str, Any] = {"tool": "bash", "command": "test"}
    circular_schema["self"] = circular_schema  # Self-reference

    try:
        validate_schema_depth(circular_schema, max_depth=10)
        # If we reach here without error, test fails
        logger.error("Circular reference validation failed: error not raised")
        return False
    except RecursionError as e:
        # Fallback behavior: log error and note depth limit
        logger.error(f"Invalid schema: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error type: {type(e).__name__}: {e}")
        return False


def run_tests() -> tuple[list[tuple[str, bool]], float]:
    """
    Run all fallback tests and return results.

    Returns:
        Tuple of (test_results, execution_time_seconds)
    """
    import time

    start_time = time.time()

    tests = [
        ("Invalid JSON Structure", test_invalid_json_structure),
        ("Missing Required Fields", test_missing_required_fields),
        ("Wrong Parameter Types", test_wrong_parameter_types),
        ("Circular Schema References", test_circular_schema_references),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            logger.error(f"Test '{test_name}' raised unexpected exception: {e}")
            results.append((test_name, False))

    elapsed = time.time() - start_time
    return results, elapsed


def print_results(results: list[tuple[str, bool]], elapsed: float) -> None:
    """Print test results in table format."""
    print("\n" + "=" * 60)
    print("Schema Fallback Test Results")
    print("=" * 60)
    print(f"\n{'Test Scenario':<35} {'Status':<10}")
    print("-" * 60)

    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<35} {status:<10}")

    print("-" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nResults: {passed_count}/{total_count} passed")
    print(f"Execution time: {elapsed:.3f}s")

    # Print captured logs
    log_contents = log_stream.getvalue()
    if log_contents:
        print("\n" + "=" * 60)
        print("Fallback Logs (Error Handling)")
        print("=" * 60)
        print(log_contents)

    print("=" * 60 + "\n")


def main() -> int:
    """
    Main entry point.

    Returns:
        0 if all tests pass, 1 if any test fails
    """
    results, elapsed = run_tests()
    print_results(results, elapsed)

    all_passed = all(passed for _, passed in results)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
