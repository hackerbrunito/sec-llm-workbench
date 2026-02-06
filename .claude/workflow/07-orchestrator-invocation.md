# Protocolo de Invocación del Orquestador

Cómo el orquestador debe invocar a code-implementer y otros agentes.

---

## Context Hygiene

- Run `/clear` between unrelated tasks
- Run `/clear` when switching phases
- After 2 failed correction attempts, `/clear` and reformulate
- Use subagents for investigation to keep main context clean
- Monitor context usage with `/context` regularly

---

## Principio Fundamental

> "Direct agents to work on **one feature at a time** rather than attempting entire applications"
> — Anthropic Best Practices

**Una invocación = Una tarea específica y acotada**

---

## Granularidad de Tareas

### ✅ Correcto: Tareas Específicas

| Invocación | Scope |
|------------|-------|
| "Implementa domain layer de Phase 5" | Un layer |
| "Implementa entity Permission" | Un componente |
| "Agrega método check_permission a AuthService" | Una función |
| "Corrige error en OpenFGAAdapter.check()" | Un fix |

### ❌ Incorrecto: Tareas Demasiado Amplias

| Invocación | Problema |
|------------|----------|
| "Implementa Phase 5" | Demasiado amplio, agotará contexto |
| "Implementa toda la autorización" | Múltiples layers mezclados |
| "Termina el proyecto" | Imposible en una invocación |

---

## Secuencia de Layers (Arquitectura Hexagonal)

Para cada Phase, invocar code-implementer en este orden:

```
1. domain      → Entities, Value Objects, Domain Services
2. ports       → Interfaces/Protocols (input y output)
3. usecases    → Application Services, Use Cases
4. adapters    → Implementaciones de ports (APIs, DBs, etc.)
5. infrastructure → Config, DI, Logging setup
6. tests       → Unit tests, Integration tests
```

Cada layer es una invocación separada.

---

## Estructura del Prompt de Invocación

Cada invocación a code-implementer debe incluir:

```markdown
## Context
- Project: [nombre del proyecto]
- Phase: [número y nombre de la fase]
- Layer: [domain|ports|usecases|adapters|infrastructure|tests]

## Spec
- Project spec: [path al archivo de spec]
- Target directory: [path donde escribir código]

## Task
[Descripción específica de qué implementar]

## Components to Create
- [Componente 1]: [descripción breve]
- [Componente 2]: [descripción breve]

## References
- Existing patterns: [paths a código similar existente]
- Dependencies: [qué ya existe que este código usará]
```

---

## Ejemplos de Invocaciones Correctas

### Ejemplo 1: Domain Layer

```python
Task(
    subagent_type="code-implementer",
    prompt="""
## Context
- Project: SIOPV
- Phase: 5 (OpenFGA Authorization)
- Layer: domain

## Spec
- Project spec: projects/siopv.json
- Target directory: ~/siopv/src/siopv/domain/authorization/

## Task
Implement domain entities and value objects for OpenFGA authorization.

## Components to Create
- Permission: Entity representing a permission (action on resource)
- Role: Entity representing a role with permissions
- AuthorizationContext: Value object with user, resource, action
- AuthorizationResult: Value object with decision and reasoning

## References
- Existing patterns: ~/siopv/src/siopv/domain/vulnerability/
- Dependencies: Base entity from domain/base.py
"""
)
```

### Ejemplo 2: Ports Layer

```python
Task(
    subagent_type="code-implementer",
    prompt="""
## Context
- Project: SIOPV
- Phase: 5 (OpenFGA Authorization)
- Layer: ports

## Spec
- Project spec: projects/siopv.json
- Target directory: ~/siopv/src/siopv/application/ports/

## Task
Define port interfaces for authorization service.

## Components to Create
- AuthorizationPort: Protocol for checking permissions
- AuthorizationStorePort: Protocol for storing/retrieving authorization data

## References
- Existing patterns: ~/siopv/src/siopv/application/ports/enrichment.py
- Dependencies: Domain entities from domain/authorization/
"""
)
```

### Ejemplo 3: Adapter Layer

