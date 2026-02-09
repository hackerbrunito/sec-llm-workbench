# Agent Tool Schemas (Phase 3: Programmatic Tool Calling)

**Date:** 2026-02-07
**Status:** Phase 3 Implementation
**Impact:** -37% tokens, $4.2k/year baseline cost reduction (150 cycles/month × $0.47/cycle × 12 months)

---

## Overview

Structured JSON schemas for tool invocation reduce token consumption while improving precision. Instead of natural language tool descriptions, agents use explicit JSON schemas that define:
- Tool name and purpose
- Required/optional parameters
- Parameter types and constraints
- Example invocations

This document defines schemas for 8 core tools used by verification agents.

---

## File Operations

### Bash Schema

**Purpose:** Execute shell commands for linting, testing, git operations, and toolchain invocation. Supports timeouts and process control for long-running operations.

**Use Cases:**
- Run static analysis tools (ruff, mypy, bandit)
- Execute test suites with coverage reporting
- Perform git operations (status, diff, log)
- Invoke build tools and package managers (uv, pip)
- Measure code metrics (radon, complexity analysis)

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `command` | string | Yes | Non-empty, valid shell syntax | Full command with args |
| `description` | string | No | Max 200 chars | Human-readable purpose |
| `timeout_ms` | number | No | Range: 1000-600000 | Default: 120000 (2 min) |

**Constraints:**
- Commands execute in project root directory by default
- Environment inherits from parent shell (PATH, virtualenv)
- Max timeout: 10 minutes (600000ms) for heavy operations
- Working directory persists between calls
- Shell state (variables, aliases) does NOT persist

**Examples:**

1. **Ruff validation with custom config:**
```json
{
  "tool": "bash",
  "command": "uv run ruff check src/ --config pyproject.toml",
  "description": "Verify Python formatting against project standards",
  "timeout_ms": 30000
}
```
**Output:** List of violations with file paths and line numbers
**Interpretation:** Exit code 0 = pass, non-zero = violations found

2. **Coverage report generation:**
```json
{
  "tool": "bash",
  "command": "pytest tests/ --cov=src --cov-report=json --cov-report=term",
  "description": "Generate test coverage metrics",
  "timeout_ms": 180000
}
```
**Output:** JSON coverage data + terminal summary
**Interpretation:** Parse JSON for programmatic threshold checks (>80%)

3. **Git diff for code review:**
```json
{
  "tool": "bash",
  "command": "git diff --unified=3 main...HEAD",
  "description": "Show changes since branch diverged from main"
}
```
**Output:** Unified diff format with 3 lines context
**Interpretation:** Review added/removed lines for semantic changes

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `TimeoutError` | Command exceeds timeout | Increase `timeout_ms` or optimize command |
| `CommandNotFoundError` | Tool not in PATH | Install dependency with `uv add` |
| `ExitCode != 0` | Validation failures | Parse stderr for specific violations |
| `PermissionDenied` | Insufficient file permissions | Check file ownership and chmod |

**Performance Notes:**
- Long-running tests (>2 min): Increase timeout to 300000ms
- Heavy I/O operations: Consider splitting into smaller batches
- Git operations on large repos: Use `--no-pager` to prevent hanging
- Parallel tool execution: Use `&` for background jobs cautiously (job control varies)

---

### Read Schema

**Purpose:** Read file contents with optional line-range filtering for efficient large-file inspection. Supports text files, code, configuration, and documentation with automatic encoding detection.

**Use Cases:**
- Inspect source code for pattern analysis
- Read configuration files for validation
- Extract specific sections from large files using offset/limit
- Verify file contents before modification
- Load documentation for context

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `file_path` | string | Yes | Absolute path, file must exist | Relative paths rejected |
| `offset` | number | No | Line number ≥1 | Starting line (1-indexed) |
| `limit` | number | No | Lines to read, ≥1 | Max lines from offset |

**Constraints:**
- Absolute paths required (e.g., `/Users/bruno/project/file.py`)
- Lines >2000 chars are truncated with `...` marker
- Default behavior: Read entire file (no offset/limit)
- Binary files return error (use for text files only)
- Symlinks are followed automatically

