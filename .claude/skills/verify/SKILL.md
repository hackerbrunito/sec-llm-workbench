---
name: verify
disable-model-invocation: true
description: "Ejecuta los 5 agentes mandatorios de verificacion y limpia markers pendientes"
context: fork
agent: general-purpose
argument-hint: "[--fix]"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Task"]
---

# /verify

Ejecuta agentes de verificacion y limpia markers de archivos pendientes.

## Uso

```
/verify                    # Synchronous verification (immediate)
/verify --fix              # Auto-fix issues
/verify --batch            # Batch API mode (50% cost savings, 24h latency)
/verify --batch --wave 1   # Submit Wave 1 only
/verify --batch --wave 2   # Submit Wave 2 only
```

### Batch Mode (50% Cost Savings) - ⚠️ EXPERIMENTAL

Uses Anthropic Batch API for non-interactive verification:
- **Cost:** 50% discount vs. synchronous API
- **Latency:** Up to 24 hours (most batches < 1 hour)
- **Ideal for:** Non-urgent verification, large codebases
- **Status:** Experimental feature, not integrated in production workflow
- **Script:** `.ignorar/experimental-scripts/batch-api-verification/submit-batch-verification.py`

**Workflow:**
1. Submit batch: `python .ignorar/experimental-scripts/batch-api-verification/submit-batch-verification.py submit --wave 1`
2. Poll status: `python .ignorar/experimental-scripts/batch-api-verification/submit-batch-verification.py poll BATCH_ID`
3. Download results: `python .ignorar/experimental-scripts/batch-api-verification/submit-batch-verification.py results BATCH_ID`

## Current State
- Pending files: !`ls .build/checkpoints/pending/ 2>/dev/null || echo "none"`
- Last verification: !`ls -t .build/logs/agents/ 2>/dev/null | head -1 || echo "none"`

## Comportamiento

### 1. Identificar Archivos Pendientes

```bash
ls $CLAUDE_PROJECT_DIR/.build/checkpoints/pending/ 2>/dev/null
```

Si no hay archivos pendientes: "No hay archivos pendientes de verificacion"

### 2. Ejecutar Agentes (WAVE-BASED PARALLEL)

TODOS deben ejecutarse en paralelo (2 waves). Si alguno falla, PARAR y reportar.

**Orchestration Reference:** `.claude/scripts/orchestrate-parallel-verification.py`
- Wave-based parallel execution (Wave 1: 3 agents ~7 min, Wave 2: 2 agents ~5 min)
- Threshold validation per `.claude/rules/verification-thresholds.md`
- JSONL logging to `.build/logs/agents/YYYY-MM-DD.jsonl`
- Automated pending marker cleanup on success

#### Wave 1 (Paralelo - ~7 min max)

Submit 3 agents in parallel with few-shot examples:

**best-practices-enforcer:**
```
Task(subagent_type="best-practices-enforcer", prompt="""Verifica archivos Python pendientes: type hints, Pydantic v2, httpx, structlog, pathlib

EXPECTED OUTPUT STRUCTURE:

## Findings

### 1. Missing Type Hints on Function
- **File:** src/handlers/input.py:42
- **Severity:** MEDIUM
- **Pattern:** Function lacks type hints
- **Current:** def process_user_input(data):
- **Expected:** def process_user_input(data: dict[str, Any]) -> ProcessResult:
- **Fix:** Add modern type hints (dict[str, ...] not typing.Dict)

### 2. Pydantic v1 Pattern Detected
- **File:** src/models/config.py:15
- **Severity:** MEDIUM
- **Pattern:** Using 'class Config' instead of ConfigDict
- **Fix:** Use ConfigDict(validate_assignment=True) pattern

## Summary
- Total violations: N
- CRITICAL: 0
- MEDIUM: N
- LOW: N

---

Now audit pending Python files following this exact structure.""")
```

**security-auditor:**
```
Task(subagent_type="security-auditor", prompt="""Audita seguridad: OWASP Top 10, secrets, injection, LLM security

EXPECTED OUTPUT STRUCTURE:

## Security Findings

### 1. SQL Injection Vulnerability
- **File:** src/db/queries.py:34
- **CWE:** CWE-89 (SQL Injection)
- **Severity:** CRITICAL
- **Description:** User input directly interpolated without parameterization
- **Attack Vector:** Attacker injects SQL via user_email parameter
- **Fix:** Use parameterized queries
- **OWASP:** A03:2021 – Injection

### 2. Hardcoded API Key
- **File:** src/config/credentials.py:12
- **Severity:** CRITICAL
- **Description:** API key hardcoded in source code
- **Fix:** Load from environment using os.getenv()
- **OWASP:** A02:2021 – Cryptographic Failures

## Summary
- Total findings: N
- CRITICAL: N (requires immediate fix)
- HIGH: N
- MEDIUM: N

---

Now audit pending files following this exact structure. Prioritize CRITICAL/HIGH severity.""")
```

**hallucination-detector:**
```
Task(subagent_type="hallucination-detector", prompt="""Verifica sintaxis de bibliotecas externas contra Context7

EXPECTED OUTPUT STRUCTURE:

## Hallucination Check Results

### ✅ VERIFIED USAGE

#### 1. httpx AsyncClient
- **Library:** httpx
- **Pattern:** httpx.AsyncClient(timeout=30.0)
- **File:** src/api/client.py:15
- **Context7 Status:** VERIFIED (v0.24.1 docs)

#### 2. Pydantic ConfigDict
- **Library:** pydantic
- **Pattern:** model_config = ConfigDict(validate_assignment=True)
- **File:** src/models/user.py:8
- **Context7 Status:** VERIFIED (Pydantic v2)

### ⚠️ HALLUCINATED USAGE

#### 1. structlog wrap_logger with wrapper_class
- **Library:** structlog
- **Pattern:** structlog.wrap_logger(logger, wrapper_class=...)
- **File:** src/logging/config.py:22
- **Status:** UNVERIFIED - Not in docs
- **Recommendation:** Use make_filtering_bound_logger() instead

## Summary
- Total usages checked: N
- VERIFIED: N (match Context7)
- HALLUCINATED: N (requires correction)

---

Now verify pending files using Context7 queries. Follow this exact structure.""")
```

