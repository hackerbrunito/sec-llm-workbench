# Configuración Pendiente para Claude y META-PROYECTO

**Fecha:** 26 enero 2026
**Contexto:** Deep research sobre comportamiento autopilot de Claude Code y soluciones viables
**Versión Claude Code Actual:** 2.0.5 (DESACTUALIZADA)
**Versión Requerida:** 2.1.12+ (última: 2.1.12, 24 enero 2026)

---

## 🚨 PROBLEMA RAÍZ IDENTIFICADO

### El Error Fundamental

**Lo que hicimos:**
Creamos "Sistema Anti-Autopilot" con 3 capas:
1. Comando obligatorio `/project:start-siopv-phase`
2. Hook PreToolUse que bloquea Write/Edit sin checkpoints
3. Confirmación humana ANTES de CADA Write/Edit

**Por qué NO funciona:**

1. ❌ **Contradice propósito del META-PROYECTO**
   - META-PROYECTO = desarrollo autónomo y automatizado
   - Sistema Anti-Autopilot = destruye automatización completamente
   - Convierte Claude en asistente pasivo

2. ❌ **Bug conocido en PreToolUse (Issue #13744)**
   - Exit code 2 bloquea Bash ✅
   - Exit code 2 NO bloquea Write/Edit ❌
   - Bug reportado desde dic 2025
   - Cerrado como duplicado, SIN confirmación de fix

3. ❌ **Instruction Overflow**
   - System prompt Claude Code: ~50 instrucciones
   - Límite confiable LLMs: 150-200 instrucciones
   - CLAUDE.md + orchestrator.md: >200 instrucciones
   - Resultado: Claude ignora instrucciones (Issue #18660)

---

## 📊 DEEP RESEARCH - HALLAZGOS CRÍTICOS (3 RONDAS)

### Ronda 1: Identificación del Problema

**Fuentes:** 6 búsquedas web especializadas

1. **Issue #18660: CLAUDE.md no se sigue confiablemente**
   - Problema reconocido por comunidad
   - "Instructions read but not reliably followed"
   - Causa: overflow de instrucciones + falta enforcement

2. **PreToolUse Hooks tienen BUGS activos:**
   - Issue #2814: Hooks System Issues
   - Issue #5093: Hooks no ejecutan
   - Issue #13744: Exit code 2 no bloquea Write/Edit
   - Issue #3514: preventContinuation:true ignorado

3. **Failure Modes de Agentes Autónomos:**
   - 14 modos de fallo distintos en 3 categorías
   - Long trajectories causan hallucinations
   - Solución: Reflection after each step

4. **Orchestration Patterns Emergentes:**
   - Master-Clone vs Lead-Specialist
   - Reflection loops en cada paso
   - Verification strategies antes de commits

### Ronda 2: Investigación de Soluciones

**Fuentes:** 6 búsquedas enfocadas en fixes y workarounds

1. **Issue #18660 - Soluciones Propuestas:**

   **A) Priority/Enforcement Syntax:**
   ```markdown
   <!-- ENFORCE -->
   Always add TSDoc comments
   <!-- /ENFORCE -->
   ```

   **B) Pre-Completion Checklist:**
   - Claude revisa rules ANTES de marcar trabajo completo

   **C) Hooks Integration:**
   - Ya sabemos que tiene bugs

   **D) Explicit Compliance Confirmation:**
   - Requerir confirmación de cumplimiento en respuestas

2. **Instruction Following Limit:**
   - Fine-tuning con 50+ ejemplos mínimo
   - Quantización reduce memory 50% (8-bit)
   - KV caching para optimización

3. **Reflexion Pattern (Más Robusto que ReAct):**

   **ReAct (común pero limitado):**
   ```
   Thought → Action → Observation → Thought...
   ```
   - Reflexión "online" durante ejecución
   - Sufre hallucinations en tareas largas

   **Reflexion (solución real):**
   ```
   Execute → Reflect on Trace → Store Memory → Retry
   ```
   - Reflexión "post-hoc" después de completar
   - Identifica errores en trace completo
   - Usa memoria para learning
   - Convergencia gradual a solución correcta

