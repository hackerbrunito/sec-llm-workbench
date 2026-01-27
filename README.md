# META-PROYECTO: Vibe Coding Framework 2026

Framework para generar proyectos Python profesionales de forma 100% autónoma usando Claude Code y técnicas de Vibe Coding.

🌐 *[English version below](#meta-project-vibe-coding-framework-2026)*

---

## Qué es esto

Este es un **META-PROYECTO** (framework generador), no un proyecto de software convencional.

```
META-PROYECTO (este repo)          PROYECTO GENERADO
─────────────────────────          ──────────────────
Framework de Vibe Coding     →     Proyecto limpio y profesional
Configuración de Claude      →     Código exportable
Agentes y Skills             →     Sin rastro de Vibe Coding
```

El proyecto generado es completamente independiente y funciona con `git clone + uv sync`.

## Plataformas Soportadas

| Plataforma | Soporte |
|------------|---------|
| **Linux** | Soporte nativo |
| **macOS** | Soporte nativo |
| **Windows 10/11** | Requiere WSL2 o Git Bash |

> **Usuarios de Windows:** Este framework usa scripts bash para hooks y automatización. Para ejecutarlo en Windows, necesitas:
> - [WSL2 (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) - Recomendado
> - [Git Bash](https://git-scm.com/downloads) - Incluido con Git para Windows
>
> Consulta la documentación oficial para instalación y configuración.

## Requisitos

| Requisito | Instalación |
|-----------|-------------|
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |
| Node.js 18+ | [nodejs.org](https://nodejs.org/) |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | Según tu sistema operativo |
| Upstash API Key | [console.upstash.com](https://console.upstash.com/) |

## Instalación

```bash
# 1. Clonar el repositorio (puedes usar cualquier nombre de directorio)
git clone <repo-url> ~/<your-directory>
cd ~/<your-directory>

# 2. Configurar variables de entorno
cp .env.example .env
# Editar .env y añadir UPSTASH_API_KEY
```

> **Nota:** El directorio puede tener cualquier nombre. El framework es agnóstico al nombre del directorio.

## Uso

### Continuar un proyecto existente

```bash
cd ~/<your-directory>  # O el nombre que hayas elegido
claude
```

Escribir el trigger:
```
Continúa con [PROYECTO]
```

### Crear un proyecto nuevo

1. Copiar las plantillas:
```bash
cp docs/project-spec.md.example docs/<your-project>-spec.md
cp projects/project-config.md.example projects/<your-project>.md
```

2. Editar la especificación y configuración con los detalles de tu proyecto.

3. Lanzar Claude:
```bash
cd ~/<your-directory>
claude
> Continúa con <your-project>
```

## Estructura

```
<meta-proyecto>/
├── README.md                     # Este archivo
├── CLAUDE.md                     # Instrucciones principales (auto-load)
├── .env.example                  # Template de variables
├── .mcp.json                     # Context7 MCP server
│
├── .claude/
│   ├── settings.json             # Permisos y hooks
│   ├── rules/
│   │   └── orchestrator.md       # Flujo autónomo (auto-load)
│   ├── agents/                   # 7 agentes con YAML frontmatter
│   ├── commands/                 # 6 slash commands
│   ├── skills/                   # 7 skills con SKILL.md
│   └── hooks/                    # Scripts de enforcement
│
├── templates/                    # Templates para proyectos nuevos
├── memory-bank/                  # Técnicas y estándares
├── docs/                         # Especificaciones de proyectos
│   └── project-spec.md.example   # Plantilla de especificación
└── projects/                     # Configuración por proyecto
    └── project-config.md.example # Plantilla de configuración
```

## Triggers Disponibles

| Trigger | Acción |
|---------|--------|
| `Continúa con [PROYECTO]` | Continuar proyecto existente |
| `Trabaja en [PROYECTO]` | Igual que el anterior |
| `Crea un nuevo proyecto [NOMBRE]` | Crear proyecto desde cero |
| (sin instrucción) | Claude busca proyecto activo y continúa |

## Agentes

| Agente | Modelo | Función |
|--------|--------|---------|
| best-practices-enforcer | haiku | Verificar Python 2026 best practices |
| security-auditor | sonnet | Auditar OWASP Top 10, secrets, LLM security |
| code-reviewer | sonnet | Review de calidad y mantenibilidad |
| test-generator | sonnet | Generar tests unitarios |
| hallucination-detector | sonnet | Verificar código contra docs oficiales |
| vulnerability-researcher | sonnet | Investigar CVEs (NVD, GitHub, EPSS) |
| xai-explainer | sonnet | Explicabilidad ML con SHAP/LIME |

## Flujo Autónomo

```
Trigger
   │
   ▼
Cargar CLAUDE.md + orchestrator.md (automático)
   │
   ▼
Leer projects/[proyecto].md
   │
   ▼
Leer especificación del proyecto
   │
   ▼
Detectar estado actual
   │
   ▼
┌─────────────────────────────────┐
│         LOOP PRINCIPAL          │
│                                 │
│  Generar código                 │
│       │                         │
│       ▼                         │
│  Verificar (agentes)            │
│       │                         │
│       ▼                         │
│  ¿Pasó? ──No──► Corregir ──┐   │
│       │                     │   │
│      Sí◄────────────────────┘   │
│       │                         │
│       ▼                         │
│  Commit                         │
│       │                         │
│       ▼                         │
│  Siguiente tarea                │
│       │                         │
│       ▼                         │
│  ¿Completado? ──No──► LOOP     │
│       │                         │
│      Sí                         │
│       │                         │
└───────┼─────────────────────────┘
        ▼
   Proyecto terminado
```

## Best Practices Aplicadas

- **Python 3.11+**: Type hints modernos (`list[str]`, `X | None`)
- **Pydantic v2**: `ConfigDict`, `@field_validator`
- **Async HTTP**: `httpx` (no `requests`)
- **Logging**: `structlog` (no `print`)
- **Paths**: `pathlib` (no `os.path`)
- **Package Manager**: `uv` (no `pip`)

## Self-Correcting

Los errores se documentan automáticamente en `CLAUDE.md` tabla "ERRORES PASADOS → REGLAS" para no repetirlos.

## Autor

`<your-name>` (`<your-github-profile>`)

## Licencia

MIT

---

# META-PROJECT: Vibe Coding Framework 2026

Framework to generate professional Python projects 100% autonomously using Claude Code and Vibe Coding techniques.

---

## What is this

This is a **META-PROJECT** (generator framework), not a conventional software project.

```
META-PROJECT (this repo)           GENERATED PROJECT
────────────────────────           ──────────────────
Vibe Coding Framework        →     Clean, professional project
Claude Configuration         →     Exportable code
Agents and Skills            →     No trace of Vibe Coding
```

The generated project is completely independent and works with `git clone + uv sync`.

## Supported Platforms

| Platform | Support |
|----------|---------|
| **Linux** | Native support |
| **macOS** | Native support |
| **Windows 10/11** | Requires WSL2 or Git Bash |

> **Windows users:** This framework uses bash scripts for hooks and automation. To run on Windows, you need either:
> - [WSL2 (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/install) - Recommended
> - [Git Bash](https://git-scm.com/downloads) - Comes with Git for Windows
>
> Please refer to their official documentation for installation and configuration.

## Requirements

| Requirement | Installation |
|-------------|--------------|
| Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |
| Node.js 18+ | [nodejs.org](https://nodejs.org/) |
| uv | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | According to your operating system |
| Upstash API Key | [console.upstash.com](https://console.upstash.com/) |

## Installation

```bash
# 1. Clone the repository (you can use any directory name)
git clone <repo-url> ~/<your-directory>
cd ~/<your-directory>

# 2. Configure environment variables
cp .env.example .env
# Edit .env and add UPSTASH_API_KEY
```

> **Note:** The directory can have any name. The framework is directory-name agnostic.

## Usage

### Continue an existing project

```bash
cd ~/<your-directory>  # Or the name you chose
claude
```

Write the trigger:
```
Continue with [PROJECT]
```

### Create a new project

1. Copy the templates:
```bash
cp docs/project-spec.md.example docs/<your-project>-spec.md
cp projects/project-config.md.example projects/<your-project>.md
```

2. Edit the specification and configuration with your project details.

3. Launch Claude:
```bash
cd ~/<your-directory>
claude
> Continue with <your-project>
```

## Structure

```
<meta-project>/
├── README.md                     # This file
├── CLAUDE.md                     # Main instructions (auto-load)
├── .env.example                  # Environment variables template
├── .mcp.json                     # Context7 MCP server
│
├── .claude/
│   ├── settings.json             # Permissions and hooks
│   ├── rules/
│   │   └── orchestrator.md       # Autonomous flow (auto-load)
│   ├── agents/                   # 7 agents with YAML frontmatter
│   ├── commands/                 # 6 slash commands
│   ├── skills/                   # 7 skills with SKILL.md
│   └── hooks/                    # Enforcement scripts
│
├── templates/                    # Templates for new projects
├── memory-bank/                  # Techniques and standards
├── docs/                         # Project specifications
│   └── project-spec.md.example   # Specification template
└── projects/                     # Per-project configuration
    └── project-config.md.example # Configuration template
```

## Available Triggers

| Trigger | Action |
|---------|--------|
| `Continue with [PROJECT]` | Continue existing project |
| `Work on [PROJECT]` | Same as above |
| `Create a new project [NAME]` | Create project from scratch |
| (no instruction) | Claude finds active project and continues |

## Agents

| Agent | Model | Function |
|-------|-------|----------|
| best-practices-enforcer | haiku | Verify Python 2026 best practices |
| security-auditor | sonnet | Audit OWASP Top 10, secrets, LLM security |
| code-reviewer | sonnet | Quality and maintainability review |
| test-generator | sonnet | Generate unit tests |
| hallucination-detector | sonnet | Verify code against official docs |
| vulnerability-researcher | sonnet | Research CVEs (NVD, GitHub, EPSS) |
| xai-explainer | sonnet | ML explainability with SHAP/LIME |

## Autonomous Flow

```
Trigger
   │
   ▼
Load CLAUDE.md + orchestrator.md (automatic)
   │
   ▼
Read projects/[project].md
   │
   ▼
Read project specification
   │
   ▼
Detect current state
   │
   ▼
┌─────────────────────────────────┐
│          MAIN LOOP              │
│                                 │
│  Generate code                  │
│       │                         │
│       ▼                         │
│  Verify (agents)                │
│       │                         │
│       ▼                         │
│  Passed? ──No──► Fix ───────┐  │
│       │                      │  │
│      Yes◄────────────────────┘  │
│       │                         │
│       ▼                         │
│  Commit                         │
│       │                         │
│       ▼                         │
│  Next task                      │
│       │                         │
│       ▼                         │
│  Completed? ──No──► LOOP       │
│       │                         │
│      Yes                        │
│       │                         │
└───────┼─────────────────────────┘
        ▼
   Project finished
```

## Applied Best Practices

- **Python 3.11+**: Modern type hints (`list[str]`, `X | None`)
- **Pydantic v2**: `ConfigDict`, `@field_validator`
- **Async HTTP**: `httpx` (not `requests`)
- **Logging**: `structlog` (not `print`)
- **Paths**: `pathlib` (not `os.path`)
- **Package Manager**: `uv` (not `pip`)

## Self-Correcting

Errors are automatically documented in `CLAUDE.md` table "PAST ERRORS → RULES" to prevent repetition.

## Author

`<your-name>` (`<your-github-profile>`)

## License

MIT