Wait for all 3 to complete before proceeding to Wave 2.

#### Wave 2 (Paralelo - ~5 min max)

Submit 2 agents in parallel:

**code-reviewer:**
```
Task(subagent_type="code-reviewer", prompt="""Review calidad: complejidad, DRY, naming, mantenibilidad

Focus areas:
- Cyclomatic complexity (>10 = flag for refactoring)
- Duplicate code patterns (suggest consolidation)
- Variable/function naming clarity (camelCase/snake_case consistency)
- Maintainability: Is this code easily understood by other developers?
- Performance bottlenecks or inefficient patterns

Provide actionable recommendations.""")
```

**test-generator:**
```
Task(subagent_type="test-generator", prompt="""Genera tests unitarios para modulos sin cobertura

Coverage analysis:
- Identify functions/methods with <80% coverage
- Generate pytest-style unit tests
- Include edge cases (empty inputs, None, exceptions)
- Mock external dependencies
- Test both happy path and error paths

Output format:
- Suggested test file location
- Test class/function names
- Number of test cases per function
- Expected coverage improvement""")
```

Wait for both to complete.

## Tool Schema Invocation (Phase 3 - Programmatic Tool Calling)

Agents use structured JSON schemas to invoke tools with precision and reduced token overhead.

### Schema Structure

Every tool invocation follows this pattern:
```json
{
  "tool": "tool_name",
  "required_param": "value",
  "optional_param": "value (if applicable)"
}
```

### Wave 1 Agents (Schema Usage %)
- **best-practices-enforcer:** 60% schema usage (Grep, Read, Bash, save_agent_report)
- **security-auditor:** 50% schema usage (Grep, Bash, Read, save_agent_report)
- **hallucination-detector:** 70% schema usage (Grep, Read, context7_resolve_library_id, context7_query_docs, save_agent_report)

### Wave 2 Agents (Partial Schema)
- **code-reviewer:** 40% schema usage (Read, save_agent_report)
- **test-generator:** 30% schema usage (Bash, Read, save_agent_report)

### Common Schemas

**File Search:**
```json
{
  "tool": "grep",
  "pattern": "...",
  "path": "src",
  "type": "py"
}
```

**Read File:**
```json
{
  "tool": "read",
  "file_path": "/absolute/path/file.py"
}
```

**Run Command:**
```json
{
  "tool": "bash",
  "command": "uv run pytest tests/"
}
```

**Save Report:**
```json
{
  "tool": "save_agent_report",
  "agent_name": "best-practices-enforcer",
  "phase": 3,
  "findings": [...],
  "summary": {"total": N, "critical": 0, "high": N, "medium": N, "low": N}
}
```

**Context7 Queries (hallucination-detector only):**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "httpx",
  "query": "async client timeout"
}
```

### Validation & Fallback

If agent produces invalid schema:
1. Schema validation fails → log error
2. Fall back to natural language tool description
3. Agent continues with guidance

If schema validation passes:
- Agent uses structured tool invocation
- Reduced token overhead (60-70% smaller than natural language)
- Explicit constraints prevent misuse

### Schema Reference

For complete schema definitions see: `.claude/rules/agent-tool-schemas.md`

---

### 3. Logging de Agentes (OBLIGATORIO)

Después de ejecutar CADA agente, añadir entrada JSONL a `.build/logs/agents/YYYY-MM-DD.jsonl`:

```json
{
  "id": "<uuid>",
  "timestamp": "<ISO8601>",
  "session_id": "<session_id>",
  "agent": "<agent_name>",
  "files": ["<archivo1>", "<archivo2>"],
  "status": "PASSED|FAILED",
  "findings": [],
  "duration_ms": <milliseconds>
}
```

Si el agente encuentra hallazgos, también registrar en `.build/logs/decisions/YYYY-MM-DD.jsonl`:

```json
{
  "id": "<uuid>",
  "timestamp": "<ISO8601>",
  "session_id": "<session_id>",
  "agent": "<agent_name>",
  "type": "finding",
  "severity": "HIGH|MEDIUM|LOW",
  "finding": "<descripcion>",
  "file": "<archivo>",
  "outcome": "flagged|fixed"
}
```

### 4. Si TODOS Pasan, Limpiar Markers

```bash
rm -rf $CLAUDE_PROJECT_DIR/.build/checkpoints/pending/*
```

### 5. Verificaciones Adicionales

```bash
uv run ruff format src tests --check
uv run ruff check src tests
uv run mypy src
uv run pytest tests/ -v
```

### Con --fix

```bash
uv run ruff format src tests
uv run ruff check src tests --fix
```

## Sistema de Markers

- `post-code.sh` crea markers en `.build/checkpoints/pending/` despues de Write/Edit en .py
- `pre-git-commit.sh` bloquea commit si hay markers pendientes
- `/verify` ejecuta agentes y limpia markers si todo pasa

## Sistema de Trazabilidad

- Logs de agentes: `.build/logs/agents/YYYY-MM-DD.jsonl`
- Logs de decisiones: `.build/logs/decisions/YYYY-MM-DD.jsonl`
- Ver `/show-trace` para consultar logs
- Ver `/generate-report` para generar reportes
