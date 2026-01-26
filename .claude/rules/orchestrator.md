# Orquestador del META-PROYECTO

> **Este archivo es el CEREBRO del Vibe Coding.**
> Claude DEBE leer y seguir estas instrucciones automáticamente.

---

## PRINCIPIO FUNDAMENTAL

```
El usuario dice QUÉ quiere.
Claude decide CÓMO y lo HACE.
Sin preguntas. Sin confirmaciones. Solo resultados.
```

---

## 0. REFRESCO DE CONTEXTO (CRÍTICO)

En proyectos largos con múltiples fases y agentes, Claude DEBE refrescar su contexto periódicamente para evitar olvidos.

### Cuándo Releer

```
ANTES de cada tarea mayor (nueva fase, nuevo módulo):
1. Releer projects/[proyecto].md
2. Releer la especificación completa del proyecto
3. Verificar progreso actual
4. Confirmar objetivo de la tarea

DESPUÉS de invocar un agente:
1. Integrar feedback del agente
2. Si hubo correcciones, verificar alineación con especificación

CADA 3-5 tareas completadas:
1. Releer especificación para evitar drift
2. Verificar que el trabajo sigue alineado con el diseño
```

### Comando de Refresco

Si Claude detecta confusión o pérdida de contexto:
```
1. PARAR trabajo actual
2. Releer projects/[proyecto].md
3. Releer especificación completa
4. Resumir: "Estoy en Fase X, trabajando en Y, próximo paso Z"
5. Continuar
```

### Señales de Pérdida de Contexto

- Dudas sobre arquitectura ya definida
- Preguntas que la especificación ya responde
- Inconsistencias con código previamente generado
- Repetición de errores ya corregidos

**Si detectas estas señales: REFRESCA CONTEXTO antes de continuar.**

---

## 0.5 SISTEMA ANTI-AUTOPILOT (CRÍTICO)

**PROBLEMA IDENTIFICADO:**
Claude tiene tendencia demostrada a entrar en "piloto automático", ignorando orchestrator y especificaciones, actuando basándose en entrenamiento obsoleto incluso después de que el usuario haya invertido tiempo creando documentación exhaustiva.

**EVIDENCIA:**
- errors-to-rules.md error 2026-01-26: "Piloto automático"
- 2 intentos de implementación SIOPV, ambos ignorando docs
- 10 días invertidos creando orchestrator + especificación, ambos ignorados

### Sistema de 3 Capas (OBLIGATORIO)

#### CAPA 1: Comando de Inicio Obligatorio

**ANTES de trabajar en CUALQUIER proyecto, el usuario DEBE ejecutar:**

```bash
/project:start-[proyecto]-phase X
```

**Este comando FUERZA:**
1. Lectura COMPLETA de orchestrator.md
2. Lectura COMPLETA de especificación del proyecto
3. Lectura COMPLETA de errors-to-rules.md
4. Creación de checkpoints verificables en /tmp/
5. Confirmación explícita del usuario antes de proceder

**Claude NO puede empezar a trabajar sin este comando.**

---

#### CAPA 2: Hooks de Bloqueo Mecánico

**Hook: `.claude/hooks/pre-write.sh`**

Ejecuta ANTES de cada Write/Edit/NotebookEdit:

```bash
# Verifica checkpoints obligatorios
if [ ! -f /tmp/claude-orchestrator-read-$(date +%Y%m%d) ]; then
    echo "❌ BLOQUEADO: No has leído orchestrator hoy"
    echo "Ejecuta: /project:start-[proyecto]-phase X"
    exit 1
fi

if [ ! -f /tmp/claude-spec-read-$(date +%Y%m%d) ]; then
    echo "❌ BLOQUEADO: No has leído especificación hoy"
    echo "Ejecuta: /project:start-[proyecto]-phase X"
    exit 1
fi

if [ ! -f /tmp/claude-errors-read-$(date +%Y%m%d) ]; then
    echo "❌ BLOQUEADO: No has leído errors-to-rules hoy"
    echo "Ejecuta: /project:start-[proyecto]-phase X"
    exit 1
fi
```

**BLOQUEO TÉCNICO AL 100%:** No puede usar Write/Edit sin checkpoints.

---

#### CAPA 3: Confirmación Humana Obligatoria

**ANTES de CADA acción de modificación (Write/Edit/Bash que modifica archivos):**

Claude DEBE:

1. **ANUNCIAR** qué va a hacer:
   ```
   "Voy a [acción específica: crear pyproject.toml / editar settings.py / etc]"
   ```

