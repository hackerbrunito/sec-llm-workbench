# Skill: Trivy Integration

Integración con Trivy scanner para ingestión de vulnerabilidades.

---

## Formato de Reporte Trivy

```json
{
  "SchemaVersion": 2,
  "ArtifactName": "myapp:latest",
  "ArtifactType": "container_image",
  "Results": [
    {
      "Target": "python-pkg",
      "Class": "lang-pkgs",
      "Type": "pip",
      "Vulnerabilities": [
        {
          "VulnerabilityID": "CVE-2024-1234",
          "PkgName": "requests",
          "InstalledVersion": "2.28.0",
          "FixedVersion": "2.31.0",
          "Severity": "HIGH",
          "Title": "HTTP Request Smuggling",
          "Description": "...",
          "References": ["https://nvd.nist.gov/..."],
          "CVSS": {
            "nvd": {
              "V3Score": 7.5,
              "V3Vector": "CVSS:3.1/AV:N/AC:L/..."
            }
          }
        }
      ]
    }
  ]
}
```

---

## Parser de Trivy

```python
from dataclasses import dataclass
from pathlib import Path
import json

from src.domain.entities.vulnerability import Vulnerability


@dataclass
class TrivyVulnerability:
    """Raw vulnerability from Trivy report."""

    vulnerability_id: str
    pkg_name: str
    installed_version: str
    fixed_version: str | None
    severity: str
    title: str | None
    description: str | None
    cvss_score: float | None
    cvss_vector: str | None
    references: list[str]


def parse_trivy_report(report_path: Path) -> list[TrivyVulnerability]:
    """Parse Trivy JSON report into domain objects."""

    with report_path.open() as f:
        data = json.load(f)

    vulnerabilities: list[TrivyVulnerability] = []

    for result in data.get("Results", []):
        for vuln in result.get("Vulnerabilities", []):
            # Extract CVSS from nested structure
            cvss = vuln.get("CVSS", {}).get("nvd", {})

            vulnerabilities.append(TrivyVulnerability(
                vulnerability_id=vuln["VulnerabilityID"],
                pkg_name=vuln["PkgName"],
                installed_version=vuln["InstalledVersion"],
                fixed_version=vuln.get("FixedVersion"),
                severity=vuln["Severity"],
                title=vuln.get("Title"),
                description=vuln.get("Description"),
                cvss_score=cvss.get("V3Score"),
                cvss_vector=cvss.get("V3Vector"),
                references=vuln.get("References", []),
            ))

    return vulnerabilities
```

---

## Conversión a Entidades de Dominio

```python
def trivy_to_domain(trivy_vuln: TrivyVulnerability) -> Vulnerability:
    """Convert Trivy vulnerability to domain entity."""

    return Vulnerability(
        cve_id=trivy_vuln.vulnerability_id,
        package_name=trivy_vuln.pkg_name,
        installed_version=trivy_vuln.installed_version,
        fixed_version=trivy_vuln.fixed_version,
        severity=trivy_vuln.severity.upper(),
        description=trivy_vuln.description,
        cvss_v3_score=trivy_vuln.cvss_score,
        cvss_vector=trivy_vuln.cvss_vector,
    )
```

---

## Deduplicación

```python
def deduplicate_vulnerabilities(
    vulnerabilities: list[Vulnerability]
) -> list[Vulnerability]:
    """Remove duplicate CVEs, keeping highest severity."""

    seen: dict[str, Vulnerability] = {}
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}

    for vuln in vulnerabilities:
        if vuln.cve_id in seen:
            existing = seen[vuln.cve_id]
            if severity_order.get(vuln.severity, 0) > severity_order.get(existing.severity, 0):
                seen[vuln.cve_id] = vuln
        else:
            seen[vuln.cve_id] = vuln

    return list(seen.values())
```

---

## Use Case Completo

```python
# src/application/use_cases/ingest_trivy.py
from dataclasses import dataclass
from pathlib import Path

import structlog

from src.domain.entities.vulnerability import Vulnerability

logger = structlog.get_logger(__name__)


@dataclass
class IngestTrivyResult:
    """Result of Trivy ingestion."""

    total_parsed: int
    deduplicated: int
    valid: int
    errors: list[str]


class IngestTrivyUseCase:
    """Parse and ingest vulnerabilities from Trivy JSON reports."""

    async def execute(self, report_path: Path) -> IngestTrivyResult:
        """Execute the ingestion use case."""

        errors: list[str] = []

        # Parse
        logger.info("parsing_trivy_report", path=str(report_path))
        raw_vulns = parse_trivy_report(report_path)
        total_parsed = len(raw_vulns)

        # Convert
        domain_vulns = [trivy_to_domain(v) for v in raw_vulns]

        # Deduplicate
        deduped = deduplicate_vulnerabilities(domain_vulns)
        deduplicated = len(deduped)

        # Validate
        valid_vulns = [v for v in deduped if v.cve_id.startswith("CVE-")]
        valid = len(valid_vulns)

        logger.info(
            "trivy_ingestion_complete",
            total=total_parsed,
            deduplicated=deduplicated,
            valid=valid,
        )

        return IngestTrivyResult(
            total_parsed=total_parsed,
            deduplicated=deduplicated,
            valid=valid,
            errors=errors,
        )
```

---

## Ejecutar Trivy (CLI)

```bash
# Escanear imagen Docker
trivy image myapp:latest -f json -o trivy-report.json

# Escanear filesystem
trivy fs . -f json -o trivy-report.json

# Escanear con severidad mínima
trivy image myapp:latest --severity HIGH,CRITICAL -f json -o trivy-report.json
```

---

## Testing

```python
@pytest.fixture
def sample_trivy_report(tmp_path: Path) -> Path:
    report = {
        "SchemaVersion": 2,
        "Results": [{
            "Vulnerabilities": [{
                "VulnerabilityID": "CVE-2024-1234",
                "PkgName": "requests",
                "InstalledVersion": "2.28.0",
                "Severity": "HIGH",
            }]
        }]
    }
    path = tmp_path / "trivy.json"
    path.write_text(json.dumps(report))
    return path


@pytest.mark.asyncio
async def test_ingest_trivy(sample_trivy_report: Path):
    use_case = IngestTrivyUseCase()
    result = await use_case.execute(sample_trivy_report)

    assert result.total_parsed == 1
    assert result.valid == 1
```
