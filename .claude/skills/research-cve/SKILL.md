---
name: research-cve
description: "Investigar un CVE especifico usando multiples fuentes OSINT"
disable-model-invocation: true
---

# /research-cve

Investigar un CVE usando fuentes OSINT.

## Uso

```
/research-cve CVE-2024-1234
/research-cve CVE-2024-1234 --deep        # Investigacion profunda
/research-cve CVE-2024-1234 --exploit     # Buscar exploits/POCs
```

## Workflow

1. Validar formato CVE-YYYY-NNNNN
2. Consultar NVD API v2.0
3. Consultar GitHub Security Advisories
4. Consultar EPSS Score
5. Buscar exploits (Exploit-DB, PacketStorm)
6. Compilar informe

## Fuentes

| Fuente | Datos |
|--------|-------|
| NVD | CVSS, descripcion, referencias, CWE |
| GitHub | Advisory, affected packages, patches |
| EPSS | Probabilidad de explotacion (30 dias) |
| CISA KEV | Si esta en catalogo de explotados |

## Agente

Invoca internamente al agente `vulnerability-researcher`.
