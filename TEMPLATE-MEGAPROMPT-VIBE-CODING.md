# PLANTILLA: META-PROYECTO + PROYECTO con Vibe Coding 2026

> **Versión:** 1.2
> **Fecha:** 2026-01-27
> **Uso:** Copiar esta plantilla para iniciar cualquier proyecto nuevo con Vibe Coding
> **Incluye:** Docker multi-stage, DevContainers para VS Code

---

## Placeholder Conventions

All placeholders in this template follow the [Cookiecutter/Jinja2 standard](https://cookiecutter.readthedocs.io/en/stable/advanced/templates_in_context.html): **lowercase_snake_case** inside double curly braces with spaces.

### Variable Registry

| Variable | Description | Example value |
|----------|-------------|---------------|
| `{{ project_name }}` | Human-readable project name | `My Security App` |
| `{{ project_slug }}` | Lowercase, hyphenated (for packages, dirs, URLs) | `my-security-app` |
| `{{ project_description }}` | One-line project description | `AI-powered vulnerability scanner` |
| `{{ project_type }}` | Project type | `CLI Tool`, `API`, `Dashboard` |
| `{{ author_name }}` | Author full name | `Jane Doe` |
| `{{ author_email }}` | Author email | `jane@example.com` |
| `{{ github_user }}` | GitHub username | `janedoe` |
| `{{ main_command }}` | CLI entrypoint command | `my-security-app` |
| `{{ app_port }}` | Application port | `8000` |
| `{{ db_user }}` | Database username | `postgres` |
| `{{ db_password }}` | Database password | `postgres` |
| `{{ db_name }}` | Database name | `my_security_app` |

### Derived Values

Following the Cookiecutter pattern, some values derive from others:

```
project_name    = "My Security App"
project_slug    = project_name | lower | replace(' ', '-')  → "my-security-app"
db_name         = project_name | lower | replace(' ', '_')  → "my_security_app"
```

### Convention Rules

| Context | Convention | Example |
|---------|-----------|---------|
| `.template` files | `{{ lowercase_snake_case }}` | `{{ project_name }}` |
| Documentation (non-template) | `<angle-brackets>` for example values | `<your-username>` |
| Documentation (triggers) | `[UPPER_CASE]` for user-substituted values | `[PROJECT]` |
| Bash scripts | `${VARIABLE}` for environment variables | `${CLAUDE_PROJECT_DIR}` |

---

# PARTE 1: META-PROYECTO (Vibe Coding - Reutilizable)

## 1.1 Estructura de Directorios del META-PROYECTO

```
.claude/
├── settings.json              # Permisos y configuración
├── hooks/                     # Scripts automáticos
│   ├── pre-commit.sh
│   ├── post-code.sh
│   └── verify-best-practices.sh
├── git-workflow.md            # Workflow de Git
├── agents/                    # Subagentes (personalizar por proyecto)
│   └── [agentes-del-proyecto].md
├── commands/                  # Slash commands (personalizar por proyecto)
│   └── [comandos-del-proyecto].md
└── skills/                    # Skills (personalizar por proyecto)
    └── [skills-del-proyecto]/SKILL.md
```

---

## 1.2 PLANTILLA: settings.json

```json
{
  "project": {
    "name": "{{ project_name }}",
    "description": "{{ project_description }}",
    "version": "0.1.0",
    "author": "{{ author_name }}"
  },
  "permissions": {
    "allow": [
      "Bash(uv *)",
      "Bash(ruff *)",
      "Bash(mypy *)",
      "Bash(pytest *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(chmod +x *)",
      "Read(*)",
      "Write(*)",
      "Edit(*)",
      "Glob(*)",
      "Grep(*)"
    ],
    "deny": [
      "Bash(rm -rf /)",
      "Bash(sudo *)",
      "Bash(git push --force *)",
      "Bash(git reset --hard *)"
    ]
  },
  "python": {
    "version": "3.11+",
    "package_manager": "uv",
    "style": {
      "type_hints": "modern (list[str], X | None)",
      "pydantic": "v2 (ConfigDict, field_validator)",
      "logging": "structlog",
      "paths": "pathlib",
      "strings": "f-strings",
      "http": "httpx (async)",
      "async": "required_for_io"
    }
  },
  "verification": {
    "workflow": [
      "best-practices-enforcer",
      "security-auditor",
      "code-reviewer"
    ],
    "required_before_commit": true,
    "hooks": {
      "post_code": ".claude/hooks/post-code.sh",
      "pre_commit": ".claude/hooks/pre-commit.sh",
      "verify_practices": ".claude/hooks/verify-best-practices.sh"
    }
  },
  "mcp_servers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "required": true,
      "use_before_code_generation": true
    }
  },
  "behavior": {
    "auto_fix": true,
    "ask_confirmation": false,
    "self_correcting": true,
    "git_auto_commit": true
  }
}
```

---

## 1.3 PLANTILLA: hooks/pre-commit.sh

```bash
#!/bin/bash
# =============================================================================
# Pre-Commit Hook - Verificación antes de cada commit
# =============================================================================

set -e

echo "🔍 Ejecutando verificaciones pre-commit..."

# 1. Formatear código
echo "📝 Verificando formato..."
uv run ruff format src tests --check || {
    echo "⚠️  Ejecutando ruff format..."
    uv run ruff format src tests
}

# 2. Linting
echo "🔎 Verificando linting..."
uv run ruff check src tests --fix

# 3. Type checking
echo "🔤 Verificando tipos..."
uv run mypy src --ignore-missing-imports

# 4. Tests unitarios
echo "🧪 Ejecutando tests..."
uv run pytest tests/unit -q --tb=short 2>/dev/null || echo "⚠️  No hay tests aún"

echo "✅ Pre-commit completado"
```

---

## 1.4 PLANTILLA: hooks/post-code.sh

```bash
#!/bin/bash
# =============================================================================
# Post-Code Hook - Después de generar código
# =============================================================================

set -e

echo "🔧 Ejecutando post-code..."

# 1. Formatear
uv run ruff format src tests

# 2. Lint + fix
uv run ruff check src tests --fix --unsafe-fixes 2>/dev/null || true

# 3. Organizar imports
uv run ruff check src tests --select I --fix

echo "✅ Post-code completado"
```

---

## 1.5 PLANTILLA: hooks/verify-best-practices.sh

```bash
#!/bin/bash
# =============================================================================
# Verificar Best Practices Python 2026
# =============================================================================

set -e

echo "🎯 Verificando mejores prácticas..."

# Type hints legacy
if grep -r "from typing import List\|from typing import Dict\|from typing import Optional" src/ 2>/dev/null; then
    echo "❌ ERROR: Type hints legacy. Usar list[str], dict[str, int], X | None"
    exit 1
fi

# Pydantic v1
if grep -r "class Config:" src/ 2>/dev/null | grep -v "ConfigDict"; then
    echo "❌ ERROR: Pydantic v1. Usar ConfigDict"
    exit 1
fi

# requests sync
if grep -r "import requests" src/ 2>/dev/null; then
    echo "❌ ERROR: Usar httpx en lugar de requests"
    exit 1
fi

# os.path
if grep -r "os\.path\." src/ 2>/dev/null; then
    echo "❌ ERROR: Usar pathlib en lugar de os.path"
    exit 1
fi

echo "✅ Best practices OK"
```

---

## 1.6 PLANTILLA: git-workflow.md

```markdown
# Git Workflow Automático

## Comportamiento de Claude

### HACER Automáticamente (sin preguntar)
- git add . (después de verificaciones)
- git commit -m "tipo(scope): descripción"
- Incluir Co-Authored-By

### NUNCA Hacer
- git push (sin confirmación)
- git push --force
- git reset --hard

### Convención de Commits
- feat: nueva funcionalidad
- fix: corrección de bug
- refactor: refactorización
- test: tests
- docs: documentación
- chore: mantenimiento

### Formato
```
tipo(scope): descripción corta

Co-Authored-By: Claude <noreply@anthropic.com>
```
```

---

## 1.7 PLANTILLA: Subagente Genérico

```markdown
# {{ agent_name }} Agent

{{ project_description }}

---

## COMPORTAMIENTO MANDATORIO (AUTOMÁTICO)

Cuando este agente sea invocado, **DEBE ejecutar automáticamente**:

1. {{ action_1 }}
2. {{ action_2 }}
3. {{ action_3 }}

**NUNCA preguntar** para acciones estándar.
**SIEMPRE corregir** automáticamente si es posible.

---

## Configuración

```yaml
name: {{ agent_slug }}
description: {{ description }}
allowed-tools:
  - Read
  - Edit
  - Bash
  - Grep
  - Glob
  - WebSearch  # Si necesita buscar en web
  - WebFetch   # Si necesita obtener docs
```

## Checklist
- [ ] {{ checklist_item_1 }}
- [ ] {{ checklist_item_2 }}

## Output
- `✅ {{ agent_name }} PASSED`
- `❌ {{ agent_name }} FAILED` - Con detalles
```

---

# PARTE 2: PROYECTO (Esqueleto - Personalizar)

## 2.1 Estructura de Directorios del PROYECTO

```
{{ project_name }}/
├── CLAUDE.md                  # Instrucciones principales
├── pyproject.toml             # Dependencias (uv)
├── .gitignore
├── .env.example               # Variables de entorno (plantilla)
│
├── .claude/                   # META-PROYECTO (ver Parte 1)
│
├── memory-bank/               # Contexto persistente
│   ├── @architecture.md       # Arquitectura del proyecto
│   ├── @progress.md           # Estado actual
│   └── @decisions.md          # Decisiones arquitectónicas
│
├── src/
│   ├── __init__.py
│   └── {{ modules }}/           # Módulos del proyecto
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docs/
└── data/
```

---

## 2.2 PLANTILLA: CLAUDE.md

```markdown
# {{ project_name }}

> **Autor:** {{ author_name }}
> **Tipo:** {{ project_type }}

---

## REGLAS ABSOLUTAS (NO NEGOCIABLES)

### 1. Package Management
```
SIEMPRE: uv sync, uv run, uv add
NUNCA:   pip install, venv
```

### 2. Type Hints (Python 3.11+)
```python
# ✅ CORRECTO
def process(items: list[str]) -> dict[str, int]: ...
def get_item(id: int) -> Item | None: ...

# ❌ PROHIBIDO
from typing import List, Dict, Optional
```

### 3. Pydantic v2
```python
# ✅ CORRECTO
from pydantic import BaseModel, ConfigDict, field_validator

class MyModel(BaseModel):
    model_config = ConfigDict(strict=True)

    @field_validator("field")
    @classmethod
    def validate(cls, v: str) -> str: ...

# ❌ PROHIBIDO
class Config:
    frozen = True

@validator("field")
def validate(cls, v): ...
```

### 4. HTTP Async
```python
# ✅ CORRECTO
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# ❌ PROHIBIDO
import requests
```

### 5. Logging
```python
# ✅ CORRECTO
import structlog
logger = structlog.get_logger(__name__)

# ❌ PROHIBIDO
print(...)
```

### 6. Paths
```python
# ✅ CORRECTO
from pathlib import Path

# ❌ PROHIBIDO
import os.path
```

### 7. MCP Context7
```
ANTES de generar código con bibliotecas externas:
→ Consultar Context7 para docs actualizadas
→ NO asumir sintaxis
```

### 8. Workflow Automático
```
DESPUÉS de generar código → hooks automáticos
ANTES de commit → verificaciones
Si hay errores → corregir SIN preguntar
```

### 9. Sin Confirmaciones
```
HACER: Implementar, verificar, corregir
NO HACER: "¿Quieres que...?"

Excepciones:
- Decisiones arquitectónicas mayores
- Eliminación de archivos importantes
```

---

## ERRORES PASADOS → REGLAS (Self-Correcting)

| Fecha | Error | Regla Agregada |
|-------|-------|----------------|
| | | |

---

## Arquitectura

{{ architecture_diagram }}

---

## Stack Tecnológico

### Core
- Python 3.11+
- uv (package manager)
- ruff (linter + formatter)
- mypy (type checker)

### {{ category_1 }}
- {{ technology_1 }}
- {{ technology_2 }}

### {{ category_2 }}
- {{ technology_3 }}
- {{ technology_4 }}

---

## Estructura del Proyecto

```
{{ directory_structure }}
```

---

## Comandos

```bash
# Setup
uv sync

# Desarrollo
uv run pytest
uv run ruff check src
uv run mypy src

# Ejecutar
uv run {{ main_command }}
```

---

## Referencias
- `memory-bank/@architecture.md`
- `memory-bank/@progress.md`
- `memory-bank/@decisions.md`
```

---

## 2.3 PLANTILLA: pyproject.toml

```toml
[project]
name = "{{ project_slug }}"
version = "0.1.0"
description = "{{ project_description }}"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "{{ author_name }}", email = "{{ author_email }}"}
]

dependencies = [
    # Core
    "pydantic>=2.5",
    "pydantic-settings>=2.1",

    # {{ category }}
    # "{{ dependency }}>=X.Y",

    # Utilities
    "structlog>=24.1",
    "httpx>=0.26",
    "python-dotenv>=1.0",
    "typer>=0.9",
    "rich>=13.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
    "ruff>=0.1.9",
    "mypy>=1.8",
]

[project.scripts]
{{ project_slug }} = "src.cli:app"

[tool.uv]
dev-dependencies = [
    "pytest>=8.0",
    "pytest-cov>=4.1",
    "pytest-asyncio>=0.23",
    "ruff>=0.1.9",
    "mypy>=1.8",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP", "ARG", "SIM", "TCH", "PTH", "PL", "RUF", "S", "ANN"]
ignore = ["E501", "ANN101", "ANN102"]

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 2.4 PLANTILLA: memory-bank/@architecture.md

```markdown
# {{ project_name }} Architecture

## Visión General

{{ architecture_description }}

---

## Diagrama

```
{{ ascii_diagram }}
```

---

## Componentes

| Componente | Responsabilidad | Tecnología |
|------------|-----------------|------------|
| {{ component_1 }} | {{ responsibility_1 }} | {{ tech_1 }} |
| {{ component_2 }} | {{ responsibility_2 }} | {{ tech_2 }} |

---

## Flujo de Datos

```
{{ data_flow }}
```

---

## Integraciones Externas

- {{ api_1 }}
- {{ api_2 }}
```

---

## 2.5 PLANTILLA: memory-bank/@progress.md

```markdown
# {{ project_name }} Progress Tracker

## Estado Actual

**Fase Actual:** {{ current_phase }}
**Última Actualización:** {{ date }}
**Siguiente Paso:** {{ next_step }}

---

## Progreso

### {{ phase_1_name }} {{ status }}
- [ ] {{ task_1 }}
- [ ] {{ task_2 }}

### {{ phase_2_name }} {{ status }}
- [ ] {{ task_1 }}
- [ ] {{ task_2 }}

---

## Métricas

| Métrica | Valor | Target |
|---------|-------|--------|
| Test Coverage | 0% | 80% |
| Linting | N/A | 0 errors |
| Type Checking | N/A | 0 errors |

---

## Setup

```bash
uv sync
uv run pytest
```

---

## Historial

### {{ date }}
- {{ change_1 }}
- {{ change_2 }}
```

---

## 2.6 PLANTILLA: memory-bank/@decisions.md

```markdown
# {{ project_name }} Architectural Decisions

---

## ADR-001: {{ title }}

**Estado:** Aceptado
**Fecha:** {{ date }}
**Contexto:** {{ context }}

### Opciones Consideradas

1. **{{ option_1 }}**
   - Pros: {{ pros }}
   - Cons: {{ cons }}

2. **{{ option_2 }}**
   - Pros: {{ pros }}
   - Cons: {{ cons }}

### Decisión

**{{ decision }}** porque:
- {{ reason_1 }}
- {{ reason_2 }}

### Consecuencias

- {{ consequence_1 }}
- {{ consequence_2 }}

---

## Decisiones Pendientes

- [ ] {{ pending_decision_1 }}
- [ ] {{ pending_decision_2 }}
```

---

## 2.7 PLANTILLA: .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg

# Virtual environments
.venv/
venv/
ENV/

# uv
.uv/
uv.lock

# IDE
.idea/
.vscode/
*.swp
*.swo
.DS_Store

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/

# Environment
.env
.env.local
*.env

# Project specific
data/
logs/
*.log
```

---

## 2.8 PLANTILLA: tests/conftest.py

```python
"""Pytest configuration and fixtures."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_data_dir(project_root: Path) -> Path:
    """Return the sample data directory."""
    return project_root / "data" / "samples"


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create and return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
```

---

# PARTE 3: CHECKLIST DE NUEVO PROYECTO

## 3.1 Crear Estructura

```bash
# 1. Crear directorio del proyecto
mkdir {{ project_name }}
cd {{ project_name }}

# 2. Inicializar git
git init

# 3. Crear estructura
mkdir -p .claude/{hooks,agents,commands,skills}
mkdir -p memory-bank
mkdir -p src
mkdir -p tests/{unit,integration}
mkdir -p docs data

# 4. Crear archivos base
touch .gitignore
touch pyproject.toml
touch CLAUDE.md
touch .claude/settings.json
touch .claude/git-workflow.md
touch .claude/hooks/{pre-commit.sh,post-code.sh,verify-best-practices.sh}
touch memory-bank/{@architecture.md,@progress.md,@decisions.md}
touch src/__init__.py
touch tests/__init__.py tests/conftest.py
```

## 3.2 Personalizar

1. [ ] Editar `CLAUDE.md` con arquitectura específica
2. [ ] Editar `pyproject.toml` con dependencias específicas
3. [ ] Editar `.claude/settings.json` con nombre del proyecto
4. [ ] Crear subagentes específicos en `.claude/agents/`
5. [ ] Crear commands específicos en `.claude/commands/`
6. [ ] Crear skills específicos en `.claude/skills/`
7. [ ] Documentar arquitectura en `memory-bank/@architecture.md`
8. [ ] Documentar decisiones en `memory-bank/@decisions.md`

## 3.3 Inicializar

```bash
# Hacer hooks ejecutables
chmod +x .claude/hooks/*.sh

# Instalar dependencias
uv sync

# Verificar setup
uv run ruff --version
uv run mypy --version
uv run pytest --version

# Primer commit
git add .
git commit -m "chore: initial project setup with Vibe Coding 2026"
```

---

# PARTE 4: RESUMEN RÁPIDO

## ¿Qué es reutilizable? (META-PROYECTO)

| Componente | Reutilizable | Personalizar |
|------------|--------------|--------------|
| settings.json | 90% | Nombre, descripción |
| hooks/*.sh | 100% | - |
| git-workflow.md | 100% | - |
| pyproject.toml (base) | 70% | Dependencias |
| CLAUDE.md (reglas) | 80% | Arquitectura |
| conftest.py | 80% | Fixtures específicos |
| Dockerfile | 85% | Comando principal |
| docker-compose.yml | 60% | Servicios específicos |
| .dockerignore | 95% | Paths específicos |
| .devcontainer/* | 80% | Puertos, servicios |

## ¿Qué personalizar? (PROYECTO)

| Componente | Crear nuevo |
|------------|-------------|
| Subagentes | Específicos del dominio |
| Commands | Específicos del proyecto |
| Skills | Específicos del proyecto |
| @architecture.md | Diagrama del proyecto |
| @decisions.md | ADRs del proyecto |
| src/ | Todo el código |

---

# PARTE 5: DOCKER Y DEVCONTAINERS (Opcional)

## 5.1 PLANTILLA: Dockerfile (Multi-stage)

```dockerfile
# =============================================================================
# {{ project_name }} - Dockerfile Multi-stage
# =============================================================================

# -----------------------------------------------------------------------------
# Base stage: Common setup
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS base

# Metadata
LABEL maintainer="{{ author_name }} <{{ author_email }}>"
LABEL description="{{ project_description }}"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# -----------------------------------------------------------------------------
# Builder stage: Install dependencies
# -----------------------------------------------------------------------------
FROM base AS builder

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Create virtual environment and install dependencies
RUN uv sync --no-dev

# -----------------------------------------------------------------------------
# Production stage: Minimal image for production
# -----------------------------------------------------------------------------
FROM base AS production

# Create non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid 1000 -m appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser src/ /app/src/

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER appuser

# Default command (customize per project)
CMD ["python", "-m", "src.main"]

# -----------------------------------------------------------------------------
# Development stage: Full development environment
# -----------------------------------------------------------------------------
FROM base AS development

# Install development dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Install additional dev tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Default command for development
CMD ["sleep", "infinity"]
```

---

## 5.2 PLANTILLA: .dockerignore

```dockerignore
# Git
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
*.egg
dist/
build/

# Virtual environments
.venv/
venv/
ENV/
.uv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Environment files (secrets!)
.env
.env.local
.env.*.local
*.env

# Logs
logs/
*.log

# Data (puede ser muy grande)
data/
!data/.gitkeep

# Documentation build
docs/_build/
site/

# OS
.DS_Store
Thumbs.db

# Docker
Dockerfile
docker-compose*.yml
.dockerignore

# DevContainers
.devcontainer/

# Claude Code
.claude/

# Memory bank
memory-bank/

# Temporary files
*.tmp
*.temp
tmp/
temp/
```

---

## 5.3 PLANTILLA: docker-compose.yml

```yaml
# =============================================================================
# {{ project_name }} - Docker Compose
# =============================================================================

services:
  # ===========================================================================
  # Main Application
  # ===========================================================================
  app:
    build:
      context: .
      target: development
    container_name: {{ project_slug }}-app
    volumes:
      - .:/app
      - app-venv:/app/.venv
    environment:
      - PYTHONUNBUFFERED=1
      # Add service-specific environment variables
      # - SERVICE_HOST={{ service_name }}
      # - SERVICE_PORT={{ service_port }}
    # depends_on:
    #   - {{ service_name }}
    networks:
      - {{ project_slug }}-network
    ports:
      - "{{ app_port }}:{{ app_port }}"
    command: ["uv", "run", "{{ main_command }}"]

  # ===========================================================================
  # Additional Services (uncomment as needed)
  # ===========================================================================

  # Example: PostgreSQL Database
  # postgres:
  #   image: postgres:16
  #   container_name: {{ project_slug }}-postgres
  #   environment:
  #     - POSTGRES_USER={{ db_user }}
  #     - POSTGRES_PASSWORD={{ db_password }}
  #     - POSTGRES_DB={{ db_name }}
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"
  #   networks:
  #     - {{ project_slug }}-network

  # Example: Redis Cache
  # redis:
  #   image: redis:7-alpine
  #   container_name: {{ project_slug }}-redis
  #   ports:
  #     - "6379:6379"
  #   networks:
  #     - {{ project_slug }}-network

  # ===========================================================================
  # Tests Runner (optional, for CI)
  # ===========================================================================
  tests:
    build:
      context: .
      target: development
    container_name: {{ project_slug }}-tests
    volumes:
      - .:/app
    environment:
      - PYTHONUNBUFFERED=1
    networks:
      - {{ project_slug }}-network
    command: ["uv", "run", "pytest", "-v", "--cov=src", "--cov-report=term-missing"]
    profiles:
      - testing

# =============================================================================
# Networks
# =============================================================================
networks:
  {{ project_slug }}-network:
    driver: bridge

# =============================================================================
# Volumes
# =============================================================================
volumes:
  app-venv:
    driver: local
  # postgres-data:
  #   driver: local
```

---

## 5.4 PLANTILLA: .devcontainer/devcontainer.json

```json
{
  "name": "{{ project_name }} Development",
  "dockerComposeFile": ["../docker-compose.yml", "docker-compose.devcontainer.yml"],
  "service": "devcontainer",
  "workspaceFolder": "/app",

  // Features to add to the dev container
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/node:1": {
      "version": "lts"
    }
  },

  // VS Code settings
  "customizations": {
    "vscode": {
      "settings": {
        "python.defaultInterpreterPath": "/app/.venv/bin/python",
        "python.formatting.provider": "none",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
          "source.fixAll.ruff": "explicit",
          "source.organizeImports.ruff": "explicit"
        },
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true
        },
        "python.analysis.typeCheckingMode": "strict",
        "python.analysis.autoImportCompletions": true,
        "files.exclude": {
          "**/__pycache__": true,
          "**/.pytest_cache": true,
          "**/.mypy_cache": true,
          "**/.ruff_cache": true,
          "**/*.pyc": true
        },
        "terminal.integrated.defaultProfile.linux": "bash"
      },
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "tamasfe.even-better-toml",
        "redhat.vscode-yaml",
        "ms-azuretools.vscode-docker",
        "eamodio.gitlens",
        "streetsidesoftware.code-spell-checker",
        "GitHub.copilot",
        "GitHub.copilot-chat"
      ]
    }
  },

  // Post-create command
  "postCreateCommand": "uv sync && uv run pre-commit install || true",

  // Post-start command
  "postStartCommand": "echo '🚀 {{ project_name }} DevContainer ready!'",

  // Environment variables
  "containerEnv": {
    "PYTHONUNBUFFERED": "1",
    "PYTHONDONTWRITEBYTECODE": "1"
  },

  // Forward ports (customize per project)
  "forwardPorts": [8000],
  "portsAttributes": {
    "8000": {"label": "Main App", "onAutoForward": "notify"}
  },

  // Run as non-root user
  "remoteUser": "vscode"
}
```

---

## 5.5 PLANTILLA: .devcontainer/docker-compose.devcontainer.yml

```yaml
# =============================================================================
# DevContainer Docker Compose Override
# =============================================================================
# Extends docker-compose.yml for VS Code DevContainers
# =============================================================================

