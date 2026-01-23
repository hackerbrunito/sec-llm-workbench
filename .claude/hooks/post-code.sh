#!/bin/bash
# =============================================================================
# Post-Code Hook - META-PROYECTO
# =============================================================================
# Ejecutado automáticamente después de Write/Edit en archivos Python
# Recibe JSON via stdin con información del archivo editado
# =============================================================================

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

# Si no encontramos pyproject.toml, salir
if [ ! -f "$PROJECT_DIR/pyproject.toml" ]; then
    exit 0
fi

cd "$PROJECT_DIR"

# Formatear y verificar el archivo
uv run ruff format "$FILE_PATH" 2>/dev/null || true
uv run ruff check "$FILE_PATH" --fix 2>/dev/null || true

exit 0
