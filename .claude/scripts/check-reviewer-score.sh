#!/usr/bin/env bash
# check-reviewer-score.sh - Verificar score de code-reviewer contra threshold
# Reference: .claude/rules/verification-thresholds.md
# Exit codes: 0 = PASS (score >= 9.0), 1 = FAIL (score < 9.0), 0 with WARNING = no report found

set -euo pipefail

# Threshold definido en verification-thresholds.md
THRESHOLD=9.0

# Directorio base de reportes
REPORTS_DIR="${CLAUDE_PROJECT_DIR:-.}/.ignorar/production-reports/code-reviewer"

# Funcion para comparar floats (bash no tiene floats nativos)
compare_floats() {
    local score="$1"
    local threshold="$2"
    # Usar awk para comparacion de floats: 1 si score >= threshold, 0 en caso contrario
    awk -v s="$score" -v t="$threshold" 'BEGIN { if (s >= t) exit 0; else exit 1 }'
}

# Verificar si existe el directorio de reportes
if [ ! -d "$REPORTS_DIR" ]; then
    echo "⚠️  WARNING: No se encontró directorio de reportes code-reviewer ($REPORTS_DIR)"
    echo "   Primera vez ejecutando verificación - se permite commit (graceful degradation)"
    echo "   Threshold esperado: >= ${THRESHOLD}/10"
    exit 0
fi

# Buscar el reporte más reciente (por timestamp en el nombre del archivo)
# Formato esperado: YYYY-MM-DD-HHmmss-phase-N-code-reviewer-*.md
LATEST_REPORT=$(find "$REPORTS_DIR" -type f -name "*.md" 2>/dev/null | sort -r | head -n 1)

if [ -z "$LATEST_REPORT" ]; then
    echo "⚠️  WARNING: No se encontró ningún reporte de code-reviewer"
    echo "   Primera vez ejecutando verificación - se permite commit (graceful degradation)"
    echo "   Threshold esperado: >= ${THRESHOLD}/10"
    exit 0
fi

echo "📄 Reporte más reciente: $(basename "$LATEST_REPORT")"

# Intentar extraer el score del reporte
# Patrones comunes:
# - "Score: X.X/10"
# - "Overall: X.X/10"
# - "## Overall Score: X.X/10"
# - "**Overall Score:** X.X/10"
# - "Overall Score: X.X out of 10"

SCORE=""

# Intentar varios patrones en orden de especificidad
if grep -qE "(Overall Score|Score|SCORE).*[0-9]+\.[0-9]+.*(/10|out of 10)" "$LATEST_REPORT" 2>/dev/null; then
    # Extraer el primer número decimal encontrado después de "Score" o "Overall"
    SCORE=$(grep -iE "(Overall Score|Score)" "$LATEST_REPORT" | grep -oE "[0-9]+\.[0-9]+" | head -n 1)
fi

# Si no encontramos score con el patron anterior, intentar patrones más generales
if [ -z "$SCORE" ]; then
    # Buscar lineas que contengan "X.X/10" o "X/10"
    if grep -qE "[0-9]+(\.[0-9]+)?[[:space:]]*/[[:space:]]*10" "$LATEST_REPORT" 2>/dev/null; then
        SCORE=$(grep -oE "[0-9]+\.[0-9]+[[:space:]]*/[[:space:]]*10" "$LATEST_REPORT" | head -n 1 | grep -oE "^[0-9]+\.[0-9]+")
    fi
fi

# Si aún no encontramos score, buscar patrones de rating/calificación
if [ -z "$SCORE" ]; then
    # Buscar "Rating: X.X", "Calificación: X.X", etc.
    if grep -qiE "(rating|calificación|calificacion).*[0-9]+\.[0-9]+" "$LATEST_REPORT" 2>/dev/null; then
        SCORE=$(grep -iE "(rating|calificación|calificacion)" "$LATEST_REPORT" | grep -oE "[0-9]+\.[0-9]+" | head -n 1)
    fi
fi

# Si después de todos los intentos no encontramos score, WARN y permitir
if [ -z "$SCORE" ]; then
    echo "⚠️  WARNING: No se pudo extraer score del reporte de code-reviewer"
    echo "   Reporte: $LATEST_REPORT"
    echo "   Se permite commit (graceful degradation - parsing failed)"
    echo "   Threshold esperado: >= ${THRESHOLD}/10"
    echo ""
    echo "   RECOMENDACION: Revisar manualmente el reporte o ajustar el formato para incluir:"
    echo "   'Overall Score: X.X/10' o 'Score: X.X/10'"
    exit 0
fi

# Validar que el score sea un número válido
if ! [[ "$SCORE" =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "⚠️  WARNING: Score extraído no es un número válido: '$SCORE'"
    echo "   Se permite commit (graceful degradation - invalid score format)"
    echo "   Threshold esperado: >= ${THRESHOLD}/10"
    exit 0
fi

echo "📊 Score detectado: ${SCORE}/10"
echo "🎯 Threshold requerido: >= ${THRESHOLD}/10"

# Comparar score contra threshold
if compare_floats "$SCORE" "$THRESHOLD"; then
    echo "✅ PASS: Score ${SCORE}/10 cumple con threshold >= ${THRESHOLD}/10"
    exit 0
else
    echo "❌ FAIL: Score ${SCORE}/10 NO cumple con threshold >= ${THRESHOLD}/10"
    echo ""
    echo "ACCION REQUERIDA:"
    echo "1. Revisar el reporte: $LATEST_REPORT"
    echo "2. Corregir los problemas de calidad identificados"
    echo "3. Ejecutar /verify para re-evaluar"
    echo "4. Intentar commit nuevamente"
    exit 1
fi