services:
  devcontainer:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile
    container_name: {{ project_slug }}-devcontainer
    volumes:
      - ..:/app:cached
      - devcontainer-venv:/app/.venv
      - ~/.gitconfig:/home/vscode/.gitconfig:ro
      - ~/.ssh:/home/vscode/.ssh:ro
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONDONTWRITEBYTECODE=1
      # Add service connections
      # - SERVICE_HOST={{ service_name }}
      # - SERVICE_PORT={{ service_port }}
    # depends_on:
    #   - {{ service_name }}
    networks:
      - {{ project_slug }}-network
    # Keep container running
    command: sleep infinity

volumes:
  devcontainer-venv:
    driver: local
```

---

## 5.6 PLANTILLA: .devcontainer/Dockerfile

```dockerfile
# =============================================================================
# {{ project_name }} - DevContainer Dockerfile
# =============================================================================
# Optimized image for VS Code DevContainers development
# =============================================================================

FROM python:3.11-slim

# Metadata
LABEL maintainer="{{ author_name }} <{{ author_email }}>"
LABEL description="{{ project_name }} DevContainer for VS Code"

# Avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Essential tools
    curl \
    wget \
    git \
    # Build tools (for some Python packages)
    build-essential \
    # Useful utilities
    vim \
    less \
    jq \
    # For health checks
    netcat-openbsd \
    # Clean up
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user 'vscode' (standard for DevContainers)
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN pip install uv

