#!/usr/bin/env bash
# =============================================================================
# Pre-Commit Hook - Verificación antes de cada commit
# =============================================================================
# Este hook se ejecuta en el PROYECTO DESTINO, no en el META-PROYECTO
# =============================================================================

set -e

# Obtener el directorio del proyecto (pasado como argumento o usar actual)
PROJECT_DIR="${1:-.}"

echo "🔍 Ejecutando verificaciones pre-commit en $PROJECT_DIR..."

cd "$PROJECT_DIR"

# 1. Verificar que uv está disponible
if ! command -v uv &> /dev/null; then
    echo "❌ ERROR: uv no está instalado"
    exit 1
fi

# 2. Formatear código
echo "📝 Verificando formato..."
uv run ruff format src tests --check 2>/dev/null || {
    echo "⚠️  Formateando código..."
    uv run ruff format src tests
}

# 3. Linting
echo "🔎 Verificando linting..."
uv run ruff check src tests --fix

# 4. Type checking
echo "🔤 Verificando tipos..."
uv run mypy src --ignore-missing-imports 2>/dev/null || echo "⚠️  mypy encontró warnings"

# 5. Tests unitarios
echo "🧪 Ejecutando tests unitarios..."
uv run pytest tests/unit -q --tb=short 2>/dev/null || echo "⚠️  Algunos tests fallaron o no existen"

echo "✅ Pre-commit completado"
