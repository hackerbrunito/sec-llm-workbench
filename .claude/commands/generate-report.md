# /generate-report

Generar reporte de auditoría en PDF con explicabilidad XAI.

---

## Uso

```bash
/generate-report                      # Reporte completo
/generate-report --format pdf         # Solo PDF
/generate-report --format markdown    # Solo Markdown
/generate-report --top 10             # Top 10 vulnerabilidades
/generate-report --cve CVE-2024-1234  # Reporte de CVE específico
```

---

## Workflow

```
1. Cargar datos de vulnerabilidades procesadas
2. Cargar clasificaciones del modelo
3. Generar explicaciones XAI (SHAP/LIME)
4. Crear visualizaciones
5. Compilar PDF con FPDF2
6. Guardar en output/
```

---

## Estructura del Reporte

```markdown
# Vulnerability Audit Report
## Executive Summary
## Methodology
## Findings
### Critical Vulnerabilities
### High Vulnerabilities
### Risk Distribution
## XAI Explanations
### Global Feature Importance (SHAP)
### Individual Explanations (LIME)
## Recommendations
## Appendix: Raw Data
```

---

## Ejemplo de Output

```
📄 GENERATING AUDIT REPORT

Processing:
├── Loading 47 vulnerabilities...
├── Loading classifications...
├── Generating SHAP summary...
├── Generating LIME explanations (top 10)...
├── Creating visualizations...
└── Compiling PDF...

✅ Report generated successfully!

Output files:
├── output/audit-report-2026-01-21.pdf (2.3 MB)
├── output/audit-report-2026-01-21.md
├── output/figures/shap_summary.png
├── output/figures/risk_distribution.png
└── output/figures/lime_explanations/
    ├── CVE-2024-1234.html
    ├── CVE-2024-5678.html
    └── ...
```

---

## Código de Referencia

```python
# src/interfaces/cli/main.py
@app.command()
def report(
    output: Path = typer.Option(Path("./output"), help="Output directory"),
    format: str = typer.Option("pdf", help="Output format: pdf, markdown, both"),
    top: int = typer.Option(10, help="Number of top vulnerabilities to detail"),
) -> None:
    """Generate audit report with XAI explanations."""
    # Implementación en Fase 8
```

---

## Dependencias

```python
# Para generación de PDF
from fpdf import FPDF

# Para visualizaciones
import matplotlib.pyplot as plt
import shap

# Para HTML interactivo
from lime.lime_tabular import LimeTabularExplainer
```

---

## Tríada de Evidencia (Requisito TFM)

Cada vulnerabilidad crítica incluye:
1. **Datos** - CVE, CVSS, EPSS, referencias
2. **Clasificación** - Score del modelo, confidence
3. **Explicación** - SHAP values + LIME rules
