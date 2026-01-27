# Before Commit

## Checklist Obligatorio

1. ✅ Ejecutar /verify (5 agentes)
2. ✅ ruff format + ruff check
3. ✅ mypy src
4. ✅ pytest (si hay tests)

## Comando /verify

Ejecuta automáticamente:
- best-practices-enforcer
- security-auditor
- hallucination-detector
- code-reviewer
- test-generator

Limpia markers en `.build/checkpoints/pending/`

## Hook pre-git-commit.sh

BLOQUEA commit si hay archivos .py sin verificar.

## Si verificación falla

1. NO hacer commit
2. Corregir errores
3. Ejecutar /verify de nuevo
4. Solo entonces commit
