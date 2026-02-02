# Decisiones Automáticas

El orquestador delega estas decisiones a code-implementer SIN preguntar:

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

## Fuentes Obligatorias (code-implementer)

**ANTES de escribir CUALQUIER código**, `code-implementer` debe consultar:

### 1. `.claude/docs/python-standards.md`
- Type hints modernos (`list[str]`, `X | None`)
- Pydantic v2 (`ConfigDict`, `@field_validator`)
- httpx async (no requests)
- structlog (no print)
- pathlib (no os.path)

### 2. `.claude/rules/core-rules.md`
- Tech stack del proyecto
- Reglas generales

### 3. Context7 MCP
- Sintaxis moderna para CADA biblioteca
- Patrones actualizados
- NO asumir de memoria

**Quién lo hace:** `code-implementer` (no el orquestador)

**Propósito:** Generar código con:
- Técnicas más modernas
- Patrones actualizados
- Sintaxis correcta
- Lógica óptima