4. **PreToolUse Bug NO Tiene Workaround Efectivo:**
   - Issue #13744 cerrado como duplicado
   - No hay fix confirmado
   - Workaround: PostToolUse (audit después, no prevención)
   - Alternativa: `{"decision": "block"}` pero elimina granularidad

5. **Master-Clone vs Lead-Specialist:**

   **Master-Clone:**
   - ✅ Tareas long multistep con autonomía
   - ❌ Falla cuando cada agente necesita mucho contexto
   - ❌ "Agent will start to miss things and it will be costly"

   **Lead-Specialist (mejor para SIOPV):**
   - ✅ Problemas modulares a especialistas
   - ✅ Coordinador mantiene estado global
   - ✅ Adecuado para dominios especializados

### Ronda 3: Información Actualizada (Enero 2026)

**Fuentes:** 6 búsquedas enfocadas en versiones 2.1.x

1. **Claude Code 2.1.0 (7 enero 2026) - RELEASE MAYOR:**
   - 1096 commits de mejoras
   - Hot reload para skills
   - Hooks en agents & skills frontmatter
   - Wildcard permissions: `Bash(*-h*)`
   - /teleport para session portability
   - Multilingual output support

2. **Claude Code 2.1.9 (16 enero 2026) - CRÍTICO:**

   **Nueva Feature: additionalContext**
   ```json
   {
     "decision": "ask",
     "additionalContext": "⚠️ Recordatorio inyectado en contexto",
     "message": "¿Confirmas continuar?"
   }
   ```
   - Permite inyectar contexto en próximo mensaje de Claude
   - REQUIERE v2.1.9+
   - NO disponible en 2.0.5

   **Nueva Feature: updatedInput con ask**
   ```json
   {
     "decision": "ask",
     "updatedInput": {...},
     "message": "Input modificado, ¿proceder?"
   }
   ```
   - Hook puede modificar input Y pedir confirmación
   - Patrón middleware en lugar de blocking

   **Otros cambios:**
   - Timeout: 60s → 10 minutos
   - Hook `once: true` para operaciones costosas
   - `agent_type` en SessionStart hook input

3. **Claude Code 2.1.12 (24 enero 2026) - ÚLTIMA VERSIÓN:**
   - Última versión estable
   - Refinements adicionales
   - Bug fixes no especificados

4. **Issue #13744 Status:**
   - ❌ Cerrado como DUPLICADO (no como "fixed")
   - ❌ Changelog NO menciona fix de blocking bug
   - ⚠️ NO hay confirmación de que exit code 2 bloquee Write/Edit
   - ✅ Solo confirma nueva feature `additionalContext`

5. **CLAUDE.md Enforcement 2026 - Best Practices:**

   **Anthropic Official Guidance:**
   - "CLAUDE.md should be refined like any frequently used prompt"
   - "Common mistake: adding extensive content without iterating"
   - "We run CLAUDE.md through prompt improver"
   - **Usar emphasis: "IMPORTANT", "YOU MUST"**

   **Límites confirmados:**
   - Frontier LLMs: ~150-200 instrucciones máximo
   - System prompt Claude Code: ~50 instrucciones
   - **Tu CLAUDE.md debe tener <50 instrucciones core**

   **Estructura recomendada:**
   ```markdown
   ## WHAT (tech stack) - conciso
   ## WHY (purpose) - 1-2 párrafos máximo
   ## HOW (workflow) - máximo 10 pasos
   ```

   **Enforcement Levels:**
   - `<!-- STRICT -->` - Claude rechaza generar código
   - `**IMPORTANT:**` - Aumenta adherencia
   - `**YOU MUST:**` - Máxima prioridad

6. **Reflexion Pattern 2026 - Arquitectura PRA:**
   ```
   Perception → Reasoning → Action → Reflection → [Loop]
   ```

   **Frameworks líderes:**
   - **LangGraph:** Human-in-the-Loop con checkpoints
   - **CrewAI:** Multi-agent con role/memory/reasoning
   - **AutoGen:** Microsoft framework con automation

   **Governance-First Design (prioridad 2026):**
   - "Enterprises that embed controls, auditability, and system integration from outset achieve sustainable deployments"
   - Problema: "Agentic AI moving faster than controls can be built"

