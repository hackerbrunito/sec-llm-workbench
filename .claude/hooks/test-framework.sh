#!/usr/bin/env bash
# Framework self-testing script
# Validates Claude Code framework configuration integrity
set -euo pipefail

# Resolve project root relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLAUDE_DIR="$PROJECT_ROOT/.claude"

PASS=0
FAIL=0

echo "=== Framework Validation ==="

pass() {
  echo "[PASS] $1"
  PASS=$((PASS + 1))
}

fail() {
  echo "[FAIL] $1"
  FAIL=$((FAIL + 1))
}

# ============================================================
# 1. settings.json structure
# ============================================================

SETTINGS="$CLAUDE_DIR/settings.json"

if [ ! -f "$SETTINGS" ]; then
  fail "settings.json: file not found"
else
  # Check permissions.deny exists and is an array
  if jq -e '.permissions.deny | type == "array"' "$SETTINGS" > /dev/null 2>&1; then
    pass "settings.json: permissions.deny exists (array)"
  else
    fail "settings.json: missing or invalid permissions.deny"
  fi

  # Check permissions.ask exists and is an array
  if jq -e '.permissions.ask | type == "array"' "$SETTINGS" > /dev/null 2>&1; then
    pass "settings.json: permissions.ask exists (array)"
  else
    fail "settings.json: missing or invalid permissions.ask"
  fi

  # Check permissions.allow exists and is an array
  if jq -e '.permissions.allow | type == "array"' "$SETTINGS" > /dev/null 2>&1; then
    pass "settings.json: permissions.allow exists (array)"
  else
    fail "settings.json: missing or invalid permissions.allow"
  fi

  # Check sandbox.enabled is true
  if jq -e '.sandbox.enabled == true' "$SETTINGS" > /dev/null 2>&1; then
    pass "settings.json: sandbox.enabled is true"
  else
    fail "settings.json: sandbox.enabled is not true"
  fi

  # Check attribution.commit is set
  if jq -e '.attribution.commit != null and .attribution.commit != ""' "$SETTINGS" > /dev/null 2>&1; then
    COMMIT_VAL=$(jq -r '.attribution.commit' "$SETTINGS")
    pass "settings.json: attribution.commit set to '$COMMIT_VAL'"
  else
    fail "settings.json: attribution.commit not set"
  fi
fi

# ============================================================
# 2. Agent YAML frontmatter validation
# ============================================================

AGENTS_DIR="$CLAUDE_DIR/agents"
VALID_MODELS="sonnet haiku opus"
REQUIRED_AGENT_FIELDS="name description tools model memory"

for agent_file in "$AGENTS_DIR"/*.md; do
  basename_file=$(basename "$agent_file")

  if [ ! -f "$agent_file" ]; then
    fail "agent $basename_file: file not found"
    continue
  fi

  # Extract YAML frontmatter (between first pair of ---)
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$agent_file" | sed '1d;$d')

  if [ -z "$frontmatter" ]; then
    fail "agent $basename_file: no YAML frontmatter found"
    continue
  fi

  # Check each required field
  for field in $REQUIRED_AGENT_FIELDS; do
    value=$(echo "$frontmatter" | grep "^${field}:" | head -1 | sed "s/^${field}:[[:space:]]*//" | sed 's/^"//' | sed 's/"$//')
    if [ -z "$value" ]; then
      fail "agent $basename_file: missing '$field' field"
    else
      # Additional checks for specific fields
      case "$field" in
        memory)
          if [ "$value" = "project" ]; then
            pass "agent $basename_file: memory is 'project'"
          else
            fail "agent $basename_file: memory is '$value', expected 'project'"
          fi
          ;;
        model)
          if echo "$VALID_MODELS" | grep -qw "$value"; then
            pass "agent $basename_file: model '$value' is valid"
          else
            fail "agent $basename_file: model '$value' is not one of: $VALID_MODELS"
          fi
          ;;
        *)
          pass "agent $basename_file: has '$field' field"
          ;;
      esac
    fi
  done
done

# ============================================================
# 3. Skill YAML frontmatter validation
# ============================================================

SKILLS_DIR="$CLAUDE_DIR/skills"
REQUIRED_SKILL_FIELDS="name description"

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_file="$skill_dir/SKILL.md"
  skill_name=$(basename "$skill_dir")

  if [ ! -f "$skill_file" ]; then
    fail "skill $skill_name: SKILL.md not found"
    continue
  fi

  # Extract YAML frontmatter
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$skill_file" | sed '1d;$d')

  if [ -z "$frontmatter" ]; then
    fail "skill $skill_name: no YAML frontmatter found"
    continue
  fi

  # Check required fields
  for field in $REQUIRED_SKILL_FIELDS; do
    value=$(echo "$frontmatter" | grep "^${field}:" | head -1 | sed "s/^${field}:[[:space:]]*//" | sed 's/^"//' | sed 's/"$//')
    if [ -z "$value" ]; then
      fail "skill $skill_name: missing '$field' field"
    else
      pass "skill $skill_name: has '$field' field"
    fi
  done

  # Check for context: fork OR disable-model-invocation
  has_context_fork=$(echo "$frontmatter" | grep -c "^context:.*fork" || true)
  has_disable_model=$(echo "$frontmatter" | grep -c "^disable-model-invocation:" || true)
  has_user_invocable_false=$(echo "$frontmatter" | grep -c "^user-invocable:.*false" || true)

  if [ "$has_context_fork" -gt 0 ] || [ "$has_disable_model" -gt 0 ] || [ "$has_user_invocable_false" -gt 0 ]; then
    pass "skill $skill_name: has context:fork, disable-model-invocation, or user-invocable:false"
  else
    fail "skill $skill_name: missing context:fork or disable-model-invocation"
  fi
