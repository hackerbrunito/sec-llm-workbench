#!/usr/bin/env python3
"""
check-module-coverage.py — Per-module coverage floor enforcement.

Usage: python3 check-module-coverage.py <target-project-path>

Reads coverage.xml from the target project and flags any module below 50% line coverage.
Exit code 0 = all modules pass. Exit code 1 = one or more modules below floor.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

FLOOR = 0.50  # 50% minimum per module

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check-module-coverage.py <target-project-path>")
        sys.exit(1)

    target = Path(sys.argv[1]).expanduser().resolve()
    coverage_xml = target / "coverage.xml"

    if not coverage_xml.exists():
        print(f"WARNING: coverage.xml not found at {coverage_xml}")
        print("Run: cd {target} && uv run pytest --cov --cov-report=xml")
        sys.exit(1)

    tree = ET.parse(coverage_xml)
    root = tree.getroot()

    failures = []
    modules_checked = 0

    for cls in root.iter("class"):
        filename = cls.get("filename", "")
        # Skip non-real modules
        if not filename or filename.startswith("<"):
            continue
        # Skip __init__.py files (often intentionally empty)
        if filename.endswith("__init__.py"):
            continue

        line_rate = float(cls.get("line-rate", "1.0"))
        modules_checked += 1

        if line_rate < FLOOR:
            failures.append({
                "file": filename,
                "coverage": line_rate,
                "pct": f"{line_rate * 100:.1f}%",
            })

    print(f"\n=== Per-Module Coverage Floor Check (minimum: {FLOOR*100:.0f}%) ===")
    print(f"Modules checked: {modules_checked}")

    if not failures:
        print(f"PASS: All {modules_checked} modules meet the {FLOOR*100:.0f}% floor.")
        sys.exit(0)
    else:
        print(f"\nFAIL: {len(failures)} module(s) below {FLOOR*100:.0f}% coverage floor:\n")
        for f in sorted(failures, key=lambda x: x["coverage"]):
            print(f"  {f['pct']:>7}  {f['file']}")
        print(f"\nFIX: Add tests for the modules listed above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