2. **ESPECIFICAR** qué consultó:
   ```
   - Orchestrator sección: [número y tema]
   - Especificación líneas: [líneas específicas consultadas]
   - Context7 consulta: [query realizado o "no aplica"]
   - Agentes a ejecutar después: [lista de agentes]
   ```

3. **ESPERAR** confirmación del usuario:
   ```
   "¿Confirmas que proceda?"
   ```

4. **SOLO ENTONCES** ejecutar la acción.

**NUNCA ejecutar Write/Edit sin esta confirmación previa.**

---

### Verificación de Checkpoints

**Checkpoints requeridos (creados por comando inicio):**

```bash
/tmp/claude-orchestrator-read-YYYYMMDD    # Leí orchestrator hoy
/tmp/claude-spec-read-YYYYMMDD            # Leí especificación hoy
/tmp/claude-errors-read-YYYYMMDD          # Leí errors-to-rules hoy
/tmp/claude-context7-consulted-NNNN       # Consulté Context7 para acción NNNN
```

**Los hooks verifican estos checkpoints antes de CADA operación.**

---

### Flujo Obligatorio

```
Usuario: "/project:start-siopv-phase 0"
    ↓
Comando: Lee orchestrator completo
Comando: Lee especificación completa
Comando: Lee errors-to-rules completo
Comando: Crea checkpoints en /tmp/
Comando: "He leído todo. Fase 0: Setup. ¿Confirmas inicio?"
    ↓
Usuario: "Confirmado"
    ↓
Claude: "Voy a crear pyproject.toml.
- Orchestrator: Sección 3 paso 1
- Especificación: Líneas 200-250
- Context7: Consultaré 'uv pyproject best practices'
- Agentes: best-practices-enforcer, hallucination-detector
¿Confirmas?"
    ↓
Usuario: "Confirmado"
    ↓
Claude: [Consulta Context7]
Claude: [Usa Write para crear archivo]
Hook: ✅ Checkpoints OK, permitir Write
Claude: [Archivo creado]
Claude: [Ejecuta best-practices-enforcer]
Claude: [Ejecuta hallucination-detector]
Claude: "Archivo creado y verificado. Siguiente paso..."
```

---

### Por Qué Este Sistema es Necesario

**La sección 0 "REFRESCO DE CONTEXTO" YA existe** con instrucciones claras:
- "ANTES de cada tarea mayor: Releer projects/[proyecto].md, especificación, etc."
- "DESPUÉS de invocar agente: Integrar feedback"
- "CADA 3-5 tareas: Releer especificación"

**Claude ignora sistemáticamente estas instrucciones.**

**Razón:** Piloto automático. Actúa basándose en patrones de entrenamiento sin consultar memoria episódica.

**Solución:** NO confiar en que Claude "recordará" seguir instrucciones. Forzar mecánicamente con:
1. Comando que OBLIGA lectura
2. Hooks que BLOQUEAN sin checkpoints
3. Confirmación humana que VERIFICA comprensión

---

### Excepciones (NINGUNA)

**NO hay excepciones a este sistema:**
- ❌ "Esta tarea es simple, no necesito confirmación"
- ❌ "Ya leí los docs ayer, no necesito releer"
- ❌ "Solo es un cambio pequeño, no necesito Context7"

**TODAS las acciones requieren:**
- ✅ Checkpoints de lectura válidos (mismo día)
- ✅ Anuncio + especificación de consultas
- ✅ Confirmación del usuario

---

### Actualización del Principio Fundamental

**MODIFICACIÓN:**

```
El usuario dice QUÉ quiere.
Claude decide CÓMO (consultando orchestrator + especificación + Context7).
Claude ANUNCIA qué hará y qué consultó.
Claude ESPERA confirmación del usuario.
Claude HACE (solo después de confirmación).
```

**El sistema Anti-Autopilot SOBRESCRIBE el principio "sin confirmaciones"** porque la evidencia demuestra que Claude no sigue instrucciones sin verificación externa forzada.

---

## 1. TRIGGERS DE INICIO

Cuando el usuario inicia una sesión, Claude DEBE detectar automáticamente qué hacer:

### Trigger A: "Continúa con [PROYECTO]" o "Trabaja en [PROYECTO]"
```
1. Leer projects/[proyecto].md
2. Leer la especificación del proyecto (si existe)
3. Detectar estado actual (ver sección 2)
4. Continuar desde donde se quedó
```

### Trigger B: "Crea un nuevo proyecto [NOMBRE]"
```
1. Ejecutar /new-project [nombre] [path]
2. Crear projects/[nombre].md
3. Iniciar Fase 0: Setup
```

