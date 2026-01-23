# META-PROYECTO: Framework Vibe Coding 2026

> **Propósito:** Framework para generar proyectos Python profesionales con técnicas de Vibe Coding
> **Autor:** [AUTHOR_NAME]
> **Versión:** 2.0

---

## QUÉ ES ESTE PROYECTO

Este es un **META-PROYECTO** (framework generador), NO un proyecto de software convencional.

```
META-PROYECTO (aquí)              PROYECTO GENERADO
────────────────────              ──────────────────
Framework de Vibe Coding    →     Proyecto limpio y profesional
Configuración de Claude     →     Código exportable
Técnicas de desarrollo      →     Sin rastro de Vibe Coding
```

### Proyectos Activos

| Proyecto | Path | Descripción |
|----------|------|-------------|
| (ejemplo) | `~/<proyecto>/` | Descripción del proyecto |

Ver configuración específica en `projects/[nombre].md`

> **Nota:** Agregar proyectos reales a esta tabla según se vayan creando.

---

## ORQUESTADOR (LEER OBLIGATORIO)

**Al iniciar cada sesión, Claude carga automáticamente:**

```
.claude/rules/orchestrator.md  ← SE CARGA AUTOMÁTICAMENTE
```

Este archivo define:
- **Triggers** - Cómo detectar qué hacer
- **Estados** - En qué fase está el proyecto
- **Flujo** - Loop de desarrollo autónomo
- **Agentes** - Cuándo y cómo invocarlos
- **Decisiones** - Qué hacer sin preguntar

**El orquestador es el CEREBRO del Vibe Coding.**

---

## REGLAS ABSOLUTAS (NO NEGOCIABLES)

### 1. Separación META vs PROYECTO
```
TODO el código generado va en el PROYECTO DESTINO (ej: ~/<proyecto>/)
NUNCA crear código de aplicación en este META-PROYECTO
Este directorio es SOLO configuración de Vibe Coding
```

### 2. Proyecto Limpio
```
El proyecto generado DEBE ser exportable sin este META-PROYECTO
NUNCA incluir .claude/, memory-bank/, hooks en el proyecto destino
El proyecto destino debe funcionar con un simple: git clone + uv sync
```

### 3. Package Management
```
SIEMPRE: uv sync, uv run, uv add
NUNCA:   pip install, pip freeze, python -m venv
```

### 4. Type Hints (Python 3.11+)
```python
# CORRECTO
def process(items: list[str]) -> dict[str, int]: ...
def get_user(id: int) -> User | None: ...

# PROHIBIDO
from typing import List, Dict, Optional
```

### 5. Pydantic v2 (NO v1)
```python
# CORRECTO
from pydantic import BaseModel, ConfigDict, field_validator

class Model(BaseModel):
    model_config = ConfigDict(strict=True)

    @field_validator("field")
    @classmethod
    def validate(cls, v: str) -> str: ...

# PROHIBIDO
class Config:
    frozen = True

@validator("field")
def validate(cls, v): ...
```

### 6. HTTP Async
```python
# CORRECTO
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# PROHIBIDO
import requests
```

### 7. Logging
```python
# CORRECTO
import structlog
logger = structlog.get_logger(__name__)

# PROHIBIDO
print(...)
```

### 8. Paths
```python
# CORRECTO
from pathlib import Path

# PROHIBIDO
import os.path
```

### 9. MCP Context7 (OBLIGATORIO)
```
ANTES de generar código con bibliotecas externas:
1. Consultar Context7 para docs actualizadas
2. Verificar sintaxis y patrones actuales
3. NO asumir - SIEMPRE verificar
```

### 10. Sin Confirmaciones
```
HACER: Implementar, verificar, corregir
NO HACER: "¿Quieres que...?", "¿Debería...?"

Excepciones (preguntar):
- Decisiones arquitectónicas mayores
- Eliminación de archivos importantes
- Cambios irreversibles
```

### 11. Workflow Automático con Verificación

```
DESPUÉS de generar código, EJECUTAR AUTOMÁTICAMENTE:

[Generar código]
       ↓
[spawn best-practices-enforcer] → ❌ Rechazado → [Corregir] → ↩️
       ↓ ✅
[spawn security-auditor] → ❌ Rechazado → [Corregir] → ↩️
       ↓ ✅
[spawn hallucination-detector] → ❌ Rechazado → [Corregir] → ↩️
       ↓ ✅
[ruff format + ruff check --fix]
       ↓
[mypy src]
       ↓
[Commit permitido]
```

**Regla:** El usuario define QUÉ, Claude decide CÓMO y lo HACE.

---

## ERRORES PASADOS → REGLAS (Self-Correcting)

> Cada error se documenta para no repetirlo.
> Claude DEBE agregar nuevas reglas cuando cometa errores.

| Fecha | Error | Regla Agregada |
|-------|-------|----------------|
| 2026-01-20 | Usar pip en lugar de uv | Regla #3: SIEMPRE uv |
| 2026-01-20 | Subagentes pasivos | Subagentes con COMPORTAMIENTO ACTIVO |
| 2026-01-20 | Pedir confirmaciones innecesarias | Regla #10: Sin confirmaciones |
| 2026-01-21 | META-PROYECTO dentro de [PROYECTO] | Regla #1: Separación META vs PROYECTO |
| 2026-01-22 | Referencias a proyecto específico en orchestrator.md | META-PROYECTO 100% genérico, usar [PROYECTO] |
| 2026-01-22 | orchestrator.md en .claude/ no se carga automáticamente | Usar .claude/rules/ para carga automática |
| 2026-01-22 | Agents sin YAML frontmatter moderno | Usar formato: name, description, tools |
| 2026-01-22 | README.md con referencias a proyecto específico | Usar [PROYECTO] en toda documentación |