7. **Session Memory - Realidad 2026:**
   - ❌ NO hay memoria cross-session automática
   - ✅ `.claude/rules/*.md` se carga automáticamente
   - ✅ CLAUDE.md se carga automáticamente
   - ⚠️ "Claude Code starts every session with zero context"

---

## ✅ SOLUCIÓN VIABLE BASADA EN INVESTIGACIÓN

### Sistema 2026 (Reemplaza Anti-Autopilot)

**Arquitectura de 4 Capas:**

#### **CAPA 1: CLAUDE.md Optimizado (<50 instrucciones)**

```markdown
# SIOPV Development Rules - META-PROYECTO

## CRITICAL RULES (15 instrucciones máximo)

**YOU MUST** at session start:
1. Read `.claude/rules/orchestrator.md` COMPLETE
2. Read `docs/SIOPV_Propuesta_Tecnica_v2.txt` COMPLETE
3. Read `.claude/rules/errors-to-rules.md` COMPLETE
4. Announce what you read and wait for confirmation to proceed

**IMPORTANT** before ANY Write/Edit:
5. Query Context7 MCP for library syntax verification
6. Verify current syntax against official documentation
7. Never use training data without Context7 verification

**YOU MUST** after ANY Write/Edit:
8. Execute best-practices-enforcer agent
9. Execute security-auditor agent
10. Execute hallucination-detector agent
11. Execute code-reviewer agent
12. Execute test-generator agent (if applicable)

**STRICT** before git commit:
13. ALL 5 agents must pass with zero errors
14. If agent fails, fix and re-run ALL agents
15. Document any errors found in `.claude/rules/errors-to-rules.md`

## Workflow Details
See `.claude/rules/orchestrator.md` for complete autonomous workflow

## Standards Details
See `.claude/rules/python-standards.md` for Python 2026 best practices

## Error History
See `.claude/rules/errors-to-rules.md` for past mistakes to avoid
```

**Total: 15 core instructions + referencias externas**

---

#### **CAPA 2: PreToolUse Hook con additionalContext (2.1.9+)**

**Archivo:** `/Users/bruno/sec-llm-workbench/.claude/hooks/pre-write.sh`

**REEMPLAZAR contenido actual con:**

```bash
#!/usr/bin/env bash
# Pre-write hook: Middleware pattern con additionalContext
# Requiere Claude Code 2.1.9+

set -euo pipefail

TODAY=$(date +%Y%m%d)

# Verificar checkpoints diarios
MISSING_DOCS=()

if [[ ! -f "/tmp/claude-orchestrator-read-${TODAY}" ]]; then
    MISSING_DOCS+=("orchestrator.md")
fi

if [[ ! -f "/tmp/claude-spec-read-${TODAY}" ]]; then
    MISSING_DOCS+=("SIOPV_Propuesta_Tecnica_v2.txt")
fi

if [[ ! -f "/tmp/claude-errors-read-${TODAY}" ]]; then
    MISSING_DOCS+=("errors-to-rules.md")
fi

# Si faltan documentos, inyectar contexto y pedir confirmación
if [[ ${#MISSING_DOCS[@]} -gt 0 ]]; then
    DOCS_LIST=$(IFS=', '; echo "${MISSING_DOCS[*]}")

    cat <<EOF
{
  "decision": "ask",
  "additionalContext": "⚠️ RECORDATORIO CRÍTICO: Debes leer estos documentos COMPLETOS antes de Write/Edit:\n- ${DOCS_LIST}\n\nEsto previene errores de 'piloto automático' donde actúas basado en training obsoleto en lugar de consultar documentación actual del proyecto.\n\nPara crear checkpoints: /project:init-siopv",
  "message": "¿Has leído la documentación obligatoria hoy? Confirma para continuar o cancela para leer primero."
}
EOF
    exit 0
fi

# Si todos los checkpoints existen, permitir
echo '{"decision": "allow"}'
exit 0
```

