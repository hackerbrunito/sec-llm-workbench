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

**→ See `.claude/rules/model-selection-strategy.md` for model selection decision tree**

**Quick Reference:**
- **code-implementer:** Sonnet (default), Opus (>5 modules, architectural)
- **All 5 verification agents:** Sonnet (pattern recognition)

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

**Note:** Teammates go idle after every turn - this is normal behavior.

- Idle notifications are automatic (system-generated)
- Idle doesn't mean "done" or "unavailable"
- Idle agents can still receive messages and wake up
- Only comment on idleness if it blocks your work

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

## Hybrid Model Strategy (Phase 4)

**Cost reduction: -26% vs single-model baseline**

### Concepto

Verificación en 2 fases para optimizar costo sin pérdida de calidad:
- **Fase 1 (Cheap Scan):** Haiku/Sonnet hace escaneo amplio, detecta patrones sospechosos
- **Fase 2 (Deep Dive):** Opus analiza SOLO secciones marcadas en profundidad

### Patrones de Uso

#### Pattern 1: code-implementer (Haiku draft → Opus refinement)
```python
# Fase 1: Haiku genera estructura básica (~50 líneas)
Task(
    subagent_type="code-implementer",
    model="haiku",
    prompt="""Genera estructura básica de módulo de autenticación:
- Clases principales con métodos stub
- Type hints
- Docstrings básicos
NO implementes lógica compleja todavía."""
)

# Fase 2: Opus refina SOLO lógica compleja
Task(
    subagent_type="code-implementer",
    model="opus",
    prompt="""Refina SOLO estos métodos del draft de Haiku:
- authenticate(): Implementa lógica JWT + refresh tokens
- validate_permissions(): Implementa RBAC lookup
Contexto: {haiku_draft}"""
)
```

**Cuándo usar:**
- Módulos >300 líneas con 20-30% lógica compleja
- 70-80% es boilerplate (clases, imports, type hints)
- Lógica compleja concentrada en 2-3 funciones

**Ahorro esperado:** 40-50% vs Opus completo

#### Pattern 2: Verification Agents (Sonnet scan → Opus deep dive)
```python
# Fase 1: Sonnet escanea todo el código con heurísticas rápidas
scan_result = await run_cheap_scan(
    agent="security-auditor",
    model="sonnet",
    files=pending_files,
)
# Resultado: Lista de secciones sospechosas con líneas específicas

# Fase 2: Opus analiza SOLO secciones marcadas
for flagged_section in scan_result.flagged_sections:
    deep_dive_result = await run_deep_dive(
        agent="security-auditor",
        model="opus",
        section=flagged_section,  # Solo 10-30 líneas de contexto
    )
```

**Cuándo usar:**
- Codebase grande (>1000 líneas) con pocos problemas reales
- Cheap scan marca 5-10% del código para deep dive
- 90-95% del código es limpio (no necesita análisis profundo)

**Ahorro esperado:** 50-60% vs Opus full scan

### Script de Orquestación

**⚠️ EXPERIMENTAL:** Este script es parte de investigación Phase 4 (no integrado en producción)

**Ubicación:** `.ignorar/experimental-scripts/phase4-hybrid-verification/hybrid-verification.py`

**Uso:**
```bash
# Ejecutar verificación híbrida en archivos pendientes
python .ignorar/experimental-scripts/phase4-hybrid-verification/hybrid-verification.py

# Ver logs
cat .build/logs/hybrid-verification/$(date +%Y-%m-%d).jsonl | jq
```

**Output:**
```json
{
  "status": "SUCCESS",
  "total_cost_usd": 0.35,
  "scan_cost_usd": 0.08,
  "deep_dive_cost_usd": 0.27,
  "cost_comparison": {
    "baseline_all_opus": 0.75,
    "hierarchical_routing": 0.47,
    "hybrid": 0.35,
    "savings_vs_baseline_pct": 53.3,
    "savings_vs_hierarchical_pct": 25.5
  }
}
```

### Heurísticas de Cheap Scan

El cheap scan marca secciones basado en:

| Heurística | Threshold | Severidad | Ejemplo |
|-----------|-----------|-----------|---------|
| Cyclomatic complexity | >10 | HIGH | Funciones con >10 ramas |
| Function length | >30 lines | MEDIUM | Métodos muy largos |
| SQL patterns + f-strings | Any match | CRITICAL | `f"SELECT * FROM {table}"` |
| Hardcoded secrets | Keywords + `=` + `"` | HIGH | `api_key = "sk-xxx"` |
| Legacy type hints | `List[`, `Dict[` | MEDIUM | `from typing import List` |
| `print()` statements | Any | LOW | `print("debug")` |

### Thresholds de Deep Dive

Solo invocar Opus si:
- **CRITICAL findings:** Siempre (SQL injection, secrets)
- **HIGH findings:** Si >2 en mismo archivo
- **MEDIUM findings:** Si >5 en mismo módulo
- **LOW findings:** NO (arreglar sin deep dive)

### Cost Breakdown Example

**Archivo típico: 300 líneas Python**

| Fase | Model | Tokens | Cost | % of Opus |
|------|-------|--------|------|-----------|
| Cheap scan (full file) | Sonnet | 20K input + 2K output | $0.09 | 12% |
| Deep dive (3 sections × 30 lines) | Opus | 3 × (2K input + 1K output) | $0.68 | 91% |
| **Total hybrid** | Mixed | 26K | **$0.77** | **103%** |
| Opus full scan | Opus | 20K input + 5K output | $0.75 | 100% |

**Nota:** Hybrid NO ahorra si cheap scan marca >40% del código. En ese caso, usar Opus directo.

### Decision Tree: ¿Cuándo usar Hybrid?

```
¿Archivo >500 líneas?
├─ NO → Usar Sonnet single-model (no overhead de 2 fases)
└─ SÍ → ¿Esperamos >5 problemas reales?
    ├─ SÍ → Usar Opus single-model (cheap scan marcará >40%)
    └─ NO → Usar HYBRID (cheap scan marca <20%, gran ahorro)
```

### Integration con /verify

El skill `/verify` puede invocar hybrid mode:

```bash
# Default: hierarchical routing (Sonnet para todo)
/verify

# Hybrid mode: Sonnet scan → Opus deep dive
/verify --hybrid

# Force Opus: Análisis completo (legacy behavior)
/verify --opus
```

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
