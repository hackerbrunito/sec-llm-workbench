# /scan-vulnerabilities

Escanear y procesar vulnerabilidades desde un reporte Trivy.

---

## Uso

```bash
/scan-vulnerabilities [path-to-trivy-json]
/scan-vulnerabilities data/samples/trivy-report.json
```

---

## Workflow

```
1. Leer reporte Trivy JSON
2. Parsear vulnerabilidades (CVE, severity, package, version)
3. Deduplicar por CVE ID
4. Validar formato de datos
5. Mostrar resumen
6. Preguntar si continuar con enriquecimiento
```

---

## Ejemplo de Output

```
📊 SCAN RESULTS: trivy-report.json

Found: 47 vulnerabilities
├── CRITICAL: 3
├── HIGH: 12
├── MEDIUM: 18
└── LOW: 14

Top Critical:
1. CVE-2024-1234 - openssl 3.0.1 → 3.0.12
2. CVE-2024-5678 - requests 2.28.0 → 2.31.0
3. CVE-2024-9012 - numpy 1.24.0 → 1.26.0

¿Continuar con enriquecimiento RAG? [y/N]
```

---

## Código de Referencia

```python
# src/interfaces/cli/main.py
@app.command()
def scan(
    input_file: Path = typer.Argument(..., help="Path to Trivy JSON report"),
    output_dir: Path = typer.Option(Path("."), help="Output directory"),
) -> None:
    """Ingest and process a Trivy vulnerability scan."""
    # Implementación en Fase 1
```

---

## Integración con Pipeline

```
/scan-vulnerabilities
        ↓
[Fase 1: Ingestion] → Parsear Trivy JSON
        ↓
[Fase 2: RAG] → Enriquecer con NVD, GitHub, EPSS
        ↓
[Fase 3: Classify] → XGBoost + XAI
        ↓
[Fase 4: Orchestrate] → LangGraph pipeline
```
