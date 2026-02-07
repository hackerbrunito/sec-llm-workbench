---
name: scan-vulnerabilities
disable-model-invocation: true
description: "Escanear y procesar vulnerabilidades desde un reporte Trivy"
context: fork
argument-hint: "[trivy-json-path]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "WebSearch", "WebFetch"]
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