```python
Task(
    subagent_type="code-implementer",
    prompt="""
## Context
- Project: SIOPV
- Phase: 5 (OpenFGA Authorization)
- Layer: adapters

## Spec
- Project spec: projects/siopv.json
- Target directory: ~/siopv/src/siopv/adapters/authorization/

## Task
Implement OpenFGA adapter for authorization.

## Components to Create
- OpenFGAAdapter: Implementation of AuthorizationPort using OpenFGA client
- OpenFGAConfig: Configuration for OpenFGA connection

## References
- Existing patterns: ~/siopv/src/siopv/adapters/enrichment/nvd_client.py
- Dependencies: AuthorizationPort from ports, domain entities
- External library: openfga-sdk (query Context7)
"""
)
```

### Ejemplo 4: Fix Específico

```python
Task(
    subagent_type="code-implementer",
    prompt="""
## Context
- Project: SIOPV
- Phase: 5 (OpenFGA Authorization)
- Layer: adapters

## Spec
- Project spec: projects/siopv.json
- Target file: ~/siopv/src/siopv/adapters/authorization/openfga_adapter.py

## Task
Fix timeout handling in OpenFGAAdapter.check_permission() method.

## Issue
- Current: No timeout, can hang indefinitely
- Expected: 30s timeout with retry logic

## References
- Similar fix: ~/siopv/src/siopv/adapters/enrichment/nvd_client.py:45-60
"""
)
```

---

## Flujo Completo de una Phase

```
Orquestador                               code-implementer
    │
    ├─── Invocación 1: domain ─────────►  Implementa, genera reporte
    │    ◄─── Reporte 001-domain.md ────  001-domain-layer.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    ├─── Invocación 2: ports ──────────►  Implementa, genera reporte
    │    ◄─── Reporte 002-ports.md ─────  002-ports-interfaces.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    ├─── Invocación 3: usecases ───────►  Implementa, genera reporte
    │    ◄─── Reporte 003-usecases.md ──  003-authorization-usecase.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    ├─── Invocación 4: adapters ───────►  Implementa, genera reporte
    │    ◄─── Reporte 004-adapters.md ──  004-openfga-adapter.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    ├─── Invocación 5: infrastructure ─►  Implementa, genera reporte
    │    ◄─── Reporte 005-infra.md ─────  005-di-configuration.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    ├─── Invocación 6: tests ──────────►  Implementa, genera reporte
    │    ◄─── Reporte 006-tests.md ─────  006-unit-tests.md
    │
    ├─── [CHECKPOINT: aprobación humana]
    │
    └─── Ejecutar 5 agentes de verificación (en paralelo)
              ├── best-practices-enforcer
              ├── security-auditor
              ├── hallucination-detector
              ├── code-reviewer
              └── test-generator
```

---

## Invocación de Agentes de Verificación

Los 5 agentes de verificación se invocan DESPUÉS de completar todos los layers:

```python
# Invocar en paralelo después de implementación completa
Task(subagent_type="best-practices-enforcer",
     prompt="Verify Phase 5 code in ~/siopv/src/siopv/domain/authorization/, adapters/authorization/, application/usecases/")

Task(subagent_type="security-auditor",
     prompt="Audit Phase 5 code for OWASP vulnerabilities, focus on authorization bypass, injection")

Task(subagent_type="hallucination-detector",
     prompt="Verify all external library syntax against Context7: openfga-sdk, pydantic, httpx")

Task(subagent_type="code-reviewer",
     prompt="Review Phase 5 code quality, complexity, DRY violations")

Task(subagent_type="test-generator",
     prompt="Generate additional tests for uncovered code in Phase 5")
```

---

## Checklist del Orquestador

Antes de cada invocación a code-implementer:

- [ ] ¿La tarea es específica (un layer o componente)?
- [ ] ¿Incluí el contexto completo (project, phase, layer)?
- [ ] ¿Especifiqué el path de la spec y target directory?
- [ ] ¿Listé los componentes específicos a crear?
- [ ] ¿Incluí referencias a código existente similar?
- [ ] ¿Es alcanzable en una sola invocación?

---

## Anti-Patrones

| Anti-Patrón | Por qué es malo | Corrección |
|-------------|-----------------|------------|
| "Implementa toda la phase" | Agota contexto, errores acumulados | Dividir en layers |
| Prompt sin spec path | Agente no sabe qué implementar | Incluir path a spec |
| Sin referencias a código existente | Inconsistencia de estilo | Incluir paths de ejemplos |
| Múltiples layers en una invocación | Mezcla responsabilidades | Una invocación por layer |
| Prompt vago "arregla los errores" | Ambiguo, resultados impredecibles | Especificar qué errores |
