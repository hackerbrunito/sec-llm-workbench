---
name: new-project
description: "Crea un nuevo proyecto Python profesional con arquitectura hexagonal"
argument-hint: "[name] [path]"
context: fork
---

# /new-project

Crea un nuevo proyecto Python con arquitectura hexagonal.

## Uso

```
/new-project [nombre] [path]
```

## Comportamiento AUTOMATICO

### 1. Crear Estructura Hexagonal

```bash
mkdir -p $PROJECT_PATH/src/{domain/{entities,value_objects,services},application/{ports,use_cases,services},adapters/{persistence,llm,external_apis},infrastructure/{config,logging,di},interfaces/{api,cli,dashboard}}
mkdir -p $PROJECT_PATH/tests/{unit,integration,e2e}
mkdir -p $PROJECT_PATH/{docs,data/samples}
```

### 2. Generar Archivos desde Templates

Usar templates del META-PROYECTO (`$CLAUDE_PROJECT_DIR/templates/`):
- `pyproject.toml`, `Dockerfile`, `.gitignore`

### 3. Crear Archivos Base

- `src/__init__.py`, `src/domain/exceptions.py`
- `src/infrastructure/config/settings.py` (Pydantic Settings v2)
- `src/infrastructure/logging/setup.py` (structlog)
- `src/interfaces/cli/main.py` (Typer)
- `tests/conftest.py`

### 4. Inicializar Git + uv

```bash
cd $PROJECT_PATH && git init && uv sync && git add . && git commit -m "chore: initial project setup"
```

### 5. Crear Config en META-PROYECTO

Crear `projects/[nombre].md` con path, stack, progreso.