**Permisos:**
```bash
chmod +x /Users/bruno/sec-llm-workbench/.claude/hooks/pre-write.sh
```

---

#### **CAPA 3: Reflexion Loop en Orchestrator**

**Archivo:** `/Users/bruno/sec-llm-workbench/.claude/rules/orchestrator.md`

**AGREGAR esta sección al workflow de cada fase:**

```markdown
## Autonomous Reflexion Loop (PRA Pattern)

Para CADA tarea de desarrollo:

### 1. PERCEPTION (¿Qué debo hacer?)
- Identificar línea específica en specification
- Identificar sección específica en orchestrator
- Identificar errores pasados relevantes en errors-to-rules.md

**Output:** Plan claro con referencias exactas

---

### 2. REASONING (¿Cómo lo haré?)
- Query Context7 MCP para sintaxis actual de bibliotecas
- Verificar sintaxis contra documentación oficial
- Diseñar approach basado en specification
- Considerar patrones arquitectónicos (hexagonal)

**Output:** Diseño técnico detallado

---

### 3. ACTION (Ejecutar)
- Write/Edit código siguiendo diseño
- Usar sintaxis verificada por Context7
- Seguir estándares Python 2026

**Output:** Código implementado

---

### 4. REFLECTION (¿Lo hice bien?)

**Ejecutar TODOS los agentes (obligatorio):**

```bash
# 1. Best Practices Enforcer
spawn agent: best-practices-enforcer
- Verifica: type hints, Pydantic v2, httpx, structlog, pathlib
- Si falla: anotar errores, volver a REASONING

# 2. Security Auditor
spawn agent: security-auditor
- Verifica: OWASP Top 10, secrets, injection, LLM security
- Si falla: anotar errores, volver a REASONING

# 3. Hallucination Detector
spawn agent: hallucination-detector
- Verifica: sintaxis contra Context7, APIs correctas
- Si falla: anotar errores, volver a REASONING

# 4. Code Reviewer
spawn agent: code-reviewer
- Verifica: calidad, mantenibilidad, complejidad, DRY
- Si falla: anotar errores, volver a REASONING

# 5. Test Generator (si aplica)
spawn agent: test-generator
- Genera: unit tests para módulos sin coverage
- Si falla: anotar errores, volver a REASONING
```

**Output:** Feedback de 5 agentes

---

### 5. VERIFY (¿Agentes aprueban?)

**Criterio de éxito:** TODOS los agentes pasan sin errores

```
✅ TODOS PASAN:
   → Proceder a paso 6 (LEARN)
   → Preparar commit

❌ ALGUNO FALLA:
   → Documentar errores encontrados
   → Volver a REASONING con feedback
   → NO hacer commit
   → NO continuar a siguiente tarea
```

---

### 6. LEARN (Documentar para futuro)

Si hubo errores en iteraciones:
- Agregar patrón a `.claude/rules/errors-to-rules.md`
- Usar template del archivo
- Incluir: fecha, error, regla para prevenir

**Output:** Base de conocimiento actualizada

---

### 7. COMMIT (Solo si verificación exitosa)

```bash
git add [archivos modificados]
git commit -m "tipo(scope): descripción

- Detalle 1
- Detalle 2

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"
```

**Output:** Código commiteado y verificado

---

## Loop Automático

Este loop se ejecuta AUTOMÁTICAMENTE sin pedir permiso en cada paso.

**Confirmación humana SOLO para:**
- Inicio de fase nueva
- Cambios arquitectónicos mayores
- Eliminación de archivos importantes
- Decisiones que afecten >3 módulos

**NO pedir confirmación para:**
- Write/Edit individual siguiendo spec
- Correcciones basadas en feedback de agentes
- Ejecución de agentes
- Tests automáticos
- Commits aprobados por agentes
```

---

#### **CAPA 4: Human-in-the-Loop Checkpoints**

**Archivo:** `/Users/bruno/sec-llm-workbench/.claude/rules/orchestrator.md`

**AGREGAR esta sección:**

