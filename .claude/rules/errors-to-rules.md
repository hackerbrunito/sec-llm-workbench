# Errores → Reglas (Self-Correcting Log)

Registro de errores cometidos y las reglas creadas para no repetirlos.

---

## Cómo Usar Este Archivo

1. Cuando Claude cometa un error, documentarlo aquí
2. Crear una regla específica para prevenir el error
3. Si es un patrón recurrente, agregar a CLAUDE.md como REGLA ABSOLUTA

---

## Registro de Errores

### 2026-01-20: Usar pip en lugar de uv

**Error:**
```bash
pip install pydantic  # ❌
```

**Contexto:** Claude usó pip por defecto al instalar dependencias.

**Regla creada:**
```
SIEMPRE usar uv (uv sync, uv add, uv run)
NUNCA usar pip install, pip freeze, python -m venv
```

**Estado:** ✅ Agregado a REGLAS ABSOLUTAS

---

### 2026-01-20: Subagentes pasivos

**Error:**
Los subagentes solo documentaban qué verificar, no ejecutaban verificaciones.

**Contexto:** Los archivos .md de subagentes eran documentación pasiva.

**Regla creada:**
```
Subagentes DEBEN tener COMPORTAMIENTO MANDATORIO
Deben EJECUTAR automáticamente, no solo DOCUMENTAR
```

**Estado:** ✅ Subagentes reescritos con comportamiento activo

---

### 2026-01-20: Pedir confirmaciones innecesarias

**Error:**
```
"¿Quieres que implemente esta función?"
"¿Debería agregar tests?"
```

**Contexto:** Claude pedía confirmación para tareas estándar.

**Regla creada:**
```
HACER: Implementar, verificar, corregir
NO HACER: "¿Quieres que...?", "¿Debería...?"

Solo preguntar para:
- Decisiones arquitectónicas mayores
- Eliminación de archivos importantes
- Cambios irreversibles
```

**Estado:** ✅ Agregado a REGLAS ABSOLUTAS

---

### 2026-01-21: META-PROYECTO dentro de SIOPV

**Error:**
Poner `.claude/`, `memory-bank/`, hooks dentro del proyecto SIOPV, contaminando el TFM.

**Contexto:** El usuario necesita presentar SIOPV como proyecto limpio y profesional.

**Regla creada:**
```
El META-PROYECTO debe estar SEPARADO del proyecto generado
El proyecto generado debe ser EXPORTABLE sin configuración de Vibe Coding
NUNCA incluir .claude/, memory-bank/ en proyectos destino
```

**Estado:** ✅ Rediseño completado con separación

---

### 2026-01-23: Audit missed hardcoded GitHub URL in README

**Error:**
Ran an audit searching for hardcoded references but missed `https://github.com/hackerbrunito/VIBE_CODING_2026.git` in README.md line 33.

**Contexto:**
Used grep to search for `github.com/hackerbrunito` but the search returned "None found" despite the URL being present. Did not manually verify critical files like README.md after automated search.

**Regla creada:**
```
AFTER automated audits, ALWAYS manually verify critical files:
- README.md
- CLAUDE.md
- .env.example
- Any file that users will see first

Automated grep searches can fail silently. Trust but verify.
```

**Estado:** ✅ URL fixed, rule documented

---

### 2026-01-26: No consultar Context7 ANTES de escribir configuración

**Error:**
Escribí `.pre-commit-config.yaml` basándome en "experiencia" usando `rev: v1.8.0` (obsoleto), `--ignore-missing-imports` (contradictorio con --strict), sin consultar Context7 para verificar versión actual y best practices oficiales.

**Contexto:**
Asumí sintaxis de memoria en lugar de verificar documentación oficial antes de escribir archivos de configuración o código que usa bibliotecas externas.

**Regla creada:**
```
ANTES de escribir archivos de configuración o código que use bibliotecas externas:
1. Consultar Context7 MCP para verificar: versión actual, sintaxis oficial, best practices
2. NO asumir basándose en experiencia/memoria
3. Orchestrator línea 286: "NUNCA asumir sintaxis de memoria. SIEMPRE verificar"
```

**Estado:** ✅ Documentado, correcciones aplicadas con Context7

---

### 2026-01-26: Correcciones sin ejecutar agentes

**Error:**
Cuando pre-commit falló, corregí errores manualmente (agregué `# type: ignore`, cambié versiones, modifiqué dependencies) sin ejecutar hallucination-detector, best-practices-enforcer o security-auditor para verificar que las correcciones fueran correctas.

