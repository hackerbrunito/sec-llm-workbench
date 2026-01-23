#!/bin/bash
# =============================================================================
# Verificar Best Practices Python 2026
# =============================================================================
# Verifica que el código sigue las mejores prácticas modernas
# =============================================================================

set -e

PROJECT_DIR="${1:-.}"
ERRORS=0

echo "🎯 Verificando mejores prácticas en $PROJECT_DIR..."

cd "$PROJECT_DIR"

# 1. Type hints legacy (List, Dict, Optional)
echo "🔍 Verificando type hints..."
if grep -rn "from typing import List\|from typing import Dict\|from typing import Optional" src/ 2>/dev/null; then
    echo "❌ ERROR: Type hints legacy detectados"
    echo "   Usar: list[str], dict[str, int], X | None"
    ERRORS=$((ERRORS + 1))
fi

# 2. Pydantic v1 patterns
echo "🔍 Verificando Pydantic v2..."
if grep -rn "class Config:" src/ 2>/dev/null | grep -v "ConfigDict" | grep -v "#"; then
    echo "❌ ERROR: Pydantic v1 pattern detectado (class Config)"
    echo "   Usar: model_config = ConfigDict(...)"
    ERRORS=$((ERRORS + 1))
fi

if grep -rn "@validator(" src/ 2>/dev/null; then
    echo "❌ ERROR: @validator detectado (Pydantic v1)"
    echo "   Usar: @field_validator con @classmethod"
    ERRORS=$((ERRORS + 1))
fi

# 3. requests (sync HTTP)
echo "🔍 Verificando HTTP async..."
if grep -rn "^import requests$\|^from requests import" src/ 2>/dev/null; then
    echo "❌ ERROR: requests (sync) detectado"
    echo "   Usar: httpx con async"
    ERRORS=$((ERRORS + 1))
fi

# 4. os.path
echo "🔍 Verificando pathlib..."
if grep -rn "os\.path\." src/ 2>/dev/null; then
    echo "❌ ERROR: os.path detectado"
    echo "   Usar: pathlib.Path"
    ERRORS=$((ERRORS + 1))
fi

# 5. print statements (excepto en CLI/debug)
echo "🔍 Verificando logging..."
if grep -rn "^\s*print(" src/ 2>/dev/null | grep -v "cli.py" | grep -v "# debug"; then
    echo "⚠️  WARNING: print() detectado"
    echo "   Considerar usar: structlog"
fi

# Resultado
if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ FAILED: $ERRORS errores de best practices"
    exit 1
else
    echo ""
    echo "✅ Best practices OK"
fi
