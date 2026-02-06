<!-- version: 2026-02 -->
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

## Verification Thresholds

| Check | PASS | FAIL |
|-------|------|------|
| code-reviewer score | >= 9.0/10 | < 9.0/10 |
| ruff check errors | 0 errors | Any errors |
| ruff check warnings | 0 warnings | Any warnings |
| mypy errors | 0 errors | Any errors |
| pytest | All pass | Any fail |
| best-practices-enforcer | 0 violations | Any violation |
| security-auditor | 0 CRITICAL/HIGH | Any CRITICAL/HIGH (MEDIUM = warning) |
| hallucination-detector | 0 hallucinations | Any hallucination |

## Hook pre-git-commit.sh

BLOQUEA commit si hay archivos .py sin verificar.

## Si verificación falla

1. NO hacer commit
2. Corregir errores
3. Ejecutar /verify de nuevo
4. Solo entonces commit
