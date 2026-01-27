---
name: generate-report
description: "Generar reporte de auditoria en PDF con explicabilidad XAI"
argument-hint: "[options]"
disable-model-invocation: true
---

# /generate-report

Generar reporte de auditoria con explicaciones XAI (SHAP/LIME).

## Uso

```
/generate-report                      # Reporte completo
/generate-report --format pdf         # Solo PDF
/generate-report --format markdown    # Solo Markdown
/generate-report --top 10             # Top 10 vulnerabilidades
/generate-report --cve CVE-2024-1234  # CVE especifico
```

## Workflow

1. Cargar datos de vulnerabilidades procesadas
2. Cargar clasificaciones del modelo
3. Generar explicaciones XAI (SHAP/LIME)
4. Crear visualizaciones
5. Compilar PDF con FPDF2
6. Guardar en output/

## Estructura del Reporte

- Executive Summary
- Methodology
- Findings (Critical, High)
- XAI Explanations (SHAP global, LIME individual)
- Recommendations
- Appendix: Raw Data

## Evidence Triad

Cada vulnerabilidad critica incluye:
1. **Datos** - CVE, CVSS, EPSS, referencias
2. **Clasificacion** - Score del modelo, confidence
3. **Explicacion** - SHAP values + LIME rules
