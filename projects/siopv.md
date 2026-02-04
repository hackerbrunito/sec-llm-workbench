# SIOPV - Configuration

> **Path:** `~/siopv/`
> **Type:** Sistema de Orquestación (CLI + API + Dashboard)
> **Deadline:** 1 de marzo de 2026

---

## Specification

**REQUIRED:** Before working on this project, read the specification:

```
docs/SIOPV_Propuesta_Tecnica_v2.txt
```

---

## Description

Sistema Inteligente de Orquestación y Priorización de Vulnerabilidades para pipelines CI/CD.
Implementa un pipeline híbrido ML + GenAI con 8 fases: Ingesta → RAG (CRAG) → ML Classification →
Orchestration (LangGraph) → Authorization (OpenFGA) → Privacy (DLP) → Human-in-the-Loop → Output.

---

## Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| uv | latest | Package manager |
| LangGraph | >=0.2.0 | AI orchestration |
| Claude | Haiku 4.5 + Sonnet 4.5 | LLM reasoning |
| XGBoost | >=2.0.0 | ML classification |
| SHAP/LIME | latest | Explainability (XAI) |
| ChromaDB | >=0.5.0 | Vector database (RAG) |
| Presidio | >=2.2.0 | DLP sanitization |
| OpenFGA | latest | Fine-grained authorization |
| Streamlit | >=1.40.0 | Dashboard |
| PostgreSQL | 16 | Database (checkpointing) |

---

## Progress

### Phase 0: Setup ✅

| Task | Status | Notes |
|------|--------|-------|
| Project structure (hexagonal) | ✅ Completado | src/siopv/{domain,application,adapters,infrastructure,interfaces} |
| pyproject.toml with dependencies | ✅ Completado | 214 packages resolved, uv.lock generated |
| Base files (exceptions, settings, logging) | ✅ Completado | Pydantic v2 + structlog (Context7 verified) |
| CLI skeleton (Typer) | ✅ Completado | `siopv --help` working |
| Git + uv initialization | ✅ Completado | main branch, .gitignore, .env.example |
| Unit tests | ✅ Completado | 87 tests, 76% coverage |
| 5-agent verification | ✅ Completado | best-practices, security, hallucination, code-review, test-gen |

### Phase 1: Ingesta y Preprocesamiento ✅

| Task | Status | Notes |
|------|--------|-------|
| VulnerabilityRecord entity (Pydantic v2) | ✅ Completado | CVEId, CVSSScore, PackageVersion, LayerInfo value objects + VulnerabilityRecord entity |
| Trivy JSON parser | ✅ Completado | TrivyParser class, schema v2, Results[].Vulnerabilities[] |
| Map-Reduce deduplication | ✅ Completado | deduplicate_vulnerabilities() by (cve_id, package, version) |
| Batch processing by package | ✅ Completado | group_by_package(), sort_by_severity(), IngestTrivyReportUseCase |
| Unit tests | ✅ Completado | 80 new tests, 99.4% coverage en Fase 1 |
| 5-agent verification | ✅ Completado | best-practices ✓, security ✓, hallucination ✓, code-review 8/10, test-gen ✓ |

### Phase 2: Enriquecimiento (Dynamic RAG) ✅

| Task | Status | Notes |
|------|--------|-------|
| NVD API client (httpx) | ✅ Completado | Rate limiter + circuit breaker + tenacity retry |
| GitHub Security Advisories client | ✅ Completado | GraphQL API, ecosystem mapping, CVE/package lookup |
| EPSS API client | ✅ Completado | Exploit prediction scores, batch queries |
| Tavily Search API client | ✅ Completado | OSINT fallback when relevance < 0.6 |
| ChromaDB adapter | ✅ Completado | PersistentClient + LRU cache (1000 entries) |
| CRAG pattern implementation | ✅ Completado | EnrichContextUseCase, relevance threshold 0.6 |
| Resilience infrastructure | ✅ Completado | CircuitBreaker (CLOSED/OPEN/HALF_OPEN) + TokenBucket RateLimiter |
| Unit tests | ✅ Completado | 63 new tests, 230 total, 62% coverage |
| 5-agent verification | ✅ Completado | best-practices ✓, security ✓, hallucination ✓, code-review 8.5/10, test-gen ✓ |

### Phase 3: Clasificación ML ✅

| Task | Status | Notes |
|------|--------|-------|
| Dataset construction (CISA KEV) | ✅ Completado | CISAKEVLoader with schema validation, path traversal protection |
| Feature engineering | ✅ Completado | FeatureEngineer: 14 features (CVSS metrics + EPSS + temporal + context) |
| XGBoost training + Optuna | ✅ Completado | XGBoostClassifier with Optuna hyperparameter optimization |
| SMOTE balancing | ✅ Completado | SMOTE integration for class imbalance handling |
| SHAP global explanation | ✅ Completado | SHAPExplainer: TreeExplainer + feature importance |
| LIME local explanation | ✅ Completado | LIMEExplainer: per-prediction explanations with configurable seeds |
| Model persistence | ✅ Completado | ModelPersistence: SHA-256 + HMAC integrity, path traversal protection |
| Unit tests | ✅ Completado | 635 tests total, 74% coverage, security tests included |
| 5-agent verification | ✅ Completado | best-practices ✓, security ✓, hallucination ✓, code-review ✓, test-gen ✓ |

