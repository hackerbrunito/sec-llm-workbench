#!/usr/bin/env bash
# Pre-Git-Commit Hook - Bloquea commit si hay archivos sin verificar
# Este hook se ejecuta ANTES de cualquier comando Bash
# Solo actua si el comando es "git commit"
# Output format: hookSpecificOutput (verified via Context7 2026-01-27)

set -euo pipefail

# Leer JSON de stdin
INPUT=$(cat)

# Extraer el comando del JSON
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# Si no es un comando git commit, permitir
if [[ "$COMMAND" != *"git commit"* ]]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
EOF
    exit 0
fi

# Es un git commit - verificar markers pendientes
VERIFICATION_DIR="${CLAUDE_PROJECT_DIR:-.}/.build/checkpoints/pending"

# Si no existe el directorio, no hay nada pendiente
if [ ! -d "$VERIFICATION_DIR" ]; then
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
EOF
    exit 0
fi

# Contar archivos pendientes de verificacion
PENDING_COUNT=$(find "$VERIFICATION_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$PENDING_COUNT" -gt 0 ]; then
    # Obtener lista de archivos pendientes
    PENDING_FILES=""
    for marker in "$VERIFICATION_DIR"/*; do
        if [ -f "$marker" ]; then
            FILE_PATH=$(jq -r '.file' "$marker" 2>/dev/null || echo "unknown")
            PENDING_FILES="${PENDING_FILES}- ${FILE_PATH}\n"
        fi
    done

    # Bloquear commit
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "COMMIT BLOQUEADO: Hay ${PENDING_COUNT} archivo(s) Python sin verificar por agentes. Archivos pendientes: ${PENDING_FILES}ACCION REQUERIDA: Ejecuta /verify para correr los agentes de verificacion, despues intenta commit de nuevo."
  }
}
EOF
    exit 0
fi

# Todo verificado, permitir commit
cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow"
  }
}
EOF
exit 0
