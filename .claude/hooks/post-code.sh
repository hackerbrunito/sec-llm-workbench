#!/usr/bin/env bash
# =============================================================================
# Post-Code Hook - META-PROYECTO
# =============================================================================
# Ejecutado automáticamente después de Write/Edit
# 1. Formatea código con ruff
# 2. Marca archivo como "pendiente de verificación por agentes"
# =============================================================================

set -euo pipefail

# Leer JSON de stdin
INPUT=$(cat)

# Extraer file_path del JSON
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Si no hay file_path, salir
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Solo procesar archivos Python
if [[ "$FILE_PATH" != *.py ]]; then
    exit 0
fi

# No procesar archivos del META-PROYECTO
META_PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
if [ -n "$META_PROJECT_DIR" ] && [[ "$FILE_PATH" == "$META_PROJECT_DIR"* ]]; then
    exit 0
fi

# Verificar que el archivo existe
if [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Obtener directorio del proyecto (buscar pyproject.toml hacia arriba)
PROJECT_DIR=$(dirname "$FILE_PATH")
while [ "$PROJECT_DIR" != "/" ]; do
    if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
        break
    fi
    PROJECT_DIR=$(dirname "$PROJECT_DIR")
done

# Si encontramos pyproject.toml, formatear
if [ -f "$PROJECT_DIR/pyproject.toml" ]; then
    cd "$PROJECT_DIR"
    uv run ruff format "$FILE_PATH" 2>/dev/null || true
    uv run ruff check "$FILE_PATH" --fix 2>/dev/null || true
fi

# =============================================================================
# SISTEMA DE VERIFICACIÓN PENDIENTE
# =============================================================================
# Marcar que este archivo necesita verificación por agentes antes de commit

VERIFICATION_DIR="${CLAUDE_PROJECT_DIR:-.}/.build/checkpoints/pending"
mkdir -p "$VERIFICATION_DIR"

# Crear marker con hash del archivo para tracking
FILE_HASH=$(echo "$FILE_PATH" | if command -v md5sum &>/dev/null; then md5sum; else md5; fi | cut -c1-8)
MARKER_FILE="$VERIFICATION_DIR/$FILE_HASH"

# Guardar info del archivo pendiente
cat > "$MARKER_FILE" << EOF
{
  "file": "$FILE_PATH",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "verified": false
}
EOF

exit 0
