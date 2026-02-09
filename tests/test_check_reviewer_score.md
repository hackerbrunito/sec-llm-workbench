# Test Scenarios for check-reviewer-score.sh

## Overview

This document describes test scenarios for `.claude/scripts/check-reviewer-score.sh`, which validates code-reviewer scores against the 9.0/10 threshold defined in `verification-thresholds.md`.

## Test Scenarios

### Scenario 1: No Reports Directory Exists

**Setup:**
```bash
# Remove reports directory
rm -rf .ignorar/production-reports/code-reviewer
```

**Expected Behavior:**
- Exit code: 0 (PASS with graceful degradation)
- Output: ⚠️ WARNING message about missing directory
- Message includes: "Primera vez ejecutando verificación - se permite commit"
- Displays threshold: ">= 9.0/10"

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 2: Empty Reports Directory

**Setup:**
```bash
# Create empty directory
mkdir -p .ignorar/production-reports/code-reviewer
```

**Expected Behavior:**
- Exit code: 0 (PASS with graceful degradation)
- Output: ⚠️ WARNING message about no reports found
- Message includes: "Primera vez ejecutando verificación - se permite commit"
- Displays threshold: ">= 9.0/10"

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 3: Report with Score 9.5 (PASS)

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

cat > .ignorar/production-reports/code-reviewer/phase-3/2026-02-09-143000-phase-3-code-reviewer-domain-layer.md << 'EOF'
# Code Review Report

## Summary

Module reviewed successfully with high quality.

## Overall Score: 9.5/10

**Breakdown:**
- Complexity & Maintainability: 4/4
- DRY & Duplication: 2/2
- Naming & Clarity: 2/2
- Performance: 1/1
- Testing: 0.5/1

## Findings

No critical issues found.
EOF
```

**Expected Behavior:**
- Exit code: 0 (PASS)
- Output: "✅ PASS: Score 9.5/10 cumple con threshold >= 9.0/10"
- Displays detected score: "📊 Score detectado: 9.5/10"
- Displays threshold: "🎯 Threshold requerido: >= 9.0/10"

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 4: Report with Score 8.5 (FAIL)

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

cat > .ignorar/production-reports/code-reviewer/phase-3/2026-02-09-143000-phase-3-code-reviewer-domain-layer.md << 'EOF'
# Code Review Report

## Summary

Module has quality issues that need addressing.

## Overall Score: 8.5/10

**Breakdown:**
- Complexity & Maintainability: 3/4
- DRY & Duplication: 2/2
- Naming & Clarity: 1.5/2
- Performance: 1/1
- Testing: 1/1

## Findings

- HIGH: Cyclomatic complexity exceeds 10 in function `process_data()`
- MEDIUM: Inconsistent naming conventions
EOF
```

**Expected Behavior:**
- Exit code: 1 (FAIL)
- Output: "❌ FAIL: Score 8.5/10 NO cumple con threshold >= 9.0/10"
- Displays detected score: "📊 Score detectado: 8.5/10"
- Displays action items:
  1. Review report path
  2. Correct quality issues
  3. Execute /verify
  4. Try commit again

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 5: Report with Unparseable Score (WARN)

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

cat > .ignorar/production-reports/code-reviewer/phase-3/2026-02-09-143000-phase-3-code-reviewer-domain-layer.md << 'EOF'
# Code Review Report

## Summary

This report uses a non-standard format.

## Quality Assessment

The code is excellent and meets all standards.

## Recommendations

Continue following best practices.
EOF
```

**Expected Behavior:**
- Exit code: 0 (PASS with graceful degradation)
- Output: ⚠️ WARNING message about unparseable score
- Message includes: "Se permite commit (graceful degradation - parsing failed)"
- Recommendation: Add "Overall Score: X.X/10" format

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 6: Multiple Reports (Should Pick Most Recent)

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

# Older report with FAIL score
cat > .ignorar/production-reports/code-reviewer/phase-3/2026-02-08-100000-phase-3-code-reviewer-old.md << 'EOF'
# Code Review Report
## Overall Score: 7.5/10
EOF

# Newer report with PASS score
cat > .ignorar/production-reports/code-reviewer/phase-3/2026-02-09-143000-phase-3-code-reviewer-new.md << 'EOF'
# Code Review Report
## Overall Score: 9.2/10
EOF
```

**Expected Behavior:**
- Exit code: 0 (PASS)
- Output: Uses score from most recent report (9.2/10)
- Displays: "📄 Reporte más reciente: 2026-02-09-143000-phase-3-code-reviewer-new.md"
- Confirms PASS with score 9.2/10

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 7: Alternative Score Formats

**Setup:**
Test various score format patterns that the script should handle:

```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

# Format 1: "Score: X.X/10"
cat > .ignorar/production-reports/code-reviewer/phase-3/format1.md << 'EOF'
# Report
Score: 9.1/10
EOF

# Format 2: "Overall: X.X/10"
cat > .ignorar/production-reports/code-reviewer/phase-3/format2.md << 'EOF'
# Report
Overall: 9.3/10
EOF

# Format 3: "**Overall Score:** X.X/10"
cat > .ignorar/production-reports/code-reviewer/phase-3/format3.md << 'EOF'
# Report
**Overall Score:** 9.4/10
EOF

# Format 4: "Overall Score: X.X out of 10"
cat > .ignorar/production-reports/code-reviewer/phase-3/format4.md << 'EOF'
# Report
Overall Score: 9.6 out of 10
EOF
```

