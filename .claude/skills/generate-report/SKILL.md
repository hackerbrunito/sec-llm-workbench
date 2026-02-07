---
name: generate-report
description: "Generar reporte de sesion con metricas y trazabilidad"
argument-hint: "[options]"
context: fork
allowed-tools: ["Read", "Write", "Grep", "Glob", "Bash"]
---

# /generate-report

Generar reporte de sesión con métricas de agentes y trazabilidad.

## Uso

```
/generate-report                      # Reporte de sesion actual
/generate-report --date 2026-01-31    # Reporte de fecha especifica
/generate-report --format markdown    # Solo Markdown (default)
/generate-report --format pdf         # PDF con FPDF2
/generate-report --xai                # Incluir explicaciones XAI si hay modelo
```

## Workflow

1. Leer logs de `.build/logs/sessions/` para obtener resumen de sesión
2. Leer logs de `.build/logs/agents/` para métricas de agentes
3. Leer logs de `.build/logs/decisions/` para decisiones tomadas
4. Generar reporte Markdown con métricas y trazabilidad
5. Guardar en `.build/logs/reports/YYYY-MM-DD-<session_id>.md`
6. Opcionalmente compilar a PDF con FPDF2

## Estructura del Reporte

```markdown
# Session Report: <session_id>

## Summary
- Started: <timestamp>
- Agents invoked: <count>
- Decisions logged: <count>
- Commits: <allowed>/<blocked>

## Agent Invocations
| Agent | Files | Status | Duration | Findings |
|-------|-------|--------|----------|----------|
| best-practices-enforcer | 3 | PASSED | 4.5s | 0 |
| security-auditor | 3 | PASSED | 6.2s | 1 |
...

## Decisions Log
| Time | Type | Agent | Outcome | Details |
|------|------|-------|---------|---------|
| 10:30 | finding | security-auditor | flagged | SQL injection risk |
| 10:45 | commit | - | allowed | all_verified |
...

## Findings Summary
- HIGH: <count>
- MEDIUM: <count>
- LOW: <count>

## XAI Explanations (if --xai)
- SHAP global feature importance
- LIME individual explanations
```

## Output

Reportes se guardan en `.build/logs/reports/` (tracked en git).

Ejemplo: `.build/logs/reports/2026-01-31-abc123.md`

## Evidence Triad (para reportes XAI)

Cada vulnerabilidad critica incluye:
1. **Datos** - CVE, CVSS, EPSS, referencias
2. **Clasificacion** - Score del modelo, confidence
3. **Explicacion** - SHAP values + LIME rules
