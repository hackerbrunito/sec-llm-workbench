<!-- version: 2026-02 -->
# Invocación de Agentes

**Prerequisite:** Read `.claude/workflow/02-reflexion-loop.md` before running the reflection loop (on-demand, not auto-loaded).

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

**→ See `.claude/docs/verification-thresholds.md` for PASS/FAIL criteria for each agent**

| Agente | Cuándo | Qué verifica | Reporte | Modelo Recomendado |
|--------|--------|--------------|---------|-------------------|
| best-practices-enforcer | Después de code-implementer | type hints, Pydantic v2, httpx, structlog | ~500+ líneas (flexible) | Sonnet |
| security-auditor | Después de best-practices | OWASP Top 10, secrets, injection | ~500+ líneas (flexible) | Sonnet |
| hallucination-detector | Siempre (TODO el código) | Sintaxis contra Context7 | ~500+ líneas (flexible) | Sonnet |
| code-reviewer | Antes de commit | Calidad, DRY, complejidad | ~500+ líneas (flexible) | Sonnet |
| test-generator | Al completar módulo | Tests unitarios | ~500+ líneas (flexible) | Sonnet |

## Model Selection

**→ Read `.claude/docs/model-selection-strategy.md` on demand for model selection decision tree**

**Quick Reference:**
- **code-implementer:** Sonnet (default), Opus (>5 modules, architectural)
- **All 5 verification agents:** Sonnet (pattern recognition)

## Cómo invocar

### Required: Target Project Path

When invoking ANY agent, ALWAYS include the target project path in the prompt:

> "Target project: `[TARGET_PROJECT]` — the active project path from `projects/*.json` or `.build/active-project`. All file and git operations must use this directory."

This prevents agents from accidentally operating on the meta-project (`sec-llm-workbench/`).

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

#### Wave 3 - Submit 3 agents in parallel (after Wave 2 completes)
```python
Task(
    subagent_type="integration-tracer",
    model="sonnet",
    prompt="""Trace execution paths from all entry points (CLI commands, graph add_node calls)
through the full call chain. Verify parameter forwarding, detect stubs/hollow endpoints,
dead code, and symbols exported in __all__ but never imported in execution paths.

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/integration-tracer/phase-{N}/{TIMESTAMP}-phase-{N}-integration-tracer-{slug}.md`
"""
)
Task(
    subagent_type="async-safety-auditor",
    model="sonnet",
    prompt="""Audit all async/sync boundary violations: asyncio.run() inside async contexts,
sync blocking calls in async functions, missing await on coroutines, and event loop
nesting issues.

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/async-safety-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-async-safety-auditor-{slug}.md`
"""
)
Task(
    subagent_type="semantic-correctness-auditor",
    model="sonnet",
    prompt="""Audit all Python files for semantic correctness issues:
1. @field_validator / @model_validator / @validator bodies that return v without any condition (no-op validators)
2. Functions whose docstring describes behavior X but body does not implement X (returns empty/None/pass)
3. except branches that silently swallow exceptions without logging or re-raising
4. Fallback returns that should be errors (returning [] when real data was expected)

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/semantic-correctness-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-semantic-correctness-auditor-{slug}.md`
"""
)
Task(
    subagent_type="smoke-test-runner",
    model="sonnet",
    prompt="""Execute end-to-end pipeline smoke test with synthetic input CVE-2024-1234.
Verify pipeline runs without crashes and output contains classification, severity, cve_id.

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/smoke-test-runner/phase-{N}/{TIMESTAMP}-phase-{N}-smoke-test-runner-{slug}.md`
"""
)
Task(
    subagent_type="config-validator",
    model="sonnet",
    prompt="""Validate configuration consistency: env vars in .env.example,
docker-compose.yml service references, Settings fields without defaults.

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/config-validator/phase-{N}/{TIMESTAMP}-phase-{N}-config-validator-{slug}.md`
"""
)
Task(
    subagent_type="regression-guard",
    model="sonnet",
    prompt="""Check for cross-phase regressions. Find recently changed files,
build reverse dependency map, run pytest on affected modules.

Target project: `[TARGET_PROJECT]`