**Examples:**

1. **Full file read for code review:**
```json
{
  "tool": "read",
  "file_path": "/Users/bruno/sec-llm-workbench/src/api/client.py"
}
```
**Output:** Complete file with line numbers (cat -n format)
**Interpretation:** Line 1 starts at `1\tContent...`, scan for patterns

2. **Paginated read for large files:**
```json
{
  "tool": "read",
  "file_path": "/Users/bruno/sec-llm-workbench/src/models/user.py",
  "offset": 50,
  "limit": 100
}
```
**Output:** Lines 50-149 with line numbers
**Interpretation:** Isolate specific class/function without loading full file

3. **Configuration validation:**
```json
{
  "tool": "read",
  "file_path": "/Users/bruno/sec-llm-workbench/pyproject.toml"
}
```
**Output:** TOML configuration with line numbers
**Interpretation:** Parse for dependency versions, tool settings

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `FileNotFoundError` | Path doesn't exist | Use Glob to find correct path |
| `PermissionError` | No read access | Check file permissions (chmod) |
| `IsADirectoryError` | Path points to directory | Use Glob to list directory contents |
| `UnicodeDecodeError` | Binary file read attempt | Check file type before reading |
| `InvalidOffset` | Offset exceeds file length | Read without offset first |

**Performance Notes:**
- Files >10K lines: Use offset/limit to paginate (avoids token waste)
- Repeated reads: Cache in agent memory if needed multiple times
- Large config files: Read once, parse in memory
- Log files: Use `limit` to read recent entries (tail-like behavior)

---

### Glob Schema

**Purpose:** Fast file pattern matching using glob syntax for discovering files by name, extension, or directory structure. Returns sorted results by modification time (most recent first).

**Use Cases:**
- Find all Python files for verification (`**/*.py`)
- Locate configuration files (`.env*`, `*.toml`)
- Discover test files (`tests/**/test_*.py`)
- Identify potential secrets (`**/.env`, `**/credentials.*`)
- Build file lists for batch processing

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `pattern` | string | Yes | Valid glob syntax | Supports `*`, `**`, `?`, `[]` |
| `path` | string | No | Valid directory path | Default: current working directory |

**Constraints:**
- Pattern uses standard glob syntax: `*` (any chars), `**` (recursive), `?` (single char)
- Results sorted by modification time (newest first)
- Hidden files require explicit pattern (`.*/.*` or `**/.*`)
- Symbolic links followed by default
- Case-sensitive on Linux/macOS, case-insensitive on Windows

**Examples:**

1. **Find all Python source files:**
```json
{
  "tool": "glob",
  "pattern": "src/**/*.py"
}
```
**Output:** List of absolute paths sorted by modification time
**Interpretation:** Most recently modified files appear first

2. **Detect environment files (security):**
```json
{
  "tool": "glob",
  "pattern": "**/.env*",
  "path": "/Users/bruno/sec-llm-workbench"
}
```
**Output:** Paths to `.env`, `.env.local`, `.env.example`, etc.
**Interpretation:** Check if `.env` committed to git (security risk)

3. **Locate test files for coverage analysis:**
```json
{
  "tool": "glob",
  "pattern": "tests/**/test_*.py"
}
```
**Output:** All test files matching `test_*.py` pattern
**Interpretation:** Compare against source files to identify coverage gaps

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `NoMatchesFound` | Pattern too specific | Broaden pattern (e.g., `**/*.py` vs `src/*.py`) |
| `InvalidPattern` | Malformed glob syntax | Escape special chars, check brackets |
| `PathNotFound` | Invalid directory path | Verify `path` parameter exists |
| `TooManyResults` | Pattern too broad | Narrow with subdirectory or extension |

**Performance Notes:**
- Large repos (>10K files): Use specific patterns to avoid full tree scan
- Recursive patterns (`**`): Can be slow on deep directories, limit scope
- Hidden file search: More expensive than visible files
- Pattern ordering: More specific patterns first (e.g., `src/**/*.py` vs `**/*.py`)