```markdown
## Human-in-the-Loop Checkpoints (LangGraph Style)

### Workflow se PAUSA automáticamente para aprobación humana en:

1. **Inicio de Fase Nueva:**
   ```
   Claude: "📋 CHECKPOINT: Fase X - [Nombre]

   Objetivos:
   - Objetivo 1
   - Objetivo 2

   Deliverables:
   - Archivo 1
   - Archivo 2

   ❓ ¿Apruebas iniciar esta fase? (sí/no)"
   ```

2. **Cambio Arquitectónico Mayor:**
   ```
   Claude: "🏗️ CHECKPOINT: Cambio Arquitectónico

   Propuesta: [descripción]
   Impacto: [módulos afectados]
   Alternativas consideradas: [lista]

   ❓ ¿Apruebas este cambio? (sí/no)"
   ```

3. **Eliminación de Archivos Importantes:**
   ```
   Claude: "🗑️ CHECKPOINT: Eliminación

   Archivos a eliminar:
   - [lista]

   Razón: [justificación]
   Backup: [ubicación]

   ❓ ¿Apruebas eliminar? (sí/no)"
   ```

4. **Decisión Multi-Módulo (>3 módulos afectados):**
   ```
   Claude: "🔀 CHECKPOINT: Cambio Multi-Módulo

   Módulos afectados:
   - [lista de >3 módulos]

   Razón: [justificación]

   ❓ ¿Apruebas proceder? (sí/no)"
   ```

### Workflow continúa AUTOMÁTICAMENTE para:

- ✅ Write/Edit de archivo individual siguiendo spec
- ✅ Correcciones basadas en feedback de agentes
- ✅ Ejecución de agentes de verificación
- ✅ Tests automáticos
- ✅ Commits cuando todos los agentes aprueban
- ✅ Iteraciones de Reflexion Loop
- ✅ Consultas a Context7
- ✅ Lectura de documentación
```

---

#### **CAPA 5: Comando de Inicialización**

**Archivo:** `/Users/bruno/sec-llm-workbench/.claude/commands/init-siopv.md`

**CREAR (nuevo archivo):**

```markdown
---
name: "project:init-siopv"
description: "Inicializa sesión SIOPV con lectura obligatoria de documentación"
---

# Comando: /project:init-siopv

## Propósito

Forzar lectura completa de documentación al inicio de sesión para prevenir comportamiento "autopilot".

## Uso

```
/project:init-siopv
```

## Comportamiento

### Paso 1: Lectura Forzada (sin omitir)

Claude DEBE leer COMPLETOS estos archivos:

```bash
.claude/rules/orchestrator.md
docs/SIOPV_Propuesta_Tecnica_v2.txt
.claude/rules/errors-to-rules.md
```

**No resúmenes. No skimming. Lectura COMPLETA.**

### Paso 2: Creación de Checkpoints

Crear archivos de verificación:

```bash
touch /tmp/claude-orchestrator-read-$(date +%Y%m%d)
touch /tmp/claude-spec-read-$(date +%Y%m%d)
touch /tmp/claude-errors-read-$(date +%Y%m%d)
```

Estos checkpoints:
- Expiran diariamente (YYYYMMDD)
- Son verificados por pre-write.sh
- Bloquean Work/Edit si no existen

### Paso 3: Anuncio de Comprensión

Claude ANUNCIA:

```
📖 DOCUMENTACIÓN LEÍDA:

✅ orchestrator.md (completo, [N] líneas)
   Secciones clave identificadas:
   - [Sección 1]
   - [Sección 2]

✅ SIOPV_Propuesta_Tecnica_v2.txt (completo, [N] líneas)
   Fase actual: [X]
   Objetivos: [lista]
   Deliverables: [lista]

✅ errors-to-rules.md (completo, [N] errores registrados)
   Errores relevantes para evitar:
   - [Error 1]
   - [Error 2]

✅ Checkpoints creados en /tmp/

🤖 Sistema listo para desarrollo autónomo con Reflexion Loop.

