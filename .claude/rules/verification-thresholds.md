<!-- version: 2026-02 -->
# Verification Thresholds - Single Source of Truth

**Purpose:** Centralized definition of all verification pass/fail criteria across the project.

**Last Updated:** 2026-02-08
**Status:** Active
**Referenced by:**
- `.claude/workflow/05-before-commit.md` (before-commit checklist)
- `.claude/hooks/pre-git-commit.sh` (commit blocking logic)
- `.claude/workflow/04-agents.md` (agent verification outcomes)

---

## Verification Thresholds Table

| Check | Category | PASS Criteria | FAIL Criteria | Blocking | Agent |
|-------|----------|---------------|--------------|---------:|--------|
| **ruff check (errors)** | Code Quality | 0 errors | Any error | ✅ Yes | N/A |
| **ruff check (warnings)** | Code Quality | 0 warnings | Any warning | ✅ Yes | N/A |
| **ruff format** | Code Style | No changes needed | Changes required | ✅ Yes | N/A |
| **mypy errors** | Type Safety | 0 errors | Any error | ✅ Yes | N/A |
| **pytest** | Testing | All tests pass | Any test fails | ✅ Yes | test-generator |
| **best-practices-enforcer** | Standards | 0 violations | Any violation | ✅ Yes | best-practices-enforcer |
| **security-auditor** | Security | 0 CRITICAL/HIGH | Any CRITICAL/HIGH | ✅ Yes | security-auditor |
| **security-auditor (MEDIUM)** | Security | Warning level | N/A | ❌ No | security-auditor |
| **hallucination-detector** | Correctness | 0 hallucinations | Any hallucination | ✅ Yes | hallucination-detector |
| **code-reviewer score** | Code Quality | >= 9.0/10 | < 9.0/10 | ✅ Yes | code-reviewer |

---

## Details by Agent

### 1. best-practices-enforcer

**Scope:** Modern Python standards (Pydantic v2, httpx, structlog, pathlib, type hints)

**Violations:**
- Using `typing.List` instead of `list[str]`
- Using `typing.Dict` instead of `dict[str, Any]`
- Using `typing.Optional[X]` instead of `X | None`
- Using Pydantic v1 `class Config:` instead of `ConfigDict`
- Using `requests` instead of `httpx`
- Using `print()` instead of `structlog`
- Using `os.path` instead of `pathlib.Path`
- Missing type hints on function parameters/returns

**Pass:** 0 violations
**Fail:** Any violation found

---

### 2. security-auditor

**Scope:** OWASP Top 10, secrets, injection attacks, authentication/authorization

**Critical/High Issues:**
- Hardcoded API keys, passwords, or tokens (CWE-798)
- SQL injection patterns (CWE-89)
- Cross-site scripting (XSS) patterns (CWE-79)
- Command injection patterns (CWE-78)
- Authentication/authorization bypasses
- Insecure deserialization (CWE-502)
- Insufficient input validation
- Cryptographic weaknesses

**Medium Issues:**
- Weak hashing algorithms
- Missing security headers (advisory)
- Suspicious patterns (informational)

**Pass:** 0 CRITICAL or HIGH severity findings
**Fail:** Any CRITICAL or HIGH severity finding
**Warning (Non-blocking):** MEDIUM severity findings allowed (logged but not blocking)

---

### 3. hallucination-detector

**Scope:** Library syntax verification against Context7 MCP

**Hallucinations:**
- Using deprecated library APIs
- Incorrect function/method signatures
- Wrong parameter names or types
- Missing imports
- Version mismatches (e.g., using Pydantic v2 syntax with v1)
- Non-existent library functions

**Pass:** 0 hallucinations detected
**Fail:** Any hallucination found

---

### 4. code-reviewer

**Scope:** Code quality, maintainability, complexity, DRY principle

**Review Criteria:**
- Cyclomatic complexity > 10 per function (flag for simplification)
- Duplicate code patterns (DRY violations)
- Naming consistency and clarity
- Function/method length > 30 lines (suggest extraction)
- Missing docstrings for public functions (advisory)
- Performance bottlenecks
- Test coverage < 80%

