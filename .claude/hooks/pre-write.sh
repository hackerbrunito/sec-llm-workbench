#!/usr/bin/env bash
# Pre-write hook: Verifica que Claude haya leído documentación obligatoria
# Parte del Sistema Anti-Autopilot

set -euo pipefail

TODAY=$(date +%Y%m%d)

REQUIRED_CHECKPOINTS=(
    "/tmp/claude-orchestrator-read-${TODAY}"
    "/tmp/claude-spec-read-${TODAY}"
    "/tmp/claude-errors-read-${TODAY}"
)

MISSING=()

for checkpoint in "${REQUIRED_CHECKPOINTS[@]}"; do
    if [[ ! -f "$checkpoint" ]]; then
        MISSING+=("$checkpoint")
    fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "❌ BLOQUEADO: Sistema Anti-Autopilot activado"
    echo ""
    echo "Faltan checkpoints de lectura obligatoria:"
    for missing in "${MISSING[@]}"; do
        echo "  - $missing"
    done
    echo ""
    echo "Ejecuta primero:"
    echo "  /project:start-siopv-phase [número]"
    echo ""
    exit 1
fi

exit 0
