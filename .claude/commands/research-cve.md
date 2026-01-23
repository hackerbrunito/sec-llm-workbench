# /research-cve

Investigar un CVE específico usando múltiples fuentes OSINT.

---

## Uso

```bash
/research-cve CVE-2024-1234
/research-cve CVE-2024-1234 --deep        # Investigación profunda
/research-cve CVE-2024-1234 --exploit     # Buscar exploits/POCs
```

---

## Workflow

```
1. Validar formato CVE-YYYY-NNNNN
2. Consultar NVD API v2.0
3. Consultar GitHub Security Advisories
4. Consultar EPSS Score
5. Buscar exploits (Tavily → Exploit-DB, PacketStorm)
6. Compilar informe de investigación
```

---

## Fuentes Consultadas

| Fuente | Datos Obtenidos |
|--------|-----------------|
| NVD | CVSS, descripción, referencias, CWE |
| GitHub | Advisory, affected packages, patches |
| EPSS | Probabilidad de explotación (30 días) |
| CISA KEV | Si está en catálogo de explotados |
| Tavily | POCs, exploits, artículos técnicos |

---

## Ejemplo de Output

```
🔍 RESEARCHING: CVE-2024-1234

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 SCORES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CVSS v3.1:  9.8 CRITICAL
Vector:     CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
EPSS:       0.847 (Percentile: 98.2%)
KEV:        ⚠️  YES - Added 2024-01-15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 AFFECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Package:    openssl
Ecosystem:  pip
Vulnerable: < 3.0.12
Fixed:      3.0.12

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 DESCRIPTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
A buffer overflow vulnerability in OpenSSL allows
remote attackers to execute arbitrary code via...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💀 EXPLOITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[!] POC AVAILABLE
- Exploit-DB: https://exploit-db.com/exploits/12345
- GitHub POC: https://github.com/user/CVE-2024-1234

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 RECOMMENDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️  IMMEDIATE PATCHING REQUIRED
- High EPSS + Active exploitation + POC available
- Upgrade to openssl >= 3.0.12
- Apply vendor patches immediately

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 REFERENCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- NVD: https://nvd.nist.gov/vuln/detail/CVE-2024-1234
- GitHub: https://github.com/advisories/GHSA-xxxx-yyyy
- Vendor: https://openssl.org/news/secadv/...
```

---

## Integración con Agente

Este comando invoca internamente al agente `vulnerability-researcher`:

```
/research-cve CVE-2024-1234
        ↓
[spawn vulnerability-researcher]
        ↓
[Compilar resultados]
        ↓
[Mostrar informe]
```