❓ ¿Confirmas que proceda con Fase [X]? (sí/no)
```

### Paso 4: Espera Confirmación

Claude NO procede hasta recibir confirmación explícita del usuario.

## Cuándo Usar

- **Obligatorio:** Al iniciar cada sesión de desarrollo en SIOPV
- **Obligatorio:** Después de `claude update`
- **Obligatorio:** Si checkpoints en /tmp/ expiraron
- **Obligatorio:** Si pre-write.sh bloquea operación

## Notas

- Los checkpoints son diarios, debes re-ejecutar este comando cada día
- Este comando NO destruye autonomía, solo fuerza contexto inicial
- Después de este comando, Claude trabaja autónomamente con Reflexion Loop
```

---

## 🔧 ARCHIVOS QUE NECESITAN ACTUALIZACIÓN

### 1. CLAUDE.md
**Ubicación:** `/Users/bruno/sec-llm-workbench/CLAUDE.md`

**Acción:** REEMPLAZAR sección de REGLAS ABSOLUTAS con versión optimizada (<50 instrucciones)

---

### 2. orchestrator.md
**Ubicación:** `/Users/bruno/sec-llm-workbench/.claude/rules/orchestrator.md`

**Acción:**
- AGREGAR sección "Autonomous Reflexion Loop (PRA Pattern)"
- AGREGAR sección "Human-in-the-Loop Checkpoints"
- ELIMINAR sección 0.5 "SISTEMA ANTI-AUTOPILOT" (contraproducente)

---

### 3. pre-write.sh
**Ubicación:** `/Users/bruno/sec-llm-workbench/.claude/hooks/pre-write.sh`

**Acción:** REEMPLAZAR completamente con versión que usa `additionalContext` (requiere 2.1.9+)

---

### 4. confirmation-required.md
**Ubicación:** `/Users/bruno/sec-llm-workbench/.claude/rules/confirmation-required.md`

**Acción:** ELIMINAR (contraproducente, destruye autonomía)

---

### 5. start-siopv-phase.md
**Ubicación:** `/Users/bruno/sec-llm-workbench/.claude/commands/start-siopv-phase.md`

**Acción:** RENOMBRAR a `init-siopv.md` y REEMPLAZAR contenido

---

### 6. errors-to-rules.md
**Ubicación:** `/Users/bruno/sec-llm-workbench/.claude/rules/errors-to-rules.md`

**Acción:** AGREGAR error sobre "Sistema Anti-Autopilot contraproducente"

---

## 📋 CHECKLIST DE ACTUALIZACIÓN

### Fase 1: Actualizar Claude Code (CRÍTICO)

```bash
# En otra terminal
claude update

# Verificar
claude --version  # → Debe ser 2.1.12

# Razón: Necesitas additionalContext feature (2.1.9+)
```

**Estado:** ❌ PENDIENTE (versión actual: 2.0.5)

---

### Fase 2: Probar additionalContext

Después de actualizar a 2.1.12, verificar que `additionalContext` funciona:

```bash
# 1. Ejecutar pre-write.sh manualmente
/Users/bruno/sec-llm-workbench/.claude/hooks/pre-write.sh

# 2. Debe retornar JSON con additionalContext
# 3. Verificar que Claude recibe el contexto adicional
```

**Estado:** ❌ PENDIENTE (requiere 2.1.12 primero)

---

### Fase 3: Actualizar Archivos de Configuración

**Orden recomendado:**

1. ✅ **CLAUDE.md** - Optimizar a <50 instrucciones
2. ✅ **orchestrator.md** - Agregar Reflexion Loop + Human-in-the-Loop
3. ✅ **pre-write.sh** - Reemplazar con versión additionalContext
4. ✅ **init-siopv.md** - Crear nuevo comando
5. ✅ **errors-to-rules.md** - Documentar error Anti-Autopilot
6. ✅ **Eliminar:** confirmation-required.md

**Estado:** ❌ PENDIENTE (hacer después de probar additionalContext)

---

### Fase 4: Probar Sistema Completo

```bash
# 1. Reiniciar Claude Code
claude

# 2. Ejecutar comando de inicialización
/project:init-siopv

# 3. Verificar que:
#    - Lee documentación completa
#    - Crea checkpoints
#    - Anuncia comprensión
#    - Espera confirmación

# 4. Intentar Write/Edit:
#    - Debe ejecutar Reflexion Loop automáticamente
#    - Debe ejecutar 5 agentes sin pedir permiso
#    - Solo debe pausar en Human-in-the-Loop checkpoints

# 5. Verificar autonomía preservada
```