# Set working directory
WORKDIR /app

# Change ownership of /app to vscode user
RUN chown -R $USERNAME:$USERNAME /app

# Switch to non-root user
USER $USERNAME

# Add local bin to PATH for user-installed tools
ENV PATH="/home/$USERNAME/.local/bin:$PATH"

# Copy pyproject.toml and install dependencies
# (This will be overwritten by the volume mount, but helps with caching)
COPY --chown=$USERNAME:$USERNAME pyproject.toml ./
COPY --chown=$USERNAME:$USERNAME uv.lock* ./

# Install dependencies
RUN uv sync || true

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["sleep", "infinity"]
```

---

## 5.7 Estructura de Directorios Actualizada (con Docker)

```
{{ project_name }}/
├── CLAUDE.md
├── pyproject.toml
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Servicios principales
├── .dockerignore
├── .gitignore
├── .env.example
│
├── .devcontainer/             # VS Code DevContainers
│   ├── devcontainer.json
│   ├── docker-compose.devcontainer.yml
│   └── Dockerfile
│
├── .claude/                   # META-PROYECTO
│   ├── settings.json
│   ├── hooks/
│   ├── git-workflow.md
│   ├── agents/
│   ├── commands/
│   └── skills/
│
├── memory-bank/
├── src/
├── tests/
├── docs/
└── data/
```

---

## 5.8 Comandos Docker

```bash
# Desarrollo con Docker Compose
docker compose up -d           # Iniciar servicios
docker compose logs -f app     # Ver logs
docker compose exec app bash   # Shell en el contenedor
docker compose down            # Detener servicios

# Tests en Docker
docker compose --profile testing run tests

# Build production image
docker build --target production -t {{ project_slug }}:latest .

# VS Code DevContainers
# Abrir VS Code → Command Palette → "Dev Containers: Reopen in Container"
```

---

## 5.9 Checklist Docker (añadir a Parte 3)

```bash
# 5. Crear archivos Docker (si se usa)
touch Dockerfile
touch .dockerignore
touch docker-compose.yml

# 6. Crear DevContainers (si se usa VS Code)
mkdir -p .devcontainer
touch .devcontainer/devcontainer.json
touch .devcontainer/docker-compose.devcontainer.yml
touch .devcontainer/Dockerfile
```

---

**FIN DE PLANTILLA**
