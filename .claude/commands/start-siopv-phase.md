---
name: "project:start-siopv-phase"
description: "Inicia una fase del proyecto SIOPV con lectura obligatoria de documentación (Anti-Autopilot)"
---

# Comando: /project:start-siopv-phase

**Propósito:** Sistema Anti-Autopilot - Fuerza lectura completa de documentación antes de permitir trabajo.

## Uso

```
/project:start-siopv-phase [número_fase]
```

Ejemplo: `/project:start-siopv-phase 0`

## Qué hace este comando

1. **Lee COMPLETO** el orquestador (orchestrator.md)
2. **Lee COMPLETO** las especificaciones (docs/SIOPV_Propuesta_Tecnica_v2.txt)
3. **Lee COMPLETO** el registro de errores (errors-to-rules.md)
4. **Crea checkpoints** en /tmp/ para verificación por hooks
5. **Solicita confirmación** explícita del usuario antes de proceder

## Parámetros

- `número_fase`: Número de la fase a iniciar (0-5)

## Comportamiento

### Paso 1: Lectura Forzada

Claude DEBE leer los 3 documentos COMPLETOS:

```
.claude/rules/orchestrator.md
docs/SIOPV_Propuesta_Tecnica_v2.txt
.claude/rules/errors-to-rules.md
```

### Paso 2: Creación de Checkpoints

Crea archivos de verificación:

```bash
/tmp/claude-orchestrator-read-YYYYMMDD
/tmp/claude-spec-read-YYYYMMDD
/tmp/claude-errors-read-YYYYMMDD
```

### Paso 3: Confirmación Humana

Claude ANUNCIA:
- Qué documentos leyó
- Qué entendió de la fase actual
- Qué planea hacer a continuación

Luego ESPERA confirmación explícita del usuario.

### Paso 4: Trabajo Autorizado

Solo después de confirmación, Claude puede usar Write/Edit.

## Hooks Relacionados

- `.claude/hooks/pre-write.sh` - Verifica checkpoints antes de Write/Edit

## Ejemplo de Ejecución

```
Usuario: /project:start-siopv-phase 0

Claude:
📖 Leyendo documentación obligatoria...
✅ orchestrator.md leído (5234 líneas)
✅ SIOPV_Propuesta_Tecnica_v2.txt leído (1872 líneas)
✅ errors-to-rules.md leído (235 líneas)

✅ Checkpoints creados en /tmp/

📋 RESUMEN DE FASE 0:
- Objetivo: Setup inicial del proyecto
- Arquitectura: Hexagonal (domain/application/adapters/infrastructure/interfaces)
- Tecnologías: Python 3.11+, uv, Pydantic v2, Typer, structlog
- Deliverables: pyproject.toml, .pre-commit-config.yaml, estructura de directorios
- Línea en spec: 613 (pre-commit hooks)

🤖 PLAN DE ACCIÓN:
1. Verificar estructura de directorios existente
2. Crear/actualizar pyproject.toml
3. Configurar pre-commit hooks
4. Ejecutar TODOS los agentes antes de commit
5. No omitir test-generator ni code-reviewer

❓ ¿Confirmas que proceda con este plan? (sí/no)
```

## Notas

- Los checkpoints expiran al día siguiente (YYYYMMDD)
- Debes re-ejecutar este comando cada día
- Este comando es OBLIGATORIO antes de cualquier trabajo en SIOPV
