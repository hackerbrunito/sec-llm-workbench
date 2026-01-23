# /new-project Command

Crea un nuevo proyecto Python profesional con arquitectura hexagonal.

---

## Uso

```
/new-project [nombre] [path]
```

**Ejemplos:**
```
/new-project mi-api ~/mi-api
/new-project data-pipeline ~/data-pipeline
```

---

## Comportamiento AUTOMÁTICO

Cuando se ejecute este comando, Claude DEBE ejecutar **SIN PREGUNTAR**:

### 1. Crear Estructura Hexagonal
```bash
PROJECT_PATH="$2"
PROJECT_NAME="$1"

mkdir -p $PROJECT_PATH/src/{domain/{entities,value_objects,services},application/{ports,use_cases,services},adapters/{persistence,llm,external_apis},infrastructure/{config,logging,di},interfaces/{api,cli,dashboard}}
mkdir -p $PROJECT_PATH/tests/{unit,integration,e2e}
mkdir -p $PROJECT_PATH/{docs,data/samples}
```

### 2. Generar Archivos desde Templates
Usar templates del META-PROYECTO (`$CLAUDE_PROJECT_DIR/templates/`):
- `pyproject.toml` ← `pyproject.toml.template`
- `Dockerfile` ← `Dockerfile.template`
- `.gitignore` ← `.gitignore.template`

Reemplazar variables:
- `{{ PROJECT_NAME }}` → nombre del proyecto (MAYÚSCULAS)
- `{{ project_name_lower }}` → nombre en minúsculas
- `{{ project_description }}` → descripción breve
- `{{ author_name }}` → nombre del autor (preguntar si no está en config)
- `{{ github_user }}` → usuario de GitHub (preguntar si no está en config)

### 3. Crear Archivos Base
```python
# src/__init__.py
"""{{ PROJECT_NAME }} - {{ project_description }}"""
__version__ = "0.1.0"

# src/domain/exceptions.py
# src/infrastructure/config/settings.py (Pydantic Settings v2)
# src/infrastructure/logging/setup.py (structlog)
# src/interfaces/cli/main.py (Typer)
# tests/conftest.py (fixtures base)
```

### 4. Crear README.md Profesional
Con badges, instalación, uso, arquitectura.

### 5. Crear .env.example
Variables de entorno necesarias.

### 6. Inicializar Git + uv
```bash
cd $PROJECT_PATH
git init
uv sync
git add .
git commit -m "chore: initial project setup with hexagonal architecture"
```

### 7. Crear Config en META-PROYECTO
Crear `projects/[nombre].md` con:
- Path del proyecto
- Stack tecnológico
- Progreso de fases

---

## Archivos Generados

```
$PROJECT_PATH/
├── pyproject.toml          # Desde template
├── Dockerfile              # Multi-stage con uv
├── docker-compose.yml      # Servicios base
├── .gitignore              # Desde template
├── .env.example
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── services/
│   │   └── exceptions.py
│   ├── application/
│   │   ├── ports/
│   │   ├── use_cases/
│   │   └── services/
│   ├── adapters/
│   ├── infrastructure/
│   │   ├── config/settings.py
│   │   └── logging/setup.py
│   └── interfaces/
│       └── cli/main.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── docs/
```

---

## Output Esperado

```
✅ Proyecto creado: {{ PROJECT_NAME }}
   Path: {{ path }}
   Arquitectura: Hexagonal (Ports & Adapters)

Estructura generada:
├── src/domain/          # Entidades y reglas de negocio
├── src/application/     # Casos de uso y puertos
├── src/adapters/        # Implementaciones concretas
├── src/infrastructure/  # Config, logging, DI
├── src/interfaces/      # CLI, API, Dashboard
└── tests/               # Unit, integration, e2e

Verificaciones:
✅ pyproject.toml generado
✅ Dockerfile multi-stage
✅ Git inicializado
✅ uv sync completado

Próximos pasos:
1. cd {{ path }}
2. Configurar .env desde .env.example
3. uv run {{ project_name_lower }} --help

Config META-PROYECTO: projects/{{ project_name_lower }}.md
```