### Trigger C: Usuario describe una tarea específica
```
1. Si solo hay un proyecto en projects/*.md → usar ese
2. Si hay múltiples proyectos → preguntar cuál
3. Mapear tarea a fase del proyecto
4. Ejecutar la tarea
5. Ejecutar verificación automática
```

### Trigger D: Sesión sin instrucción específica
```
1. Listar proyectos disponibles en projects/*.md
2. Si solo hay uno → usarlo automáticamente
3. Si hay múltiples → preguntar: "¿Con qué proyecto quieres trabajar?"
4. Leer progreso actual
5. Identificar siguiente tarea pendiente
6. HACER la tarea (no preguntar)
```

---

## 2. DETECCIÓN DE ESTADO

Claude DEBE detectar automáticamente el estado del proyecto:

```python
# Pseudocódigo de detección
def detectar_estado(proyecto_path: str) -> Estado:
    if not existe(proyecto_path):
        return Estado.NO_EXISTE

    if not existe(proyecto_path / "pyproject.toml"):
        return Estado.NECESITA_SETUP

    if not existe(proyecto_path / "src"):
        return Estado.NECESITA_ESTRUCTURA

    # Leer progreso desde projects/[nombre].md
    progreso = leer_progreso()

    # Encontrar primera fase pendiente
    for fase in progreso:
        if fase.estado == "⏳ Pendiente":
            return Estado.EN_PROGRESO, fase

    return Estado.COMPLETADO
```

### Estados Posibles

| Estado | Acción Automática |
|--------|-------------------|
| NO_EXISTE | Ejecutar /new-project |
| NECESITA_SETUP | Crear pyproject.toml, estructura |
| NECESITA_ESTRUCTURA | Crear directorios hexagonales |
| EN_PROGRESO | Continuar siguiente fase pendiente |
| COMPLETADO | Reportar, preguntar siguiente proyecto |

---

## 3. FLUJO DE DESARROLLO (LOOP PRINCIPAL)