---

### Grep Schema

**Purpose:** Fast content search using ripgrep (rg) with regex support for finding patterns, vulnerabilities, and deprecated code across large codebases. Supports filtering by file type, output modes, and context lines.

**Use Cases:**
- Search for hardcoded secrets and credentials
- Find deprecated API usage (e.g., `typing.List`)
- Locate security vulnerabilities (SQL injection patterns)
- Identify TODO/FIXME comments
- Detect import statement patterns

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `pattern` | string | Yes | Valid regex (ripgrep syntax) | Literal braces need escaping |
| `path` | string | No | Valid directory/file path | Default: current directory |
| `type` | string | No | File type (py, js, json, etc.) | More efficient than glob filter |
| `output_mode` | string | No | content/files_with_matches/count | Default: files_with_matches |

**Constraints:**
- Uses ripgrep syntax (NOT standard grep): braces require escaping `\{`
- `output_mode=content` shows matching lines with context (use `-A`, `-B`, `-C`)
- `output_mode=files_with_matches` shows only file paths (faster for counting)
- `output_mode=count` shows match counts per file
- Case-sensitive by default (use `-i` parameter for case-insensitive)
- Multiline patterns require `multiline: true` parameter

**Examples:**

1. **Security: Find hardcoded secrets:**
```json
{
  "tool": "grep",
  "pattern": "hardcoded|password|secret|api_key|token",
  "path": "/Users/bruno/sec-llm-workbench/src",
  "type": "py",
  "output_mode": "content"
}
```
**Output:** File paths + line numbers + matched lines
**Interpretation:** Any match is HIGH severity security risk (CWE-798)

2. **Best practices: Find legacy type hints:**
```json
{
  "tool": "grep",
  "pattern": "from typing import.*(List|Dict|Optional|Union)",
  "type": "py",
  "output_mode": "files_with_matches"
}
```
**Output:** File paths containing legacy typing imports
**Interpretation:** Files need migration to modern syntax (`list[str]` not `List[str]`)

3. **Code review: Find SQL injection patterns:**
```json
{
  "tool": "grep",
  "pattern": "execute\\(.*f\"|SELECT.*\\{",
  "path": "/Users/bruno/sec-llm-workbench/src",
  "type": "py",
  "output_mode": "content"
}
```
**Output:** Lines with potential SQL injection (f-strings in queries)
**Interpretation:** CRITICAL vulnerability (CWE-89), requires parameterized queries

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `InvalidRegex` | Malformed regex pattern | Escape special chars: `\.`, `\{`, `\(` |
| `NoMatches` | Pattern too specific | Broaden pattern or check file type filter |
| `TooManyMatches` | Pattern too broad | Add context (path or type filter) |
| `TimeoutError` | Large repo + complex regex | Simplify regex or narrow path scope |

**Performance Notes:**
- Large repos (>50K files): Use `type` filter to reduce search space
- Complex regex: Test with `output_mode=count` first to estimate matches
- Context lines (`-A`, `-B`, `-C`): Only use with `output_mode=content`
- Case-insensitive search (`-i`): Slower than case-sensitive, use sparingly

---

## Context7 MCP Tools (hallucination-detector only)

### context7_resolve_library_id Schema

**Purpose:** Resolve human-readable library names to Context7-compatible library IDs for documentation queries. Returns the most relevant match based on name similarity, description relevance, and documentation coverage.

**Use Cases:**
- Convert library names to Context7 IDs before querying docs
- Discover available library versions in Context7
- Validate library exists in documentation corpus
- Find alternative library names (e.g., "requests" vs "httpx")
- Check documentation quality (code snippet count, benchmark score)

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `libraryName` | string | Yes | Library/package name | Case-insensitive, partial match OK |
| `query` | string | Yes | User's original question | Used for relevance ranking |

