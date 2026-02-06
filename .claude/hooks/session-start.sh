#!/usr/bin/env bash
# =============================================================================
# Session Start Hook - META-PROYECTO
# =============================================================================
# Inicializa sesión y sistema de trazabilidad

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Leer JSON de stdin para obtener session_id
INPUT=$(cat)
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty' 2>/dev/null)

# Si no hay session_id, generar uno basado en timestamp
if [ -z "$SESSION_ID" ]; then
    SESSION_ID="local-$(date +%Y%m%d-%H%M%S)"
fi

# Crear .env del META-PROYECTO si no existe
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

# =============================================================================
# SISTEMA DE TRAZABILIDAD - Inicializar logs
# =============================================================================

LOGS_DIR="$PROJECT_DIR/.build/logs"
mkdir -p "$LOGS_DIR/agents"
mkdir -p "$LOGS_DIR/sessions"
mkdir -p "$LOGS_DIR/decisions"
mkdir -p "$LOGS_DIR/reports"

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

exit 0