### Phase 4: Orquestación (LangGraph) ✅

| Task | Status | Notes |
|------|--------|-------|
| State schema (TypedDict) | ✅ Completado | PipelineState TypedDict (LangGraph requirement, not Pydantic) |
| Nodes: ingest, enrich, classify, escalate | ✅ Completado | 4 pure functions delegating to use cases |
| Uncertainty Trigger (adaptive threshold) | ✅ Completado | Percentile-90 historical discrepancy, ML vs LLM |
| Checkpointing (SQLite) | ✅ Completado | SqliteSaver with path validation + extension whitelist |
| Graph compilation (PipelineGraphBuilder) | ✅ Completado | StateGraph + conditional edges + builder pattern |
| Unit tests | ✅ Completado | 714 tests total, 76% coverage |
| 5-agent verification | ✅ Completado | best-practices ✓, security ✓, hallucination ✓, code-review 8.2/10, test-gen ✓ |

### Phase 5: Autorización (OpenFGA) ⏳

| Task | Status | Notes |
|------|--------|-------|
| ReBAC model definition | ⏳ Pendiente | Define relations (user, project, vuln) |
| OpenFGA adapter | ⏳ Pendiente | Check permissions |
| Authorization gatekeeper node | ⏳ Pendiente | Integrate in LangGraph |
| Unit tests | ⏳ Pendiente | Mock OpenFGA |

### Phase 6: Privacidad (DLP) ⏳

| Task | Status | Notes |
|------|--------|-------|
| Presidio analyzer setup | ⏳ Pendiente | Detect PII/secrets |
| Presidio anonymizer setup | ⏳ Pendiente | Redact sensitive data |
| Claude Haiku semantic validator | ⏳ Pendiente | Contextual sanitization |
| DLP guardrail node | ⏳ Pendiente | Dual-layer sanitization |
| Unit tests | ⏳ Pendiente | Test detection + redaction |

### Phase 7: Human-in-the-Loop ⏳

| Task | Status | Notes |
|------|--------|-------|
| Streamlit dashboard | ⏳ Pendiente | Display escalated cases |
| Tríada de evidencia UI | ⏳ Pendiente | Summary + LIME plot + CoT log |
| Polling mechanism (SQLite) | ⏳ Pendiente | Detect escalated cases |
| Timeout escalation logic | ⏳ Pendiente | 4h → 8h → 24h auto-approval |
| Unit tests | ⏳ Pendiente | Mock dashboard interactions |

### Phase 8: Output (Acción y Auditoría) ⏳

| Task | Status | Notes |
|------|--------|-------|
| Jira adapter | ⏳ Pendiente | Create enriched tickets |
| PDF report generator (FPDF2) | ⏳ Pendiente | Audit trail PDF |
| Ticket enrichment (CVSS, EPSS, confidence) | ⏳ Pendiente | Custom Jira fields |
| Output action node | ⏳ Pendiente | Final pipeline step |
| Unit tests | ⏳ Pendiente | Mock Jira API |

---

## Commands

```bash
# Setup
cd ~/siopv
uv sync
cp .env.example .env

# Run CLI
uv run siopv --help
uv run siopv process-report trivy-report.json
uv run siopv dashboard

# Tests
uv run pytest tests/ -v --cov=src

# Linting
uv run ruff check src tests
uv run ruff format src tests

# Type checking
uv run mypy src
```

---

## Timeline

| Week | Dates | Phase | Deliverables |
|------|-------|-------|--------------|
| 1 | 26 ene - 1 feb | Phase 1 | Ingestion engine + tests |
| 2 | 2-8 feb | Phase 2 | RAG (CRAG) + APIs integration |
| 3 | 9-15 feb | Phase 3 | ML model + SHAP/LIME |
| 4 | 16-22 feb | Phase 4 | LangGraph orchestration |
| 5 | 23 feb - 1 mar | Phases 5-6 | OpenFGA + DLP |
| 6 | 2-8 mar | Phases 7-8 | Dashboard + Output |

**Current Status:** Phase 4 (LangGraph Orchestration) completado. Ready for Phase 5 (OpenFGA Authorization).

---

## Notes

- Este archivo queda en el META-PROYECTO, NO en ~/siopv/
- El proyecto generado debe permanecer limpio y exportable
- Actualizar progreso conforme se completan fases
- Consultar Context7 ANTES de usar bibliotecas externas
- Ejecutar agentes de verificación después de cada implementación