**Constraints:**
- Do NOT call more than 3 times per question (quota limit)
- Returns single best match (not exhaustive list)
- Prioritizes: exact name match > description relevance > snippet count
- May fail if library not in Context7 corpus (fallback to memory)
- Monthly quota limits apply (check for 429 errors)

**Examples:**

1. **Resolve httpx for async client verification:**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "httpx",
  "query": "async client timeout configuration"
}
```
**Output:** `{"library_id": "/encode/httpx", "version": "0.24.1", "benchmark_score": 95}`
**Interpretation:** Use `/encode/httpx` for subsequent `query_docs` calls

2. **Resolve Pydantic for validation checking:**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "pydantic",
  "query": "Pydantic v2 ConfigDict and field_validator usage"
}
```
**Output:** `{"library_id": "/pydantic/pydantic", "version": "2.5.0", "benchmark_score": 98}`
**Interpretation:** High benchmark score = comprehensive docs available

3. **Resolve with partial name match:**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "struct",
  "query": "structured logging with context"
}
```
**Output:** `{"library_id": "/hynek/structlog", "version": "23.2.0", "benchmark_score": 88}`
**Interpretation:** Context7 matched "struct" to "structlog"

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `QuotaExceeded` | Monthly API limit reached | Use fallback to agent memory |
| `NoMatchFound` | Library not in Context7 | Use training data, mark as "unverified" |
| `AmbiguousMatch` | Multiple libraries match | Refine `query` with more context |
| `TimeoutError` | Server latency >10s | Retry once, then fallback |

**Performance Notes:**
- Typical latency: 200-500ms (fast)
- Cache results in agent memory for repeated queries
- Batch library lookups at start of verification cycle
- Use `query` field strategically (better relevance = better match)

---

### context7_query_docs Schema

**Purpose:** Query library documentation with specific questions to retrieve verified syntax, examples, and best practices. Returns code snippets, API signatures, and usage patterns directly from official documentation.

**Use Cases:**
- Verify correct function/method signatures
- Retrieve code examples for specific functionality
- Check parameter types and constraints
- Validate deprecated vs current API usage
- Discover recommended patterns and anti-patterns

**Parameters:**

| Parameter | Type | Required | Constraints | Notes |
|-----------|------|----------|-------------|-------|
| `libraryId` | string | Yes | Context7 format: `/org/project` | From `resolve_library_id` |
| `query` | string | Yes | Specific question, 10-100 words | Better specificity = better results |

**Constraints:**
- Do NOT call more than 3 times per question (quota limit)
- Requires valid `libraryId` from `resolve_library_id` first
- Do NOT include sensitive data (API keys, credentials) in query
- Query specificity critical: "How to X?" > "Tell me about X"
- Returns semantic search results (not exact text match)

**Examples:**

1. **Verify httpx AsyncClient timeout syntax:**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/encode/httpx",
  "query": "How to set timeout parameter in AsyncClient constructor?"
}
```
**Output:** Code snippet + explanation showing `httpx.AsyncClient(timeout=30.0)` or `httpx.Timeout(connect=5.0, read=30.0)`
**Interpretation:** Compare against codebase usage, flag mismatches as hallucinations

2. **Check Pydantic v2 validator syntax:**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/pydantic/pydantic",
  "query": "What is the correct decorator for field validation in Pydantic v2?"
}
```
**Output:** Example showing `@field_validator('field_name')` with `@classmethod` decorator
**Interpretation:** Detect legacy `@validator` usage in codebase (v1 pattern)

3. **Discover structlog best practices:**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/hynek/structlog",
  "query": "Recommended way to configure structlog for production JSON logging"
}
```
**Output:** Configuration example with processors, formatters, and context binding
**Interpretation:** Compare project setup against recommended patterns

**Common Failure Modes:**

| Error | Cause | Remediation |
|-------|-------|-------------|
| `InvalidLibraryId` | Malformed ID or not resolved | Call `resolve_library_id` first |
| `QuotaExceeded` | Monthly limit reached | Use fallback to training data |
| `VagueQuery` | Query too broad ("tell me about X") | Rephrase with specific question |
| `TimeoutError` | Server latency >10s | Retry once, then fallback |
| `NoResults` | Query doesn't match documentation | Rephrase or try related terms |

