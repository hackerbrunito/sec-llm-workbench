---
name: init-session
description: "Inicia sesion de desarrollo con lectura obligatoria de documentacion"
disable-model-invocation: true
---

# /init-session

Inicializa sesion de desarrollo con lectura de documentacion y creacion de checkpoints.

## Uso

```
/init-session [numero_fase]
```

## Comportamiento

### Paso 1: Lectura Forzada

Claude DEBE leer los 3 documentos COMPLETOS:

```
.claude/workflow/ (todos los archivos)
[especificacion del proyecto segun projects/*.md]
.claude/docs/errors-to-rules.md
```

### Paso 2: Creacion de Checkpoints

```bash
mkdir -p "$CLAUDE_PROJECT_DIR/.build/checkpoints/daily"
touch "$CLAUDE_PROJECT_DIR/.build/checkpoints/daily/orchestrator-read-$(date +%Y%m%d)"
touch "$CLAUDE_PROJECT_DIR/.build/checkpoints/daily/spec-read-$(date +%Y%m%d)"
touch "$CLAUDE_PROJECT_DIR/.build/checkpoints/daily/errors-read-$(date +%Y%m%d)"
```

Checkpoints se guardan en `.build/checkpoints/daily/` (gitignored), expiran diariamente.

### Paso 3: Anuncio

```
DOCUMENTACION LEIDA:
- orchestrator/workflow (completo)
- [Especificacion] (completo)
- errors-to-rules.md ([N] reglas)

CHECKPOINT: Fase [X] - [Nombre]
Objetivos: [lista]
Deliverables: [lista]

Confirmas iniciar esta fase? (si/no)
```

### Paso 4: Proceder con Autonomia

Despues de confirmacion, Claude trabaja autonomamente con Reflexion Loop (PRA Pattern).
