<!-- version: 2026-02 -->
# Before Commit

<!-- COMPACT-SAFE: 5 agents via /verify, thresholds in verification-thresholds.md, pre-commit hook blocks unverified .py files -->

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

**→ See `.claude/rules/verification-thresholds.md` for complete threshold definitions**
| best-practices-enforcer | 0 violations | Any violation |
| security-auditor | 0 CRITICAL/HIGH | Any CRITICAL/HIGH (MEDIUM = warning) |
| hallucination-detector | 0 hallucinations | Any hallucination |

## Hook pre-git-commit.sh

BLOQUEA commit si hay archivos .py sin verificar.

## Si verificación falla

1. Evita hacer commit
2. Corregir errores
3. Ejecutar /verify de nuevo
4. Luego commit