### Cómo Agregar Nuevas Reglas

1. Identificar el error específico
2. Agregar fila a la tabla
3. Si es patrón recurrente, crear REGLA ABSOLUTA
4. Documentar en `memory-bank/@errors-to-rules.md`

---

## ESTRUCTURA DEL META-PROYECTO

```
<meta-proyecto>/  # Cualquier nombre de directorio
├── CLAUDE.md                     # Este archivo (instrucciones principales)
├── .mcp.json                     # Configuración MCP servers (Context7)
├── .gitignore
│
├── .claude/
│   ├── settings.json             # Permisos (allow/deny)
│   ├── rules/                    # SE CARGAN AUTOMÁTICAMENTE
│   │   └── orchestrator.md       # CEREBRO - Flujo autónomo
│   ├── hooks/                    # Enforcement automático
│   │   ├── session-start.sh      # Auto-crea .env al iniciar sesión
│   │   ├── post-code.sh          # Ruff format/check después de Write/Edit
│   │   ├── pre-commit.sh         # Verificación antes de commit
│   │   └── verify-best-practices.sh
│   ├── agents/                   # 7 Subagentes activos
│   │   ├── best-practices-enforcer.md
│   │   ├── security-auditor.md
│   │   ├── code-reviewer.md
│   │   ├── test-generator.md
│   │   ├── vulnerability-researcher.md
│   │   ├── xai-explainer.md
│   │   └── hallucination-detector.md
│   ├── commands/                 # 6 Slash commands
│   │   ├── new-project.md
│   │   ├── verify.md
│   │   ├── scan-vulnerabilities.md
│   │   ├── run-tests.md
│   │   ├── generate-report.md
│   │   └── research-cve.md
│   ├── skills/                   # 7 Skills (patrones de referencia)
│   │   ├── coding-standards-2026/
│   │   ├── langraph-patterns/
│   │   ├── trivy-integration/
│   │   ├── xai-visualization/
│   │   ├── cve-research/
│   │   ├── openfga-patterns/
│   │   └── presidio-dlp/
│   └── git-workflow.md           # Workflow Git + Worktrees
│
├── memory-bank/
│   ├── @techniques.md            # Técnicas Vibe Coding
│   ├── @python-standards.md      # Estándares Python 2026
│   └── @errors-to-rules.md       # Log de errores→reglas
│
├── templates/                    # Plantillas para proyectos
│   ├── pyproject.toml.template
│   ├── Dockerfile.template
│   ├── docker-compose.yml.template
│   └── README.md.template
│
└── projects/                     # Config por proyecto
    └── [proyecto].md             # Un archivo por proyecto
```

---

## CÓMO USAR ESTE META-PROYECTO

### Configuración Inicial (solo una vez)

```bash
cd ~/vibe-coding  # Tu directorio del META-PROYECTO
cp .env.example .env
# Editar .env y añadir UPSTASH_API_KEY
```

### Iniciar Sesión de Desarrollo

```bash
cd ~/vibe-coding  # Tu directorio del META-PROYECTO
claude
# Escribir: "Continúa con [PROYECTO]"
```

Claude carga automáticamente:
1. `.env` (variables de entorno)
2. `CLAUDE.md` (instrucciones)
3. `.mcp.json` (MCP servers)
4. `.claude/settings.json` (permisos y hooks)

### Crear Nuevo Proyecto

```bash
# Usar comando /new-project o pedir:
"Crear nuevo proyecto llamado X en ~/X/"
```

### Cambiar de Proyecto Activo

```bash
# Editar projects/[nombre].md o pedir:
"Trabajar en el proyecto Y"
```

---

## PROYECTOS ACTUALES

> Los proyectos activos se definen en `projects/[nombre].md`
> Formato de cada proyecto:
> - **Path:** `~/<proyecto>/`
> - **Tipo:** Tipo de proyecto
> - **Descripción:** Descripción breve
> - **Config:** `projects/<proyecto>.md`

---

## MCP SERVERS

### Context7 (CRÍTICO)

Configurado en `.mcp.json` (raíz del proyecto).

**Configuración de API Key:**
```bash
# 1. Copiar plantilla
cp .env.example .env

# 2. Editar .env y añadir tu API key
UPSTASH_API_KEY=tu-api-key-de-upstash
```

Claude Code carga `.env` automáticamente al iniciar. No se necesita configuración adicional.

**Obtener API Key:** https://console.upstash.com/

**Uso OBLIGATORIO** antes de generar código con bibliotecas externas.

---

## VERIFICACIÓN

```bash
# Verificar que el proyecto destino es exportable
cd ~/<proyecto>
ls -la  # NO debe tener .claude/, memory-bank/

# Verificar que funciona independiente
git clone [url] test-clone
cd test-clone
uv sync
uv run pytest
```

---

## REFERENCIAS

- `.claude/rules/orchestrator.md` - **CEREBRO** - Flujo autónomo (CARGA AUTOMÁTICA)
- `projects/[proyecto].md` - Configuración específica de cada proyecto
- `memory-bank/@techniques.md` - Técnicas de Vibe Coding
- `memory-bank/@python-standards.md` - Estándares Python 2026
- `.claude/git-workflow.md` - Workflow de Git
- `TEMPLATE-MEGAPROMPT-VIBE-CODING.md` - Plantilla reutilizable