**Performance Notes:**
- Typical latency: 400-1000ms (moderate)
- Cache results for repeated queries in same verification cycle
- Prioritize queries for unfamiliar libraries (known libs = use memory)
- Batch related queries (e.g., all httpx questions together)

---

## Agent Operations

### Task Schema

Used for: Delegating work to subagents

```json
{
  "tool": "task",
  "subagent_type": "string",
  "prompt": "string",
  "context": "string (optional)"
}
```

**Example (code-implementer delegation):**
```json
{
  "tool": "task",
  "subagent_type": "code-implementer",
  "prompt": "Implement domain layer for user management module"
}
```

---

### SendMessage Schema

Used for: Team communication

```json
{
  "tool": "send_message",
  "type": "message|broadcast",
  "recipient": "string (required for type='message')",
  "content": "string",
  "summary": "string"
}
```

**Example:**
```json
{
  "tool": "send_message",
  "type": "message",
  "recipient": "team-lead",
  "content": "Phase 3 implementation complete with 37% token reduction",
  "summary": "Phase 3 complete, token reduction achieved"
}
```

---

## Report Generation (All Agents)

### save_agent_report Schema

Used for: Saving verification reports to persistent storage

```json
{
  "tool": "save_agent_report",
  "agent_name": "string (enum)",
  "phase": "number",
  "findings": "array",
  "summary": "object",
  "wave": "string (optional)",
  "start_time": "string (ISO8601, optional)",
  "end_time": "string (ISO8601, optional)"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_name` | string | Yes | One of: best-practices-enforcer, security-auditor, hallucination-detector, code-reviewer, test-generator |
| `phase` | number | Yes | Phase number (e.g., 3) |
| `findings` | array | Yes | Array of finding objects |
| `summary` | object | Yes | Summary counts: {total, critical, high, medium, low} |
| `wave` | string | No | "Wave1" or "Wave2" |
| `start_time` | string | No | ISO8601 timestamp |
| `end_time` | string | No | ISO8601 timestamp |

**Finding Object Structure:**
```json
{
  "id": "string (unique ID)",
  "file": "string (absolute path)",
  "line": "number (optional)",
  "severity": "string (CRITICAL|HIGH|MEDIUM|LOW)",
  "finding": "string (description)",
  "fix": "string (recommended fix)"
}
```

**Summary Object Structure:**
```json
{
  "total": "number",
  "critical": "number",
  "high": "number",
  "medium": "number",
  "low": "number"
}
```

**Example (best-practices-enforcer):**
```json
{
  "tool": "save_agent_report",
  "agent_name": "best-practices-enforcer",
  "phase": 3,
  "findings": [
    {
      "id": "BP001",
      "file": "/Users/bruno/sec-llm-workbench/src/models/user.py",
      "line": 12,
      "severity": "MEDIUM",
      "finding": "Using Pydantic v1 'class Config' pattern instead of ConfigDict",
      "fix": "Replace with: model_config = ConfigDict(validate_assignment=True)"
    },
    {
      "id": "BP002",
      "file": "/Users/bruno/sec-llm-workbench/src/api/client.py",
      "line": 15,
      "severity": "LOW",
      "finding": "Missing type hints on function parameter",
      "fix": "Add type hint: def process(data: dict[str, Any]) -> ProcessResult"
    }
  ],
  "summary": {
    "total": 2,
    "critical": 0,
    "high": 0,
    "medium": 1,
    "low": 1
  },
  "wave": "Wave1",
  "start_time": "2026-02-07T10:30:00Z",
  "end_time": "2026-02-07T10:35:00Z"
}
```

**Example (security-auditor):**
```json
{
  "tool": "save_agent_report",
  "agent_name": "security-auditor",
  "phase": 3,
  "findings": [
    {
      "id": "SEC001",
      "file": "/Users/bruno/sec-llm-workbench/src/config/credentials.py",
      "line": 12,
      "severity": "CRITICAL",
      "finding": "Hardcoded API key in source code (CWE-798)",
      "fix": "Load from environment: api_key = os.getenv('API_KEY')"
    }
  ],
  "summary": {
    "total": 1,
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0
  }
}
```