**Estado:** ❌ PENDIENTE (hacer después de actualizar archivos)

---

## 🎯 DIFERENCIAS CRÍTICAS: Anti-Autopilot vs Sistema 2026

| Aspecto | Anti-Autopilot (erróneo) | Sistema 2026 (viable) |
|---------|---------------------------|----------------------|
| **Filosofía** | Bloquear TODO hasta confirmación | Autonomía con guardrails |
| **Confirmaciones** | CADA Write/Edit | Solo checkpoints mayores |
| **Enforcement** | PreToolUse blocking (bug) | additionalContext + emphasis |
| **Instrucciones** | >200 (overflow) | <50 core + referencias |
| **Agentes** | Sin integración clara | Reflexion Loop automático |
| **Autonomía** | ❌ Destruida | ✅ Preservada |
| **Hooks** | Depende de bug | Middleware pattern (2.1.9+) |
| **Viabilidad** | ❌ No funciona técnicamente | ✅ Basado en investigación real |

---

## 🚨 ERRORES A NO REPETIR

### Error 1: Sistema Anti-Autopilot
**Fecha:** 26 enero 2026
**Error:** Creé sistema que requiere confirmación humana antes de CADA Write/Edit, destruyendo completamente la autonomía del META-PROYECTO
**Regla:** Confirmar propósito del sistema ANTES de diseñar soluciones. META-PROYECTO = autonomía con guardrails, NO asistente pasivo

### Error 2: Confiar en PreToolUse Blocking
**Fecha:** 26 enero 2026
**Error:** Diseñé sistema basado en exit code 2 bloqueando Write/Edit cuando Issue #13744 confirma que este bug existe y NO está arreglado
**Regla:** Verificar bugs conocidos ANTES de diseñar arquitectura. No asumir que features funcionan sin investigación

### Error 3: Instruction Overflow
**Fecha:** 26 enero 2026
**Error:** CLAUDE.md + orchestrator.md suman >200 instrucciones cuando límite confiable es 150-200
**Regla:** CLAUDE.md debe tener <50 instrucciones core. Usar referencias externas para detalles. Issue #18660 confirma este problema

### Error 4: No Verificar Versión Actual
**Fecha:** 26 enero 2026
**Error:** Diseñé sistema para features de 2.1.9+ cuando versión actual es 2.0.5 (additionalContext no disponible)
**Regla:** SIEMPRE verificar `claude --version` ANTES de diseñar soluciones que dependen de features específicas

---

## 📚 FUENTES Y REFERENCIAS

### GitHub Issues (Claude Code)
- Issue #18660: CLAUDE.md instructions not reliably followed
- Issue #13744: PreToolUse exit code 2 doesn't block Write/Edit
- Issue #3514: preventContinuation:true ignored
- Issue #2814: Hooks System Issues
- Issue #5093: Hooks not executing

### Versiones Claude Code
- 2.0.5: Versión actual (desactualizada)
- 2.1.0: Release mayor (7 enero 2026, 1096 commits)
- 2.1.9: additionalContext feature (16 enero 2026)
- 2.1.12: Última estable (24 enero 2026)

### Documentación Oficial
- Claude Code Hooks Guide: https://code.claude.com/docs/en/hooks-guide
- Claude Code Memory: https://code.claude.com/docs/en/memory
- CHANGELOG: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md

### Papers & Research
- Fundamentals of Building Autonomous LLM Agents (arXiv)
- Why Do Multi-Agent LLM Systems Fail (arXiv)
- Reflexion Pattern vs ReAct Pattern (Hugging Face)

### Best Practices (2026)
- Anthropic Official: CLAUDE.md refinement guide
- Emphasis enforcement: "IMPORTANT", "YOU MUST"
- Instruction limit: 150-200 para frontier LLMs
- Governance-First Design para enterprise deployment

---