Save your report to `.ignorar/production-reports/regression-guard/phase-{N}/{TIMESTAMP}-phase-{N}-regression-guard-{slug}.md`
"""
)
```
**Wait for all 6 to complete** (~7 min max)

**Total with Wave 3: ~19 minutes** (Wave 1: ~7 min + Wave 2: ~5 min + Wave 3: ~7 min)

## Wave 3 Verification Agents

### 6. integration-tracer

**Scope:** End-to-end execution path integrity — from entry points to leaf implementations

**Model:** Sonnet

**When to use:**
- After code-implementer delivers new modules or modifies existing call chains
- When adding new CLI commands or graph nodes
- After refactoring that changes function signatures or parameter lists
- When auditing for dead code or orphaned exports

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Hollow entry points** | CLI commands or graph nodes that terminate in stubs (`pass`, `...`, `TODO`, `raise NotImplementedError`) without calling real implementation | CRITICAL |
| **Parameter dropping** | Functions that accept parameters but do not forward them to the functions they call (silently dropped args) | HIGH |
| **Dead exports** | Symbols listed in `__all__` that are never imported anywhere in the actual execution graph | HIGH |
| **Unreachable code** | Functions defined but never called from any entry point (dead code in execution paths) | MEDIUM |
| **Broken call chains** | Entry point → intermediate → leaf paths where an intermediate function does not call the expected next step | HIGH |

**Verification method:**
1. Identify all entry points: CLI commands (`typer`/`click` handlers), graph node functions (`add_node` targets), API route handlers
2. For each entry point, trace the full call chain to leaf functions using AST analysis + grep
3. At each call boundary, verify that parameters accepted by the caller are forwarded (not silently dropped)
4. Check all `__all__` exports against actual imports in execution-reachable modules
5. Flag functions that exist in source but have no caller in any traced path

**PASS/FAIL criteria:**
- **PASS:** 0 integration gaps (0 CRITICAL + 0 HIGH findings)
- **FAIL:** Any CRITICAL or HIGH finding
- **Warning (non-blocking):** MEDIUM findings (unreachable code) are logged but not blocking

**Example invocation:**
```python
Task(
    subagent_type="integration-tracer",
    model="sonnet",
    prompt="""Trace all execution paths in the target project.

Target project: `/Users/bruno/siopv/`

Entry points to trace:
1. CLI: `src/siopv/interfaces/cli/main.py` — all typer commands
2. Graph: `src/siopv/application/orchestration/graph.py` — all add_node() targets
3. DI: `src/siopv/infrastructure/di/__init__.py` — all exported factory functions

For each entry point:
- Follow the call chain to leaf implementations
- Verify parameters are forwarded at each boundary
- Flag stubs, hollow endpoints, dropped parameters
- Report __all__ exports never imported in execution paths
- Report dead code (defined but never called)

PASS criteria: 0 CRITICAL + 0 HIGH findings.

Save your report to `.ignorar/production-reports/integration-tracer/phase-7/2026-03-05-150000-phase-7-integration-tracer-full-trace.md`
"""
)
```

**Report structure:**
```markdown
# Integration Tracer Report

## Summary
- Entry points traced: N
- Call chains verified: N
- Integration gaps found: N (C critical, H high, M medium)
- Status: PASS / FAIL

## Entry Points Traced
### 1. [entry point name]
- Chain: entry → func_a() → func_b() → leaf()
- Parameters forwarded: YES / NO (details)
- Status: OK / GAP

## Findings
### [ID] [Severity] [Title]
- File: path/to/file.py:line
- Description: ...
- Fix: ...
```

### 7. async-safety-auditor

**Scope:** Async/sync boundary violations that cause runtime crashes or deadlocks

**Model:** Sonnet

**When to use:**
- After code-implementer delivers modules that mix sync and async code
- When project uses LangGraph, httpx async, or any async framework
- After refactoring sync code to async or vice versa

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **`asyncio.run()` in async context** | Calling `asyncio.run()` from within a function already running inside an event loop (e.g., LangGraph nodes, async handlers) — causes `RuntimeError: This event loop is already running` | CRITICAL |
| **Missing `await`** | Calling a coroutine without `await`, resulting in a `RuntimeWarning` and the coroutine never executing | HIGH |
| **Sync blocking in async** | Calling blocking I/O (`time.sleep`, `requests.get`, synchronous DB calls) inside an `async def` function, blocking the event loop | HIGH |
| **Event loop nesting** | Using `nest_asyncio` or manual loop nesting as a workaround instead of proper async architecture | MEDIUM |

**Verification method:**
1. Find all `async def` functions and their call trees
2. Grep for `asyncio.run()` inside async functions or functions called from async contexts
3. Check for `await` on all coroutine calls
4. Find sync blocking calls (`time.sleep`, `requests.`, `open(`) inside `async def` bodies
5. Detect `nest_asyncio.apply()` usage

**PASS/FAIL criteria:**
- **PASS:** 0 CRITICAL + 0 HIGH findings
- **FAIL:** Any CRITICAL or HIGH finding (blocking)
- **Warning (non-blocking):** MEDIUM findings (nest_asyncio) are logged but not blocking

**Example invocation:**
```python
Task(
    subagent_type="async-safety-auditor",
    model="sonnet",
    prompt="""Audit all async/sync boundary violations in the target project.