---

## Agent-Specific Tool Usage

### best-practices-enforcer

**Primary Tools:** Grep, Read, Bash
**Schema Usage:** 60%

**Focus Areas:**
- Type hints (list[str] not List[str])
- Pydantic v2 (ConfigDict, @field_validator)
- HTTP async (httpx not requests)
- Logging (structlog not print)
- Paths (pathlib not os.path)

**Tool Invocation Examples:**

1. **Find Pydantic violations:**
```json
{
  "tool": "grep",
  "pattern": "from typing import.*List|Dict|Optional|Union",
  "path": "src",
  "type": "py"
}
```

2. **Check specific file:**
```json
{
  "tool": "read",
  "file_path": "src/models/user.py"
}
```

3. **Run ruff check:**
```json
{
  "tool": "bash",
  "command": "uv run ruff check src/"
}
```

4. **Save report:**
```json
{
  "tool": "save_agent_report",
  "agent_name": "best-practices-enforcer",
  "phase": 3,
  "findings": [],
  "summary": {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}
}
```

---

### security-auditor

**Primary Tools:** Grep, Bash, Read
**Schema Usage:** 50%

**Focus Areas:**
- OWASP Top 10 violations
- SQL injection, XSS, CSRF
- Hardcoded secrets
- Authentication/authorization issues
- Data validation gaps

**Tool Invocation Examples:**

1. **Search for hardcoded secrets:**
```json
{
  "tool": "grep",
  "pattern": "hardcoded\\|password\\|secret\\|api\\.?key\\|token",
  "path": "src",
  "type": "py",
  "output_mode": "content"
}
```

2. **Find SQL injection patterns:**
```json
{
  "tool": "grep",
  "pattern": "SELECT.*\\{|execute.*f\"|sql.*%.*%",
  "path": "src",
  "type": "py"
}
```

3. **Run security linter:**
```json
{
  "tool": "bash",
  "command": "bandit -r src/ -f json"
}
```

---

### hallucination-detector

**Primary Tools:** Grep, Read, Context7 MCP
**Schema Usage:** 70%

**Focus Areas:**
- Library syntax verification against Context7
- Deprecated API usage
- Version mismatches
- Missing imports

**Tool Invocation Examples:**

1. **Find httpx usage:**
```json
{
  "tool": "grep",
  "pattern": "httpx\\.",
  "path": "src",
  "type": "py",
  "output_mode": "files_with_matches"
}
```

2. **Read httpx usage context:**
```json
{
  "tool": "read",
  "file_path": "src/api/client.py",
  "offset": 10,
  "limit": 30
}
```

3. **Resolve httpx library ID:**
```json
{
  "tool": "context7_resolve_library_id",
  "libraryName": "httpx",
  "query": "AsyncClient timeout parameter"
}
```

4. **Query httpx documentation:**
```json
{
  "tool": "context7_query_docs",
  "libraryId": "/httpx/httpx",
  "query": "How to set timeout in AsyncClient?"
}
```

---

### code-reviewer

**Primary Tools:** Read, Bash
**Schema Usage:** 40%

**Focus Areas:**
- Cyclomatic complexity (>10 = flag)
- DRY violations (duplicate code)
- Naming consistency
- Maintainability
- Performance bottlenecks

**Tool Invocation Examples:**

1. **Inspect code for complexity:**
```json
{
  "tool": "read",
  "file_path": "src/handlers/complex_handler.py"
}
```

2. **Run complexity analysis:**
```json
{
  "tool": "bash",
  "command": "radon cc src/ -a"
}
```

---

### test-generator

**Primary Tools:** Bash, Read
**Schema Usage:** 30%

**Focus Areas:**
- Test coverage gaps (<80%)
- Edge case coverage
- Happy path + error path tests
- Mock external dependencies
- Test naming conventions