**Contexto:**
Al encontrar fallos, apliqué correcciones basándome en el error mostrado sin verificar con agentes que la solución fuera la correcta según estándares actuales.

**Regla creada:**
```
NUNCA hacer correcciones por tu cuenta. Cuando algo falla:
1. Ejecutar agentes aplicables (hallucination-detector, best-practices-enforcer, security-auditor)
2. Aplicar las recomendaciones de los agentes
3. Verificar que la corrección es correcta
4. Commit solo si todo pasa

Si pre-commit falla → ejecutar agentes → aplicar correcciones → commit
```

**Estado:** ✅ Proceso corregido, agentes ejecutados

---

### 2026-01-26: No seguir flujo completo del orchestrator antes de commit

**Error:**
Omití `code-reviewer` antes de ambos commits (fdf5367 y e779467). Asumí que solo necesitaba ejecutar 3 agentes (best-practices-enforcer, security-auditor, hallucination-detector) ignorando que el orchestrator define 7 pasos antes de commit.

**Contexto:**
No revisé el flujo completo del orchestrator (líneas 164-194) antes de hacer commit. Asumí que "este commit es simple y no necesita todos los pasos".

**Regla creada:**
```
Antes de CADA commit, ejecutar flujo COMPLETO del orchestrator sin excepciones:
1. best-practices-enforcer
2. security-auditor
3. hallucination-detector
4. ruff format + check
5. mypy strict
6. pytest (si hay tests)
7. code-reviewer

NO asumir que "este commit es simple". Flujo completo SIEMPRE.
```

**Estado:** ✅ Documentado para sesiones futuras

---

### 2026-01-26: Asumir que módulos "de setup" no necesitan tests

**Error:**
Omití `test-generator` asumiendo que "Fase 0 = Setup = solo configuración = no necesita tests", cuando en realidad creé 4 módulos completos (settings.py, logging/setup.py, cli/main.py, exceptions.py) con lógica que SÍ necesita tests.

**Contexto:**
Interpreté "Setup" como "no hay lógica", ignorando que hay validadores Pydantic, configuración de structlog, CLI commands con validación de paths, y custom exceptions.

**Regla creada:**
```
TODO módulo Python con lógica necesita tests, sin excepciones por fase/tipo:
- Validadores Pydantic → tests
- Configuración de logging → tests
- CLI commands → tests
- Custom exceptions → tests
- Settings con @model_validator → tests

Orchestrator línea 244: "Se completa un módulo/feature" - aplica a TODOS los módulos.
```

**Estado:** ⏳ Pendiente generar tests para Fase 0

---

### 2026-01-26: No documentar errores inmediatamente

**Error:**
Cometí múltiples errores durante la sesión pero no los documenté en `errors-to-rules.md` hasta que el usuario me lo pidió explícitamente.

**Contexto:**
Identifiqué errores (por fallo de verificación o señalado por el usuario) pero no los agregué inmediatamente al log de errores.

**Regla creada:**
```
Inmediatamente después de identificar un error:
1. Agregar entrada a .claude/rules/errors-to-rules.md
2. Formato: Fecha, Error, Contexto, Regla creada, Estado
3. NO esperar al final de la sesión
4. NO esperar a que el usuario lo pida

CLAUDE.md línea 179: "Claude DEBE agregar nuevas reglas cuando cometa errores"
```

**Estado:** ✅ Agregando errores ahora

---

### 2026-01-26: Inventar recomendaciones de Anthropic

**Error:**
Afirmé: "Opción B: Mover a docs/ (Recomendado por Anthropic)" cuando Anthropic NO recomienda específicamente dónde poner logs de errores. Me lo inventé.

**Contexto:**
Usuario preguntó por recomendaciones oficiales. En lugar de admitir que no había evidencia, inventé que Anthropic recomendaba algo que no encontré en la documentación.

