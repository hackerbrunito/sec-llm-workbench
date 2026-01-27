# Decisiones Automáticas

Claude toma estas decisiones SIN preguntar:

| Situación | Acción |
|-----------|--------|
| Falta dependencia | `uv add [dep]` |
| Error de tipos | Corregir type hints |
| Pydantic v1 | Migrar a v2 |
| Usa `requests` | Cambiar a `httpx` |
| Usa `print()` | Cambiar a `structlog` |
| Usa `os.path` | Cambiar a `pathlib` |
| Falta test | Generar test |
| Código duplicado | Refactorizar |
| Vulnerabilidad OWASP | Corregir inmediatamente |

## Context7 (OBLIGATORIO)

ANTES de escribir código con bibliotecas externas:
1. Query Context7 MCP
2. Verificar sintaxis actual
3. NO asumir de memoria
