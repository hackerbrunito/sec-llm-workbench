---
name: verify
description: "Ejecuta los 5 agentes mandatorios de verificacion y limpia markers pendientes"
disable-model-invocation: true
context: fork
agent: general-purpose
argument-hint: "[--fix]"
---

# /verify

Ejecuta agentes de verificacion y limpia markers de archivos pendientes.

## Uso

```
/verify
/verify --fix
```

## Current State
- Pending files: !`ls .build/checkpoints/pending/ 2>/dev/null || echo "none"`
- Last verification: !`ls -t .build/logs/agents/ 2>/dev/null | head -1 || echo "none"`

## Comportamiento

### 1. Identificar Archivos Pendientes

```bash
ls $CLAUDE_PROJECT_DIR/.build/checkpoints/pending/ 2>/dev/null
```

Si no hay archivos pendientes: "No hay archivos pendientes de verificacion"

### 2. Ejecutar Agentes (OBLIGATORIO, EN ORDEN)

TODOS deben ejecutarse. Si uno falla, PARAR y reportar.

Para CADA agente, registrar en `.build/logs/agents/YYYY-MM-DD.jsonl`:

```
Task(subagent_type="best-practices-enforcer", prompt="Verifica archivos Python pendientes: type hints, Pydantic v2, httpx, structlog, pathlib")
Task(subagent_type="security-auditor", prompt="Audita seguridad: OWASP Top 10, secrets, injection, LLM security")
Task(subagent_type="hallucination-detector", prompt="Verifica sintaxis de bibliotecas externas contra Context7")
Task(subagent_type="code-reviewer", prompt="Review calidad: complejidad, DRY, naming, mantenibilidad")
Task(subagent_type="test-generator", prompt="Genera tests unitarios para modulos sin cobertura")
```

### 3. Logging de Agentes (OBLIGATORIO)

Después de ejecutar CADA agente, añadir entrada JSONL a `.build/logs/agents/YYYY-MM-DD.jsonl`:

```json
{
  "id": "<uuid>",
  "timestamp": "<ISO8601>",
  "session_id": "<session_id>",
  "agent": "<agent_name>",
  "files": ["<archivo1>", "<archivo2>"],
  "status": "PASSED|FAILED",
  "findings": [],
  "duration_ms": <milliseconds>
}
```

Si el agente encuentra hallazgos, también registrar en `.build/logs/decisions/YYYY-MM-DD.jsonl`:

```json
{
  "id": "<uuid>",
  "timestamp": "<ISO8601>",
  "session_id": "<session_id>",
  "agent": "<agent_name>",
  "type": "finding",
  "severity": "HIGH|MEDIUM|LOW",
  "finding": "<descripcion>",
  "file": "<archivo>",
  "outcome": "flagged|fixed"
}
```

### 4. Si TODOS Pasan, Limpiar Markers

```bash
rm -rf $CLAUDE_PROJECT_DIR/.build/checkpoints/pending/*
```

### 5. Verificaciones Adicionales

```bash
uv run ruff format src tests --check
uv run ruff check src tests
uv run mypy src
uv run pytest tests/ -v
```

### Con --fix

```bash
uv run ruff format src tests
uv run ruff check src tests --fix
```

## Sistema de Markers

- `post-code.sh` crea markers en `.build/checkpoints/pending/` despues de Write/Edit en .py
- `pre-git-commit.sh` bloquea commit si hay markers pendientes
- `/verify` ejecuta agentes y limpia markers si todo pasa

## Sistema de Trazabilidad

- Logs de agentes: `.build/logs/agents/YYYY-MM-DD.jsonl`
- Logs de decisiones: `.build/logs/decisions/YYYY-MM-DD.jsonl`
- Ver `/show-trace` para consultar logs
- Ver `/generate-report` para generar reportes