**Regla creada:**
```
NUNCA afirmar que X recomienda Y sin evidencia directa:
1. Si no encontraste la recomendación en docs oficiales → decir "No encontré recomendación oficial"
2. Si solo encontraste opiniones de usuarios → decir "Usuarios sugieren X, pero NO es oficial"
3. NUNCA decir "Recomendado por [autoridad]" sin cita exacta

Honestidad > Parecer que sabes la respuesta
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Afirmar popularidad sin evidencia suficiente

**Error:**
Dije "Opción 1: Patrón centminmod (más popular)" habiendo investigado solo 5 fuentes (Anthropic docs + 3 repos GitHub + 1 artículo). Eso NO es suficiente para afirmar "más popular".

**Contexto:**
Intenté dar una recomendación definitiva sin tener datos estadísticos reales de uso.

**Regla creada:**
```
Para afirmar "más popular", "más común", "estándar de la industria":
- Necesitas: Encuestas, estadísticas de uso, múltiples fuentes (20+)
- NO suficiente: 3-5 ejemplos anecdóticos

Alternativas honestas:
- "De las 5 fuentes revisadas, 3 usan X"
- "Encontré este patrón en proyectos comunitarios, pero no tengo datos de popularidad"
- "No tengo evidencia suficiente para afirmar cuál es más popular"
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Shallow research presentado como "deep research"

**Error:**
Usuario pidió "deep research". Solo busqué 5 fuentes (Anthropic docs + 3 repos + 1 artículo) y presenté eso como investigación profunda.

**Contexto:**
"Deep research" implica investigación exhaustiva. 5 fuentes es investigación superficial.

**Regla creada:**
```
Niveles de investigación:
- Quick search: 1-3 fuentes
- Standard research: 5-10 fuentes
- Deep research: 20+ fuentes, múltiples tipos (docs oficiales, repos, foros, papers, blogs)

Si usuario pide "deep research" y solo haces 5 fuentes:
1. Admitir: "Solo encontré 5 fuentes, esto es investigación limitada"
2. Preguntar: "¿Quieres que continúe buscando más fuentes?"
3. NO presentar investigación superficial como profunda
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Contradecirse con evidencia del filesystem

**Error:**
Usuario cuestionó de dónde saqué el prefijo `@` en nombres de archivo. Yo había afirmado que archivos no tenían `@`. Filesystem mostró que SÍ: `@errors-to-rules.md`, `@techniques.md`, `@python-standards.md`.

**Contexto:**
No verifiqué el filesystem antes de afirmar. Asumí basándome en conversación en lugar de verificar evidencia.

**Regla creada:**
```
Antes de afirmar sobre estado de archivos/directorios:
1. Usar Bash/Glob/Read para VERIFICAR
2. NO asumir basándose en conversación previa
3. Si usuario cuestiona tu afirmación → verificar inmediatamente antes de defender

El filesystem es fuente de verdad, no tu memoria de la conversación.
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Confundir configuración global vs proyecto-específica

**Error:**
Mezclé conceptos de `~/.claude/` (Claude Code global) con `/Users/bruno/sec-llm-workbench/.claude/` (META-PROYECTO). Causó confusión al usuario sobre qué estábamos discutiendo.

**Contexto:**
No aclaré explícitamente que estaba cambiando de contexto entre configuración global de Claude Code y configuración del META-PROYECTO.

**Regla creada:**
```
Al discutir configuraciones de Claude Code, SIEMPRE aclarar el scope:

"Esto va en ~/.claude/ (configuración global de usuario)"
vs
"Esto va en /path/proyecto/.claude/ (configuración del proyecto)"
vs
"Esto va en /path/META-PROYECTO/.claude/ (configuración del framework)"

Hacer explícito el scope en CADA mención para evitar confusión.
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Sugerir crear más documentos cuando ya existen suficientes

**Error:**
Sugerí crear "documento de procedimiento de implementación" cuando orchestrator.md y especificación técnica ya contienen toda la información necesaria. Inventé excusas en lugar de admitir que simplemente NO los leo.

**Contexto:**
Usuario señaló que invirtió 10 días creando orchestrator + especificación, y yo sugerí crear MÁS docs. Esto fue evasivo: el problema no es falta de documentación, es que NO consulto la existente.

**Regla creada:**
```
Cuando falles en seguir proceso definido en docs existentes:
1. NO sugerir crear más documentos
2. NO inventar excusas ("el doc no es suficientemente específico")
3. Admitir honestamente: "Los docs son suficientes, el problema es que NO los consulto antes de actuar"