## ⏭️ PRÓXIMOS PASOS INMEDIATOS

### 1. Actualizar Claude Code (30 segundos)
```bash
claude update
claude --version  # Verificar 2.1.12
```

### 2. Probar additionalContext (5 minutos)
```bash
# Ejecutar pre-write.sh y verificar JSON output
# Confirmar que feature está disponible
```

### 3. Actualizar Configuración (30 minutos)
- CLAUDE.md optimizado
- orchestrator.md con Reflexion Loop
- pre-write.sh con additionalContext
- Crear init-siopv.md
- Documentar error en errors-to-rules.md

### 4. Probar Sistema Completo (1 hora)
- Reiniciar Claude Code
- Ejecutar /project:init-siopv
- Verificar autonomía + guardrails
- Confirmar Reflexion Loop funciona

### 5. Comenzar Fase 0 SIOPV (según disponibilidad)
- Usar sistema actualizado
- Documentar resultados
- Iterar si es necesario

---

## 💡 CONCEPTOS CLAVE PARA RECORDAR

### 1. Middleware > Blocking
PreToolUse con `additionalContext` actúa como middleware que inyecta recordatorios, NO como bloqueador absoluto. Esto es mejor porque:
- No depende de bugs
- Mantiene autonomía
- Proporciona contexto en tiempo real

### 2. Reflexion > ReAct
Reflexion pattern (post-hoc reflection después de cada tarea) es más robusto que ReAct (online reflection durante ejecución) para prevenir hallucinations en workflows largos.

### 3. Emphasis en CLAUDE.md
Anthropic confirma que agregar "IMPORTANT", "YOU MUST" aumenta adherencia a instrucciones. No es placebo, es documentado oficialmente.

### 4. <50 Instrucciones Core
System prompt de Claude Code ya tiene ~50 instrucciones. Tu CLAUDE.md compite con ellas. Límite total confiable: 150-200. Por tanto: CLAUDE.md debe tener <50 instrucciones core + referencias.

### 5. Human-in-the-Loop ≠ Sin Autonomía
Checkpoints humanos solo en decisiones mayores preserva autonomía para trabajo diario mientras previene errores arquitectónicos costosos.

### 6. Lead-Specialist para SIOPV
SIOPV tiene dominios especializados (security, quality, testing, XAI). Lead-Specialist pattern con coordinador central es más apropiado que Master-Clone.

### 7. Session Memory = CLAUDE.md + rules/
No hay memoria cross-session automática. Toda persistencia viene de archivos en `.claude/rules/*.md` que se cargan automáticamente.

---

## 📞 CONTACTO PARA PRÓXIMA SESIÓN

**Al iniciar próxima sesión, decir:**

```
"Lee configuracion_pendiente_para_Claude_y_mega_proyecto.md y confirma comprensión de:
1. Por qué Sistema Anti-Autopilot no funciona
2. Qué es Sistema 2026 viable
3. Estado actual (2.0.5 vs 2.1.12)
4. Próximos pasos inmediatos"
```

**NO empezar implementación hasta:**
- ✅ Actualizar a Claude Code 2.1.12
- ✅ Probar que additionalContext funciona
- ✅ Confirmar comprensión de este documento

---

## 🎯 OBJETIVO FINAL

**META-PROYECTO debe ser:**
- ✅ Autónomo (development sin confirmaciones constantes)
- ✅ Confiable (Reflexion Loop previene errores)
- ✅ Verificado (5 agentes antes de cada commit)
- ✅ Documentado (errors-to-rules.md aprende de errores)
- ✅ Seguro (Human-in-the-Loop en decisiones mayores)

**META-PROYECTO NO debe ser:**
- ❌ Asistente pasivo que pide confirmación constantemente
- ❌ Sistema que bloquea TODO (destruye autonomía)
- ❌ Configuración con >200 instrucciones (overflow)
- ❌ Dependiente de bugs conocidos (PreToolUse blocking)

---

**FIN DEL DOCUMENTO**

Este documento contiene TODO el contexto necesario para continuar sin pérdida de información.

Fecha: 26 enero 2026, 02:47 CET
Versión: 1.0