done

# ============================================================
# 4. Workflow files validation
# ============================================================

WORKFLOW_DIR="$CLAUDE_DIR/workflow"
WORKFLOW_FILES=(
  "01-session-start.md"
  "02-reflexion-loop.md"
  "03-human-checkpoints.md"
  "04-agents.md"
  "05-before-commit.md"
  "06-decisions.md"
  "07-orchestrator-invocation.md"
)

for wf in "${WORKFLOW_FILES[@]}"; do
  wf_path="$WORKFLOW_DIR/$wf"
  if [ ! -f "$wf_path" ]; then
    fail "workflow $wf: file not found"
  else
    pass "workflow $wf: exists"

    # Check for version header comment (<!-- version: ... -->)
    first_line=$(head -1 "$wf_path")
    if echo "$first_line" | grep -q '<!-- version:'; then
      pass "workflow $wf: has version header"
    else
      fail "workflow $wf: missing version header (expected '<!-- version: ... -->' on first line)"
    fi
  fi
done

# ============================================================
# 5. Cross-references validation
# ============================================================

# 5a. Agent names in 04-agents.md should match actual agent files
AGENTS_WORKFLOW="$WORKFLOW_DIR/04-agents.md"
if [ -f "$AGENTS_WORKFLOW" ]; then
  # Extract agent names referenced in the workflow file
  # Look for subagent_type="<name>" patterns (macOS-compatible, no -P flag)
  referenced_agents=$(grep -oE 'subagent_type="[^"]+"' "$AGENTS_WORKFLOW" 2>/dev/null \
    | sed 's/subagent_type="//' | sed 's/"$//' | sort -u)

  if [ -n "$referenced_agents" ]; then
    while IFS= read -r agent_name; do
      if [ -f "$AGENTS_DIR/${agent_name}.md" ]; then
        pass "cross-ref: agent '$agent_name' in 04-agents.md has matching file"
      else
        fail "cross-ref: agent '$agent_name' referenced in 04-agents.md but no $AGENTS_DIR/${agent_name}.md found"
      fi
    done <<< "$referenced_agents"
  else
    fail "cross-ref: could not extract agent references from 04-agents.md"
  fi

  # Also check agent names from table rows (| agent-name |)
  table_agents=$(grep -oE '\| (code-implementer|security-auditor|hallucination-detector|code-reviewer|test-generator|best-practices-enforcer|vulnerability-researcher|xai-explainer) ' "$AGENTS_WORKFLOW" 2>/dev/null | sed 's/^| //' | sed 's/ $//' | sort -u)
  if [ -n "$table_agents" ]; then
    while IFS= read -r agent_name; do
      if [ -f "$AGENTS_DIR/${agent_name}.md" ]; then
        pass "cross-ref: agent '$agent_name' in 04-agents.md table has matching file"
      else
        fail "cross-ref: agent '$agent_name' in 04-agents.md table but no file found"
      fi
    done <<< "$table_agents"
  fi
else
  fail "cross-ref: 04-agents.md not found"
fi

# 5b. Skills referenced in agent files should exist
for agent_file in "$AGENTS_DIR"/*.md; do
  basename_file=$(basename "$agent_file")
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$agent_file" | sed '1d;$d')

  # Extract skills field: skills: [skill1, skill2]
  skills_line=$(echo "$frontmatter" | grep "^skills:" || true)
  if [ -n "$skills_line" ]; then
    # Parse skills list from [skill1, skill2] format
    skills=$(echo "$skills_line" | sed 's/skills:[[:space:]]*\[//' | sed 's/\]//' | tr ',' '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    while IFS= read -r skill_name; do
      if [ -z "$skill_name" ]; then
        continue
      fi
      if [ -d "$SKILLS_DIR/$skill_name" ] && [ -f "$SKILLS_DIR/$skill_name/SKILL.md" ]; then
        pass "cross-ref: skill '$skill_name' referenced in $basename_file exists"
      else
        fail "cross-ref: skill '$skill_name' referenced in $basename_file but not found in $SKILLS_DIR/"
      fi
    done <<< "$skills"
  fi
done

# ============================================================
# Results
# ============================================================

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi

exit 0
