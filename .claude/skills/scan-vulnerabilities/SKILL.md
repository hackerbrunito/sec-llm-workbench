---
name: scan-vulnerabilities
description: "Escanear y procesar vulnerabilidades desde un reporte Trivy"
disable-model-invocation: true
argument-hint: "[trivy-json-path]"
---

# /scan-vulnerabilities

Escanear y procesar vulnerabilidades desde un reporte Trivy JSON.

## Uso

```
/scan-vulnerabilities [path-to-trivy-json]
```

## Workflow

1. Leer reporte Trivy JSON
2. Parsear vulnerabilidades (CVE, severity, package, version)
3. Deduplicar por CVE ID
4. Validar formato de datos
5. Mostrar resumen
6. Preguntar si continuar con enriquecimiento

## Pipeline

```
/scan-vulnerabilities → [Ingestion] → [RAG] → [Classify] → [Orchestrate]
```
