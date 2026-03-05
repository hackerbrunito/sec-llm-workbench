#!/usr/bin/env bash
# scan-git-history-for-secrets.sh
# One-time scan of git history for accidentally committed secrets.
# Scans ALL commits in git log for common secret patterns.
# Usage: bash .claude/scripts/scan-git-history-for-secrets.sh [project-path]
# If project-path is omitted, uses .build/active-project

set -euo pipefail

# Resolve target project path
TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    TARGET=$(cat .build/active-project 2>/dev/null || echo "")
    TARGET="${TARGET/#\~/$HOME}"
fi

if [ -z "$TARGET" ] || [ ! -d "$TARGET" ]; then
    echo "ERROR: Target project path not found. Pass it as argument or set .build/active-project"
    exit 1
fi

if [ ! -d "$TARGET/.git" ]; then
    echo "ERROR: $TARGET is not a git repository"
    exit 1
fi

echo "Scanning git history for secrets in: $TARGET"
echo "This may take a moment for large repos..."
echo ""

FINDINGS=0
REPORT_FILE="/tmp/secrets-history-scan-$(date +%Y%m%d-%H%M%S).txt"

# Secret patterns to search for in git history
# Format: description|regex_pattern
PATTERNS=(
    "AWS Access Key|AKIA[0-9A-Z]{16}"
    "AWS Secret Key|[aA]ws.{0,20}['\"][0-9a-zA-Z/+]{40}['\"]"
    "Generic API Key|api[_-]?key['\"\s]*[:=]['\"\s]*[0-9a-zA-Z\-_]{20,}"
    "Generic Secret|secret['\"\s]*[:=]['\"\s]*[0-9a-zA-Z\-_]{20,}"
    "Generic Password|password['\"\s]*[:=]['\"\s]*[^\s]{8,}"
    "Private Key Header|-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
    "GitHub Token|gh[pousr]_[0-9a-zA-Z]{36,}"
    "Anthropic API Key|sk-ant-[a-zA-Z0-9\-_]{40,}"
    "OpenAI API Key|sk-[a-zA-Z0-9]{48}"
    "Slack Token|xox[baprs]-[0-9a-zA-Z\-]+"
    "Hardcoded Bearer Token|[Bb]earer [0-9a-zA-Z\-_.]{20,}"
    "Database URL with credentials|[a-z]+://[^:]+:[^@]+@[a-z0-9\-.]+"
    "Hex encoded secret (32+ chars)|[0-9a-f]{32,}"
)

{
echo "Git History Secrets Scan Report"
echo "================================"
echo "Target: $TARGET"
echo "Date: $(date)"
echo ""
} >> "$REPORT_FILE"

cd "$TARGET"

for pattern_entry in "${PATTERNS[@]}"; do
    description="${pattern_entry%%|*}"
    pattern="${pattern_entry##*|}"

    matches=$(git log -p --all --full-history -- . 2>/dev/null | grep -E "$pattern" | grep -v "^Binary" | head -20 || true)

    if [ -n "$matches" ]; then
        FINDINGS=$((FINDINGS + 1))
        echo "  [FOUND] $description"
        {
        echo "## $description"
        echo "Pattern: $pattern"
        echo "Matches (first 20):"
        echo "$matches" | head -20
        echo ""
        } >> "$REPORT_FILE"
    fi
done

echo ""
echo "================================"
if [ "$FINDINGS" -gt 0 ]; then
    echo "RESULT: $FINDINGS secret pattern(s) found in git history."
    echo "Review $REPORT_FILE for details."
    echo ""
    echo "To remove secrets from git history, use:"
    echo "  git filter-repo --path <file> --invert-paths"
    echo "  OR: BFG Repo Cleaner (https://rtyley.github.io/bfg-repo-cleaner/)"
    echo ""
    echo "IMPORTANT: After removing from history, rotate all exposed credentials immediately."
    exit 1
else
    echo "RESULT: No secret patterns found in git history. CLEAN."
    exit 0
fi
