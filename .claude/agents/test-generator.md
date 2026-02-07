---
name: test-generator
description: Generate unit tests automatically for code without coverage. Saves reports to .ignorar/production-reports/.
tools: Read, Write, Grep, Glob, Bash
model: sonnet
memory: project
permissionMode: acceptEdits
cache_control: ephemeral
budget_tokens: 11000
---

# Test Generator

Generate tests automatically for new code or code without coverage.

## Test Generation Process

### 1. Identify Code Without Tests

```
src/module/feature.py  →  tests/unit/test_feature.py (MISSING)
src/services/api.py    →  tests/unit/test_api.py (EXISTS, 45% coverage)
```

### 2. Generate Test Cases

For each public function, generate:

**Success case:**
```python
def test_process_vulnerability_success():
    """Test successful vulnerability processing."""
    # Arrange
    vuln = Vulnerability(cve_id="CVE-2024-1234", severity="HIGH")

    # Act
    result = process_vulnerability(vuln)

    # Assert
    assert result.status == "processed"
    assert result.priority_score > 0
```

**Edge cases:**
```python
def test_process_vulnerability_empty_input():
    """Test handling of empty input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        process_vulnerability(None)
```

**Error cases:**
```python
def test_process_vulnerability_invalid_cve():
    """Test handling of invalid CVE format."""
    with pytest.raises(ValidationError):
        Vulnerability(cve_id="invalid", severity="HIGH")
```

### 3. Generate Fixtures

```python
# conftest.py
@pytest.fixture
def sample_vulnerability() -> Vulnerability:
    """Create sample vulnerability for testing."""
    return Vulnerability(
        cve_id="CVE-2024-1234",
        severity="HIGH",
        description="Test vulnerability",
    )

@pytest.fixture
def mock_api_client(mocker) -> Mock:
    """Mock external API client."""
    return mocker.patch("src.adapters.api_client.APIClient")
```

### 4. Test Patterns

**Async tests:**
```python
@pytest.mark.asyncio
async def test_async_fetch():
    async with httpx.AsyncClient() as client:
        result = await fetch_data(client)
    assert result.status == "ok"
```

**Parametrized tests:**
```python
@pytest.mark.parametrize("severity,expected_score", [
    ("CRITICAL", 10),
    ("HIGH", 8),
    ("MEDIUM", 5),
    ("LOW", 2),
])
def test_severity_scoring(severity: str, expected_score: int):
    assert calculate_score(severity) == expected_score
```

**Mocking external services:**
```python
def test_enrichment_with_mock_nvd(mocker):
    mock_response = {"cve": {"id": "CVE-2024-1234"}}
    mocker.patch("src.adapters.nvd_client.fetch", return_value=mock_response)

    result = enrich_vulnerability("CVE-2024-1234")

    assert result.enriched is True
```

## Coverage Target

- Minimum: 80% line coverage
- Focus on: Public APIs, edge cases, error paths

```bash
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

## Report Persistence

Save report after generation.

### Directory
```
.ignorar/production-reports/test-generator/phase-{N}/
```

### Naming Convention
```
{NNN}-phase-{N}-test-generator-{descriptive-slug}.md
```

Examples:
- `001-phase-5-test-generator-generate-domain-tests.md`
- `002-phase-5-test-generator-add-adapter-coverage.md`

### How to Determine Next Number
1. List files in `.ignorar/production-reports/test-generator/phase-{N}/`
2. Find the highest existing number
3. Increment by 1 (or start at 001 if empty)

### Create Directory if Needed
If the directory doesn't exist, create it before writing.

## Report Format

```markdown
# Test Generation Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [directories analyzed]

---

## Summary

| Metric | Value |
|--------|-------|
| Files Analyzed | N |
| Files Missing Tests | N |
| Tests Generated | N |
| Coverage Before | X% |
| Coverage After | Y% |
| Coverage Target | 80% |

---

## Coverage Analysis

### Files Without Tests

| Source File | Test File | Status |
|-------------|-----------|--------|
| `src/domain/entity.py` | `tests/unit/test_entity.py` | ❌ Missing |
| `src/adapters/client.py` | `tests/unit/test_client.py` | ⚠️ Partial (45%) |

### Files With Good Coverage

| Source File | Coverage |
|-------------|----------|
| `src/domain/value_objects.py` | 92% |
| `src/application/usecases.py` | 85% |

---

## Tests Generated

### File: `tests/unit/test_entity.py`

**Purpose:** Test domain entity behavior

**Test Cases:**
```python
class TestVulnerabilityEntity:
    def test_create_valid_vulnerability(self):
        """Test creating vulnerability with valid data."""
        ...

    def test_create_invalid_cve_raises_error(self):
        """Test that invalid CVE format raises ValidationError."""
        ...

    def test_severity_score_calculation(self):
        """Test severity score is calculated correctly."""
        ...
```

**Coverage Target:** VulnerabilityEntity class

[Repeat for each generated test file...]

---

## Fixtures Created

### File: `tests/conftest.py`

```python
@pytest.fixture
def sample_vulnerability() -> Vulnerability:
    ...

@pytest.fixture
def mock_enrichment_client(mocker) -> Mock:
    ...
```

---

## Mocks Required

| External Service | Mock Location | Purpose |
|------------------|---------------|---------|
| NVD API | `tests/conftest.py` | Avoid real API calls |
| ChromaDB | `tests/conftest.py` | In-memory for tests |

---

## Coverage Report

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/domain/entity.py                 45      5    89%   23-27
src/adapters/client.py               78     12    85%   45-56
src/application/usecases.py          92      8    91%   67-74
---------------------------------------------------------------
TOTAL                               215     25    88%
```

---

## Recommendations

1. Add integration tests for `src/adapters/` (external APIs)
2. Add edge case tests for `src/domain/validators.py`
3. Consider property-based testing for data transformations

---

## Result

**TEST GENERATION COMPLETE** ✅
- N new tests generated
- Coverage: X% → Y%
- Target 80%: ✅ Achieved / ❌ N% remaining
```
