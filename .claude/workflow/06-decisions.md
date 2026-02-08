<!-- version: 2026-02 -->
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
| Selección de modelo | Usar decision tree de `.claude/rules/model-selection-strategy.md` |

## Fuentes Obligatorias (code-implementer)

**ANTES de escribir CUALQUIER código**, `code-implementer` debe consultar:

### 1. `.claude/docs/python-standards.md`
- Type hints modernos (`list[str]`, `X | None`)
- Pydantic v2 (`ConfigDict`, `@field_validator`)
- httpx async (no requests)
- structlog (no print)
- pathlib (no os.path)

### 2. `.claude/rules/tech-stack.md`
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

---

## Model Routing Rules

**Quick Reference** (ver `.claude/rules/model-selection-strategy.md` para decision tree completo):

| Tipo de Tarea | Modelo | Rationale |
|---------------|--------|-----------|
| **File ops** (read, glob, grep) | Haiku | Simple, no synthesis needed |
| **Simple edits** (<100 cambios) | Haiku | Mechanical task |
| **Simple write** (template-based) | Haiku | Clear spec, no synthesis |
| **Bash commands** (ruff, mypy, pytest) | Haiku | Straightforward execution |
| **Simple test script** (<50 líneas) | Haiku | Clear pattern |
| **Config validation** (syntax) | Haiku | Mechanical check |
| **Metrics collection** | Haiku | Straightforward measurement |
| **Code synthesis** (50-300 líneas) | Sonnet | Multi-file reasoning |
| **Complex test suite** (>50 líneas, edge cases) | Sonnet | Edge case coverage |
| **Config analysis** (semantic) | Sonnet | Requires understanding |
| **Verification agents** (todos) | Sonnet | Pattern recognition |
| **Multi-file refactor** (2-5 archivos) | Sonnet | Coordinated changes |
| **Gap analysis** (3-5 archivos) | Sonnet | Synthesis without full context |
| **Documentation generation** | Sonnet | Synthesizing from code |
| **Prompt engineering** | Sonnet | Multi-agent coordination |
| **Design pattern implementation** | Sonnet | Pattern recognition |
| **Multi-module feature** (2-5 módulos) | Sonnet | Cross-module dependencies |
| **Arquitectura** (>5 módulos) | Opus | Full project context required |
| **Parallel execution** (coordinación) | Opus | Complex multi-agent state |
| **System-wide refactor** (>5 módulos) | Opus | Cascading dependencies |

### Cost Targets
- **Haiku:** 5-35× cheaper than Opus
- **Sonnet:** 5× cheaper than Opus
- **Opus:** Only ~10% of tasks
- **Target:** <$0.50 per cycle (40-60% reduction vs. all-Opus)

### Override Decision
Orquestador puede override basado en:
- Task complexity discovered during execution
- Multi-file dependencies (upgrade Haiku → Sonnet)
- Full project context needed (upgrade Sonnet → Opus)
- Task more mechanical than expected (downgrade Sonnet → Haiku)