**Tool Invocation Examples:**

1. **Generate coverage report:**
```json
{
  "tool": "bash",
  "command": "pytest tests/ --cov=src --cov-report=json"
}
```

2. **Inspect function to test:**
```json
{
  "tool": "read",
  "file_path": "src/validators/input_validator.py"
}
```

---

## Token Impact Analysis

### Current Token Usage (Baseline)

Per-agent breakdown (50,000 tokens):
- System prompt + instructions: 2,000 tokens (4%)
- Tool descriptions (natural language): 5,000 tokens (10%)
- Input formatting + examples: 2,000 tokens (4%)
- Report generation guidance: 3,000 tokens (6%)
- Input code to verify: 15,000 tokens (30%)
- Working memory (reasoning): 20,000 tokens (40%)
- Other: 3,000 tokens (6%)

**5 agents × 50K = 250K tokens/cycle**

### With Phase 3 Schemas

Per-agent reduction:
- Tool descriptions: 5,000 → 1,500 tokens (-70%)
- Input formatting: 2,000 → 800 tokens (-60%)
- Report guidance: 3,000 → 1,200 tokens (-60%)
- Constraint expressions: 1,000 → 300 tokens (-70%)

**New per-agent total: 31.5K tokens (-37%)**
**5 agents × 31.5K = 157.5K tokens/cycle**

### Savings Summary

| Metric | Before Phase 3 | After Phase 3 | Savings |
|--------|----------------|---------------|---------|
| Tokens per cycle | 250,000 | 157,500 | 92,500 (-37%) |
| Cost per cycle | $0.75 | $0.47 | $0.28 (-37%) |
| Daily cycles (5/day) | 5 × $0.75 = $3.75 | 5 × $0.47 = $2.35 | $1.40/day |
| Monthly cycles (150/month) | 150 × $0.75 = $112.50 | 150 × $0.47 = $70.50 | $42/month |
| Annual baseline | - | - | $4,230/year (150 cycles × $0.47 × 12) |

### Post-Phase 3 Measurement (Task 3.4)

Real-world cost savings validation is available via:

**`.claude/scripts/measure-routing-savings.py`**

This script analyzes API usage logs to validate hierarchical model routing (Haiku/Sonnet/Opus) cost savings:

**Expected Savings with Hierarchical Routing:**
- **Annual baseline (150 cycles/month):** $504/year
- **Target distribution:** 40% Haiku, 50% Sonnet, 10% Opus
- **Cost reduction:** 40-60% vs all-Opus baseline
- **Actual master plan results:** $12.84 for 32 tasks (74% reduction vs estimated $50 all-Opus)

**Combined Benefits (Schemas + Hierarchical Routing):**
- Schemas: -37% tokens
- Routing: -40-60% tokens vs all-Opus
- **Combined:** ~60-70% cost reduction for verification cycles

For detailed theoretical validation, decision tree alignment, and continuous monitoring guidance, see:
`.ignorar/production-reports/phase3/2026-02-08-phase3-task34-routing-savings-validation.md`

---

## Validation & Fallback

### Schema Validation

All schemas should pass JSON validation before use:

```python
import json
schema = {...}
try:
    json.dumps(schema)  # Validate JSON structure
except json.JSONDecodeError as e:
    # Log error and fall back to natural language
    logger.error(f"Invalid schema: {e}")
```

### Fallback Strategy

If schema validation fails:
1. Log error with schema path and details
2. Fall back to natural language tool description
3. Agent continues with natural language guidance
4. Report discrepancy for analysis

---

## Fallback & Observability

### Context7 MCP Fallback Behavior

When Context7 MCP tools fail, agents should gracefully degrade:

**Failure Scenarios:**
- Context7 server timeout (>10s)
- Connection errors
- Invalid library name
- Rate limiting

**Fallback Actions:**
1. **hallucination-detector:** Log warning, continue with pattern matching only (no doc verification)
2. **code-implementer:** Use memory/training data as last resort, mark as "unverified" in report
3. Log fallback event for observability tracking

