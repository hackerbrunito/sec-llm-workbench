#!/usr/bin/env bash
# =============================================================================
# Session Start Hook - META-PROYECTO
# =============================================================================

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Crear .env del META-PROYECTO si no existe
if [ ! -f "$PROJECT_DIR/.env" ] && [ -f "$PROJECT_DIR/.env.example" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
fi

exit 0