Target project: `[TARGET_PROJECT]`

Check for:
1. asyncio.run() inside async contexts (graph nodes, async handlers)
2. Missing await on coroutine calls
3. Sync blocking calls (time.sleep, requests.get, open()) inside async def
4. nest_asyncio or event loop nesting workarounds

PASS criteria: 0 CRITICAL + 0 HIGH findings.

Save your report to `.ignorar/production-reports/async-safety-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-async-safety-auditor-{slug}.md`
"""
)
```

**Grep patterns for detection:**
```bash
# asyncio.run() in any Python file (then verify if caller is async)
rg -n "asyncio\.run\(" --type py

# Sync blocking in async functions
rg -U "async def.*\n(.*\n)*?.*time\.sleep\(" --type py
rg -U "async def.*\n(.*\n)*?.*requests\.(get|post|put|delete)\(" --type py

# nest_asyncio usage
rg -n "nest_asyncio" --type py
```

### 8. semantic-correctness-auditor

**Scope:** Detects code that is syntactically valid and passes linters but is semantically wrong — the body does not match the stated intent.

**Model:** Sonnet

**When to use:**
- After every code-implementer cycle (Wave 3, runs after Wave 1+2 complete)
- Especially important for Pydantic models, exception handling, and adapter/port implementations
- Critical for projects using stub-first development where stubs may never get filled in

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **No-op validators** | `@field_validator` / `@model_validator` / `@validator` body returns `v` or `values` without any condition, transformation, or side effect | HIGH |
| **Hollow functions** | Function has a docstring describing behavior X but body is `pass`, `return None`, `return []`, `return {}`, or `...` (Ellipsis) | HIGH |
| **Swallowed exceptions** | `except` branch that neither logs (structlog/logging), re-raises, nor stores the exception — silently drops errors | HIGH |
| **Wrong fallback returns** | Function returns empty collection (`[]`, `{}`, `set()`) or sentinel value in `except` block when the caller expects real data, hiding failures instead of raising | MEDIUM |

**Verification method:**
1. Find all `@field_validator`, `@model_validator`, `@validator` decorated functions
2. Parse their bodies — flag if they only contain `return v` / `return values` with no conditionals or transformations
3. Find all functions with docstrings — compare docstring claims vs body (flag `pass`, `return None`, `...`)
4. Find all `except` blocks — verify each one either logs, re-raises, or stores the exception
5. Find `except` blocks that return empty collections — cross-reference with caller expectations

**PASS/FAIL criteria:**
- **PASS:** 0 semantic no-ops detected (0 HIGH findings)
- **FAIL:** Any HIGH finding (blocking)
- **Warning (non-blocking):** MEDIUM findings (wrong fallback returns) are logged but not blocking

**Example invocation:**
```python
Task(
    subagent_type="semantic-correctness-auditor",
    model="sonnet",
    prompt="""Audit all Python files for semantic correctness issues.

Target project: `[TARGET_PROJECT]`

Check for:
1. @field_validator / @model_validator / @validator bodies that return v without any condition (no-op validators)
2. Functions whose docstring describes behavior X but body does not implement X (returns empty/None/pass)
3. except branches that silently swallow exceptions without logging or re-raising
4. Fallback returns that should be errors (returning [] when real data was expected)

PASS criteria: 0 semantic no-ops (0 HIGH findings).