**Expected Behavior:**
- All formats should be recognized
- Score should be correctly extracted
- Exit code: 0 (all are PASS scores)

**Test Commands:**
```bash
# Test each format
for report in .ignorar/production-reports/code-reviewer/phase-3/format*.md; do
    echo "Testing: $report"
    CLAUDE_PROJECT_DIR=. bash -c "REPORTS_DIR='.ignorar/production-reports/code-reviewer' find '$REPORTS_DIR' -name '$(basename $report)' -exec ./claude/scripts/check-reviewer-score.sh {} \;"
done
```

---

### Scenario 8: Edge Case - Score Exactly 9.0 (Boundary Test)

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

cat > .ignorar/production-reports/code-reviewer/phase-3/boundary.md << 'EOF'
# Code Review Report
## Overall Score: 9.0/10
EOF
```

**Expected Behavior:**
- Exit code: 0 (PASS - boundary is inclusive)
- Output: "✅ PASS: Score 9.0/10 cumple con threshold >= 9.0/10"

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

### Scenario 9: Edge Case - Invalid Score Format

**Setup:**
```bash
mkdir -p .ignorar/production-reports/code-reviewer/phase-3

cat > .ignorar/production-reports/code-reviewer/phase-3/invalid.md << 'EOF'
# Code Review Report
## Overall Score: invalid/10
EOF
```

**Expected Behavior:**
- Exit code: 0 (PASS with graceful degradation)
- Output: ⚠️ WARNING about invalid number format
- Message includes: "Score extraído no es un número válido"

**Test Command:**
```bash
./claude/scripts/check-reviewer-score.sh
echo "Exit code: $?"
```

---

## Automated Test Suite

### Shell Script Test Runner

Create a test runner that automates all scenarios:

```bash
#!/usr/bin/env bash
# test-check-reviewer-score.sh - Automated test suite

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/.test-tmp"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

setup() {
    echo "Setting up test environment..."
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR/.ignorar/production-reports/code-reviewer/phase-3"
    export CLAUDE_PROJECT_DIR="$TEST_DIR"
}

teardown() {
    echo "Cleaning up test environment..."
    rm -rf "$TEST_DIR"
}

run_test() {
    local test_name=$1
    local expected_exit_code=$2
    local setup_func=$3

    echo -e "\n${YELLOW}Running: $test_name${NC}"

    # Run setup
    $setup_func

    # Run script
    local output
    local exit_code
    output=$("$PROJECT_ROOT/.claude/scripts/check-reviewer-score.sh" 2>&1) || exit_code=$?
    exit_code=${exit_code:-0}

    # Check result
    if [ "$exit_code" -eq "$expected_exit_code" ]; then
        echo -e "${GREEN}✓ PASS${NC}: Exit code $exit_code (expected $expected_exit_code)"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: Exit code $exit_code (expected $expected_exit_code)"
        ((FAILED++))
    fi

    echo "$output"
}

# Test scenario functions
test_no_directory() {
    rm -rf "$TEST_DIR/.ignorar/production-reports/code-reviewer"
}

test_empty_directory() {
    mkdir -p "$TEST_DIR/.ignorar/production-reports/code-reviewer"
}

test_pass_score() {
    cat > "$TEST_DIR/.ignorar/production-reports/code-reviewer/phase-3/report.md" << 'EOF'
# Code Review Report
## Overall Score: 9.5/10
EOF
}

test_fail_score() {
    cat > "$TEST_DIR/.ignorar/production-reports/code-reviewer/phase-3/report.md" << 'EOF'
# Code Review Report
## Overall Score: 8.5/10
EOF
}

test_unparseable() {
    cat > "$TEST_DIR/.ignorar/production-reports/code-reviewer/phase-3/report.md" << 'EOF'
# Code Review Report
No score here!
EOF
}

# Run all tests
setup

run_test "Scenario 1: No reports directory" 0 test_no_directory
run_test "Scenario 2: Empty directory" 0 test_empty_directory
run_test "Scenario 3: PASS score (9.5)" 0 test_pass_score
run_test "Scenario 4: FAIL score (8.5)" 1 test_fail_score
run_test "Scenario 5: Unparseable score" 0 test_unparseable

teardown

echo -e "\n${YELLOW}========================================${NC}"
echo -e "${GREEN}PASSED: $PASSED${NC}"
echo -e "${RED}FAILED: $FAILED${NC}"
echo -e "${YELLOW}========================================${NC}"

exit $FAILED
```

---

## Integration with Pre-Commit Hook

The script is called from `.claude/hooks/pre-git-commit.sh`:

```bash
# Check code-reviewer score (after pending files check)
if ! ./.claude/scripts/check-reviewer-score.sh; then
    echo ""
    echo "COMMIT BLOQUEADO: Code reviewer score no cumple con threshold >= 9.0/10."
    exit 1
fi
```

---

## Notes

1. **Graceful Degradation**: The script allows commits when:
   - No reports directory exists (first-time setup)
   - No reports found (first-time verification)
   - Score cannot be parsed (format issue, not quality issue)

2. **Pattern Matching**: The script supports multiple score formats to handle variations in report generation

3. **Float Comparison**: Uses `awk` for floating-point comparison since bash doesn't support native float arithmetic

4. **Timestamp Ordering**: Uses `sort -r` on filenames to find the most recent report (relies on ISO 8601 timestamp format in filename)

5. **Exit Codes**:
   - 0 = PASS or graceful degradation
   - 1 = FAIL (score < 9.0/10)