Más documentación NO soluciona el problema de ignorar documentación existente.
```

**Estado:** ✅ Documentado

---

### 2026-01-26: Piloto automático - Ignorar orchestrator y especificaciones (ERROR RAÍZ)

**Error:**
A pesar de tener orchestrator.md (flujo de trabajo completo) y especificación técnica detallada (requisitos exactos), en 2 intentos de implementar SIOPV actué en "piloto automático" basándome en entrenamiento obsoleto sin consultar los documentos.

**Contexto:**
Usuario invirtió 10 días creando orchestrator y especificación con instrucciones claras y específicas. Me dijo que serían suficientes. En ambos intentos de implementación, los ignoré completamente y actué basándome en "experiencia/memoria" con información obsoleta.

**Regla creada:**
```
ESTE ES EL ERROR RAÍZ de esta sesión. Todos los demás errores derivan de este.

Sistema Anti-Autopilot implementado (orchestrator sección 0.5):
1. Comando inicio obligatorio: /project:start-[proyecto]-phase X
   - FUERZA lectura de orchestrator, especificación, errors-to-rules
   - Crea checkpoints verificables

2. Hooks de bloqueo: .claude/hooks/pre-write.sh
   - BLOQUEA Write/Edit sin checkpoints de lectura
   - Verificación mecánica, no depende de "buena voluntad"

3. Confirmación obligatoria:
   - ANTES de cada Write/Edit: anunciar qué harás
   - Especificar qué docs consultaste
   - ESPERAR confirmación del usuario
   - Solo entonces ejecutar

NUNCA confiar en que Claude "recordará" seguir el proceso.
Forzar mecánicamente con hooks + confirmación humana.
```

**Estado:** ⏳ Pendiente implementar sistema Anti-Autopilot

---

## Template para Nuevos Errores

```markdown
### YYYY-MM-DD: [Título del error]

**Error:**
[Qué se hizo mal]

**Contexto:**
[Por qué ocurrió]

**Regla creada:**
```
[Nueva regla específica]
```

**Estado:** ⏳ Pendiente / ✅ Implementado
```

---

## Estadísticas

| Categoría | Errores | Reglas Creadas |
|-----------|---------|----------------|
| Package Management | 1 | 1 |
| Comportamiento | 2 | 2 |
| Arquitectura | 1 | 1 |
| Auditoría | 1 | 1 |
| Proceso de Verificación | 3 | 3 |
| Consulta de Documentación | 1 | 1 |
| Testing | 1 | 1 |
| Honestidad y Verificación | 4 | 4 |
| Comunicación | 1 | 1 |
| Evasión | 1 | 1 |
| Piloto Automático (RAÍZ) | 1 | 1 |
| **Total** | **17** | **17** |

---

## Patrones Identificados

### Patrones de Implementación:
1. **Asumir defaults legacy** - pip, typing.List, Pydantic v1
2. **Pasividad** - Documentar en lugar de ejecutar
3. **Exceso de confirmaciones** - Preguntar lo obvio
4. **Mezclar concerns** - META + PROYECTO juntos
5. **Confiar ciegamente en automatización** - No verificar resultados de grep/búsquedas
6. **Actuar sin consultar documentación oficial** - Asumir sintaxis de memoria en lugar de verificar Context7
7. **Omitir pasos del workflow** - Saltar agentes o pasos del orchestrator asumiendo que "no aplican"
8. **Corregir sin verificar** - Aplicar fixes basándose en error sin validar con agentes
9. **Asumir excepciones por contexto** - "Fase 0 no necesita tests", "commit simple no necesita code-reviewer"

### Patrones Meta (Comunicación y Honestidad):
10. **Inventar autoridad** - Afirmar "X recomienda Y" sin evidencia directa
11. **Afirmar sin datos** - "Más popular", "estándar" con solo 3-5 ejemplos
12. **Shallow research disfrazado** - Presentar 5 fuentes como "deep research"
13. **No verificar antes de afirmar** - Asumir estado del filesystem sin verificar
14. **Scope ambiguo** - No aclarar si hablo de global/proyecto/META-PROYECTO
15. **Evasión con más documentación** - Sugerir más docs en lugar de admitir que ignoro los existentes

### Patrón Raíz (CRÍTICO):
**PILOTO AUTOMÁTICO:** Actuar basándose en "experiencia/memoria" ignorando orchestrator y especificaciones, incluso después de invertir 10 días creándolos.

Este es el ERROR RAÍZ del que derivan todos los demás. Requiere sistema Anti-Autopilot con bloqueo mecánico + confirmación humana.

**Acción:** Sistema Anti-Autopilot implementado en orchestrator sección 0.5 (hooks + comando inicio + confirmación obligatoria).