Save your report to `.ignorar/production-reports/semantic-correctness-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-semantic-correctness-auditor-{slug}.md`
"""
)
```

**Grep patterns for detection:**
```bash
# No-op validators (return v unchanged)
rg -n "@(field_validator|model_validator|validator)" -A 5 --type py | grep "return v\b"

# Hollow functions (docstring + pass/return None)
rg -U '"""[^"]+"""[\s\n]+(pass|return None|return \[\]|return \{\}|\.\.\.)' --type py

# Swallowed exceptions
rg -n "except.*:" -A 3 --type py | grep -E "(pass$|return None$|continue$)"

# Wrong fallback returns in except blocks
rg -U "except.*:[\s\n]+return \[\]" --type py
```

**Report structure:**
```markdown
# Semantic Correctness Auditor Report

## Summary
- Files scanned: N
- Semantic no-ops found: N (H high, M medium)
- Status: PASS / FAIL

## Findings
### [ID] [Severity] [Category] [Title]
- File: path/to/file.py:line
- Pattern: no-op-validator | hollow-function | swallowed-exception | wrong-fallback
- Description: ...
- Fix: ...

## Statistics
- No-op validators: N
- Hollow functions: N
- Swallowed exceptions: N
- Wrong fallback returns: N
```

### 9. smoke-test-runner

**Scope:** End-to-end runtime verification — the only agent that actually executes the project

**Model:** Sonnet

**When to use:**
- Every /verify run (Wave 3, parallel with other Wave 3 agents)
- Especially critical after changes to graph topology, node implementations, or CLI entry points
- After any change to the pipeline's main execution path

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Import failure** | Project cannot be imported via `uv run python -c "import [project]"` | CRITICAL |
| **Pipeline crash** | Unhandled exception during pipeline run with CVE-2024-1234 | CRITICAL |
| **Timeout** | Pipeline does not complete within 120 seconds | CRITICAL |
| **Missing required field** | Output dict missing `classification`/`severity`/`cve_id` | HIGH |
| **Empty output** | Pipeline completes but produces no output | HIGH |

**Verification method:**
1. Resolve target project path from `.build/active-project`
2. Read `pyproject.toml` to discover project name and CLI entry points
3. Verify project is importable via `uv run python -c "import [project]"`
4. Execute pipeline with synthetic input `CVE-2024-1234` using discovered CLI command
5. Enforce 120-second timeout via `timeout 120`
6. Inspect output for unhandled exceptions (`Traceback (most recent call last):`)
7. Verify output contains required fields: `classification`, `severity`, `cve_id`

**PASS/FAIL criteria:**
- **PASS:** Pipeline runs end-to-end without exception, output contains all required fields
- **FAIL:** Any CRITICAL or HIGH finding

**Example invocation:**
```python
Task(
    subagent_type="smoke-test-runner",
    model="sonnet",
    prompt="""Execute end-to-end pipeline smoke test.

Target project: `[TARGET_PROJECT]`

Run pipeline with synthetic input CVE-2024-1234 and verify output contains
classification, severity, and cve_id fields.

PASS criteria: 0 crashes, all required fields present.

Save your report to `.ignorar/production-reports/smoke-test-runner/phase-{N}/{TIMESTAMP}-phase-{N}-smoke-test-runner-smoke-test.md`
"""
)
```

**Report structure:**
```markdown
# Smoke Test Report

## Summary
- Command run: [full command]
- Exit code: N
- Duration: N seconds
- Required fields found: classification=[Y/N], severity=[Y/N], cve_id=[Y/N]
- Status: PASS / FAIL

## Findings
### [ST-001] [Severity] [Title]
- File: path/to/file.py:line
- Description: ...
- Fix: ...
```

### 10. config-validator

**Scope:** Configuration consistency — env vars and Docker service references

**Model:** Sonnet

**When to use:**
- After adding new Settings fields or new os.getenv() calls
- After modifying docker-compose.yml service definitions
- After any change to infrastructure configuration
- Every /verify run (Wave 3)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Missing .env.example** | No .env.example file found in project root | CRITICAL |
| **Undocumented env var** | settings.* or os.getenv() reference not in .env.example | HIGH |
| **Mismatched docker service** | Service name in code not defined in docker-compose.yml | HIGH |
| **Undocumented Settings field** | Settings field with no default not in .env.example | HIGH |

**Verification method:**
1. Resolve target project path from `.build/active-project`
2. Grep `settings.*`, `os.getenv()`, `os.environ[]` across all `.py` files to build required env vars list
3. Read `.env.example` and extract all documented variable names
4. Cross-reference required vs documented — flag gaps
5. Read `docker-compose.yml` and extract service names and port mappings
6. Grep code for Docker service name references — flag mismatches
7. Find `Settings` classes, identify fields with no default — cross-reference with `.env.example`

**PASS/FAIL criteria:**
- **PASS:** All required env vars documented, all docker service references consistent
- **FAIL:** Any CRITICAL or HIGH finding

**Example invocation:**
```python
Task(
    subagent_type="config-validator",
    model="sonnet",
    prompt="""Validate configuration consistency.

Target project: `[TARGET_PROJECT]`

Check all settings.* and os.getenv() references against .env.example.
Check docker-compose.yml service names against code references.

PASS criteria: all env vars documented, all docker services consistent.

Save your report to `.ignorar/production-reports/config-validator/phase-{N}/{TIMESTAMP}-phase-{N}-config-validator-config-check.md`
"""
)
```

**Report structure:**
```markdown
# Config Validator Report

## Summary
- Required env vars found in code: N
- Documented in .env.example: N
- Undocumented (FAIL): N
- Docker services in docker-compose.yml: N
- Mismatched references: N
- Status: PASS / FAIL

## Findings
### [CV-001] [Severity] [Title]
- File: path/to/file.py:line
- Description: ...
- Fix: ...
```

### 11. regression-guard

**Scope:** Cross-phase regression detection via targeted pytest on reverse-dependent modules

**Model:** Sonnet

**When to use:**
- After changes to shared modules (state, DI, constants, graph topology)
- When completing a phase that modifies modules used in earlier phases
- Every /verify run (Wave 3)

**What it checks:**

| Check | Description | Severity |
|-------|-------------|----------|
| **Test regression** | Previously-passing test now FAILED after recent changes | HIGH |
| **Test ERROR** | Test fails to collect or setup due to import/fixture error | HIGH |

**Verification method:**
1. `git diff HEAD~1 --name-only` to find recently changed files
2. Grep to find all modules that import from changed files (reverse dependency map)
3. Find corresponding test files for each reverse-dependent module
4. Run `uv run pytest [affected_tests] -v --tb=short`
5. Flag any FAILED or ERROR

**PASS/FAIL criteria:**
- **PASS:** 0 FAILED, 0 ERROR in all reverse-dependent test modules
- **FAIL:** Any FAILED or ERROR in affected test modules

**Example invocation:**
```python
Task(
    subagent_type="regression-guard",
    model="sonnet",
    prompt="""Check for cross-phase regressions.

Target project: `[TARGET_PROJECT]`

Find recently changed files, build reverse dependency map, run pytest on affected modules.
Flag any previously-passing test that now fails.

PASS criteria: 0 regressions in reverse-dependent modules.

Save your report to `.ignorar/production-reports/regression-guard/phase-{N}/{TIMESTAMP}-phase-{N}-regression-guard-regression-check.md`
"""
)
```

**Report structure:**
```markdown
# Regression Guard Report

## Summary
- Changed files (HEAD~1): N
- Reverse-dependent modules: N
- Affected test files: N
- Tests run: N
- PASSED: N | FAILED: N | ERROR: N | SKIPPED: N
- Status: PASS / FAIL

## Findings
### [RG-001] [Severity] [Title]
- File: path/to/file.py:line
- Description: ...
- Caused by change to: ...
- Fix: ...
```

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

## Wave 3 Verification Agents

Specialized agents that target specific runtime safety concerns beyond standard code quality. These run in Wave 3 (parallel, after Wave 1+2 complete).

| Agente | Cuándo | Qué verifica | Reporte | Modelo Recomendado |
|--------|--------|--------------|---------|-------------------|
| integration-tracer | After code-implementer modifies call chains | Execution path integrity, stubs, dead exports | ~500+ líneas (flexible) | Sonnet |
| async-safety-auditor | After code-implementer touches async code | `asyncio.run()` reachability from async contexts | ~500+ líneas (flexible) | Sonnet |
| semantic-correctness-auditor | After every code-implementer cycle | No-op validators, hollow functions, swallowed exceptions | ~500+ líneas (flexible) | Sonnet |
| smoke-test-runner | Every /verify run (Wave 3) | End-to-end pipeline execution | ~500+ líneas (flexible) | Sonnet |
| config-validator | Every /verify run (Wave 3) | Env var and docker config consistency | ~500+ líneas (flexible) | Sonnet |
| regression-guard | Every /verify run (Wave 3) | Cross-phase regression detection | ~500+ líneas (flexible) | Sonnet |

### async-safety-auditor

**Purpose:** Detect `asyncio.run()` calls that are reachable from async contexts (LangGraph nodes, Streamlit handlers, FastAPI endpoints), which cause `RuntimeError: This event loop is already running` at runtime.

| Agente | Cuándo | Qué verifica | Reporte | Modelo Recomendado |
|--------|--------|--------------|---------|-------------------|
| async-safety-auditor | After code-implementer touches async code, LangGraph nodes, or Streamlit handlers | `asyncio.run()` reachability from async contexts | ~500+ líneas (flexible) | Sonnet |

#### What It Checks

1. **Find every `asyncio.run()` call** in the codebase via grep/AST scan
2. **Identify the runtime context** of each call site:
   - **LangGraph** — nodes registered in the graph are invoked within an async event loop
   - **Streamlit** — runs its own async event loop; `asyncio.run()` inside handlers will crash
   - **FastAPI** — async endpoints and dependencies run inside uvicorn's event loop
   - **CLI (`__main__`, `typer`, `click`)** — sync context; `asyncio.run()` is safe here
3. **Trace async reachability** — check if a sync function containing `asyncio.run()` is:
   - Registered as a LangGraph node (via `graph.add_node()` or `StateGraph` registration)
   - Called from an `async def` function (direct or transitive)
   - Used as a FastAPI dependency or endpoint
   - Invoked from a Streamlit callback
4. **Flag `nest_asyncio`** usage as a workaround (not a fix) — it masks the underlying design issue and can cause subtle bugs with task cancellation and exception propagation
5. **Recommend conversion** to `async def` + `await` pattern for all flagged call sites

#### PASS/FAIL Criteria

| Criteria | PASS | FAIL |
|----------|------|------|
| `asyncio.run()` in async-reachable paths | 0 occurrences | Any occurrence |
| `nest_asyncio.apply()` usage | 0 occurrences (WARNING if found) | N/A (non-blocking, but logged as HIGH warning) |

**PASS:** 0 `asyncio.run()` calls reachable from any async context (LangGraph, Streamlit, FastAPI).
**FAIL:** Any `asyncio.run()` call that can be reached from an async runtime context.

#### When to Use

- After implementing or modifying LangGraph nodes
- After adding Streamlit handlers that call domain logic
- After integrating FastAPI endpoints with existing sync services
- During Phase 7 (Human-in-the-Loop / Streamlit) and Phase 8 (Output) of SIOPV
- Any time `asyncio.run()` or `nest_asyncio` appears in a diff

#### Example Invocation

```python
Task(
    subagent_type="async-safety-auditor",
    model="sonnet",
    prompt="""Audit async safety in target project.

Target project: `[TARGET_PROJECT]`

Steps:
1. Grep for all `asyncio.run()` calls across the codebase
2. Grep for all `nest_asyncio` imports/usage
3. Identify LangGraph node registrations (graph.add_node, StateGraph)
4. Identify Streamlit handlers and FastAPI endpoints
5. For each `asyncio.run()` call, trace whether it is reachable from:
   - A function registered as a LangGraph node
   - An async def function (direct or transitive caller)
   - A Streamlit callback or FastAPI endpoint/dependency
6. Flag each reachable `asyncio.run()` as FAIL with:
   - File path and line number
   - The async context that reaches it (LangGraph/Streamlit/FastAPI)
   - Recommended fix (convert to async def + await)
7. Flag any `nest_asyncio.apply()` as HIGH warning (workaround, not fix)

Save your report to `.ignorar/production-reports/async-safety-auditor/phase-{N}/{TIMESTAMP}-phase-{N}-async-safety-auditor-{slug}.md`
"""
)
```

#### Example Findings

```
FAIL: src/application/orchestration/nodes/dlp_node.py:45
  asyncio.run(sanitize_async(...))
  Context: Function `dlp_node` registered as LangGraph node via graph.add_node("dlp", dlp_node)
  Fix: Convert `dlp_node` to `async def dlp_node(state)` and replace `asyncio.run()` with `await`

WARNING: src/infrastructure/adapters/llm/client.py:12
  import nest_asyncio; nest_asyncio.apply()
  Issue: nest_asyncio masks event loop conflicts; does not fix the root cause
  Fix: Remove nest_asyncio, convert callers to async def + await
```
