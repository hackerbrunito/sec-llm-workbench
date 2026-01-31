# Sistema de Trazabilidad

Sistema de logging y reportes para el framework Vibe Coding 2026.

## Arquitectura

```
.build/logs/
├── agents/       # JSONL - invocaciones de agentes (gitignored)
├── sessions/     # JSON - resúmenes de sesión (gitignored)
├── decisions/    # JSONL - decisiones tomadas (gitignored)
└── reports/      # MD - reportes generados (TRACKED en git)
```

## Formato de Logs

### Agent Log (`agents/YYYY-MM-DD.jsonl`)

Registra cada invocación de agente durante `/verify`:

```json
{
  "id": "uuid",
  "timestamp": "2026-01-31T10:30:15Z",
  "session_id": "abc123",
  "agent": "best-practices-enforcer",
  "files": ["src/main.py", "src/utils.py"],
  "status": "PASSED",
  "findings": [],
  "duration_ms": 4500
}
```

Campos:
- `id`: UUID único de la invocación
- `timestamp`: ISO8601 UTC
- `session_id`: ID de sesión de Claude Code
- `agent`: Nombre del agente ejecutado
- `files`: Lista de archivos analizados
- `status`: `PASSED` o `FAILED`
- `findings`: Array de hallazgos (vacío si PASSED)
- `duration_ms`: Duración en milisegundos

### Decision Log (`decisions/YYYY-MM-DD.jsonl`)

Registra decisiones tomadas (cambios de código, findings, commits):

```json
{
  "id": "uuid",
  "timestamp": "2026-01-31T10:30:22Z",
  "session_id": "abc123",
  "type": "finding",
  "agent": "security-auditor",
  "severity": "HIGH",
  "finding": "SQL injection in execute()",
  "file": "src/db.py",
  "outcome": "flagged"
}
```

Tipos de decisión:
- `code_change`: Archivo escrito/editado (via post-code.sh)
- `finding`: Hallazgo de agente (via /verify)
- `commit`: Commit permitido/bloqueado (via pre-git-commit.sh)

### Session Summary (`sessions/YYYY-MM-DD-<session_id>.json`)

Resumen de sesión inicializado al arrancar:

```json
{
  "session_id": "abc123",
  "started_at": "2026-01-31T10:00:00Z",
  "project_dir": "/path/to/project",
  "agents_invoked": 15,
  "decisions": 5,
  "commits": 2
}
```

## Skills Relacionadas

### `/show-trace`

Mostrar últimas entradas de logs en consola:

```
/show-trace                     # Últimas 10 entradas
/show-trace -n 20               # Últimas 20 entradas
/show-trace --agents            # Solo logs de agentes
/show-trace --decisions         # Solo decisiones
/show-trace --date 2026-01-31   # Fecha específica
/show-trace --agent security-auditor  # Filtrar por agente
```

### `/generate-report`

Generar reporte completo en Markdown:

```
/generate-report                      # Sesión actual
/generate-report --date 2026-01-31    # Fecha específica
/generate-report --format pdf         # Exportar a PDF
```

Los reportes se guardan en `.build/logs/reports/` y están tracked en git.

## Hooks que Generan Logs

| Hook | Evento | Log |
|------|--------|-----|
| `session-start.sh` | Inicio de sesión | `sessions/` |
| `post-code.sh` | Write/Edit archivo | `decisions/` |
| `pre-git-commit.sh` | git commit | `decisions/` |
| `/verify` (skill) | Ejecución de agentes | `agents/` + `decisions/` |

## Retención

- Logs locales (`agents/`, `sessions/`, `decisions/`): gitignored, efímeros
- Reportes (`reports/`): tracked en git, persistentes

Para limpiar logs antiguos:
```bash
find .build/logs/agents -mtime +30 -delete
find .build/logs/decisions -mtime +30 -delete
find .build/logs/sessions -mtime +30 -delete
```
