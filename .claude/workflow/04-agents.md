<!-- version: 2026-02 -->
# Invocación de Agentes

## Agente de Implementación

| Agente | Cuándo | Qué hace | Reporte | Modelo Recomendado |
|--------|--------|----------|---------|-------------------|
| code-implementer | Cuando hay código que escribir | Consulta fuentes (ver abajo), implementa con técnicas modernas | ~500+ líneas (flexible) | Sonnet (default), Opus (>5 módulos) |

### code-implementer DEBE consultar:

1. **`.claude/docs/python-standards.md`** → Estándares del proyecto (Pydantic v2, httpx, structlog, pathlib, type hints modernos)
2. **`.claude/rules/tech-stack.md`** → Tech stack y reglas generales
3. **Context7 MCP** → Sintaxis moderna y patrones actualizados para CADA biblioteca usada

### Orden de consulta:
```
1. Leer python-standards.md (QUÉ usar)
2. Leer tech-stack.md (reglas del proyecto)
3. Query Context7 (CÓMO usarlo correctamente)
4. Implementar código
5. Generar reporte técnico
```

## 5 Agentes de Verificación

**→ See `.claude/rules/verification-thresholds.md` for PASS/FAIL criteria for each agent**

| Agente | Cuándo | Qué verifica | Reporte | Modelo Recomendado |
|--------|--------|--------------|---------|-------------------|
| best-practices-enforcer | Después de code-implementer | type hints, Pydantic v2, httpx, structlog | ~500+ líneas (flexible) | Sonnet |
| security-auditor | Después de best-practices | OWASP Top 10, secrets, injection | ~500+ líneas (flexible) | Sonnet |
| hallucination-detector | Siempre (TODO el código) | Sintaxis contra Context7 | ~500+ líneas (flexible) | Sonnet |
| code-reviewer | Antes de commit | Calidad, DRY, complejidad | ~500+ líneas (flexible) | Sonnet |
| test-generator | Al completar módulo | Tests unitarios | ~500+ líneas (flexible) | Sonnet |

## Model Selection

**All agents use hierarchical model routing** based on task complexity. See `.claude/rules/model-selection-strategy.md` for the complete decision tree.

**Default models:**
- **code-implementer:** Sonnet (50-300 lines), Opus (>5 modules, architectural)
- **All 5 verification agents:** Sonnet (pattern recognition, no full project context needed)

**Override guidelines:**
- Upgrade to Opus: >10 file dependencies, architectural decisions, complex multi-agent coordination
- Downgrade to Haiku: Simple file operations, mechanical tasks, clear templates

## Cómo invocar

### Implementación (Sequential)
```
# Default: Sonnet for typical module implementation
Task(
    subagent_type="code-implementer",
    model="sonnet",
    prompt="Implementa módulo de autenticación en src/auth/..."
)

# Override: Opus for complex architectural work
Task(
    subagent_type="code-implementer",
    model="opus",
    prompt="Refactoriza 7 módulos para arquitectura hexagonal..."
)
```

### Verificación (WAVE-BASED PARALLEL)

#### Wave 1 - Submit 3 agents in parallel
```python
# All verification agents use Sonnet for pattern recognition
# Submit all 3 in a single message for parallel execution
Task(
    subagent_type="best-practices-enforcer",
    model="sonnet",
    prompt="""Verifica archivos Python: type hints, Pydantic v2, httpx, structlog, pathlib.

Save your report to `.ignorar/production-reports/best-practices-enforcer/phase-{N}/{TIMESTAMP}-phase-{N}-best-practices-enforcer-{slug}.md`
"""
)
Task(
    subagent_type="security-auditor",
    model="sonnet",
    prompt="""Audita seguridad: OWASP Top 10, secrets, injection, LLM security.

Save your report to `.ignorar/production-reports/security-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-security-auditor-{slug}.md`
"""
)
Task(
    subagent_type="hallucination-detector",
    model="sonnet",
    prompt="""Verifica sintaxis de TODO el código contra Context7 MCP.

Save your report to `.ignorar/production-reports/hallucination-detector/phase-{N}/{TIMESTAMP}-phase-{N}-hallucination-detector-{slug}.md`
"""
)
```
**Wait for all 3 to complete** (~7 min max)

#### Wave 2 - Submit 2 agents in parallel
```python
# Submit both in a single message for parallel execution
Task(
    subagent_type="code-reviewer",
    model="sonnet",
    prompt="""Review calidad: complejidad, DRY, naming, mantenibilidad.

Save your report to `.ignorar/production-reports/code-reviewer/phase-{N}/{TIMESTAMP}-phase-{N}-code-reviewer-{slug}.md`
"""
)
Task(
    subagent_type="test-generator",
    model="sonnet",
    prompt="""Genera tests unitarios para módulos sin cobertura.

Save your report to `.ignorar/production-reports/test-generator/phase-{N}/{TIMESTAMP}-phase-{N}-test-generator-{slug}.md`
"""
)
```
**Wait for both to complete** (~5 min max)

**Total: ~12 minutes** (vs. ~87 minutes sequential, 86% improvement)

#### Idle State Management

**IMPORTANT:** Teammates go idle after every turn - this is normal behavior.

- Idle notifications are automatic (system-generated)
- Idle does NOT mean "done" or "unavailable"
- Idle agents can still receive messages and wake up
- Do NOT comment on idleness unless it blocks your work

**Normal flow:**
```
Agent sends message → Agent goes idle (automatic) → Ready for next task
```

## Reportes Técnicos

Todos los agentes deben generar reportes técnicos detallados (~500+ líneas, flexible):
- Proporciona **trazabilidad completa** del proceso
- Permite al orquestador **responder cualquier pregunta**
- Total esperado: **~3000-4000 líneas** por ciclo completo

## Si falla
- Delegar corrección a code-implementer
- Documentar en errors-to-rules.md si es error nuevo
- Volver a verificar con los 5 agentes

## Agent Teams (Opus 4.6)

Opus 4.6 soporta coordinacion paralela de agentes con task lists compartidas.
Esto permite ejecutar los 5 agentes de verificacion en paralelo en lugar de secuencialmente.

### Uso potencial
```
# Paralelo (mas rapido, mas tokens)
Task(best-practices-enforcer, ...) + Task(security-auditor, ...) + Task(hallucination-detector, ...)
# Esperar resultados, luego:
Task(code-reviewer, ...) + Task(test-generator, ...)
```

### Cuando usar
- Ciclos de verificacion completos (5 agentes)
- Auditorias multi-archivo donde cada agente revisa un scope independiente

### Cuando NO usar
- Tareas con dependencias secuenciales (code-implementer → verificacion)
- Contexto limitado (cada agente paralelo consume tokens independientes)