**Pass:** Code reviewer score >= 9.0/10
**Fail:** Code reviewer score < 9.0/10

**Score Breakdown (Out of 10):**
- Complexity & Maintainability: 0-4 points
- DRY & Duplication: 0-2 points
- Naming & Clarity: 0-2 points
- Performance: 0-1 point
- Testing: 0-1 point

---

### 5. test-generator

**Scope:** Test coverage, edge cases, mock management

**Coverage Criteria:**
- Overall coverage >= 80%
- Critical paths covered (happy path + error path)
- Edge cases tested (None, empty, boundary values)
- External dependencies mocked
- Test naming follows convention: `test_<function>_<scenario>`

**Pass:** All tests pass + coverage >= 80%
**Fail:** Any test fails OR coverage < 80%

---

## Command Blockers

These checks are automatically applied by `.claude/hooks/pre-git-commit.sh`:

1. **Git commit command** is intercepted
2. **Check pending directory:** `.build/checkpoints/pending/`
   - If pending files exist: **BLOCK** with message
   - If no pending files: **ALLOW** (proceed to next check)
3. **Check code-reviewer score:** Via `.claude/scripts/check-reviewer-score.sh`
   - If score < 9.0/10: **BLOCK** with message
   - If score >= 9.0/10: **ALLOW** (all verified)
   - If no report found: **WARN** but allow (graceful degradation)
   - If parsing fails: **WARN** but allow (graceful degradation)

**Blocking Message Format (Pending Files):**
```
COMMIT BLOQUEADO: Hay {N} archivo(s) Python sin verificar por agentes.
Archivos pendientes: {LIST}
ACCION REQUERIDA: Ejecuta /verify para correr los agentes de verificacion, despues intenta commit de nuevo.
```

**Blocking Message Format (Code Reviewer Score):**
```
COMMIT BLOQUEADO: Code reviewer score no cumple con threshold >= 9.0/10.

[Score output from check-reviewer-score.sh]

ACCION REQUERIDA: Corrige los problemas de calidad identificados y ejecuta /verify nuevamente.
```

**Helper Script:** `.claude/scripts/check-reviewer-score.sh`
- Searches for most recent code-reviewer report in `.ignorar/production-reports/code-reviewer/`
- Extracts score using multiple pattern matching strategies
- Returns exit code 0 (PASS) if score >= 9.0/10
- Returns exit code 1 (FAIL) if score < 9.0/10
- Returns exit code 0 with WARNING if no report found (first-time setup)
- Returns exit code 0 with WARNING if score parsing fails (graceful degradation)

---

## Workflow Integration

### Before Commit Checklist
```
1. ✅ Ejecutar /verify (5 agentes de verificación)
2. ✅ ruff format + ruff check
3. ✅ mypy src
4. ✅ pytest (si hay tests)
```

### /verify Command
Runs automatically:
- best-practices-enforcer
- security-auditor
- hallucination-detector
- code-reviewer
- test-generator

Cleans markers in `.build/checkpoints/pending/`

### If Verification Fails
1. DO NOT commit
2. Fix errors
3. Run `/verify` again
4. Only then commit

---

## Threshold History & Changes

### Version 2026-02 (Current)
- Extracted from `.claude/workflow/05-before-commit.md`
- Centralized for consistency
- Added detail columns for each agent
- Added command blocker documentation

---

## Related Files

- **Workflow Reference:** `.claude/workflow/05-before-commit.md`
- **Agent Invocation:** `.claude/workflow/04-agents.md`
- **Commit Hook:** `.claude/hooks/pre-git-commit.sh`
- **Session Start:** `.claude/workflow/01-session-start.md`

---

## Adding New Thresholds

When adding new verification checks:

1. Update this file with new row in table
2. Add detailed section below
3. Update relevant workflow files to reference this file
4. Update `.claude/hooks/pre-git-commit.sh` if it's a blocking check
5. Document in `.claude/docs/errors-to-rules.md` if threshold was controversial

---

**Maintained by:** Orchestrator + Code Implementer
**Reviewed by:** best-practices-enforcer + security-auditor
**Last verified:** 2026-02-08