```
┌─────────────────────────────────────────────────────────────┐
│                    LOOP PRINCIPAL                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐                                           │
│  │ 1. DETECTAR  │ ← ¿Qué fase/tarea toca?                   │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ 2. PLANEAR   │ ← Descomponer en subtareas                │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ 3. EJECUTAR  │ ← Escribir código                         │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────────────────────────────────┐               │
│  │ 4. VERIFICAR (Loop de Calidad)           │               │
│  │                                          │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ best-practices-enforcer         │◄───┼── Si falla,   │
│  │  └─────────────┬───────────────────┘    │   corregir    │
│  │                │ ✓                       │   y repetir   │
│  │                ▼                         │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ security-auditor                │◄───┤               │
│  │  └─────────────┬───────────────────┘    │               │
│  │                │ ✓                       │               │
│  │                ▼                         │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ hallucination-detector          │◄───┤               │
│  │  └─────────────┬───────────────────┘    │               │
│  │                │ ✓                       │               │
│  │                ▼                         │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ ruff format + ruff check        │    │               │
│  │  └─────────────┬───────────────────┘    │               │
│  │                │ ✓                       │               │
│  │                ▼                         │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ mypy src                        │    │               │
│  │  └─────────────┬───────────────────┘    │               │
│  │                │ ✓                       │               │
│  │                ▼                         │               │
│  │  ┌─────────────────────────────────┐    │               │
│  │  │ pytest (si hay tests)           │    │               │
│  │  └─────────────────────────────────┘    │               │
│  │                                          │               │
│  └──────────────────────────────────────────┘               │
│         │                                                    │
│         ▼ Todo OK                                           │
│  ┌──────────────┐                                           │
│  │ 5. COMMIT    │ ← git add + commit                        │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ 6. ACTUALIZAR│ ← Marcar tarea completada                 │
│  │   PROGRESO   │   en projects/[proyecto].md               │
│  └──────┬───────┘                                           │
│         │                                                    │
│         ▼                                                    │
│  ┌──────────────┐                                           │
│  │ 7. SIGUIENTE │ ← Volver a paso 1                         │
│  └──────────────┘                                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. INVOCACIÓN DE AGENTES

Los agentes se invocan mediante el Task tool con comportamiento específico:

### best-practices-enforcer
```
INVOCAR cuando: Después de escribir/editar código Python
ACCIÓN: Lee .claude/agents/best-practices-enforcer.md y ejecuta verificaciones
SI FALLA: Corregir automáticamente, no preguntar
```

### security-auditor
```
INVOCAR cuando: Después de best-practices-enforcer pasa
ACCIÓN: Lee .claude/agents/security-auditor.md y ejecuta auditoría
SI FALLA: Corregir vulnerabilidades, documentar en @errors-to-rules.md
```

### hallucination-detector
```
INVOCAR cuando: Código usa bibliotecas externas
ACCIÓN: Verificar con Context7 MCP que la sintaxis es correcta
SI FALLA: Consultar Context7, corregir sintaxis
```

### test-generator
```
INVOCAR cuando: Se completa un módulo/feature
ACCIÓN: Generar tests unitarios para el código nuevo
```

### code-reviewer
```
INVOCAR cuando: Antes de commit
ACCIÓN: Review final del código
```

---

## 5. DECISIONES AUTOMÁTICAS

Claude toma estas decisiones SIN preguntar:

| Situación | Decisión Automática |
|-----------|---------------------|
| Falta dependencia | `uv add [dependencia]` |
| Error de tipos | Corregir type hints |
| Error de Pydantic v1 | Migrar a v2 |
| Usa `requests` | Cambiar a `httpx` |
| Usa `print()` | Cambiar a `structlog` |
| Usa `os.path` | Cambiar a `pathlib` |
| Falta test | Generar test |
| Código duplicado | Refactorizar |
| Vulnerabilidad OWASP | Corregir inmediatamente |

---

## 6. CONSULTA CONTEXT7 (OBLIGATORIO)

ANTES de escribir código que use bibliotecas externas:

```
1. Identificar biblioteca (ej: langraph, pydantic, httpx)
2. Usar Context7 MCP para obtener docs actualizadas
3. Verificar sintaxis actual (no asumir)
4. Solo entonces escribir código
```

**NUNCA asumir sintaxis de memoria. SIEMPRE verificar.**

---

## 7. ACTUALIZACIÓN DE PROGRESO

Después de completar cada tarea, Claude DEBE:

```
1. Editar projects/[proyecto].md
2. Cambiar estado de la tarea: ⏳ Pendiente → ✅ Completado
3. Agregar notas si es relevante
4. Identificar siguiente tarea
```

Ejemplo:
```markdown
| 1. Ingestion | ✅ Completado | Parser Trivy implementado |
| 2. RAG (CRAG) | ⏳ Pendiente | Siguiente tarea |
```

---

## 8. MANEJO DE ERRORES

### Error en Verificación
```
1. NO preguntar al usuario
2. Leer el error
3. Corregir automáticamente
4. Volver a verificar
5. Repetir hasta que pase (máx 3 intentos)
6. Si falla 3 veces: documentar en @errors-to-rules.md y reportar
```

### Error de Contexto (no sabe qué hacer)
```
1. Leer projects/[proyecto].md
2. Leer especificación del proyecto
3. Leer memory-bank/ para contexto adicional
4. Si aún no está claro: preguntar al usuario (ÚNICA excepción)
```

### Error de Dependencia/Biblioteca
```
1. Consultar Context7 MCP
2. Si Context7 no tiene info: WebSearch
3. Implementar con docs actualizadas
```

---

## 9. EJEMPLO DE SESIÓN AUTÓNOMA

```
Usuario: "Continúa con [PROYECTO]"

Claude (interno):
1. Leer projects/[proyecto].md
2. Leer especificación del proyecto (path indicado en projects/[proyecto].md)
3. Ver progreso → Identificar primera fase pendiente
4. Detectar qué falta → Componente X no implementado
5. Planear subtareas:
   - Crear archivos necesarios según arquitectura
   - Crear entities/models
   - Crear tests
6. EJECUTAR (sin preguntar)
7. Verificar con agentes
8. Commit
9. Actualizar progreso
10. Continuar con siguiente tarea

Claude (al usuario):
"He implementado [componente] (Fase N):
- src/[path]/[archivo].py
- src/domain/entities/[entity].py
- tests/unit/test_[componente].py

Verificaciones pasadas: ✅ ruff ✅ mypy ✅ tests
Commit: feat([scope]): implement [descripción]

Continuando con Fase 2 (RAG)..."
```

---

## 10. RESUMEN EJECUTIVO

```
┌─────────────────────────────────────────────────────────────┐
│                 VIBE CODING = AUTONOMÍA                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Usuario dice QUÉ                                        │
│  2. Claude detecta DÓNDE estamos                            │
│  3. Claude decide CÓMO                                      │
│  4. Claude HACE (código)                                    │
│  5. Claude VERIFICA (agentes)                               │
│  6. Claude CORRIGE (si falla)                               │
│  7. Claude COMMITEA (si pasa)                               │
│  8. Claude CONTINÚA (siguiente tarea)                       │
│  9. Repetir hasta completar                                 │
│                                                              │
│  Intervención humana: SOLO para decisiones arquitectónicas  │
│                       mayores o cambios de dirección        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```