**Example Fallback Logic:**
```python
try:
    library_id = await resolve_library_id(library_name="httpx")
    docs = await query_docs(library_id=library_id, query="AsyncClient timeout")
except TimeoutError:
    logger.warning("context7_fallback", reason="timeout", library=library_name)
    # Log fallback event: {"event": "fallback_activated", "reason": "context7_timeout"}
    # Continue with best-effort verification
except Exception as e:
    logger.error("context7_error", error=str(e))
    # Log fallback event
```

### Health Check

**Quick Health Check:**
```bash
python .claude/scripts/mcp-health-check.py
```

**Exit Codes:**
- 0 = Healthy (latency <3s, successful)
- 1 = Degraded (latency 3-10s OR partial failure)
- 2 = Failed (latency >10s OR complete failure)

**Automated Monitoring:**
```bash
# In CI/CD or cron job
python .claude/scripts/mcp-health-check.py --quiet && echo "MCP OK" || echo "MCP Issue"
```

### Observability Metrics

**Track via mcp-observability.py:**
- Call counts (resolve-library-id, query-docs)
- Latency (avg, p95, p99)
- Error rate
- Fallback activation rate

**Alert Thresholds:**
- ⚠️  Fallback rate >10% → Investigate Context7 connectivity
- ⚠️  P95 latency >5s → Check server load or network

**Run Observability Tool:**
```bash
# Summary output
python .claude/scripts/mcp-observability.py --log-file ~/.claude/logs/mcp-calls.jsonl

# JSON for automation
python .claude/scripts/mcp-observability.py --log-file ~/.claude/logs/mcp-calls.jsonl --output json
```

**Dashboard:**
View metrics at `.ignorar/production-reports/mcp-observability/dashboard.md`

### Log Format for MCP Calls

Agents should log MCP calls in this format:

```json
{"timestamp": "2026-02-08T10:30:00Z", "tool": "context7_resolve_library_id", "library": "httpx", "latency_ms": 234, "status": "success"}
{"timestamp": "2026-02-08T10:30:05Z", "tool": "context7_query_docs", "library_id": "/httpx/httpx", "latency_ms": 456, "status": "success"}
{"timestamp": "2026-02-08T10:30:10Z", "event": "fallback_activated", "reason": "context7_timeout"}
```

### When to Check Health

**Before critical operations:**
- Before running hallucination-detector on large codebase
- Before code-implementer starts implementing with many external libraries
- After Context7 server updates or deployments

**Monitoring schedule:**
- Hourly health checks in production
- Daily observability reports
- Alert on consecutive health check failures (3+ in 1 hour)

### Validation Checklist

Before deploying Phase 3:
- [ ] All JSON schemas pass `json.loads()`
- [ ] All schema properties are defined
- [ ] Required fields marked correctly
- [ ] Examples match schema structure
- [ ] No circular schema references
- [ ] Enums match actual agent names

---

## Integration Points

### Phase 1 + 2 + 3 Architecture

```
Phase 1: Parallel Execution
  └─ Wave 1: best-practices, security-auditor, hallucination-detector (3 agents, ~7 min)
  └─ Wave 2: code-reviewer, test-generator (2 agents, ~5 min)

Phase 2: Few-Shot Examples
  └─ Each agent has structured output examples
  └─ Reduces explanation overhead

Phase 3: Programmatic Tool Schemas
  └─ Each agent invokes tools using JSON schemas
  └─ Reduces natural language overhead by 37%
  └─ Final cycle: ~11 min, -37% tokens
```

---

## Deployment Checklist

- [ ] `.claude/rules/agent-tool-schemas.md` created
- [ ] `.claude/skills/verify/SKILL.md` updated with tool schema reference
- [ ] All 5 agent prompts updated with schema examples
- [ ] All JSON schemas validated
- [ ] Testing completed (3 test phases)
- [ ] Performance metrics confirmed
- [ ] Changes committed to main

---

**Status:** Ready for verification agents to use
**Last Updated:** 2026-02-07
**Version:** 1.0
