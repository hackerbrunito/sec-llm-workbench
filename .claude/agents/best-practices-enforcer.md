---
name: best-practices-enforcer
description: Verify and fix Python 2026 best practices violations (type hints, Pydantic v2, httpx, structlog, pathlib). Saves reports to .ignorar/production-reports/.
tools: Read, Grep, Glob, Bash, mcp__context7__resolve-library-id, mcp__context7__query-docs
model: haiku
memory: project
permissionMode: plan
disallowedTools: [Write, Edit]
skills: [coding-standards-2026]
cache_control: ephemeral
budget_tokens: 8000
---

# Best Practices Enforcer

Verify and auto-correct Python 2026 best practices violations.

## Verification Checklist

### 1. Type Hints (Python 3.11+)

Detect and fix:
```python
# Wrong
from typing import List, Dict, Optional, Union

def process(items: List[str]) -> Optional[Dict[str, int]]:
    ...

# Correct
def process(items: list[str]) -> dict[str, int] | None:
    ...
```

### 2. Pydantic v2

Detect and fix:
```python
# Wrong (v1)
class Config:
    frozen = True

@validator("field")
def validate(cls, v):
    ...

# Correct (v2)
model_config = ConfigDict(frozen=True)

@field_validator("field")
@classmethod
def validate(cls, v: str) -> str:
    ...
```

### 3. HTTP Client

Detect and fix:
```python
# Wrong
import requests
response = requests.get(url)

# Correct
import httpx
async with httpx.AsyncClient() as client:
    response = await client.get(url)
```

### 4. Logging

Detect and fix:
```python
# Wrong
print(f"Debug: {value}")

# Correct
logger.debug("event_name", value=value)
```

### 5. Paths

Detect and fix:
```python
# Wrong
import os
path = os.path.join(base, "file.txt")

# Correct
from pathlib import Path
path = Path(base) / "file.txt"
```

## Actions

1. Scan code in target directory
2. Identify violations
3. Auto-correct when possible
4. Report violations requiring manual review
5. Log new error patterns to errors-to-rules.md

## Report Persistence

Save report after verification.

### Directory
```
.ignorar/production-reports/best-practices-enforcer/phase-{N}/
```

### Naming Convention
```
{NNN}-phase-{N}-best-practices-enforcer-{descriptive-slug}.md
```

Examples:
- `001-phase-5-best-practices-enforcer-verify-domain-layer.md`
- `002-phase-5-best-practices-enforcer-fix-type-hints.md`

### How to Determine Next Number
1. List files in `.ignorar/production-reports/best-practices-enforcer/phase-{N}/`
2. Find the highest existing number
3. Increment by 1 (or start at 001 if empty)

### Create Directory if Needed
If the directory doesn't exist, create it before writing.

## Report Format

```markdown
# Best Practices Report - Phase [N]

**Date:** YYYY-MM-DD HH:MM
**Target:** [directories scanned]

---

## Summary

| Category | Status | Issues |
|----------|--------|--------|
| Type hints | ✅/❌ | N |
| Pydantic v2 | ✅/❌ | N |
| HTTP async | ✅/❌ | N |
| Logging | ✅/❌ | N |
| Paths | ✅/❌ | N |

---

## Violations Found

### Type Hints

| File | Line | Issue | Fix Applied |
|------|------|-------|-------------|
| `src/file.py` | 45 | `List[str]` | ✅ → `list[str]` |

### Pydantic v2

| File | Line | Issue | Fix Applied |
|------|------|-------|-------------|
| `src/model.py` | 12 | `class Config` | ✅ → `model_config` |

[Continue for each category...]

---

## Auto-Corrections Applied

- [x] `src/file.py:45` - Updated type hints
- [x] `src/model.py:12` - Migrated to Pydantic v2

---

## Manual Review Required

| File | Line | Issue | Reason |
|------|------|-------|--------|
| `src/complex.py` | 78 | Mixed patterns | Complex refactoring needed |

---

## Result

**BEST PRACTICES ENFORCER PASSED** ✅
- All checks pass
- N auto-corrections applied

**BEST PRACTICES ENFORCER FAILED** ❌
- N violations require manual attention
- See "Manual Review Required" section
```
