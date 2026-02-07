#!/usr/bin/env bash
# =============================================================================
# Session Start Hook - META-PROYECTO
# =============================================================================
# Inicializa sesión y sistema de trazabilidad

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Use CLAUDE_SESSION_ID env var (Anthropic standard), fallback to timestamp
SESSION_ID="${CLAUDE_SESSION_ID:-local-$(date +%Y%m%d-%H%M%S)}"

# =============================================================================
# DEPENDENCY CHECKS - Verify required tools
# =============================================================================

check_command() {
    local cmd="$1"
    local description="$2"

    if ! command -v "$cmd" &> /dev/null; then
        echo "ERROR: Required command '$cmd' not found: $description"
        echo ""
        case "$cmd" in
            uv)
                echo "Install uv (Python package manager):"
                echo "  macOS: brew install uv"
                echo "  Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
                ;;
            ruff)
                echo "Install ruff (Python linter):"
                echo "  macOS: brew install ruff"
                echo "  Linux: pip install ruff"
                ;;
            mypy)
                echo "Install mypy (Python type checker):"
                echo "  macOS: brew install mypy"
                echo "  Linux: pip install mypy"
                ;;
            pytest)
                echo "Install pytest (Python test framework):"
                echo "  macOS: brew install pytest"
                echo "  Linux: pip install pytest"
                ;;
        esac
        echo ""
        exit 1
    fi
}

# Check for required dependencies
check_command "uv" "Python package manager (uv)"
check_command "ruff" "Python linter and formatter (ruff)"
check_command "mypy" "Python static type checker (mypy)"
check_command "pytest" "Python test framework (pytest)"

# =============================================================================
# ENVIRONMENT VALIDATION - Check for required API keys
# =============================================================================

if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
    echo "INFO: Creating .env from .env.example"
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

# Load .env file if it exists
if [ -f "$PROJECT_DIR/.env" ]; then
    set +o allexport
    source "$PROJECT_DIR/.env" || true
    set -o allexport
fi

# Check for UPSTASH_API_KEY if Context7 is referenced
if grep -r "Context7\|context7" "$PROJECT_DIR/.claude/agents" &>/dev/null 2>&1; then
    if [ -z "${UPSTASH_API_KEY:-}" ]; then
        echo "WARNING: UPSTASH_API_KEY not set. Context7 features will be unavailable."
        echo "See .env.example for setup instructions."
    fi
fi


# =============================================================================
# LOG ROTATION - Keep 30-day rolling window
# =============================================================================

rotate_logs() {
    local log_dir="$1"
    local max_age_days=30

    if [ ! -d "$log_dir" ]; then
        return 0
    fi

    # Find and compress logs older than 7 days (keep compressed for archival)
    find "$log_dir" -name "*.log" -o -name "*.jsonl" -o -name "*.json" | while read -r file; do
        if [ -f "$file" ]; then
            file_age=$(( ($(date +%s) - $(stat -c %Y "$file" 2>/dev/null || stat -f %m "$file")) / 86400 ))

            # Compress if older than 7 days
            if [ "$file_age" -gt 7 ] && [ ! -f "${file}.gz" ]; then
                if command -v gzip &> /dev/null; then
                    gzip -f "$file" 2>/dev/null || true
                fi
            fi

            # Delete if older than max_age_days
            if [ "$file_age" -gt "$max_age_days" ]; then
                rm -f "$file" "${file}.gz" 2>/dev/null || true
            fi
        fi
    done
}

# =============================================================================
# SISTEMA DE TRAZABILIDAD - Inicializar logs
# =============================================================================

LOGS_DIR="$PROJECT_DIR/.build/logs"
mkdir -p "$LOGS_DIR/agents"
mkdir -p "$LOGS_DIR/sessions"
mkdir -p "$LOGS_DIR/decisions"
mkdir -p "$LOGS_DIR/reports"

# Run log rotation on agents, sessions, and decisions directories
rotate_logs "$LOGS_DIR/agents"
rotate_logs "$LOGS_DIR/sessions"
rotate_logs "$LOGS_DIR/decisions"

# Crear directorios de checkpoints (requeridos por post-code.sh y pre-git-commit.sh)
mkdir -p "$PROJECT_DIR/.build/checkpoints/pending"
mkdir -p "$PROJECT_DIR/.build/checkpoints/daily"

# Crear resumen de sesión
DATE=$(date +%Y-%m-%d)
SESSION_FILE="$LOGS_DIR/sessions/${DATE}-${SESSION_ID}.json"

cat > "$SESSION_FILE" << EOF
{
  "session_id": "$SESSION_ID",
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "project_dir": "$PROJECT_DIR",
  "agents_invoked": 0,
  "decisions": 0,
  "commits": 0
}
EOF

# Persist session_id so other hooks can read it
echo "$SESSION_ID" > "$PROJECT_DIR/.build/current-session-id"

# =============================================================================
# STATE FILES - Detectar proyecto activo y fase actual
# =============================================================================

validate_project_schema() {
    local project_file="$1"
    local schema_file="$PROJECT_DIR/projects/schema.json"

    if [ ! -f "$schema_file" ]; then
        return 0  # Skip validation if schema doesn't exist
    fi

    if ! command -v jq &> /dev/null; then
        return 0  # Skip if jq not available
    fi

    # Validate using jq (basic validation)
    if jq -e '.name and .phase and .status' "$project_file" &>/dev/null; then
        # Check valid status values
        local status=$(jq -r '.status' "$project_file")
        if ! echo "$status" | grep -qE '^(not_started|in_progress|paused|completed|archived)$'; then
            echo "ERROR: Invalid status '$status' in $project_file"
            echo "Valid values: not_started, in_progress, paused, completed, archived"
            exit 1
        fi
        return 0
    else
        echo "ERROR: Project file $project_file missing required fields (name, phase, status)"
        exit 1
    fi
}

# Buscar proyecto activo en projects/*.json
PROJECTS_DIR="$PROJECT_DIR/projects"
if [ -d "$PROJECTS_DIR" ]; then
    PROJECT_COUNT=$(find "$PROJECTS_DIR" -name '*.json' -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$PROJECT_COUNT" -eq 1 ]; then
        PROJECT_FILE=$(find "$PROJECTS_DIR" -name '*.json' -type f 2>/dev/null | head -1)

        # Validate project schema
        validate_project_schema "$PROJECT_FILE"

        PROJECT_NAME=$(jq -r '.project.name // empty' "$PROJECT_FILE" 2>/dev/null)
        CURRENT_PHASE=$(jq -r '.currentPhase // empty' "$PROJECT_FILE" 2>/dev/null)

        if [ -n "$PROJECT_NAME" ]; then
            echo "$PROJECT_NAME" > "$PROJECT_DIR/.build/active-project"
        fi
        if [ -n "$CURRENT_PHASE" ]; then
            echo "$CURRENT_PHASE" > "$PROJECT_DIR/.build/current-phase"
        fi
    fi
fi

exit 0
