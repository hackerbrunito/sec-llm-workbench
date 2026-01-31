---
name: show-trace
description: "Mostrar ultimas entradas de logs de trazabilidad"
argument-hint: "[options]"
disable-model-invocation: true
---

# /show-trace

Mostrar últimas entradas de logs del sistema de trazabilidad.

## Uso

```
/show-trace                     # Ultimas 10 entradas de todos los logs
/show-trace -n 20               # Ultimas 20 entradas
/show-trace --agents            # Solo logs de agentes
/show-trace --decisions         # Solo logs de decisiones
/show-trace --sessions          # Solo resúmenes de sesión
/show-trace --date 2026-01-31   # Logs de fecha especifica
/show-trace --agent security-auditor  # Filtrar por agente específico
```

## Comportamiento

### 1. Leer Logs

Leer archivos JSONL de:
- `.build/logs/agents/YYYY-MM-DD.jsonl`
- `.build/logs/decisions/YYYY-MM-DD.jsonl`
- `.build/logs/sessions/YYYY-MM-DD-*.json`

### 2. Formato de Salida (consola)

```
=== Trace Log (last 10 entries) ===

[10:30:15] AGENT best-practices-enforcer
           Files: src/main.py, src/utils.py
           Status: PASSED (4.5s)

[10:30:22] AGENT security-auditor
           Files: src/main.py, src/utils.py
           Status: FAILED (6.2s)
           Findings: 1 HIGH

[10:30:22] DECISION finding
           Agent: security-auditor
           Severity: HIGH
           Finding: SQL injection in execute()
           Outcome: flagged

[10:45:00] DECISION commit
           Outcome: blocked
           Reason: pending_verification:2

[11:00:00] DECISION commit
           Outcome: allowed
           Reason: all_verified

=== End of Trace ===
```

### 3. Filtros

- `--agents`: Solo mostrar entradas de `.build/logs/agents/`
- `--decisions`: Solo mostrar entradas de `.build/logs/decisions/`
- `--sessions`: Solo mostrar resúmenes de `.build/logs/sessions/`
- `--date YYYY-MM-DD`: Filtrar por fecha
- `--agent <name>`: Filtrar por nombre de agente
- `-n <count>`: Número de entradas a mostrar (default: 10)

## Ubicación de Logs

```
.build/logs/
├── agents/       # JSONL - invocaciones de agentes
├── sessions/     # JSON - resúmenes de sesión
├── decisions/    # JSONL - decisiones tomadas
└── reports/      # MD - reportes generados
```

## Ver También

- `/generate-report` - Generar reporte completo en Markdown/PDF
- `/verify` - Ejecutar agentes de verificación
